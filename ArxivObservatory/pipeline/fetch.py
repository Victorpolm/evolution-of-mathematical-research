"""Polite serial fetcher for arXiv e-print sources.

- one request at a time, POLITE_DELAY between requests, Retry-After honored
- pins the version recorded at harvest time (e-print/<id>v<n>)
- resumable: papers with a terminal status in `files` are skipped
- seeded-random fetch order, so a partially fetched corpus is an unbiased
  random sample of the selection (interim statistics stay honest)
- e-print responses are gzip tarballs, gzip single TeX files, or bare PDFs
  (pdf-only submissions); stored under corpus/<yymm>/<id>/ without extraction

Usage:
    python3 -m pipeline.fetch --months 2608 2607 [--limit N]
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import random
import sys
import tarfile
import time
from pathlib import Path

import requests

from . import db

EPRINT_URL = "https://export.arxiv.org/e-print/{id}v{v}"
USER_AGENT = "ArxivObservatory/0.1 (research pilot; contact: jo314schmitt@gmail.com)"
# base spacing between requests; tune via env when arXiv 429s (each 429 costs
# a 60s Retry-After wait, so a higher clean rate can be net faster)
POLITE_DELAY = float(os.environ.get("ARXIV_FETCH_DELAY", "4.0"))


def detect_kind(data: bytes) -> str:
    """'tar.gz' | 'tex.gz' | 'pdf' | 'unknown'"""
    if data[:4] == b"%PDF":
        return "pdf"
    if data[:2] == b"\x1f\x8b":
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz"):
                return "tar.gz"
        except tarfile.TarError:
            # stream-validate the gzip header + start of stream; decompressing
            # a byte prefix raises EOFError on perfectly valid large files
            # (codex review-3)
            try:
                with gzip.GzipFile(fileobj=io.BytesIO(data)) as g:
                    g.read(512)
            except OSError:
                return "unknown"
            return "tex.gz"
    return "unknown"


def record(con, arxiv_id: str, kind: str, version, path, sha, nbytes, status: str) -> None:
    with con:
        con.execute(
            "INSERT OR REPLACE INTO files (arxiv_id, kind, version, path, sha256, bytes, "
            "fetched_at, status) VALUES (?,?,?,?,?,?,?,?)",
            (arxiv_id, kind, version, path, sha, nbytes,
             dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), status))


def fetch_one(session, con, arxiv_id: str, version: int,
              v1_refill: bool = False) -> str:
    """Fetch e-print/{id}v{version}. In v1_refill mode the blob lands at a
    v1-suffixed path and is recorded ONLY in artifacts (version=1, channel
    'export-v1') — the files row (bulk/latest ledger) is left untouched."""
    url = EPRINT_URL.format(id=arxiv_id, v=version)
    for attempt in range(5):
        try:
            resp = session.get(url, timeout=180)
        except requests.RequestException as exc:
            time.sleep(10 * (attempt + 1))
            if attempt == 4:
                if not v1_refill:
                    record(con, arxiv_id, "src", version, None, None, None,
                           f"error:conn:{exc}")
                return "error"
            continue
        if resp.status_code in (429, 503):
            try:
                wait = int(resp.headers.get("Retry-After", "60"))
            except ValueError:
                wait = 60
            print(f"  {resp.status_code}, waiting {wait}s", flush=True)
            time.sleep(wait)
            continue
        if resp.status_code == 404:
            if not v1_refill:
                record(con, arxiv_id, "src", version, None, None, None, "error:404")
            return "404"
        if resp.status_code != 200:
            if not v1_refill:
                record(con, arxiv_id, "src", version, None, None, None,
                       f"error:http{resp.status_code}")
            return "error"
        data = resp.content
        kind = detect_kind(data)
        yymm = arxiv_id.split(".")[0]
        pdir = db.CORPUS_DIR / yymm / arxiv_id
        pdir.mkdir(parents=True, exist_ok=True)
        suffix = "_v1" if v1_refill else ""
        if kind == "pdf":
            path = pdir / f"paper{suffix}.pdf"
            file_kind, status = "pdf", "ok_pdf_only"
        elif kind in ("tar.gz", "tex.gz"):
            path = pdir / (f"src{suffix}.tar.gz" if kind == "tar.gz"
                           else f"src{suffix}.tex.gz")
            file_kind, status = "src", "ok"
        else:
            path = pdir / f"eprint{suffix}.unknown"
            file_kind, status = "src", "ok_unknown_format"
            if v1_refill:
                # review-6 P1-2: an HTTP-200 body that is not TeX/tar/PDF is
                # NOT a successful v1 acquisition — quarantine the bytes for
                # diagnosis, register no artifact, stay refill-eligible
                path.write_bytes(data)
                return "unknown-format"
        sha = hashlib.sha256(data).hexdigest()
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            # review-6 P1-1: never overwrite bytes an existing artifact row
            # may reference — divert differing content to a content-suffixed
            # path so every artifact row keeps identifying its own bytes
            exts = "".join(path.suffixes)          # ".tar.gz" / ".pdf" / ...
            stem = path.name[: -len(exts)] if exts else path.name
            path = path.with_name(f"{stem}.{sha[:12]}{exts}")
        path.write_bytes(data)
        rel = str(path.relative_to(db.PROJECT_ROOT))
        now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        with con:  # files + artifacts commit together — no artifactless
            # success window on crash (codex re-review F4)
            if not v1_refill:
                con.execute(
                    "INSERT OR REPLACE INTO files (arxiv_id, kind, version, path, "
                    "sha256, bytes, fetched_at, status) VALUES (?,?,?,?,?,?,?,?)",
                    (arxiv_id, file_kind, version, rel, sha, len(data), now, status))
            con.execute(
                "INSERT OR IGNORE INTO artifacts (arxiv_id, version, kind, "
                "requested_version, path, sha256, bytes, fetch_channel, fetched_at, format) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (arxiv_id, version, file_kind, version, rel, sha, len(data),
                 "export-v1" if v1_refill else "export", now, kind))
        return status
    if not v1_refill:
        record(con, arxiv_id, "src", version, None, None, None, "error:retries")
    return "error"


def log_refill_attempt(arxiv_id: str, status: str,
                       run: str | None = None) -> None:
    """Refill mode records successes in `artifacts` only, so failures would
    otherwise be invisible: a restart could not distinguish never-attempted
    from failed-repeatedly, and terminal 404s (withdrawn v1) from transient
    errors (review-4 P0-1). Append every terminal outcome to a JSONL ledger,
    scoped to the invocation's manifest run id (review-6: reconciliation must
    not credit an older invocation's outcomes to this run's targets)."""
    path = db.PROJECT_ROOT / "corpus" / "logs" / "v1refill_attempts.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps({
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "run": run, "arxiv_id": arxiv_id, "status": status}) + "\n")


def select_v1_refill(con, months: list[str],
                     flagged_first: str | None = None,
                     flagged_only: bool = False) -> list[tuple[str, int]]:
    """v1-estimand refill: every corpus paper with >=2 versions needs a
    version-pinned v1 blob (bulk chunks hold 'latest at re-roll time', which
    calibration showed is 12-23 months after announcement — see LEDGER).
    Selection is idempotent: papers that already have a v1 src/pdf artifact
    are skipped. Simple rule over cutoff heuristics: refetching a paper whose
    bulk blob happens to be v1 is a few thousand harmless extra fetches."""
    ids_file = Path(__file__).parent / "aws" / "math_ids.txt"
    corpus = {l.strip() for l in ids_file.open()} if ids_file.exists() else None
    prefixes = tuple(months)
    rows = con.execute(
        "SELECT v.arxiv_id FROM versions v "
        "WHERE substr(v.arxiv_id,1,4) IN (%s) "
        "GROUP BY v.arxiv_id HAVING COUNT(*) > 1" % ",".join("?" * len(prefixes)),
        prefixes).fetchall()
    have_v1 = {r["arxiv_id"] for r in con.execute(
        "SELECT DISTINCT arxiv_id FROM artifacts WHERE version = 1")}
    todo = [(r["arxiv_id"], 1) for r in rows
            if r["arxiv_id"] not in have_v1
            and (corpus is None or r["arxiv_id"] in corpus)]
    todo.sort()
    random.Random(42).shuffle(todo)  # partial progress = unbiased sample
    if flagged_first:
        # flag-scoped phase 1: scanner-flagged papers jump the queue (their
        # v1 text decides the preliminary numbers); each phase stays a
        # seeded-random sample of its stratum
        flagged = {r["arxiv_id"] for r in con.execute(
            "SELECT DISTINCT arxiv_id FROM scan_hits WHERE scan_run=? "
            "AND tier IN ('llm','generic') AND rule_class != 'known_fp'",
            (flagged_first,))}
        if flagged_only:
            # review-5 immediate action: the approved phase is a FINITE queue,
            # not a priority ordering — the unflagged tail needs its own
            # explicitly approved invocation (--include-unflagged-tail)
            todo = [t for t in todo if t[0] in flagged]
        else:
            todo = ([t for t in todo if t[0] in flagged]
                    + [t for t in todo if t[0] not in flagged])
    return todo


def select_todo(con, months: list[str], all_cats: bool = False) -> list[tuple[str, int]]:
    prefixes = tuple(months)
    cat_filter = "" if all_cats else "AND p.primary_category LIKE 'math%' "
    rows = con.execute(
        "SELECT p.arxiv_id, p.latest_version FROM papers p "
        "LEFT JOIN files f ON f.arxiv_id = p.arxiv_id AND f.kind IN ('src','pdf') "
        "  AND (f.status LIKE 'ok%' OR f.status = 'error:404') "
        "WHERE f.arxiv_id IS NULL " + cat_filter +
        "AND substr(p.arxiv_id, 1, 4) IN (%s)"
        % ",".join("?" * len(prefixes)), prefixes).fetchall()
    todo = [(r["arxiv_id"], r["latest_version"] or 1) for r in rows]
    todo.sort()
    random.Random(42).shuffle(todo)
    return todo


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", nargs="+", default=["2608", "2607"],
                    help="yymm arXiv id prefixes to fetch")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--all-cats", action="store_true",
                    help="include papers whose primary category is not math.*")
    ap.add_argument("--v1-refill", action="store_true",
                    help="fetch pinned v1 for every multi-version corpus paper "
                         "(v1 estimand); records artifacts only, never files")
    ap.add_argument("--flagged-first", default=None, metavar="SCAN_RUN",
                    help="v1-refill: fetch scanner-flagged papers before the rest")
    ap.add_argument("--flagged-only", action="store_true",
                    help="v1-refill: fetch ONLY the flagged papers of "
                         "--flagged-first and stop (approved finite phase)")
    ap.add_argument("--include-unflagged-tail", action="store_true",
                    help="v1-refill: explicitly authorize the ~56k unflagged "
                         "tail (owner decision 2026-08-11: requires prior "
                         "arXiv coordination — see DECISIONS.md)")
    args = ap.parse_args()

    if args.v1_refill:
        # exhaustive mode truth table (review-6): EVERY v1-refill invocation
        # must be exactly one of the two authorized modes — there is no
        # "unscoped" form
        if args.flagged_only and args.include_unflagged_tail:
            sys.exit("--flagged-only and --include-unflagged-tail are "
                     "mutually exclusive")
        if args.flagged_only and not args.flagged_first:
            sys.exit("--flagged-only needs --flagged-first SCAN_RUN to "
                     "define the flagged set")
        if not args.flagged_only and not args.include_unflagged_tail:
            sys.exit("v1-refill needs explicit authorization: "
                     "--flagged-only --flagged-first SCAN_RUN for the "
                     "approved finite phase, or --include-unflagged-tail "
                     "after arXiv coordination (DECISIONS.md 2026-08-11)")

    con = db.connect()
    session = requests.Session()
    session.trust_env = False  # fixed arXiv origin; no ambient proxies/.netrc
    session.headers["User-Agent"] = USER_AGENT

    if args.v1_refill:
        todo = select_v1_refill(con, args.months, args.flagged_first,
                                args.flagged_only)
    else:
        todo = select_todo(con, args.months, args.all_cats)
    if args.limit:
        todo = todo[: args.limit]
    print(f"{len(todo)} papers to fetch (months {args.months}"
          f"{', v1-refill' if args.v1_refill else ''}"
          f"{', FLAGGED-ONLY' if args.v1_refill and args.flagged_only else ''})",
          flush=True)
    refill_run = None
    if args.v1_refill:
        if args.flagged_first and not con.execute(
                "SELECT 1 FROM scan_runs WHERE run_id=? AND stage='tex'",
                (args.flagged_first,)).fetchone():
            sys.exit(f"--flagged-first {args.flagged_first!r} is not a known "
                     "full-text scan run")
        # exact target manifest WITH the member preimage (review-6: a hash
        # alone only proves equality when the list itself is retained)
        mdir = db.PROJECT_ROOT / "corpus" / "logs"
        mdir.mkdir(parents=True, exist_ok=True)
        ids = [t[0] for t in todo]
        ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        refill_run = "v1r-" + ts.replace(":", "").replace("-", "")[:15]
        manifest = {
            "run": refill_run, "ts": ts,
            "mode": "flagged-only" if args.flagged_only else "full",
            "flagged_scan_run": args.flagged_first, "months": args.months,
            "n_targets": len(ids), "delay_s": POLITE_DELAY, "limit": args.limit,
            "targets_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
            "targets": ids,
        }
        (mdir / f"v1refill_manifest_{refill_run}.json").write_text(
            json.dumps(manifest, indent=1))
    t0 = time.time()
    counts: dict[str, int] = {}
    for i, (arxiv_id, version) in enumerate(todo, 1):
        status = fetch_one(session, con, arxiv_id, version, args.v1_refill)
        if args.v1_refill:
            log_refill_attempt(arxiv_id, status, refill_run)
        counts[status] = counts.get(status, 0) + 1
        if i % 25 == 0:
            rate = i / (time.time() - t0)
            eta_h = (len(todo) - i) / rate / 3600 if rate else 0
            print(f"{i}/{len(todo)} ({counts}) eta {eta_h:.1f}h", flush=True)
        time.sleep(POLITE_DELAY)
    print(f"done: {counts}", flush=True)
    if args.v1_refill and not args.limit:
        # terminal reconciliation: every manifest target must end with a v1
        # artifact or a ledgered terminal 404 — anything else is unresolved
        # and the exit code says so (review-5)
        have_v1 = {r[0] for r in con.execute(
            "SELECT DISTINCT arxiv_id FROM artifacts WHERE version = 1")}
        seen_404 = set()
        ledger = db.PROJECT_ROOT / "corpus" / "logs" / "v1refill_attempts.jsonl"
        if ledger.exists():
            for line in ledger.read_text().splitlines():
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # only THIS invocation's terminal 404s count (review-6)
                if rec.get("status") == "404" and rec.get("run") == refill_run:
                    seen_404.add(rec.get("arxiv_id"))
        unresolved = [i for i, _ in todo if i not in have_v1 and i not in seen_404]
        if unresolved:
            print(f"UNRESOLVED: {len(unresolved)} targets have neither a v1 "
                  f"artifact nor a terminal 404 (first: {unresolved[:5]}) — "
                  "rerun to retry", flush=True)
            return 1
        print("reconciliation clean: every target has a terminal outcome",
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
