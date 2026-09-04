"""Offline analysis of participation and output concentration in arXiv math.

The input is a metadata-only CSV with one row per paper-author pair.  No
paper text, snippets, or per-paper AI labels are consumed or emitted.  The
module deliberately uses only the Python standard library so it remains
fixture-testable in the repository's minimal environment.

Required columns
----------------
work_id, arxiv_id, publication_year, author_id, primary_subfield

Optional columns
----------------
publication_month, referenced_works_count, institution_ids, country_codes,
authorships_truncated, authorships_total, authorships_missing_id

``publication_year`` must be the arXiv identifier year, not OpenAlex's
version-of-record publication year.  See ``DEMOCRATIZATION.md``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence
from xml.sax.saxutils import escape


REQUIRED_COLUMNS = {
    "work_id",
    "arxiv_id",
    "publication_year",
    "author_id",
    "primary_subfield",
}


@dataclass
class Paper:
    work_id: str
    arxiv_id: str
    year: int
    month: int | None
    subfield: str
    referenced_works_count: int | None
    authorships_truncated: bool = False
    authorships_total: int | None = None
    authorships_missing_id: int | None = None
    authors: set[str] = field(default_factory=set)


@dataclass
class LoadDiagnostics:
    input_rows: int = 0
    duplicate_authorship_rows: int = 0
    papers_with_truncated_authorships: int = 0
    papers_with_known_authorship_coverage: int = 0
    papers_with_missing_author_ids: int = 0


def _parse_optional_int(value: str | None, *, field_name: str, row_no: int) -> int | None:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"row {row_no}: invalid {field_name}={value!r}") from exc


def _parse_bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes"}


def load_authorships(path: Path | str) -> tuple[dict[str, Paper], LoadDiagnostics]:
    """Load and validate one-row-per-paper-author metadata."""
    path = Path(path)
    papers: dict[str, Paper] = {}
    diagnostics = LoadDiagnostics()

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"input is missing required columns: {sorted(missing)}")

        for row_no, row in enumerate(reader, start=2):
            diagnostics.input_rows += 1
            work_id = row["work_id"].strip()
            arxiv_id = row["arxiv_id"].strip()
            author_id = row["author_id"].strip()
            subfield = row["primary_subfield"].strip() or "unknown"
            if not work_id or not arxiv_id or not author_id:
                raise ValueError(f"row {row_no}: work_id, arxiv_id, and author_id are required")

            year = _parse_optional_int(
                row.get("publication_year"), field_name="publication_year", row_no=row_no
            )
            month = _parse_optional_int(
                row.get("publication_month"), field_name="publication_month", row_no=row_no
            )
            references = _parse_optional_int(
                row.get("referenced_works_count"),
                field_name="referenced_works_count",
                row_no=row_no,
            )
            authorships_total = _parse_optional_int(
                row.get("authorships_total"), field_name="authorships_total", row_no=row_no
            )
            authorships_missing_id = _parse_optional_int(
                row.get("authorships_missing_id"),
                field_name="authorships_missing_id",
                row_no=row_no,
            )
            if year is None or not 1900 <= year <= 2100:
                raise ValueError(f"row {row_no}: publication_year is out of range")
            if month is not None and not 1 <= month <= 12:
                raise ValueError(f"row {row_no}: publication_month is out of range")
            if references is not None and references < 0:
                raise ValueError(f"row {row_no}: referenced_works_count is negative")
            if authorships_total is not None and authorships_total < 1:
                raise ValueError(f"row {row_no}: authorships_total must be positive")
            if authorships_missing_id is not None and authorships_missing_id < 0:
                raise ValueError(f"row {row_no}: authorships_missing_id is negative")
            if (
                authorships_total is not None
                and authorships_missing_id is not None
                and authorships_missing_id > authorships_total
            ):
                raise ValueError(f"row {row_no}: missing authorships exceed total authorships")

            truncated = _parse_bool(row.get("authorships_truncated"))
            paper = papers.get(work_id)
            if paper is None:
                paper = Paper(
                    work_id=work_id,
                    arxiv_id=arxiv_id,
                    year=year,
                    month=month,
                    subfield=subfield,
                    referenced_works_count=references,
                    authorships_truncated=truncated,
                    authorships_total=authorships_total,
                    authorships_missing_id=authorships_missing_id,
                )
                papers[work_id] = paper
            else:
                signature = (
                    paper.arxiv_id,
                    paper.year,
                    paper.month,
                    paper.subfield,
                    paper.referenced_works_count,
                    paper.authorships_total,
                    paper.authorships_missing_id,
                )
                incoming = (
                    arxiv_id,
                    year,
                    month,
                    subfield,
                    references,
                    authorships_total,
                    authorships_missing_id,
                )
                if signature != incoming:
                    raise ValueError(f"row {row_no}: inconsistent metadata for work {work_id}")
                paper.authorships_truncated = paper.authorships_truncated or truncated

            if author_id in paper.authors:
                diagnostics.duplicate_authorship_rows += 1
            paper.authors.add(author_id)

    if not papers:
        raise ValueError("input contains no papers")
    if any(not paper.authors for paper in papers.values()):
        raise ValueError("every paper must have at least one author")
    diagnostics.papers_with_truncated_authorships = sum(
        paper.authorships_truncated for paper in papers.values()
    )
    diagnostics.papers_with_known_authorship_coverage = sum(
        paper.authorships_total is not None and paper.authorships_missing_id is not None
        for paper in papers.values()
    )
    diagnostics.papers_with_missing_author_ids = sum(
        (paper.authorships_missing_id or 0) > 0 for paper in papers.values()
    )
    return papers, diagnostics


def gini(values: Sequence[float]) -> float:
    """Return the population Gini coefficient for non-negative values."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if ordered[0] < 0:
        raise ValueError("Gini values must be non-negative")
    total = sum(ordered)
    if total == 0:
        return 0.0
    n = len(ordered)
    weighted = sum((2 * index - n - 1) * value for index, value in enumerate(ordered, 1))
    return weighted / (n * total)


def top_share(values: Sequence[float], proportion: float) -> float:
    """Share held by the top ceil(proportion * n) observations."""
    if not 0 < proportion <= 1:
        raise ValueError("proportion must lie in (0, 1]")
    if not values:
        return 0.0
    total = sum(values)
    if total <= 0:
        return 0.0
    count = max(1, math.ceil(proportion * len(values)))
    return sum(sorted(values, reverse=True)[:count]) / total


def _median(values: Iterable[float]) -> float | None:
    values = list(values)
    return float(statistics.median(values)) if values else None


def _scope_metrics(
    papers: Sequence[Paper],
    *,
    frame_papers: Sequence[Paper] | None = None,
    year: int,
    scope: str,
    first_observed_year: dict[str, int],
    data_start_year: int,
) -> dict[str, object]:
    frame_papers = list(frame_papers if frame_papers is not None else papers)
    fractional: dict[str, float] = defaultdict(float)
    full: dict[str, float] = defaultdict(float)
    team_sizes: list[int] = []
    references: list[int] = []

    for paper in papers:
        team_size = len(paper.authors)
        team_sizes.append(team_size)
        if paper.referenced_works_count is not None:
            references.append(paper.referenced_works_count)
        for author_id in paper.authors:
            fractional[author_id] += 1.0 / team_size
            full[author_id] += 1.0

    active_authors = sorted(fractional)
    ages = [year - first_observed_year[author_id] for author_id in active_authors]
    n_authors = len(active_authors)
    n_papers = len(papers)
    n_frame_papers = len(frame_papers)
    fractional_values = [fractional[author_id] for author_id in active_authors]
    full_values = [full[author_id] for author_id in active_authors]

    return {
        "year": year,
        "scope": scope,
        "n_papers_frame": n_frame_papers,
        "n_papers": n_papers,
        "n_active_authors": n_authors,
        "fractional_output_per_author": n_papers / n_authors if n_authors else None,
        "new_author_share": sum(age == 0 for age in ages) / n_authors if n_authors else None,
        "early_career_share_0_3": sum(age <= 3 for age in ages) / n_authors if n_authors else None,
        "median_observed_math_age": _median(ages),
        "left_censored_author_share": (
            sum(first_observed_year[a] == data_start_year for a in active_authors) / n_authors
            if n_authors
            else None
        ),
        "solo_paper_share": sum(size == 1 for size in team_sizes) / n_papers,
        "team_3plus_share": sum(size >= 3 for size in team_sizes) / n_papers,
        "mean_team_size": statistics.fmean(team_sizes),
        "median_team_size": _median(team_sizes),
        "top_1pct_fractional_share": top_share(fractional_values, 0.01),
        "top_5pct_fractional_share": top_share(fractional_values, 0.05),
        "top_10pct_fractional_share": top_share(fractional_values, 0.10),
        "gini_fractional_output": gini(fractional_values),
        "top_10pct_full_count_share": top_share(full_values, 0.10),
        "gini_full_count_output": gini(full_values),
        "mean_referenced_works": statistics.fmean(references) if references else None,
        "median_referenced_works": _median(references),
        "reference_coverage_share": len(references) / n_papers,
        "truncated_authorship_paper_share": (
            sum(paper.authorships_truncated for paper in papers) / n_papers
        ),
        "authorship_coverage_known_share": (
            sum(
                paper.authorships_total is not None and paper.authorships_missing_id is not None
                for paper in frame_papers
            )
            / n_frame_papers
        ),
        "complete_authorship_paper_share": (
            sum(
                paper.authorships_total is not None
                and paper.authorships_missing_id == 0
                and not paper.authorships_truncated
                for paper in frame_papers
            )
            / n_frame_papers
        ),
        "missing_author_id_slot_share": (
            sum(paper.authorships_missing_id or 0 for paper in frame_papers)
            / sum(paper.authorships_total or 0 for paper in frame_papers)
            if sum(paper.authorships_total or 0 for paper in frame_papers)
            else None
        ),
    }


def compute_annual_metrics(
    papers: dict[str, Paper],
    *,
    analysis_start: int,
    analysis_end: int,
    minimum_lookback: int = 5,
    include_subfields: bool = True,
    require_complete_authorships: bool = False,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Compute yearly overall and subfield metrics.

    The dataset must begin at least ``minimum_lookback`` years before the
    analysis window.  This does not eliminate left-censoring; it makes the
    operational definition of observed entry less fragile.
    """
    if analysis_end < analysis_start:
        raise ValueError("analysis_end precedes analysis_start")
    data_start_year = min(paper.year for paper in papers.values())
    data_end_year = max(paper.year for paper in papers.values())
    if analysis_start - data_start_year < minimum_lookback:
        raise ValueError(
            f"only {analysis_start - data_start_year} lookback years; "
            f"at least {minimum_lookback} required"
        )

    first_observed_year: dict[str, int] = {}
    for paper in papers.values():
        for author_id in paper.authors:
            first_observed_year[author_id] = min(
                paper.year, first_observed_year.get(author_id, paper.year)
            )

    metrics: list[dict[str, object]] = []
    for year in range(analysis_start, analysis_end + 1):
        year_papers = [paper for paper in papers.values() if paper.year == year]
        if not year_papers:
            continue
        analyzed_year_papers = year_papers
        if require_complete_authorships:
            analyzed_year_papers = [
                paper
                for paper in year_papers
                if paper.authorships_total is not None
                and paper.authorships_missing_id == 0
                and not paper.authorships_truncated
            ]
        if not analyzed_year_papers:
            continue
        metrics.append(
            _scope_metrics(
                analyzed_year_papers,
                frame_papers=year_papers,
                year=year,
                scope="all",
                first_observed_year=first_observed_year,
                data_start_year=data_start_year,
            )
        )
        if include_subfields:
            subfields = sorted({paper.subfield for paper in year_papers})
            for subfield in subfields:
                subfield_frame = [paper for paper in year_papers if paper.subfield == subfield]
                subfield_papers = [
                    paper for paper in analyzed_year_papers if paper.subfield == subfield
                ]
                if not subfield_papers:
                    continue
                metrics.append(
                    _scope_metrics(
                        subfield_papers,
                        frame_papers=subfield_frame,
                        year=year,
                        scope=f"subfield:{subfield}",
                        first_observed_year=first_observed_year,
                        data_start_year=data_start_year,
                    )
                )

    diagnostics = {
        "data_start_year": data_start_year,
        "data_end_year": data_end_year,
        "analysis_start": analysis_start,
        "analysis_end": analysis_end,
        "lookback_years": analysis_start - data_start_year,
        "n_input_papers": len(papers),
        "n_unique_authors": len(first_observed_year),
        "require_complete_authorships": require_complete_authorships,
        "age_definition": "years since first observed arXiv-math work in input data",
        "left_censoring_warning": (
            "Authors first observed in the initial data year may have earlier careers. "
            "Observed age is not global academic age."
        ),
    }
    return metrics, diagnostics


CSV_FIELDS = [
    "year",
    "scope",
    "n_papers_frame",
    "n_papers",
    "n_active_authors",
    "fractional_output_per_author",
    "new_author_share",
    "early_career_share_0_3",
    "median_observed_math_age",
    "left_censored_author_share",
    "solo_paper_share",
    "team_3plus_share",
    "mean_team_size",
    "median_team_size",
    "top_1pct_fractional_share",
    "top_5pct_fractional_share",
    "top_10pct_fractional_share",
    "gini_fractional_output",
    "top_10pct_full_count_share",
    "gini_full_count_output",
    "mean_referenced_works",
    "median_referenced_works",
    "reference_coverage_share",
    "truncated_authorship_paper_share",
    "authorship_coverage_known_share",
    "complete_authorship_paper_share",
    "missing_author_id_slot_share",
]


def write_metrics_csv(metrics: Sequence[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in metrics:
            writer.writerow({field: row.get(field) for field in CSV_FIELDS})


def _indexed(values: Sequence[float | int | None]) -> list[float | None]:
    base = next((float(value) for value in values if value not in (None, 0)), None)
    return [None if value is None or base is None else 100 * float(value) / base for value in values]


def _polyline(
    values: Sequence[float | None],
    years: Sequence[int],
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    low: float,
    high: float,
) -> str:
    points = []
    year_span = max(1, max(years) - min(years))
    value_span = max(1e-12, high - low)
    for year, value in zip(years, values):
        if value is None:
            continue
        px = x + width * (year - min(years)) / year_span
        py = y + height - height * (value - low) / value_span
        points.append(f"{px:.1f},{py:.1f}")
    return " ".join(points)


def _panel(
    title: str,
    years: Sequence[int],
    series: Sequence[tuple[str, Sequence[float | None], str]],
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    percent: bool = False,
) -> str:
    plot_x, plot_y = x + 52, y + 40
    # Leave distinct bands for year ticks and the legend so compact panels do
    # not place the first year on top of the first series label.
    plot_w, plot_h = width - 72, height - 116
    finite = [float(v) for _, values, _ in series for v in values if v is not None]
    low = 0.0 if percent else min(finite, default=0.0)
    high = max(finite, default=1.0)
    if math.isclose(low, high):
        high = low + 1.0
    if not percent:
        padding = 0.08 * (high - low)
        low = max(0.0, low - padding)
        high += padding

    parts = [
        f'<g><text x="{x + 12}" y="{y + 20}" class="title">{escape(title)}</text>',
        f'<line x1="{plot_x}" y1="{plot_y}" x2="{plot_x}" y2="{plot_y + plot_h}" class="axis"/>',
        f'<line x1="{plot_x}" y1="{plot_y + plot_h}" x2="{plot_x + plot_w}" y2="{plot_y + plot_h}" class="axis"/>',
        f'<text x="{plot_x - 8}" y="{plot_y + 4}" text-anchor="end" class="tick">{high:.1f}{"%" if percent else ""}</text>',
        f'<text x="{plot_x - 8}" y="{plot_y + plot_h + 4}" text-anchor="end" class="tick">{low:.1f}{"%" if percent else ""}</text>',
        f'<text x="{plot_x}" y="{plot_y + plot_h + 18}" class="tick">{min(years)}</text>',
        f'<text x="{plot_x + plot_w}" y="{plot_y + plot_h + 18}" text-anchor="end" class="tick">{max(years)}</text>',
    ]
    for index, (label, values, color) in enumerate(series):
        points = _polyline(values, years, x=plot_x, y=plot_y, width=plot_w, height=plot_h, low=low, high=high)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        legend_x = plot_x + (index % 2) * (plot_w / 2)
        legend_y = y + height - 26 + (index // 2) * 14
        parts.append(f'<line x1="{legend_x}" y1="{legend_y - 4}" x2="{legend_x + 16}" y2="{legend_y - 4}" stroke="{color}" stroke-width="2.5"/>')
        parts.append(f'<text x="{legend_x + 21}" y="{legend_y}" class="legend">{escape(label)}</text>')
    parts.append("</g>")
    return "".join(parts)


def write_overview_svg(metrics: Sequence[dict[str, object]], path: Path) -> None:
    overall = sorted((row for row in metrics if row["scope"] == "all"), key=lambda r: r["year"])
    if not overall:
        raise ValueError("no overall rows to plot")
    years = [int(row["year"]) for row in overall]
    colors = ["#146b8c", "#d97706", "#6b4c9a", "#248f5a"]
    production = [
        ("papers (index)", _indexed([row["n_papers"] for row in overall]), colors[0]),
        ("active authors (index)", _indexed([row["n_active_authors"] for row in overall]), colors[1]),
        ("output/author (index)", _indexed([row["fractional_output_per_author"] for row in overall]), colors[2]),
    ]
    concentration = [
        ("top 1%", [100 * float(row["top_1pct_fractional_share"]) for row in overall], colors[0]),
        ("top 5%", [100 * float(row["top_5pct_fractional_share"]) for row in overall], colors[1]),
        ("top 10%", [100 * float(row["top_10pct_fractional_share"]) for row in overall], colors[2]),
        ("Gini", [100 * float(row["gini_fractional_output"]) for row in overall], colors[3]),
    ]
    entry = [
        ("new observed authors", [100 * float(row["new_author_share"]) for row in overall], colors[0]),
        ("observed age 0–3", [100 * float(row["early_career_share_0_3"]) for row in overall], colors[1]),
        ("left-censored", [100 * float(row["left_censored_author_share"]) for row in overall], colors[2]),
    ]
    teams = [
        ("mean team size", [float(row["mean_team_size"]) for row in overall], colors[0]),
        ("median team size", [float(row["median_team_size"]) for row in overall], colors[1]),
    ]

    width, height = 1120, 760
    panels = [
        _panel("Production decomposition (first year = 100)", years, production, x=20, y=50, width=530, height=320),
        _panel("Output concentration", years, concentration, x=570, y=50, width=530, height=320, percent=True),
        _panel("Observed entry and censoring", years, entry, x=20, y=410, width=530, height=320, percent=True),
        _panel("Collaboration size", years, teams, x=570, y=410, width=530, height=320),
    ]
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        "<style>text{font-family:Arial,sans-serif;fill:#202124}.heading{font-size:22px;font-weight:700}"
        ".title{font-size:16px;font-weight:700}.tick,.legend{font-size:11px}.axis{stroke:#777;stroke-width:1}</style>"
        '<rect width="100%" height="100%" fill="#fff"/>'
        '<text x="24" y="30" class="heading">arXiv mathematics: participation and concentration</text>'
        + "".join(panels)
        + "</svg>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_analysis(
    input_path: Path,
    output_dir: Path,
    *,
    analysis_start: int,
    analysis_end: int,
    minimum_lookback: int = 5,
    include_subfields: bool = True,
    require_complete_authorships: bool = False,
) -> dict[str, Path]:
    papers, load_diagnostics = load_authorships(input_path)
    metrics, diagnostics = compute_annual_metrics(
        papers,
        analysis_start=analysis_start,
        analysis_end=analysis_end,
        minimum_lookback=minimum_lookback,
        include_subfields=include_subfields,
        require_complete_authorships=require_complete_authorships,
    )
    if not metrics:
        raise ValueError("analysis window contains no papers")

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "annual_metrics.csv"
    svg_path = output_dir / "democratization_overview.svg"
    manifest_path = output_dir / "methodology.json"
    write_metrics_csv(metrics, csv_path)
    write_overview_svg(metrics, svg_path)
    manifest = {
        **diagnostics,
        "input_sha256": _sha256(input_path),
        "load_diagnostics": load_diagnostics.__dict__,
        "fractional_counting": "each author receives 1/k for a k-author paper",
        "top_decile_definition": "top ceil(0.10 * active authors) within year and scope",
        "outputs_are_aggregate_only": True,
        "causal_claim": "none; descriptive census of OpenAlex-linked metadata",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"metrics": csv_path, "plot": svg_path, "manifest": manifest_path}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="paper-author CSV")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--analysis-start", required=True, type=int)
    parser.add_argument("--analysis-end", required=True, type=int)
    parser.add_argument("--minimum-lookback", type=int, default=5)
    parser.add_argument("--overall-only", action="store_true")
    parser.add_argument(
        "--require-complete-authorships",
        action="store_true",
        help="exclude papers with unknown/missing/truncated OpenAlex author IDs",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    outputs = run_analysis(
        args.input,
        args.output_dir,
        analysis_start=args.analysis_start,
        analysis_end=args.analysis_end,
        minimum_lookback=args.minimum_lookback,
        include_subfields=not args.overall_only,
        require_complete_authorships=args.require_complete_authorships,
    )
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
