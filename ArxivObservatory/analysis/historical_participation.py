"""Offline historical papers/contributors analysis of a frozen OpenAlex cache.

Stream and validate projected pages, retaining compact bylines instead of all
OpenAlex objects. Output is aggregate-only; no acquisition or identity resolver.
"""
import argparse
from collections import Counter, defaultdict
import csv
import datetime as dt
import gzip
import hashlib
import json
import math
from pathlib import Path

from .openalex_names import NORMALIZER, arxiv_ids, metrics, prepare, quality
from .retention_audit import partial_credit, summarize, orcid_opportunity


def months(start, end):
    y, m = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    if not (1 <= m <= 12 and 1 <= em <= 12) or start > end:
        raise ValueError("Invalid month range")
    return [f"{i // 12:04d}-{i % 12 + 1:02d}"
            for i in range(y * 12 + m - 1, ey * 12 + em)]


def read_compact(snapshot, start, end, required_partitions=None):
    """Check every page and reconcile work/arXiv duplicates across partitions."""
    source = json.loads((snapshot / "acquisition.json").read_text())
    if not source.get("complete"):
        raise ValueError("Acquisition incomplete")
    partitions = source["partitions"]
    observed = [p["publication_month"] for p in partitions]
    if len(set(observed)) != len(observed):
        raise ValueError("Repeated acquisition partition")
    if required_partitions is not None and set(observed) != set(required_partitions):
        raise ValueError("Missing or unexpected acquisition partitions")
    seen, mapped, multiplicity = {}, {}, Counter()
    diagnostic = Counter()
    stages, outside, pub = Counter(), Counter(), defaultdict(Counter)
    for partition in partitions:
        if not partition.get("pagination_complete"):
            raise ValueError("Incomplete partition")
        count = 0
        for item in partition["pages"]:
            path = snapshot / source.get("page_directory", "pages") / item["file"]
            blob = path.read_bytes()
            if hashlib.sha256(blob).hexdigest() != item["sha256"]:
                raise ValueError("Page hash mismatch")
            page = json.loads(gzip.decompress(blob))
            if len(page["results"]) != item["works"] or page["meta"]["count"] != partition["initial_count"]:
                raise ValueError("Page count mismatch or changing API population")
            count += len(page["results"])
            for work in page["results"]:
                field = ((work.get("primary_topic") or {}).get("field") or {}).get("id")
                if field != "https://openalex.org/fields/26" or "arxiv" not in (work.get("indexed_in") or []):
                    raise ValueError("Work outside declared mathematics/arXiv scope")
                if not str(work.get("publication_date", "")).startswith(partition["publication_month"]):
                    raise ValueError("Work outside its publication-date partition")
                fingerprint = hashlib.sha256(json.dumps(work, sort_keys=True).encode()).digest()
                wid = work["id"]
                if wid in seen:
                    diagnostic["duplicate_cached_work_rows"] += 1
                    if seen[wid] != fingerprint:
                        raise ValueError("Conflicting duplicate OpenAlex work")
                    raise ValueError("Repeated work in disjoint pagination: reconcile before analysis")
                seen[wid] = fingerprint
                diagnostic["candidate_works"] += 1
                ids = arxiv_ids(work)
                if len(ids) != 1:
                    stage = "no_unique_modern_arxiv_id" if not ids else "multiple_arxiv_ids"
                else:
                    aid = next(iter(ids))
                    month = f"20{aid[:2]}-{aid[2:4]}"
                    stage = "target_id_window" if start <= month <= end else "outside_target_id_window"
                    if stage == "outside_target_id_window":
                        outside[month[:4]] += 1
                stages[stage] += 1
                pub[str(work["publication_year"])][stage] += 1
                if stage != "target_id_window":
                    continue
                compact, _ = prepare([work], start, end)
                paper = compact[0]
                multiplicity[aid] += 1
                mapped[aid] = paper if multiplicity[aid] == 1 else None
    # Compare partition totals after streaming, independently of deduplication.
        if count != partition["retrieved"] or count != partition["initial_count"]:
            raise ValueError("Partition total mismatch")
    papers = [p for _, p in sorted(mapped.items()) if p is not None]
    diagnostic.update({"unique_arxiv_papers_in_window": len(papers),
                       "duplicate_arxiv_id_groups": sum(n > 1 for n in multiplicity.values()),
                       "works_in_duplicate_arxiv_groups": sum(n for n in multiplicity.values() if n > 1)})
    assert len(papers) + diagnostic["works_in_duplicate_arxiv_groups"] == stages["target_id_window"]
    linkage = defaultdict(Counter)
    for aid, n in multiplicity.items():
        row = linkage[f"20{aid[:2]}-{aid[2:4]}"]
        row["mapped_arxiv_ids"] += 1
        row["unambiguous_linked_papers"] += n == 1
        row["ambiguous_arxiv_groups"] += n > 1
        row["works_in_ambiguous_groups"] += n if n > 1 else 0
    return papers, source, dict(diagnostic), {
        "stages": dict(stages), "outside_target_window_by_id_year": dict(sorted(outside.items())),
        "by_publication_year": {y: dict(v) for y, v in sorted(pub.items())},
        "linkage_by_id_month": {m: dict(v) for m, v in sorted(linkage.items())}}


def period_row(period, papers):
    paired = [p for p in papers if not p["reasons"]]
    return {"period": period, **metrics(paired), "coverage": summarize(papers)}


def series(papers, start, end):
    """Unique contributors are unions within each window, never summed counts."""
    by_month = defaultdict(list)
    for p in papers:
        by_month[p["month"]].append(p)
    window = months(start, end)
    monthly = [period_row(m, by_month[m]) for m in window]
    annual, rolling = [], []
    for y in sorted({m[:4] for m in window}):
        year_months = [m for m in window if m.startswith(y)]
        if len(year_months) == 12:
            annual.append(period_row(y, [p for m in year_months for p in by_month[m]]))
    for i in range(11, len(window)):
        rows = [p for m in window[i - 11:i + 1] for p in by_month[m]]
        rolling.append(period_row(window[i], rows))
    return {"annual": annual, "monthly": monthly, "rolling12": rolling}


def decomposition(before, after):
    result = {"from": before["period"], "to": after["period"]}
    if not before["papers"] or not after["papers"]:
        return {**result, "available": False}
    dlog_p = math.log(after["papers"] / before["papers"])
    result.update({"available": True, "papers_log_change": dlog_p,
                   "linked_papers_log_change": math.log(after["coverage"]["linked_papers"] / before["coverage"]["linked_papers"]),
                   "retention_log_change": math.log(after["coverage"]["retention"] / before["coverage"]["retention"])})
    assert math.isclose(dlog_p, result["linked_papers_log_change"] + result["retention_log_change"], abs_tol=1e-12)
    for method in ("names", "ids"):
        a = math.log(after[method]["authors"] / before[method]["authors"])
        ratio = math.log(after[method]["papers_per_author"] / before[method]["papers_per_author"])
        assert math.isclose(a + ratio, dlog_p, abs_tol=1e-12)
        result[method] = {"contributors_log_change": a, "papers_per_contributor_log_change": ratio}
    return result


def add_linkage_coverage(data):
    """Expose version-link exclusions before the byline-retention denominator."""
    link = data["flow"]["linkage_by_id_month"]
    all_months = months(*data["upload_window"])
    for mode in ("annual", "monthly", "rolling12"):
        for row in data[mode]:
            if mode == "annual":
                selected = [m for m in all_months if m.startswith(row["period"])]
            elif mode == "monthly":
                selected = [row["period"]]
            else:
                end = all_months.index(row["period"])
                selected = all_months[end - 11:end + 1]
            total = sum(link.get(m, {}).get("mapped_arxiv_ids", 0) for m in selected)
            ambiguous = sum(link.get(m, {}).get("ambiguous_arxiv_groups", 0) for m in selected)
            assert total - ambiguous == row["coverage"]["linked_papers"]
            row["coverage"].update({"mapped_arxiv_ids": total, "ambiguous_arxiv_groups": ambiguous,
                "overall_retention": row["papers"] / total if total else None,
                "linkage_retention": (total - ambiguous) / total if total else None})


def write_report(data, output):
    rows = data["annual"]
    first, last = rows[0], rows[-1]
    text = ["# Historical papers per observed contributor", "",
            "Computed from a frozen OpenAlex snapshot retrieved on 16 September 2026. "
            "These are descriptive measurements of recorded names and IDs in a selected "
            "arXiv-linked Mathematics population, not validated counts of people.", "",
            "## First graph and estimand", "",
            "For each period t, P_t counts retained papers and A_t counts distinct contributor "
            "keys on those exact papers. We compute P_t/A_t twice: raw-name keys without "
            "additional entity resolution, and OpenAlex's existing resolved author IDs. "
            "We do not create a new merging algorithm. Neither definition is a bound on people.", "",
            "Each complete k-slot byline allocates 1/k to each slot, so total credit equals P_t "
            "and its mean over distinct keys is P_t/A_t. This is not the average full-count "
            "papers someone coauthored (I_t/A_t), and changes need not reflect individual productivity.", "",
            "## Annual results", "",
            "| Year | Linked papers | Retained P | Retention | Distinct names | OpenAlex IDs | P/names | P/IDs |",
            "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        text.append(f"| {r['period']} | {r['coverage']['linked_papers']:,} | {r['papers']:,} | "
                    f"{r['coverage']['retention']:.2%} | {r['names']['authors']:,} | {r['ids']['authors']:,} | "
                    f"{r['names']['papers_per_author']:.4f} | {r['ids']['papers_per_author']:.4f} |")
    text += ["", "## Work-to-paper reconciliation", "",
             "| Acquisition / linkage stage | Works or papers |", "|---|---:|"]
    stages = data["flow"]["stages"]
    for label, value in [
        ("Unique acquired works", data["diagnostics"]["candidate_works"]),
        ("Outside 2010–2025 arXiv ID dates", stages.get("outside_target_id_window", 0)),
        ("No unique modern arXiv ID", stages.get("no_unique_modern_arxiv_id", 0)),
        ("Multiple arXiv IDs on one work", stages.get("multiple_arxiv_ids", 0)),
        ("Works in ambiguous multiple-work/arXiv groups", data["diagnostics"]["works_in_duplicate_arxiv_groups"]),
        ("Uniquely linked target-window papers", data["diagnostics"]["unique_arxiv_papers_in_window"]),
        ("Paired papers after byline checks", sum(r["papers"] for r in rows)),
    ]:
        text.append(f"| {label} | {value:,} |")
    text += ["", "The date filter is distinct from failed linkage and from byline exclusions. "
             "The JSON breaks outside-window records down by arXiv ID year and all stages "
             "down by OpenAlex publication year.", "",
             "| Year | Mapped arXiv paper IDs | Ambiguous version-link groups | Paired / mapped paper IDs |",
             "|---|---:|---:|---:|"]
    for r in rows:
        c = r["coverage"]
        text.append(f"| {r['period']} | {c['mapped_arxiv_ids']:,} | {c['ambiguous_arxiv_groups']:,} | {c['overall_retention']:.2%} |")
    text += ["", "Mapped paper IDs count distinct in-window arXiv IDs on works with one parsable "
             "modern ID, before excluding IDs linked to multiple OpenAlex works. The byline "
             "retention denominator in the first table excludes those ambiguous groups. "
             "Neither retention percentage measures coverage of all arXiv mathematics.", "",
             "## What the records show", ""]
    for method, label in (("names", "raw names"), ("ids", "OpenAlex IDs")):
        a, b = first[method]["papers_per_author"], last[method]["papers_per_author"]
        text.append(f"- {first['period']}–{last['period']}: P/A using {label} changes from {a:.4f} to {b:.4f} ({b/a-1:+.2%}).")
    text.append(f"- Retained papers change {last['papers']/first['papers']-1:+.2%}; observed ID counts "
                f"{last['ids']['authors']/first['ids']['authors']-1:+.2%}; raw-name counts "
                f"{last['names']['authors']/first['names']['authors']-1:+.2%}. Thus contributor-key counts "
                "grow faster than retained papers under both definitions.")
    text.append(f"- Mean returned team size increases from {first['mean_team_size']:.3f} to "
                f"{last['mean_team_size']:.3f} ({last['mean_team_size']/first['mean_team_size']-1:+.2%}). "
                "The collaboration identity P/A = (I/A)/(I/P) separates this accounting term "
                "from full-count coauthored-paper participation.")
    for method, label in (("names", "raw name"), ("ids", "OpenAlex ID")):
        a, b = first[method]["incidences_per_author"], last[method]["incidences_per_author"]
        text.append(f"- Coauthored-paper incidences per {label}, I/A: {a:.3f} to {b:.3f} ({b/a-1:+.2%}). "
                    "This is a different measure from fractional P/A, still subject to identity and coverage limitations.")
    retention = [r["coverage"]["retention"] for r in rows]
    text += [f"- Retention ranges from {min(retention):.2%} to {max(retention):.2%}. "
             "These changes in selection must accompany the ratios; dividing by authors does not correct them.", "",
             "The agreement or disagreement between the two identity definitions is a sensitivity "
             "diagnostic. Shared selection, homonyms, spelling variants and split/merged IDs can "
             "affect both series. No real-person trend or causal effect of AI is established.", "",
             "## Coverage and partial bylines", "",
             "The JSON also reports annual raw-name and identified-ID counts before missing-ID "
             "paper exclusions, retaining all otherwise usable bylines. Missing slots keep 1/k "
             "unallocated credit; unusable bylines keep one whole paper equivalent. Allocated "
             "credit + missing-ID credit + unusable-byline credit equals all linked papers. "
             "Allocated credit per identified ID is reported separately from P/A. "
             "This broader sensitivity does not recover missing people or correct selection.", "",
             "| Year | Usable papers / names | Usable papers / observed IDs | Allocated credit / ID | Unallocated / linked credit |",
             "|---|---:|---:|---:|---:|"]
    for row in data["annual_audit"]:
        p = row["partial_credit"]
        text.append(f"| {row['period']} | {p['usable_papers_per_raw_name']:.4f} | "
                    f"{p['usable_papers_per_identified_id']:.4f} | {p['mean_allocated_credit_per_id']:.4f} | "
                    f"{p['total_unallocated_credit']/p['linked_papers']:.2%} |")
    text += ["", "Usable papers / observed IDs counts all usable papers in the numerator, including "
             "those with unidentified slots. It is not mean fractional credit per observed ID. "
             "The allocated-credit column retains that distinction.", "",
             "## Acquisition and analysis rules", "",
             f"- {data['diagnostics']['candidate_works']:,} unique OpenAlex works acquired; "
             f"{data['diagnostics']['unique_arxiv_papers_in_window']:,} uniquely linked target-window papers.",
             "- Query: indexed_in:arxiv, primary_topic.field.id:26, publication years 2010–2026; "
             "204 monthly partitions, 100 results/page, selected fields, at most "
             "10 requests/second. All partitions fit within the 10,000-result basic-paging limit; each complete partition uses one paging strategy. Completed cursor partitions were retained; mixed partitions were reconciled by re-fetching their cursor prefix using numbered pages. Unique work counts were required to match each partition total. Credentials stayed in memory; only the free daily allowance was used.",
             "- Analysis dates: arXiv ID months January 2010–December 2025, a proxy for initial "
             "submission month. OpenAlex publication dates can refer to later journal versions. "
             "The query catches only versions with publication years 2010–2026; it is not a census "
             "of all arXiv mathematics and does not establish primary arXiv category membership.",
             "- Require exactly one modern arXiv ID per work; exclude all works in ambiguous "
             "multiple-work/one-arXiv groups. Count an arXiv paper once, irrespective of version.",
             "- Paired papers require nonempty complete names and usable IDs, no repeated ID "
             "within a byline, no group-name flag, no truncation flag, and fewer than 100 slots. "
             "The returned byline is not independently validated as the original arXiv byline.",
             "- Name normalization: " + NORMALIZER + ". Equal strings are counted together; "
             "this does not establish that they represent one person.",
             "- Calendar years and rolling 12-month windows recompute contributor unions; "
             "they do not sum monthly distinct counts. No smoothing or imputation is applied. "
             "All 16 years are shown; a five-year lookback is relevant to future entry analyses, "
             "not required to define annual active-key counts.",
             "- Every page hash, scope filter and partition count was checked before analysis. "
             "API retrieval is a bounded interval, not a transactional database snapshot. "
             "Created/update dates are retained, but one extraction cannot reconstruct historical "
             "byline completeness at equal elapsed time since indexing.",
             "- Exact frozen-record counts have no sampling interval here. Identity error and "
             "selective missingness need external validation; a bootstrap would not resolve them.", "",
             "## Mathematics and prior work", "",
             "P = A × (I/A) / (I/P); Δlog P = Δlog A + Δlog(P/A). "
             "For linked papers L and retention c, P = Lc. Both decompositions are checked "
             "numerically and saved for every adjacent year. These identities describe accounting, "
             "not mechanisms. Mean team size and annual subfield results are available in the JSON.", "",
             "The revised method and its discussion of Hulek & Teschke (2023), Grossman (2005), "
             "Fanelli & Larivière (2016), and author-disambiguation studies remain the foundation. "
             "See analysis/STATISTICAL_RESEARCH_PLAN.md in the repository, relative to ArxivObservatory. "
             "This run implements the narrower papers/contributors question; entry, concentration "
             "and AI effects need their own validation and design.", "",
             "## Reproduce offline", "", "```bash",
             "cd ArxivObservatory",
             "python -m analysis.historical_participation --snapshot /path/to/openalex-historical-20260916 --output /path/to/results",
             "python tests/run_participation_checks.py", "```", "",
             "The raw projected cache is supplied separately as a metadata snapshot, not committed "
             "to GitHub. acquisition_manifest.json pins all page hashes. The acquisition helper "
             "is included in that snapshot; contributed analysis remains offline.", ""]
    (output / "HISTORICAL_PARTICIPATION.md").write_text("\n".join(text))


def run(snapshot, output):
    start, end = "2010-01", "2025-12"
    papers, source, diagnostic, flow = read_compact(snapshot, start, end, months("2010-01", "2026-12"))
    data = {"schema_version": 1, "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "status": "Descriptive observed-key analysis; real-person and causal interpretations unvalidated",
            "upload_window": [start, end], "source_scope": source["query_scope"],
            "snapshot_manifest_sha256": hashlib.sha256((snapshot / "acquisition.json").read_bytes()).hexdigest(),
            "retrieval_interval": [source["first_page_retrieved_at"], source["last_page_retrieved_at"]],
            "normalizer": NORMALIZER, "diagnostics": diagnostic, "flow": flow,
            **series(papers, start, end), "annual_audit": [], "by_subfield": []}
    add_linkage_coverage(data)
    for annual in data["annual"]:
        y = annual["period"]
        rows = [p for p in papers if p["month"].startswith(y)]
        paired = [p for p in rows if not p["reasons"]]
        partial = partial_credit(rows)
        n = partial["raw_name_keys_usable"]
        partial["usable_papers_per_raw_name"] = partial["usable_byline_papers"] / n if n else None
        data["annual_audit"].append({"period": y, "quality": quality(rows),
            "partial_credit": partial, "orcid_on_paired_papers": orcid_opportunity(paired)})
        for field in sorted({p["subfield"] for p in rows}):
            data["by_subfield"].append({"subfield": field, **period_row(y, [p for p in rows if p["subfield"] == field])})
    data["adjacent_year_decompositions"] = [decomposition(a, b) for a, b in zip(data["annual"], data["annual"][1:])]
    output.mkdir(parents=True, exist_ok=True)
    (output / "historical_participation.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    (output / "acquisition_manifest.json").write_bytes((snapshot / "acquisition.json").read_bytes())
    with (output / "historical_annual.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "linked_papers", "retained_papers", "retention", "name_keys", "id_keys", "papers_per_name", "papers_per_id", "mean_team_size"])
        for r in data["annual"]:
            writer.writerow([r["period"], r["coverage"]["linked_papers"], r["papers"], r["coverage"]["retention"],
                             r["names"]["authors"], r["ids"]["authors"], r["names"]["papers_per_author"],
                             r["ids"]["papers_per_author"], r["mean_team_size"]])
    write_report(data, output)
    print(json.dumps({"years": len(data["annual"]), "diagnostics": diagnostic, "output": str(output)}))
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.snapshot, args.output)
