"""Immutable run management shared by scan/classify stages.

Rules (codex reviews LB-02):
- run ids are unique forever; reusing one is an error, never an overwrite
- a rerun creates a new run and may mark the old one superseded (metadata-only
  status change; hits/items/labels are never deleted)
- every run records protocol identity (code commit, lexicon/taxonomy versions,
  params) at start and a terminal status + counts at finish
"""

from __future__ import annotations

import datetime as dt
import json
import sqlite3
import sys


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def new_run_id(prefix: str) -> str:
    return f"{prefix}-{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%S}"


def _assert_unused(con: sqlite3.Connection, table: str, run_id: str) -> None:
    if con.execute(f"SELECT 1 FROM {table} WHERE run_id=?", (run_id,)).fetchone():
        sys.exit(f"run id '{run_id}' already exists in {table} — runs are "
                 "immutable; pick a new id (rerun without --run to autogenerate)")
    # legacy guard: v1 hits table also namespaces run ids
    if table == "scan_runs" and con.execute(
            "SELECT 1 FROM scan_hits WHERE scan_run=? LIMIT 1", (run_id,)).fetchone():
        sys.exit(f"run id '{run_id}' already has scan_hits rows — pick a new id")


def start_scan_run(con: sqlite3.Connection, run_id: str, stage: str,
                   lexicon_version: str, code_commit: str, params: dict) -> None:
    _assert_unused(con, "scan_runs", run_id)
    with con:
        con.execute(
            "INSERT INTO scan_runs (run_id, stage, lexicon_version, code_commit, "
            "params_json, started_at, status) VALUES (?,?,?,?,?,?,'running')",
            (run_id, stage, lexicon_version, code_commit,
             json.dumps(params, sort_keys=True), utcnow()))


def finish_scan_run(con: sqlite3.Connection, run_id: str, status: str,
                    n_items: int, n_hits: int, n_errors: int,
                    supersedes: str | None = None) -> None:
    with con:
        con.execute(
            "UPDATE scan_runs SET finished_at=?, status=?, n_items=?, n_hits=?, "
            "n_errors=? WHERE run_id=?",
            (utcnow(), status, n_items, n_hits, n_errors, run_id))
        if supersedes and status == "complete":
            con.execute(
                "UPDATE scan_runs SET status='superseded', superseded_by=? "
                "WHERE run_id=? AND status != 'superseded'", (run_id, supersedes))
        elif supersedes:
            # never retire the last good run for a partial replacement
            # (codex review-3: supersede only after acceptance)
            print(f"NOT superseding '{supersedes}': new run is {status}")


def start_classification_run(con: sqlite3.Connection, run_id: str, scan_runs: list[str],
                             backend: str, model: str, prompt_sha256: str,
                             taxonomy_version: str, isolate: bool,
                             code_commit: str, params: dict) -> None:
    _assert_unused(con, "classification_runs", run_id)
    with con:
        con.execute(
            "INSERT INTO classification_runs (run_id, scan_runs_json, backend, model, "
            "prompt_sha256, taxonomy_version, isolate, params_json, code_commit, "
            "started_at, status) VALUES (?,?,?,?,?,?,?,?,?,?,'running')",
            (run_id, json.dumps(scan_runs), backend, model, prompt_sha256,
             taxonomy_version, int(isolate), json.dumps(params, sort_keys=True),
             code_commit, utcnow()))


def finish_classification_run(con: sqlite3.Connection, run_id: str, status: str,
                              n_items: int, n_errors: int,
                              holder: str | None = None) -> None:
    """Terminal-status transition. When `holder` is given, the lease holder is
    re-verified INSIDE the same transaction as the status write (review-12
    B6): a heartbeat check before this call leaves a window in which a stale
    process could overwrite the successor's terminal state."""
    with con:
        if holder is not None:
            row = con.execute("SELECT holder FROM run_leases WHERE run_id=?",
                              (run_id,)).fetchone()
            if row is None or row[0] != holder:
                raise LeaseLostAtFinish(
                    f"lease for run '{run_id}' is no longer held by this "
                    "process — terminal status belongs to the successor")
        con.execute(
            "UPDATE classification_runs SET finished_at=?, status=?, n_items=?, "
            "n_errors=? WHERE run_id=?", (utcnow(), status, n_items, n_errors, run_id))


class LeaseLostAtFinish(RuntimeError):
    pass
