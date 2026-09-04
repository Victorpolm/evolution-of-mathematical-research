from pipeline import classify, taxonomy


GOOD = {"polarity": "author_use", "tools": ["ChatGPT"], "models": ["GPT-5.5"],
        "categories": ["proof_generation", "writing_editing"],
        "epistemic_impact": "supportive", "locations": ["acknowledgments"],
        "confidence": 0.9, "quote": "We thank ChatGPT for help",
        "flags": {"catalytic": True}}
SNIPPET = "Acknowledgments. We thank  ChatGPT\nfor help with the writing."


def test_validate_good_label():
    clean, problems = classify.validate_label(dict(GOOD), SNIPPET)
    assert clean is not None and not problems
    assert clean["quote_grounded"] is True
    assert clean["flags"] == {"catalytic": True}


def test_validate_rejects_bad_polarity():
    clean, problems = classify.validate_label({"polarity": "yes"}, "x")
    assert clean is None and problems


def test_validate_clears_usage_fields_on_non_author():
    # all keys present (review-6: absent required fields are now rejected,
    # so this test supplies the full schema and checks only the clearing)
    lab = {"polarity": "topic_only", "categories": ["writing_editing"],
           "epistemic_impact": "supportive", "locations": ["body"],
           "confidence": 0.8, "quote": "", "tools": [], "models": [],
              "flags": {"catalytic": False}}
    clean, problems = classify.validate_label(lab, "x")
    assert clean is not None
    assert clean["categories"] == [] and clean["epistemic_impact"] == "not_applicable"
    assert problems  # the clearing is recorded, never silent


def test_validate_rejects_missing_quote():
    clean, problems = classify.validate_label(dict(GOOD, quote=""), SNIPPET)
    assert clean is None and any("missing quote" in p for p in problems)


def test_validate_rejects_unknown_category():
    clean, problems = classify.validate_label(
        dict(GOOD, categories=["writing_editing", "made_up"]), SNIPPET)
    assert clean is None and any("unknown categories" in p for p in problems)


def test_validate_rejects_bad_enums_and_ranges():
    assert classify.validate_label(dict(GOOD, location="nowhere"), SNIPPET)[0] is None
    assert classify.validate_label(dict(GOOD, confidence=5), SNIPPET)[0] is None
    assert classify.validate_label(dict(GOOD, epistemic_impact="huge"), SNIPPET)[0] is None
    assert classify.validate_label(dict(GOOD, extra_field=1), SNIPPET)[0] is None
    assert classify.validate_label(dict(GOOD, flags=["catalytic"]), SNIPPET)[0] is None
    assert classify.validate_label(dict(GOOD, flags={"bogus": True}), SNIPPET)[0] is None


def test_validate_r5_and_cross_field_invariants():
    """Taxonomy v2.2 R5: zero_contribution is legal for author_use but only
    without catalytic; catalytic requires >= supportive (review-7 P0-1)."""
    ok, _ = classify.validate_label(
        dict(GOOD, epistemic_impact="zero_contribution",
             flags={"catalytic": False}), SNIPPET)
    assert ok is not None and ok["epistemic_impact"] == "zero_contribution"
    assert classify.validate_label(
        dict(GOOD, epistemic_impact="zero_contribution",
             flags={"catalytic": True}), SNIPPET)[0] is None
    assert classify.validate_label(
        dict(GOOD, epistemic_impact="cosmetic",
             flags={"catalytic": True}), SNIPPET)[0] is None  # R2
    assert classify.validate_label(
        dict(GOOD, epistemic_impact="not_applicable"), SNIPPET)[0] is None
    ok2, _ = classify.validate_label(
        dict(GOOD, epistemic_impact="undetermined",
             flags={"catalytic": False}), SNIPPET)
    assert ok2 is not None
    # v2.8: catalytic is the only flag; non-author labels carry it False
    lab = dict(GOOD, polarity="topic_only", categories=[], tools=[],
               models=[], epistemic_impact="not_applicable", quote="",
               flags={"catalytic": False})
    ok3, _ = classify.validate_label(lab, SNIPPET)
    assert ok3 is not None and ok3["flags"] == {"catalytic": False}


def test_validate_rejects_string_flag_values():
    # bool("false") is True — a stringly-typed flag must be rejected (review-3)
    clean, problems = classify.validate_label(
        dict(GOOD, flags={"catalytic": "false"}), SNIPPET)
    assert clean is None and any("JSON booleans" in p for p in problems)


def test_quote_grounding_whitespace_insensitive():
    assert classify.ground_quote("We thank ChatGPT for help", SNIPPET)
    assert not classify.ground_quote("invented evidence", SNIPPET)


def test_prompt_header_embeds_taxonomy():
    h = classify.build_prompt_header()
    for cat in taxonomy.CATEGORIES:
        assert cat in h
    for pol in taxonomy.POLARITIES:
        assert pol in h
    assert taxonomy.TAXONOMY_VERSION in h


def test_isolated_batches_never_mix_papers():
    snippets = [{"arxiv_id": f"2607.0000{i % 3}", "n": i} for i in range(10)]
    for b in classify.make_batches(snippets, isolate=True):
        assert len({s["arxiv_id"] for s in b}) == 1


def test_extract_json_strips_fences():
    assert classify.extract_json('```json\n[{"id": 0}]\n```') == [{"id": 0}]


def test_merge_snippets_scoped_to_run(fixture_con):
    sn = classify.merge_snippets(fixture_con, ["scan-t"])
    assert {s["arxiv_id"] for s in sn} == {"2607.00001", "2607.00002"}
    classify.finalize_snippets(sn, "psha", "m1", False)
    h1 = sn[0]["input_hash"]
    classify.finalize_snippets(sn, "psha", "OTHER-MODEL", False)
    assert sn[0]["input_hash"] != h1  # protocol identity covers the model
