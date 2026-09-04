"""Review-11 regression tests: honest comprehension checking (A1),
machine-visible co-located R5 states (A5), diagnostic preservation in paper
rollup (A6), corrected cached-read tariff + snapshot authority (B1/B2),
hardened campaign closure (B3), and scan-target validation (B5)."""

import json
import sqlite3

import pytest

from pipeline import (classify, comprehension, db as dbmod, llm_api, report,
                      taxonomy)

SNIP = "Acknowledgments. We thank ChatGPT for help with the writing."


def _author(**over):
    lab = {"polarity": "author_use", "tools": ["ChatGPT"], "models": [],
           "categories": ["writing_editing"], "epistemic_impact": "supportive",
           "locations": ["acknowledgments"], "confidence": 0.9,
           "quote": "We thank ChatGPT for help",
           "flags": {"catalytic": False}}
    lab.update(over)
    return lab


# --- A5: co-located R5 states are machine-visible and consistent -------------

def test_r5_booleans_required_and_consistent():
    # v2.8 rewrite of this guard: the co-located booleans are RETIRED —
    # neither the prompt nor the schema mention them, and a label carrying
    # them is rejected as unknown keys (labels across versions never merge)
    header = classify.build_prompt_header()
    assert "has_explicit_zero_attempt" not in header
    schema = llm_api.label_schema()
    assert "has_explicit_zero_attempt" not in schema["required"]
    assert "has_explicit_zero_attempt" not in schema["properties"]
    clean, problems = classify.validate_label(
        _author(has_explicit_zero_attempt=True), SNIP)
    assert clean is None and any("unknown keys" in p for p in problems)
    # scalar zero_contribution stands alone now
    clean, _ = classify.validate_label(
        _author(epistemic_impact="zero_contribution"), SNIP)
    assert clean is not None


# --- A6: diagnostics + R5 booleans survive rollup, order-independently -------

def test_rollup_preserves_ea_and_r5_in_any_order(fixture_con):
    # v2.8 rewrite: a zero_contribution label alongside a cosmetic label —
    # the paper rolls up to the graded impact, and the zero-attempt state
    # derives from the per-label impacts
    con = fixture_con
    lab_use = _author(epistemic_impact="cosmetic", quote_grounded=True)
    lab_ea = _author(epistemic_impact="zero_contribution",
                     categories=["proof_generation"], quote_grounded=True)
    for run, order in (("cls-r11a", (lab_use, lab_ea)),
                       ("cls-r11b", (lab_ea, lab_use))):
        with con:
            con.execute(
                "INSERT INTO classification_runs (run_id, scan_runs_json, "
                "backend, model, taxonomy_version, isolate, status, "
                "code_commit) VALUES (?,'[\"scan-t\"]','api:openai','m',"
                "'2.7',1,'complete','abc1234')", (run,))
            for i, lab in enumerate(order):
                cur = con.execute(
                    "INSERT INTO classification_items (run_id, arxiv_id, "
                    "version, snippet_sha256, status, polarity, label_json, "
                    "quote, quote_grounded, render_status, created_at) "
                    "VALUES (?,'2607.00001',1,?,'ok',?,?,?,?, 'rendered',"
                    "'2026-08-13T00:00:00+00:00')",
                    (run, f"h-{run}-{i}", lab["polarity"], json.dumps(lab),
                     lab["quote"], int(lab["quote_grounded"])))
                con.execute("INSERT INTO classification_evidence VALUES (?,1)",
                            (cur.lastrowid,))
        rollup, _ = report.paper_rollup(con, run, "scan-t", True, False)
        lab = rollup["2607.00001"]
        assert lab["polarity"] == "author_use", run
        # graded impact wins at paper level (v2.8 owner rule)
        assert lab["epistemic_impact"] == "cosmetic", run
        # the fruitless attempt survives via the per-label impact
        assert lab["has_zero_contribution_attempt"] is True, run
        assert lab["has_contributing_use"] is True, run


# --- B2: cached reads at the official rate -----------------------------------

def test_cached_read_priced_at_official_rate():
    p = llm_api.PRICES_USD_PER_MTOK["gpt-5.6-luna"]
    assert p["cached_input"] == 0.02 and p["cache_write"] == 0.25
    usd = llm_api._cost_usd_classes(
        "gpt-5.6-luna", {"input": 0, "cached_input": 1_000_000,
                         "cache_write": 0, "output": 0})
    assert abs(usd - 0.02) < 1e-12
    # the worst-rate reservation still covers the cache-write class
    assert llm_api._worst_input_rate("gpt-5.6-luna") == 0.25


# --- B1: the campaign snapshot is the pricing authority ----------------------

def test_campaign_snapshot_overrides_code_table(tmp_path):
    dbp = tmp_path / "s.db"
    dbmod.connect(dbp).close()
    llm_api._reset_for_tests()
    try:
        llm_api.create_campaign(dbp, "AP-SNAP", "openai", "gpt-5.6-luna",
                                5.0, "p")
        snap = {"gpt-5.6-luna": {"input": 0.50, "cached_input": 0.05,
                                 "cache_write": 0.60, "output": 2.00,
                                 "asof": "test"}}
        con = sqlite3.connect(dbp)
        with con:
            con.execute("UPDATE budget_campaigns SET price_snapshot_json=? "
                        "WHERE approval_id='AP-SNAP'", (json.dumps(snap),))
        con.close()
        llm_api.attach_ledger(dbp, "r-snap", approval_id="AP-SNAP",
                              provider="openai", model="gpt-5.6-luna",
                              cap_usd=5.0)
        # settlement/reservation now price from the BOUND snapshot, not the
        # mutable code table (review-11 B1)
        assert llm_api._price("gpt-5.6-luna")["input"] == 0.50
        usd = llm_api._cost_usd_classes(
            "gpt-5.6-luna", {"input": 1_000_000, "cached_input": 0,
                             "cache_write": 0, "output": 0})
        assert abs(usd - 0.50) < 1e-12
    finally:
        llm_api._reset_for_tests()
    assert llm_api._price("gpt-5.6-luna")["input"] == 0.20  # fallback restored


# --- B3: closure refuses unresolved reservations -----------------------------

def test_close_campaign_refuses_open_reservations(tmp_path, monkeypatch):
    dbp = tmp_path / "c.db"
    dbmod.connect(dbp).close()
    llm_api.create_campaign(dbp, "AP-CL", "openai", "gpt-5.6-luna", 5.0, "p")
    con = sqlite3.connect(dbp)
    with con:
        con.execute("INSERT INTO api_spend (ts, run_id, provider, model, "
                    "kind, usd, approval_id) VALUES ('t','r','openai',"
                    "'gpt-5.6-luna','reserved',0.01,'AP-CL')")
    con.close()
    monkeypatch.setattr(llm_api.db, "DB_PATH", dbp)
    monkeypatch.setattr("sys.argv", ["llm_api", "close-campaign",
                                     "--approval-id", "AP-CL",
                                     "--reconciliation-note", "n"])
    with pytest.raises(SystemExit, match="unresolved reservation"):
        llm_api.main()


# --- B5: scan-target validation ----------------------------------------------

def test_report_scoped_params_detection_still_works(fixture_con):
    # guard: the earlier scoped-refusal path remains intact after the
    # review-11 edits
    con = fixture_con
    with con:
        con.execute(
            "INSERT INTO classification_runs (run_id, scan_runs_json, "
            "backend, model, taxonomy_version, isolate, status, code_commit, "
            "params_json) VALUES ('cls-sc2','[\"scan-t\"]','api:openai','m',"
            "'2.7',1,'complete_scoped','abc1234','{}')")
    with pytest.raises(SystemExit, match="SCOPED"):
        report.run_info(con, "scan-t", "cls-sc2")


# --- A1: the comprehension checker computes, never asserts -------------------

def test_comprehension_checker_reports_instability_honestly():
    keys = [k for k, _, _, _ in comprehension.VIGNETTES]
    base = {k: {"polarity": e["polarity"],
                "impact": e.get("impact", e.get("impact_any_of", ["x"])[0]),
                "categories": sorted(e["categories"]),
                "flags": {f: (f in e["flags"]) for f in taxonomy.FLAGS},
                "location": e.get("location",
                                  e.get("location_any_of", ["unknown"])[0])}
            for k, _, _, e in comprehension.VIGNETTES}
    stable = comprehension.check([base, base, base])
    assert stable["expected_ok"] == stable["n_vignettes"]
    assert stable["stable_counts"]["flags"] == stable["n_vignettes"]
    # perturb ONE flag in ONE repetition: the checker must see it
    import copy
    wobble = copy.deepcopy(base)
    wobble[keys[0]]["flags"]["catalytic"] = True
    res = comprehension.check([base, wobble, base])
    assert res["stable_counts"]["flags"] == res["n_vignettes"] - 1
    row = next(r for r in res["rows"] if r["vignette"] == keys[0])
    assert not row["stable"]["flags"]
    assert "flags" in row["expected_mismatches"]
