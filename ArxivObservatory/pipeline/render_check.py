"""Render-truth check: evidence quotes must occur in the arXiv-compiled PDF.

Implements DESIGN_PLATFORM §8 (layer 3). Comment-stripping regexes are
brittle; the oracle for "does this text render?" is arXiv's own compiled,
version-pinned PDF — no TeX execution needed. Every author_use evidence quote
from a classification run is matched (whitespace/hyphenation/ligature
normalized, exact then fuzzy) against pdftotext of that PDF.

Outcomes per item (classification_items.render_status):
    rendered               — quote found exactly (or dehyphenated) in the PDF
    rendered_fuzzy         — fuzzy match ≥ threshold; review-queue material,
                             NOT render certification (review-4 P0-6) — the
                             --require-rendered gate excludes it
    non_rendered_evidence  — PDF text obtained, quote absent (excluded from
                             headline counts; ethically gated residual bucket)
    quote_too_short        — quote below the discrimination minimum; never
                             certified either way (excluded by the gate)
    unknown_version        — artifact version unknown (bulk snapshot); a
                             version-pinned check is impossible
    no_pdf                 — 404 on every source for the pinned version
    pdf_error              — transient download/extraction failure (retryable)

Every check appends a render_checks row (append-only audit trail); the status
column on the item is the only thing updated.

PDF sources, in order: existing corpus artifact -> GCS mirror
gs://arxiv-dataset (free, version-pinned, no credentials) -> polite
export.arxiv.org fallback.

Usage:
    python3 -m pipeline.render_check --run cls-20260810T... [--limit 50]
    python3 -m pipeline.render_check --run cls-... --polarity author_use non_use_statement
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

from . import db, runs

GCS_URL = "https://storage.googleapis.com/arxiv-dataset/arxiv/arxiv/pdf/{yymm}/{id}v{v}.pdf"
EXPORT_URL = "https://export.arxiv.org/pdf/{id}v{v}"
USER_AGENT = "ArxivObservatory/0.1 (research pilot; contact: jo314schmitt@gmail.com)"
GCS_DELAY = 0.5
EXPORT_DELAY = 4.0
FUZZY_THRESHOLD = 0.80
PDF_TIMEOUT = 120

LIGATURES = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl",
             "\ufb03": "ffi", "\ufb04": "ffl", "\u00ad": ""}
# commands whose argument does NOT render (a \label{ChatGPT} must never make
# source-only evidence look rendered — codex re-review F9)
KILL_ARG_RE = re.compile(
    r"\\(?:label|ref|eqref|pageref|autoref|[cC]ref|cite[a-z]*|url|input|include|"
    r"includegraphics|bibliography(?:style)?)\*?\s*(?:\[[^\]]*\])?\{[^{}]*\}")
HREF_RE = re.compile(r"\\href\s*\{[^{}]*\}\s*\{([^{}]*)\}")  # only 2nd arg renders
TEX_CMD_ARG_RE = re.compile(r"\\[a-zA-Z@]+\s*\{([^{}]*)\}")
TEX_CMD_RE = re.compile(r"\\[a-zA-Z@]+\s*")
MIN_QUOTE_WORDS = 3
MIN_QUOTE_CHARS = 15


def detex_quote(quote: str) -> str:
    """Light de-TeX so a source-derived quote can match rendered text:
    non-rendering command args dropped, \\href keeps its text arg,
    \\emph{X} -> X, bare commands dropped, math/grouping chars removed."""
    quote = KILL_ARG_RE.sub(" ", quote)
    quote = HREF_RE.sub(r"\1", quote)
    prev = None
    while prev != quote:
        prev = quote
        quote = TEX_CMD_ARG_RE.sub(r"\1", quote)
    quote = TEX_CMD_RE.sub(" ", quote)
    return quote.translate(str.maketrans({"{": "", "}": "", "$": "", "~": " "}))


def normalize(text: str) -> str:
    """Shared normalization for quote and PDF text before matching."""
    for lig, plain in LIGATURES.items():
        text = text.replace(lig, plain)
    text = text.replace("-\n", "")            # line-break hyphenation
    text = re.sub(r"[\u2010-\u2015]", "-", text)   # dash family
    text = re.sub(r"[\u2018\u2019`]", "'", text)
    text = re.sub(r"[\u201c\u201d]|''|``", '"', text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _window_score(q: str, window: str) -> float:
    """Coverage of q by matching blocks, penalized by the stretch of the
    matched span — insertions inside the match reduce the score (F9)."""
    sm = difflib.SequenceMatcher(None, q, window, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size > 0]
    if not blocks:
        return 0.0
    covered = sum(b.size for b in blocks)
    span = (blocks[-1].b + blocks[-1].size) - blocks[0].b
    return covered / max(len(q), span)


def match_quote(quote: str, pdf_text: str) -> tuple[bool, str, float]:
    """(matched, method, score). Exact normalized substring first (also
    hyphen-insensitive, since PDF line-break hyphenation is lossy); else every
    occurrence of each 3-word anchor shingle is fuzzy-compared locally.
    Quotes too short to be discriminating are never certified (F9)."""
    q = normalize(detex_quote(quote))
    t = normalize(pdf_text)
    if not q:
        return False, "no-text", 0.0
    if len(q) < MIN_QUOTE_CHARS or len(q.split()) < MIN_QUOTE_WORDS:
        return False, "quote-too-short", 0.0
    if q in t:
        return True, "exact", 1.0
    if q.replace("-", "") in t.replace("-", ""):
        return True, "exact-dehyphen", 1.0
    words = q.split()
    best = 0.0
    for i in range(max(1, len(words) - 2)):
        anchor = " ".join(words[i:i + 3])
        pos = t.find(anchor)
        n_seen = 0
        while pos != -1 and n_seen < 20:  # every occurrence, not just the first
            lo = max(0, pos - len(q) - 100)
            hi = min(len(t), pos + len(q) + 100)
            best = max(best, _window_score(q, t[lo:hi]))
            if best >= FUZZY_THRESHOLD:
                return True, "fuzzy", round(best, 3)
            pos = t.find(anchor, pos + 1)
            n_seen += 1
    if best > 0:
        return False, "fuzzy", round(best, 3)
    return False, "anchor-miss", 0.0


def pdf_path_for(arxiv_id: str, version: int) -> Path:
    yymm = arxiv_id.split(".")[0]
    return db.CORPUS_DIR / "pdf" / yymm / f"{arxiv_id}v{version}.pdf"


def obtain_pdf(con, session: requests.Session, arxiv_id: str, version: int
               ) -> tuple[Path | None, str, str | None]:
    """Returns (path, source, error). Cached fetches record sha256."""
    # 1. corpus artifact of the same version (pdf-only submissions)
    row = con.execute(
        "SELECT path FROM artifacts WHERE arxiv_id=? AND kind='pdf' AND version=? "
        "ORDER BY id DESC LIMIT 1", (arxiv_id, version)).fetchone()
    if row and (db.PROJECT_ROOT / row["path"]).exists():
        return db.PROJECT_ROOT / row["path"], "corpus", None
    # 2. cache from a previous render-check
    dest = pdf_path_for(arxiv_id, version)
    if dest.exists() and dest.stat().st_size > 0:
        return dest, "cache", None
    dest.parent.mkdir(parents=True, exist_ok=True)
    # 3. GCS mirror, then export fallback; a transient failure on one source
    # must not mask the other or become a terminal no_pdf (F13)
    yymm = arxiv_id.split(".")[0]
    transient = None
    for url, delay, source in (
            (GCS_URL.format(yymm=yymm, id=arxiv_id, v=version), GCS_DELAY, "gcs"),
            (EXPORT_URL.format(id=arxiv_id, v=version), EXPORT_DELAY, "export")):
        try:
            resp = session.get(url, timeout=180)
        except requests.RequestException as exc:
            transient = f"transient:{source}:{exc}"
            continue
        time.sleep(delay)
        if resp.status_code == 200 and resp.content[:4] == b"%PDF":
            dest.write_bytes(resp.content)
            sha = hashlib.sha256(resp.content).hexdigest()
            with con:
                con.execute(
                    "INSERT OR IGNORE INTO artifacts (arxiv_id, version, kind, "
                    "requested_version, path, sha256, bytes, fetch_channel, "
                    "fetched_at, format) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (arxiv_id, version, "pdf", version,
                     str(dest.relative_to(db.PROJECT_ROOT)), sha, len(resp.content),
                     "gcs-pdf" if source == "gcs" else "export", runs.utcnow(), "pdf"))
            return dest, source, None
        if resp.status_code >= 500 or resp.status_code == 429:
            transient = f"transient:{source}:http{resp.status_code}"
    return None, "none", transient or "notfound-on-all-sources"


def pdf_text(pdf_file: Path) -> str:
    # content-bound cache: the filename carries the source-PDF hash so a
    # refetched PDF can never inherit stale text (review-6 P0-6)
    sha = hashlib.sha256(pdf_file.read_bytes()).hexdigest()
    cache = pdf_file.with_suffix(f".{sha[:12]}.txt")
    if cache.exists() and cache.stat().st_size > 0:
        return cache.read_text(errors="replace")
    proc = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf_file), str(cache)],
                          capture_output=True, text=True, timeout=PDF_TIMEOUT)
    if proc.returncode != 0 or not cache.exists():
        return ""
    return cache.read_text(errors="replace")


def check_run(run_id: str, polarities: list[str], limit: int | None,
              redo: bool) -> int:
    con = db.connect()
    q = ("SELECT id, arxiv_id, version, quote FROM classification_items "
         "WHERE run_id=? AND status='ok' AND polarity IN (%s) "
         "AND quote IS NOT NULL AND quote != ''"
         % ",".join("?" * len(polarities)))
    if not redo:
        q += " AND render_status IN ('unchecked','pdf_error')"
    items = con.execute(q, [run_id, *polarities]).fetchall()
    by_paper: dict[tuple[str, int | None], list] = {}
    for it in items:
        by_paper.setdefault((it["arxiv_id"], it["version"]), []).append(it)
    papers = list(by_paper.items())
    if limit:
        papers = papers[:limit]
    print(f"{run_id}: {sum(len(v) for _, v in papers)} quotes across "
          f"{len(papers)} paper-versions to check", flush=True)

    session = requests.Session()
    session.trust_env = False  # fixed origins; no ambient proxies/.netrc
    session.headers["User-Agent"] = USER_AGENT
    n_rendered = n_non = n_err = 0
    for i, ((arxiv_id, version), paper_items) in enumerate(papers, 1):
        if version is None:
            # bulk artifacts of unknown version: a version-pinned render check
            # is impossible — never silently check against v1 (F1)
            for it in paper_items:
                with con:
                    con.execute(
                        "INSERT INTO render_checks (classification_item_id, arxiv_id, "
                        "version, matched, method, checked_at) VALUES (?,?,?,?,?,?)",
                        (it["id"], arxiv_id, None, None, "unknown-version",
                         runs.utcnow()))
                    con.execute("UPDATE classification_items SET render_status="
                                "'unknown_version' WHERE id=?", (it["id"],))
            n_err += len(paper_items)
            continue
        try:
            pdf_file, source, err = obtain_pdf(con, session, arxiv_id, version)
        except OSError as exc:  # same DrvFs race on the write/cache path
            pdf_file, source, err = None, "none", f"transient:pdf-io:{exc}"
        text = ""
        pdf_sha = None
        if pdf_file is not None:
            try:
                text = pdf_text(pdf_file)
                pdf_sha = hashlib.sha256(pdf_file.read_bytes()).hexdigest()
            except subprocess.TimeoutExpired:
                err = "transient:pdftotext-timeout"
            except OSError as exc:
                # DrvFs/antivirus can hold a freshly written PDF and fail
                # reads with EINVAL — transient, retryable, never a crash
                # (this killed the 2026-08-12 run at paper 2507.18269)
                err = f"transient:pdf-read:{exc}"
                text = ""
        for it in paper_items:
            if pdf_file is None:
                # transient failures stay retryable pdf_error; only a real
                # 404-everywhere is terminal no_pdf (F13)
                terminal = err is not None and err.startswith("notfound")
                status = "no_pdf" if terminal else "pdf_error"
                matched, method, score = None, "no-pdf:" + (err or ""), None
            elif not text:
                status, matched, method, score = "pdf_error", None, "no-text", None
            else:
                ok, method, score = match_quote(it["quote"], text)
                matched = int(ok)
                if ok:
                    # fuzzy matches are review-queue material, never automatic
                    # render certification (CROSSCHECK.md; review-4 P0-6) —
                    # only exact/dehyphenated matches earn 'rendered'
                    status = "rendered" if method != "fuzzy" else "rendered_fuzzy"
                elif method == "quote-too-short":
                    status = "quote_too_short"  # not certifiable either way
                else:
                    status = "non_rendered_evidence"
            with con:
                con.execute(
                    "INSERT INTO render_checks (classification_item_id, arxiv_id, "
                    "version, pdf_sha256, pdf_source, quote_normalized, matched, "
                    "method, score, checked_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (it["id"], arxiv_id, version, pdf_sha, source,
                     normalize(detex_quote(it["quote"]))[:600], matched, method,
                     score, runs.utcnow()))
                con.execute("UPDATE classification_items SET render_status=? WHERE id=?",
                            (status, it["id"]))
            n_rendered += status in ("rendered", "rendered_fuzzy")
            n_non += status in ("non_rendered_evidence", "quote_too_short")
            n_err += status in ("no_pdf", "pdf_error")
        if i % 25 == 0:
            print(f"{i}/{len(papers)} papers: {n_rendered} rendered, "
                  f"{n_non} non-rendered/short, {n_err} errors", flush=True)
    print(f"done: {n_rendered} rendered, {n_non} non_rendered/quote_too_short, "
          f"{n_err} no_pdf/pdf_error/unknown_version", flush=True)
    return 0 if n_err == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="classification run id")
    ap.add_argument("--polarity", nargs="+", default=["author_use"])
    ap.add_argument("--limit", type=int, default=None, help="max paper-versions")
    ap.add_argument("--redo", action="store_true",
                    help="re-check items that already have a render status")
    args = ap.parse_args()
    return check_run(args.run, args.polarity, args.limit, args.redo)


if __name__ == "__main__":
    sys.exit(main())
