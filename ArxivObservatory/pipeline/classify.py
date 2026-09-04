"""Stage-1 LLM classification of scan hits.

Two backends share one prompt/validator/storage protocol:
- codex (default): batched through the headless codex agent CLI
- api: direct non-agentic HTTP calls (Anthropic/OpenAI/Google via
  pipeline/llm_api.py) — tools off, temperature 0 where supported, ONE PAPER
  PER REQUEST (isolation is structural, satisfying the freeze contract's
  isolate gate; review-4 P0-4's preferred boundary), token usage metered

Hits are merged into per-paper snippets (nearby hits share one snippet), then
batches go to the backend with a strict-JSON annotation prompt whose label
definitions come verbatim from pipeline/taxonomy.py (versioned). The LLM is a
second retrieval system, not ground truth.

v2 protocol discipline (LB-05/06):
- every invocation is an immutable classification_run recording backend,
  pinned model, prompt hash, taxonomy version, and params
- one classification_items row per snippet — including invalid and failed
  ones — plus normalized classification_evidence links to scan hits
- responses are validated against a closed schema (enums from taxonomy.py,
  confidence range, bounded strings); the evidence quote is grounded against
  the exact snippet text that was sent
- --isolate puts each paper in its own model call (prompt-injection
  containment); --model pins the codex model (-m) and is recorded
- failures are durable and the exit code is nonzero if any batch failed

Usage:
    python3 -m pipeline.classify --runs tex-20260810T154813 --model gpt-5.4-codex
    python3 -m pipeline.classify --runs tex-... meta-... --isolate --workers 4
    python3 -m pipeline.classify --resume cls-20260810T160000 --runs tex-...
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import db, runs, taxonomy

BATCH_SIZE = 30
MERGE_GAP = 600          # hits closer than this (same member) share a snippet
SNIPPET_MAX = 2400       # chars of context sent per snippet
MAX_QUOTE_CHARS = 600
MAX_LIST_ITEMS = 20
MAX_STR_CHARS = 120

PROMPT_TEMPLATE = """\
You are an expert annotator for a metascience study measuring the DISCLOSED, \
actively invoked use of generative-AI systems performing DELEGATED, \
traditionally human intellectual work in mathematics research papers \
(non-delegated instrument/artifact use is classified topic_only unless a \
separate delegated use is disclosed). Each snippet below comes from the \
LaTeX source or arXiv metadata of a math paper and contains at least one \
AI-related keyword (marked terms listed per snippet). Classify each snippet.

{definitions}

Additional output fields:
- tools: canonical tool/system names mentioned as USED (e.g. "ChatGPT", \
"Claude", "Gemini", "Copilot", "Danus", "Lean"). Empty unless author_use.
- models: exact model strings as written, verbatim (e.g. "GPT-5.5 Pro", \
"Claude Opus 4.8", "o4-mini"). Empty if no specific model named.
- confidence: 0.0-1.0.
- quote: shortest VERBATIM quote from the snippet that justifies polarity. \
Must be copied character-for-character from the snippet text.

Reply with ONLY a JSON object {{"labels": [...]}} with one object per
snippet, in the same order:
{{"id": <snippet id>, "polarity": "...", "tools": [...], "models": [...],
 "categories": [...], "epistemic_impact": "...", "locations": ["..."],
 "flags": {flags_example},
 "confidence": 0.0-1.0, "quote": "..."}}
Every field is required: use [] for empty lists, "not_applicable" for
epistemic_impact on non-author_use labels, ["unknown"] for locations, and
include EVERY flag key with an explicit true/false. epistemic_impact is
the strongest explicitly GRADED use in the snippet (vaguer or fruitless
co-uses never change it).
Write the quote on ONE line: replace source line breaks with single spaces,
and escape every backslash as \\\\ (LaTeX commands must survive JSON
round-tripping unchanged).

Snippets follow, separated by lines of dashes.
"""


def build_prompt_header() -> str:
    # the flags example is GENERATED from taxonomy.FLAGS so the prompt can
    # never name fewer flag keys than the strict provider schema requires
    # (review-8 A2: the hand-written example omitted method_component)
    flags_example = json.dumps({f: False for f in taxonomy.FLAGS})
    return PROMPT_TEMPLATE.format(definitions=taxonomy.prompt_definitions(),
                                  flags_example=flags_example)


def merge_snippets(con, scan_runs: list[str]) -> list[dict]:
    """Group hits into classifiable snippets (per paper-version, member,
    proximity). The key includes version AND scan run, so hits from different
    source versions or protocols can never merge into one snippet (F10)."""
    q = ("SELECT id, arxiv_id, version, source_kind, file_member, term, tier, offset, "
         "context, rule_class, scan_run FROM scan_hits WHERE scan_run IN (%s) "
         "AND tier IN ('llm','generic') AND rule_class != 'known_fp' "
         "ORDER BY arxiv_id, version, scan_run, source_kind, file_member, offset"
         % ",".join("?" * len(scan_runs)))
    snippets: list[dict] = []
    cur = None
    for r in con.execute(q, scan_runs):
        key = (r["arxiv_id"], r["version"], r["scan_run"], r["source_kind"],
               r["file_member"])
        if (cur is None or cur["key"] != key
                or r["offset"] - cur["last_offset"] > MERGE_GAP):
            cur = {"key": key, "arxiv_id": r["arxiv_id"], "version": r["version"],
                   "scan_run": r["scan_run"],
                   "source_kind": r["source_kind"], "member": r["file_member"],
                   "terms": [], "context": r["context"], "last_offset": r["offset"],
                   "hit_ids": []}
            snippets.append(cur)
        cur["terms"].append(r["term"])
        cur["hit_ids"].append(r["id"])
        cur["last_offset"] = r["offset"]
        if len(r["context"]) > len(cur["context"]):
            cur["context"] = r["context"]
    return snippets


def finalize_snippets(snippets: list[dict], prompt_sha: str, model: str,
                      isolate: bool) -> None:
    """Full-protocol input hash: paper, version, location, terms, exact text,
    prompt, taxonomy, model, isolation mode (review: cache identity must
    cover the whole envelope)."""
    for s in snippets:
        s["terms"] = sorted(set(s["terms"]))
        s["context"] = s["context"][:SNIPPET_MAX]
        s["input_hash"] = hashlib.sha256("|".join([
            s["arxiv_id"], str(s["version"]), s.get("scan_run") or "",
            s["source_kind"] or "", s["member"] or "", ",".join(s["terms"]),
            s["context"], prompt_sha, taxonomy.TAXONOMY_VERSION, model,
            str(int(isolate)),
        ]).encode()).hexdigest()


def build_prompt(header: str, batch: list[dict]) -> str:
    # no arXiv id in the provider-visible prompt (review-7 vendor
    # minimization): the model needs the text, not the paper's identity
    parts = [header]
    for i, s in enumerate(batch):
        parts.append(
            f"----------\nSNIPPET {i} (source={s['source_kind']}, "
            f"marked terms: {', '.join(s['terms'])}):\n{s['context']}\n")
    parts.append('----------\nRemember: ONLY the JSON object '
                 '{"labels": [...]}, no prose.')
    return "\n".join(parts)


_CONTROL_RE = re.compile(r"[\x00-\x1f]")


def _reject_control_chars(obj) -> None:
    """TeX copied with under-escaped backslashes decodes to control
    characters while remaining VALID JSON: \\beta -> backspace+'eta',
    \\nabla -> newline+'abla', \\tau -> tab+'au', \\ref -> CR+'ef'
    (review-5 P0-7, tightened per review-6 P0-3 to ALL C0 controls — the
    prompt requires single-line quotes, so \\n\\r\\t are never legitimate
    either). Raising routes the reply to the re-ask retry."""
    if isinstance(obj, str):
        if _CONTROL_RE.search(obj):
            raise ValueError("control character in decoded string "
                             "(under-escaped TeX backslash?)")
    elif isinstance(obj, list):
        for x in obj:
            _reject_control_chars(x)
    elif isinstance(obj, dict):
        for v in obj.values():
            _reject_control_chars(v)


def extract_json(text: str):
    """Strict parse: NO regex repair (review-5 P0-7 — the repair silently
    corrupted TeX commands whose first letter is a legal JSON escape).
    Malformed JSON and control-char corruption both raise, which triggers the
    single re-ask; the API backend additionally enforces provider-native
    schemas so this path is a backstop there."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end <= start:
        raise ValueError("no JSON array found")
    labels = json.loads(text[start:end + 1], object_pairs_hook=_no_dup_keys)
    _reject_control_chars(labels)
    return labels


def _no_dup_keys(pairs):
    """Duplicate JSON keys silently last-win in json.loads — reject them
    (review-6 P0-2)."""
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError(f"duplicate JSON key {k!r}")
        d[k] = v
    return d


def call_codex(prompt: str, model: str | None, effort: str | None = None,
               timeout: int = 600) -> str:
    with tempfile.NamedTemporaryFile("r", suffix=".txt", delete=False) as out:
        out_path = Path(out.name)
    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only"]
    if model:
        cmd += ["-m", model]
    if effort:
        cmd += ["-c", f"model_reasoning_effort={effort}"]
    cmd += ["-o", str(out_path), "-"]
    try:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                              timeout=timeout)
        if proc.returncode != 0:
            raise RuntimeError(f"codex exec rc={proc.returncode}: {proc.stderr[-500:]}")
        return out_path.read_text()
    finally:
        out_path.unlink(missing_ok=True)


_WS_RE = re.compile(r"\s+")


def _norm(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def ground_quote(quote: str, snippet_text: str) -> bool:
    """Whitespace-normalized substring check: did the model copy its evidence
    verbatim from the text it was shown?"""
    if not quote:
        return False
    return _norm(quote) in _norm(snippet_text)


ALLOWED_KEYS = {"polarity", "tools", "models", "categories", "epistemic_impact",
                "locations", "confidence", "quote", "flags"}


def validate_label(lab: dict, snippet_text: str) -> tuple[dict | None, list[str]]:
    """Strict closed-schema validation against taxonomy.py: invalid enum
    values, ranges, or missing required fields REJECT the label (clean=None)
    instead of being silently rewritten (codex re-review F7). The only
    coercion is clearing usage fields on non-author_use labels, which are
    definitionally empty and never enter statistics."""
    problems: list[str] = []
    if not isinstance(lab, dict):
        return None, ["not an object"]
    extra = sorted(set(lab) - ALLOWED_KEYS)
    if extra:
        return None, [f"unknown keys {extra}"]
    # review-6 P0-2: absent required fields are REJECTED, never defaulted —
    # a silent default hides provider/schema drift from the validator
    missing = sorted(ALLOWED_KEYS - set(lab))
    if missing:
        return None, [f"missing required keys {missing}"]
    polarity = lab.get("polarity")
    if polarity not in taxonomy.POLARITIES:
        return None, [f"bad polarity {polarity!r}"]

    def str_list(key: str) -> list[str] | None:
        val = lab[key]
        if not isinstance(val, list) or len(val) > MAX_LIST_ITEMS \
                or not all(isinstance(x, str) for x in val):
            problems.append(f"{key} not a bounded list of strings")
            return None
        if any(len(x) > MAX_STR_CHARS for x in val):
            # reject, don't truncate: truncation hides drift (review-6)
            problems.append(f"{key} entry exceeds {MAX_STR_CHARS} chars")
            return None
        return sorted({x.strip() for x in val if x.strip()})

    tools, models = str_list("tools"), str_list("models")
    categories = str_list("categories")
    if tools is None or models is None or categories is None:
        return None, problems
    bad_cats = [c for c in categories if c not in taxonomy.CATEGORIES]
    if bad_cats:
        return None, [f"unknown categories {bad_cats}"]
    impact = lab["epistemic_impact"]
    if impact not in taxonomy.IMPACTS:
        return None, [f"unknown impact {impact!r}"]
    locations = lab["locations"]
    if (not isinstance(locations, list) or not locations
            or not all(isinstance(l, str) for l in locations)):
        return None, ["locations must be a non-empty list"]
    bad_locs = sorted(set(locations) - set(taxonomy.LOCATIONS))
    if bad_locs:
        return None, [f"unknown locations {bad_locs}"]
    locations = sorted(set(locations))
    confidence = lab["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        # bool is an int subclass: true would silently become 1.0 (review-6)
        return None, ["confidence must be a JSON number"]
    confidence = float(confidence)
    if not (confidence == confidence and 0.0 <= confidence <= 1.0):
        return None, [f"confidence {confidence} out of range or non-finite"]
    quote = lab["quote"]
    if not isinstance(quote, str):
        return None, ["quote must be a string"]
    if len(quote) > MAX_QUOTE_CHARS:
        return None, [f"quote exceeds {MAX_QUOTE_CHARS} chars"]
    quote = quote.strip()
    flags_in = lab["flags"]
    if not isinstance(flags_in, dict):
        return None, ["flags must be an object"]
    bad_flags = sorted(set(flags_in) - set(taxonomy.FLAGS))
    if bad_flags:
        return None, [f"unknown flags {bad_flags}"]
    # review-8 A2: the provider-native strict schema requires EVERY flag key
    # — the local fail-closed authority must not be weaker than the provider
    missing_flags = sorted(set(taxonomy.FLAGS) - set(flags_in))
    if missing_flags:
        return None, [f"missing flag keys {missing_flags}"]
    if not all(isinstance(v, bool) for v in flags_in.values()):
        # bool("false") is True — literal booleans only (review-3)
        return None, ["flag values must be JSON booleans"]
    flags = dict(flags_in)
    if polarity == "author_use":
        if not quote:
            return None, ["missing quote for author_use"]
        if not categories:
            return None, ["author_use needs at least one category "
                          "(use 'unspecified' when the role is unknown)"]
        # cross-field invariants shared with the human ingest path
        # (review-7 P0-1, unified per review-8 A3)
        invariant_problems = taxonomy.cross_field_problems(True, impact, flags)
        if invariant_problems:
            return None, invariant_problems
    elif polarity == "non_use_statement" and not quote:
        return None, ["missing quote for non_use_statement"]
    elif polarity == "unclear" and not quote:
        # v2.8 R6: unclear requires an explicit (if uninterpretable)
        # statement — there must be a quotable statement
        return None, ["missing quote for unclear"]
    else:
        # review-9 A4: a semantic contradiction (catalytic on a non-use
        # polarity) is REJECTED and re-asked, exactly like the human ingest
        # path — never silently repaired
        invariant_problems = taxonomy.cross_field_problems(False, impact, flags)
        if invariant_problems:
            return None, invariant_problems
        # non-use snippets carry no usage labels (v2.8: catalytic is the
        # only flag, and it is author_use-only)
        if categories or impact != "not_applicable" or tools:
            problems.append("usage fields on non-author_use cleared")
        categories, impact, tools = [], "not_applicable", []
        flags = {k: False for k in taxonomy.FLAGS}
    clean = {"polarity": polarity, "tools": tools, "models": models,
             "categories": categories, "epistemic_impact": impact,
             "locations": locations, "confidence": confidence, "quote": quote,
             "flags": flags,
             "quote_grounded": ground_quote(quote, snippet_text)}
    return clean, problems


def make_caller(backend: str, model: str | None, effort: str | None,
                fence=None):
    """Returns prompt -> raw-text. 'codex' shells out to the agent CLI;
    'api' does a direct non-agentic structured-output HTTP call (tools off,
    temperature 0 where supported) — review-4 P0-4's preferred boundary.
    With a fence (the run lease), every PHYSICAL dispatch checks the fence
    first — queued or splitting work stops paying the moment the lease is
    lost (review-9 B3)."""
    if backend == "api":
        from . import llm_api
        if not model:
            sys.exit("--backend api requires an explicit --model (exact API "
                     "model id, e.g. claude-haiku-4-5-20251001)")

        def call(prompt: str) -> str:
            if fence is not None and fence.lost.is_set():
                raise RuntimeError("lease lost — dispatch fenced (review-9 B3)")
            return llm_api.call_api(prompt, model)
        return call
    return lambda prompt: call_codex(prompt, model, effort)


class _RequestError(RuntimeError):
    """Wraps a request failure together with every prompt/response exchange
    that led to it, so FAILED split nodes and re-asks keep their exact
    prompt hashes and physical attempts (review-9 B4 — the old failure path
    recorded prompt=None and collapsed two calls into one record)."""

    def __init__(self, cause: Exception, exchanges: list[dict]):
        super().__init__(str(cause))
        self.cause = cause
        self.exchanges = exchanges


def _drain_attempts() -> list[dict]:
    return ATTEMPT_SOURCE[0]() if ATTEMPT_SOURCE[0] else []


def _attempt(batch: list[dict], prompt: str, call, split_path: str = "R"
             ) -> tuple[list[tuple[dict, dict | None, dict, list[str]]],
                        list[dict]]:
    """One logical request. Returns (per-snippet results, exchanges), where
    each exchange = {prompt, raw, attempts} for one DISTINCT prompt sent
    (the parse re-ask is its own exchange). Failures raise _RequestError
    carrying all exchanges so far."""
    exchanges: list[dict] = []

    def do_call(p: str) -> str:
        if REQUEST_CTX[0]:
            idx = len(exchanges)
            REQUEST_CTX[0]({
                "split_path": split_path + (f".reask{idx}" if idx else ""),
                "snippet_hashes": [s["input_hash"] for s in batch]})
        try:
            raw_ = call(p)
        except Exception as exc:
            exchanges.append({"prompt": p, "raw": None,
                              "attempts": _drain_attempts()})
            raise _RequestError(exc, exchanges) from exc
        exchanges.append({"prompt": p, "raw": raw_,
                          "attempts": _drain_attempts()})
        return raw_

    raw = do_call(prompt)
    try:
        labels = extract_json(raw)
    except (ValueError, json.JSONDecodeError):
        raw = do_call(prompt + "\n\nYour previous reply could not be parsed. "
                      'Reply with ONLY the JSON object {"labels": [...]}, '
                      "nothing else.")
        try:
            labels = extract_json(raw)
        except (ValueError, json.JSONDecodeError) as exc:
            raise _RequestError(exc, exchanges) from exc

    def fail(msg: str):
        raise _RequestError(ValueError(msg), exchanges)

    if not isinstance(labels, list) or len(labels) != len(batch):
        fail(f"expected {len(batch)} labels, got "
             f"{len(labels) if isinstance(labels, list) else type(labels)}")
    # map replies by their echoed id — never trust positional order
    by_id: dict[int, dict] = {}
    for lab in labels:
        if (not isinstance(lab, dict) or isinstance(lab.get("id"), bool)
                or not isinstance(lab.get("id"), int)):
            # bool passes isinstance(int) — reject explicitly (review-6)
            fail("label without integer id")
        by_id[lab["id"]] = lab
    if sorted(by_id) != list(range(len(batch))):
        fail(f"label ids {sorted(by_id)} don't cover batch")
    out = []
    for i, s in enumerate(batch):
        raw_lab = dict(by_id[i])
        raw_lab.pop("id", None)
        clean, problems = validate_label(raw_lab, s["context"])
        out.append((s, clean, raw_lab, problems))
    return out, exchanges


# review-8 A2: the retry must demand the SAME top-level shape as the
# original contract (the old text asked for a "corrected JSON array")
RETRY_SCHEMA_NOTE = ('Reply again with ONLY the corrected JSON object '
                     '{"labels": [...]}, using exactly the allowed field '
                     'names and enum values.')

_SPLITTABLE_MARKERS = ("truncated", "expected", "label ids", "don't cover",
                       "duplicate", "no JSON array", "control character")


def _splittable(exc: Exception) -> bool:
    """Failures worth bisecting: output-length truncation, id-coverage or
    schema/parse failures — provider-side effects of oversized batches.
    Transport exhaustion and budget stops are NOT splittable (they would
    only multiply paid calls)."""
    if isinstance(exc, _RequestError):
        exc = exc.cause
    if isinstance(exc, (json.JSONDecodeError, ValueError)):
        return True
    return isinstance(exc, RuntimeError) and any(
        m in str(exc) for m in _SPLITTABLE_MARKERS)


# set to llm_api.drain_attempts by main() for the api backend so every
# request record captures exactly the physical attempts of ITS OWN call
# (thread-local in llm_api — review-8 B3); None for the codex backend
ATTEMPT_SOURCE: list = [None]
# set to llm_api.set_request_context for the api backend: split path +
# ordered snippet hashes reach the PRE-DISPATCH attempt row (review-10 B7)
REQUEST_CTX: list = [None]


def _fence_check(con, lease) -> None:
    """Durable holder verification INSIDE the same transaction as the writes
    it protects (review-10 B6). Under WAL, a takeover between this read and
    the write upgrade aborts the transaction (SQLITE_BUSY_SNAPSHOT), so a
    store can never land after a takeover either way."""
    if lease is None:
        return
    row = con.execute("SELECT holder FROM run_leases WHERE run_id=?",
                      (lease.run_id,)).fetchone()
    if row is None or row[0] != lease.holder:
        raise LeaseHeld(f"lease for run '{lease.run_id}' is no longer held "
                        "by this process — refusing to store")


def _bail_release(lease) -> None:
    if lease is not None and not lease.lost.is_set():
        try:
            lease.release()
        except Exception:
            pass


def _records_from(batch: list[dict], split_path: str,
                  exchanges: list[dict], error: str | None = None
                  ) -> list[dict]:
    """One durable record per DISTINCT prompt sent (review-9 B4): the exact
    ordered snippet hashes (child batches restart snippet ids at 0 — id i
    maps to snippet_hashes[i]), the deterministic split path, prompt AND
    response hashes even on failure, and the physical attempts (with
    reservation/attempt row ids) that belong to that exchange alone."""
    hashes = [s["input_hash"] for s in batch]
    recs = []
    for i, ex in enumerate(exchanges):
        recs.append({
            "split_path": split_path + (f".reask{i}" if i else ""),
            "snippet_hashes": hashes,
            "prompt_sha256": (hashlib.sha256(ex["prompt"].encode()).hexdigest()
                              if ex.get("prompt") else None),
            "response_sha256": (hashlib.sha256(ex["raw"].encode()).hexdigest()
                                if ex.get("raw") else None),
            "response": ex.get("raw"),
            "attempts": ex.get("attempts") or [],
        })
    if error:
        if not recs:  # non-request failure (tooling bug): still durable
            recs.append({"split_path": split_path, "snippet_hashes": hashes,
                         "prompt_sha256": None, "response_sha256": None,
                         "response": None, "attempts": _drain_attempts()})
        recs[-1]["error"] = error
    return recs


def classify_batch(batch: list[dict], header: str, call, split_path: str = "R"
                   ) -> tuple[list, list[dict], list[tuple[dict, Exception]]]:
    """Returns (per-snippet results, request records, failed snippets).

    Adaptive deterministic bisection (review-7 P0-4): a multi-snippet batch
    that fails with a splittable error (length truncation, id coverage,
    schema) is halved in stable order and each half retried recursively; a
    single snippet that still fails becomes a reason-coded terminal failure
    for THAT snippet only — the old fixed-batch retry repaid the same
    truncation and made whole complex papers vanish. Split paths are
    deterministic: R, R.L, R.R, R.L.L, ... ('!' suffix = failed request,
    '.reaskN' = parse re-ask exchange)."""
    try:
        out, recs = _classify_once(batch, header, call, split_path)
        return out, recs, []
    except _RequestError as exc:
        cause = exc.cause
        recs = _records_from(batch, split_path + "!", exc.exchanges,
                             error=f"{type(cause).__name__}: {str(cause)[:200]}")
    except Exception as exc:  # noqa: BLE001 - converted to per-snippet state
        cause = exc
        recs = _records_from(batch, split_path + "!", [],
                             error=f"{type(exc).__name__}: {str(exc)[:200]}")
    if len(batch) == 1 or not _splittable(cause):
        return [], recs, [(s, cause) for s in batch]
    mid = len(batch) // 2
    o1, r1, f1 = classify_batch(batch[:mid], header, call, split_path + ".L")
    o2, r2, f2 = classify_batch(batch[mid:], header, call, split_path + ".R")
    return o1 + o2, recs + r1 + r2, f1 + f2


def _classify_once(batch: list[dict], header: str, call, split_path: str = "R"
                   ) -> tuple[list[tuple[dict, dict | None, dict, list[str]]], list[dict]]:
    """One batch attempt. Schema-invalid labels get ONE full-batch retry
    naming the violations; per-snippet the valid result wins (F7)."""
    prompt = build_prompt(header, batch)
    out, exchanges = _attempt(batch, prompt, call, split_path)
    recs = _records_from(batch, split_path, exchanges)
    invalid = [(i, probs) for i, (_, clean, _, probs) in enumerate(out)
               if clean is None]
    if invalid:
        complaint = "; ".join(f"snippet {i}: {', '.join(p)}" for i, p in invalid[:10])
        retry_prompt = (prompt + "\n\nYour previous reply violated the schema "
                        f"({complaint}). " + RETRY_SCHEMA_NOTE)
        try:
            out2, ex2 = _attempt(batch, retry_prompt, call,
                                 split_path + ".schema-retry")
            recs += _records_from(batch, split_path + ".schema-retry", ex2)
            out = [o2 if o1[1] is None and o2[1] is not None else o1
                   for o1, o2 in zip(out, out2)]
        except _RequestError as exc:
            # failed schema retries keep their prompt AND any response hash
            recs += _records_from(
                batch, split_path + ".schema-retry!", exc.exchanges,
                error=f"{type(exc.cause).__name__}: {str(exc.cause)[:200]}")
            # keep first-attempt results; invalids stay durable
    return out, recs


def make_batches(todo: list[dict], isolate: bool) -> list[list[dict]]:
    if not isolate:
        return [todo[i:i + BATCH_SIZE] for i in range(0, len(todo), BATCH_SIZE)]
    by_paper: dict[str, list[dict]] = {}
    for s in todo:
        by_paper.setdefault(s["arxiv_id"], []).append(s)
    batches = []
    for paper_snips in by_paper.values():
        batches.extend(paper_snips[i:i + BATCH_SIZE]
                       for i in range(0, len(paper_snips), BATCH_SIZE))
    return batches


def store_results(con, run_id: str, results, now: str, lease=None) -> None:
    with con:
        _fence_check(con, lease)  # in-transaction (review-10 B6)
        for s, clean, raw_lab, problems in results:
            status = "ok" if clean else "invalid:" + "; ".join(problems)[:200]
            row = (run_id, s["arxiv_id"], s["version"], s["source_kind"], s["member"],
                   s["input_hash"], s["context"], status,
                   clean["polarity"] if clean else None,
                   json.dumps({**clean, "problems": problems}) if clean else None,
                   json.dumps(raw_lab), clean["quote"] if clean else None,
                   int(clean["quote_grounded"]) if clean else None, now)
            cur = con.execute(
                "INSERT OR IGNORE INTO classification_items "
                "(run_id, arxiv_id, version, source_kind, file_member, snippet_sha256, "
                "snippet_text, status, polarity, label_json, raw_response, quote, "
                "quote_grounded, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
            if cur.rowcount:
                item_id = cur.lastrowid
            else:
                old = con.execute(
                    "SELECT id, status FROM classification_items WHERE run_id=? "
                    "AND snippet_sha256=?", (run_id, s["input_hash"])).fetchone()
                if old is None:
                    continue
                item_id = old["id"]
                # a retry may upgrade a durable error/invalid row to ok —
                # never the other way around (F6). Content-identical snippets
                # from a DIFFERENT hit cluster land here too: keep the row but
                # still record this cluster's evidence edges below (review-4:
                # a `continue` here silently dropped 63 hit edges)
                if old["status"] != "ok" and clean is not None:
                    con.execute(
                        "UPDATE classification_items SET status=?, polarity=?, "
                        "label_json=?, raw_response=?, quote=?, quote_grounded=?, "
                        "created_at=? WHERE id=?",
                        (status, clean["polarity"],
                         json.dumps({**clean, "problems": problems}),
                         json.dumps(raw_lab), clean["quote"],
                         int(clean["quote_grounded"]), now, old["id"]))
            con.executemany(
                "INSERT OR IGNORE INTO classification_evidence VALUES (?,?)",
                [(item_id, hid) for hid in s["hit_ids"]])


LEASE_STALE_S = 600
LEASE_HEARTBEAT_S = 120


class LeaseHeld(RuntimeError):
    pass


class RunLease:
    """Single-writer lease with holder fencing (review-8 B2): acquisition is
    one BEGIN IMMEDIATE check-and-upsert (two starters serialize; the loser
    sees a fresh heartbeat and refuses); the holder token includes random
    bytes so an old process can never refresh or delete its successor's
    lease (every write is WHERE run_id AND holder); heartbeats come from a
    time-driven keeper thread, so a long request/retry/split chain cannot
    be falsely stolen; a failed fenced heartbeat sets .lost and the main
    loop stops storing results or dispatching paid work."""

    def __init__(self, db_path, run_id: str):
        self.db_path, self.run_id = str(db_path), run_id
        self.holder = f"{socket.gethostname()}:{os.getpid()}:{os.urandom(8).hex()}"
        self.lost = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.took_over_from: str | None = None

    def _con(self):
        import sqlite3
        con = sqlite3.connect(self.db_path, timeout=60)
        con.isolation_level = None
        return con

    def acquire(self) -> None:
        con = self._con()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT holder, heartbeat_at FROM run_leases WHERE run_id=?",
                (self.run_id,)).fetchone()
            if row is not None and row[0] != self.holder:
                hb = _dt.datetime.fromisoformat(row[1])
                age = (_dt.datetime.now(_dt.timezone.utc) - hb).total_seconds()
                if age < LEASE_STALE_S:
                    con.execute("ROLLBACK")
                    raise LeaseHeld(
                        f"run '{self.run_id}' is leased by {row[0]} "
                        f"(heartbeat {int(age)}s ago) — refusing concurrent "
                        "paid work; wait for the lease to expire or stop "
                        "the other process")
                self.took_over_from = row[0]  # stale takeover, audited
            con.execute(
                "INSERT INTO run_leases (run_id, holder, acquired_at, "
                "heartbeat_at, generation) VALUES (?,?,?,?,1) "
                "ON CONFLICT(run_id) DO UPDATE "
                "SET holder=excluded.holder, acquired_at=excluded.acquired_at, "
                "heartbeat_at=excluded.heartbeat_at, "
                "generation=run_leases.generation+1",
                (self.run_id, self.holder, runs.utcnow(), runs.utcnow()))
            con.execute("COMMIT")
        except BaseException:
            try:
                con.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            con.close()
        self._thread = threading.Thread(target=self._keeper, daemon=True,
                                        name=f"lease-{self.run_id}")
        self._thread.start()

    def heartbeat(self) -> bool:
        """Fenced heartbeat; False means the lease is no longer ours."""
        con = self._con()
        try:
            cur = con.execute(
                "UPDATE run_leases SET heartbeat_at=? WHERE run_id=? AND holder=?",
                (runs.utcnow(), self.run_id, self.holder))
            return cur.rowcount == 1
        finally:
            con.close()

    def _keeper(self) -> None:
        misses = 0
        while not self._stop.wait(LEASE_HEARTBEAT_S):
            try:
                if not self.heartbeat():
                    self.lost.set()
                    return
                misses = 0
            except Exception:
                # transient DB contention: retry next tick — but sustained
                # failure past a grace window means we can no longer prove
                # we hold the lease, so treat it as LOST before another
                # process's stale takeover could pass (review-9 B3)
                misses += 1
                if misses >= 3:
                    self.lost.set()
                    return

    def release(self) -> None:
        self._stop.set()
        con = self._con()
        try:
            con.execute("DELETE FROM run_leases WHERE run_id=? AND holder=?",
                        (self.run_id, self.holder))
        finally:
            con.close()


def store_batch_error(con, run_id: str, batch: list[dict], exc: Exception,
                      now: str, lease=None) -> None:
    with con:
        _fence_check(con, lease)  # error stores are fenced too (review-10 B6)
        for s in batch:
            cur = con.execute(
                "INSERT OR IGNORE INTO classification_items "
                "(run_id, arxiv_id, version, source_kind, file_member, snippet_sha256, "
                "snippet_text, status, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (run_id, s["arxiv_id"], s["version"], s["source_kind"], s["member"],
                 s["input_hash"], s["context"],
                 f"error:{type(exc).__name__}: {str(exc)[:200]}", now))
            if cur.rowcount:
                # error items keep their evidence lineage too, so run-scoped
                # coverage queries see them (review-3 P0-3)
                con.executemany(
                    "INSERT OR IGNORE INTO classification_evidence VALUES (?,?)",
                    [(cur.lastrowid, hid) for hid in s["hit_ids"]])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True, help="scan run ids to classify")
    ap.add_argument("--backend", choices=["codex", "api"], default="codex",
                    help="codex = agent CLI (batched); api = direct "
                         "non-agentic HTTP call, one paper per request "
                         "(review-4 P0-4 preferred; implies --isolate)")
    ap.add_argument("--model", default=None,
                    help="codex: -m model; api: exact provider model id "
                         "(claude-*/gpt-*/gemini-*); recorded in the run")
    ap.add_argument("--effort", default=None,
                    choices=["minimal", "low", "medium", "high", "xhigh"],
                    help="codex reasoning effort override; part of the recorded "
                         "model identity")
    ap.add_argument("--isolate", action="store_true",
                    help="one paper per model call (prompt-injection containment)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit-batches", type=int, default=None)
    ap.add_argument("--max-total-tokens", type=int, default=None,
                    help="api: abort once cumulative input+output tokens "
                         "exceed this (budget guard for experiments)")
    ap.add_argument("--max-usd-per-provider", type=float, default=None,
                    help="api: hard USD cap per provider, enforced by "
                         "pre-dispatch reservation against a snapshotted "
                         "price table (owner budget, DECISIONS.md); "
                         "MANDATORY for --backend api")
    ap.add_argument("--budget-approval", default=None, metavar="ID",
                    help="api: owner spend-approval reference recorded with "
                         "the run (e.g. DECISIONS-2026-08-11); mandatory "
                         "for --backend api")
    ap.add_argument("--resume", default=None, metavar="RUN_ID",
                    help="continue an existing classification run")
    ap.add_argument("--papers-file", default=None, metavar="PATH",
                    help="restrict classification to the arXiv ids listed "
                         "one-per-line (input scoping, recorded in the "
                         "invocation ledger; used for tracked adherence "
                         "checks — review-9 A3)")
    args = ap.parse_args()

    campaign = None
    if args.backend == "api":
        from . import llm_api
        if args.effort:
            sys.exit("--effort is codex-only; api models are pinned by their id")
        if not args.model:
            sys.exit("--backend api requires --model (exact API model id)")
        provider = llm_api.provider_of_model(args.model)  # fail fast
        # review-9 B7: only the selected provider's key enters this process
        llm_api.load_env(provider)
        # review-7 Gate A: the cap and its owner approval are mandatory, and
        # only approved providers may spend (DECISIONS.md)
        if not args.max_usd_per_provider or args.max_usd_per_provider <= 0:
            sys.exit("--backend api requires a positive "
                     "--max-usd-per-provider (owner budget, DECISIONS.md)")
        if not args.budget_approval:
            sys.exit("--backend api requires --budget-approval <id> "
                     "referencing the owner spend approval")
        if provider not in ("openai", "anthropic") \
                and not os.environ.get("ARXIV_OBS_ALLOW_PROVIDER"):
            sys.exit(f"provider '{provider}' is not on the approved "
                     "allowlist (openai, anthropic — DECISIONS.md); set "
                     "ARXIV_OBS_ALLOW_PROVIDER=1 to override deliberately")
        # review-9 B1: fail closed on unknown approval ids — a campaign is
        # pre-created owner authority, never a CLI side effect. review-10
        # B5: validate the FULL binding before any run row exists, so a
        # typoed cap / wrong model / closed campaign cannot leave a phantom
        # 'running' run
        try:
            campaign = llm_api.get_campaign(db.DB_PATH, args.budget_approval)
        except RuntimeError as exc:
            sys.exit(str(exc))
        if campaign["status"] != "active":
            sys.exit(f"campaign {args.budget_approval!r} is "
                     f"{campaign['status']!r} — not spendable")
        if campaign["provider"] != provider or campaign["model"] != args.model:
            sys.exit(f"campaign {args.budget_approval!r} is bound to "
                     f"{campaign['provider']}/{campaign['model']}, not "
                     f"{provider}/{args.model}")
        if abs(campaign["cap_usd"] - args.max_usd_per_provider) > 1e-9:
            sys.exit(f"campaign cap is ${campaign['cap_usd']:.2f}; the CLI "
                     f"requested ${args.max_usd_per_provider:.2f} — one "
                     "campaign, one cap")
        args.isolate = True  # per-paper calls are inherent to the api backend
        llm_api.set_budget(args.max_total_tokens, args.max_usd_per_provider)

    # review-10 B1: the scoped target is part of the run's IDENTITY —
    # canonicalized before protocol creation, its hash in the protocol, its
    # full preimage in params_json, and a changed/omitted scope on resume
    # refuses via the protocol hash
    scope = scope_ids = None
    if args.papers_file:
        scope_ids = sorted({ln.strip() for ln in
                            Path(args.papers_file).read_text().splitlines()
                            if ln.strip()})
        if not scope_ids:
            sys.exit(f"--papers-file {args.papers_file} contains no ids")
        scope = {"mode": "papers-file", "n": len(scope_ids),
                 "ids_sha256": hashlib.sha256(
                     "\n".join(scope_ids).encode()).hexdigest(),
                 "purpose": "scoped adherence/dev subset — NEVER a "
                            "population output (review-10 B1)"}
        print(f"--papers-file: scoped to {len(scope_ids)} papers "
              f"(ids sha256 {scope['ids_sha256'][:12]}…)", flush=True)

    con = db.connect()
    # review-11 B5: a typo or a still-running scan must never produce a
    # plausible-looking (even empty) terminal classification
    for sr in args.runs:
        srow = con.execute("SELECT status FROM scan_runs WHERE run_id=?",
                           (sr,)).fetchone()
        if srow is None:
            sys.exit(f"scan run '{sr}' does not exist")
        if srow["status"] not in ("complete", "partial"):
            sys.exit(f"scan run '{sr}' has non-terminal status "
                     f"'{srow['status']}' — wait for it to finish")
    header = build_prompt_header()
    prompt_sha = hashlib.sha256(header.encode()).hexdigest()
    model_label = args.model or "codex-default(unpinned)"
    if args.effort:
        model_label += f"@{args.effort}"
    if not args.model:
        print("WARNING: model not pinned — fine for dev, not for analysis runs",
              flush=True)

    backend_label = args.backend
    schema_sha = max_out = None
    if args.backend == "api":
        from . import llm_api
        backend_label = f"api:{llm_api.provider_of_model(args.model)}"
        schema_sha = hashlib.sha256(json.dumps(
            llm_api.batch_schema(), sort_keys=True).encode()).hexdigest()
        max_out = llm_api.MAX_OUTPUT_TOKENS

    # ONE canonical protocol object; its hash is the resume identity
    # (review-6 P0-4: label-by-label comparison missed code, schema, and
    # decoder drift — a resumed run must be byte-identical protocol or a
    # new superseding run)
    tax_md = Path(__file__).parent.parent / "TAXONOMY.md"
    protocol = {"code_commit": db.code_commit(), "prompt_sha256": prompt_sha,
                "taxonomy": taxonomy.TAXONOMY_VERSION,
                "taxonomy_md_sha256": (hashlib.sha256(
                    tax_md.read_bytes()).hexdigest() if tax_md.exists()
                    else None),
                "backend": backend_label, "model": model_label,
                "isolate": args.isolate, "scan_runs": sorted(args.runs),
                "schema_sha256": schema_sha,
                "split_policy": "bisect-v1",
                "max_output_tokens": max_out,
                # review-8 B4: inference controls are part of the protocol
                # identity; provider-RETURNED identity is persisted per
                # attempt (api_attempts.returned_model/system_fingerprint)
                "inference_controls": (
                    {"anthropic_google_temperature": 0.0,
                     "openai_temperature": "provider-default (pinned chat "
                     "completions; not set)",
                     "openai_reasoning_effort": "medium (explicitly pinned; "
                     "documented default as of 2026-08-12 — review-9 A6)",
                     "openai_store": False}
                    if args.backend == "api" else None),
                # review-9 B1: campaign identity is part of the protocol —
                # a resumed run can never switch approval, cap, or tariff
                "campaign": ({"approval_id": campaign["approval_id"],
                              "provider": campaign["provider"],
                              "model": campaign["model"],
                              "cap_usd": campaign["cap_usd"],
                              "price_snapshot_sha256": hashlib.sha256(
                                  (campaign["price_snapshot_json"] or "")
                                  .encode()).hexdigest()}
                             if campaign else None),
                # review-10 B1: scope mode + membership hash + count are run
                # identity; a resume with a changed or omitted papers file
                # produces a different protocol hash and refuses
                "scope": scope,
                "batch_size": BATCH_SIZE, "merge_gap": MERGE_GAP,
                "snippet_max": SNIPPET_MAX}
    protocol_sha = hashlib.sha256(
        json.dumps(protocol, sort_keys=True).encode()).hexdigest()

    if args.resume:
        run_id = args.resume
        row = con.execute(
            "SELECT model, prompt_sha256, isolate, scan_runs_json, backend, "
            "taxonomy_version, status, params_json FROM classification_runs "
            "WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            sys.exit(f"no classification run '{run_id}' to resume")
        if row["status"].startswith("complete"):  # incl. complete_scoped
            sys.exit(f"run '{run_id}' is {row['status']} — terminal runs are "
                     "immutable; start a new run")
        stored_sha = json.loads(row["params_json"] or "{}").get("protocol_sha256")
        if stored_sha != protocol_sha:
            sys.exit(f"protocol mismatch: run '{run_id}' was started under "
                     f"protocol {str(stored_sha)[:12]}…, current is "
                     f"{protocol_sha[:12]}… (code/prompt/schema/backend/"
                     "model/taxonomy/scan-run drift, or a pre-protocol run) "
                     "— start a new superseding run instead")
    else:
        run_id = runs.new_run_id("cls")
        runs.start_classification_run(
            con, run_id, sorted(args.runs), backend_label, model_label, prompt_sha,
            taxonomy.TAXONOMY_VERSION, args.isolate, db.code_commit(),
            {"batch_size": BATCH_SIZE, "merge_gap": MERGE_GAP,
             "snippet_max": SNIPPET_MAX, "workers": args.workers,
             "limit_batches": args.limit_batches,
             "budget_approval": args.budget_approval,
             # full immutable target preimage IN the run row (review-10 B1)
             "scope": ({**scope, "ids": scope_ids} if scope else None),
             "protocol": protocol, "protocol_sha256": protocol_sha})

    lease = None
    new_run = not args.resume
    if args.backend == "api":
        from . import llm_api
        try:
            # durable cross-process CAMPAIGN budget (review-8 B1): spend rows
            # are scoped to the owner approval id; a fresh approval never
            # inherits prior pilots' spend, and admission is atomic in SQLite
            llm_api.attach_ledger(
                db.DB_PATH, run_id, approval_id=args.budget_approval,
                provider=llm_api.provider_of_model(args.model),
                model=args.model, cap_usd=args.max_usd_per_provider,
                purpose=f"classification run {run_id}")
            ATTEMPT_SOURCE[0] = llm_api.drain_attempts  # per-thread provenance
            REQUEST_CTX[0] = llm_api.set_request_context  # pre-dispatch identity
            lease = RunLease(db.DB_PATH, run_id)  # single payer per run
            lease.acquire()
        except (LeaseHeld, RuntimeError) as exc:
            if new_run:
                # review-10 B5: no phantom 'running' rows — a failed setup
                # is a reason-coded terminal state
                runs.finish_classification_run(con, run_id, "setup-failed",
                                               0, 0)
            sys.exit(str(exc))
        # review-10 B6: the durable fence is enforced INSIDE every paid
        # admission transaction from here on
        llm_api.set_fence(run_id, lease.holder)
        if lease.took_over_from:
            print(f"WARNING: stale lease taken over from "
                  f"{lease.took_over_from} (heartbeat older than "
                  f"{LEASE_STALE_S}s)", flush=True)

    # review-10 B6: NOTHING between lease acquisition and process
    # exit may leave the lease held on an exception path
    try:
        snippets = merge_snippets(con, args.runs)
        if scope_ids is not None:
            wanted = set(scope_ids)
            snippets = [s for s in snippets if s["arxiv_id"] in wanted]
            print(f"scope: {len(snippets)} snippets across "
                  f"{len({s['arxiv_id'] for s in snippets})} of the "
                  f"{len(scope_ids)} target papers", flush=True)
        finalize_snippets(snippets, prompt_sha, model_label, args.isolate)
        # only VALID stored labels are done: error AND invalid rows stay
        # retryable (review-5 P0-6 — 'NOT LIKE error%' froze invalids forever;
        # store_results upgrades invalid->ok, never the reverse)
        done = {r["snippet_sha256"] for r in con.execute(
            "SELECT snippet_sha256 FROM classification_items WHERE run_id=? "
            "AND status = 'ok'", (run_id,))}
        todo = [s for s in snippets if s["input_hash"] not in done]
        print(f"{run_id}: {len(snippets)} snippets, {len(todo)} to classify "
              f"({len(snippets) - len(todo)} already stored)", flush=True)

        batches = make_batches(todo, args.isolate)
        n_full = len(batches)
        if args.limit_batches:
            batches = batches[: args.limit_batches]
        now = runs.utcnow()

        log_dir = db.CORPUS_DIR / "logs" / "classify"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{run_id}.jsonl"  # exact model responses, audit-only
        # per-invocation ledger: every resume is a recorded event, not a silent
        # continuation under the first invocation's manifest (review-5 P0-6)
        inv_path = log_dir / f"{run_id}.invocations.jsonl"
        with inv_path.open("a") as f:
            f.write(json.dumps({
                "type": "invocation", "ts": runs.utcnow(),
                "code_commit": db.code_commit(), "backend": backend_label,
                "model": model_label, "isolate": args.isolate,
                "workers": args.workers, "limit_batches": args.limit_batches,
                "max_total_tokens": args.max_total_tokens,
                "max_usd_per_provider": args.max_usd_per_provider,
                "budget_approval": args.budget_approval,
                "papers_file": args.papers_file,
                "lease_holder": lease.holder if lease else None,
                "lease_takeover_from": lease.took_over_from if lease else None,
                "scope": scope,
                "n_todo": len(todo)}) + "\n")
        if scope is not None:
            # human-readable immutable target manifest (the authoritative
            # preimage lives in the run row's params_json — review-10 B1)
            (log_dir / f"{run_id}.scope.json").write_text(json.dumps(
                {**scope, "run_id": run_id, "ids": scope_ids}, indent=1))

        caller = make_caller(args.backend, args.model, args.effort, fence=lease)
        n_ok = n_err = n_invalid = 0
        lease_lost = False
        try:
            from concurrent.futures import FIRST_COMPLETED, wait as _fwait
            with ThreadPoolExecutor(max_workers=args.workers) as ex:
                # bounded submission window (review-9 B3): after a lease loss at
                # most ~2x workers of queued work exists, and every physical
                # dispatch re-checks the fence inside the caller anyway
                pending: dict = {}
                batch_iter = iter(batches)

                def submit_more() -> None:
                    while len(pending) < args.workers * 2:
                        if lease is not None and lease.lost.is_set():
                            return
                        b = next(batch_iter, None)
                        if b is None:
                            return
                        pending[ex.submit(classify_batch, b, header, caller)] = b

                submit_more()
                while pending:
                    done_futs, _ = _fwait(pending, return_when=FIRST_COMPLETED)
                    stop = False
                    for fut in done_futs:
                        batch = pending.pop(fut)
                        # fencing assertion: once the lease is lost this process
                        # must neither store results nor keep paying
                        if lease is not None and lease.lost.is_set():
                            lease_lost = True
                            print("LEASE LOST — another process holds this run "
                                  "now; aborting without storing further "
                                  "results", flush=True)
                            for f_ in pending:
                                f_.cancel()
                            stop = True
                            break
                        try:
                            results, recs, failed = fut.result()
                        except Exception as exc:  # noqa: BLE001 - tooling bug
                            n_err += 1
                            try:
                                store_batch_error(con, run_id, batch, exc, now,
                                                  lease)
                            except LeaseHeld:
                                lease_lost = True
                                if lease is not None:
                                    lease.lost.set()
                                stop = True
                                break
                            print(f"  batch FAILED ({batch[0]['arxiv_id']}...): "
                                  f"{exc}", flush=True)
                            continue
                        if failed:
                            n_err += 1
                            try:
                                for s, exc in failed:
                                    # per-snippet terminal failures after
                                    # bisection — retryable on resume (review-7)
                                    store_batch_error(con, run_id, [s], exc, now,
                                                      lease)
                            except LeaseHeld:
                                lease_lost = True
                                if lease is not None:
                                    lease.lost.set()
                                stop = True
                                break
                            print(f"  {len(failed)} snippet(s) failed after "
                                  f"bisection ({batch[0]['arxiv_id']}): "
                                  f"{failed[0][1]}", flush=True)
                        if recs:
                            # one log line per DISTINCT prompt with its exact
                            # snippet hashes and split path (review-8/9 B3/B4)
                            ts = runs.utcnow()
                            with log_path.open("a") as lf:
                                for rec in recs:
                                    lf.write(json.dumps({
                                        "ts": ts,
                                        "split_path": rec["split_path"],
                                        "snippet_hashes": rec["snippet_hashes"],
                                        "prompt_sha256": rec["prompt_sha256"],
                                        "response_sha256": rec["response_sha256"],
                                        "error": rec.get("error"),
                                        "response": rec["response"]}) + "\n")
                            if args.backend == "api":
                                # attempt rows were inserted PRE-DISPATCH and
                                # updated at response time in the worker thread
                                # (review-9 B5); here we only add the logical
                                # linkage: split path, prompt/response hashes,
                                # ordered snippet hashes
                                with con:
                                    for rec in recs:
                                        for a in rec["attempts"]:
                                            if a.get("attempt_row_id") is None:
                                                continue
                                            con.execute(
                                                "UPDATE api_attempts SET "
                                                "split_path=?, prompt_sha256=?, "
                                                "response_sha256=?, "
                                                "snippet_hashes_json=? WHERE id=?",
                                                (rec["split_path"],
                                                 rec["prompt_sha256"],
                                                 rec["response_sha256"],
                                                 json.dumps(rec["snippet_hashes"]),
                                                 a["attempt_row_id"]))
                                with inv_path.open("a") as f:
                                    for rec in recs:
                                        for a in rec["attempts"]:
                                            f.write(json.dumps({
                                                "type": "attempt",
                                                "split_path": rec["split_path"],
                                                **a}) + "\n")
                        if results:
                            # durable holder check in front of every result
                            # store (review-9 B3): a fenced heartbeat that no
                            # longer matches means we must not write
                            if lease is not None and not lease.heartbeat():
                                lease.lost.set()
                                lease_lost = True
                                print("LEASE LOST at store time — discarding "
                                      "batch results", flush=True)
                                stop = True
                                break
                            try:
                                store_results(con, run_id, results, now, lease)
                            except LeaseHeld:
                                lease_lost = True
                                lease.lost.set()
                                stop = True
                                break
                            n_ok += 1
                            n_invalid += sum(1 for _, clean, _, _ in results
                                             if clean is None)
                            print(f"  batch ok ({n_ok}/{len(batches)})", flush=True)
                    if stop:
                        break
                    submit_more()
        except BaseException:
            # crash must not leave the lease held until stale timeout
            if lease is not None and not lease.lost.is_set():
                lease.release()
            raise
        n_items = con.execute("SELECT COUNT(*) FROM classification_items WHERE run_id=?",
                              (run_id,)).fetchone()[0]
        n_item_err = con.execute(
            "SELECT COUNT(*) FROM classification_items WHERE run_id=? AND status != 'ok'",
            (run_id,)).fetchone()[0]
        # complete requires every stored item valid, not merely no failures in
        # THIS invocation (F6)
        partial = n_err > 0 or len(batches) < n_full or n_item_err > 0 or lease_lost
        # review-10 B1: a scoped run is NEVER 'complete' for its scan run —
        # report/freeze refuse the scoped status; review-10 B6: after a lease
        # loss the successor owns the terminal state, we must not overwrite it
        full_status = "partial" if partial else (
            "complete_scoped" if scope else "complete")
        if lease_lost:
            print("lease lost — terminal status belongs to the successor; "
                  "leaving the run row untouched", flush=True)
        else:
            try:
                # review-12 B6: holder re-verified inside the status txn —
                # the heartbeat check above leaves a takeover window
                runs.finish_classification_run(
                    con, run_id, full_status, n_items, n_item_err,
                    holder=lease.holder if lease is not None else None)
            except runs.LeaseLostAtFinish:
                print("lease lost at terminal-status time — status belongs "
                      "to the successor; leaving the run row untouched",
                      flush=True)
                full_status = "lease-lost"
        print(f"done: {n_ok} batches stored, {n_err} failed, {n_invalid} invalid labels, "
              f"{n_item_err} non-ok items ({run_id}, {full_status})", flush=True)
        if args.backend == "api":
            from . import llm_api
            for m, u in llm_api.usage_summary().items():
                print(f"tokens[{m}]: {u['calls']} calls, {u['input']:,} in / "
                      f"{u['output']:,} out", flush=True)
            state = llm_api.budget_state()
            for prov, usd in state["spent_usd"].items():
                print(f"spent[{prov}]: ${usd:.2f}"
                      + (f" of ${state['max_usd_per_provider']:.2f} cap"
                         if state["max_usd_per_provider"] else ""), flush=True)
            # durable usage/price/budget record for reconciliation vs the
            # provider console (review-5 P0-4); MERGED across invocations —
            # overwriting hid earlier resumes' spend (review-6 P0-1)
            upath = log_dir / f"{run_id}.usage.json"
            try:
                merged = json.loads(upath.read_text()).get("usage", {})
            except (OSError, json.JSONDecodeError):
                merged = {}
            for m, u in llm_api.usage_summary().items():
                prev = merged.setdefault(m, {"input": 0, "output": 0, "calls": 0})
                for k in ("input", "output", "calls"):
                    prev[k] += u[k]
            upath.write_text(json.dumps(
                {"ts": runs.utcnow(), "usage": merged, "budget": state}, indent=1))
            if lease is not None and not lease_lost:
                lease.release()  # fenced: deletes only OUR holder row
            # NB: every attempt travels inside its request record (thread-local
            # buffers, review-8 B3) — there is no global tail to drain; spend
            # from any in-flight dispatch at abort time is durable in api_spend
        return 0 if not partial else 1
    except BaseException:
        _bail_release(lease)
        raise


if __name__ == "__main__":
    sys.exit(main())
