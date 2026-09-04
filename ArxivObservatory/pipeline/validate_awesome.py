"""Recall cross-check against seewoo5/awesome-ai-for-math.

Every arXiv-linked entry in their table is bucketed against our pipeline:
  in_frame_flagged      — math-primary, in window, our scanner flagged it
  in_frame_not_flagged  — math-primary, in window, no scanner flag
                          (either a scanner miss OR no in-text disclosure exists;
                          these go to the manual/agent audit queue)
  out_of_frame_category — primary category not math.*
  out_of_frame_window   — outside the harvest window
  not_in_db             — in window by ID but absent from harvest (investigate)

Usage: python3 -m pipeline.validate_awesome --readme <path> [--llm-only]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import db

ROW_RE = re.compile(r"^\| \*\*\[(?P<title>.+?)\]\((?P<url>[^)]+)\)\*\* \| (?P<subjects>[^|]+) \|")
ARXIV_ID_RE = re.compile(r"arxiv\.org/(?:abs|pdf|src)/(\d{4}\.\d{4,5})")


def parse_entries(readme: Path) -> list[dict]:
    entries = []
    for line in readme.read_text().splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        ids = ARXIV_ID_RE.findall(line)
        entries.append({
            "title": m.group("title"),
            "subjects": [s.strip() for s in m.group("subjects").split(",")],
            "arxiv_id": ids[0] if ids else None,
            "all_ids": ids,
        })
    return entries


def bucket(con, entries: list[dict], window_months: set[str],
           flagged: set[str]) -> list[dict]:
    for e in entries:
        pid = e["arxiv_id"]
        if pid is None:
            e["bucket"] = "no_arxiv_id"
            continue
        yymm = pid.split(".")[0]
        if yymm not in window_months:
            e["bucket"] = "out_of_frame_window"
            continue
        row = con.execute("SELECT primary_category FROM papers WHERE arxiv_id=?",
                          (pid,)).fetchone()
        if row is None:
            e["bucket"] = "not_in_db"
            continue
        e["primary_category"] = row["primary_category"]
        if not (row["primary_category"] or "").startswith("math"):
            e["bucket"] = "out_of_frame_category"
            continue
        e["bucket"] = "in_frame_flagged" if pid in flagged else "in_frame_not_flagged"
    return entries


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", required=True)
    ap.add_argument("--llm-only", action="store_true",
                    help="restrict to entries with subject tag 'LLM'")
    ap.add_argument("--months", nargs="+", default=["2605", "2606", "2607", "2608"])
    ap.add_argument("--runs", nargs="+", default=["meta-v1", "tex-v1"])
    ap.add_argument("--out", default="reports/awesome_validation.json")
    args = ap.parse_args()

    con = db.connect()
    entries = parse_entries(Path(args.readme))
    if len(entries) < 50:
        sys.exit(f"FATAL: only {len(entries)} entries parsed — README format changed?")
    if args.llm_only:
        entries = [e for e in entries if "LLM" in e["subjects"]]
    flagged = {r["arxiv_id"] for r in con.execute(
        "SELECT DISTINCT arxiv_id FROM scan_hits WHERE scan_run IN (%s) "
        "AND tier IN ('llm','generic') AND rule_class != 'known_fp'"
        % ",".join("?" * len(args.runs)), args.runs)}
    entries = bucket(con, entries, set(args.months), flagged)

    counts: dict[str, int] = {}
    for e in entries:
        counts[e["bucket"]] = counts.get(e["bucket"], 0) + 1
    print(f"{len(entries)} entries ({'LLM-tagged' if args.llm_only else 'all'}):")
    for b, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {b:24s} {c}")
    for e in entries:
        if e["bucket"] in ("in_frame_not_flagged", "not_in_db"):
            print(f"  -> {e['bucket']}: {e['arxiv_id']} {e['title'][:70]}")
    out = Path(args.out)
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(entries, indent=1))
    print(f"written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
