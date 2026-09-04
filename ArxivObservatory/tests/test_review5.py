"""Regressions from review_codex5.md: freeze bypasses, budget enforcement,
refill boundary, schema generation, legacy ingest gating."""

import json

import pytest

from pipeline import llm_api, report
from pipeline.classify import ALLOWED_KEYS


def _freeze(con, tmp_path):
    report.build(con, "scan-t", "cls-t", tmp_path / "r.md",
                 "2026-07-01", "2026-08-08", freeze="rel-t")


def test_freeze_rejects_unpinned_with_effort_suffix(fixture_con, tmp_path):
    """'codex-default(unpinned)@medium' must not pass the pin check."""
    with fixture_con:
        fixture_con.execute("UPDATE classification_runs SET "
                            "model='codex-default(unpinned)@medium', "
                            "backend='api:openai' WHERE run_id='cls-t'")
    with pytest.raises(SystemExit, match="unpinned"):
        _freeze(fixture_con, tmp_path)


def test_freeze_rejects_unknown_commit(fixture_con, tmp_path):
    """db.code_commit() returns literal 'unknown' on git failure — truthy,
    not dirty-suffixed, and must still be rejected."""
    with fixture_con:
        fixture_con.execute("UPDATE scan_runs SET code_commit='unknown' "
                            "WHERE run_id='scan-t'")
    with pytest.raises(SystemExit, match="dirty/unknown"):
        _freeze(fixture_con, tmp_path)


def test_freeze_rejects_non_api_backend(fixture_con, tmp_path):
    """Isolated codex still isn't the approved analysis backend
    (DECISIONS.md 2026-08-11)."""
    with fixture_con:
        fixture_con.execute("UPDATE classification_runs SET backend='codex' "
                            "WHERE run_id='cls-t'")
    with pytest.raises(SystemExit, match="backend"):
        _freeze(fixture_con, tmp_path)


@pytest.fixture()
def clean_budget():
    llm_api._reset_for_tests()
    yield
    llm_api._reset_for_tests()


def test_budget_blocks_before_any_http(monkeypatch, clean_budget):
    """A tripped USD budget must fail BEFORE dispatch — no paid request."""
    def boom(*a, **k):
        raise AssertionError("HTTP request sent despite exhausted budget")
    monkeypatch.setattr(llm_api, "_post", boom)
    llm_api.set_budget(max_usd_per_provider=0.0000001)
    with pytest.raises(llm_api.BudgetExceeded):
        llm_api.call_api("x" * 4000, "gpt-5.6-luna")
    # the stop latches: every later call fails instantly too
    with pytest.raises(llm_api.BudgetExceeded):
        llm_api.call_api("y", "gpt-5.6-luna")


def test_budget_refuses_unpriced_model(monkeypatch, clean_budget):
    """Under a USD cap, a model without a price snapshot must be refused,
    not billed at an assumed price of zero."""
    monkeypatch.setattr(llm_api, "_post", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("HTTP despite unpriced model")))
    llm_api.set_budget(max_usd_per_provider=50.0)
    with pytest.raises(llm_api.BudgetExceeded, match="price snapshot"):
        llm_api.call_api("hello", "gpt-imaginary-model")


def test_failed_call_commits_reservation(monkeypatch, clean_budget):
    """A transport failure does not prove the provider didn't bill: the
    reservation is committed as spent (conservative)."""
    def fail(*a, **k):
        raise RuntimeError("timeout-ish")
    monkeypatch.setattr(llm_api, "_call_openai", fail)
    llm_api.set_budget(max_usd_per_provider=50.0)
    with pytest.raises(RuntimeError):
        llm_api.call_api("z" * 3000, "gpt-5.6-luna")
    assert llm_api.budget_state()["spent_usd"]["openai"] > 0


def test_batch_schema_matches_validator_contract():
    schema = llm_api.batch_schema()
    item = schema["properties"]["labels"]["items"]
    assert set(item["properties"]) == ALLOWED_KEYS | {"id"}
    assert set(item["required"]) == ALLOWED_KEYS | {"id"}
    assert item["additionalProperties"] is False
    # enums come from the live taxonomy (drift protection)
    from pipeline import taxonomy
    assert item["properties"]["polarity"]["enum"] == sorted(taxonomy.POLARITIES)
    assert set(item["properties"]["flags"]["required"]) == set(taxonomy.FLAGS)


def test_env_allowlist(tmp_path, monkeypatch):
    """.env loading must ignore non-allowlisted keys (no arbitrary env
    injection from a repo file)."""
    from pipeline import db
    monkeypatch.setattr(db, "PROJECT_ROOT", tmp_path)
    (tmp_path / ".env").write_text(
        "OPENAI_API_KEY=sk-test-123\nHTTP_PROXY=http://evil:8080\n")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    llm_api.load_env()
    import os
    assert os.environ.get("OPENAI_API_KEY") == "sk-test-123"
    assert "HTTP_PROXY" not in os.environ


def test_markdown_ingest_is_legacy_gated(fixture_con, tmp_path, monkeypatch):
    from pipeline import annotate
    monkeypatch.delenv("ARXIV_OBS_LEGACY", raising=False)
    pk = tmp_path / "p.md"
    pk.write_text("## ITEM 1 — arXiv 2607.00001 v1\nVERDICT: TOPIC_ONLY\n")

    class A:
        project, reviewer, packet = "p-t", "r1", str(pk)
        json = None

    with pytest.raises(SystemExit, match="legacy"):
        annotate.cmd_ingest(A)


def test_refill_tail_needs_explicit_authorization():
    """fetch --v1-refill --flagged-first without --flagged-only or
    --include-unflagged-tail must refuse to start (review-5 immediate)."""
    import subprocess
    import sys
    proc = subprocess.run(
        [sys.executable, "-m", "pipeline.fetch", "--v1-refill",
         "--flagged-first", "scan-t", "--months", "2607"],
        capture_output=True, text=True, timeout=60)
    assert proc.returncode != 0
    assert "authorization" in (proc.stdout + proc.stderr)