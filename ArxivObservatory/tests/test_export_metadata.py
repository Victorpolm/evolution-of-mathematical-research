"""Verify field allowlists and source preservation on synthetic data."""
import csv
import hashlib
import io
import json
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path
from analysis.export_metadata import export_metadata

class ExportMetadataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.database = self.directory / "observatory.db"
        with sqlite3.connect(self.database) as con:
            con.execute("""CREATE TABLE papers (
                arxiv_id TEXT PRIMARY KEY, title TEXT, authors TEXT,
                created TEXT, categories TEXT, primary_category TEXT,
                doi TEXT, abstract TEXT, comments TEXT, submitter TEXT)""")
            con.execute("INSERT INTO papers VALUES (?,?,?,?,?,?,?,?,?,?)",
                ("2401.00001", "Synthetic title", "A. Example, B. Example",
                 "2024-01-01", "math.AG math.NT", "math.AG", None,
                 "EXCLUDED_ABSTRACT", "EXCLUDED_COMMENT", "EXCLUDED_SUBMITTER"))
        self.openalex = self.directory / "authors.csv"
        self.openalex.write_text(
            "arxiv_id,author_id,raw_author_name,authorships_total,abstract,email\n"
            "2401.00001,A5000000001,A. Example,2,EXCLUDED_OA_TEXT,EXCLUDED_EMAIL\n",
            encoding="utf-8")

    def test_allowlists_read_only_and_raw_byline_preserved(self):
        db_before, csv_before = self.database.read_bytes(), self.openalex.read_bytes()
        output = self.directory / "metadata.zip"
        manifest = export_metadata(self.database, output, self.openalex)
        self.assertEqual(db_before, self.database.read_bytes())
        self.assertEqual(csv_before, self.openalex.read_bytes())
        self.assertFalse(manifest["analysis_ready"])
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(set(archive.namelist()), {
                "papers.csv", "openalex_authorships.csv", "input_manifest.json"})
            for name in archive.namelist():
                self.assertNotIn("EXCLUDED_", archive.read(name).decode())
            data = archive.read("papers.csv")
            papers = list(csv.DictReader(io.StringIO(data.decode())))
            self.assertEqual(papers[0]["authors"], "A. Example, B. Example")
            self.assertEqual(hashlib.sha256(data).hexdigest(),
                             manifest["files"]["papers.csv"]["sha256"])
            self.assertEqual(json.loads(archive.read("input_manifest.json")), manifest)

    def test_existing_output_is_preserved(self):
        output = self.directory / "metadata.zip"
        output.write_bytes(b"previous export")
        with self.assertRaisesRegex(ValueError, "already exists"):
            export_metadata(self.database, output)
        self.assertEqual(output.read_bytes(), b"previous export")

    def test_missing_csv_schema_does_not_create_success_archive(self):
        self.openalex.write_text("wrong_column\nvalue\n", encoding="utf-8")
        output = self.directory / "metadata.zip"
        with self.assertRaisesRegex(ValueError, "arxiv_id and author_id"):
            export_metadata(self.database, output, self.openalex)
        self.assertFalse(output.exists())

if __name__ == "__main__":
    unittest.main()
