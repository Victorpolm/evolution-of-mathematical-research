"""Export existing metadata for offline participation analysis.

Reads SQLite in read-only mode. Uses an explicit allowlist: no abstracts,
paper text, excerpts or classification labels. Makes no network requests.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sqlite3
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

PAPER_FIELDS = (
    "arxiv_id", "title", "authors", "created", "categories",
    "primary_category", "doi", "msc_class", "latest_version",
    "oai_datestamp", "harvested_at",
)
OPENALEX_FIELDS = (
    "work_id", "arxiv_id", "publication_year", "publication_month",
    "author_id", "primary_subfield", "authorships_total",
    "authorships_missing_id", "authorships_truncated",
    "raw_author_name", "author_name", "arxiv_author_position",
    "author_position", "authorship_position", "author_index",
    "raw_orcid", "orcid", "alignment_status", "source_snapshot", "retrieved_at",
)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def export_metadata(database: Path, output: Path, openalex_csv: Path | None = None) -> dict:
    database, output = Path(database).resolve(), Path(output).resolve()
    openalex_csv = Path(openalex_csv).resolve() if openalex_csv else None
    if not database.is_file():
        raise ValueError("database does not exist")
    if openalex_csv is not None and not openalex_csv.is_file():
        raise ValueError("OpenAlex CSV does not exist")
    if output.exists():
        raise ValueError("output already exists; choose a new filename")
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_database_name": database.name,
        "source_database_read_only": True,
        "scope": "all existing papers; no history newly acquired",
        "paper_text_included": False,
        "author_list_definition": "raw byline from the existing metadata snapshot",
        "analysis_ready": False,
        "next_validation": ["audit corpus, dates and coverage",
                            "parse raw bylines and preserve author slots",
                            "align arXiv author slots with OpenAlex IDs"],
        "files": {},
    }
    with tempfile.TemporaryDirectory(prefix="observatory-metadata-") as directory:
        staging = Path(directory)
        con = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
        try:
            con.execute("PRAGMA query_only=ON")
            con.execute("BEGIN")
            columns = {row[1] for row in con.execute("PRAGMA table_info(papers)")}
            missing = {"arxiv_id", "authors", "created", "categories",
                       "primary_category"} - columns
            if missing:
                raise ValueError("missing required papers columns: " + ", ".join(sorted(missing)))
            fields = [name for name in PAPER_FIELDS if name in columns]
            rows, categories, missing_values = 0, Counter(), Counter()
            earliest = latest = None
            paper_csv = staging / "papers.csv"
            with paper_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(fields)
                query = "SELECT " + ",".join(fields) + " FROM papers ORDER BY arxiv_id"
                for values in con.execute(query):
                    writer.writerow(values)
                    row = dict(zip(fields, values))
                    rows += 1
                    categories[row.get("primary_category") or "(missing)"] += 1
                    for field in ("authors", "created", "categories", "primary_category"):
                        if not row.get(field):
                            missing_values[field] += 1
                    date = row.get("created")
                    if date:
                        earliest = min(earliest, date) if earliest else date
                        latest = max(latest, date) if latest else date
            if not rows:
                raise ValueError("papers table is empty")
            manifest["files"]["papers.csv"] = {
                "rows": rows, "columns": fields, "sha256": sha256(paper_csv),
            }
            manifest["metadata_inventory"] = {
                "recorded_date_min": earliest, "recorded_date_max": latest,
                "primary_categories": dict(sorted(categories.items())),
                "missing_fields": dict(sorted(missing_values.items())),
                "date_values_validated": False,
            }
        finally:
            con.close()
        if openalex_csv is not None:
            target = staging / "openalex_authorships.csv"
            with openalex_csv.open(newline="", encoding="utf-8-sig") as source:
                reader = csv.DictReader(source)
                available = set(reader.fieldnames or [])
                if {"arxiv_id", "author_id"} - available:
                    raise ValueError("OpenAlex CSV needs arxiv_id and author_id columns")
                if len(reader.fieldnames or []) != len(available):
                    raise ValueError("OpenAlex CSV has duplicate column names")
                fields = [name for name in OPENALEX_FIELDS if name in available]
                rows = 0
                with target.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=fields)
                    writer.writeheader()
                    for row in reader:
                        if None in row:
                            raise ValueError("OpenAlex CSV row has extra fields")
                        writer.writerow({field: row.get(field, "") for field in fields})
                        rows += 1
            manifest["files"]["openalex_authorships.csv"] = {
                "rows": rows, "columns": fields, "sha256": sha256(target),
                "source_sha256": sha256(openalex_csv),
            }
        else:
            manifest["missing_input"] = "existing OpenAlex authorship CSV"
        (staging / "input_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
        )
        with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(staging.iterdir()):
                archive.write(path, arcname=path.name)
    return manifest

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--openalex-csv", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = export_metadata(args.database, args.output, args.openalex_csv)
    print(json.dumps({
        "output": str(args.output),
        "paper_rows": manifest["files"]["papers.csv"]["rows"],
        "openalex_rows": manifest["files"].get("openalex_authorships.csv", {}).get("rows"),
        "analysis_ready": False,
        "next_step": "Supply this metadata archive for parsing, alignment and analysis.",
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
