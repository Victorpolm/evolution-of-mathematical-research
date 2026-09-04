"""SQLite spine of the observatory.

Unit of analysis is the paper-version. Schema lives in pipeline/migrate.py as
versioned, additive migrations:
  v1 — hackathon baseline (papers/versions/files/scan_hits/classifications/
       human_review); kept as frozen forensic history
  v2 — immutable evidence core: artifacts, scan_runs/scan_items,
       classification_runs/items/evidence, render_checks, annotations, releases

`connect()` fails closed when the database is behind the code's schema —
run `python3 -m pipeline.migrate --apply` (takes a backup first). Fresh
databases (tests, fixtures) are initialized to head automatically.
"""

from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

from . import migrate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "observatory.db"
CORPUS_DIR = PROJECT_ROOT / "corpus"


class SchemaBehindError(RuntimeError):
    pass


def connect(db_path: Path | str = DB_PATH, readonly: bool = False) -> sqlite3.Connection:
    db_path = Path(db_path)
    fresh = not db_path.exists() or db_path.stat().st_size == 0
    if readonly:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=60)
    else:
        con = sqlite3.connect(db_path, timeout=60)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA foreign_keys=ON")
    con.row_factory = sqlite3.Row
    ver = migrate.current_version(con)
    if ver < migrate.HEAD_VERSION:
        if fresh and not readonly:
            migrate.apply_pending(con, verbose=False)
        else:
            con.close()
            raise SchemaBehindError(
                f"{db_path} is at schema version {ver}, code expects "
                f"{migrate.HEAD_VERSION} — run: python3 -m pipeline.migrate --apply")
    elif ver > migrate.HEAD_VERSION:
        con.close()
        raise SchemaBehindError(
            f"{db_path} is at schema version {ver}, AHEAD of this code "
            f"(head {migrate.HEAD_VERSION}) — update the checkout")
    return con


def code_commit() -> str:
    """Current git commit (+ '-dirty' when the tree has changes); provenance stamp."""
    try:
        rev = subprocess.run(["git", "-C", str(PROJECT_ROOT), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(PROJECT_ROOT), "status", "--porcelain"],
                               capture_output=True, text=True, timeout=10).stdout.strip()
        return rev + ("-dirty" if dirty else "") if rev else "unknown"
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
