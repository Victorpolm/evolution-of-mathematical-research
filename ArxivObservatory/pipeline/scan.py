"""Full-text keyword scan over cached e-print archives.

Archives are read in memory (tarfile/gzip on bytes) — nothing is extracted to
disk, which keeps the corpus compact and avoids WSL small-file I/O. TeX
comments are stripped before matching (source-privacy default from
TECH_NOTES §1). Ancillary member names that look like chat logs are recorded
as hits of term 'ancillary-file' (evidence-type artifact).

Immutable-run discipline (LB-01/02): every invocation creates a scan_runs
manifest and writes one scan_items row per paper — including clean no-hit
scans, errors, and skipped members — so "scanned" is a provable property.
Run ids are never reused; rescans create new runs (optionally marking the old
one superseded) and never delete hits.

Modes:
    python3 -m pipeline.scan --corpus                    # everything in files table
    python3 -m pipeline.scan --corpus --supersedes tex-v1
    python3 -m pipeline.scan --pilot                     # pilot papers/ fixture
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import re
import subprocess
import sys
import tarfile
from multiprocessing import Pool
from pathlib import Path

from . import db, lexicon, runs

SNIPPET_RADIUS = 700
TEX_EXTS = {".tex", ".ltx", ".txt"}
MAX_MEMBER_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 200 * 1024 * 1024   # per-archive expanded-byte budget
ANCILLARY_RE = re.compile(
    r".*(?:chat[-_ ]?(?:gpt|log|bot)|gpt[-_0-9]|claude|gemini|deepseek|_llm|llm[-_]|"
    r"prompt|transcript|conversation|ai[-_](?:log|chat|session|dialog)).*",
    re.IGNORECASE)
COMMENT_RE = re.compile(r"(?<!\\)%.*")
URL_ARG_RE = re.compile(r"(\\(?:url|href)\{[^}]*\})")
COMMENT_ENV_RE = re.compile(r"\\begin\{comment\}.*?(?:\\end\{comment\}|\Z)", re.S)
IFFALSE_RE = re.compile(r"\\iffalse\b.*?(?:\\fi\b|\Z)", re.S)
END_DOC_RE = re.compile(r"(\\end\{document\}).*", re.S)


def strip_tex_comments(text: str) -> str:
    r"""Remove non-rendered source: %-comments, comment environments,
    \iffalse blocks, and anything after \end{document} (privacy default,
    TECH_NOTES §1 — non-rendered residue is not a disclosure signal)."""
    text = COMMENT_ENV_RE.sub("", text)
    text = IFFALSE_RE.sub("", text)
    text = END_DOC_RE.sub(r"\1", text)
    # protect % inside \url{}/\href{} args (chat-log links are evidence)
    protected = URL_ARG_RE.sub(lambda m: m.group(1).replace("%", "\x00"), text)
    return COMMENT_RE.sub("", protected).replace("\x00", "%")


def decode(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def scan_text(text: str, member: str, kind: str) -> list[dict]:
    hits = []
    if kind == "tex":
        text = lexicon.normalize(text)
    for h in lexicon.find_hits(text):
        lo = max(0, h["offset"] - SNIPPET_RADIUS)
        hi = min(len(text), h["offset"] + SNIPPET_RADIUS)
        hits.append({**h, "member": member, "kind": kind,
                     "context": text[lo:hi]})
    return hits


def scan_archive_bytes(data: bytes) -> tuple[list[dict], list[str]]:
    """Scan a raw e-print blob. Returns (hits, notes); notes record members
    that were skipped or truncated so scan_items can prove coverage."""
    hits: list[dict] = []
    notes: list[str] = []
    if data[:2] == b"\x1f\x8b" or data[257:262] == b"ustar":
        try:
            tf = tarfile.open(fileobj=io.BytesIO(data), mode="r:*")
        except tarfile.TarError:
            # stream-decompress with a hard cap: gzip.decompress() would
            # materialize a decompression bomb before any budget check
            # (review-4 §scanner)
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as g:
                raw = g.read(MAX_TOTAL_BYTES + 1)
            if len(raw) > MAX_TOTAL_BYTES:  # budget applies to single-gz too (F3)
                notes.append(f"skipped-budget:single-gz:>{MAX_TOTAL_BYTES}")
                return hits, notes
            text = decode(raw)
            if "\\documentclass" not in text and "\\begin" not in text:
                notes.append("unknown-format:single-gz")
                return hits, notes
            return scan_text(strip_tex_comments(text), "main.tex", "tex"), notes
        total = 0
        with tf:
            for m in tf.getmembers():
                if not m.isfile():
                    continue
                if ANCILLARY_RE.match(m.name) and not m.name.lower().endswith(tuple(TEX_EXTS)):
                    hits.append({"term": "ancillary-file", "tier": "llm", "offset": 0,
                                 "matched": m.name, "rule_class": "artifact",
                                 "member": m.name, "kind": "tex",
                                 "context": f"[ancillary member: {m.name}, {m.size} bytes]"})
                    continue
                suffix = Path(m.name).suffix.lower()
                if m.size > MAX_MEMBER_BYTES:
                    if suffix in TEX_EXTS:
                        notes.append(f"skipped-large:{m.name}:{m.size}")
                    continue
                if total + m.size > MAX_TOTAL_BYTES:
                    notes.append(f"skipped-budget:{m.name}:{m.size}")
                    continue
                f = tf.extractfile(m)
                if f is None:
                    continue
                if suffix in TEX_EXTS:
                    data_m = f.read()
                elif suffix in {".bbl", ".def", ".inc", ".txi", ".ldf", ""} and m.size < 2_000_000:
                    # content-sniff TeX-like members with odd extensions
                    head = f.read(512)
                    if not any(t in head for t in (b"\\documentclass", b"\\begin",
                                                   b"\\section", b"\\input", b"\\thanks")):
                        continue
                    data_m = head + f.read()
                else:
                    continue
                total += len(data_m)
                text = strip_tex_comments(decode(data_m))
                hits.extend(scan_text(text, m.name, "tex"))
        return hits, notes
    # uncompressed single file (rare): treat as tex if it looks like text
    text = decode(data)
    if "\\documentclass" in text or "\\begin" in text:
        return scan_text(strip_tex_comments(text), "main.tex", "tex"), notes
    notes.append("unknown-format:not-tex")  # never a silent clean negative (F3)
    return hits, notes


def pdf_to_text(pdf_path: Path, timeout: int = 120) -> str:
    # cache is bound to the PDF bytes that produced it — a bare .txt sibling
    # could belong to an older PDF at the same path (review-6 P0-6)
    sha = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    cache = pdf_path.with_suffix(f".{sha[:12]}.txt")
    if cache.exists() and cache.stat().st_size > 0:
        return cache.read_text(errors="replace")
    proc = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf_path), str(cache)],
        capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0 or not cache.exists():
        return ""
    return cache.read_text(errors="replace")


# per-worker cache of open monthly tars (S3 bulk corpus; paths 'tar::member')
_TAR_CACHE: dict[str, tarfile.TarFile] = {}


def read_blob(path: str) -> bytes:
    """Read a corpus blob: plain file or member inside a monthly tar."""
    if "::" in path:
        tar_rel, member = path.split("::", 1)
        tf = _TAR_CACHE.get(tar_rel)
        if tf is None:
            tf = tarfile.open(db.PROJECT_ROOT / tar_rel, "r")
            _TAR_CACHE[tar_rel] = tf
        f = tf.extractfile(member)
        if f is None:
            raise FileNotFoundError(f"member {member} not in {tar_rel}")
        return f.read()
    return (db.PROJECT_ROOT / path).read_bytes()


def item_status(err: str | None, notes: list[str]) -> str:
    """Terminal scan_items status. Anything that prevented a complete read of
    potentially rendered text must NOT be 'ok' — 'ok' is the denominator
    (codex re-review F3)."""
    if err:
        return f"error:{err.split(':', 1)[0]}"
    if any(n.startswith("skipped:pdf-tar-member") for n in notes):
        return "skipped:pdf-tar-member"
    if any(n.startswith("unknown-format") for n in notes):
        return "error:UnknownFormat"
    if any(n.startswith(("skipped-large:", "skipped-budget:")) for n in notes):
        return "incomplete:members-skipped"
    return "ok"


def scan_one(job: tuple[str, int | None, str, str, str | None]
             ) -> tuple[str, list[dict], list[str], str | None, str | None]:
    """Returns (arxiv_id, hits, notes, err, sha256-of-bytes-actually-read)."""
    arxiv_id, version, path, kind, _sha = job
    try:
        if kind == "pdf":
            if "::" in path:
                # pdf-only member inside a bulk tar: visible stratum, scanned later
                return arxiv_id, [], ["skipped:pdf-tar-member"], None, None
            p = db.PROJECT_ROOT / path
            read_sha = hashlib.sha256(p.read_bytes()).hexdigest()
            text = pdf_to_text(p)
            if not text:
                return arxiv_id, [], [], "PdfTextEmpty: extraction produced no text", read_sha
            return arxiv_id, scan_text(text, p.name, "pdf_text"), [], None, read_sha
        blob = read_blob(path)
        read_sha = hashlib.sha256(blob).hexdigest()
        hits, notes = scan_archive_bytes(blob)
        return arxiv_id, hits, notes, None, read_sha
    except Exception as exc:  # noqa: BLE001 - record, don't crash the pool
        return arxiv_id, [], [], f"{type(exc).__name__}: {exc}", None


def run_scan(jobs: list[tuple[str, int | None, str, str, str | None]],
             run_id: str, workers: int, supersedes: str | None = None,
             basis: dict[str, str] | None = None) -> int:
    con = db.connect()
    params = {"workers": workers, "n_jobs": len(jobs),
              "snippet_radius": SNIPPET_RADIUS,
              "max_member_bytes": MAX_MEMBER_BYTES,
              "max_total_bytes": MAX_TOTAL_BYTES}
    runs.start_scan_run(con, run_id, "tex", lexicon.LEXICON_VERSION,
                        db.code_commit(), params)
    basis = basis or {}
    meta = {j[0]: (j[1], j[4]) for j in jobs}  # arxiv_id -> (version, ledger sha256)
    n_hits = n_err = n_inc = 0
    with Pool(workers) as pool:
        for i, (arxiv_id, hits, notes, err, read_sha) in enumerate(
                pool.imap_unordered(scan_one, jobs, chunksize=8), 1):
            version, ledger_sha = meta[arxiv_id]
            # the recorded hash is the hash of the bytes actually scanned;
            # a ledger mismatch is a hard error, not a silent scan (F4)
            if not err and ledger_sha and read_sha and ledger_sha != read_sha:
                err = f"HashMismatch: ledger {ledger_sha[:12]} != read {read_sha[:12]}"
                hits = []
            status = item_status(err, notes)
            # count by terminal item status, not exception origin: unknown
            # formats and skipped members must also demote the run (P0-2)
            if status.startswith("error"):
                n_err += 1
                print(f"  ERROR {arxiv_id}: {err or status}", flush=True)
            elif status.startswith("incomplete"):
                n_inc += 1
            with con:
                if hits:
                    con.executemany(
                        "INSERT INTO scan_hits (arxiv_id, version, source_kind, file_member, "
                        "term, tier, offset, context, rule_class, scan_run) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?)",
                        [(arxiv_id, version, h["kind"], h["member"], h["term"],
                          h["tier"], h["offset"], h["context"], h["rule_class"], run_id)
                         for h in hits])
                    n_hits += len(hits)
                con.execute(
                    "INSERT INTO scan_items (run_id, arxiv_id, version, artifact_sha256, "
                    "status, n_hits, detail, scanned_at, version_basis) "
                    "VALUES (?,?,?,?,?,?,?,?,?)",
                    (run_id, arxiv_id, version, read_sha, status, len(hits),
                     err or ("; ".join(notes) if notes else None), runs.utcnow(),
                     basis.get(arxiv_id)))
            if i % 250 == 0:
                print(f"{i}/{len(jobs)} papers scanned, {n_hits} hits", flush=True)
    # 'complete' = every item ok or in a declared excluded stratum
    # (pdf-tar-member); any error or incomplete item makes the run 'partial'
    status = "complete" if n_err == 0 and n_inc == 0 else "partial"
    runs.finish_scan_run(con, run_id, status, len(jobs), n_hits, n_err + n_inc,
                         supersedes=supersedes)
    print(f"done: {len(jobs)} papers, {n_hits} hits, {n_err} errors, "
          f"{n_inc} incomplete ({run_id}, {status})", flush=True)
    return 0 if status == "complete" else 1


def corpus_jobs(con, months: list[str] | None
                ) -> list[tuple[str, int | None, str, str, str | None]]:
    q = ("SELECT arxiv_id, version, path, kind, status, sha256 FROM files "
         "WHERE status LIKE 'ok%' AND path IS NOT NULL")
    rows = con.execute(q).fetchall()
    by_paper: dict[str, tuple] = {}
    for r in rows:
        if months and r["arxiv_id"].split(".")[0] not in months:
            continue
        job = (r["arxiv_id"], r["version"], r["path"],
               "pdf" if r["kind"] == "pdf" else "src", r["sha256"])
        # one job per paper: prefer source over pdf-only
        if r["arxiv_id"] not in by_paper or job[3] == "src":
            by_paper[r["arxiv_id"]] = job
    return list(by_paper.values())


def v1_artifact_jobs(con, months: list[str] | None, flagged_run: str | None = None
                     ) -> list[tuple[str, int | None, str, str, str | None]]:
    """Version-pinned v1 scan jobs from the immutable artifacts ledger.

    review-4 P0-1: `files` is the mutable latest/bulk ledger and never sees
    v1-refill blobs, so `corpus_jobs` cannot feed a v1-estimand scan. Two
    provably-v1 sources are combined here:
      - explicit version=1 src/pdf artifacts (channel export-v1 refill, or any
        channel that recorded version 1), and
      - artifacts of papers with exactly ONE known version (metadata-certain:
        the re-rolled bulk 'latest' of a single-version paper is v1; papers
        that gained a v2 later are multi-version and take the explicit path).
    One job per paper. Ranking is source-first, then explicitness: src beats
    pdf even when the pdf is explicit-v1, because gcs-pdf v1 artifacts exist
    only where a render check already ran — choosing them would condition the
    input channel on a prior positive outcome (review-5 P0-8). Ties keep the
    lowest artifact id (deterministic). `--flagged SCAN_RUN` restricts to that
    run's scanner-flagged papers (an acquisition/calibration subset — NEVER a
    prevalence denominator).

    Returns (jobs, basis): basis maps arxiv_id -> 'explicit-v1' |
    'inferred-single-version', recorded on every scan_items row so the two
    v1 provenance strata stay distinct (DECISIONS.md amendment 2026-08-11)."""
    jobs: dict[str, tuple] = {}

    def add(arxiv_id, path, kind, sha, art_id, explicit: bool):
        rank = (kind != "pdf", explicit)  # src first, then explicitness
        cur = jobs.get(arxiv_id)
        if cur is None or rank > cur[0]:
            jobs[arxiv_id] = (rank, art_id,
                              (arxiv_id, 1, path, "pdf" if kind == "pdf" else "src",
                               sha), explicit)

    for r in con.execute(
            "SELECT id, arxiv_id, path, kind, sha256 FROM artifacts "
            "WHERE version = 1 AND kind IN ('src','pdf') ORDER BY id"):
        add(r["arxiv_id"], r["path"], r["kind"], r["sha256"], r["id"], True)
    single = {r[0] for r in con.execute(
        "SELECT arxiv_id FROM versions GROUP BY arxiv_id HAVING COUNT(*) = 1")}
    for r in con.execute(
            "SELECT id, arxiv_id, path, kind, sha256 FROM artifacts "
            "WHERE version IS NULL AND kind IN ('src','pdf') ORDER BY id"):
        if r["arxiv_id"] in single:
            add(r["arxiv_id"], r["path"], r["kind"], r["sha256"], r["id"], False)

    picked = jobs
    if months:
        picked = {p: v for p, v in picked.items() if p.split(".")[0] in months}
    if flagged_run:
        flagged = {r["arxiv_id"] for r in con.execute(
            "SELECT DISTINCT arxiv_id FROM scan_hits WHERE scan_run=? "
            "AND tier IN ('llm','generic') AND rule_class != 'known_fp'",
            (flagged_run,))}
        picked = {p: v for p, v in picked.items() if p in flagged}
    out = [v[2] for v in picked.values()]
    basis = {p: ("explicit-v1" if v[3] else "inferred-single-version")
             for p, v in picked.items()}
    return out, basis


def write_v1_selection_manifest(run_id: str, jobs, basis: dict[str, str],
                                months, flagged_run) -> None:
    """Hashed record of exactly what a v1 scan selected and why (review-5
    P0-8: the run ledger alone cannot prove the selection)."""
    import json
    mdir = db.CORPUS_DIR / "logs" / "scan"
    mdir.mkdir(parents=True, exist_ok=True)
    lines = sorted(f"{j[0]}:{j[1]}:{basis[j[0]]}:{j[4]}:{j[2]}" for j in jobs)
    manifest = {
        "run_id": run_id, "mode": "v1-corpus", "months": months,
        "flagged_scan_run": flagged_run,
        "n_jobs": len(jobs),
        "basis_counts": {b: sum(1 for x in basis.values() if x == b)
                         for b in sorted(set(basis.values()))},
        "selection_sha256": hashlib.sha256("\n".join(lines).encode()).hexdigest(),
        "created_at": runs.utcnow(),
    }
    (mdir / f"{run_id}.selection.json").write_text(json.dumps(manifest, indent=1))
    print(f"selection manifest: {mdir / (run_id + '.selection.json')} "
          f"({manifest['basis_counts']})", flush=True)


def pilot_jobs() -> list[tuple[str, int | None, str, str, str | None]]:
    jobs = []
    for src in sorted((db.PROJECT_ROOT / "papers").glob("*/*.source")):
        arxiv_id = src.parent.name
        jobs.append((arxiv_id, None, str(src.relative_to(db.PROJECT_ROOT)), "src", None))
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", action="store_true")
    ap.add_argument("--v1-corpus", action="store_true",
                    help="scan version-pinned v1 artifacts (explicit v1 blobs "
                         "+ single-version papers' bulk blobs) instead of the "
                         "mutable files ledger")
    ap.add_argument("--flagged", default=None, metavar="SCAN_RUN",
                    help="--v1-corpus: restrict to papers flagged in SCAN_RUN")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--months", nargs="*", default=None)
    ap.add_argument("--run", default=None,
                    help="explicit run id (must be unused); default: autogenerated")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--supersedes", default=None,
                    help="mark this older run id superseded by the new run")
    args = ap.parse_args()
    if args.pilot:
        run_id = args.run or runs.new_run_id("pilot-tex")
        return run_scan(pilot_jobs(), run_id, args.workers, args.supersedes)
    if args.v1_corpus:
        con = db.connect()
        run_id = args.run or runs.new_run_id("texv1")
        jobs, basis = v1_artifact_jobs(con, args.months, args.flagged)
        write_v1_selection_manifest(run_id, jobs, basis, args.months,
                                    args.flagged)
        return run_scan(jobs, run_id, args.workers, args.supersedes,
                        basis=basis)
    if args.corpus:
        con = db.connect()
        run_id = args.run or runs.new_run_id("tex")
        return run_scan(corpus_jobs(con, args.months), run_id, args.workers,
                        args.supersedes)
    ap.error("need --corpus, --v1-corpus, or --pilot")
    return 2


if __name__ == "__main__":
    sys.exit(main())
