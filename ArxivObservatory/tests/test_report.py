import json

import pytest

from pipeline import report


def test_wilson_known_values():
    lo, hi = report.wilson(0, 0)
    assert (lo, hi) == (0.0, 0.0)
    lo, hi = report.wilson(5, 10)
    assert 0.23 < lo < 0.24 and 0.76 < hi < 0.77
    lo, hi = report.wilson(0, 200)
    assert lo == 0.0 and 0.018 < hi < 0.020


def test_md_escape_neutralizes_injection():
    s = report.md_escape("evil | <script>alert(1)</script>\n`x`")
    assert "|" not in s.replace("\\|", "") and "<" not in s and "\n" not in s


def test_build_scoped_report(fixture_con, tmp_path):
    out = tmp_path / "r.md"
    report.build(fixture_con, "scan-t", "cls-t", out, "2026-07-01", "2026-08-08",
                 require_grounded=True, require_rendered=True, freeze="rel-t")
    text = out.read_text()
    # July: 2 scanned, 0 failed/unfetched, 2 flagged, 1 author-use, 0 pending
    assert "| 2026-07 | 2 | 0 | 0 | 2 | 1 | 0 |" in text
    assert "| 2026-08 | 1 | 0 | 0 | 0 | 0 | 0 |" in text
    # per-stratum table: July v1 has the disclosure, July later does not (F12)
    assert "| 2026-07 | v1 | 1 | 1 |" in text
    assert "| 2026-07 | later | 1 | 0 |" in text
    assert "ChatGPT" in text
    rel = fixture_con.execute(
        "SELECT * FROM releases WHERE release_id='rel-t'").fetchone()
    assert rel["scan_run"] == "scan-t" and rel["classification_run"] == "cls-t"
    manifest = json.loads(rel["manifest_json"])
    assert manifest["counts"]["scanned"] == 3
    assert manifest["counts"]["author_use"] == 1
    assert len(manifest["membership_sha256"]["scanned"]) == 64  # verifiable (F11)


def test_unknown_version_is_its_own_stratum(fixture_con, tmp_path):
    with fixture_con:
        fixture_con.execute("UPDATE scan_items SET version=NULL "
                            "WHERE run_id='scan-t' AND arxiv_id='2607.00002'")
    out = tmp_path / "ru.md"
    report.build(fixture_con, "scan-t", "cls-t", out, "2026-07-01", "2026-08-08")
    text = out.read_text()
    # NULL version never coerced to v1 (F1)
    assert "| 2026-07 | unknown | 1 | 0 |" in text
    assert "| 2026-07 | v1 | 1 | 1 |" in text


def test_gates_move_ungated_out_of_headline(fixture_con, tmp_path):
    # flip the author_use item to non-rendered: gated report drops it
    with fixture_con:
        fixture_con.execute(
            "UPDATE classification_items SET render_status='non_rendered_evidence' "
            "WHERE run_id='cls-t' AND arxiv_id='2607.00001'")
    out = tmp_path / "r2.md"
    report.build(fixture_con, "scan-t", "cls-t", out, "2026-07-01", "2026-08-08",
                 require_grounded=True, require_rendered=True)
    text = out.read_text()
    assert "| 2026-07 | 2 | 0 | 0 | 2 | 0 | 0 |" in text
    assert "1 author-use candidates excluded by evidence gates" in text


def test_missing_run_fails_closed(fixture_con, tmp_path):
    with pytest.raises(SystemExit):
        report.run_info(fixture_con, "no-such-run", "cls-t")
    with pytest.raises(SystemExit):
        report.run_info(fixture_con, "scan-t", "no-such-cls")


def test_cross_scan_run_labels_never_leak(fixture_con, tmp_path):
    """Review-3 P0-3: a classification run that consumed two scan runs must
    not contribute labels evidenced by the OTHER run to this denominator."""
    import json as _json
    with fixture_con:
        # second scan run with an author_use hit on the clean paper
        fixture_con.execute(
            "INSERT INTO scan_runs (run_id, stage, lexicon_version, status) "
            "VALUES ('scan-b','tex','2.1','complete')")
        fixture_con.execute(
            "INSERT INTO scan_items (run_id, arxiv_id, version, status, n_hits, "
            "scanned_at) VALUES ('scan-b','2608.00003',1,'ok',1,'t')")
        fixture_con.execute(
            "INSERT INTO scan_hits (arxiv_id, version, source_kind, term, tier, "
            "offset, context, rule_class, scan_run) VALUES "
            "('2608.00003',1,'tex','ChatGPT','llm',0,'We thank ChatGPT a lot',"
            "'ack_usage','scan-b')")
        hit_b = fixture_con.execute("SELECT MAX(id) FROM scan_hits").fetchone()[0]
        fixture_con.execute(
            "UPDATE classification_runs SET scan_runs_json="
            "'[\"scan-b\",\"scan-t\"]' WHERE run_id='cls-t'")
        lab = {"polarity": "author_use", "tools": ["ChatGPT"], "models": [],
               "categories": ["writing_editing"], "epistemic_impact": "cosmetic",
               "locations": ["acknowledgments"], "confidence": 0.9,
               "quote": "We thank ChatGPT a lot", "flags": {},
               "quote_grounded": True}
        fixture_con.execute(
            "INSERT INTO classification_items (run_id, arxiv_id, version, "
            "snippet_sha256, status, polarity, label_json, quote, quote_grounded, "
            "render_status, created_at) VALUES ('cls-t','2608.00003',1,'h3','ok',"
            "'author_use',?,?,1,'rendered','t')",
            (_json.dumps(lab), lab["quote"]))
        item_b = fixture_con.execute(
            "SELECT MAX(id) FROM classification_items").fetchone()[0]
        fixture_con.execute("INSERT INTO classification_evidence VALUES (?,?)",
                            (item_b, hit_b))
    # rollup against scan-t must NOT contain the scan-b-evidenced label
    rollup, _ = report.paper_rollup(fixture_con, "cls-t", "scan-t", False, False)
    assert "2608.00003" not in rollup
    # and against scan-b it must appear
    rollup_b, _ = report.paper_rollup(fixture_con, "cls-t", "scan-b", False, False)
    assert rollup_b["2608.00003"]["polarity"] == "author_use"


def test_freeze_rejects_pending(fixture_con, tmp_path):
    """A flagged-but-unclassified paper blocks a freeze (review-3 P0-4)."""
    with fixture_con:
        # new flagged paper in the scan run with no classification item
        fixture_con.execute(
            "INSERT INTO papers (arxiv_id, primary_category, created, "
            "latest_version) VALUES ('2607.00009','math.CO','2026-07-05',1)")
        fixture_con.execute(
            "INSERT INTO scan_items (run_id, arxiv_id, version, status, n_hits, "
            "scanned_at) VALUES ('scan-t','2607.00009',1,'ok',1,'t')")
        fixture_con.execute(
            "INSERT INTO scan_hits (arxiv_id, version, source_kind, term, tier, "
            "offset, context, rule_class, scan_run) VALUES "
            "('2607.00009',1,'tex','Claude','llm',0,'used Claude','ack_usage',"
            "'scan-t')")
    with pytest.raises(SystemExit):
        report.build(fixture_con, "scan-t", "cls-t", tmp_path / "rp.md",
                     "2026-07-01", "2026-08-08", freeze="rel-pending")


def test_unrelated_runs_rejected(fixture_con):
    # a classification run that consumed a DIFFERENT scan run cannot be
    # paired with this denominator (F2)
    with fixture_con:
        fixture_con.execute(
            "INSERT INTO classification_runs (run_id, scan_runs_json, backend, "
            "model, taxonomy_version, isolate, status) VALUES "
            "('cls-other','[\"scan-other\"]','codex','m1','2.0',0,'complete')")
    with pytest.raises(SystemExit):
        report.run_info(fixture_con, "scan-t", "cls-other")


def test_meta_scan_rejected_as_fulltext_denominator(fixture_con):
    with fixture_con:
        fixture_con.execute(
            "INSERT INTO scan_runs (run_id, stage, lexicon_version, status) "
            "VALUES ('meta-run','meta','2.1','complete')")
        fixture_con.execute(
            "INSERT INTO scan_items (run_id, arxiv_id, version, status, n_hits, "
            "scanned_at) VALUES ('meta-run','2607.00001',1,'ok',0,'t')")
    with pytest.raises(SystemExit):
        report.run_info(fixture_con, "meta-run", "cls-t")


def test_freeze_requires_pinned_complete_runs(fixture_con, tmp_path):
    with fixture_con:
        fixture_con.execute("UPDATE classification_runs SET "
                            "model='codex-default(unpinned)' WHERE run_id='cls-t'")
    with pytest.raises(SystemExit):
        report.run_info(fixture_con, "scan-t", "cls-t", freeze=True)
    with fixture_con:
        fixture_con.execute("UPDATE classification_runs SET model='m1', "
                            "status='partial' WHERE run_id='cls-t'")
    with pytest.raises(SystemExit):
        report.run_info(fixture_con, "scan-t", "cls-t", freeze=True)
