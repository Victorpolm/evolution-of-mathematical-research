"""Offline contributor populations and top-decile output on paired papers.

Consumes the existing frozen cache; exports aggregates only, never identities.
Full coauthored-paper counts deduplicate a key within each paper. Fractional
credit retains all byline slots, including repeated raw-name strings.
"""
import argparse
from collections import Counter, defaultdict
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

from .historical_participation import months, read_compact


def top_decile(values):
    """Exact 10% rank mass with proportional allocation across boundary ties.

    Scores rounded to 12 decimals define ties; unrounded scores define credit.
    This avoids arbitrary identity-based tie breaking and ceiling bias for
    populations whose size is not divisible by ten.
    """
    values = list(values)
    if any(not math.isfinite(x) or x <= 0 for x in values):
        raise ValueError("Rank only active keys with finite, positive output")
    n = len(values)
    if not n:
        return {"contributors": 0, "group_mass": 0, "share": None,
                "threshold": None, "strictly_above": 0, "boundary_ties": 0,
                "boundary_weight": None, "top_output": 0, "total_output": 0,
                "top_mean": None, "other90_mean": None, "mean_ratio": None}
    groups = defaultdict(list)
    for v in values:
        groups[round(v, 12)].append(v)
    mass = n / 10
    remaining = mass
    included, outputs = 0, []
    for score in sorted(groups, reverse=True):
        group = groups[score]
        if remaining <= len(group):
            weight = remaining / len(group)
            outputs.append(weight * math.fsum(group))
            threshold, ties, above = score, len(group), included
            break
        outputs.append(math.fsum(group))
        included += len(group)
        remaining -= len(group)
    total, top = math.fsum(values), math.fsum(outputs)
    top_mean = top / mass
    other_mean = (total - top) / (n - mass)
    return {"contributors": n, "group_mass": mass, "share": top / total,
            "threshold": threshold, "strictly_above": above,
            "boundary_ties": ties, "boundary_weight": weight,
            "top_output": top, "total_output": total,
            "top_mean": top_mean, "other90_mean": other_mean,
            "mean_ratio": top_mean / other_mean}


def output_counts(papers, method):
    fractional, coauthored = defaultdict(float), Counter()
    for paper in papers:
        keys = paper[method]
        k = paper["slots"]
        if paper["reasons"] or not k or len(keys) != k or any(not v for v in keys):
            raise ValueError("Contributor analysis requires complete paired bylines")
        coauthored.update(set(keys))
        for key in keys:
            fractional[key] += 1 / k
    if not math.isclose(math.fsum(fractional.values()), len(papers), abs_tol=1e-8):
        raise ValueError("Fractional paper-credit conservation failed")
    return fractional, coauthored


def period_row(period, papers, full_populations):
    row = {"period": period, "papers": len(papers),
           "authorship_slots": sum(p["slots"] for p in papers)}
    for method in ("names", "ids"):
        fractional, coauthored = output_counts(papers, method)
        if not set(coauthored).issubset(full_populations[method]):
            raise ValueError("Window keys must belong to the full-study population")
        active, full = len(coauthored), len(full_populations[method])
        j = sum(coauthored.values())
        row[method] = {
            "authors": active,
            "papers_per_active_contributor": len(papers) / active if active else None,
            "papers_per_study_contributor": len(papers) / full if full else None,
            "coauthored_participations": j,
            "coauthored_papers_per_active_contributor": j / active if active else None,
            "fractional": top_decile(fractional.values()),
            "coauthored": top_decile(coauthored.values()),
        }
    return row


def analyze(papers, start, end):
    paired = [p for p in papers if not p["reasons"]]
    if any(not start <= p["month"] <= end for p in paired):
        raise ValueError("Paper outside the requested observation window")
    population = {m: {k for p in paired for k in p[m]} for m in ("names", "ids")}
    by_month = defaultdict(list)
    for p in paired:
        by_month[p["month"]].append(p)
    window = months(start, end)
    study = period_row(f"{start} to {end}", paired, population)
    annual, rolling = [], []
    monthly = [period_row(m, by_month[m], population) for m in window]
    for year in sorted({m[:4] for m in window}):
        selected = [m for m in window if m.startswith(year)]
        if len(selected) == 12:
            annual.append(period_row(year, [p for m in selected for p in by_month[m]], population))
    for i in range(11, len(window)):
        selected = window[i - 11:i + 1]
        rolling.append(period_row(window[i], [p for m in selected for p in by_month[m]], population))
    return {"study": study, "annual": annual, "monthly": monthly, "rolling12": rolling}


def verify_baseline(data, baseline):
    if data["snapshot_manifest_sha256"] != baseline["snapshot_manifest_sha256"]:
        raise ValueError("Baseline and contributor analysis must use the same snapshot")
    for mode in ("annual", "monthly", "rolling12"):
        if len(data[mode]) != len(baseline[mode]):
            raise ValueError("Baseline period count changed")
        for a, b in zip(data[mode], baseline[mode]):
            if (a["period"], a["papers"], a["authorship_slots"]) != (b["period"], b["papers"], b["authorship_slots"]):
                raise ValueError("Baseline paper population changed")
            for m in ("names", "ids"):
                if a[m]["authors"] != b[m]["authors"]:
                    raise ValueError("Baseline contributor population changed")
                if not math.isclose(a[m]["papers_per_active_contributor"], b[m]["papers_per_author"], abs_tol=1e-12):
                    raise ValueError("Baseline annual/window ratio changed")


def write_report(data, output):
    study, annual = data["study"], data["annual"]
    text = ["# Contributor populations and the most prolific decile", "",
        "Computed offline from the same frozen OpenAlex metadata and exactly the same paired "
        "papers as the historical participation analysis. All outputs describe observed keys, "
        "not validated people. No additional API requests or identity-merging algorithm.", "",
        "## Why papers per contributor can be less than one", "",
        "One paper with three distinct contributors gives P/A = 1/3, although each contributor "
        "coauthored one paper. P/A is mean fractional paper credit, not mean coauthored papers.", "",
        "Let S_p contain all k_p returned author slots of retained paper p, and g_m(s) map a slot "
        "to a raw-name key or an OpenAlex author ID. Define", "",
        r"$$c^{(m)}_{it}=\sum_{p\in t}\sum_{s\in S_p}\frac{\mathbf{1}\{g_m(s)=i\}}{k_p},\qquad f^{(m)}_{it}=\sum_{p\in t}\mathbf{1}\{i\in g_m(S_p)\}.$$", "",
        "Then sum_i c_it = P_t. Full coauthored-paper counts f_it count each key once per paper; "
        "their sum J_t can exceed P_t. For names, J_t can be less than byline-slot count I_t "
        "when several slots have the same string. Earlier archived slot-based statistics remain unchanged.", "",
        "## Three denominators / time horizons", "",
        "- P_t/A_t: papers in a year or window divided by distinct keys active on those same papers.",
        "- P_t/A_all: the same papers divided by the union of keys observed anywhere in 2010–2025. "
        "Keys inactive in t contribute zero. This is a fixed retrospective pool, not the active research workforce.",
        "- P_all/A_all: all retained papers over 2010–2025 divided by that union. This is a 16-year total per key, not an annual rate.",
        "", "A_all is computed independently for each identity definition and is never a sum of annual counts. "
        "Changing the study endpoints changes A_all. With a fixed denominator, the P_t/A_all trend "
        "has exactly the same percentage changes as paper counts; it cannot separate growth in participation from output.", "",
        f"Retained papers in the full study: **{study['papers']:,}**.", "",
        "| Identity definition | Full-study distinct keys | P_all/A_all | Mean coauthored papers over whole study |",
        "|---|---:|---:|---:|"]
    for m, label in (("names", "Distinct raw names"), ("ids", "OpenAlex author IDs")):
        r = study[m]
        text.append(f"| {label} | {r['authors']:,} | {r['papers_per_active_contributor']:.4f} | {r['coauthored_papers_per_active_contributor']:.4f} |")
    text += ["", "## Annual denominator comparison", "",
        "| Year | Papers | Active names | Active IDs | P/active names | P/active IDs | P/all names | P/all IDs |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in annual:
        n, i = r["names"], r["ids"]
        text.append(f"| {r['period']} | {r['papers']:,} | {n['authors']:,} | {i['authors']:,} | "
            f"{n['papers_per_active_contributor']:.4f} | {i['papers_per_active_contributor']:.4f} | "
            f"{n['papers_per_study_contributor']:.4f} | {i['papers_per_study_contributor']:.4f} |")
    text += ["", "## Most prolific decile", "",
        "Rank active keys separately for each identity definition, time window and measure. "
        "Fractional credit is the primary concentration measure; coauthored-paper counts are a sensitivity view. "
        "The whole-study decile is ranked on cumulative 2010–2025 output. Annual/window deciles are "
        "re-ranked each period, not a fixed set of contributors followed through time.", "",
        "Use an exact top-decile mass of 0.1 A. At the cutoff, allocate the remaining membership "
        "weight proportionally across all tied keys; there is no arbitrary name/ID tie-break. "
        "Fractional scores rounded to 12 decimal places define ties only; unrounded values determine output. "
        "The JSON records the threshold, strictly-above count, tied count and common boundary weight.", "",
        r"$$S_{10,t}^{(m)}=\frac{\sum_i w_{it}x_{it}}{\sum_i x_{it}},\qquad \sum_i w_{it}=0.1A_t,\qquad \frac{\bar{x}_{\mathrm{top10},t}}{\bar{x}_{\mathrm{other90},t}}=\frac{9S_{10,t}}{1-S_{10,t}}.$$", "",
        "For fractional output, the share denominator is P. For full counts, it is J, the sum of "
        "key–paper participations, not a count of distinct papers. A single coauthored paper can "
        "contribute to several keys. Equal output for all keys would give a 10% share and a mean ratio of 1.", "",
        "### Annual top-decile shares", "",
        "| Year | Fractional: names | Fractional: IDs | Coauthored: names | Coauthored: IDs |",
        "|---|---:|---:|---:|---:|"]
    for r in annual:
        text.append(f"| {r['period']} | {r['names']['fractional']['share']:.2%} | {r['ids']['fractional']['share']:.2%} | "
            f"{r['names']['coauthored']['share']:.2%} | {r['ids']['coauthored']['share']:.2%} |")
    text += ["", "### Full-study cumulative ranking", "",
        "| Identity | Ranking measure | Top 10% share | Top 10% mean | Other 90% mean | Mean ratio |",
        "|---|---|---:|---:|---:|---:|"]
    for m, label in (("names", "Names"), ("ids", "IDs")):
        for measure in ("fractional", "coauthored"):
            r = study[m][measure]
            text.append(f"| {label} | {measure} | {r['share']:.2%} | {r['top_mean']:.4f} | {r['other90_mean']:.4f} | {r['mean_ratio']:.2f} |")
    a, b = annual[0], annual[-1]
    text += ["", "## Descriptive findings and limits", ""]
    for m, label in (("names", "distinct names"), ("ids", "OpenAlex IDs")):
        x, y = a[m]["fractional"]["share"], b[m]["fractional"]["share"]
        text.append(f"- Under {label}, the annual top-decile fractional share changes from {x:.2%} "
                    f"in {a['period']} to {y:.2%} in {b['period']} ({100*(y-x):+.2f} percentage points). "
                    f"The cumulative whole-study share is {study[m]['fractional']['share']:.2%}.")
    text += ["", "The whole-study and annual concentration measures have different exposure lengths and "
        "membership rules. Their levels should not be read as a change over time. A top-decile share "
        "describes concentration of recorded output; it does not measure research quality, contribution "
        "effort or a causal AI effect. Changing retention, OpenAlex coverage, field composition, team size "
        "and identity splits/merges can affect comparisons. The two identity definitions are sensitivity "
        "analyses, not lower/upper bounds on people. Current metadata can differ from original arXiv bylines.", "",
        "## Provenance and reproduction", "",
        f"Snapshot manifest SHA-256: `{data['snapshot_manifest_sha256']}`.", "",
        "The analysis verifies every compressed metadata page and reproduces P, A and slot counts for "
        "all 16 annual, 192 monthly and 181 rolling windows of the historical baseline. Metadata was "
        "retrieved on 16 September 2026; analysis dates come from arXiv ID months. Source scope: "
        "OpenAlex works indexed in arXiv, primary field Mathematics (26), publication years 2010–2026, "
        "with arXiv ID dates 2010–2025. Ambiguous work-to-paper links and incomplete paired bylines "
        "remain excluded exactly as documented in the historical analysis.", "",
        "```sh", "python -m analysis.contributor_populations --snapshot /path/to/frozen-cache \\",
        "  --baseline reports/historical_participation_20260916/historical_participation.json \\",
        "  --out reports/contributor_populations_20260916", "```", ""]
    (output / "CONTRIBUTOR_POPULATIONS.md").write_text("\n".join(text))


def write_csv(data, output):
    fields = ["period", "papers", "identity", "active_contributors", "study_contributors",
        "papers_per_active_contributor", "papers_per_study_contributor",
        "coauthored_papers_per_active_contributor", "fractional_top10_share", "coauthored_top10_share",
        "fractional_top10_mean", "fractional_other90_mean", "coauthored_top10_mean", "coauthored_other90_mean"]
    with (output / "contributor_populations_annual.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in data["annual"]:
            for m in ("names", "ids"):
                r = row[m]
                writer.writerow({"period": row["period"], "papers": row["papers"], "identity": m,
                    "active_contributors": r["authors"], "study_contributors": data["study"][m]["authors"],
                    **{k: r[k] for k in fields[5:8]},
                    "fractional_top10_share": r["fractional"]["share"], "coauthored_top10_share": r["coauthored"]["share"],
                    "fractional_top10_mean": r["fractional"]["top_mean"], "fractional_other90_mean": r["fractional"]["other90_mean"],
                    "coauthored_top10_mean": r["coauthored"]["top_mean"], "coauthored_other90_mean": r["coauthored"]["other90_mean"]})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text())
    start, end = baseline["upload_window"]
    print("Validating frozen metadata and preparing paired papers…", flush=True)
    papers, _, diagnostic, _ = read_compact(args.snapshot, start, end, months("2010-01", "2026-12"))
    print("Computing contributor unions, window ratios and top-decile output…", flush=True)
    data = {"schema_version": 1, "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "upload_window": [start, end], "source_scope": baseline["source_scope"],
        "snapshot_manifest_sha256": hashlib.sha256((args.snapshot / "acquisition.json").read_bytes()).hexdigest(),
        "retrieval_interval": baseline["retrieval_interval"], "normalizer": baseline["normalizer"],
        "diagnostics": diagnostic,
        "definitions": {
            "active_population": "Union of distinct keys on paired papers within the selected window",
            "study_population": "Union of distinct keys on all paired papers dated 2010-01 through 2025-12",
            "fractional": "One/k credit per byline slot; credits of slots sharing a key accumulate",
            "coauthored": "One full paper per distinct key per paper; repeated raw-name slots counted once",
            "decile": "Rank active keys separately by identity, window and output measure; exact 10% population mass",
            "ties": "Proportional membership across cutoff ties; scores rounded to 12 decimals only for ranking",
            "study_ranking": "Cumulative output over the full observation window, not an average of window deciles",
            "interpretation": "Observed contributor keys in a selected OpenAlex population, not validated people"},
        **analyze(papers, start, end)}
    verify_baseline(data, baseline)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "contributor_populations.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    write_csv(data, args.out)
    write_report(data, args.out)
    print(json.dumps({"status": "complete", "baseline_windows_verified": 389,
        "papers": data["study"]["papers"],
        "full_study_contributors": {m: data["study"][m]["authors"] for m in ("names", "ids")}}, indent=2), flush=True)


if __name__ == "__main__":
    main()
