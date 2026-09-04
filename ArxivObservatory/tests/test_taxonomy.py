"""Drift check: TAXONOMY.md (human doc) and pipeline/taxonomy.py (machine
copy) must describe the same vocabulary and version."""

from pathlib import Path

from pipeline import taxonomy

DOC = (Path(__file__).resolve().parent.parent / "TAXONOMY.md").read_text()


def test_version_in_sync():
    assert f"v{taxonomy.TAXONOMY_VERSION}" in DOC.splitlines()[0]


def test_all_categories_documented():
    for cat in taxonomy.CATEGORIES:
        assert f"| {cat} |" in DOC, f"category {cat} missing from TAXONOMY.md"


def test_all_polarities_documented():
    for pol in taxonomy.POLARITIES:
        assert f"| {pol} |" in DOC, f"polarity {pol} missing from TAXONOMY.md"


def test_impacts_and_flags_documented():
    for imp in taxonomy.IMPACTS:
        if imp != "none":
            assert imp in DOC
    for flag in taxonomy.FLAGS:
        assert flag in DOC


def test_locations_documented():
    for loc in taxonomy.LOCATIONS:
        assert loc in DOC


def test_decision_rules_present_in_prompt():
    text = taxonomy.prompt_definitions()
    assert "R1" in text and "R2" in text and "catalytic" in text
