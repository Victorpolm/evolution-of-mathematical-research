"""Review-8 Gate A regression tests: prompt/schema parity (A2),
human/machine label-space parity (A3), paper-level flag aggregation (A3),
campaign-scoped durable budgets (B1), lease fencing (B2), and split/attempt
provenance (B3)."""

import json
import sqlite3

import pytest

from pipeline import annotate, classify, db as dbmod, llm_api, taxonomy

SNIP = "Acknowledgments. We thank ChatGPT for help with the writing."
MACHINE_AUTHOR = {
    "polarity": "author_use", "tools": ["ChatGPT"], "models": [],
    "categories": ["writing_editing"], "epistemic_impact": "supportive",
    "locations": ["acknowledgments"], "confidence": 0.9,
    "quote": "We thank ChatGPT for help",
    "flags": {"catalytic": False}}


# --- A2: prompt/schema/validator parity --------------------------------------

def test_prompt_names_every_flag_and_no_stale_none():
    header = classify.build_prompt_header()
    flags_example = json.dumps({f: False for f in taxonomy.FLAGS})
    assert flags_example in header  # generated example covers ALL flags
    assert '"none"' not in header   # v2.2+ has no impact 'none'
    assert "not_applicable" in header


def test_retry_note_demands_object_shape():
    assert '{"labels"' in classify.RETRY_SCHEMA_NOTE
    assert "array" not in classify.RETRY_SCHEMA_NOTE


def test_schema_and_validator_require_the_same_fields():
    schema = llm_api.label_schema()
    assert set(schema["required"]) == classify.ALLOWED_KEYS | {"id"}
    assert set(schema["properties"]["flags"]["required"]) == set(taxonomy.FLAGS)
    assert set(schema["properties"]["epistemic_impact"]["enum"]) \
        == set(taxonomy.IMPACTS)
    assert set(schema["properties"]["polarity"]["enum"]) \
        == set(taxonomy.POLARITIES)
    # the local fail-closed authority requires every flag key, like strict
    # mode — and rejects retired v2.7 flag keys (v2.8)
    clean, problems = classify.validate_label(
        dict(MACHINE_AUTHOR, flags={}), SNIP)
    assert clean is None and any("missing flag keys" in p for p in problems)
    clean, problems = classify.validate_label(
        dict(MACHINE_AUTHOR, flags={"catalytic": False,
                                    "method_component": False}), SNIP)
    assert clean is None and any("unknown flags" in p for p in problems)


# --- A3: human/machine parity ------------------------------------------------

def test_human_machine_cross_field_parity_matrix():
    """Every impact x catalytic combination is accepted or rejected
    IDENTICALLY by the machine validator and the human ingest validator."""
    for impact in taxonomy.IMPACTS:
        for cat in (False, True):
            m_ok = classify.validate_label(
                dict(MACHINE_AUTHOR, epistemic_impact=impact,
                     flags={"catalytic": cat}),
                SNIP)[0] is not None
            h_ok = annotate.validate_verdict_item(
                {"arxiv_id": "0000.00000", "version": 1,
                 "verdict": "TRUE_DISCLOSURE",
                 "categories": ["unspecified"],
                 "locations": ["unknown"], "impact": impact,
                 "flags": ["catalytic"] if cat else [],
                 "tools": "", "notes": ""})[0] is not None
            if impact == "not_applicable":
                assert not m_ok and not h_ok
            else:
                assert m_ok == h_ok, (impact, cat)


def test_human_topic_only_method_component_roundtrip():
    # v2.8: the tri-state diagnostics are RETIRED — a legacy export carrying
    # them is rejected, never silently dropped (labels across taxonomy
    # versions are never merged)
    item = {"arxiv_id": "0000.00000", "version": 1, "verdict": "TOPIC_ONLY",
            "categories": [], "locations": [], "impact": "", "flags": [],
            "method_component": "yes", "tools": "", "notes": ""}
    clean, err = annotate.validate_verdict_item(item)
    assert clean is None and "legacy" in err
    plain = {"arxiv_id": "0000.00000", "version": 1, "verdict": "TOPIC_ONLY",
             "categories": [], "locations": [], "impact": "", "flags": [],
             "tools": "", "notes": ""}
    clean, err = annotate.validate_verdict_item(plain)
    assert clean is not None, err
    assert clean["impact"] == "not_applicable"  # canonical, never ""
    # catalytic on a non-disclosure verdict fails closed (shared invariant)
    assert annotate.validate_verdict_item(
        dict(plain, flags=["catalytic"]))[0] is None


def test_paper_rollup_flag_aggregation_is_order_independent(fixture_con):
    from pipeline import report
    con = fixture_con
    lab_cat = dict(MACHINE_AUTHOR, flags={"catalytic": True},
                   quote_grounded=True)
    lab_mc = {"polarity": "topic_only", "tools": [], "models": [],
              "categories": [], "epistemic_impact": "not_applicable",
              "locations": ["body"], "confidence": 0.9, "quote": "",
              "flags": {"catalytic": False}, "quote_grounded": False}
    for run, order in (("cls-o1", (lab_cat, lab_mc)),
                       ("cls-o2", (lab_mc, lab_cat))):
        with con:
            con.execute(
                "INSERT INTO classification_runs (run_id, scan_runs_json, "
                "backend, model, taxonomy_version, isolate, status, "
                "code_commit) VALUES (?,'[\"scan-t\"]','api:openai','m',"
                "'2.3',1,'complete','abc1234')", (run,))
            for i, lab in enumerate(order):
                cur = con.execute(
                    "INSERT INTO classification_items (run_id, arxiv_id, "
                    "version, snippet_sha256, status, polarity, label_json, "
                    "quote, quote_grounded, render_status, created_at) "
                    "VALUES (?,'2607.00001',1,?,'ok',?,?,?,?, 'rendered',"
                    "'2026-08-12T00:00:00+00:00')",
                    (run, f"h-{run}-{i}", lab["polarity"], json.dumps(lab),
                     lab["quote"], int(lab["quote_grounded"])))
                con.execute("INSERT INTO classification_evidence VALUES (?,1)",
                            (cur.lastrowid,))
        rollup, _ = report.paper_rollup(con, run, "scan-t", True, False)
        assert rollup["2607.00001"]["polarity"] == "author_use"
        assert rollup["2607.00001"]["flags"].get("catalytic") is True, run


# --- B1: campaign-scoped durable budget --------------------------------------

def test_campaign_never_inherits_prior_spend_and_is_cross_process(tmp_path):
    dbp = tmp_path / "b.db"
    dbmod.connect(dbp).close()
    con = sqlite3.connect(dbp)
    with con:  # $21.81 of pre-campaign pilot spend, no approval id
        con.execute("INSERT INTO api_spend (ts, run_id, provider, model, kind, "
                    "usd) VALUES ('t','r0','openai','gpt-5.6-luna','settled',"
                    "21.81)")
    llm_api._reset_for_tests()
    try:
        # review-9 B1: campaigns are pre-created in a deliberate step
        llm_api.create_campaign(dbp, "APPROVAL-T", "openai", "gpt-5.6-luna",
                                1.0, "test campaign")
        llm_api.attach_ledger(dbp, "r1", approval_id="APPROVAL-T",
                              provider="openai", model="gpt-5.6-luna",
                              cap_usd=1.0)
        llm_api.set_budget(None, 1.0)
        # fresh campaign baseline ignores the $21.81 (review-8 B1)
        assert llm_api.budget_state()["spent_usd"].get("openai", 0.0) == 0.0
        est, row_id, _att = llm_api._reserve("openai", "gpt-5.6-luna", "x" * 3000)
        assert row_id is not None
        llm_api._release("openai", "gpt-5.6-luna", est,
                         llm_api._est_tokens("x" * 3000), row_id)
        # ANOTHER process reserves nearly the whole campaign cap durably
        with con:
            con.execute("INSERT INTO api_spend (ts, run_id, provider, model, "
                        "kind, usd, approval_id) VALUES ('t','r2','openai',"
                        "'gpt-5.6-luna','reserved',0.999,'APPROVAL-T')")
        with pytest.raises(llm_api.BudgetExceeded):
            llm_api._reserve("openai", "gpt-5.6-luna", "x" * 3000)
    finally:
        llm_api._reset_for_tests()
        con.close()


def test_campaign_binding_is_strict(tmp_path):
    dbp = tmp_path / "b2.db"
    dbmod.connect(dbp).close()
    llm_api._reset_for_tests()
    try:
        llm_api.create_campaign(dbp, "APPROVAL-S", "openai", "gpt-5.6-luna",
                                5.0, "test campaign")
        llm_api.attach_ledger(dbp, "r1", approval_id="APPROVAL-S",
                              provider="openai", model="gpt-5.6-luna",
                              cap_usd=5.0)
        llm_api._reset_for_tests()
        with pytest.raises(RuntimeError, match="one campaign, one cap"):
            llm_api.attach_ledger(dbp, "r2", approval_id="APPROVAL-S",
                                  provider="openai", model="gpt-5.6-luna",
                                  cap_usd=9.0)
        llm_api._reset_for_tests()
        with pytest.raises(RuntimeError, match="one approval"):
            llm_api.attach_ledger(dbp, "r3", approval_id="APPROVAL-S",
                                  provider="anthropic",
                                  model="claude-haiku-4-5-20251001",
                                  cap_usd=5.0)
    finally:
        llm_api._reset_for_tests()


# --- B2: lease fencing -------------------------------------------------------

def test_lease_acquire_refuse_takeover_and_fencing(tmp_path):
    dbp = tmp_path / "l.db"
    dbmod.connect(dbp).close()
    a = classify.RunLease(dbp, "run-x")
    a.acquire()
    a._stop.set()  # silence keeper for the test
    b = classify.RunLease(dbp, "run-x")
    with pytest.raises(classify.LeaseHeld):
        b.acquire()  # fresh heartbeat: concurrent start refused
    con = sqlite3.connect(dbp)
    with con:  # age the heartbeat beyond the stale threshold
        con.execute("UPDATE run_leases SET heartbeat_at="
                    "'2020-01-01T00:00:00+00:00' WHERE run_id='run-x'")
    c = classify.RunLease(dbp, "run-x")
    c.acquire()  # stale takeover succeeds and is audited
    c._stop.set()
    assert c.took_over_from == a.holder
    # the OLD holder's fenced heartbeat fails and cannot refresh the lease
    assert a.heartbeat() is False
    # the old holder's release cannot delete the successor's lease
    a.release()
    row = con.execute("SELECT holder FROM run_leases WHERE run_id='run-x'"
                      ).fetchone()
    assert row is not None and row[0] == c.holder
    c.release()
    assert con.execute("SELECT COUNT(*) FROM run_leases").fetchone()[0] == 0
    con.close()


# --- B3: split/attempt provenance --------------------------------------------

def _leaf_label():
    return {"id": 0, "polarity": "topic_only", "tools": [], "models": [],
            "categories": [], "epistemic_impact": "not_applicable",
            "locations": ["unknown"], "confidence": 0.5, "quote": "",
            "flags": {"catalytic": False}}


def test_bisection_records_map_children_to_exact_snippets():
    batch = [{"arxiv_id": f"000{i}.0000{i}", "version": 1,
              "source_kind": "tex", "member": "m", "terms": ["ChatGPT"],
              "context": "ctx", "input_hash": f"hash{i}", "hit_ids": []}
             for i in range(4)]
    header = classify.build_prompt_header()

    def fake_call(prompt):
        if prompt.count("SNIPPET ") > 1:
            raise RuntimeError("openai: truncated at max_completion_tokens")
        return json.dumps([_leaf_label()])

    out, recs, failed = classify.classify_batch(batch, header, fake_call)
    assert not failed and len(out) == 4
    paths = {r["split_path"]: r for r in recs}
    # the parent failure and both intermediate failures are durable records
    assert "R!" in paths and paths["R!"]["snippet_hashes"] == [
        "hash0", "hash1", "hash2", "hash3"]
    assert paths["R.L!"]["snippet_hashes"] == ["hash0", "hash1"]
    assert paths["R.R!"]["snippet_hashes"] == ["hash2", "hash3"]
    # every leaf record names EXACTLY its own snippet, so child snippet id 0
    # maps unambiguously back through snippet_hashes[0]
    for leaf, h in (("R.L.L", "hash0"), ("R.L.R", "hash1"),
                    ("R.R.L", "hash2"), ("R.R.R", "hash3")):
        assert paths[leaf]["snippet_hashes"] == [h]
        assert paths[leaf]["response_sha256"] is not None
