import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from analysis.historical_participation import add_linkage_coverage, decomposition, months, read_compact, series
from analysis.openalex_names import prepare


def work(wid, aid, date, names=("Alice",), ids=("A1",)):
    return {"id": "https://openalex.org/" + wid, "doi": None,
            "publication_date": date, "publication_year": int(date[:4]),
            "indexed_in": ["arxiv"], "primary_topic": {"field": {"id": "https://openalex.org/fields/26"}},
            "locations": [{"landing_page_url": "https://arxiv.org/abs/" + aid}],
            "authorships": [{"raw_author_name": n, "author": {"id": i}} for n, i in zip(names, ids)]}


class HistoricalChecks(unittest.TestCase):
    def test_window_unions_and_fractional_identity(self):
        raw = [work("W1", "1001.00001", "2010-01-01", ("Alice", "Bob"), ("A1", "A2")),
               work("W2", "1002.00001", "2010-02-01", ("Alice", "Carol"), ("A1", "A3"))]
        papers, _ = prepare(raw, "2010-01", "2010-12")
        data = series(papers, "2010-01", "2010-12")
        year = data["annual"][0]
        self.assertEqual(year["ids"]["authors"], 3)  # Not 2+2 monthly authors.
        self.assertAlmostEqual(year["ids"]["papers_per_author"], 2/3)
        self.assertAlmostEqual(year["ids"]["fractional_credit_sum"], 2)
        self.assertEqual(data["rolling12"][0]["ids"], year["ids"])
        self.assertIsNone(data["monthly"][2]["ids"]["papers_per_author"])

    def test_names_and_ids_are_not_ordered_and_use_same_papers(self):
        raw = [work("W1", "1001.00001", "2010-01-01", ("Same Name", "Same Name"), ("A1", "A2")),
               work("W2", "1101.00001", "2011-01-01", ("Alice",), ("A3",)),
               work("W3", "1102.00001", "2011-02-01", ("A. Alice",), ("A3",)),
               work("W4", "1103.00001", "2011-03-01", ("Missing ID",), (None,))]
        papers, _ = prepare(raw, "2010-01", "2011-12")
        a, b = series(papers, "2010-01", "2011-12")["annual"]
        self.assertLess(a["names"]["authors"], a["ids"]["authors"])
        self.assertGreater(b["names"]["authors"], b["ids"]["authors"])
        self.assertEqual(b["coverage"]["linked_papers"], 3)
        self.assertEqual(b["papers"], 2)
        self.assertEqual(b["names"]["fractional_credit_sum"], b["ids"]["fractional_credit_sum"])
        parts = decomposition(a, b)
        self.assertAlmostEqual(parts["papers_log_change"], parts["linked_papers_log_change"] + parts["retention_log_change"])

    def make_snapshot(self, root):
        (root / "pages").mkdir()
        partitions = []
        for month, records in [
            ("2010-01", [work("W1", "1001.00001", "2010-01-01"), work("W3", "1001.00003", "2010-01-02")]),
            ("2010-02", [work("W2", "1001.00001", "2010-02-01")]),
        ]:
            target = root / "pages" / (month + ".json.gz")
            target.write_bytes(gzip.compress(json.dumps({"meta": {"count":len(records)}, "results":records}).encode()))
            partitions.append({"publication_month":month, "pagination_complete":True, "retrieved":len(records),
                               "initial_count":len(records), "pages":[{"file":target.name, "works":len(records),
                               "sha256":hashlib.sha256(target.read_bytes()).hexdigest()}]})
        (root / "acquisition.json").write_text(json.dumps({"complete":True, "partitions":partitions}))

    def test_arxiv_collision_across_pages_and_partitions_excludes_whole_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_snapshot(root)
            papers, _, diagnostic, flow = read_compact(root, "2010-01", "2010-12", months("2010-01", "2010-02"))
            self.assertEqual([p["arxiv_id"] for p in papers], ["1001.00003"])
            self.assertEqual(diagnostic["works_in_duplicate_arxiv_groups"], 2)
            self.assertEqual(diagnostic["candidate_works"], 3)
            data = {"upload_window":["2010-01", "2010-12"], "flow":flow,
                    **series(papers, "2010-01", "2010-12")}
            add_linkage_coverage(data)
            for row in (data["annual"][0], data["monthly"][0], data["rolling12"][0]):
                self.assertEqual(row["coverage"]["mapped_arxiv_ids"], 2)
                self.assertEqual(row["coverage"]["ambiguous_arxiv_groups"], 1)
                self.assertEqual(row["coverage"]["retention"], 1)
                self.assertEqual(row["coverage"]["overall_retention"], .5)

    def test_incomplete_scope_and_corruption_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_snapshot(root)
            with self.assertRaisesRegex(ValueError, "partitions"):
                read_compact(root, "2010-01", "2010-12", months("2010-01", "2010-03"))
            target = next((root / "pages").glob("*.gz"))
            target.write_bytes(b"damaged")
            with self.assertRaisesRegex(ValueError, "hash"):
                read_compact(root, "2010-01", "2010-12")
            path = root / "acquisition.json"
            data = json.loads(path.read_text()); data["complete"] = False
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                read_compact(root, "2010-01", "2010-12")

    def test_only_full_calendar_years_and_full_rolling_windows(self):
        data = series([], "2010-02", "2011-12")
        self.assertEqual([r["period"] for r in data["annual"]], ["2011"])
        self.assertEqual(len(data["rolling12"]), 12)
        self.assertEqual(data["rolling12"][0]["period"], "2011-01")
        self.assertFalse(decomposition(data["annual"][0], data["annual"][0])["available"])


if __name__ == "__main__":
    unittest.main()
