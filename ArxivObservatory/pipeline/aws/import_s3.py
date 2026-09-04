"""Import the S3-filtered monthly tars into the artifact ledger.

Runs LOCALLY after sync_home.sh has rsynced corpus/s3/math_<yymm>.tar from
the EC2 filter instance. Before any scan touches the tars (LEDGER: AWS
importer), this:

1. walks every member of every monthly tar, hashing bytes (sha256 ledger)
   and detecting format (tar.gz / tex.gz / pdf / unknown);
2. reconciles in BOTH directions:
   - every ID in pipeline/aws/math_ids.txt within the covered months must
     appear in exactly one tar member (missing -> reported);
   - every member ID must be in math_ids.txt (extras -> reported), and is
     cross-checked against harvested `papers`;
   - duplicate members (crash/retry artifacts of the filter) are reported;
3. with --register, writes append-only `artifacts` rows (fetch_channel
   's3-bulk', version NULL — bulk chunks hold the latest version at chunk
   creation, an approximately fixed-lag snapshot) and INSERT OR IGNOREs
   `files` rows so scan job selection sees the corpus. Existing rows (e.g.
   version-pinned export fetches for 2605-2608) are never overwritten.

Member paths are recorded as 'corpus/s3/math_<yymm>.tar::<member>' —
pipeline.scan reads these in place via a per-worker tar handle cache.

Exit is nonzero on any missing/extra/duplicate/tar-error so this gates the
scan step. Usage:

    python3 -m pipeline.aws.import_s3                # reconcile only (dry)
    python3 -m pipeline.aws.import_s3 --register
    python3 -m pipeline.aws.import_s3 --months 2308 2309 --out reports/s3_import.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tarfile
from pathlib import Path

from .. import db, runs

S3_DIR = db.CORPUS_DIR / "s3"
IDS_FILE = Path(__file__).parent / "math_ids.txt"
TAR_RE = re.compile(r"math_(\d{4})\.tar$")
ID_RE = re.compile(r"^\d{4}\.\d{4,5}$")


def detect_format(data: bytes) -> str:
    if data[:4] == b"%PDF":
        return "pdf"
    if data[:2] == b"\x1f\x8b":
        return "gz"          # gzipped tar or single tex file; scan handles both
    return "unknown"


def walk_tar(tar_path: Path) -> tuple[dict[str, dict], list[str], str | None]:
    """Returns ({arxiv_id: member info}, duplicate ids, tar error)."""
    members: dict[str, dict] = {}
    dupes: list[str] = []
    try:
        with tarfile.open(tar_path, "r") as tf:
            for m in tf:
                if not m.isfile():
                    continue
                stem = Path(m.name).name
                stem = stem[: stem.rfind(".")] if "." in stem else stem
                if not ID_RE.match(stem):
                    dupes.append(f"non-id-member:{m.name}")
                    continue
                f = tf.extractfile(m)
                if f is None:
                    continue
                data = f.read()
                info = {"member": m.name, "sha256": hashlib.sha256(data).hexdigest(),
                        "bytes": len(data), "format": detect_format(data)}
                if stem in members:
                    if info["sha256"] == members[stem]["sha256"]:
                        dupes.append(f"dup-identical:{stem}")
                    else:
                        dupes.append(f"dup-DIFFERING:{stem}")
                    continue
                members[stem] = info
    except (tarfile.TarError, EOFError, OSError) as exc:
        return members, dupes, f"{type(exc).__name__}: {exc}"
    return members, dupes, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--register", action="store_true",
                    help="write artifacts + files rows (default: reconcile only); "
                         "refused while reconciliation problems exist")
    ap.add_argument("--force", action="store_true",
                    help="register despite reconciliation problems (understood gaps)")
    ap.add_argument("--months", nargs="*", default=None,
                    help="yymm subset (default: every math_*.tar present)")
    ap.add_argument("--out", default="reports/s3_import.json")
    args = ap.parse_args()

    tars = sorted(S3_DIR.glob("math_*.tar"))
    if args.months:
        tars = [t for t in tars if TAR_RE.search(t.name).group(1) in args.months]
    if not tars:
        sys.exit(f"no math_*.tar files under {S3_DIR}")
    months = [TAR_RE.search(t.name).group(1) for t in tars]
    print(f"importing {len(tars)} monthly tars: {', '.join(months)}", flush=True)

    target_ids = {line.strip() for line in IDS_FILE.open() if line.strip()}
    ledger: dict[str, dict] = {}
    problems: dict[str, list[str]] = {"tar_errors": [], "duplicates": [],
                                      "extras": [], "unknown_format": [],
                                      "missing": [], "not_in_papers": []}
    tar_shas: dict[str, str] = {}
    for tar_path in tars:
        yymm = TAR_RE.search(tar_path.name).group(1)
        rel = str(tar_path.relative_to(db.PROJECT_ROOT))
        h = hashlib.sha256()
        with tar_path.open("rb") as f:
            for blk in iter(lambda: f.read(1 << 22), b""):
                h.update(blk)
        tar_shas[tar_path.name] = h.hexdigest()
        members, dupes, err = walk_tar(tar_path)
        if err:
            problems["tar_errors"].append(f"{tar_path.name}: {err}")
        problems["duplicates"] += [f"{tar_path.name}:{d}" for d in dupes]
        for pid, info in members.items():
            if not pid.startswith(yymm):
                problems["extras"].append(f"{tar_path.name}: {pid} (wrong month)")
                continue
            if pid not in target_ids:
                problems["extras"].append(f"{tar_path.name}: {pid} (not in math_ids)")
                continue
            if info["format"] == "unknown":
                # never let unrecognized bytes become a successful source (F3/F8)
                problems["unknown_format"].append(f"{tar_path.name}: {pid}")
                continue
            if pid in ledger:
                problems["duplicates"].append(f"across-tars:{pid}")
                continue
            ledger[pid] = {**info, "path": f"{rel}::{info['member']}"}
        print(f"  {tar_path.name}: {len(members)} members "
              f"({len(dupes)} dupes)", flush=True)

    covered = {pid for pid in target_ids if pid[:4] in months}
    problems["missing"] = sorted(covered - set(ledger))

    con = db.connect()
    harvested = {r["arxiv_id"] for r in con.execute(
        "SELECT arxiv_id FROM papers WHERE substr(arxiv_id,1,4) IN (%s)"
        % ",".join("?" * len(months)), months)}
    problems["not_in_papers"] = sorted(set(ledger) - harvested)

    n_problems = sum(len(v) for v in problems.values())
    if args.register:
        # registration is gated: a partial/inconsistent ledger never enters the
        # DB (F8); --force overrides for consciously accepted gaps
        if n_problems and not args.force:
            print(f"REFUSING to register: {n_problems} reconciliation problems "
                  "(rerun with --force only if the gaps are understood)", flush=True)
        else:
            now = runs.utcnow()
            n_new = 0
            registered = True
            with con:
                for pid, info in ledger.items():
                    kind = "pdf" if info["format"] == "pdf" else "src"
                    # SELECT-guard: UNIQUE with NULL version does not dedupe (F8)
                    exists = con.execute(
                        "SELECT 1 FROM artifacts WHERE arxiv_id=? AND kind=? "
                        "AND sha256=? AND fetch_channel='s3-bulk'",
                        (pid, kind, info["sha256"])).fetchone()
                    if exists:
                        continue
                    con.execute(
                        "INSERT INTO artifacts (arxiv_id, version, kind, "
                        "requested_version, path, sha256, bytes, fetch_channel, "
                        "fetched_at, format) VALUES (?,NULL,?,NULL,?,?,?,'s3-bulk',?,?)",
                        (pid, kind, info["path"], info["sha256"], info["bytes"], now,
                         info["format"]))
                    cur = con.execute(
                        "INSERT OR IGNORE INTO files (arxiv_id, kind, version, path, "
                        "sha256, bytes, fetched_at, status) VALUES (?,?,NULL,?,?,?,?,?)",
                        (pid, kind, info["path"], info["sha256"], info["bytes"], now,
                         "ok" if kind == "src" else "ok_pdf_only"))
                    if not cur.rowcount:
                        # a prior FAILED fetch row (e.g. error:404) must not
                        # shadow a good bulk source (codex review-3); existing
                        # ok rows (version-pinned export fetches) are kept
                        con.execute(
                            "UPDATE files SET version=NULL, path=?, sha256=?, "
                            "bytes=?, fetched_at=?, status=? WHERE arxiv_id=? "
                            "AND kind=? AND status NOT LIKE 'ok%'",
                            (info["path"], info["sha256"], info["bytes"], now,
                             "ok" if kind == "src" else "ok_pdf_only", pid, kind))
                    n_new += 1
            print(f"registered {n_new} new papers into artifacts/files "
                  f"({len(ledger) - n_new} already present)", flush=True)

    did_register = bool(args.register and (not n_problems or args.force))
    report = {
        "created_at": runs.utcnow(), "months": months, "tar_sha256": tar_shas,
        "target_ids_in_window": len(covered), "members_ledgered": len(ledger),
        "registered": did_register,  # what actually happened, not the flag
        "problems": {k: {"count": len(v), "sample": v[:50]}
                     for k, v in problems.items()},
    }
    out = Path(args.out)
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"ledger: {len(ledger)}/{len(covered)} target papers found; "
          f"{n_problems} problems -> {out}", flush=True)
    for k, v in problems.items():
        if v:
            print(f"  {k}: {len(v)} (first: {v[0]})", flush=True)
    return 0 if n_problems == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
