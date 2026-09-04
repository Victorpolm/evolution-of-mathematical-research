import json

from pipeline import comprehension, comprehension_score, taxonomy

POL_TO_VERDICT = {v: k for k, v in
                  comprehension_score.VERDICT_TO_POLARITY.items()
                  if k != "NO_AI_MENTION"}


def perfect_export():
    items = []
    for i, (key, _t, _c, exp) in enumerate(comprehension.VIGNETTES, 1):
        loc = exp.get("location") or exp["location_any_of"][0]
        imp = exp.get("impact") or exp["impact_any_of"][0]
        true_d = exp["polarity"] == "author_use"
        items.append({
            "arxiv_id": f"V{i:02d}", "version": 1,
            "verdict": POL_TO_VERDICT[exp["polarity"]],
            "categories": exp["categories"] if true_d else [],
            "impact": imp if true_d else "",
            "flags": exp["flags"] if true_d else [],
            "tools": "", "locations": [loc], "notes": "",
        })
    return {"project": "p1", "reviewer": "r1",
            "codebook_version": taxonomy.TAXONOMY_VERSION, "items": items}


def manifest():
    mapping = {f"V{i:02d}": k for i, (k, _t, _c, _e)
               in enumerate(comprehension.VIGNETTES, 1)}
    return {"project": "p1", "reviewers": {"r1": {"mapping": mapping}}}


def test_perfect_export_scores_all_axes():
    res = comprehension_score.score(perfect_export(), manifest())
    assert res["expected_ok"] == res["n_vignettes"]
    assert all(not r["expected_mismatches"] for r in res["rows"])


def test_polarity_flip_and_unfilled_location_are_distinguished():
    exp = perfect_export()
    by_id = {it["arxiv_id"]: it for it in exp["items"]}
    m = manifest()
    inv = {v: k for k, v in m["reviewers"]["r1"]["mapping"].items()}
    # R6 seam: topic_only graded as FALSE_POSITIVE must count as a polarity
    # miss, not slip through
    by_id[inv["intro_thanks"]]["verdict"] = "FALSE_POSITIVE"
    by_id[inv["intro_thanks"]]["locations"] = []
    # empty location on a non-disclosure verdict with "unknown" allowed
    # falls back to unknown and passes
    by_id[inv["plain_lean"]]["locations"] = []
    res = comprehension_score.score(exp, m)
    rows = {r["vignette"]: r for r in res["rows"]}
    assert "polarity" in rows["intro_thanks"]["expected_mismatches"]
    assert rows["intro_thanks"]["location_not_filled"]
    assert not rows["plain_lean"]["expected_mismatches"]


def test_codebook_mismatch_refused(tmp_path):
    import pytest
    exp = perfect_export()
    exp["codebook_version"] = "2.7"
    with pytest.raises(SystemExit):
        comprehension_score.score(exp, manifest())
