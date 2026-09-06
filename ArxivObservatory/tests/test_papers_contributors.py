import csv
import tempfile
import unittest
from pathlib import Path

from analysis.papers_contributors import analyze, parse_id


class PapersContributorsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def manifest(self, ids):
        path = self.root / "manifest.txt"
        path.write_text("\n".join(ids) + "\n")
        return path

    def authorships(self, rows):
        path = self.root / "paper_authors.csv"
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["work_id", "arxiv_id", "publication_year", "publication_month",
                             "author_id", "primary_subfield", "authorships_total", "authorships_missing_id"])
            writer.writerows(rows)
        return path

    def run_analysis(self, ids, **kwargs):
        return analyze(self.manifest(ids), start_month="2024-01", end_month="2024-12",
                       source={"label": "synthetic fixture"}, **kwargs)

    def test_versions_deduplicated_and_missing_contributors_remain_null(self):
        result = self.run_analysis(["2401.00001", "2401.00001v2", "2402.00002"])
        self.assertEqual(result["annual"][0]["papers"], 2)
        self.assertIsNone(result["annual"][0]["contributors"])
        self.assertIsNone(result["annual"][0]["papersPerContributor"])
        self.assertEqual(result["diagnostics"]["duplicateManifestLines"], 1)

    def test_rolling_authors_are_union_not_sum_and_same_papers_are_used(self):
        rows = [
            ("w1", "2401.00001", 2024, 1, "A", "math.AG", 2, 0),
            ("w1", "2401.00001", 2024, 1, "B", "math.AG", 2, 0),
            ("w2", "2402.00002", 2024, 2, "A", "math.AG", 1, 0),
            ("w3", "2402.00003", 2024, 2, "C", "math.AG", 2, 1),
        ]
        result = self.run_analysis(["2401.00001", "2402.00002", "2402.00003"],
                                   authorships_path=self.authorships(rows))
        annual = result["annual"][0]
        self.assertEqual((annual["framePapers"], annual["papers"], annual["contributors"]), (3, 2, 2))
        self.assertEqual(annual["papersPerContributor"], 1)
        self.assertEqual(annual["fullCountPerContributor"], 1.5)
        self.assertEqual(result["rolling12"][0]["contributors"], 2)
        self.assertEqual(sum(r["contributors"] for r in result["monthly"]), 3)
        self.assertEqual(annual["completePaperShare"], 2 / 3)

    def test_partial_years_are_omitted_and_outside_window_reported(self):
        result = analyze(self.manifest(["2308.00001", "2401.00002", "2501.00003", "2502.00004"]),
                         start_month="2023-08", end_month="2025-01", source={})
        self.assertEqual([r["period"] for r in result["annual"]], ["2024"])
        self.assertEqual(result["diagnostics"]["incompleteCalendarYearsOmitted"], [2023, 2025])
        self.assertEqual(result["diagnostics"]["papersOutsideWindow"], 1)

    def test_declared_complete_but_short_author_list_is_excluded(self):
        rows = [("w1", "2401.00001", 2024, 1, "A", "math.AG", 2, 0)]
        result = self.run_analysis(["2401.00001"], authorships_path=self.authorships(rows))
        self.assertEqual(result["annual"][0]["papers"], 0)
        self.assertEqual(result["diagnostics"]["authorships"]["excludedPaperReasons"],
                         {"identified_count_disagrees_with_total": 1})

    def test_duplicate_work_mapping_is_rejected(self):
        rows = [(w, "2401.00001", 2024, 1, "A", "math.AG", 1, 0) for w in ["w1", "w2"]]
        with self.assertRaisesRegex(ValueError, "multiple work IDs"):
            self.run_analysis(["2401.00001"], authorships_path=self.authorships(rows))

    def test_date_disagreement_and_bad_source_hash_are_rejected(self):
        rows = [("w1", "2401.00001", 2023, 1, "A", "math.AG", 1, 0)]
        with self.assertRaisesRegex(ValueError, "date disagrees"):
            self.run_analysis(["2401.00001"], authorships_path=self.authorships(rows))
        with self.assertRaisesRegex(ValueError, "Git blob SHA"):
            analyze(self.manifest(["2401.00001"]), start_month="2024-01", end_month="2024-12",
                    source={"blobSha": "incorrect"})
        with self.assertRaises(ValueError):
            parse_id("2413.00001")


if __name__ == "__main__":
    unittest.main()
