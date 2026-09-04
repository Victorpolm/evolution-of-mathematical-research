"""Review-9 Gate A/B regression tests: machine rejects semantic
contradictions instead of repairing them (A4), campaigns fail closed and
never self-authorize (B1), token estimates provably upper-bound (B2),
re-ask/failure provenance keeps every distinct prompt (B4), and attempt
rows are durable before dispatch (B5)."""

import json
import sqlite3

import pytest

from pipeline import annotate, classify, db as dbmod, llm_api, taxonomy

SNIP = "Acknowledgments. We thank ChatGPT for help with the writing."


# --- A4: no silent repair of semantic contradictions -------------------------

def test_machine_rejects_non_author_catalytic_like_human():
    lab = {"polarity": "topic_only", "tools": [], "models": [],
           "categories": [], "epistemic_impact": "not_applicable",
           "locations": ["body"], "confidence": 0.9, "quote": "",
           "flags": {"catalytic": True}}
    clean, problems = classify.validate_label(lab, SNIP)
    assert clean is None and any("catalytic requires author_use" in p
                                 for p in problems)
    # the human path rejects the identical combination
    assert annotate.validate_verdict_item(
        {"arxiv_id": "0000.00000", "version": 1, "verdict": "TOPIC_ONLY",
         "categories": [], "locations": [], "impact": "",
         "flags": ["catalytic"], "tools": "", "notes": ""})[0] is None
    # catalytic=False (schema-required key) is NOT a contradiction
    lab["flags"] = {"catalytic": False}
    clean, _ = classify.validate_label(lab, SNIP)
    assert clean is not None and clean["flags"] == {"catalytic": False}


# --- B1: campaigns never self-authorize --------------------------------------

def test_attach_unknown_campaign_fails_closed(tmp_path):
    dbp = tmp_path / "b.db"
    dbmod.connect(dbp).close()
    llm_api._reset_for_tests()
    try:
        with pytest.raises(RuntimeError, match="unknown budget campaign"):
            llm_api.attach_ledger(dbp, "r1", approval_id="TYPO-ID",
                                  provider="openai", model="gpt-5.6-luna",
                                  cap_usd=50.0)
        with pytest.raises(RuntimeError, match="unknown budget campaign"):
            llm_api.get_campaign(dbp, "TYPO-ID")
    finally:
        llm_api._reset_for_tests()


def test_create_campaign_is_deliberate_and_immutable(tmp_path):
    dbp = tmp_path / "b2.db"
    dbmod.connect(dbp).close()
    llm_api.create_campaign(dbp, "AP-1", "openai", "gpt-5.6-luna", 5.0, "p")
    with pytest.raises(RuntimeError, match="already exists"):
        llm_api.create_campaign(dbp, "AP-1", "openai", "gpt-5.6-luna", 9.0, "p")
    with pytest.raises(ValueError):
        llm_api.create_campaign(dbp, "AP-2", "openai", "gpt-5.6-luna", 0, "p")
    row = llm_api.get_campaign(dbp, "AP-1")
    assert row["cap_usd"] == 5.0 and row["status"] == "active"


# --- B2: provable input upper bound ------------------------------------------

def test_est_tokens_upper_bounds_bytes():
    for text in ("plain ascii", "unicode ∇τβ — καλημέρα", "x" * 10000):
        assert llm_api._est_tokens(text) >= len(text.encode("utf-8"))


# --- B4: every distinct prompt is its own record ------------------------------

def _leaf_label(i=0):
    return {"id": i, "polarity": "topic_only", "tools": [], "models": [],
            "categories": [], "epistemic_impact": "not_applicable",
            "locations": ["unknown"], "confidence": 0.5, "quote": "",
             "flags": {"catalytic": False}}


def _batch(n):
    return [{"arxiv_id": f"000{i}.0000{i}", "version": 1,
             "source_kind": "tex", "member": "m", "terms": ["ChatGPT"],
             "context": "ctx", "input_hash": f"hash{i}", "hit_ids": []}
            for i in range(n)]


def test_parse_reask_creates_two_prompt_records():
    header = classify.build_prompt_header()
    calls = []

    def flaky_call(prompt):
        calls.append(prompt)
        if len(calls) == 1:
            return "no json here at all"
        return json.dumps([_leaf_label()])

    out, recs, failed = classify.classify_batch(_batch(1), header, flaky_call)
    assert not failed and len(out) == 1
    paths = [r["split_path"] for r in recs]
    assert paths == ["R", "R.reask1"]
    # each record hashes ITS OWN prompt — the re-ask prompt differs
    assert recs[0]["prompt_sha256"] != recs[1]["prompt_sha256"]
    assert recs[0]["response_sha256"] is not None  # unparseable ≠ unrecorded


def test_failed_batch_keeps_prompt_hash():
    header = classify.build_prompt_header()

    def dead_call(prompt):
        raise RuntimeError("openai http503")

    out, recs, failed = classify.classify_batch(_batch(1), header, dead_call)
    assert failed and not out
    assert recs and recs[-1]["error"].startswith("RuntimeError")
    # review-9 B4: the failed node retains its exact prompt hash
    assert all(r["prompt_sha256"] is not None for r in recs)
    assert recs[0]["snippet_hashes"] == ["hash0"]


# --- B5/B7: atomic pre-dispatch admission ------------------------------------

def test_admission_is_atomic_reservation_plus_attempt(tmp_path):
    """review-10 B7: the reservation and the attempt row are ONE
    transaction, and the pre-dispatch attempt already carries prompt hash,
    split path, and snippet identity."""
    dbp = tmp_path / "a.db"
    dbmod.connect(dbp).close()
    llm_api._reset_for_tests()
    try:
        llm_api.create_campaign(dbp, "AP-B5", "openai", "gpt-5.6-luna",
                                5.0, "p")
        llm_api.attach_ledger(dbp, "run-b5", approval_id="AP-B5",
                              provider="openai", model="gpt-5.6-luna",
                              cap_usd=5.0)
        llm_api._tls.attempt_no = 0
        llm_api._tls.prompt_sha = "deadbeef" * 8
        llm_api.set_request_context({"split_path": "R.L",
                                     "snippet_hashes": ["h1", "h2"]})
        spend_id, att_id = llm_api._ledger_admit("openai", "gpt-5.6-luna",
                                                 0.01)
        assert spend_id is not None and att_id is not None
        con = sqlite3.connect(dbp)
        pre = con.execute(
            "SELECT run_id, approval_id, reservation_row_id, state, "
            "prompt_sha256, split_path, snippet_hashes_json, http_status "
            "FROM api_attempts WHERE id=?", (att_id,)).fetchone()
        # the row exists BEFORE any response — crash-visible provenance with
        # exact input identity
        assert pre == ("run-b5", "AP-B5", spend_id, "admitted",
                       "deadbeef" * 8, "R.L", '["h1", "h2"]', None)
        # the paired reservation exists in the SAME committed state
        assert con.execute("SELECT kind FROM api_spend WHERE id=?",
                           (spend_id,)).fetchone()[0] == "reserved"
        llm_api._tls.attempt_row_id = att_id
        llm_api._tls.reservation_row_id = spend_id
        import time as _t
        llm_api._record_attempt("openai", "gpt-5.6-luna", "chat", _t.monotonic(),
                                "req-1", "stop", {"prompt_tokens": 5}, 200,
                                returned_model="gpt-5.6-luna-2026-08-01",
                                system_fingerprint="fp_x")
        post = con.execute("SELECT request_id, http_status, returned_model, "
                           "system_fingerprint, state FROM api_attempts "
                           "WHERE id=?", (att_id,)).fetchone()
        assert post == ("req-1", 200, "gpt-5.6-luna-2026-08-01", "fp_x",
                        "responded")
        con.close()
    finally:
        llm_api._reset_for_tests()


def test_admission_rejects_wrong_model_in_transaction(tmp_path):
    """review-10 B5: provider/model binding is checked INSIDE the admission
    transaction, not only at attach time."""
    dbp = tmp_path / "a2.db"
    dbmod.connect(dbp).close()
    llm_api._reset_for_tests()
    try:
        llm_api.create_campaign(dbp, "AP-B5b", "openai", "gpt-5.6-luna",
                                5.0, "p")
        llm_api.attach_ledger(dbp, "run-b5b", approval_id="AP-B5b",
                              provider="openai", model="gpt-5.6-luna",
                              cap_usd=5.0)
        with pytest.raises(llm_api.BudgetExceeded, match="bound to"):
            llm_api._ledger_admit("openai", "gpt-4o-mini", 0.01)
    finally:
        llm_api._reset_for_tests()


# --- error normalization (B7) ------------------------------------------------

def test_err_summary_drops_free_text():
    class FakeResp:
        status_code = 400

        def json(self):
            return {"error": {"type": "invalid_request_error",
                              "code": "bad_schema",
                              "message": "SECRET SNIPPET CONTENT ECHOED"}}

    s = llm_api._err_summary(FakeResp())
    assert "invalid_request_error" in s and "bad_schema" in s
    assert "SECRET" not in s
