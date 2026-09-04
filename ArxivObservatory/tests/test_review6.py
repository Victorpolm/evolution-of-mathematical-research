"""Regressions from review_codex6.md: refill truth table, per-dispatch
budgets with durable spend, Anthropic strict, fail-closed validator, full C0
rejection, PDF cache binding, unknown-format acquisition, overwrite divert."""

import gzip
import json
import subprocess
import sys

import pytest

from pipeline import classify, db, fetch, llm_api
from pipeline.classify import extract_json, validate_label


# --- refill mode truth table --------------------------------------------------

@pytest.mark.parametrize("argv", [
    ["--v1-refill", "--months", "2607"],
    ["--v1-refill", "--flagged-only", "--months", "2607"],
    ["--v1-refill", "--flagged-first", "scan-t", "--months", "2607"],
    ["--v1-refill", "--flagged-only", "--flagged-first", "scan-t",
     "--include-unflagged-tail", "--months", "2607"],
])
def test_refill_rejects_every_unauthorized_form(argv):
    proc = subprocess.run(
        [sys.executable, "-m", "pipeline.fetch"] + argv,
        capture_output=True, text=True, timeout=60)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "authorization" in out or "exclusive" in out or "needs" in out


# --- budget: per-dispatch reservation, durable baseline -----------------------

@pytest.fixture()
def clean_budget():
    llm_api._reset_for_tests()
    yield
    llm_api._reset_for_tests()


def test_429_rejection_releases_reservation(monkeypatch, clean_budget):
    """A 429 is a provable rejection: its reservation must be freed, or a
    normal overnight 429 rate would burn phantom budget and spuriously latch
    the cap (night-ops fix, documented in DECISIONS/LEDGER)."""
    def always_429(*a, **k):
        raise llm_api._Retryable("http429", billed_possible=False)
    monkeypatch.setattr(llm_api, "_post", always_429)
    monkeypatch.setattr(llm_api.time, "sleep", lambda s: None)
    llm_api.set_budget(max_usd_per_provider=50.0)
    with pytest.raises(RuntimeError, match="unreachable"):
        llm_api.call_api("x" * 3000, "gpt-5.6-luna")
    assert llm_api.budget_state()["spent_usd"].get("openai", 0.0) == 0.0
    # and nothing stays reserved either
    assert llm_api._reserved_usd.get("openai", 0.0) == 0.0


def test_every_physical_retry_is_reserved(monkeypatch, clean_budget):
    """Each transport retry must consume its own reservation (review-6:
    one reservation used to cover up to four dispatches)."""
    def always_retryable(*a, **k):
        raise llm_api._Retryable("http503")
    monkeypatch.setattr(llm_api, "_post", always_retryable)
    monkeypatch.setattr(llm_api.time, "sleep", lambda s: None)
    llm_api.set_budget(max_usd_per_provider=50.0)
    prompt = "x" * 3000
    with pytest.raises(RuntimeError, match="unreachable"):
        llm_api.call_api(prompt, "gpt-5.6-luna")
    p = llm_api.PRICES_USD_PER_MTOK["gpt-5.6-luna"]
    per = (llm_api._est_tokens(prompt) * llm_api._worst_input_rate("gpt-5.6-luna")
           + llm_api.MAX_OUTPUT_TOKENS * p["output"]) / 1e6
    spent = llm_api.budget_state()["spent_usd"]["openai"]
    assert abs(spent - llm_api.RETRIES * per) < 1e-9
    # transport failures leave attempt records (review-6 P1-6)
    kinds = [a["endpoint"] for a in llm_api.drain_attempts()]
    assert kinds.count("transport-failure") == llm_api.RETRIES


def test_token_cap_counts_inflight_reservations(clean_budget):
    """Concurrent workers must not jointly pass the same remaining-token
    headroom: reservations count before settlement."""
    need = llm_api._est_tokens("y" * 3000) + llm_api.MAX_OUTPUT_TOKENS
    llm_api.set_budget(max_tokens=need + 10)  # room for exactly one call
    r1, _row, _att = llm_api._reserve("openai", "gpt-5.6-luna", "y" * 3000)
    assert r1 >= 0.0
    with pytest.raises(llm_api.BudgetExceeded, match="token"):
        llm_api._reserve("openai", "gpt-5.6-luna", "y" * 3000)


def test_spend_survives_process_restart(tmp_path, monkeypatch, clean_budget):
    """A resume must inherit historical provider spend, not a fresh cap."""
    dbfile = tmp_path / "led.db"
    con = db.connect(dbfile)  # head schema incl. api_spend
    con.close()
    llm_api.attach_ledger(dbfile, "run-a")
    llm_api.set_budget(max_usd_per_provider=50.0)
    prompt = "z" * 3000
    reserved, row, _att = llm_api._reserve("openai", "gpt-5.6-luna", prompt)
    llm_api._settle("openai", "gpt-5.6-luna", reserved,
                    llm_api._est_tokens(prompt),
                    {"input": 100_000_000, "cached_input": 0,
                     "cache_write": 0, "output": 1_000_000}, row)
    spent_before = llm_api.budget_state()["spent_usd"]["openai"]
    assert spent_before > 20  # 100M input tokens at $0.20/M
    # simulate a fresh process
    llm_api._reset_for_tests()
    llm_api.attach_ledger(dbfile, "run-a")
    # a cap just above the historical spend leaves no room for another call
    llm_api.set_budget(max_usd_per_provider=spent_before + 0.001)
    assert abs(llm_api.budget_state()["spent_usd"]["openai"]
               - spent_before) < 1e-6
    with pytest.raises(llm_api.BudgetExceeded):
        llm_api._reserve("openai", "gpt-5.6-luna", "w" * 3000)


def test_anthropic_request_is_strict(monkeypatch, clean_budget):
    captured = {}

    def fake_post(url, headers, body, timeout):
        captured.update(body)

        class R:
            status_code = 200

            @staticmethod
            def json():
                return {"id": "msg_1", "stop_reason": "tool_use",
                        "usage": {"input_tokens": 10, "output_tokens": 5},
                        "content": [{"type": "tool_use",
                                     "input": {"labels": []}}]}
        return R()
    monkeypatch.setattr(llm_api, "_post", fake_post)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    out = llm_api.call_api("p", "claude-haiku-4-5-20251001")
    assert out == "[]"
    tool = captured["tools"][0]
    assert tool["strict"] is True  # review-6 P0-2
    assert tool["input_schema"]["properties"]["labels"]


# --- parser and validator strictness ------------------------------------------

def test_all_c0_controls_rejected():
    """\\nabla, \\tau, \\ref decode via LEGAL JSON escapes to control chars —
    all C0 controls are rejected now (review-6 P0-3)."""
    for bad in (r'[{"q": "the \nabla operator"}]',
                r'[{"q": "for \tau > 0"}]',
                r'[{"q": "see \ref above"}]'):
        with pytest.raises(ValueError):
            extract_json(bad)


def test_duplicate_json_keys_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        extract_json('[{"id": 0, "id": 1}]')


def _full_label(**over):
    lab = {"polarity": "author_use", "tools": ["ChatGPT"], "models": [],
           "categories": ["writing_editing"], "epistemic_impact": "cosmetic",
           "locations": ["acknowledgments"], "confidence": 0.9,
           "quote": "We thank ChatGPT",
           "flags": {"catalytic": False}}
    lab.update(over)
    return lab


SNIP = "We thank ChatGPT for help"


def test_validator_rejects_missing_required_fields():
    lab = _full_label()
    del lab["tools"]
    clean, problems = validate_label(lab, SNIP)
    assert clean is None and "missing required keys" in problems[0]


def test_validator_rejects_bool_and_nonfinite_confidence():
    assert validate_label(_full_label(confidence=True), SNIP)[0] is None
    assert validate_label(_full_label(confidence=float("nan")), SNIP)[0] is None


def test_validator_rejects_overlong_instead_of_truncating():
    lab = _full_label(tools=["x" * (classify.MAX_STR_CHARS + 1)])
    assert validate_label(lab, SNIP)[0] is None
    lab = _full_label(quote="q" * (classify.MAX_QUOTE_CHARS + 1))
    assert validate_label(lab, SNIP)[0] is None


def test_valid_label_still_passes():
    clean, _ = validate_label(_full_label(), SNIP)
    assert clean is not None and clean["quote_grounded"] is True


# --- fetch: unknown format and byte-overwrite guard ---------------------------

class _FakeResp:
    def __init__(self, content):
        self.status_code, self.content, self.headers = 200, content, {}


class _FakeSession:
    def __init__(self, content):
        self._content = content

    def get(self, url, timeout):
        return _FakeResp(self._content)


@pytest.fixture()
def corpus_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(db, "CORPUS_DIR", tmp_path / "corpus")
    return tmp_path


def test_unknown_format_is_not_v1_success(fixture_con, corpus_tmp):
    """An HTTP-200 HTML body must not create a v1 artifact (review-6 P1-2)."""
    status = fetch.fetch_one(_FakeSession(b"<html>rate limited</html>"),
                             fixture_con, "2607.00001", 1, v1_refill=True)
    assert status == "unknown-format"
    assert fixture_con.execute(
        "SELECT COUNT(*) FROM artifacts WHERE arxiv_id='2607.00001' "
        "AND version=1").fetchone()[0] == 0
    assert (corpus_tmp / "corpus" / "2607" / "2607.00001"
            / "eprint_v1.unknown").exists()


def test_differing_bytes_divert_to_content_path(fixture_con, corpus_tmp):
    """Refetching different bytes must never overwrite a path an artifact
    row references (review-6 P1-1)."""
    tex1 = gzip.compress(b"\\documentclass{article} one")
    tex2 = gzip.compress(b"\\documentclass{article} two")
    assert fetch.fetch_one(_FakeSession(tex1), fixture_con,
                           "2607.00002", 1, v1_refill=True) == "ok"
    assert fetch.fetch_one(_FakeSession(tex2), fixture_con,
                           "2607.00002", 1, v1_refill=True) == "ok"
    rows = fixture_con.execute(
        "SELECT path, sha256 FROM artifacts WHERE arxiv_id='2607.00002' "
        "AND version=1 ORDER BY id").fetchall()
    assert len(rows) == 2
    assert rows[0]["path"] != rows[1]["path"]
    for r in rows:
        p = corpus_tmp / r["path"]
        assert p.exists()
        import hashlib
        assert hashlib.sha256(p.read_bytes()).hexdigest() == r["sha256"]


# --- PDF text cache binding ---------------------------------------------------

def test_pdf_text_cache_bound_to_bytes(tmp_path, monkeypatch):
    from pipeline import scan
    pdf = tmp_path / "p.pdf"

    def fake_run(cmd, capture_output, text, timeout):
        # emulate pdftotext: write derived text from current pdf bytes
        out = tmp_path / cmd[-1].split("/")[-1]
        from pathlib import Path
        Path(cmd[-1]).write_text(pdf.read_bytes().decode())

        class P:
            returncode = 0
        return P()
    monkeypatch.setattr(scan.subprocess, "run", fake_run)
    pdf.write_bytes(b"FIRST")
    assert scan.pdf_to_text(pdf) == "FIRST"
    pdf.write_bytes(b"SECOND")  # replaced PDF at the same path
    assert scan.pdf_to_text(pdf) == "SECOND"  # stale cache must not answer