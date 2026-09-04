"""Versioned, append-only schema migrations for observatory.db.

Design rules (codex reviews LB-01/02/03/05):
- migrations are additive; nothing here ever drops or rewrites existing rows
- an existing database is backed up (SQLite backup API) before the first
  migration in a session touches it
- `db.connect()` refuses to serve a database that is behind HEAD_VERSION;
  fresh (empty) databases are initialized to HEAD_VERSION automatically

Usage:
    python3 -m pipeline.migrate            # show status
    python3 -m pipeline.migrate --apply    # backup + apply pending migrations
"""

from __future__ import annotations

import argparse
import datetime as dt
import sqlite3
import sys
from pathlib import Path

# --- v1: baseline hackathon schema (unchanged from the original db.py) -------

V1_BASELINE = """
CREATE TABLE IF NOT EXISTS papers (
    arxiv_id TEXT PRIMARY KEY,          -- e.g. 2606.24135 (new-style, no version)
    title TEXT,
    authors TEXT,
    submitter TEXT,
    abstract TEXT,
    comments TEXT,
    categories TEXT,                    -- space-separated; first entry = primary
    primary_category TEXT,
    msc_class TEXT,
    journal_ref TEXT,
    doi TEXT,
    license TEXT,
    created DATE,                       -- v1 submission date (UTC date)
    latest_version INTEGER,
    oai_datestamp DATE,
    harvested_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_papers_created ON papers(created);
CREATE INDEX IF NOT EXISTS idx_papers_primary ON papers(primary_category);

CREATE TABLE IF NOT EXISTS versions (
    arxiv_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    date TEXT,
    size TEXT,
    PRIMARY KEY (arxiv_id, version)
);

CREATE TABLE IF NOT EXISTS files (
    arxiv_id TEXT NOT NULL,
    kind TEXT NOT NULL,                 -- 'src' | 'pdf' | 'pdf_text'
    version INTEGER,
    path TEXT,
    sha256 TEXT,
    bytes INTEGER,
    fetched_at TEXT,
    status TEXT,
    PRIMARY KEY (arxiv_id, kind)
);

CREATE TABLE IF NOT EXISTS scan_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id TEXT NOT NULL,
    version INTEGER,
    source_kind TEXT,
    file_member TEXT,
    term TEXT,
    tier TEXT,
    offset INTEGER,
    context TEXT,
    rule_class TEXT,
    scan_run TEXT
);
CREATE INDEX IF NOT EXISTS idx_hits_paper ON scan_hits(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_hits_run ON scan_hits(scan_run);

CREATE TABLE IF NOT EXISTS classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id TEXT NOT NULL,
    version INTEGER,
    stage TEXT,
    model TEXT,
    input_hash TEXT,
    label_json TEXT,
    created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_class_paper ON classifications(arxiv_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_class_dedupe
    ON classifications(arxiv_id, stage, model, input_hash);

CREATE TABLE IF NOT EXISTS human_review (
    arxiv_id TEXT PRIMARY KEY,
    version INTEGER,
    classification TEXT,
    evidence TEXT,
    reviewer TEXT,
    reviewed_at TEXT
);
"""

# --- v2: immutable evidence core ---------------------------------------------
# Append-only run/item/evidence tables. The legacy tables above stay in place
# (frozen forensic data); all new pipeline stages write exclusively to these.

V2_EVIDENCE_CORE = """
-- Successful immutable blobs, keyed by paper-version + content hash (LB-03).
-- `files` remains the mutable fetch-attempt ledger; this table records only
-- verified successes and is never updated or deleted.
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id TEXT NOT NULL,
    version INTEGER,                    -- effective version of the blob (NULL = unknown)
    kind TEXT NOT NULL CHECK (kind IN ('src','pdf')),
    requested_version INTEGER,          -- version asked for at fetch time
    path TEXT NOT NULL,                 -- relative to project root
    sha256 TEXT NOT NULL,
    bytes INTEGER,
    fetch_channel TEXT,                 -- 'export' | 's3-bulk' | 'gcs-pdf' | 'legacy-files'
    fetched_at TEXT,
    format TEXT,                        -- 'tar.gz' | 'tex.gz' | 'pdf' | 'unknown'
    UNIQUE (arxiv_id, kind, version, sha256)
);
CREATE INDEX IF NOT EXISTS idx_artifacts_paper ON artifacts(arxiv_id);

-- One row per scan invocation. Run ids are generated, unique, and never
-- reused; a rerun creates a new run that supersedes the old one (LB-02).
CREATE TABLE IF NOT EXISTS scan_runs (
    run_id TEXT PRIMARY KEY,
    stage TEXT NOT NULL,                -- 'tex' | 'meta' | 'pdf'
    lexicon_version TEXT,
    taxonomy_version TEXT,
    code_commit TEXT,
    params_json TEXT,
    started_at TEXT,
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',  -- running | complete | failed | superseded
    superseded_by TEXT REFERENCES scan_runs(run_id),
    n_items INTEGER,
    n_hits INTEGER,
    n_errors INTEGER
);

-- Per-paper completion ledger: every paper handed to a scan run gets exactly
-- one row, including clean no-hit scans, errors, and skips (LB-01).
CREATE TABLE IF NOT EXISTS scan_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES scan_runs(run_id),
    arxiv_id TEXT NOT NULL,
    version INTEGER,
    artifact_sha256 TEXT,
    status TEXT NOT NULL,               -- 'ok' | 'error:<class>' | 'skipped:<reason>'
    n_hits INTEGER NOT NULL DEFAULT 0,
    detail TEXT,                        -- error text / skipped-member notes
    scanned_at TEXT,
    UNIQUE (run_id, arxiv_id, version)
);
CREATE INDEX IF NOT EXISTS idx_scan_items_run ON scan_items(run_id);
CREATE INDEX IF NOT EXISTS idx_scan_items_paper ON scan_items(arxiv_id);

-- One row per classification invocation; protocol identity is explicit.
CREATE TABLE IF NOT EXISTS classification_runs (
    run_id TEXT PRIMARY KEY,
    scan_runs_json TEXT,                -- JSON list of consumed scan run ids
    backend TEXT,                       -- 'codex'
    model TEXT,                         -- pinned model id as invoked
    prompt_sha256 TEXT,
    taxonomy_version TEXT,
    isolate INTEGER NOT NULL DEFAULT 0, -- 1 = one paper per model call
    params_json TEXT,
    code_commit TEXT,
    started_at TEXT,
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    superseded_by TEXT REFERENCES classification_runs(run_id),
    n_items INTEGER,
    n_errors INTEGER
);

-- One row per classified snippet. Validated labels only; raw model output is
-- retained for audit. Invalid/failed snippets get durable non-ok status
-- instead of vanishing (LB-05/06).
CREATE TABLE IF NOT EXISTS classification_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES classification_runs(run_id),
    arxiv_id TEXT NOT NULL,
    version INTEGER,
    source_kind TEXT,
    file_member TEXT,
    snippet_sha256 TEXT NOT NULL,       -- full protocol input hash
    snippet_text TEXT,                  -- exactly what the model saw
    status TEXT NOT NULL,               -- 'ok' | 'invalid:<reason>' | 'error:<class>'
    polarity TEXT CHECK (polarity IN
        ('author_use','non_use_statement','topic_only','false_positive','unclear')
        OR polarity IS NULL),
    label_json TEXT,                    -- validated structured verdict
    raw_response TEXT,                  -- restricted: for audit only, never published
    quote TEXT,
    quote_grounded INTEGER,             -- 1 = quote found in snippet_text (normalized)
    render_status TEXT NOT NULL DEFAULT 'unchecked',
        -- 'unchecked' | 'rendered' | 'non_rendered_evidence' | 'no_pdf' | 'pdf_error'
    created_at TEXT,
    UNIQUE (run_id, snippet_sha256)
);
CREATE INDEX IF NOT EXISTS idx_class_items_run ON classification_items(run_id);
CREATE INDEX IF NOT EXISTS idx_class_items_paper ON classification_items(arxiv_id);

-- Normalized evidence chain: which scan hits fed which classification (LB-02).
CREATE TABLE IF NOT EXISTS classification_evidence (
    classification_item_id INTEGER NOT NULL REFERENCES classification_items(id),
    scan_hit_id INTEGER NOT NULL REFERENCES scan_hits(id),
    PRIMARY KEY (classification_item_id, scan_hit_id)
);

-- Render-truth checks (DESIGN_PLATFORM §8): does the evidence quote occur in
-- the arXiv-compiled, version-pinned PDF text?
CREATE TABLE IF NOT EXISTS render_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classification_item_id INTEGER REFERENCES classification_items(id),
    arxiv_id TEXT NOT NULL,
    version INTEGER,
    pdf_sha256 TEXT,
    pdf_source TEXT,                    -- 'gcs' | 'export' | 'corpus'
    quote_normalized TEXT,
    matched INTEGER,                    -- 1 = quote found in rendered text
    method TEXT,                        -- 'exact' | 'fuzzy' | 'anchor-miss' | 'no-text'
    score REAL,
    checked_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_render_paper ON render_checks(arxiv_id);

-- Human annotations, append-only, multi-reviewer (replaces single-row
-- human_review for new work; old table kept as frozen history).
CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,              -- e.g. 'gold-v1', 'calibration-2026-08'
    arxiv_id TEXT NOT NULL,
    version INTEGER,
    reviewer TEXT NOT NULL,
    blinded INTEGER NOT NULL DEFAULT 0, -- 1 = reviewer did not see machine labels
    verdict TEXT,                       -- project-specific enum, see codebook
    label_json TEXT,                    -- structured labels (taxonomy vocabulary)
    notes TEXT,
    codebook_version TEXT,
    created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_annotations_paper ON annotations(project, arxiv_id);

-- Frozen analysis releases: reports/site builds name exactly one (LB-05).
CREATE TABLE IF NOT EXISTS releases (
    release_id TEXT PRIMARY KEY,
    created_at TEXT,
    code_commit TEXT,
    cohort_json TEXT,                   -- dates, category rule, version policy
    scan_run TEXT REFERENCES scan_runs(run_id),
    classification_run TEXT REFERENCES classification_runs(run_id),
    manifest_json TEXT,                 -- counts, provenance, checksums
    notes TEXT
);
"""

# --- v3: backfill artifacts from the legacy files ledger ---------------------
# Successful fetches recorded before v2 become artifact rows; channel
# 'legacy-files' marks them as backfilled (version = requested = assumed
# effective, which held for export.arxiv.org version-pinned URLs).

V3_ARTIFACT_BACKFILL = """
INSERT OR IGNORE INTO artifacts
    (arxiv_id, version, kind, requested_version, path, sha256, bytes,
     fetch_channel, fetched_at, format)
SELECT arxiv_id, version, kind, version, path, sha256, bytes,
       'legacy-files', fetched_at,
       CASE WHEN path LIKE '%.tar.gz' THEN 'tar.gz'
            WHEN path LIKE '%.tex.gz' THEN 'tex.gz'
            WHEN path LIKE '%.pdf' THEN 'pdf'
            ELSE 'unknown' END
FROM files
WHERE status LIKE 'ok%' AND path IS NOT NULL AND sha256 IS NOT NULL
      AND kind IN ('src','pdf');
"""

MIGRATIONS: list[tuple[int, str, object]] = [  # sql: str | Callable[[con], None]
    (1, "baseline hackathon schema", V1_BASELINE),
    (2, "immutable evidence core (runs/items/evidence/annotations/releases)",
     V2_EVIDENCE_CORE),
    (3, "backfill artifacts from legacy files successes", V3_ARTIFACT_BACKFILL),
    # review-5 P0-8: explicit-v1 vs inferred-single-version must be distinct,
    # frozen strata — never silently identical
    (4, "scan_items.version_basis (v1 provenance stratum)",
     "ALTER TABLE scan_items ADD COLUMN version_basis TEXT;"),
    # review-6 P0-1: provider spend must be cumulative across processes and
    # resumes — the owner budget is per-provider-pilot, not per-invocation
    (5, "api_spend ledger (durable cross-process budget accounting)",
     "CREATE TABLE IF NOT EXISTS api_spend (\n"
     "  id INTEGER PRIMARY KEY,\n"
     "  ts TEXT NOT NULL,\n"
     "  run_id TEXT,\n"
     "  provider TEXT NOT NULL,\n"
     "  model TEXT NOT NULL,\n"
     "  kind TEXT NOT NULL,\n"          # 'settled' | 'failed-reserved'
     "  usd REAL NOT NULL,\n"
     "  tokens_in INTEGER,\n"
     "  tokens_out INTEGER\n"
     ");\n"
     "CREATE INDEX IF NOT EXISTS idx_api_spend_provider ON api_spend(provider);"),
    # review-7 P0-4: concurrent resume processes must not both pay for the
    # same run — single-writer lease with heartbeat takeover
    (6, "run_leases (single-writer API run lease)",
     "CREATE TABLE IF NOT EXISTS run_leases (\n"
     "  run_id TEXT PRIMARY KEY,\n"
     "  holder TEXT NOT NULL,\n"
     "  acquired_at TEXT NOT NULL,\n"
     "  heartbeat_at TEXT NOT NULL\n"
     ");"),
    # review-8 B1/B3: the owner budget is per-provider PER CAMPAIGN — a
    # durable campaign object scopes every spend row to its approval id, so
    # a new approval never inherits prior pilots' spend and two processes
    # admit reservations against ONE durable sum (BEGIN IMMEDIATE), never
    # against process-local memory. api_attempts makes every physical
    # dispatch a durable row linked to its reservation, split path, and
    # exact snippet hashes.
    (7, "budget_campaigns + api_spend.approval_id + api_attempts provenance",
     "ALTER TABLE api_spend ADD COLUMN approval_id TEXT;\n"
     "CREATE INDEX IF NOT EXISTS idx_api_spend_approval "
     "ON api_spend(approval_id);\n"
     "CREATE TABLE IF NOT EXISTS budget_campaigns (\n"
     "  approval_id TEXT PRIMARY KEY,\n"
     "  provider TEXT NOT NULL,\n"
     "  model TEXT NOT NULL,\n"
     "  cap_usd REAL NOT NULL,\n"
     "  price_snapshot_json TEXT,\n"
     "  purpose TEXT,\n"
     "  status TEXT NOT NULL DEFAULT 'active',\n"
     "  created_at TEXT NOT NULL,\n"
     "  closed_at TEXT\n"
     ");\n"
     "CREATE TABLE IF NOT EXISTS api_attempts (\n"
     "  id INTEGER PRIMARY KEY,\n"
     "  ts TEXT NOT NULL,\n"
     "  run_id TEXT,\n"
     "  approval_id TEXT,\n"
     "  provider TEXT NOT NULL,\n"
     "  model TEXT NOT NULL,\n"
     "  endpoint TEXT,\n"
     "  request_id TEXT,\n"
     "  returned_model TEXT,\n"
     "  system_fingerprint TEXT,\n"
     "  stop_reason TEXT,\n"
     "  http_status INTEGER,\n"
     "  usage_json TEXT,\n"
     "  duration_ms INTEGER,\n"
     "  reservation_row_id INTEGER,\n"
     "  attempt_no INTEGER,\n"
     "  split_path TEXT,\n"
     "  prompt_sha256 TEXT,\n"
     "  snippet_hashes_json TEXT\n"
     ");\n"
     "CREATE INDEX IF NOT EXISTS idx_api_attempts_run ON api_attempts(run_id);"),
    # review-10 B5/B6/B7: campaign authorization becomes an append-only event
    # log (creation + amendments are recorded events, never in-place edits of
    # authority); run leases carry a monotonically increasing fencing
    # generation; api_attempts get an explicit dispatch state and a
    # uniqueness guarantee that one reservation backs at most one attempt.
    (8, "campaign_events + lease fencing generation + attempt state",
     "CREATE TABLE IF NOT EXISTS campaign_events (\n"
     "  id INTEGER PRIMARY KEY,\n"
     "  ts TEXT NOT NULL,\n"
     "  approval_id TEXT NOT NULL,\n"
     "  event TEXT NOT NULL,\n"          # 'created' | 'amended' | 'closed'
     "  detail_json TEXT\n"
     ");\n"
     "CREATE INDEX IF NOT EXISTS idx_campaign_events "
     "ON campaign_events(approval_id);\n"
     "ALTER TABLE run_leases ADD COLUMN generation INTEGER NOT NULL DEFAULT 0;\n"
     "ALTER TABLE api_attempts ADD COLUMN state TEXT;\n"
     "CREATE UNIQUE INDEX IF NOT EXISTS idx_api_attempts_reservation "
     "ON api_attempts(reservation_row_id) WHERE reservation_row_id IS NOT NULL;"),
    # review-12: raw provider responses are hashed at record time (llm_api
    # _resp_sha) so evidence disputes can be settled against the exact bytes.
    # Callable, not SQL: the live DB received the column ad hoc when the
    # hashing landed (the v2.7 run recorded hashes), so the ALTER must be
    # guarded — SQLite has no ADD COLUMN IF NOT EXISTS.
    (9, "api_attempts.response_sha256 (durable response-hash provenance)",
     lambda con: None if "response_sha256" in {
         r[1] for r in con.execute("PRAGMA table_info(api_attempts)")
     } else con.execute(
         "ALTER TABLE api_attempts ADD COLUMN response_sha256 TEXT")),
]
HEAD_VERSION = MIGRATIONS[-1][0]


def current_version(con: sqlite3.Connection) -> int:
    has_meta = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_version'"
    ).fetchone()
    if not has_meta:
        # pre-migration database: either empty (fresh) or v1 (hackathon)
        has_papers = con.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='papers'"
        ).fetchone()
        return 1 if has_papers else 0
    row = con.execute("SELECT MAX(version) FROM schema_version").fetchone()
    return row[0] or 0


def backup(db_path: Path) -> Path | None:
    """One-time SQLite-API backup before the first migration of an existing DB."""
    if not db_path.exists() or db_path.stat().st_size == 0:
        return None
    bdir = db_path.parent / "backups"
    bdir.mkdir(exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    dest = bdir / f"{db_path.stem}-pre-v{HEAD_VERSION}-{stamp}.db"
    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(dest)
    with dst:
        src.backup(dst)
    src.close()
    dst.close()
    return dest


def apply_pending(con: sqlite3.Connection, verbose: bool = True) -> list[int]:
    """Apply all pending migrations inside exclusive transactions."""
    ver = current_version(con)  # before creating schema_version, so v1 detection works
    con.execute("""CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY, description TEXT, applied_at TEXT)""")
    if ver == 1 and not con.execute(
            "SELECT 1 FROM schema_version WHERE version=1").fetchone():
        # stamp the pre-existing hackathon schema retroactively
        con.execute("INSERT OR IGNORE INTO schema_version VALUES (1, ?, ?)",
                    ("baseline hackathon schema (stamped retroactively)",
                     dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")))
        con.commit()
    applied = []
    for version, desc, sql in MIGRATIONS:
        if version <= ver:
            continue
        # executescript() autocommits any open transaction first, so atomicity
        # must live INSIDE the script: schema + version stamp commit together
        # or not at all (codex re-review F17).
        now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        if callable(sql):
            # same atomicity contract as the script path: schema change and
            # version stamp commit together or not at all
            con.execute("BEGIN IMMEDIATE")
            try:
                sql(con)
                con.execute("INSERT INTO schema_version VALUES (?, ?, ?)",
                            (version, desc, now))
                con.commit()
            except BaseException:
                con.rollback()
                raise
        else:
            safe_desc = desc.replace("'", "''")
            stamp = (f"INSERT INTO schema_version VALUES ({version}, "
                     f"'{safe_desc}', '{now}');")
            script = f"BEGIN IMMEDIATE;\n{sql}\n{stamp}\nCOMMIT;"
            con.executescript(script)
        applied.append(version)
        if verbose:
            print(f"applied migration {version}: {desc}")
    return applied


def main() -> int:
    from . import db  # local import to avoid cycle
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--db", default=None, help="database path (default: observatory.db)")
    args = ap.parse_args()
    db_path = Path(args.db) if args.db else db.DB_PATH
    con = sqlite3.connect(db_path, timeout=60)
    ver = current_version(con)
    print(f"{db_path}: schema version {ver}, head {HEAD_VERSION}")
    if ver > HEAD_VERSION:
        # never "up to date": this checkout cannot know what a newer schema
        # means (db.connect refuses it too — review-4)
        print(f"database schema v{ver} is AHEAD of this code (head "
              f"v{HEAD_VERSION}) — update the code checkout")
        return 1
    if ver == HEAD_VERSION:
        print("up to date")
        return 0
    if not args.apply:
        print("pending migrations:")
        for version, desc, _ in MIGRATIONS:
            if version > ver:
                print(f"  {version}: {desc}")
        print("run with --apply to migrate (a backup is taken first)")
        return 1
    con.close()
    b = backup(db_path)
    if b:
        print(f"backup written to {b}")
    con = sqlite3.connect(db_path, timeout=60)
    apply_pending(con)
    con.close()
    print("migration complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
