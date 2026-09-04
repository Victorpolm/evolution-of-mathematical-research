"""Direct structured-output API backends for classification (review-4 P0-4,
hardened per review-5 P0-4/P0-7).

Providers are inferred from the model id:
    claude-*                -> Anthropic Messages API (forced tool schema)
    gpt-* / o* / chatgpt-*  -> OpenAI chat completions (strict json_schema;
                               single pinned endpoint, no runtime fallback)
    gemini-*                -> Google generateContent (responseSchema)

Contract:
- provider-NATIVE schema enforcement (not merely JSON-prompted output); the
  local validator in classify.py remains the fail-closed authority
- every call reserves its estimated cost BEFORE dispatch against a
  per-provider USD budget with a snapshotted price table; once a budget trips,
  every subsequent call fails immediately without an HTTP request
- a conservative rule: failed calls keep their reservation as spent (a
  timeout does not prove the provider did not process and bill the request)
- per-call attempt metadata (endpoint, request id, stop reason, usage,
  retries, duration) is buffered for the caller to persist
- one dedicated Session per thread: trust_env=False (no ambient proxies or
  .netrc), no redirects
- keys come from the environment or the gitignored repo-root `.env`
  (allowlisted names only); values are never logged
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time

import requests

from . import db, taxonomy

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODELS_URL = "https://api.openai.com/v1/models"
GOOGLE_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "{model}:generateContent")

MAX_OUTPUT_TOKENS = 4000
RETRIES = 4
ENV_ALLOWLIST = {"ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"}

# Operator-verified price snapshots (USD per 1M tokens), covering EVERY
# usage class the provider bills (review-10 B2: the live adherence run was
# billed 174,153 cache-WRITE tokens that the old base-rate-only table
# undercounted by 12.45%). A USD budget refuses models without a snapshot;
# update deliberately and record the date.
PRICES_USD_PER_MTOK = {
    # official Luna model page, re-checked 2026-08-13 (review-11 B2): base
    # input 0.20, CACHED INPUT 0.02 (the 2026-08-12 snapshot wrongly used
    # 0.25 — conservative for the cap, wrong for the ledger; corrected with
    # a refund row), cache writes 1.25x base = 0.25, output 1.20
    "gpt-5.6-luna": {"input": 0.20, "cached_input": 0.02, "cache_write": 0.25,
                     "output": 1.20, "asof": "2026-08-13"},
    # anthropic pricing page — cache classes set to the 1.25x CEILING as a
    # conservative placeholder; RE-VERIFY every class before any paid
    # Anthropic run (a hard cap may over-reserve, never under-charge)
    "claude-haiku-4-5-20251001": {"input": 1.00, "cached_input": 1.25,
                                  "cache_write": 1.25, "output": 5.00,
                                  "asof": "2026-08-12"},
}
USAGE_CLASSES = ("input", "cached_input", "cache_write")  # + "output"

_lock = threading.Lock()
_usage: dict[str, dict[str, int]] = {}     # model -> {input, output, calls}
_spent_usd: dict[str, float] = {}          # provider -> committed USD (incl.
                                           # durable baseline when attached)
_reserved_usd: dict[str, float] = {}       # provider -> in-flight USD
_reserved_tokens: dict[str, int] = {}      # provider -> in-flight tokens
_budget_tokens: list[int | None] = [None]
_budget_usd: list[float | None] = [None]   # per provider
_stopped: list[str | None] = [None]        # first budget-stop reason
_ledger: list = [None, None]               # [db_path, run_id]
_campaign: list = [None]                   # approval id scoping spend rows
_campaign_prices: list = [None]            # parsed authoritative snapshot
_tls = threading.local()                   # session, ledger con, attempts,
                                           # current reservation-row context



class _Retryable(RuntimeError):
    def __init__(self, msg: str, retry_after: int = 0,
                 billed_possible: bool = True,
                 http_status: int | None = None):
        super().__init__(msg)
        self.retry_after = retry_after
        # a 429 response is proof the rate limiter REJECTED the request —
        # releasing its reservation is accurate, not optimistic; timeouts
        # and 5xx stay conservative (the provider may have processed them)
        self.billed_possible = billed_possible
        # review-9 B5: keep the real HTTP status for the attempt record
        self.http_status = http_status


class BudgetExceeded(RuntimeError):
    pass


class LeaseFenceLost(RuntimeError):
    """The durable run-lease fence no longer names this process — refuse the
    dispatch (review-10 B6: the fence is checked INSIDE the admission
    transaction, not only in process memory)."""


_fence: list = [None]  # (run_id, holder) enforced inside every admission


def set_fence(run_id: str, holder: str) -> None:
    _fence[0] = (run_id, holder)


def set_request_context(ctx: dict | None) -> None:
    """Logical-request context (split path + ordered snippet hashes) set by
    the classifier before each physical call, so the PRE-DISPATCH attempt
    row already carries exact input identity (review-10 B7)."""
    _tls.request_ctx = ctx


def _reset_for_tests() -> None:
    with _lock:
        _usage.clear()
        _spent_usd.clear()
        _reserved_usd.clear()
        _reserved_tokens.clear()
        _budget_tokens[0] = _budget_usd[0] = None
        _stopped[0] = None
        _ledger[0] = _ledger[1] = None
        _campaign[0] = None
    _fence[0] = None
    _campaign_prices[0] = None
    _tls.attempts = []
    _tls.reservation_row_id = None
    _tls.attempt_no = None
    _tls.attempt_row_id = None
    _tls.request_ctx = None
    _tls.prompt_sha = None
    _tls.last_usage = None
    con = getattr(_tls, "ledger_con", None)
    if con is not None:
        con.close()
        _tls.ledger_con = None


def _ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())


def attach_ledger(db_path, run_id: str, approval_id: str | None = None,
                  provider: str | None = None, model: str | None = None,
                  cap_usd: float | None = None,
                  purpose: str | None = None) -> None:
    """Bind the durable api_spend ledger and (review-8 B1) a budget
    CAMPAIGN: spend rows are scoped to the owner approval id, so a newly
    approved campaign never inherits prior pilots' spend, and reservation
    admission is checked against the durable campaign sum inside one
    BEGIN IMMEDIATE transaction — cross-process safe, never process-local
    memory. Without an approval id the legacy all-history pooling applies
    (kept for ad-hoc diagnostics only). Stale 'reserved' rows from a
    crashed process stay counted as spent (conservative — the dispatch may
    have been billed) and are flagged for provider-console reconciliation."""
    import sqlite3
    _ledger[0], _ledger[1] = str(db_path), run_id
    _campaign[0] = approval_id
    con = sqlite3.connect(_ledger[0], timeout=60)
    try:
        if approval_id is not None:
            row = con.execute(
                "SELECT provider, model, cap_usd, status FROM budget_campaigns "
                "WHERE approval_id=?", (approval_id,)).fetchone()
            if row is None:
                # review-9 B1: an unknown approval id must NEVER create its
                # own spending authority — campaigns are pre-created in a
                # separate owner-authorized step (create_campaign / the
                # `python3 -m pipeline.llm_api create-campaign` CLI)
                raise RuntimeError(
                    f"unknown budget campaign {approval_id!r} — refusing to "
                    "spend. Create it deliberately first: python3 -m "
                    "pipeline.llm_api create-campaign ...")
            else:
                if row[3] != "active":
                    raise RuntimeError(
                        f"budget campaign {approval_id!r} is {row[3]!r} — "
                        "not spendable")
                if (provider is not None and row[0] != provider) or \
                        (model is not None and row[1] != model):
                    raise RuntimeError(
                        f"campaign {approval_id!r} is bound to "
                        f"{row[0]}/{row[1]}, not {provider}/{model} — one "
                        "approval, one provider+model")
                if cap_usd is not None and abs(float(row[2]) - cap_usd) > 1e-9:
                    raise RuntimeError(
                        f"campaign {approval_id!r} cap is ${row[2]:.2f}; the "
                        f"CLI requested ${cap_usd:.2f} — one campaign, one "
                        "cap (amend budget_campaigns deliberately instead)")
            rows = con.execute(
                "SELECT provider, COALESCE(SUM(usd),0) FROM api_spend "
                "WHERE approval_id=? GROUP BY provider",
                (approval_id,)).fetchall()
            stale = con.execute(
                "SELECT COUNT(*) FROM api_spend WHERE kind='reserved' "
                "AND approval_id=?", (approval_id,)).fetchone()[0]
        else:
            rows = con.execute(
                "SELECT provider, COALESCE(SUM(usd),0) FROM api_spend "
                "GROUP BY provider").fetchall()
            stale = con.execute(
                "SELECT COUNT(*) FROM api_spend WHERE kind='reserved'"
            ).fetchone()[0]
    finally:
        con.close()
    if stale:
        print(f"WARNING: {stale} stale in-flight reservation rows from a "
              "previous crash are counted as spent — reconcile against the "
              "provider console", flush=True)
    if approval_id is not None:
        # review-11 B1: parse the campaign snapshot and make it the pricing
        # authority when it covers every billed class; otherwise fall back
        # to the code table with a loud warning (acceptable only for the
        # pilot-era campaign whose snapshot predates class-aware tariffs)
        try:
            snap_row = None
            con2 = sqlite3.connect(_ledger[0], timeout=60)
            try:
                snap_row = con2.execute(
                    "SELECT price_snapshot_json FROM budget_campaigns "
                    "WHERE approval_id=?", (approval_id,)).fetchone()
            finally:
                con2.close()
            snap = json.loads(snap_row[0]) if snap_row and snap_row[0] else {}
            models_ok = {m: p for m, p in snap.items()
                         if isinstance(p, dict)
                         and all(c in p for c in (*USAGE_CLASSES, "output"))}
            if model is not None and model in models_ok:
                _campaign_prices[0] = models_ok
            else:
                _campaign_prices[0] = None
                print("WARNING: campaign tariff snapshot incomplete for "
                      f"{model!r} — falling back to the code price table. "
                      "Pilot campaigns only; a full-run campaign must carry "
                      "a complete authoritative snapshot (review-11 B1)",
                      flush=True)
        except (ValueError, TypeError):
            _campaign_prices[0] = None
            print("WARNING: unparsable campaign tariff snapshot — falling "
                  "back to the code price table", flush=True)
    with _lock:
        for prov, usd in rows:
            _spent_usd[prov] = float(usd)


def create_campaign(db_path, approval_id: str, provider: str, model: str,
                    cap_usd: float, purpose: str) -> None:
    """Owner-authorized campaign creation — a SEPARATE deliberate step
    (review-9 B1). Refuses to overwrite an existing campaign, refuses
    non-finite caps and models without a full tariff snapshot (review-10
    B5), and records an append-only 'created' event (campaign_events)."""
    import math
    import sqlite3
    if not approval_id or cap_usd is None or not math.isfinite(cap_usd) \
            or cap_usd <= 0:
        raise ValueError("campaign needs an approval id and a positive, "
                         "finite cap")
    price = _price(model)
    if price is None:
        raise ValueError(f"no tariff snapshot for model {model!r} — add all "
                         "usage classes to PRICES_USD_PER_MTOK first "
                         "(review-10 B2)")
    missing = [c for c in (*USAGE_CLASSES, "output") if c not in price]
    if missing:
        raise ValueError(f"tariff snapshot for {model!r} lacks usage classes "
                         f"{missing} — a hard cap needs every billed class")
    con = sqlite3.connect(str(db_path), timeout=60)
    try:
        exists = con.execute("SELECT 1 FROM budget_campaigns WHERE "
                             "approval_id=?", (approval_id,)).fetchone()
        if exists:
            raise RuntimeError(f"campaign {approval_id!r} already exists — "
                               "campaigns are immutable; amend purpose via "
                               "amend-campaign or create a new approval id")
        snapshot = json.dumps({model: price, "asof": _ts()})
        with con:
            con.execute(
                "INSERT INTO budget_campaigns (approval_id, provider, model, "
                "cap_usd, price_snapshot_json, purpose, status, created_at) "
                "VALUES (?,?,?,?,?,?, 'active', ?)",
                (approval_id, provider, model, cap_usd, snapshot, purpose,
                 _ts()))
            con.execute(
                "INSERT INTO campaign_events (ts, approval_id, event, "
                "detail_json) VALUES (?,?,?,?)",
                (_ts(), approval_id, "created",
                 json.dumps({"provider": provider, "model": model,
                             "cap_usd": cap_usd, "purpose": purpose,
                             "price_snapshot": json.loads(snapshot)})))
    finally:
        con.close()


def get_campaign(db_path, approval_id: str) -> dict:
    """Load a campaign row for protocol binding (review-9 B1: campaign
    identity enters the classification protocol hash, so a resumed run can
    never switch approval/cap). Raises on unknown id."""
    import sqlite3
    con = sqlite3.connect(str(db_path), timeout=60)
    try:
        row = con.execute(
            "SELECT approval_id, provider, model, cap_usd, "
            "price_snapshot_json, status FROM budget_campaigns "
            "WHERE approval_id=?", (approval_id,)).fetchone()
    finally:
        con.close()
    if row is None:
        raise RuntimeError(
            f"unknown budget campaign {approval_id!r} — create it "
            "deliberately first: python3 -m pipeline.llm_api create-campaign")
    return {"approval_id": row[0], "provider": row[1], "model": row[2],
            "cap_usd": float(row[3]), "price_snapshot_json": row[4],
            "status": row[5]}


def _ledger_con():
    import sqlite3
    con = getattr(_tls, "ledger_con", None)
    if con is None:
        con = sqlite3.connect(_ledger[0], timeout=60)
        con.isolation_level = None  # explicit BEGIN IMMEDIATE transactions
        _tls.ledger_con = con
    return con


def _ledger_admit(provider: str, model: str, usd: float
                  ) -> tuple[int | None, int | None]:
    """ONE atomic admission transaction (review-7/-8/-10): campaign
    status/cap/provider/model verification, lease-fence verification, the
    durable 'reserved' spend row, AND the pre-dispatch api_attempts row all
    commit or fail together. A crash at any point leaves either nothing or
    a fully-linked reservation+attempt pair; two processes admit against
    one durable sum because reserved rows carry their estimate in usd.
    Returns (spend_row_id, attempt_row_id)."""
    if _ledger[0] is None:
        return None, None
    con = _ledger_con()
    con.execute("BEGIN IMMEDIATE")
    try:
        if _campaign[0] is not None:
            cap_row = con.execute(
                "SELECT cap_usd, status, provider, model FROM budget_campaigns "
                "WHERE approval_id=?", (_campaign[0],)).fetchone()
            if cap_row is None or cap_row[1] != "active":
                raise BudgetExceeded(
                    f"budget campaign {_campaign[0]!r} missing or inactive")
            # review-10 B5: the campaign's provider+model binding is
            # re-verified INSIDE every admission transaction, not only once
            # at attach time
            if cap_row[2] != provider or cap_row[3] != model:
                raise BudgetExceeded(
                    f"campaign {_campaign[0]!r} is bound to "
                    f"{cap_row[2]}/{cap_row[3]}, not {provider}/{model}")
            committed = con.execute(
                "SELECT COALESCE(SUM(usd),0) FROM api_spend "
                "WHERE approval_id=?", (_campaign[0],)).fetchone()[0]
            if committed + usd > float(cap_row[0]):
                raise BudgetExceeded(
                    f"campaign {_campaign[0]} exhausted (durable, all "
                    f"processes): ${committed:.2f} committed + ${usd:.2f} "
                    f"next > ${cap_row[0]:.2f} cap")
        # review-10 B6: the run-lease fence is part of the SAME transaction
        # that admits the spend — a stale process cannot pay after takeover
        if _fence[0] is not None:
            frow = con.execute("SELECT holder FROM run_leases WHERE run_id=?",
                               (_fence[0][0],)).fetchone()
            if frow is None or frow[0] != _fence[0][1]:
                raise LeaseFenceLost(
                    f"lease for run {_fence[0][0]!r} is no longer held by "
                    "this process — dispatch refused")
        cur = con.execute(
            "INSERT INTO api_spend (ts, run_id, provider, model, kind, usd, "
            "tokens_in, tokens_out, approval_id) VALUES (?,?,?,?,?,?,?,?,?)",
            (_ts(), _ledger[1], provider, model, "reserved", usd, None, None,
             _campaign[0]))
        spend_id = cur.lastrowid
        # review-10 B7: the reservation and the pre-dispatch attempt row are
        # ONE atomic admission — a charge can never exist without request
        # provenance, and the attempt already carries exact input identity
        ctx = getattr(_tls, "request_ctx", None) or {}
        cur = con.execute(
            "INSERT INTO api_attempts (ts, run_id, approval_id, provider, "
            "model, reservation_row_id, attempt_no, state, prompt_sha256, "
            "split_path, snippet_hashes_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (_ts(), _ledger[1], _campaign[0], provider, model, spend_id,
             getattr(_tls, "attempt_no", None), "admitted",
             getattr(_tls, "prompt_sha", None), ctx.get("split_path"),
             json.dumps(ctx["snippet_hashes"])
             if ctx.get("snippet_hashes") else None))
        con.execute("COMMIT")
        return spend_id, cur.lastrowid
    except BaseException:
        try:
            con.execute("ROLLBACK")
        except Exception:
            pass
        raise


def _ledger_write(provider: str, model: str, kind: str, usd: float,
                  tokens_in, tokens_out, row_id: int | None = None) -> None:
    if _ledger[0] is None:
        return
    con = _ledger_con()
    con.execute("BEGIN IMMEDIATE")
    try:
        if row_id is not None:  # transition the pre-dispatch reservation row
            con.execute(
                "UPDATE api_spend SET kind=?, usd=?, tokens_in=?, "
                "tokens_out=?, ts=? WHERE id=?",
                (kind, usd, tokens_in, tokens_out, _ts(), row_id))
        else:
            con.execute(
                "INSERT INTO api_spend (ts, run_id, provider, model, kind, usd, "
                "tokens_in, tokens_out, approval_id) VALUES (?,?,?,?,?,?,?,?,?)",
                (_ts(), _ledger[1], provider, model, kind, usd, tokens_in,
                 tokens_out, _campaign[0]))
        con.execute("COMMIT")
    except BaseException:
        try:
            con.execute("ROLLBACK")
        except Exception:
            pass
        raise


_PROVIDER_ENVVAR = {"anthropic": "ANTHROPIC_API_KEY",
                    "openai": "OPENAI_API_KEY", "google": "GOOGLE_API_KEY"}


def load_env(provider: str | None = None) -> None:
    """Set allowlisted env vars from repo-root .env (existing environment
    wins). Values are secrets: never print, never store. When a provider is
    given, ONLY that provider's key is loaded — an OpenAI-only run must not
    carry Anthropic/Google credentials in its environment (review-9 B7)."""
    if provider:
        # review-10 B8: scrub UNRELATED provider credentials inherited from
        # the parent environment — one run, one key
        for other, var in _PROVIDER_ENVVAR.items():
            if other != provider:
                os.environ.pop(var, None)
    path = db.PROJECT_ROOT / ".env"
    if not path.exists():
        return
    wanted = ({_PROVIDER_ENVVAR[provider]} if provider else set(ENV_ALLOWLIST))
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip("'\"")
        if key in wanted and val and key not in os.environ:
            os.environ[key] = val


def provider_of_model(model: str) -> str:
    m = model.lower()
    if m.startswith("claude"):
        return "anthropic"
    if m.startswith(("gpt", "o1", "o3", "o4", "chatgpt")):
        return "openai"
    if m.startswith("gemini"):
        return "google"
    raise ValueError(f"cannot infer provider from model id {model!r}")


def _key_for(provider: str) -> str:
    envvar = _PROVIDER_ENVVAR[provider]
    key = os.environ.get(envvar)
    if not key:
        raise RuntimeError(f"{envvar} not set (put it in .env — gitignored)")
    return key


def _session() -> requests.Session:
    s = getattr(_tls, "session", None)
    if s is None:
        s = requests.Session()
        s.trust_env = False           # no ambient proxies / .netrc / CA swaps
        _tls.session = s
    return s


# --- schema -------------------------------------------------------------------

def label_schema() -> dict:
    """Closed JSON schema for one label object, generated from taxonomy.py
    (single source of truth; drift-tested there). Strict-mode compatible:
    every property required, additionalProperties false."""
    flags_props = {f: {"type": "boolean"} for f in taxonomy.FLAGS}
    return {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "polarity": {"type": "string",
                         "enum": sorted(taxonomy.POLARITIES)},
            "tools": {"type": "array", "items": {"type": "string"}},
            "models": {"type": "array", "items": {"type": "string"}},
            "categories": {"type": "array",
                           "items": {"type": "string",
                                     "enum": sorted(taxonomy.CATEGORIES)}},
            "epistemic_impact": {"type": "string",
                                 "enum": sorted(taxonomy.IMPACTS)},
            "locations": {"type": "array", "minItems": 1,
                          "items": {"type": "string",
                                    "enum": list(taxonomy.LOCATIONS)}},
            "flags": {"type": "object", "properties": flags_props,
                      "required": sorted(flags_props),
                      "additionalProperties": False},
            "confidence": {"type": "number"},
            "quote": {"type": "string"},
        },
        "required": ["id", "polarity", "tools", "models", "categories",
                     "epistemic_impact", "locations", "flags",
                     "confidence", "quote"],
        "additionalProperties": False,
    }


def batch_schema() -> dict:
    return {"type": "object",
            "properties": {"labels": {"type": "array",
                                      "items": label_schema()}},
            "required": ["labels"], "additionalProperties": False}


def _strip_for_google(schema: dict) -> dict:
    """Google's responseSchema rejects additionalProperties."""
    if isinstance(schema, dict):
        return {k: _strip_for_google(v) for k, v in schema.items()
                if k != "additionalProperties"}
    if isinstance(schema, list):
        return [_strip_for_google(x) for x in schema]
    return schema


# --- budget -------------------------------------------------------------------

def set_budget(max_tokens: int | None = None,
               max_usd_per_provider: float | None = None) -> None:
    _budget_tokens[0] = max_tokens
    _budget_usd[0] = max_usd_per_provider


def budget_state() -> dict:
    with _lock:
        return {"prices": PRICES_USD_PER_MTOK,
                "max_usd_per_provider": _budget_usd[0],
                "max_tokens": _budget_tokens[0],
                "spent_usd": dict(_spent_usd),
                "campaign": _campaign[0],
                "stopped": _stopped[0]}


def usage_summary() -> dict[str, dict[str, int]]:
    with _lock:
        return {m: dict(u) for m, u in _usage.items()}


def drain_attempts() -> list[dict]:
    """Drain THIS thread's attempt buffer (review-8 B3: a global buffer
    drained by whichever future completed next attributed request ids to the
    wrong logical batch — attempts are thread-local now, and each worker
    drains its own right after its call returns)."""
    out = getattr(_tls, "attempts", [])
    _tls.attempts = []
    return out


def _price(model: str) -> dict | None:
    """Campaign tariff snapshot FIRST (review-11 B1: the run protocol binds
    the snapshot, so the snapshot — not the mutable code table — must be
    what reservation and settlement actually use); the code table is the
    fallback for snapshot-less/incomplete (pilot-era) campaigns."""
    snap = _campaign_prices[0]
    if snap and model in snap:
        return snap[model]
    return PRICES_USD_PER_MTOK.get(model)


def _worst_input_rate(model: str) -> float:
    """Worst per-token input rate across every billed usage class — the
    reservation must upper-bound whatever mix the provider bills
    (review-10 B2: cache writes cost MORE than base input)."""
    p = _price(model)
    if p is None:
        return 0.0
    return max(p.get(c, 0.0) for c in USAGE_CLASSES)


def _cost_usd_classes(model: str, classes: dict) -> float:
    """Class-aware cost: uncached input, cached input, cache writes, and
    output are each billed at their own snapshotted rate."""
    p = _price(model)
    if p is None:
        return 0.0
    return (classes.get("input", 0) * p["input"]
            + classes.get("cached_input", 0) * p.get("cached_input", p["input"])
            + classes.get("cache_write", 0) * p.get("cache_write", p["input"])
            + classes.get("output", 0) * p["output"]) / 1e6


def _int_ok(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def _validated_usage(provider: str, usage) -> dict | None:
    """Normalize provider usage into billing classes, FAIL-CLOSED
    (review-10 B3: adapters used to default absent fields to zero and
    settlement believed them — a billed success with missing usage settled
    at $0). Returns {'input','cached_input','cache_write','output'} or
    None when the usage object is missing, malformed, or internally
    inconsistent — the caller then keeps the full conservative
    reservation."""
    if not isinstance(usage, dict):
        return None
    try:
        if provider == "openai":
            pt, ct = usage.get("prompt_tokens"), usage.get("completion_tokens")
            if not (_int_ok(pt) and _int_ok(ct)) or pt == 0:
                return None
            det = usage.get("prompt_tokens_details") or {}
            cached = det.get("cached_tokens", 0)
            cw = det.get("cache_write_tokens", 0)
            if not (_int_ok(cached) and _int_ok(cw)) or cached + cw > pt:
                return None
            return {"input": pt - cached - cw, "cached_input": cached,
                    "cache_write": cw, "output": ct}
        if provider == "anthropic":
            tin, tout = usage.get("input_tokens"), usage.get("output_tokens")
            if not (_int_ok(tin) and _int_ok(tout)):
                return None
            cw = usage.get("cache_creation_input_tokens", 0)
            cr = usage.get("cache_read_input_tokens", 0)
            if not (_int_ok(cw) and _int_ok(cr)):
                return None
            # anthropic reports cache classes SEPARATELY from input_tokens
            return {"input": tin, "cached_input": cr, "cache_write": cw,
                    "output": tout}
        if provider == "google":
            pt = usage.get("promptTokenCount")
            ct = usage.get("candidatesTokenCount")
            if not (_int_ok(pt) and _int_ok(ct)) or pt == 0:
                return None
            cached = usage.get("cachedContentTokenCount", 0)
            if not _int_ok(cached) or cached > pt:
                return None
            return {"input": pt - cached, "cached_input": cached,
                    "cache_write": 0, "output": ct}
    except Exception:
        return None
    return None


_overhead_cache: list[int | None] = [None]


def _request_overhead_tokens() -> int:
    """Non-prompt request overhead upper bound (review-10 B4: the old fixed
    1,500 was unexplained): the serialized JSON schema plus a chat-framing
    margin, bounded by the same bytes>=BPE-tokens argument as the prompt.
    Measured, not guessed."""
    if _overhead_cache[0] is None:
        _overhead_cache[0] = (len(json.dumps(batch_schema()).encode("utf-8"))
                              + 800)  # role/framing/tool-wrapper margin
    return _overhead_cache[0]


def _est_tokens(prompt: str) -> int:
    """PROVABLE input upper bound (review-9 B2): every BPE token consumes at
    least one byte of input text, so the UTF-8 byte count bounds the token
    count for the prompt AND the serialized schema; output is separately
    hard-capped by MAX_OUTPUT_TOKENS. Reservations therefore exceed actuals
    ~3-6x, which is negligible against the campaign cap at these prompt
    sizes — correctness over tightness. Settlement additionally asserts
    actual <= reserved and latches if ever violated (review-10 B4)."""
    return len(prompt.encode("utf-8")) + _request_overhead_tokens()


def _reserve(provider: str, model: str, prompt: str) -> float:
    """Reserve the worst-case cost of ONE PHYSICAL DISPATCH before any HTTP
    request (review-6: retries each get their own reservation). Raises
    BudgetExceeded without spending when a cap would be crossed. Both USD and
    token checks include in-flight reservations, so concurrent workers cannot
    jointly pass the same remaining headroom."""
    est_in = _est_tokens(prompt)
    # reserve at the WORST applicable input rate — the provider chooses the
    # cache-write/cached mix, not us (review-10 B2)
    p = _price(model)
    est = (est_in * _worst_input_rate(model)
           + MAX_OUTPUT_TOKENS * (p["output"] if p else 0.0)) / 1e6
    with _lock:
        if _stopped[0]:
            raise BudgetExceeded(_stopped[0])
        cap = _budget_usd[0]
        if cap is not None:
            if not (isinstance(cap, (int, float)) and cap > 0
                    and cap == cap and cap != float("inf")):
                _stopped[0] = f"invalid USD cap {cap!r}"
                raise BudgetExceeded(_stopped[0])
            if _price(model) is None:
                _stopped[0] = (f"no price snapshot for {model!r} — refusing "
                               "to spend under a USD budget")
                raise BudgetExceeded(_stopped[0])
            committed = _spent_usd.get(provider, 0.0) + _reserved_usd.get(provider, 0.0)
            if committed + est > cap:
                _stopped[0] = (f"USD budget for {provider} exhausted: "
                               f"{committed:.2f} committed + {est:.2f} next > "
                               f"{cap:.2f} cap")
                raise BudgetExceeded(_stopped[0])
        tcap = _budget_tokens[0]
        if tcap is not None:
            total = (sum(u["input"] + u["output"] for u in _usage.values())
                     + sum(_reserved_tokens.values()))
            if total + est_in + MAX_OUTPUT_TOKENS > tcap:
                _stopped[0] = (f"token budget exhausted: {total} spent+reserved, "
                               f"cap {tcap}")
                raise BudgetExceeded(_stopped[0])
        _reserved_usd[provider] = _reserved_usd.get(provider, 0.0) + est
        _reserved_tokens[provider] = (_reserved_tokens.get(provider, 0)
                                      + est_in + MAX_OUTPUT_TOKENS)
    try:
        row_id, attempt_row_id = _ledger_admit(provider, model, est)
    except (BudgetExceeded, LeaseFenceLost) as exc:
        # durable admission rejected (possibly by ANOTHER process's spend,
        # or the fence): undo the in-memory reservation; only budget
        # rejections latch — a fence loss is not a budget event
        with _lock:
            _reserved_usd[provider] = max(0.0, _reserved_usd.get(provider, 0.0)
                                          - est)
            _reserved_tokens[provider] = max(0, _reserved_tokens.get(provider, 0)
                                             - est_in - MAX_OUTPUT_TOKENS)
            if isinstance(exc, BudgetExceeded) and not _stopped[0]:
                _stopped[0] = str(exc)
        raise
    return est, row_id, attempt_row_id


def _release(provider: str, model: str, reserved: float, est_in: int,
             row_id: int | None = None) -> None:
    """Free a reservation with zero spend — ONLY for outcomes where the
    provider provably did not process the request (HTTP 429 rejection)."""
    with _lock:
        _reserved_usd[provider] = max(0.0, _reserved_usd.get(provider, 0.0)
                                      - reserved)
        _reserved_tokens[provider] = max(0, _reserved_tokens.get(provider, 0)
                                         - est_in - MAX_OUTPUT_TOKENS)
    _ledger_write(provider, model, "released-unbilled", 0.0, None, None,
                  row_id)


def _settle(provider: str, model: str, reserved: float, est_in: int,
            classes: dict | None, row_id: int | None = None,
            transport_failed: bool = False) -> None:
    """Replace the reservation with actual class-aware cost. Fail-closed
    rules (review-5/-10 B3/B4):
    - transport failure -> the reservation is committed as spent
      ('failed-reserved'): a timeout does not prove the provider did not
      bill;
    - HTTP success with MISSING/MALFORMED usage -> the reservation is
      committed as spent ('settled-unknown-usage'), NEVER $0, until
      provider-console reconciliation;
    - valid usage -> cost computed per billing class (uncached input,
      cached input, cache write, output); if actual ever exceeds its
      reservation the HIGHER amount is charged AND the stop flag latches
      (the reservation proof failed — investigate before more spend)."""
    with _lock:
        _reserved_usd[provider] = max(0.0, _reserved_usd.get(provider, 0.0)
                                      - reserved)
        _reserved_tokens[provider] = max(0, _reserved_tokens.get(provider, 0)
                                         - est_in - MAX_OUTPUT_TOKENS)
        if transport_failed:
            _spent_usd[provider] = _spent_usd.get(provider, 0.0) + reserved
            kind, usd, tin, tout = "failed-reserved", reserved, None, None
        elif classes is None:
            _spent_usd[provider] = _spent_usd.get(provider, 0.0) + reserved
            kind, usd, tin, tout = "settled-unknown-usage", reserved, None, None
            if not _stopped[0]:
                print("WARNING: successful response with missing/malformed "
                      "usage — reservation kept as spent "
                      "(settled-unknown-usage); reconcile with the provider "
                      "console", flush=True)
        else:
            tin = (classes["input"] + classes["cached_input"]
                   + classes["cache_write"])
            tout = classes["output"]
            u = _usage.setdefault(model, {"input": 0, "output": 0, "calls": 0})
            u["input"] += tin
            u["output"] += tout
            u["calls"] += 1
            usd = _cost_usd_classes(model, classes)
            if usd > reserved and not _stopped[0]:
                _stopped[0] = (f"settlement ${usd:.6f} EXCEEDED its "
                               f"reservation ${reserved:.6f} for {model} — "
                               "the reservation envelope proof failed; "
                               "latched (review-10 B4)")
            _spent_usd[provider] = _spent_usd.get(provider, 0.0) + usd
            kind = "settled"
        cap = _budget_usd[0]
        if cap is not None and _spent_usd[provider] > cap and not _stopped[0]:
            _stopped[0] = (f"USD spend for {provider} "
                           f"(${_spent_usd[provider]:.2f}) exceeded the "
                           f"${cap:.2f} cap — latched")
    _ledger_write(provider, model, kind, usd, tin, tout, row_id)


# --- transport ----------------------------------------------------------------

def _post(url: str, headers: dict, body: dict, timeout: int
          ) -> requests.Response:
    """ONE physical dispatch (review-6: the retry loop lives in call_api so
    every physical attempt gets its own budget reservation and attempt row).
    Transport errors, 429 and 5xx raise _Retryable; other 4xx return —
    contract errors, not transients."""
    try:
        resp = _session().post(url, headers=headers, json=body,
                               timeout=timeout, allow_redirects=False)
    except requests.RequestException as exc:
        raise _Retryable(f"{type(exc).__name__}: {str(exc)[:200]}") from exc
    if resp.status_code == 429 or resp.status_code >= 500:
        try:
            wait = min(int(resp.headers.get("Retry-After", "0")), 120)
        except ValueError:
            wait = 0
        raise _Retryable(f"http{resp.status_code}", retry_after=wait,
                         billed_possible=resp.status_code != 429,
                         http_status=resp.status_code)
    return resp


def _err_summary(resp) -> str:
    """Status plus provider error type/code/param ONLY — never the free-text
    message or raw body, which can echo submitted snippet content into
    console/DB/JSONL logs (review-9 B7)."""
    try:
        err = resp.json().get("error") or {}
        bits = [f"{k}={err[k]}" for k in ("type", "code", "param")
                if err.get(k)]
    except Exception:
        bits = []
    return f"http{resp.status_code}" + (f" [{'; '.join(bits)}]" if bits else "")


# NB: the pre-dispatch api_attempts row is created INSIDE _ledger_admit —
# reservation and attempt admission are one atomic transaction (review-10 B7)


def _resp_sha(resp) -> str:
    """Normalized response-content hash; tolerates fakes without .content."""
    raw = getattr(resp, "content", None)
    if raw is None:
        try:
            raw = json.dumps(resp.json(), sort_keys=True).encode()
        except Exception:
            raw = b""
    return hashlib.sha256(raw).hexdigest()


def _record_attempt(provider: str, model: str, endpoint: str, t0: float,
                    request_id: str | None, stop_reason: str | None,
                    usage: dict | None, http_status: int | None,
                    returned_model: str | None = None,
                    system_fingerprint: str | None = None,
                    response_sha256: str | None = None) -> None:
    if not hasattr(_tls, "attempts"):
        _tls.attempts = []
    _tls.last_usage = usage  # known usage survives post-response failures
    row_id = getattr(_tls, "attempt_row_id", None)
    rec = {
        "ts": _ts(),
        "provider": provider, "model": model, "endpoint": endpoint,
        "request_id": request_id, "stop_reason": stop_reason,
        "usage": usage, "http_status": http_status,
        # review-12: every physical 200 response leaves a normalized content
        # hash in the per-exchange provenance EVEN when semantic handling
        # later raises (refusal/length/parse) — 153 length-truncated
        # responses in the v2.7 run had no response identity at all. A
        # durable api_attempts column needs migration v9 (deferred: the DB
        # is held by the live crawl).
        "response_sha256": response_sha256,
        # review-8 B4: a requested alias is not provenance — persist what
        # the provider says it actually served
        "returned_model": returned_model,
        "system_fingerprint": system_fingerprint,
        # review-8 B3: exact linkage to the durable spend reservation and
        # the retry position within call_api
        "reservation_row_id": getattr(_tls, "reservation_row_id", None),
        "attempt_no": getattr(_tls, "attempt_no", None),
        "attempt_row_id": row_id,
        "duration_ms": int((time.monotonic() - t0) * 1000)}
    _tls.attempts.append(rec)
    if row_id is not None and _ledger[0] is not None:
        # update the pre-dispatch row immediately in THIS thread — not
        # after an unrelated future completes (review-9 B5)
        con = _ledger_con()
        con.execute("BEGIN IMMEDIATE")
        try:
            con.execute(
                "UPDATE api_attempts SET ts=?, endpoint=?, request_id=?, "
                "returned_model=?, system_fingerprint=?, stop_reason=?, "
                "http_status=?, usage_json=?, duration_ms=?, state=? "
                "WHERE id=?",
                (rec["ts"], endpoint, request_id, returned_model,
                 system_fingerprint, stop_reason, http_status,
                 json.dumps(usage) if usage is not None else None,
                 rec["duration_ms"],
                 "responded" if http_status is not None else "transport-failed",
                 row_id))
            con.execute("COMMIT")
        except BaseException:
            try:
                con.execute("ROLLBACK")
            except Exception:
                pass
            raise


# --- providers ----------------------------------------------------------------

def _call_anthropic(prompt: str, model: str, timeout: int
                    ) -> tuple[str, dict | None]:
    t0 = time.monotonic()
    resp = _post(ANTHROPIC_URL,
                 {"x-api-key": _key_for("anthropic"),
                  "anthropic-version": ANTHROPIC_VERSION},
                 {"model": model, "max_tokens": MAX_OUTPUT_TOKENS,
                  "temperature": 0.0,
                  "tools": [{"name": "record_labels",
                             "description": "Record the classification "
                                            "labels for every snippet.",
                             # review-6 P0-2: forced tool_choice alone does
                             # NOT guarantee schema-valid input — strict does
                             "strict": True,
                             "input_schema": batch_schema()}],
                  "tool_choice": {"type": "tool", "name": "record_labels"},
                  "messages": [{"role": "user", "content": prompt}]},
                 timeout)
    if resp.status_code != 200:
        _record_attempt("anthropic", model, ANTHROPIC_URL, t0, None, None,
                        None, resp.status_code)
        raise RuntimeError(f"anthropic {_err_summary(resp)}")
    data = resp.json()
    usage = data.get("usage", {})
    _record_attempt("anthropic", model, ANTHROPIC_URL, t0, data.get("id"),
                    data.get("stop_reason"), usage, 200,
                    returned_model=data.get("model"),
                    response_sha256=_resp_sha(resp))
    labels = None
    for block in data.get("content", []):
        if block.get("type") == "tool_use":
            labels = block.get("input", {}).get("labels")
            break
    if labels is None:
        raise RuntimeError(f"anthropic: no tool_use block "
                           f"(stop_reason={data.get('stop_reason')!r})")
    return json.dumps(labels), usage


def _call_openai(prompt: str, model: str, timeout: int
                 ) -> tuple[str, dict | None]:
    # single pinned endpoint (review-5: no error-text-driven runtime routing)
    t0 = time.monotonic()
    resp = _post(OPENAI_CHAT_URL,
                 {"Authorization": f"Bearer {_key_for('openai')}"},
                 {"model": model,
                  "messages": [{"role": "user", "content": prompt}],
                  "max_completion_tokens": MAX_OUTPUT_TOKENS,
                  # review-9 A6: a rolling provider default is not an
                  # immutable scientific setting — pin the documented
                  # default explicitly and record it in the protocol
                  "reasoning_effort": "medium",
                  # review-7: no provider-side request storage beyond the
                  # provider's own abuse-monitoring window
                  "store": False,
                  "response_format": {
                      "type": "json_schema",
                      "json_schema": {"name": "snippet_labels",
                                      "strict": True,
                                      "schema": batch_schema()}}},
                 timeout)
    if resp.status_code != 200:
        _record_attempt("openai", model, OPENAI_CHAT_URL, t0,
                        resp.headers.get("x-request-id"), None, None,
                        resp.status_code)
        raise RuntimeError(f"openai {_err_summary(resp)}")
    data = resp.json()
    usage = data.get("usage", {})
    choice = data["choices"][0]
    _record_attempt("openai", model, OPENAI_CHAT_URL, t0,
                    data.get("id"), choice.get("finish_reason"), usage, 200,
                    returned_model=data.get("model"),
                    system_fingerprint=data.get("system_fingerprint"),
                    response_sha256=_resp_sha(resp))
    msg = choice.get("message", {})
    if msg.get("refusal"):
        # review-10 B8: refusal text can paraphrase submitted content —
        # never propagate it into exceptions/logs
        raise RuntimeError("openai refusal (text withheld)")
    if choice.get("finish_reason") == "length":
        raise RuntimeError("openai: truncated at max_completion_tokens")
    obj = json.loads(msg.get("content") or "")
    return json.dumps(obj.get("labels", [])), usage


def _call_google(prompt: str, model: str, timeout: int
                 ) -> tuple[str, dict | None]:
    t0 = time.monotonic()
    resp = _post(GOOGLE_URL.format(model=model),
                 {"x-goog-api-key": _key_for("google")},
                 {"contents": [{"parts": [{"text": prompt}]}],
                  "generationConfig": {
                      "temperature": 0.0,
                      "maxOutputTokens": MAX_OUTPUT_TOKENS,
                      "responseMimeType": "application/json",
                      "responseSchema": _strip_for_google(batch_schema())}},
                 timeout)
    if resp.status_code != 200:
        _record_attempt("google", model, "generateContent", t0, None, None,
                        None, resp.status_code)
        raise RuntimeError(f"google {_err_summary(resp)}")
    data = resp.json()
    meta = data.get("usageMetadata", {})
    cands = data.get("candidates") or []
    _record_attempt("google", model, "generateContent", t0,
                    data.get("responseId"),
                    cands[0].get("finishReason") if cands else None, meta, 200,
                    returned_model=data.get("modelVersion"),
                    response_sha256=_resp_sha(resp))
    if not cands:
        # review-10 B8: only the structured block reason, never the body
        block = (data.get("promptFeedback") or {}).get("blockReason")
        raise RuntimeError(f"google: no candidates (blockReason={block!r})")
    text = "".join(p.get("text", "") for p in
                   cands[0].get("content", {}).get("parts", []))
    obj = json.loads(text)
    return json.dumps(obj.get("labels", [])), meta


def call_api(prompt: str, model: str, timeout: int = 300) -> str:
    """Returns the JSON array of labels as canonical text (the classify
    parser and validator remain the fail-closed authority). Every PHYSICAL
    dispatch — including transport retries — is admitted atomically
    (campaign + fence + reservation + attempt row in one transaction) and
    settled with validated class-aware usage afterwards; ambiguous failures
    commit their reservation as spent (a timeout does not prove the
    provider did not bill; missing usage never settles at $0).

    review-10 B5: paid calls REQUIRE an attached campaign ledger — the
    historical ad-hoc unmetered path is closed (ARXIV_OBS_ALLOW_UNMETERED=1
    is a deliberate test/dev-only override)."""
    provider = provider_of_model(model)
    if (_ledger[0] is None or _campaign[0] is None) \
            and not os.environ.get("ARXIV_OBS_ALLOW_UNMETERED"):
        raise RuntimeError(
            "call_api without an active budget campaign is forbidden "
            "(review-10 B5): attach_ledger(..., approval_id=...) first, or "
            "set ARXIV_OBS_ALLOW_UNMETERED=1 for tests/dev only")
    fn = {"anthropic": _call_anthropic, "openai": _call_openai,
          "google": _call_google}[provider]
    est_in = _est_tokens(prompt)
    import hashlib as _hl
    _tls.prompt_sha = _hl.sha256(prompt.encode()).hexdigest()
    last_err = None
    for attempt in range(RETRIES):
        # thread-local context BEFORE admission so the atomic pre-dispatch
        # attempt row carries retry position + prompt hash + request
        # context (review-10 B7)
        _tls.attempt_no = attempt
        reserved, row_id, attempt_row_id = _reserve(provider, model, prompt)
        _tls.reservation_row_id = row_id
        _tls.attempt_row_id = attempt_row_id
        _tls.last_usage = None
        t0 = time.monotonic()
        try:
            text, usage_raw = fn(prompt, model, timeout)
        except _Retryable as exc:
            if exc.billed_possible:
                _settle(provider, model, reserved, est_in, None, row_id,
                        transport_failed=True)
            else:  # 429: provably rejected, reservation freed (no spend)
                _release(provider, model, reserved, est_in, row_id)
            # real start time and HTTP status, not a fresh timer at catch
            # time with a null status (review-9 B5)
            _record_attempt(provider, model, "transport-failure", t0, None,
                            str(exc), None, exc.http_status)
            last_err = str(exc)
            time.sleep(max(exc.retry_after, 5 * (attempt + 1)))
            continue
        except Exception:
            # a post-response handling failure (refusal/length/parse) was
            # BILLED — settle with the known usage when the response
            # carried a valid one, conservatively otherwise (review-10 B5)
            known = _validated_usage(provider, getattr(_tls, "last_usage", None))
            _settle(provider, model, reserved, est_in, known, row_id,
                    transport_failed=known is None)
            raise
        finally:
            _tls.attempt_row_id = None
            _tls.reservation_row_id = None
        # review-10 B3: usage is VALIDATED; missing/malformed usage keeps
        # the conservative reservation, never $0
        classes = _validated_usage(provider, usage_raw)
        _settle(provider, model, reserved, est_in, classes, row_id)
        return text
    raise RuntimeError(f"API unreachable after {RETRIES} attempts "
                       f"(last: {last_err})")


def list_openai_models() -> list[str]:
    resp = _session().get(
        OPENAI_MODELS_URL,
        headers={"Authorization": f"Bearer {_key_for('openai')}"},
        timeout=60, allow_redirects=False)
    resp.raise_for_status()
    return sorted(m["id"] for m in resp.json().get("data", []))


def main() -> int:
    """Campaign administration CLI (review-9 B1): campaign creation is a
    deliberate owner-authorized step, separate from any spending code."""
    import argparse
    ap = argparse.ArgumentParser(prog="python3 -m pipeline.llm_api")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create-campaign")
    c.add_argument("--approval-id", required=True)
    c.add_argument("--provider", required=True,
                   choices=["openai", "anthropic", "google"])
    c.add_argument("--model", required=True)
    c.add_argument("--cap-usd", type=float, required=True)
    c.add_argument("--purpose", required=True)
    a = sub.add_parser("amend-campaign",
                       help="append to a campaign's purpose (dated, "
                            "event-logged); caps and bindings are immutable")
    a.add_argument("--approval-id", required=True)
    a.add_argument("--append-purpose", required=True)
    cl = sub.add_parser("close-campaign",
                        help="terminally close a campaign after "
                             "provider-console reconciliation")
    cl.add_argument("--approval-id", required=True)
    cl.add_argument("--reconciliation-note", required=True)
    sub.add_parser("show-campaigns")
    args = ap.parse_args()
    import sqlite3
    if args.cmd == "create-campaign":
        create_campaign(db.DB_PATH, args.approval_id, args.provider,
                        args.model, args.cap_usd, args.purpose)
        print(f"campaign {args.approval_id} created "
              f"({args.provider}/{args.model}, ${args.cap_usd:.2f})")
    elif args.cmd == "amend-campaign":
        con = sqlite3.connect(str(db.DB_PATH), timeout=60)
        try:
            row = con.execute("SELECT purpose FROM budget_campaigns WHERE "
                              "approval_id=?", (args.approval_id,)).fetchone()
            if row is None:
                raise SystemExit(f"unknown campaign {args.approval_id!r}")
            with con:
                con.execute(
                    "UPDATE budget_campaigns SET purpose=? WHERE approval_id=?",
                    (f"{row[0] or ''} | {_ts()}: {args.append_purpose}",
                     args.approval_id))
                con.execute(
                    "INSERT INTO campaign_events (ts, approval_id, event, "
                    "detail_json) VALUES (?,?,?,?)",
                    (_ts(), args.approval_id, "amended",
                     json.dumps({"append_purpose": args.append_purpose})))
            print("purpose amended (append-only, event-logged)")
        finally:
            con.close()
    elif args.cmd == "close-campaign":
        con = sqlite3.connect(str(db.DB_PATH), timeout=60)
        con.isolation_level = None
        try:
            # review-11 B3: the final amount is computed INSIDE the closing
            # write transaction, after refusing unresolved reservations —
            # a request admitted just before closure can no longer settle
            # after the "final" number is recorded
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT status FROM budget_campaigns WHERE "
                              "approval_id=?", (args.approval_id,)).fetchone()
            if row is None:
                raise SystemExit(f"unknown campaign {args.approval_id!r}")
            if row[0] == "closed":
                raise SystemExit(f"campaign {args.approval_id!r} is already "
                                 "closed — record a superseding "
                                 "reconciliation event instead")
            open_res = con.execute(
                "SELECT COUNT(*) FROM api_spend WHERE approval_id=? AND "
                "kind='reserved'", (args.approval_id,)).fetchone()[0]
            if open_res:
                raise SystemExit(f"{open_res} unresolved reservation(s) — "
                                 "wait for every admitted request to reach "
                                 "a terminal state before closing")
            spent = con.execute(
                "SELECT COALESCE(SUM(usd),0) FROM api_spend WHERE "
                "approval_id=?", (args.approval_id,)).fetchone()[0]
            con.execute(
                "UPDATE budget_campaigns SET status='closed', closed_at=? "
                "WHERE approval_id=?", (_ts(), args.approval_id))
            con.execute(
                "INSERT INTO campaign_events (ts, approval_id, event, "
                "detail_json) VALUES (?,?,?,?)",
                (_ts(), args.approval_id, "closed",
                 json.dumps({"final_ledger_usd": spent,
                             "reconciliation_note":
                                 args.reconciliation_note})))
            con.execute("COMMIT")
            print(f"campaign {args.approval_id} closed at ${spent:.4f}")
        except BaseException:
            try:
                con.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            con.close()
    else:
        con = sqlite3.connect(str(db.DB_PATH), timeout=60)
        try:
            for r in con.execute(
                    "SELECT approval_id, provider, model, cap_usd, status, "
                    "purpose FROM budget_campaigns"):
                spent = con.execute(
                    "SELECT COALESCE(SUM(usd),0) FROM api_spend WHERE "
                    "approval_id=?", (r[0],)).fetchone()[0]
                print(f"{r[0]}: {r[1]}/{r[2]} cap ${r[3]:.2f} "
                      f"spent ${spent:.4f} [{r[4]}] — {r[5]}")
        finally:
            con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
