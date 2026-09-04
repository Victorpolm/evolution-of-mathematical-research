"""Regressions from review_codex4.md: freeze contract gaps, fuzzy render
certification, gzip bomb budget, v1 artifact scan jobs, annotate ingest
validation, dedup evidence-edge loss."""

import gzip
import json
from pathlib import Path

import pytest

from pipeline import annotate, report, scan
from pipeline.render_check import match_quote


def _freeze(con, tmp_path, **kw):
    report.build(con, "scan-t", "cls-t", tmp_path / "r.md",
                 "2026-07-01", "2026-08-08", freeze="rel-t", **kw)


def test_freeze_rejects_empty_consumed_runs(fixture_con, tmp_path):
    with fixture_con:
        fixture_con.execute(
            "UPDATE classification_runs SET scan_runs_json='[]' WHERE run_id='cls-t'")
    with pytest.raises(SystemExit, match="consumed"):
        _freeze(fixture_con, tmp_path)


def test_freeze_rejects_dirty_code(fixture_con, tmp_path):
    with fixture_con:
        fixture_con.execute("UPDATE classification_runs SET "
                            "code_commit='abc1234-dirty' WHERE run_id='cls-t'")
    with pytest.raises(SystemExit, match="dirty"):
        _freeze(fixture_con, tmp_path)


def test_freeze_rejects_non_isolated(fixture_con, tmp_path):
    with fixture_con:
        fixture_con.execute(
            "UPDATE classification_runs SET isolate=0 WHERE run_id='cls-t'")
    with pytest.raises(SystemExit, match="isolate"):
        _freeze(fixture_con, tmp_path)


def test_rejected_freeze_writes_no_report(fixture_con, tmp_path):
    """Gate checks must run BEFORE the report file is written."""
    with fixture_con:
        fixture_con.execute(
            "UPDATE classification_runs SET isolate=0 WHERE run_id='cls-t'")
    with pytest.raises(SystemExit):
        _freeze(fixture_con, tmp_path)
    assert not (tmp_path / "r.md").exists()


def test_eligible_freeze_still_freezes(fixture_con, tmp_path):
    _freeze(fixture_con, tmp_path)
    assert fixture_con.execute(
        "SELECT 1 FROM releases WHERE release_id='rel-t'").fetchone()
    assert (tmp_path / "r.md").exists()


def test_fuzzy_match_is_not_exact():
    """match_quote classifies degraded matches as 'fuzzy' — check_run maps
    those to rendered_fuzzy (review-queue), never 'rendered'."""
    quote = "we thank the ChatGPT assistant for improving the exposition"
    pdf = "we thank the Chat GPT assistant kindly for improving the -- exposition"
    ok, method, score = match_quote(quote, pdf)
    assert ok and method == "fuzzy"
    exact_ok, exact_method, _ = match_quote(quote, quote + " and more text")
    assert exact_ok and exact_method == "exact"


def test_single_gz_budget_streams(monkeypatch):
    """A high-ratio gzip payload must be bounded, not fully materialized."""
    monkeypatch.setattr(scan, "MAX_TOTAL_BYTES", 10_000)
    bomb = gzip.compress(b"\\documentclass" + b"a" * 1_000_000)
    hits, notes = scan.scan_archive_bytes(bomb)
    assert hits == []
    assert any(n.startswith("skipped-budget:single-gz") for n in notes)


def test_v1_artifact_jobs(fixture_con):
    con = fixture_con
    with con:
        # explicit v1 artifact (refill) for a multi-version paper
        con.execute("INSERT INTO versions (arxiv_id, version, date) VALUES"
                    "('2607.00001', 1, '2026-07-02')")
        con.execute("INSERT INTO versions (arxiv_id, version, date) VALUES"
                    "('2607.00001', 2, '2026-07-20')")
        con.execute("INSERT INTO artifacts (arxiv_id, version, kind, path, sha256, "
                    "fetch_channel) VALUES ('2607.00001', 1, 'src', "
                    "'corpus/2607/2607.00001/src_v1.tar.gz', 's1', 'export-v1')")
        # single-version paper: bulk blob is metadata-certain v1
        con.execute("INSERT INTO versions (arxiv_id, version, date) VALUES"
                    "('2608.00003', 1, '2026-08-01')")
        con.execute("INSERT INTO artifacts (arxiv_id, version, kind, path, sha256, "
                    "fetch_channel) VALUES ('2608.00003', NULL, 'src', "
                    "'corpus/s3/math_2608.tar::2608.00003.gz', 's3', 's3-bulk')")
        # multi-version paper WITHOUT a v1 artifact: must not appear
        con.execute("INSERT INTO versions (arxiv_id, version, date) VALUES"
                    "('2607.00002', 1, '2026-07-03')")
        con.execute("INSERT INTO versions (arxiv_id, version, date) VALUES"
                    "('2607.00002', 2, '2026-07-25')")
        con.execute("INSERT INTO artifacts (arxiv_id, version, kind, path, sha256, "
                    "fetch_channel) VALUES ('2607.00002', NULL, 'src', "
                    "'corpus/s3/math_2607.tar::2607.00002.gz', 's3b', 's3-bulk')")
    job_list, basis = scan.v1_artifact_jobs(con, None)
    jobs = {j[0]: j for j in job_list}
    assert set(jobs) == {"2607.00001", "2608.00003"}
    assert all(j[1] == 1 for j in jobs.values())  # version-pinned
    assert jobs["2607.00001"][2].endswith("src_v1.tar.gz")
    # explicit vs inferred v1 stay distinct, recorded strata (review-5 P0-8)
    assert basis == {"2607.00001": "explicit-v1",
                     "2608.00003": "inferred-single-version"}
    # flagged restriction: only 2607.00001 has a non-known-fp llm hit
    flagged, _ = scan.v1_artifact_jobs(con, None, flagged_run="scan-t")
    assert [j[0] for j in flagged] == ["2607.00001"]


def test_ingest_rejects_unassigned_and_within_file_dups(fixture_con, tmp_path):
    manifest_dir = tmp_path / "annotation" / "proj-t"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(json.dumps(
        {"assignment": {"2607.00001": "POS"}}))
    verdicts = {"project": "proj-t", "reviewer": "rev1",
                "codebook_version": __import__("pipeline.taxonomy", fromlist=["x"]).TAXONOMY_VERSION, "items": [
        {"arxiv_id": "2607.00001", "version": 1, "verdict": "NO_AI_MENTION"},
        {"arxiv_id": "2607.00001", "version": 1, "verdict": "TOPIC_ONLY"},
        {"arxiv_id": "2699.99999", "version": 1, "verdict": "NO_AI_MENTION"},
    ]}
    jf = tmp_path / "v.json"
    jf.write_text(json.dumps(verdicts))

    class A:
        project, reviewer = "proj-t", "rev1"
        json = str(jf)
        manifest = str(manifest_dir / "manifest.json")

    rc = annotate.ingest_json(fixture_con, A)
    rows = fixture_con.execute(
        "SELECT arxiv_id, verdict FROM annotations WHERE project='proj-t'").fetchall()
    assert [(r["arxiv_id"], r["verdict"]) for r in rows] == [
        ("2607.00001", "NO_AI_MENTION")]  # first wins; dup + unassigned rejected
    assert rc == 1  # unassigned item counted as rejection


def test_extract_json_is_strict_about_tex():
    """review-5 P0-7: no regex repair — a repair regex silently corrupted TeX
    commands beginning with legal JSON escape letters. Malformed escapes AND
    valid-JSON control-char corruption both raise (routing to the re-ask)."""
    from pipeline.classify import extract_json
    # illegal escape (\G): strict parse must raise, never "repair"
    with pytest.raises(json.JSONDecodeError):
        extract_json(r'[{"id": 0, "quote": "the $\Gamma$-invariant map"}]')
    # LEGAL escape that is really corrupted TeX: \beta -> backspace + 'eta'
    # parses as valid JSON — the control-char guard must reject it
    with pytest.raises(ValueError):
        extract_json(r'[{"id": 0, "quote": "we have \beta > 0"}]')
    with pytest.raises(ValueError):
        extract_json(r'[{"id": 0, "quote": "\frac{a}{b}"}]')
    # clean single-line output with properly escaped backslashes passes
    # (review-6 tightened the guard to ALL C0 controls, incl. \n)
    labels = extract_json(r'[{"q": "a b\\c and \\Gamma"}]')
    assert labels[0]["q"] == "a b\\c and \\Gamma"


def test_dedup_keeps_evidence_edges(fixture_con):
    """Content-identical snippets from different hit clusters must still link
    their hits (review-4: 63 lost edges)."""
    from pipeline import classify
    con = fixture_con
    with con:
        con.execute("INSERT INTO scan_hits (arxiv_id, version, source_kind, term, "
                    "tier, offset, context, rule_class, scan_run) VALUES "
                    "('2607.00001',1,'tex','ChatGPT','llm',900,"
                    "'We thank ChatGPT for help','ack_usage','scan-t')")
        hit2 = con.execute("SELECT MAX(id) FROM scan_hits").fetchone()[0]
    lab = {"id": "p1", "polarity": "author_use", "tools": ["ChatGPT"],
           "models": [], "categories": ["writing_editing"],
           "epistemic_impact": "cosmetic", "locations": ["acknowledgments"],
           "confidence": 0.9, "quote": "We thank ChatGPT", "quote_grounded": True,
           "flags": {"catalytic": False, "uncertain": False}}
    snippet = {"id": "p1", "arxiv_id": "2607.00001", "version": 1,
               "source_kind": "tex", "member": None, "input_hash": "h1",
               "context": "We thank ChatGPT for help", "hit_ids": [hit2]}
    classify.store_results(con, "cls-t", [(snippet, lab, lab, [])],
                           "2026-08-11T00:00:00+00:00")
    edges = {r[0] for r in con.execute(
        "SELECT scan_hit_id FROM classification_evidence WHERE "
        "classification_item_id=1")}
    assert hit2 in edges  # new cluster's hit linked despite snippet dedup
