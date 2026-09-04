"""OAI-PMH metadata harvest (arXivRaw format, set=math).

Politeness: one request per POLITE_DELAY seconds, honors 503 Retry-After,
identifies itself with a contact address. Raw pages are archived gzipped under
corpus/oai/ so any parse can be redone offline; parsing upserts into the DB.

Usage:
    python3 -m pipeline.harvest --from 2026-05-01           # harvest + parse
    python3 -m pipeline.harvest --reparse                   # reparse archived pages only
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import gzip
import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

from . import db

OAI_URL = "https://oaipmh.arxiv.org/oai"
USER_AGENT = "ArxivObservatory/0.1 (research pilot; contact: jo314schmitt@gmail.com)"
POLITE_DELAY = 4.0
NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "raw": "http://arxiv.org/OAI/arXivRaw/",
}
OAI_DIR = db.CORPUS_DIR / "oai"
STATE_PATH = OAI_DIR / "state.json"


def _text(el: ET.Element | None) -> str | None:
    if el is None or el.text is None:
        return None
    return " ".join(el.text.split()) or None


def parse_page(xml_bytes: bytes) -> tuple[list[dict], str | None]:
    """Return (records, resumption_token)."""
    root = ET.fromstring(xml_bytes)
    err = root.find("oai:error", NS)
    if err is not None:
        if err.get("code") == "noRecordsMatch":
            return [], None
        raise RuntimeError(f"OAI error {err.get('code')}: {err.text}")
    records = []
    for rec in root.iterfind(".//oai:record", NS):
        header = rec.find("oai:header", NS)
        if header is not None and header.get("status") == "deleted":
            continue
        meta = rec.find(".//raw:arXivRaw", NS)
        if meta is None:
            continue
        versions = []
        for v in meta.iterfind("raw:version", NS):
            vnum = int((v.get("version") or "v0").lstrip("v") or 0)
            vdate = _text(v.find("raw:date", NS))
            vdt = None
            if vdate:
                try:
                    vdt = email.utils.parsedate_to_datetime(vdate).isoformat()
                except (TypeError, ValueError):
                    vdt = vdate
            versions.append({"version": vnum, "date": vdt,
                             "size": _text(v.find("raw:size", NS))})
        cats = _text(meta.find("raw:categories", NS)) or ""
        created = None
        if versions:
            v1 = min(versions, key=lambda v: v["version"])
            if v1["date"]:
                created = v1["date"][:10]
        records.append({
            "arxiv_id": _text(meta.find("raw:id", NS)),
            "title": _text(meta.find("raw:title", NS)),
            "authors": _text(meta.find("raw:authors", NS)),
            # review-8 E4: the submitter's personal name had no consumer in
            # this pipeline — data minimization: never store it
            "submitter": None,
            "abstract": _text(meta.find("raw:abstract", NS)),
            "comments": _text(meta.find("raw:comments", NS)),
            "categories": cats,
            "primary_category": cats.split()[0] if cats else None,
            "msc_class": _text(meta.find("raw:msc-class", NS)),
            "journal_ref": _text(meta.find("raw:journal-ref", NS)),
            "doi": _text(meta.find("raw:doi", NS)),
            "license": _text(meta.find("raw:license", NS)),
            "created": created,
            "latest_version": max((v["version"] for v in versions), default=None),
            "oai_datestamp": _text(header.find("oai:datestamp", NS)) if header is not None else None,
            "versions": versions,
        })
    tok = root.find(".//oai:resumptionToken", NS)
    token = tok.text.strip() if tok is not None and tok.text and tok.text.strip() else None
    return records, token


def upsert(con, records: list[dict]) -> None:
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with con:
        for r in records:
            versions = r.pop("versions")
            r["harvested_at"] = now
            cols = ",".join(r)
            con.execute(
                f"INSERT OR REPLACE INTO papers ({cols}) VALUES ({','.join(':'+c for c in r)})", r)
            con.executemany(
                "INSERT OR REPLACE INTO versions (arxiv_id, version, date, size) VALUES (?,?,?,?)",
                [(r["arxiv_id"], v["version"], v["date"], v["size"]) for v in versions])


def fetch_page(session, params: dict) -> bytes:
    for attempt in range(8):
        try:
            resp = session.get(OAI_URL, params=params, timeout=300)
        except requests.RequestException as exc:
            wait = 20 * (attempt + 1)
            print(f"  {type(exc).__name__}, retrying in {wait}s", flush=True)
            time.sleep(wait)
            continue
        if resp.status_code == 503:
            try:
                wait = int(resp.headers.get("Retry-After", "30"))
            except ValueError:
                wait = 30
            print(f"  503, waiting {wait}s", flush=True)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.content
    raise RuntimeError("giving up after repeated 503s")


def harvest(from_date: str, until_date: str | None) -> None:
    # per-query archive dir + state so runs never mix pages (codex review #4/#10)
    run_key = f"from_{from_date}" + (f"_until_{until_date}" if until_date else "")
    run_dir = OAI_DIR / run_key
    run_dir.mkdir(parents=True, exist_ok=True)
    state_path = run_dir / "state.json"
    con = db.connect()
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    token = state.get("resumption_token")
    page_no = state.get("page_no", 0)

    total = 0
    while True:
        if token:
            params = {"verb": "ListRecords", "resumptionToken": token}
        else:
            params = {"verb": "ListRecords", "metadataPrefix": "arXivRaw",
                      "set": "math", "from": from_date}
            if until_date:
                params["until"] = until_date
        xml_bytes = fetch_page(session, params)
        page_no += 1
        (run_dir / f"page_{page_no:04d}.xml.gz").write_bytes(gzip.compress(xml_bytes))
        records, token = parse_page(xml_bytes)
        upsert(con, records)
        total += len(records)
        print(f"page {page_no}: {len(records)} records (total {total}), token={'yes' if token else 'none'}", flush=True)
        state_path.write_text(json.dumps(
            {"from": from_date, "resumption_token": token, "page_no": page_no}))
        if not token:
            break
        time.sleep(POLITE_DELAY)
    print(f"done: {total} records harvested", flush=True)


def reparse() -> None:
    con = db.connect()
    total = 0
    # recursive: harvest stores pages under corpus/oai/<run_key>/page_*.xml.gz
    # (review-4: the flat glob silently reparsed nothing from nested runs)
    for page in sorted(OAI_DIR.glob("**/page_*.xml.gz")):
        records, _ = parse_page(gzip.decompress(page.read_bytes()))
        upsert(con, records)
        total += len(records)
    print(f"reparsed {total} records")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="from_date", default="2026-05-01")
    ap.add_argument("--until", dest="until_date", default=None)
    ap.add_argument("--reparse", action="store_true")
    args = ap.parse_args()
    if args.reparse:
        reparse()
    else:
        harvest(args.from_date, args.until_date)
    return 0


if __name__ == "__main__":
    sys.exit(main())
