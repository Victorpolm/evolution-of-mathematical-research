"""Recall audit: full-paper agent reads over scan-NEGATIVE papers.

Samples math-primary papers whose full text was scanned without any
llm/generic hit, sends the (comment-stripped) TeX to codex, and asks for any
overlooked AI-use disclosure. A hit here is a scanner false negative; the rate
over the sample estimates scanner recall on the corpus.

Usage: python3 -m pipeline.audit --run tex-v1 --sample 30 --workers 3
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import random
import sys
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import db
from .classify import call_codex, extract_json
from .scan import TEX_EXTS, decode, strip_tex_comments

MAX_CHARS = 180_000

PROMPT = """\
You are auditing a keyword-based scanner for missed AI-use disclosures in a \
mathematics paper. Below is the (comment-stripped) LaTeX source of one arXiv \
math paper. Search it carefully — especially acknowledgments, footnotes, \
dedicated statements, appendices, and remarks inside proofs — for ANY \
statement that the authors used AI systems, LLMs, chatbots, coding agents, or \
similar tools in producing this paper (any role: writing, translation, \
literature search, computations, code, proofs, figures). Also note explicit \
statements of NON-use. Ignore: citations to AI literature, AI as subject \
matter, classical software mentions without AI (Mathematica etc.) — unless \
the text says an AI produced/ran them.

Reply with ONLY JSON:
{"disclosure_found": true/false, "non_use_statement": true/false,
 "quotes": ["verbatim quote(s)"], "tools": ["..."],
 "notes": "one sentence"}

PAPER SOURCE:
"""


def paper_text(path: Path) -> str:
    data = path.read_bytes()
    parts: list[str] = []
    if data[:2] == b"\x1f\x8b":
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                for m in tf.getmembers():
                    if m.isfile() and Path(m.name).suffix.lower() in TEX_EXTS:
                        f = tf.extractfile(m)
                        if f:
                            parts.append(f"%% FILE: {m.name}\n"
                                         + strip_tex_comments(decode(f.read())))
        except tarfile.TarError:
            parts.append(strip_tex_comments(decode(gzip.decompress(data))))
    else:
        parts.append(strip_tex_comments(decode(data)))
    text = "\n".join(parts)
    if len(text) > MAX_CHARS:
        # disclosures cluster at head (after abstract) and tail (acks/appendix):
        # drop the middle, never the end
        head, tail = (2 * MAX_CHARS) // 3, MAX_CHARS // 3
        text = text[:head] + "\n[... MIDDLE OF PAPER TRUNCATED ...]\n" + text[-tail:]
    return text


def negatives(con, run: str) -> list[str]:
    return [r["arxiv_id"] for r in con.execute(
        "SELECT DISTINCT f.arxiv_id FROM files f "
        "JOIN papers p ON p.arxiv_id = f.arxiv_id "
        "WHERE f.status LIKE 'ok%' AND f.kind='src' "
        "AND p.primary_category LIKE 'math%' "
        "AND f.arxiv_id NOT IN (SELECT DISTINCT arxiv_id FROM scan_hits "
        "  WHERE scan_run=? AND tier IN ('llm','generic') AND rule_class != 'known_fp')",
        (run,))]


def main() -> int:
    import os
    if os.environ.get("ARXIV_OBS_LEGACY") != "1":
        sys.exit("DISABLED legacy path: superseded by the v2 pipeline "
                 "(destructive/unvalidated semantics; see WORKFLOW.md). "
                 "Set ARXIV_OBS_LEGACY=1 only for historical reproduction.")
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="tex-v1")
    ap.add_argument("--sample", type=int, default=30)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--model-label", default="codex-exec-default")
    args = ap.parse_args()

    con = db.connect()
    pool = sorted(negatives(con, args.run))
    random.Random(4242).shuffle(pool)
    done = {r["arxiv_id"] for r in con.execute(
        "SELECT arxiv_id FROM classifications WHERE stage='fullpaper_negative_audit'")}
    sample = [p for p in pool if p not in done][: args.sample]
    print(f"{len(pool)} negatives, auditing {len(sample)} (already done: {len(done)})",
          flush=True)
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    # resolve paths up front — sqlite connections are not thread-safe
    paths = {pid: con.execute(
        "SELECT path FROM files WHERE arxiv_id=? AND kind='src'",
        (pid,)).fetchone()["path"] for pid in sample}

    def work(pid: str):
        text = paper_text(db.PROJECT_ROOT / paths[pid])
        raw = call_codex(PROMPT + text, timeout=900)
        # object, not array — wrap for extract_json
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1:
            raise ValueError("no JSON object in reply")
        return pid, json.loads(raw[start:end + 1])

    n_found = n_done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(work, pid): pid for pid in sample}
        for fut in as_completed(futures):
            pid = futures[fut]
            try:
                pid, lab = fut.result()
            except Exception as exc:  # noqa: BLE001
                print(f"  {pid} FAILED: {exc}", flush=True)
                continue
            found = bool(lab.get("disclosure_found"))
            n_found += found
            n_done += 1
            with con:
                con.execute(
                    "INSERT OR IGNORE INTO classifications "
                    "(arxiv_id, stage, model, input_hash, label_json, created_at) "
                    "VALUES (?,?,?,?,?,?)",
                    (pid, "fullpaper_negative_audit", args.model_label,
                     hashlib.sha256(pid.encode()).hexdigest()[:24],
                     json.dumps(lab), now))
            print(f"  {pid}: {'MISSED DISCLOSURE' if found else 'clean'}"
                  + (f" -> {lab.get('quotes')}" if found else ""), flush=True)
    print(f"done: {n_found} missed disclosures in {n_done} successfully audited "
          f"negatives ({len(sample) - n_done} failed)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
