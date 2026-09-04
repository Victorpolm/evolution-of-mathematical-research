import json
import os
import sys
from pathlib import Path

# review-10 B5: call_api requires an attached campaign; unit tests opt into
# the explicit unmetered override (the requirement itself is tested with
# monkeypatch.delenv in test_review10)
os.environ.setdefault("ARXIV_OBS_ALLOW_UNMETERED", "1")

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import db  # noqa: E402


@pytest.fixture()
def fixture_con(tmp_path):
    """Fresh head-schema DB with a tiny 3-paper release: one grounded
    author_use, one topic_only, one clean negative."""
    con = db.connect(tmp_path / "fixture.db")
    now = "2026-08-10T00:00:00+00:00"
    with con:
        for pid, created in [("2607.00001", "2026-07-02"),
                             ("2607.00002", "2026-07-03"),
                             ("2608.00003", "2026-08-01")]:
            con.execute("INSERT INTO papers (arxiv_id, primary_category, created, "
                        "latest_version, title) VALUES (?, 'math.AG', ?, 1, 'T')",
                        (pid, created))
        con.execute("INSERT INTO scan_runs (run_id, stage, lexicon_version, "
                    "status, code_commit) VALUES "
                    "('scan-t','tex','2.1','complete','abc1234')")
        for pid, st, nh, v in [("2607.00001", "ok", 1, 1),
                               ("2607.00002", "ok", 1, 2),
                               ("2608.00003", "ok", 0, 1)]:
            con.execute("INSERT INTO scan_items (run_id, arxiv_id, version, status, "
                        "n_hits, scanned_at) VALUES ('scan-t',?,?,?,?,?)",
                        (pid, v, st, nh, now))
        con.execute("INSERT INTO scan_hits (arxiv_id, version, source_kind, term, "
                    "tier, offset, context, rule_class, scan_run) VALUES "
                    "('2607.00001',1,'tex','ChatGPT','llm',10,"
                    "'We thank ChatGPT for help','ack_usage','scan-t')")
        con.execute("INSERT INTO scan_hits (arxiv_id, version, source_kind, term, "
                    "tier, offset, context, rule_class, scan_run) VALUES "
                    "('2607.00002',2,'tex','GPT','llm',5,"
                    "'GPT models are studied here','plain','scan-t')")
        # freeze-eligible provenance: clean commit stamp, isolated run on the
        # approved api backend (review-4/5 gates); rejection-path tests
        # override individual fields
        con.execute("INSERT INTO classification_runs (run_id, scan_runs_json, "
                    "backend, model, taxonomy_version, isolate, status, "
                    "code_commit) VALUES "
                    "('cls-t','[\"scan-t\"]','api:anthropic','m1','2.0',1,"
                    "'complete','abc1234')")
        lab1 = {"polarity": "author_use", "tools": ["ChatGPT"], "models": [],
                "categories": ["writing_editing"], "epistemic_impact": "cosmetic",
                "locations": ["acknowledgments"], "confidence": 0.95,
                "quote": "We thank ChatGPT", "flags": {}, "quote_grounded": True}
        lab2 = {"polarity": "topic_only", "tools": [], "models": [], "categories": [],
                "epistemic_impact": "none", "locations": ["body"], "confidence": 0.9,
                "quote": "", "flags": {}, "quote_grounded": False}
        con.execute("INSERT INTO classification_items (run_id, arxiv_id, version, "
                    "snippet_sha256, status, polarity, label_json, quote, "
                    "quote_grounded, render_status, created_at) VALUES "
                    "('cls-t','2607.00001',1,'h1','ok','author_use',?,"
                    "'We thank ChatGPT',1,'rendered',?)", (json.dumps(lab1), now))
        con.execute("INSERT INTO classification_items (run_id, arxiv_id, version, "
                    "snippet_sha256, status, polarity, label_json, quote, "
                    "quote_grounded, render_status, created_at) VALUES "
                    "('cls-t','2607.00002',2,'h2','ok','topic_only',?,'',0,"
                    "'unchecked',?)", (json.dumps(lab2), now))
        # evidence lineage: item 1 <- hit 1 (scan-t), item 2 <- hit 2 (scan-t)
        con.execute("INSERT INTO classification_evidence VALUES (1, 1)")
        con.execute("INSERT INTO classification_evidence VALUES (2, 2)")
    return con
