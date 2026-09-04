"""Review-10 Gate A/B regression tests: full tariff classes incl. cache
writes (B2), fail-closed usage validation (B3), settlement<=reservation
latch (B4), call_api campaign requirement + admission binding (B5),
transactional store fencing (B6), scoped-run refusal in reports (B1),
grader/machine decision-text unification (A2), and the active-invocation
construct (A1)."""

import json
import os
import sqlite3

import pytest

from pipeline import annotate, classify, db as dbmod, llm_api, report, taxonomy


# --- A1/A2: one coherent construct, one decision text ------------------------

def test_construct_has_no_incorporated_contradiction():
    # active-invocation construct: the taxonomy never claims 'incorporated'
    # artifacts are author_use while also routing them to topic_only
    src = open("pipeline/taxonomy.py").read()
    # v2.8: the diagnostic flags are RETIRED as recorded fields; the
    # artifact-reuse boundary lives in the topic_only rule text
    assert set(taxonomy.FLAGS) == {"catalytic"}
    assert "invoked/incorporated" not in src
    assert "pre-existing" in taxonomy.POLARITIES["topic_only"]


def test_grader_tooltips_are_generated_from_taxonomy():
    d = annotate.VERDICT_DESCRIPTIONS
    assert d["TRUE_DISCLOSURE"] == taxonomy.POLARITIES["author_use"]
    assert d["TOPIC_ONLY"] == taxonomy.POLARITIES["topic_only"]
    assert d["FALSE_POSITIVE"] == taxonomy.POLARITIES["false_positive"]
    # the old drifted phrase is gone
    assert "in producing this paper" not in d["TRUE_DISCLOSURE"]


def test_external_ai_artifact_roundtrips_and_survives_clearing():
    # v2.8 rewrite of this guard: LEGACY inputs carrying the retired
    # diagnostic are rejected on both paths, never silently accepted
    item = {"arxiv_id": "0000.00000", "version": 1, "verdict": "TOPIC_ONLY",
            "categories": [], "locations": [], "impact": "", "flags": [],
            "external_ai_artifact": "yes", "tools": "", "notes": ""}
    clean, err = annotate.validate_verdict_item(item)
    assert clean is None and "legacy" in err
    lab = {"polarity": "topic_only", "tools": [], "models": [],
           "categories": [], "epistemic_impact": "not_applicable",
           "locations": ["body"], "confidence": 0.9, "quote": "",
           "flags": {"catalytic": False, "external_ai_artifact": True}}
    mclean, problems = classify.validate_label(lab, "x")
    assert mclean is None and any("unknown flags" in p
                                  for p in problems)


def test_r5_states_recorded_for_true_disclosure_only():
    # v2.8 rewrite: the r5_states checkboxes are RETIRED; legacy exports
    # carrying them are rejected
    item = {"arxiv_id": "0000.00000", "version": 1,
            "verdict": "TRUE_DISCLOSURE", "categories": [], "locations": [],
            "impact": "supportive", "flags": [],
            "r5_states": ["also_zero_contribution_attempt"],
            "tools": "", "notes": ""}
    clean, err = annotate.validate_verdict_item(item)
    assert clean is None and "legacy" in err
    non_true = {"arxiv_id": "0000.00000", "version": 1,
                "verdict": "TOPIC_ONLY", "categories": [], "locations": [],
                "impact": "", "flags": [], "tools": "", "notes": ""}
    clean, _ = annotate.validate_verdict_item(non_true)
    assert clean is not None and "r5_states" not in clean


# --- B2: cache-write tariff --------------------------------------------------

def test_cache_write_tariff_reproduces_the_live_undercount():
    """The adherence run's exact usage mix: 174,315 prompt tokens of which
    174,153 were cache writes, 29,231 output. Base-rate-only billing gave
    $0.0699402; the documented 1.25x cache-write rate gives $0.07864785."""
    classes = {"input": 174315 - 174153, "cached_input": 0,
               "cache_write": 174153, "output": 29231}
    usd = llm_api._cost_usd_classes("gpt-5.6-luna", classes)
    assert abs(usd - 0.07864785) < 1e-8
    # and the reservation rate covers the worst class
    assert llm_api._worst_input_rate("gpt-5.6-luna") == 0.25


def test_every_priced_model_has_all_usage_classes():
    for model, p in llm_api.PRICES_USD_PER_MTOK.items():
        for c in (*llm_api.USAGE_CLASSES, "output"):
            assert c in p, (model, c)


# --- B3: usage validation fail-closed ----------------------------------------

def test_usage_validation_rejects_missing_zero_bool_inconsistent():
    v = llm_api._validated_usage
    good = {"prompt_tokens": 100, "completion_tokens": 5,
            "prompt_tokens_details": {"cached_tokens": 10,
                                      "cache_write_tokens": 80}}
    assert v("openai", good) == {"input": 10, "cached_input": 10,
                                 "cache_write": 80, "output": 5}
    assert v("openai", None) is None
    assert v("openai", {}) is None
    assert v("openai", {"prompt_tokens": 0, "completion_tokens": 5}) is None
    assert v("openai", {"prompt_tokens": True, "completion_tokens": 5}) is None
    assert v("openai", {"prompt_tokens": -1, "completion_tokens": 5}) is None
    # details exceeding the total are inconsistent, not billable at $0
    assert v("openai", {"prompt_tokens": 10, "completion_tokens": 1,
                        "prompt_tokens_details": {"cached_tokens": 20,
                                                  "cache_write_tokens": 0}}) \
        is None
    assert v("anthropic", {"input_tokens": 10, "output_tokens": 2,
                           "cache_creation_input_tokens": 3,
                           "cache_read_input_tokens": 1}) == {
        "input": 10, "cached_input": 1, "cache_write": 3, "output": 2}


def test_unknown_usage_settles_at_reservation_never_zero(tmp_path):
    dbp = tmp_path / "u.db"
    dbmod.connect(dbp).close()
    llm_api._reset_for_tests()
    try:
        llm_api.create_campaign(dbp, "AP-U", "openai", "gpt-5.6-luna", 5.0, "p")
        llm_api.attach_ledger(dbp, "run-u", approval_id="AP-U",
                              provider="openai", model="gpt-5.6-luna",
                              cap_usd=5.0)
        llm_api.set_budget(None, 5.0)
        est, row_id, _att = llm_api._reserve("openai", "gpt-5.6-luna", "x" * 100)
        llm_api._settle("openai", "gpt-5.6-luna", est,
                        llm_api._est_tokens("x" * 100), None, row_id)
        con = sqlite3.connect(dbp)
        kind, usd = con.execute("SELECT kind, usd FROM api_spend WHERE id=?",
                                (row_id,)).fetchone()
        con.close()
        assert kind == "settled-unknown-usage"
        assert abs(usd - est) < 1e-12 and usd > 0
    finally:
        llm_api._reset_for_tests()


# --- B4: settlement can never quietly exceed its reservation ------------------

def test_settlement_exceeding_reservation_latches():
    llm_api._reset_for_tests()
    try:
        llm_api.set_budget(None, 50.0)
        est, row_id, _att = llm_api._reserve("openai", "gpt-5.6-luna", "y")
        huge = {"input": 500_000_000, "cached_input": 0, "cache_write": 0,
                "output": 0}
        llm_api._settle("openai", "gpt-5.6-luna", est, llm_api._est_tokens("y"),
                        huge, row_id)
        state = llm_api.budget_state()
        assert state["stopped"] and "EXCEEDED its" in state["stopped"]
        # the HIGHER actual amount was charged, not the low reservation
        assert state["spent_usd"]["openai"] > est
    finally:
        llm_api._reset_for_tests()


# --- B5: no unmetered paid calls ---------------------------------------------

def test_call_api_requires_campaign(monkeypatch):
    llm_api._reset_for_tests()
    monkeypatch.delenv("ARXIV_OBS_ALLOW_UNMETERED", raising=False)
    with pytest.raises(RuntimeError, match="forbidden"):
        llm_api.call_api("hello", "gpt-5.6-luna")


# --- B6: stores are fenced in-transaction ------------------------------------

def test_store_refuses_after_lease_takeover(tmp_path):
    dbp = tmp_path / "l.db"
    con = dbmod.connect(dbp)
    a = classify.RunLease(dbp, "run-f")
    a.acquire()
    a._stop.set()
    # simulate takeover: successor replaces the holder in the durable row
    with con:
        con.execute("UPDATE run_leases SET holder='someone-else' "
                    "WHERE run_id='run-f'")
    with pytest.raises(classify.LeaseHeld):
        classify.store_results(con, "run-f", [], "t", lease=a)
    with pytest.raises(classify.LeaseHeld):
        classify.store_batch_error(con, "run-f", [], RuntimeError("x"), "t",
                                   lease=a)
    con.close()


# --- B1: scoped runs never feed population outputs ----------------------------

def test_report_refuses_scoped_classification_run(fixture_con):
    con = fixture_con
    with con:
        con.execute(
            "INSERT INTO classification_runs (run_id, scan_runs_json, backend, "
            "model, taxonomy_version, isolate, status, code_commit, "
            "params_json) VALUES ('cls-scoped','[\"scan-t\"]','api:openai',"
            "'m','2.5',1,'complete_scoped','abc1234',?)",
            (json.dumps({"scope": {"mode": "papers-file", "n": 3,
                                   "ids_sha256": "ff", "ids": ["a"]}}),))
    with pytest.raises(SystemExit, match="SCOPED"):
        report.run_info(con, "scan-t", "cls-scoped")


# --- B8: key scrubbing + refusal normalization --------------------------------

def test_load_env_scrubs_unrelated_provider_keys(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    monkeypatch.setenv("GOOGLE_API_KEY", "g-x")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-o-x")
    llm_api.load_env("openai")
    assert "ANTHROPIC_API_KEY" not in os.environ
    assert "GOOGLE_API_KEY" not in os.environ
    assert os.environ["OPENAI_API_KEY"] == "sk-o-x"


def test_refusal_text_is_withheld(monkeypatch):
    def fake_post(url, headers, body, timeout):
        class R:
            status_code = 200

            @staticmethod
            def json():
                return {"id": "c1", "model": "gpt-5.6-luna",
                        "usage": {"prompt_tokens": 5, "completion_tokens": 1},
                        "choices": [{"finish_reason": "stop", "message": {
                            "refusal": "VERY SENSITIVE ECHOED CONTENT"}}]}
        return R()
    monkeypatch.setattr(llm_api, "_post", fake_post)
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    llm_api._reset_for_tests()
    try:
        llm_api.set_budget(None, 50.0)
        with pytest.raises(RuntimeError) as ei:
            llm_api.call_api("p", "gpt-5.6-luna")
        assert "ECHOED" not in str(ei.value)
        assert "withheld" in str(ei.value)
    finally:
        llm_api._reset_for_tests()


# --- campaign events ----------------------------------------------------------

def test_campaign_creation_is_event_logged(tmp_path):
    dbp = tmp_path / "e.db"
    dbmod.connect(dbp).close()
    llm_api.create_campaign(dbp, "AP-E", "openai", "gpt-5.6-luna", 2.0, "why")
    con = sqlite3.connect(dbp)
    ev = con.execute("SELECT event, detail_json FROM campaign_events WHERE "
                     "approval_id='AP-E'").fetchall()
    con.close()
    assert len(ev) == 1 and ev[0][0] == "created"
    assert json.loads(ev[0][1])["cap_usd"] == 2.0
