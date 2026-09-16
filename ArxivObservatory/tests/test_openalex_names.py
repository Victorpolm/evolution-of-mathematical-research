import math
from analysis.openalex_names import (
    arxiv_ids, author_key, credits, crosswalk_diagnostics, metrics, name_key, prepare, top_share, transition,
)


def work(wid, arxiv, slots, **extra):
    return {"id": f"https://openalex.org/W{wid}", "publication_year": 2026,
            "locations": [{"landing_page_url": f"https://arxiv.org/abs/{arxiv}v2"}],
            "authorships": [{"author": {"id": aid}, "raw_author_name": name} for name, aid in slots], **extra}


def test_same_papers_merging_and_name_collision_preserve_slots():
    rows, _ = prepare([
        work(1, "2401.00001", [("A. Example", "A1"), ("Li Wei", "A2"), ("Li Wei", "A3")]),
        work(2, "2501.00001", [("Alice Example", "A1")]),
    ])
    assert not any(p["reasons"] for p in rows)
    result = metrics(rows)
    assert result["authorship_slots"] == 4
    assert result["papers"] == 2
    assert result["names"]["authors"] == result["ids"]["authors"] == 3
    f, full = credits(rows[:1], "names")
    assert math.isclose(f["Li Wei"], 2/3)
    assert full["Li Wei"] == 2
    assert metrics(rows[:1])["names"]["authors"] == 2
    assert metrics(rows[:1])["ids"]["authors"] == 3


def test_normalization_does_not_guess_person_identity():
    assert name_key("  Jose\u0301\tDupont  ") == "José Dupont"
    assert name_key("J. Dupont") != name_key("José Dupont")
    assert name_key("j. Dupont") != name_key("J. Dupont")
    assert author_key("https://openalex.org/A9999999999") is None
    assert author_key("A5317838346") is None
    assert author_key(None) is None


def test_no_display_name_fallback_and_repeated_ids_excluded():
    missing = work(1, "2401.00001", [(None, "A1")])
    missing["authorships"][0]["author"]["display_name"] = "Resolved display name"
    duplicate = work(2, "2402.00001", [("A. Example", "A2"), ("Alice Example", "A2")])
    rows, _ = prepare([missing, duplicate])
    assert "missing_raw_name" in rows[0]["reasons"]
    assert "repeated_id_in_byline" in rows[1]["reasons"]


def test_arxiv_version_dates_and_duplicate_work_mapping():
    p = work(1, "2412.12345", [("Alice Example", "A1")])
    assert arxiv_ids(p) == {"2412.12345"}
    rows, _ = prepare([p])
    assert rows[0]["month"] == "2024-12"
    rows, diagnostic = prepare([p, {**p, "id": "https://openalex.org/W2"}])
    assert not rows
    assert diagnostic["duplicate_arxiv_id_groups"] == 1
    assert not arxiv_ids({"locations": [{"landing_page_url": "https://arxiv.org.example.com/abs/2412.12345"}]})


def test_transition_is_exact_under_each_definition():
    rows, _ = prepare([
        work(1, "2401.00001", [("A. Example", "A1"), ("Departing", "A2")]),
        work(2, "2501.00001", [("Alice Example", "A1"), ("Arriving", "A3")]),
        work(3, "2502.00001", [("Alice Example", "A1")]),
    ])
    for method in ("names", "ids"):
        result = transition(rows[:1], rows[1:], method)
        assert result["paper_change"] == 1
        assert abs(result["identity_residual"]) < 1e-12
    assert transition(rows[:1], rows[1:], "names")["continuing_keys"] == 0
    assert transition(rows[:1], rows[1:], "ids")["continuing_keys"] == 1


def test_fractional_rank_boundary_and_missing_id_paired_exclusion():
    assert math.isclose(top_share([1, 1, 1], .1), .1)
    rows, _ = prepare([work(1, "2401.00001", [("A", "A1"), ("B", None)])])
    assert rows[0]["reasons"] == ["missing_or_placeholder_author_id"]
    assert rows[0]["slots"] == 2


def test_mapping_multiplicity_is_window_specific_and_slot_weighted():
    rows, _ = prepare([
        work(1, "2401.00001", [("Shared", "A1"), ("Shared", "A2")]),
        work(2, "2402.00001", [("Shared", "A1"), ("Unique", "A3")]),
        work(3, "2501.00001", [("Variant", "A1"), ("Shared", "A2")]),
    ])
    rows[0]["raw_orcids"] = ["0000-0002-1825-0097", None]
    rows[2]["raw_orcids"] = [None, "0000-0002-1825-0097"]
    first = crosswalk_diagnostics(rows[:2])
    last = crosswalk_diagnostics(rows[2:])
    pooled = crosswalk_diagnostics(rows)
    assert first["distinct_ids_per_name_frequency"] == {1: 1, 2: 1}
    assert first["share_of_slots_in_names_with_multiple_ids"] == 3/4
    assert first["raw_orcid_slot_share"] == 1/4
    assert last["names_associated_with_multiple_ids"] == 0
    assert first["ids_associated_with_multiple_names"] == last["ids_associated_with_multiple_names"] == 0
    assert pooled["ids_associated_with_multiple_names"] == 1
    assert pooled["share_of_slots_in_ids_with_multiple_names"] == 3/6
    assert pooled["raw_orcids_associated_with_multiple_ids"] == 1
    assert first["raw_orcids_associated_with_multiple_ids"] == last["raw_orcids_associated_with_multiple_ids"] == 0
    assert crosswalk_diagnostics([])["raw_orcid_slot_share"] is None
