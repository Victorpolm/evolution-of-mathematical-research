"""Offline, paired raw-name / OpenAlex-ID comparison. Python standard library.

Input: frozen projected OpenAlex API page caches plus acquisition.json.
No network calls; outputs contain only aggregate statistics.
"""
import argparse
from collections import Counter, defaultdict
import datetime as dt
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import unicodedata
from urllib.parse import unquote, urlparse

PLACEHOLDERS = {"A9999999999", "A5317838346"}
MODERN = re.compile(r"(?<!\d)(\d{4}\.\d{4,5})(?:v\d+)?(?!\d)")
GROUP = re.compile(r"\b(collaboration|consortium|et al\.?|working group|study group|and others)\b", re.I)
NORMALIZER = "nfc-whitespace-v1; case, initials, accents, punctuation preserved"


def name_key(value):
    if not isinstance(value, str):
        return None
    return " ".join(unicodedata.normalize("NFC", value).split()) or None


def author_key(value):
    if not isinstance(value, str):
        return None
    key = value.removeprefix("https://openalex.org/").removeprefix("http://openalex.org/")
    return key if re.fullmatch(r"A\d+", key) and key not in PLACEHOLDERS else None


def arxiv_ids(work):
    values = []
    for loc in work.get("locations", []):
        for key in ("landing_page_url", "pdf_url"):
            value = loc.get(key) or ""
            host = (urlparse(value).hostname or "").lower()
            if host == "arxiv.org" or host.endswith(".arxiv.org"):
                values.append(unquote(urlparse(value).path))
        if (loc.get("id") or "").lower().startswith("pmh:oai:arxiv.org:"):
            values.append(loc["id"])
    doi = work.get("doi") or ""
    if doi.lower().startswith("https://doi.org/10.48550/arxiv."):
        values.append(doi)
    ids = set()
    for value in values:
        for match in MODERN.finditer(value):
            aid = match.group(1)
            year, month = 2000 + int(aid[:2]), int(aid[2:4])
            if year >= 2007 and 1 <= month <= 12:
                ids.add(aid)
    return ids


def read_snapshot(root):
    manifest = json.loads((root / "acquisition.json").read_text())
    if not manifest.get("complete"):
        raise ValueError("Acquisition incomplete: refusing population counts from partial pages")
    works = {}
    duplicates = 0
    for partition in manifest["partitions"]:
        if not partition.get("pagination_complete"):
            raise ValueError("An acquisition partition is incomplete")
        count = 0
        for item in partition["pages"]:
            path = root / manifest.get("page_directory", "pages") / item["file"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError("Page hash mismatch: " + item["file"])
            with gzip.open(path, "rt", encoding="utf-8") as f:
                page = json.load(f)
            if len(page["results"]) != item["works"]:
                raise ValueError("Page length mismatch")
            if page["meta"]["count"] != partition["initial_count"]:
                raise ValueError("API population count changed within a partition")
            for w in page["results"]:
                primary = (w.get("primary_topic") or {}).get("field") or {}
                if primary.get("id") != "https://openalex.org/fields/26" or "arxiv" not in (w.get("indexed_in") or []):
                    raise ValueError("Record does not match the declared mathematics/arXiv scope")
                if not str(w.get("publication_date", "")).startswith(partition["publication_month"]):
                    raise ValueError("Record publication date is outside its acquisition partition")
                if w["id"] in works:
                    duplicates += 1
                    if w != works[w["id"]]:
                        raise ValueError("Conflicting duplicate OpenAlex record")
                works[w["id"]] = w
            count += len(page["results"])
        if count != partition["retrieved"] or count != partition["initial_count"]:
            raise ValueError("Population count changed during pagination; reconcile before analysis")
    return list(works.values()), manifest, duplicates


def prepare(works, start="2024-01", end="2025-12"):
    diagnostics = Counter(candidate_works=len(works))
    mapped = defaultdict(list)
    for w in works:
        ids = arxiv_ids(w)
        if len(ids) != 1:
            diagnostics["no_unique_modern_arxiv_id" if not ids else "multiple_arxiv_ids"] += 1
            continue
        aid = next(iter(ids))
        month = f"20{aid[:2]}-{aid[2:4]}"
        if not start <= month <= end:
            diagnostics["arxiv_id_outside_window"] += 1
            continue
        mapped[aid].append(w)
    papers = []
    for aid, matches in sorted(mapped.items()):
        if len(matches) != 1:
            diagnostics["duplicate_arxiv_id_groups"] += 1
            diagnostics["works_in_duplicate_arxiv_groups"] += len(matches)
            continue
        w = matches[0]
        authorships = w.get("authorships") or []
        names = [name_key(a.get("raw_author_name")) for a in authorships]
        authors = [author_key((a.get("author") or {}).get("id")) for a in authorships]
        reasons = []
        if not authorships:
            reasons.append("empty_byline")
        if w.get("is_authors_truncated") or len(authorships) >= 100:
            reasons.append("truncated_or_100plus_byline")
        if any(x is None for x in names):
            reasons.append("missing_raw_name")
        if any(x is None for x in authors):
            reasons.append("missing_or_placeholder_author_id")
        valid_ids = [a for a in authors if a]
        if len(valid_ids) != len(set(valid_ids)):
            reasons.append("repeated_id_in_byline")
        if any(GROUP.search(n or "") for n in names):
            reasons.append("possible_group_name")
        p = {"arxiv_id": aid, "work_id": w["id"], "month": f"20{aid[:2]}-{aid[2:4]}", "publication_year": w["publication_year"],
             "names": names, "ids": authors, "slots": len(authorships), "reasons": reasons,
             "subfield": ((w.get("primary_topic") or {}).get("subfield") or {}).get("display_name", "Unknown"),
             "raw_orcids": [a.get("raw_orcid") for a in authorships],
             "profile_orcids": [(a.get("author") or {}).get("orcid") for a in authorships]}
        papers.append(p)
    diagnostics["unique_arxiv_papers_in_window"] = len(papers)
    return papers, dict(diagnostics)


def top_share(values, proportion):
    ordered = sorted(values, reverse=True)
    if not ordered or not sum(ordered):
        return None
    mass = len(ordered) * proportion
    whole = int(math.floor(mass))
    boundary = (mass - whole) * ordered[whole] if whole < len(ordered) else 0
    return (sum(ordered[:whole]) + boundary) / sum(ordered)


def distribution(values):
    x = sorted(values)
    n, total = len(x), sum(x)
    if not n or not total:
        return None
    gini = 2 * sum((i + 1) * v for i, v in enumerate(x)) / (n * total) - (n + 1) / n
    return {"gini": gini, "top_1_share": top_share(x, .01), "top_5_share": top_share(x, .05), "top_10_share": top_share(x, .1), "top_100_share": sum(x[-100:]) / total if n >= 100 else None, "median": statistics.median(x)}


def credits(papers, method):
    fractional, full = defaultdict(float), Counter()
    for p in papers:
        for key in p[method]:
            full[key] += 1
            fractional[key] += 1 / p["slots"]
    return dict(fractional), full


def metrics(papers, detailed=False):
    n = len(papers)
    incidences = sum(p["slots"] for p in papers)
    result = {"papers": n, "authorship_slots": incidences,
              "mean_team_size": incidences / n if n else None,
              "median_team_size": statistics.median(p["slots"] for p in papers) if n else None}
    for method in ("names", "ids"):
        fraction, full = credits(papers, method)
        a = len(full)
        result[method] = {"authors": a, "papers_per_author": n / a if a else None,
                          "incidences_per_author": incidences / a if a else None,
                          "fractional_credit_sum": sum(fraction.values())}
        if n:
            assert a > 0
            assert math.isclose(sum(fraction.values()), n, abs_tol=1e-7)
            assert sum(full.values()) == incidences
            assert math.isclose(a * (incidences / a) / (incidences / n), n, abs_tol=1e-8)
        if detailed:
            result[method]["fractional_distribution"] = distribution(fraction.values())
            result[method]["full_distribution"] = distribution(full.values())
            result[method]["activity_frequency"] = dict(sorted(Counter(full.values()).items()))
    if detailed:
        result["team_size_frequency"] = dict(sorted(Counter(p["slots"] for p in papers).items()))
    return result


def quality(papers):
    reasons = Counter(r for p in papers for r in p["reasons"])
    slots = sum(p["slots"] for p in papers)
    kept = [p for p in papers if not p["reasons"]]
    return {"linked_papers": len(papers), "paired_papers": len(kept), "retention": len(kept) / len(papers) if papers else None,
            "excluded_papers": len(papers) - len(kept), "reasons_nonexclusive": dict(reasons), "observed_slots": slots,
            "slots_with_valid_id": sum(a is not None for p in papers for a in p["ids"]),
            "slots_with_raw_name": sum(a is not None for p in papers for a in p["names"]),
            "name_collision_papers": sum(len(set(p["names"])) < len(p["names"]) for p in kept),
            "mean_observed_team_all": slots / len(papers) if papers else None,
            "mean_team_paired": sum(p["slots"] for p in kept) / len(kept) if kept else None}


def transition(before, after, method):
    f0, _ = credits(before, method)
    f1, _ = credits(after, method)
    c = set(f0) & set(f1)
    e = set(f1) - set(f0)
    x = set(f0) - set(f1)
    terms = {"continuing_keys": len(c), "appearing_keys": len(e), "disappearing_keys": len(x),
             "continuing_credit_change": sum(f1[a] - f0[a] for a in c),
             "appearing_credit": sum(f1[a] for a in e),
             "disappearing_credit": -sum(f0[a] for a in x), "paper_change": len(after) - len(before)}
    residual = terms["paper_change"] - sum(terms[k] for k in ("continuing_credit_change", "appearing_credit", "disappearing_credit"))
    terms["identity_residual"] = residual
    assert abs(residual) < 1e-7
    assert len(f1) - len(f0) == len(e) - len(x)
    if before and after:
        m0, m1 = metrics(before), metrics(after)
        terms["log_decomposition"] = {"papers": math.log(m1["papers"] / m0["papers"]), "authors": math.log(m1[method]["authors"] / m0[method]["authors"]), "incidences_per_author": math.log(m1[method]["incidences_per_author"] / m0[method]["incidences_per_author"]), "minus_mean_team_size": -math.log(m1["mean_team_size"] / m0["mean_team_size"])}
        logs = terms["log_decomposition"]
        assert math.isclose(logs["papers"], sum(logs[k] for k in ("authors", "incidences_per_author", "minus_mean_team_size")), abs_tol=1e-12)
    return terms


def crosswalk_diagnostics(papers):
    """Describe mappings within this window; multiplicity is not an error rate."""
    by_name, by_id, by_raw_orcid = defaultdict(set), defaultdict(set), defaultdict(set)
    raw_orcid_slots = 0
    for p in papers:
        for name, aid, orcid in zip(p["names"], p["ids"], p["raw_orcids"]):
            by_name[name].add(aid)
            by_id[aid].add(name)
            if orcid:
                by_raw_orcid[orcid].add(aid)
                raw_orcid_slots += 1
    slots = sum(p["slots"] for p in papers)
    multi_names = {key for key, values in by_name.items() if len(values) > 1}
    multi_ids = {key for key, values in by_id.items() if len(values) > 1}
    name_slots = sum(name in multi_names for p in papers for name in p["names"])
    id_slots = sum(aid in multi_ids for p in papers for aid in p["ids"])
    return {"name_keys": len(by_name), "id_keys": len(by_id),
            "authorship_slots": slots,
            "names_associated_with_multiple_ids": len(multi_names),
            "ids_associated_with_multiple_names": len(multi_ids),
            "distinct_ids_per_name_frequency": dict(sorted(Counter(map(len, by_name.values())).items())),
            "distinct_names_per_id_frequency": dict(sorted(Counter(map(len, by_id.values())).items())),
            "slots_in_names_with_multiple_ids": name_slots,
            "share_of_slots_in_names_with_multiple_ids": name_slots / slots if slots else None,
            "slots_in_ids_with_multiple_names": id_slots,
            "share_of_slots_in_ids_with_multiple_names": id_slots / slots if slots else None,
            "raw_orcid_slots": raw_orcid_slots, "distinct_raw_orcids": len(by_raw_orcid),
            "raw_orcid_slot_share": raw_orcid_slots / slots if slots else None,
            "raw_orcids_associated_with_multiple_ids": sum(len(s) > 1 for s in by_raw_orcid.values()),
            "interpretation": "Many-to-many mappings on paired papers within the stated window, not validated error rates. Slot shares use all paired slots. Raw ORCIDs are source-reported strings; profile ORCIDs are not used. The ORCID subset is selected."}


def run(root, output, manifest_path=None):
    works, source, duplicate_work_rows = read_snapshot(root)
    papers, diagnostic = prepare(works)
    paired = [p for p in papers if not p["reasons"]]
    if not paired:
        raise ValueError("No eligible papers")
    months = [f"{y}-{m:02d}" for y in (2024, 2025) for m in range(1, 13)]
    result = {"schema_version": 1, "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "source": {k: source[k] for k in ("started_at", "finished_at", "query_scope", "authentication", "requests_this_run")},
              "acquisition_sha256": hashlib.sha256((root / "acquisition.json").read_bytes()).hexdigest(),
              "normalizer": NORMALIZER, "date_basis": "arXiv identifier month proxy, 2024-01 through 2025-12; OpenAlex publication dates not used as upload dates",
              "scope_caveat": "OpenAlex core records with primary field Mathematics and indexed_in arxiv, limited to OpenAlex publication years 2024-2026. This is an observed subset, not all arXiv mathematics. Earlier/later OpenAlex publication years can omit otherwise eligible uploads.",
              "authorship_caveat": "OpenAlex's source byline may describe the journal version, not the initial arXiv byline. Names and IDs are measured on the same OpenAlex authorship slots.",
              "byline_completeness": "No missing name/ID, no repeated IDs, no group-name flag, no truncation flag and fewer than 100 returned slots. This verifies supplied slots, not source byline accuracy.",
              "diagnostics": {**diagnostic, "duplicate_work_rows": duplicate_work_rows}, "quality": quality(papers), "monthly": [], "annual": [], "rolling12": []}
    result["source"]["started_at"] = source.get("first_page_retrieved_at", source["started_at"])
    result["source"]["finished_at"] = source.get("last_page_retrieved_at", source["finished_at"])
    for month in months:
        frame = [p for p in papers if p["month"] == month]
        kept = [p for p in frame if not p["reasons"]]
        result["monthly"].append({"period": month, **metrics(kept), "quality": quality(frame)})
    for year in (2024, 2025):
        frame = [p for p in papers if p["month"].startswith(str(year))]
        kept = [p for p in frame if not p["reasons"]]
        result["annual"].append({"period": str(year), **metrics(kept, True), "quality": quality(frame),
                                 "identity_diagnostics": crosswalk_diagnostics(kept)})
    for end in range(11, len(months)):
        window = set(months[end-11:end+1])
        kept = [p for p in paired if p["month"] in window]
        frame = [p for p in papers if p["month"] in window]
        result["rolling12"].append({"period": months[end], "start": months[end-11], **metrics(kept), "quality": quality(frame)})
    result["raw_name_coverage_diagnostic"] = {"note": "A separate population sensitivity check: relax only the missing-ID gate, retaining all other byline exclusions. Never pair these paper counts with author IDs from the smaller complete-ID subset.", "annual": []}
    for year in (2024, 2025):
        frame = [p for p in papers if p["month"].startswith(str(year)) and not (set(p["reasons"]) - {"missing_or_placeholder_author_id"})]
        fractional, full = credits(frame, "names")
        assert math.isclose(sum(fractional.values()), len(frame), abs_tol=1e-7)
        result["raw_name_coverage_diagnostic"]["annual"].append({"period": str(year), "papers": len(frame), "name_keys": len(full), "authorship_slots": sum(full.values()), "papers_per_name": len(frame)/len(full), "fractional_credit_sum": sum(fractional.values())})
    before, after = ([p for p in paired if p["month"].startswith(str(y))] for y in (2024, 2025))
    result["transitions_exploratory"] = {m: transition(before, after, m) for m in ("names", "ids")}
    result["identity_diagnostics"] = crosswalk_diagnostics(paired)
    result["subfields"] = [{"subfield": field, "annual": [{"period": str(y), **metrics([p for p in paired if p["subfield"] == field and p["month"].startswith(str(y))], True), "quality": quality([p for p in papers if p["subfield"] == field and p["month"].startswith(str(y))])} for y in (2024, 2025)]} for field in sorted({p["subfield"] for p in papers})]
    result["publication_year_by_upload_year"] = {str(y): dict(sorted(Counter(p["publication_year"] for p in papers if p["month"].startswith(str(y))).items())) for y in (2024, 2025)}
    if manifest_path:
        raw = manifest_path.read_bytes()
        ids = {x.strip().split("v")[0] for x in raw.decode().splitlines() if x.strip()}
        result["manifest_overlap"] = {"sha256": hashlib.sha256(raw).hexdigest(), "note": "Overlap with the existing project ID manifest; not an independently validated arXiv census", "annual": []}
        for y in (2024, 2025):
            total = sum(a.startswith(str(y)[2:]) for a in ids)
            linked = [p for p in papers if p["arxiv_id"] in ids and p["month"].startswith(str(y))]
            kept = [p for p in linked if not p["reasons"]]
            result["manifest_overlap"]["annual"].append({"period": str(y), "manifest_papers": total, "linked_overlap": len(linked), "paired_overlap": len(kept), "linked_fraction_of_manifest": len(linked) / total, "paired_fraction_of_manifest": len(kept) / total, **metrics(kept)})
    output.mkdir(parents=True, exist_ok=True)
    (output / "openalex_comparison.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--math-manifest", type=Path)
    args = parser.parse_args()
    result = run(args.snapshot, args.output, args.math_manifest)
    brief = [{"period": r["period"], "papers": r["papers"], "authorship_slots": r["authorship_slots"], "mean_team_size": r["mean_team_size"],
              **{m: {k: r[m][k] for k in ("authors", "papers_per_author", "incidences_per_author")} for m in ("ids", "names")}} for r in result["annual"]]
    print(json.dumps({"quality": result["quality"], "annual": brief, "identity_diagnostics": result["identity_diagnostics"]}, indent=2))


if __name__ == "__main__":
    main()
