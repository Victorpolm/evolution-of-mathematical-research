import csv
import json
from pathlib import Path

import pytest

from analysis.democratization import (
    compute_annual_metrics,
    gini,
    load_authorships,
    run_analysis,
    top_share,
)


FIELDS = [
    "work_id",
    "arxiv_id",
    "publication_year",
    "publication_month",
    "author_id",
    "primary_subfield",
    "referenced_works_count",
    "authorships_truncated",
    "authorships_total",
    "authorships_missing_id",
]


def _write_fixture(path: Path) -> None:
    rows = [
        # Two lookback years establish A as incumbent.
        ("w18", "1801.00001", 2018, 1, "A", "Algebra", 10, 0, 1, 0),
        ("w19", "1901.00001", 2019, 1, "A", "Algebra", 12, 0, 1, 0),
        # 2020: A has 1.5 fractional papers; new B has 0.5.
        ("w20a", "2001.00001", 2020, 1, "A", "Algebra", 20, 0, 1, 0),
        ("w20b", "2001.00002", 2020, 1, "A", "Geometry", 30, 0, 2, 0),
        ("w20b", "2001.00002", 2020, 1, "B", "Geometry", 30, 0, 2, 0),
        # 2021: one three-author collaboration; C is new.
        ("w21", "2101.00001", 2021, 1, "A", "Geometry", 40, 0, 3, 0),
        ("w21", "2101.00001", 2021, 1, "B", "Geometry", 40, 0, 3, 0),
        ("w21", "2101.00001", 2021, 1, "C", "Geometry", 40, 0, 3, 0),
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        writer.writerows(rows)


def test_fractional_decomposition_and_concentration(tmp_path):
    input_path = tmp_path / "paper_authors.csv"
    _write_fixture(input_path)
    papers, diagnostics = load_authorships(input_path)
    metrics, meta = compute_annual_metrics(
        papers,
        analysis_start=2020,
        analysis_end=2021,
        minimum_lookback=2,
        include_subfields=False,
    )

    y2020 = next(row for row in metrics if row["year"] == 2020)
    assert y2020["n_papers"] == 2
    assert y2020["n_active_authors"] == 2
    assert y2020["fractional_output_per_author"] == pytest.approx(1.0)
    assert y2020["new_author_share"] == pytest.approx(0.5)
    assert y2020["solo_paper_share"] == pytest.approx(0.5)
    assert y2020["mean_team_size"] == pytest.approx(1.5)
    assert y2020["complete_authorship_paper_share"] == pytest.approx(1.0)
    assert y2020["top_10pct_fractional_share"] == pytest.approx(0.75)
    assert y2020["mean_referenced_works"] == pytest.approx(25.0)
    assert meta["age_definition"].startswith("years since first observed")
    assert diagnostics.duplicate_authorship_rows == 0


def test_full_outputs_are_aggregate_only(tmp_path):
    input_path = tmp_path / "paper_authors.csv"
    output_dir = tmp_path / "out"
    _write_fixture(input_path)

    outputs = run_analysis(
        input_path,
        output_dir,
        analysis_start=2020,
        analysis_end=2021,
        minimum_lookback=2,
    )

    assert outputs["metrics"].exists()
    assert outputs["plot"].read_text(encoding="utf-8").startswith("<svg")
    manifest = json.loads(outputs["manifest"].read_text(encoding="utf-8"))
    assert manifest["outputs_are_aggregate_only"] is True
    assert manifest["input_sha256"]
    with outputs["metrics"].open(newline="", encoding="utf-8") as handle:
        output_fields = csv.DictReader(handle).fieldnames
    assert "author_id" not in output_fields
    assert "arxiv_id" not in output_fields


def test_lookback_gate_and_concentration_helpers(tmp_path):
    input_path = tmp_path / "paper_authors.csv"
    _write_fixture(input_path)
    papers, _ = load_authorships(input_path)

    with pytest.raises(ValueError, match="lookback"):
        compute_annual_metrics(
            papers,
            analysis_start=2020,
            analysis_end=2021,
            minimum_lookback=5,
        )

    assert top_share([1.5, 0.5], 0.10) == pytest.approx(0.75)
    assert gini([1.0, 1.0]) == pytest.approx(0.0)
    assert gini([0.0, 2.0]) == pytest.approx(0.5)


def test_complete_authorship_filter_excludes_incomplete_papers(tmp_path):
    input_path = tmp_path / "paper_authors.csv"
    _write_fixture(input_path)
    papers, _ = load_authorships(input_path)
    papers["w20a"].authorships_total = 2
    papers["w20a"].authorships_missing_id = 1

    unfiltered, _ = compute_annual_metrics(
        papers,
        analysis_start=2020,
        analysis_end=2021,
        minimum_lookback=2,
        include_subfields=False,
    )
    filtered, _ = compute_annual_metrics(
        papers,
        analysis_start=2020,
        analysis_end=2021,
        minimum_lookback=2,
        include_subfields=False,
        require_complete_authorships=True,
    )

    unfiltered_2020 = next(row for row in unfiltered if row["year"] == 2020)
    filtered_2020 = next(row for row in filtered if row["year"] == 2020)

    assert unfiltered_2020["n_papers_frame"] == 2
    assert unfiltered_2020["n_papers"] == 2
    assert unfiltered_2020["complete_authorship_paper_share"] == pytest.approx(0.5)
    assert filtered_2020["n_papers_frame"] == 2
    assert filtered_2020["n_papers"] == 1
