import math
import unittest

from analysis.contributor_populations import analyze, output_counts, top_decile


def paper(month, names, ids=None, reasons=None):
    return {"month": month, "names": names, "ids": ids or names,
            "slots": len(names), "reasons": reasons or []}


class ContributorPopulationTests(unittest.TestCase):
    def test_one_paper_three_contributors_explains_fraction_below_one(self):
        d = analyze([paper("2020-01", ["a", "b", "c"])], "2020-01", "2020-12")
        r = d["annual"][0]["names"]
        self.assertEqual(r["papers_per_active_contributor"], 1 / 3)
        self.assertEqual(r["coauthored_papers_per_active_contributor"], 1)
        self.assertAlmostEqual(r["fractional"]["share"], 0.1)

    def test_full_population_is_union_and_windows_are_recomputed(self):
        papers = [paper("2020-01", ["a", "b"]), paper("2020-12", ["a"]), paper("2021-01", ["c"])]
        d = analyze(papers, "2020-01", "2021-12")
        self.assertEqual(d["study"]["names"]["authors"], 3)
        self.assertEqual(d["annual"][0]["names"]["authors"], 2)
        self.assertEqual(d["annual"][0]["names"]["papers_per_active_contributor"], 1)
        self.assertEqual(d["annual"][0]["names"]["papers_per_study_contributor"], 2 / 3)
        self.assertEqual(d["rolling12"][1]["names"]["authors"], 2)  # Feb 2020–Jan 2021: a, c
        self.assertEqual(d["study"]["names"]["papers_per_active_contributor"], 1)

    def test_duplicate_name_slots_keep_fractional_credit_but_one_full_paper(self):
        papers = [paper("2020-01", ["same", "same", "other"], ["id1", "id2", "id3"])]
        frac, full = output_counts(papers, "names")
        self.assertEqual(full["same"], 1)
        self.assertAlmostEqual(frac["same"], 2 / 3)
        self.assertAlmostEqual(math.fsum(frac.values()), 1)
        self.assertEqual(sum(full.values()), 2)

    def test_boundary_ties_receive_equal_weights(self):
        d = top_decile([10, 10] + [1] * 8)
        self.assertEqual(d["group_mass"], 1)
        self.assertEqual(d["boundary_ties"], 2)
        self.assertEqual(d["boundary_weight"], 0.5)
        self.assertEqual(d["top_output"], 10)
        self.assertAlmostEqual(d["share"], 10 / 28)
        self.assertAlmostEqual(d["mean_ratio"], 5)

    def test_noninteger_decile_mass_no_ceiling_bias(self):
        d = top_decile([2] + [1] * 10)
        self.assertEqual(d["group_mass"], 1.1)
        self.assertEqual(d["strictly_above"], 1)
        self.assertAlmostEqual(d["boundary_weight"], .01)
        self.assertAlmostEqual(d["top_output"], 2.1)

    def test_uniform_and_float_ties(self):
        d = top_decile([1 / 3, .1 + .1 + .1 + 1 / 30, 1 / 3])
        self.assertEqual(d["boundary_ties"], 3)
        self.assertAlmostEqual(d["share"], .1)
        self.assertAlmostEqual(d["mean_ratio"], 1)

    def test_excluded_papers_do_not_enter_either_denominator(self):
        d = analyze([paper("2020-01", ["a"]), paper("2020-01", ["b"], reasons=["missing_id"])], "2020-01", "2020-12")
        self.assertEqual(d["study"]["papers"], 1)
        self.assertEqual(d["study"]["names"]["authors"], 1)
        self.assertIsNone(d["monthly"][1]["names"]["papers_per_active_contributor"])
        self.assertEqual(d["monthly"][1]["names"]["papers_per_study_contributor"], 0)
        self.assertIsNone(d["monthly"][1]["names"]["fractional"]["share"])

    def test_invalid_scores_fail(self):
        for values in ([0], [-1], [float("nan")], [float("inf")]):
            with self.assertRaises(ValueError):
                top_decile(values)


if __name__ == "__main__":
    unittest.main()
