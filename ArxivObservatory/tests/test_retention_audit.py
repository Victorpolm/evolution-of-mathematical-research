import math

from analysis.retention_audit import (
    orcid_opportunity, partial_credit, reference_cohort, standardized_retention, summarize,
)


def paper(year, number, ids, reasons=None, orcids=None):
    return {"month": f"{year}-01", "work_id": f"W{year}{number}", "ids": ids,
            "names": [f"Name {i}" for i in range(len(ids))], "slots": len(ids),
            "reasons": reasons if reasons is not None else (["missing_or_placeholder_author_id"] if None in ids else []),
            "subfield": "Fixture field", "raw_orcids": orcids or [None]*len(ids)}


def test_partial_credit_retains_missing_share_and_unusable_paper():
    rows = [paper(2024, 1, [f"A{i}" for i in range(6)]+[None]*4),
            paper(2024, 2, ["Z"], reasons=["truncated_or_100plus_byline"])]
    r = partial_credit(rows)
    assert math.isclose(r["allocated_credit_to_ids"], .6)
    assert math.isclose(r["unallocated_missing_id_credit"], .4)
    assert r["unallocated_unusable_byline_credit"] == 1
    assert math.isclose(r["allocated_credit_to_ids"]+r["total_unallocated_credit"], 2)
    assert r["identified_id_keys"] == 6
    assert math.isclose(r["mean_allocated_credit_per_id"], .1)
    assert math.isclose(r["usable_papers_per_identified_id"], 1/6)


def test_all_missing_byline_has_no_synthetic_author():
    r = partial_credit([paper(2024, 1, [None, None])])
    assert r["identified_id_keys"] == 0
    assert r["mean_allocated_credit_per_id"] is None
    assert r["allocated_credit_to_ids"] == 0
    assert r["unallocated_missing_id_credit"] == 1
    assert r["ids_full_distribution"] is None


def test_coverage_partition_has_explicit_precedence():
    rows = [paper(2024, 1, ["A"]), paper(2024, 2, [None]),
            paper(2024, 3, ["B", None]),
            paper(2024, 4, ["C"], reasons=["possible_group_name"]),
            paper(2024, 5, [None], reasons=["possible_group_name", "missing_or_placeholder_author_id"])]
    r = summarize(rows)
    assert r["states"] == {"paired": 1, "all_ids_missing": 2, "some_ids_missing": 1, "other_byline_exclusion": 1}
    assert r["retention"] == .2


def test_orcid_opportunity_separates_within_paper_and_across_papers():
    rows = [paper(2024, 1, ["A", "B"], orcids=["o1", "o1"]),
            paper(2024, 2, ["C"], orcids=["o2"]),
            paper(2024, 3, ["D"], orcids=["o2"]),
            paper(2024, 4, ["E"], orcids=["o3"])]
    r = orcid_opportunity(rows)
    assert r["distinct_source_orcids"] == 3
    assert r["orcids_with_multiple_ids"] == 2
    assert r["orcids_on_multiple_papers"] == 1
    assert r["multiple_ids_and_multiple_papers"] == 1
    assert r["multiple_id_orcids_on_only_one_paper"] == 1


def test_common_stratum_standardization_removes_pure_composition_change():
    rows = [paper(2024, 1, ["A"]), paper(2024, 2, ["B"]),
            paper(2024, 3, [None, None]), paper(2024, 4, [None, None]),
            paper(2025, 1, ["C"]), paper(2025, 2, [None, None]),
            paper(2025, 3, [None, None]), paper(2025, 4, [None, None])]
    a, b = standardized_retention(rows)["annual"]
    assert a["raw_retention_usable"] == .5 and b["raw_retention_usable"] == .25
    assert a["standardized_retention"] == b["standardized_retention"] == 3/8


def test_reference_cohort_keeps_zero_followup_keys():
    before = [paper(2024, 1, ["A"]), paper(2024, 2, ["B"])]
    after = [paper(2025, 1, ["A"]), paper(2025, 2, ["A"]), paper(2025, 3, ["C"])]
    r = reference_cohort(before, after, "ids")
    assert r["zero_observed_followup_keys"] == 1
    assert r["appearing_observed_keys"] == 1
    assert math.isclose(r["followup_full_distribution_including_zeros"]["gini"], .5)
    assert r["followup_continuing_keys_distribution"]["gini"] == 0
