"""Offline coverage audit and partial-ID credit accounting for the frozen run.

No network calls, raw names or per-paper output. This diagnoses observed
metadata; it does not estimate real-person counts or correct missingness.
"""
import argparse
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

from .openalex_names import arxiv_ids, author_key, credits, distribution, prepare, read_snapshot

MISSING = "missing_or_placeholder_author_id"


def usable(p):
    return not (set(p["reasons"]) - {MISSING})


def summarize(papers):
    """Partition every linked paper into one mutually exclusive coverage state."""
    states = Counter(paired=0, all_ids_missing=0, some_ids_missing=0, other_byline_exclusion=0)
    for p in papers:
        if not p["reasons"]:
            state = "paired"
        elif p["ids"] and not any(p["ids"]):
            state = "all_ids_missing"
        elif any(a is None for a in p["ids"]):
            state = "some_ids_missing"
        else:
            state = "other_byline_exclusion"
        states[state] += 1
    n = len(papers)
    assert sum(states.values()) == n
    return {"linked_papers": n, "paired_papers": states["paired"],
            "retention": states["paired"] / n if n else None,
            "states": dict(states),
            "state_shares": {k: v/n if n else None for k, v in states.items()}}


def partial_credit(papers):
    """Unknown IDs receive unallocated credit, never a synthetic author key.

    Papers with unusable bylines retain a whole unallocated paper equivalent.
    Other k-slot papers allocate 1/k to each valid ID and 1/k to unallocated
    credit for each missing ID. k is the returned slot count, not a validated
    original-arXiv team size. Truncated/group/repeated-ID bylines are unusable.
    """
    rows = [p for p in papers if usable(p)]
    fractional, full = defaultdict(float), Counter()
    missing_credit = 0.0
    missing_slots = 0
    for p in rows:
        assert p["slots"] > 0 and p["slots"] == len(p["ids"])
        for aid in p["ids"]:
            if aid is None:
                missing_credit += 1 / p["slots"]
                missing_slots += 1
            else:
                fractional[aid] += 1 / p["slots"]
                full[aid] += 1
    assigned = math.fsum(fractional.values())
    unusable_count = len(papers) - len(rows)
    assert math.isclose(assigned + missing_credit, len(rows), abs_tol=1e-7)
    assert math.isclose(assigned + missing_credit + unusable_count, len(papers), abs_tol=1e-7)
    names_f, names_n = credits(rows, "names")
    assert math.isclose(math.fsum(names_f.values()), len(rows), abs_tol=1e-7)
    n = len(full)
    incidences = sum(p["slots"] for p in rows)
    assert sum(full.values()) + missing_slots == incidences
    return {"linked_papers": len(papers), "usable_byline_papers": len(rows),
            "unusable_byline_papers": unusable_count, "observed_slots_usable": incidences,
            "identified_slots_usable": sum(full.values()), "unidentified_slots_usable": missing_slots,
            "identified_id_keys": n, "raw_name_keys_usable": len(names_n),
            "allocated_credit_to_ids": assigned, "unallocated_missing_id_credit": missing_credit,
            "unallocated_unusable_byline_credit": unusable_count,
            "total_unallocated_credit": missing_credit + unusable_count,
            "mean_allocated_credit_per_id": assigned/n if n else None,
            "usable_papers_per_identified_id": len(rows)/n if n else None,
            "mean_full_participation_per_id": sum(full.values())/n if n else None,
            "mean_returned_team_size_usable": incidences/len(rows) if rows else None,
            "ids_full_distribution": distribution(full.values()),
            "ids_allocated_credit_distribution": distribution(fractional.values()),
            "ids_activity_frequency": dict(sorted(Counter(full.values()).items())),
            "names_full_distribution": distribution(names_n.values()),
            "names_fractional_distribution": distribution(names_f.values()),
            "interpretation": "Observed valid IDs on usable returned bylines, including incomplete-ID papers. This does not reconstruct missing people. Allocated credit per ID is not P/A; unallocated credit is not assigned to an artificial author."}


def orcid_opportunity(papers):
    work_sets, id_sets = defaultdict(set), defaultdict(set)
    slots = 0
    for p in papers:
        for orcid, aid in zip(p["raw_orcids"], p["ids"]):
            if not orcid:
                continue
            work_sets[orcid].add(p["work_id"])
            if aid is not None:
                id_sets[orcid].add(aid)
            slots += 1
    repeated = {o for o, ws in work_sets.items() if len(ws) >= 2}
    multiple = {o for o, ids in id_sets.items() if len(ids) >= 2}
    total_slots = sum(p["slots"] for p in papers)
    return {"authorship_slots": total_slots, "source_orcid_slots": slots,
            "source_orcid_slot_share": slots/total_slots if total_slots else None,
            "distinct_source_orcids": len(work_sets), "orcids_on_multiple_papers": len(repeated),
            "orcids_with_multiple_ids": len(multiple),
            "multiple_ids_and_multiple_papers": len(multiple & repeated),
            "multiple_id_share_all_orcids": len(multiple)/len(work_sets) if work_sets else None,
            "multiple_id_share_repeated_orcids": len(multiple & repeated)/len(repeated) if repeated else None,
            "multiple_id_orcids_on_only_one_paper": len(multiple - repeated),
            "papers_per_source_orcid_frequency": dict(sorted(Counter(map(len, work_sets.values())).items())),
            "interpretation": "Source-recorded ORCID strings; neither rate is an adjudicated split rate or a population bound. Repeated observation changes the opportunity to detect a mapping to several IDs."}


def standardized_retention(papers):
    """Pooled-weight retention on common exact-team-size × subfield cells.

    This is descriptive standardization of paper retention, not inverse-
    probability correction of author counts or a missing-at-random assumption.
    """
    cells = defaultdict(lambda: {y: [0, 0] for y in ("2024", "2025")})
    for p in papers:
        if usable(p):
            v = cells[(p["subfield"], p["slots"])][p["month"][:4]]
            v[0] += 1
            v[1] += not p["reasons"]
    common = {k: v for k, v in cells.items() if all(v[y][0] for y in ("2024", "2025"))}
    pool = sum(v[y][0] for v in common.values() for y in ("2024", "2025"))
    annual = []
    for y in ("2024", "2025"):
        all_n = sum(v[y][0] for v in cells.values())
        covered = sum(v[y][0] for v in common.values())
        standardized = sum(sum(v[z][0] for z in ("2024", "2025"))/pool * v[y][1]/v[y][0] for v in common.values()) if pool else None
        annual.append({"period": y, "usable_papers": all_n, "common_support_papers": covered,
                       "common_support_share": covered/all_n if all_n else None,
                       "raw_retention_usable": sum(v[y][1] for v in cells.values())/all_n if all_n else None,
                       "standardized_retention": standardized})
    return {"strata": "OpenAlex primary subfield × exact returned team size, usable bylines only",
            "weights": "Pooled 2024 and 2025 paper counts, restricted to cells present in both years",
            "common_cells": len(common), "all_cells": len(cells), "annual": annual,
            "interpretation": "A remaining gap is within the observed strata; this does not explain the cause or correct unique-author counts."}


def reference_cohort(before, after, method):
    """Follow baseline observed keys, retaining zeros; not validated careers."""
    before = [p for p in before if usable(p)]
    after = [p for p in after if usable(p)]
    def output(rows):
        values = Counter()
        for p in rows:
            values.update(a for a in p[method] if a is not None)
        return values
    first, second = output(before), output(after)
    continuing = set(first) & set(second)
    appearing = set(second) - set(first)
    return {"baseline_keys": len(first), "continuing_observed_keys": len(continuing),
            "zero_observed_followup_keys": len(set(first)-set(second)),
            "appearing_observed_keys": len(appearing),
            "baseline_full_distribution": distribution(first.values()),
            "followup_full_distribution_including_zeros": distribution([second[a] for a in first]),
            "followup_continuing_keys_distribution": distribution([second[a] for a in continuing]),
            "followup_appearing_keys_distribution": distribution([second[a] for a in appearing]),
            "interpretation": "2024 observed keys followed into 2025 on usable bylines. Zeros include coverage loss, missing IDs, name changes and nonpublication. Appearing keys are not established career entrants. No incumbent-behavior claim is identified."}


def flow(works):
    stage = Counter()
    by_publication_year = defaultdict(Counter)
    outside_years = Counter()
    for w in works:
        ids = arxiv_ids(w)
        if not ids:
            reason = "no_unique_modern_arxiv_id"
        elif len(ids) > 1:
            reason = "multiple_arxiv_ids"
        else:
            aid = next(iter(ids))
            if "2401" <= aid[:4] <= "2512":
                reason = "target_id_window"
            else:
                reason = "outside_target_id_window"
                outside_years["20"+aid[:2]] += 1
        stage[reason] += 1
        by_publication_year[str(w["publication_year"])][reason] += 1
    assert sum(stage.values()) == len(works)
    return {"acquired_works": len(works), "stages": dict(stage),
            "outside_target_window_by_id_year": dict(sorted(outside_years.items())),
            "by_openalex_publication_year": {y: dict(v) for y, v in sorted(by_publication_year.items())}}


def run(snapshot, output):
    works, source, duplicates = read_snapshot(snapshot)
    papers, diagnostic = prepare(works)
    raw_by_id = {w["id"]: w for w in works}
    data = {"schema_version": 1, "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "status": "Coverage audit; population participation and concentration interpretations on hold",
            "snapshot_manifest_sha256": hashlib.sha256((snapshot/"acquisition.json").read_bytes()).hexdigest(),
            "source_scope": source["query_scope"], "work_flow": flow(works), "link_diagnostics": diagnostic,
            "coverage_state_definition": "Paired first; then nonempty bylines with all IDs missing; then bylines with some IDs missing; then other exclusions. Missing-ID states take precedence when other exclusion flags overlap. This partition is accounting, not a causal attribution of exclusions.",
            "duplicate_cached_work_rows": duplicates,
            "observation_clock": {"created_date_available": sum(w.get("created_date") is not None for w in works),
                                  "updated_date_available": sum(w.get("updated_date") is not None for w in works),
                                  "note": "Created/indexing history was not collected. Updated date is not an indexing date or a history of author resolution. A single snapshot cannot reconstruct equal-age historical completeness."},
            "annual": [], "monthly": [], "rolling12": [], "by_team_size": [], "by_subfield": [], "by_publication_year": [], "by_metadata_update_month": []}
    for y in ("2024", "2025"):
        rows = [p for p in papers if p["month"].startswith(y)]
        paired = [p for p in rows if not p["reasons"]]
        bad_slots = Counter()
        for p in rows:
            for a in raw_by_id[p["work_id"]]["authorships"]:
                raw = (a.get("author") or {}).get("id")
                if author_key(raw) is None:
                    label = "null_or_absent" if not raw else "unknown_placeholder" if isinstance(raw, str) and raw.endswith("A9999999999") else "deleted_placeholder" if isinstance(raw, str) and raw.endswith("A5317838346") else "other_invalid_format"
                    bad_slots[label] += 1
        data["annual"].append({"period": y, **summarize(rows), "missing_id_slot_types": dict(bad_slots),
                               "partial_id_accounting": partial_credit(rows),
                               "orcid_on_paired_papers": orcid_opportunity(paired),
                               "orcid_on_usable_bylines": orcid_opportunity([p for p in rows if usable(p)])})
        for k in sorted({p["slots"] for p in rows}):
            data["by_team_size"].append({"period": y, "returned_slots": k, **summarize([p for p in rows if p["slots"] == k])})
        for field in sorted({p["subfield"] for p in rows}):
            data["by_subfield"].append({"period": y, "subfield": field, **summarize([p for p in rows if p["subfield"] == field])})
        for pub in (2024, 2025, 2026):
            data["by_publication_year"].append({"period": y, "openalex_publication_year": pub, **summarize([p for p in rows if p["publication_year"] == pub])})
        updated = defaultdict(list)
        for p in rows:
            updated[str(raw_by_id[p["work_id"]].get("updated_date") or "unknown")[:7]].append(p)
        for month, group in sorted(updated.items()):
            data["by_metadata_update_month"].append({"period": y, "metadata_update_month": month, **summarize(group)})
    for month in sorted({p["month"] for p in papers}):
        rows = [p for p in papers if p["month"] == month]
        data["monthly"].append({"period": month, **summarize(rows), "partial_id_accounting": partial_credit(rows)})
    months = [f"{y}-{m:02d}" for y in (2024, 2025) for m in range(1, 13)]
    for end in range(11, len(months)):
        start, last = months[end-11], months[end]
        data["rolling12"].append({"period": last, "start": start,
                                  **summarize([p for p in papers if start <= p["month"] <= last])})
    a, b = data["annual"]
    data["retention_gap_pp"] = {k: 100*(b["state_shares"][k]-a["state_shares"][k]) for k in a["states"]}
    logs = {"linked_papers": math.log(b["linked_papers"]/a["linked_papers"]),
            "retention": math.log(b["retention"]/a["retention"]),
            "paired_papers": math.log(b["paired_papers"]/a["paired_papers"])}
    assert math.isclose(logs["paired_papers"], logs["linked_papers"]+logs["retention"], abs_tol=1e-12)
    data["paper_log_accounting"] = logs
    data["standardized_retention"] = standardized_retention(papers)
    before = [p for p in papers if p["month"].startswith("2024")]
    after = [p for p in papers if p["month"].startswith("2025")]
    data["reference_cohort_diagnostics"] = {m: reference_cohort(before, after, m) for m in ("ids", "names")}
    output.mkdir(parents=True, exist_ok=True)
    (output/"retention_audit.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    d = run(args.snapshot, args.output)
    print(json.dumps({"work_flow": d["work_flow"], "annual": d["annual"],
                      "retention_gap_pp": d["retention_gap_pp"], "standardized_retention": d["standardized_retention"]}, indent=2))


if __name__ == "__main__":
    main()
