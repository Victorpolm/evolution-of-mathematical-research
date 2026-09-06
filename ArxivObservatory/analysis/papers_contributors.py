"""Offline, same-population paper/contributor time series for dashboard sparklines.

Reads an existing arXiv ID manifest and, optionally, a metadata-only CSV accepted
by analysis.democratization.load_authorships. No acquisition or paid calls.
Missing contributor data remain null. Aggregate outputs contain no IDs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .democratization import load_authorships


def month_number(value: str) -> int:
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        raise ValueError(f"invalid month: {value!r}")
    year, month = map(int, value.split("-"))
    return 12 * year + month - 1


def month_label(value: int) -> str:
    year, month = divmod(value, 12)
    return f"{year:04d}-{month + 1:02d}"


def parse_id(value: str) -> tuple[str, str]:
    """Accept post-2007 IDs, normalizing versions into a single paper."""
    match = re.fullmatch(r"(\d{2})(0[1-9]|1[0-2])\.(\d{4,5})(?:v[1-9]\d*)?", value)
    if not match:
        raise ValueError(f"invalid modern arXiv ID: {value!r}")
    yy, mm, serial = match.groups()
    year = 2000 + int(yy)
    if year < 2007:
        raise ValueError("this manifest reader supports modern arXiv IDs from 2007")
    return f"{yy}{mm}.{serial}", f"{year:04d}-{mm}"


def analyze(
    manifest_path: Path,
    *,
    start_month: str,
    end_month: str,
    source: dict,
    authorships_path: Path | None = None,
) -> dict:
    """Caller must specify a window of complete months in the source snapshot.

    ID month is an explicit proxy for initial submission month. Manifest
    coverage outside the supplied list is not established by this function.
    """
    start, end = month_number(start_month), month_number(end_month)
    if end < start:
        raise ValueError("end month precedes start month")
    raw = manifest_path.read_bytes()
    blob_sha = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    if source.get("blobSha") and source["blobSha"] != blob_sha:
        raise ValueError("manifest does not match the declared Git blob SHA")
    papers_by_month: dict[str, set[str]] = defaultdict(set)
    ids: dict[str, str] = {}
    duplicates = blank_lines = 0
    for number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            blank_lines += 1
            continue
        try:
            paper_id, month = parse_id(line.strip())
        except ValueError as exc:
            raise ValueError(f"manifest line {number}: {exc}") from exc
        if paper_id in ids:
            duplicates += 1
        ids[paper_id] = month
        if start <= month_number(month) <= end:
            papers_by_month[month].add(paper_id)
    if not ids or not any(papers_by_month.values()):
        raise ValueError("manifest has no papers in the requested window")

    matched: dict[str, set[str]] = defaultdict(set)
    complete: dict[str, dict[str, set[str]]] = defaultdict(dict)
    author_diagnostics = None
    if authorships_path is not None:
        works, diagnostics = load_authorships(authorships_path)
        seen: set[str] = set()
        reasons: Counter = Counter()
        for paper in works.values():
            paper_id, month = parse_id(paper.arxiv_id)
            if paper_id in seen:
                raise ValueError(f"multiple work IDs map to arXiv ID {paper_id}; resolve before analysis")
            seen.add(paper_id)
            if paper.year != int(month[:4]) or (
                paper.month is not None and paper.month != int(month[5:])
            ):
                raise ValueError(f"metadata date disagrees with ID month for {paper_id}")
            if paper_id not in ids:
                reasons["outside_manifest"] += 1
                continue
            if not start <= month_number(month) <= end:
                reasons["outside_analysis_window"] += 1
                continue
            matched[month].add(paper_id)
            if paper.authorships_total is None or paper.authorships_missing_id is None:
                reasons["unknown_authorship_coverage"] += 1
            elif paper.authorships_truncated:
                reasons["truncated_authorships"] += 1
            elif paper.authorships_missing_id != 0:
                reasons["missing_author_ids"] += 1
            elif paper.authorships_total != len(paper.authors):
                reasons["identified_count_disagrees_with_total"] += 1
            else:
                complete[month][paper_id] = paper.authors
        author_diagnostics = {
            "inputSha256": hashlib.sha256(authorships_path.read_bytes()).hexdigest(),
            "loader": diagnostics.__dict__,
            "excludedPaperReasons": dict(reasons),
        }

    def period_row(label: str, months: list[str]) -> dict:
        frame_count = sum(len(papers_by_month[m]) for m in months)
        if authorships_path is None:
            return {"period": label, "framePapers": frame_count, "papers": frame_count,
                    "contributors": None, "papersPerContributor": None,
                    "authorships": None, "fullCountPerContributor": None,
                    "meanTeamSize": None, "matchedPaperShare": None,
                    "completePaperShare": None}
        author_sets = [authors for m in months for authors in complete[m].values()]
        contributors = set().union(*author_sets) if author_sets else set()
        n_papers, n_authors = len(author_sets), len(contributors)
        incidences = sum(map(len, author_sets))
        return {
            "period": label, "framePapers": frame_count, "papers": n_papers,
            "contributors": n_authors,
            "papersPerContributor": n_papers / n_authors if n_authors else None,
            "authorships": incidences,
            "fullCountPerContributor": incidences / n_authors if n_authors else None,
            "meanTeamSize": incidences / n_papers if n_papers else None,
            "matchedPaperShare": sum(len(matched[m]) for m in months) / frame_count if frame_count else None,
            "completePaperShare": n_papers / frame_count if frame_count else None,
        }

    months = [month_label(i) for i in range(start, end + 1)]
    monthly = [period_row(m, [m]) for m in months]
    rolling = [period_row(months[i], months[i - 11:i + 1]) for i in range(11, len(months))]
    years = range(start // 12, end // 12 + 1)
    annual = [period_row(str(year), [f"{year}-{m:02d}" for m in range(1, 13)])
              for year in years if start <= year * 12 and year * 12 + 11 <= end]
    return {
        "schemaVersion": 1,
        "source": {**source, "inputSha256": hashlib.sha256(raw).hexdigest(), "blobSha": blob_sha},
        "window": {"start": start_month, "end": end_month, "boundaryRule": "complete months declared by caller"},
        "population": "complete matched authorship papers" if authorships_path else "repository paper-ID manifest only",
        "contributorDefinition": "distinct author IDs on the same retained papers, deduplicated within each window",
        "dateDefinition": "arXiv ID month; proxy for first submission month, not journal publication date",
        "hasContributorData": authorships_path is not None,
        "diagnostics": {
            "uniqueManifestIds": len(ids), "duplicateManifestLines": duplicates,
            "blankManifestLines": blank_lines,
            "papersInWindow": sum(len(v) for v in papers_by_month.values()),
            "papersOutsideWindow": len(ids) - sum(len(v) for v in papers_by_month.values()),
            "incompleteCalendarYearsOmitted": [y for y in years if not (start <= y * 12 and y * 12 + 11 <= end)],
            "authorships": author_diagnostics,
        },
        "monthly": monthly, "rolling12": rolling, "annual": annual,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--authorships", type=Path)
    parser.add_argument("--start-month", required=True)
    parser.add_argument("--end-month", required=True)
    parser.add_argument("--source-label", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--source-blob-sha")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.manifest, start_month=args.start_month, end_month=args.end_month,
                     authorships_path=args.authorships,
                     source={"label": args.source_label, "url": args.source_url,
                             "revision": args.source_revision, "blobSha": args.source_blob_sha})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "papers_contributors.json").write_text(json.dumps(result, indent=2) + "\n")
    for name in ("monthly", "rolling12", "annual"):
        rows = result[name]
        if rows:
            with (args.output_dir / f"papers_contributors_{name}.csv").open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    print(json.dumps({"annual": result["annual"], "diagnostics": result["diagnostics"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
