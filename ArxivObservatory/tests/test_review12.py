"""Review-12 regression tests: fenced terminal status (B6), fail-closed
total comprehension expectations (B1), and DB-free legacy-gate refusal
(audit-boundary finding)."""

import copy

import pytest

from pipeline import comprehension, runs


# --- B6: terminal status is holder-fenced inside the transaction -------------

def test_finish_refuses_stale_holder(fixture_con):
    con = fixture_con
    with con:
        con.execute(
            "INSERT INTO classification_runs (run_id, scan_runs_json, backend, "
            "model, taxonomy_version, isolate, status, code_commit) VALUES "
            "('cls-r12','[\"scan-t\"]','api:openai','m','2.7',1,'running','abc')")
        con.execute(
            "INSERT INTO run_leases (run_id, holder, acquired_at, "
            "heartbeat_at, generation) VALUES ('cls-r12','successor:1:aa',"
            "'2026-08-14T00:00:00+00:00','2026-08-14T00:00:00+00:00',2)")
    with pytest.raises(runs.LeaseLostAtFinish):
        runs.finish_classification_run(con, "cls-r12", "complete", 1, 0,
                                       holder="stale:0:bb")
    st = con.execute("SELECT status FROM classification_runs WHERE "
                     "run_id='cls-r12'").fetchone()[0]
    assert st == "running"  # the successor's state was not overwritten
    # the true holder CAN finish
    runs.finish_classification_run(con, "cls-r12", "partial", 1, 0,
                                   holder="successor:1:aa")
    st = con.execute("SELECT status FROM classification_runs WHERE "
                     "run_id='cls-r12'").fetchone()[0]
    assert st == "partial"


# --- B1: expected objects must be total; the checker fails closed ------------

def test_comprehension_expected_objects_are_total():
    for key, _t, _c, exp in comprehension.VIGNETTES:
        assert "polarity" in exp, key
        assert ("impact" in exp) != ("impact_any_of" in exp), key
        assert "flags" in exp and "categories" in exp, key
        assert ("location" in exp) != ("location_any_of" in exp), key


def test_comprehension_check_raises_on_partial_expectation(monkeypatch):
    vs = copy.deepcopy(comprehension.VIGNETTES)
    k, t, c, exp = vs[0]
    del exp["flags"]
    monkeypatch.setattr(comprehension, "VIGNETTES", vs)
    with pytest.raises(ValueError, match="flag and category"):
        comprehension.check([{}])


def _base_reps():
    from pipeline import taxonomy
    return {k: {"polarity": e["polarity"],
                "impact": e.get("impact", e.get("impact_any_of", ["x"])[0]),
                "categories": sorted(e["categories"]),
                "flags": {f: (f in e["flags"]) for f in taxonomy.FLAGS},
                "location": e.get("location",
                                  e.get("location_any_of", ["unknown"])[0])}
            for k, _, _, e in comprehension.VIGNETTES}


def test_comprehension_location_wobble_is_expected_mismatch():
    # v2.8: location is a first-class checked axis (vignette set v2 frames
    # every text so location is testable)
    base = _base_reps()
    wobble = copy.deepcopy(base)
    assert "location" in dict(
        (k, e) for k, _, _, e in comprehension.VIGNETTES)["ack_polish"]
    wobble["ack_polish"]["location"] = "body"
    res = comprehension.check([base, wobble, base])
    row = next(r for r in res["rows"] if r["vignette"] == "ack_polish")
    assert "location" in row["expected_mismatches"]
    assert not row["stable"]["location"]
    assert res["expected_ok"] == res["n_vignettes"] - 1


# --- legacy markdown gate refuses BEFORE any database connection -------------

def test_legacy_gate_never_opens_db(tmp_path, monkeypatch):
    from pipeline import annotate, db as dbmod

    def boom(*a, **k):
        raise AssertionError("db.connect must not be reached")

    monkeypatch.setattr(dbmod, "connect", boom)
    monkeypatch.setattr(annotate.db, "connect", boom)
    monkeypatch.delenv("ARXIV_OBS_LEGACY", raising=False)
    pk = tmp_path / "p.md"
    pk.write_text("## ITEM 1 — arXiv 2607.00001 v1\nVERDICT: TOPIC_ONLY\n")

    class A:
        project, reviewer, packet = "p-t", "r1", str(pk)
        json = None

    with pytest.raises(SystemExit, match="legacy"):
        annotate.cmd_ingest(A)


# --- channel-aware render eligibility (owner decision 2026-08-14) -------------

def test_meta_channel_evidence_passes_render_gate(fixture_con):
    import json as _json
    from pipeline import report
    con = fixture_con
    lab = {"polarity": "author_use", "tools": ["ChatGPT"], "models": [],
           "categories": ["writing_editing"], "epistemic_impact": "cosmetic",
           "locations": ["comments_field"], "confidence": 0.9,
           "quote": "English polished with ChatGPT", "flags": {"catalytic": False},
           "quote_grounded": True}
    with con:
        con.execute(
            "INSERT INTO classification_runs (run_id, scan_runs_json, backend, "
            "model, taxonomy_version, isolate, status, code_commit) VALUES "
            "('cls-meta','[\"scan-t\"]','api:openai','m','2.8',1,'complete','abc')")
        cur = con.execute(
            "INSERT INTO classification_items (run_id, arxiv_id, version, "
            "source_kind, snippet_sha256, status, polarity, label_json, quote, "
            "quote_grounded, render_status, created_at) VALUES ('cls-meta',"
            "'2607.00001',1,'meta:comments','h-meta','ok','author_use',?,?,1,"
            "'unchecked','2026-08-14T00:00:00+00:00')",
            (_json.dumps(lab), lab["quote"]))
        con.execute("INSERT INTO classification_evidence VALUES (?,1)",
                    (cur.lastrowid,))
    rollup, ungated = report.paper_rollup(con, "cls-meta", "scan-t", True, True)
    # require_rendered=True, render_status unchecked — the metadata channel is
    # eligible by construction (Comments always shows on the abstract page)
    assert "2607.00001" not in ungated
    assert rollup["2607.00001"]["polarity"] == "author_use"
