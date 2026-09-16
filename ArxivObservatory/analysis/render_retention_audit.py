"""Render the coverage audit, response to the second reply and a data figure."""
import argparse
import json
from pathlib import Path


def render(source, output):
    d = json.loads(source.read_text())
    a, b = d["annual"]
    n = lambda x: f"{x:,}"
    f = lambda x: f"{x:,.3f}"
    pct = lambda x: f"{100*x:.2f}%"
    lines = ["# Retention audit and response to the second review", "",
             "15 September 2026. **Population participation and concentration interpretations are on hold.** The dashboard now leads with coverage diagnostics. Earlier author-count and Gini comparisons remain archived measurements of selected records, not findings about the direction of change in mathematics.", "",
             "The main concern in the reply is accepted: the exclusion rule changes the observed paper trend, and qualifying a contributor-decline headline is insufficient. We now diagnose that selection directly and allocate missing credit explicitly. The cause of missing IDs has been narrowed but not established; no adjustment here neutralizes it.", "",
             "## 1. What causes the observed retention gap?", "",
             "| Linked-paper state | 2024 | 2025 | Change in share of linked papers |", "|---|---:|---:|---:|"]
    for key, label in (("paired", "Retained for paired identity comparison"), ("all_ids_missing", "Entire byline has no IDs"), ("some_ids_missing", "Some byline IDs missing"), ("other_byline_exclusion", "Other byline exclusions")):
        lines.append(f"| {label} | {n(a['states'][key])} | {n(b['states'][key])} | {d['retention_gap_pp'][key]:+.3f} pp |")
    lines += [f"| All uniquely linked target-window papers | {n(a['linked_papers'])} | {n(b['linked_papers'])} | — |", "",
              "States are mutually exclusive, with missing-ID states taking precedence when another exclusion flag overlaps. They describe where retained coverage is lost; they do not establish a causal missingness mechanism.", "",
              f"Entirely unidentified bylines account for **{d['retention_gap_pp']['all_ids_missing']:.2f} percentage points** of the **{-d['retention_gap_pp']['paired']:.2f}-point** retention decline. The missing source IDs are null/absent, rather than the two known provider placeholders. This is substantial absence of identification at the paper level, not just isolated unidentified coauthors.", "",
              "The absence is concentrated in late 2025: November and December contain 1,577 of the 2,090 entirely unidentified bylines (75.45%). Such bylines account for 855/2,792 linked November papers (30.62%) and 722/3,135 December papers (23.03%). The monthly series locates this concentration; it does not establish indexing lag as its cause.", "",
              "### Team size and subfield", "",
              "Retention declines even within fixed returned team sizes. The following rows use all uniquely linked papers at each team size, before byline exclusions.", "",
              "| Returned team size | 2024 papers | 2024 retention | 2025 papers | 2025 retention |", "|---|---:|---:|---:|---:|"]
    for k in range(1, 7):
        x, y = [next(v for v in d["by_team_size"] if v["period"] == year and v["returned_slots"] == k) for year in ("2024", "2025")]
        lines.append(f"| {k} | {n(x['linked_papers'])} | {pct(x['retention'])} | {n(y['linked_papers'])} | {pct(y['retention'])} |")
    x, y = d["standardized_retention"]["annual"]
    lines += ["", f"Using the same pooled paper weights for exact-team-size × OpenAlex-primary-subfield cells gives standardized retention of **{pct(x['standardized_retention'])} versus {pct(y['standardized_retention'])}**. Common cells cover {pct(x['common_support_share'])} and {pct(y['common_support_share'])} of usable bylines. The gap therefore remains within those observed strata; a different mix of team sizes and subfields does not explain it away. This is a diagnostic of retention, not a correction of unique-author counts.", "",
              "| OpenAlex subfield | 2024 linked papers | 2024 retention | 2025 linked papers | 2025 retention |", "|---|---:|---:|---:|---:|"]
    fields = sorted({r["subfield"] for r in d["by_subfield"]})
    for field in fields:
        x, y = [next(v for v in d["by_subfield"] if v["period"] == year and v["subfield"] == field) for year in ("2024", "2025")]
        lines.append(f"| {field} | {n(x['linked_papers'])} | {pct(x['retention'])} | {n(y['linked_papers'])} | {pct(y['retention'])} |")
    lines += ["", "### Indexing lag is a hypothesis, not an established explanation", "",
              "The frozen projection contains work update dates but no creation/indexing dates or historical byline states. An update timestamp is not an indexing clock. This single snapshot cannot recreate what both cohorts looked like at equal time since indexing. Publication-year and metadata-update-month retention tables are supplied in the JSON as diagnostics, without interpreting either timestamp as first indexing.", "",
              "The next discriminating evidence is repeated or archived metadata for the same papers: when IDs were absent, added, replaced or lost, by source and cohort. Equal follow-up would improve a specifically defined comparison, but matching ages or overall retention rates alone does not equalize who is missing. Randomly discarding additional retained papers would not repair selective loss. A U-shaped historical completeness curve is also a hypothesis to test, not a demonstrated property of this snapshot.", "",
              "## 2. Exact paper accounting, and what normalization cannot show", "",
              r"For linked papers L and retained fraction c, paired papers R satisfy \(R=Lc\), hence", "",
              r"\[\Delta\log R=\Delta\log L+\Delta\log c.\]", "",
              "| Natural-log change, 2024 to 2025 | Value |", "|---|---:|"]
    for key, label in (("linked_papers", "Linked paper count"), ("retention", "Retention fraction"), ("paired_papers", "Sum: retained paper count")):
        lines.append(f"| {label} | {d['paper_log_accounting'][key]:+.6f} |")
    lines += ["", "The paper sign reversal is exactly explained by this accounting: linked counts rise 1.94% while retained counts fall 9.04%. This does not allocate the change in distinct authors to causes; unique keys recur across papers. The review's retention-only simulation establishes a possible mechanism, not that its assumed mechanism generated these records.", "",
              r"The separate normalization argument needs correcting. \(A/P\) and \(P/A\) are reciprocals; a rising \(A/P\) while total A falls is not a contradictory estimate of the same quantity. Counts and ratios answer different questions. Dividing by retained papers is not a missingness correction.", "",
              "## 3. Partial-ID accounting: keep the unallocated credit", "",
              "Use every returned byline that passes the non-ID rules, including papers with some or all IDs missing. For each k-slot byline, assign 1/k to each valid ID and retain 1/k as unallocated for each unidentified slot. For truncated, collective, repeated-ID or otherwise unusable bylines, retain one whole unallocated paper equivalent. No synthetic unknown author is inserted into a count or Gini.", "",
              "| Coverage / accounting quantity | 2024 | 2025 |", "|---|---:|---:|"]
    specifications = [("usable_byline_papers", "Papers with usable returned bylines", 0), ("unusable_byline_papers", "Papers with unusable bylines", 0),
                      ("identified_id_keys", "Observed valid IDs on usable bylines", 0), ("raw_name_keys_usable", "Raw name keys on the same usable bylines", 0),
                      ("allocated_credit_to_ids", "Paper credit allocated to valid IDs", 3), ("unallocated_missing_id_credit", "Unallocated credit: missing IDs", 3),
                      ("unallocated_unusable_byline_credit", "Unallocated credit: unusable bylines", 0), ("total_unallocated_credit", "Total unallocated credit", 3),
                      ("mean_allocated_credit_per_id", "Mean allocated credit per observed ID", 3), ("usable_papers_per_identified_id", "Usable papers / observed IDs (different ratio)", 3)]
    for key, label, places in specifications:
        lines.append(f"| {label} | {a['partial_id_accounting'][key]:,.{places}f} | {b['partial_id_accounting'][key]:,.{places}f} |")
    lines += ["", r"\[P_{linked}=C_{identified}+U_{missing\ IDs}+U_{unusable\ byline}.\]", "",
              r"Within usable bylines, \(\bar f_{identified}=(P_{usable}-U_{missing\ IDs})/A_{identified}\), which is not \(P_{usable}/A_{identified}\) when credit is unallocated.", "",
              "These identities reconcile for each month and each year. k remains the returned slot count, not an independently verified original-arXiv byline. The counts of missing people, their distribution of output and complete-population concentration remain unknown. Partial credit makes the missing contribution visible; it does not restore the missing identities.", "",
              "The new partial path is `analysis/retention_audit.py`. The legacy `democratization.py` partial-byline output is not used and must not be treated as a corrected entry point.", "",
              "## 4. The upstream reduction is mostly the declared time-window filter", "",
              "| Acquisition-to-analysis stage | Works / papers |", "|---|---:|",
              f"| Acquired OpenAlex works, publication years 2024–2026 | {n(d['work_flow']['acquired_works'])} |",
              f"| One modern arXiv ID outside the 2024–2025 target window | {n(d['work_flow']['stages']['outside_target_id_window'])} |",
              f"| Ambiguous: multiple arXiv IDs | {n(d['work_flow']['stages']['multiple_arxiv_ids'])} |",
              f"| No unique modern arXiv ID | {n(d['work_flow']['stages']['no_unique_modern_arxiv_id'])} |",
              f"| Uniquely linked papers in the target window | {n(a['linked_papers']+b['linked_papers'])} |",
              f"| Retained paired papers after byline exclusions | {n(a['paired_papers']+b['paired_papers'])} |", "",
              "Of the 32,552 outside-window works, 30,062 have 2026 arXiv IDs and 2,490 have older IDs. Calling the entire 39% reduction unexplained attrition is incorrect. The acquisition included 2026 publication dates to capture later published versions; not every acquired work was intended to enter the two upload cohorts. The JSON breaks the stages down by OpenAlex publication year. Ambiguous/no-ID records cannot be assigned to a target upload cohort without additional evidence.", "",
              "This accounting does not establish external coverage: OpenAlex Mathematics differs from arXiv primary mathematics, and relevant works outside the query's publication-year limits can be omitted. The existing manifest overlap remains a separate check. We now consistently distinguish acquired works, linked target-window papers, usable bylines and retained paired papers.", "",
              "## 5. ORCID: the observation opportunity matters", "",
              "The reply interprets 5/2,216 and 29/3,699 as low measured split rates. Most denominator ORCIDs, however, occur on only one retained paper. Cross-paper splitting cannot be observed without repeated observations of the same source ORCID.", "",
              "| Source-ORCID diagnostic on paired papers | 2024 | 2025 |", "|---|---:|---:|"]
    for key, label in (("distinct_source_orcids", "Distinct recorded source ORCIDs"), ("orcids_on_multiple_papers", "ORCIDs observed on at least two papers"), ("multiple_ids_and_multiple_papers", "Those repeated ORCIDs associated with multiple IDs")):
        lines.append(f"| {label} | {n(a['orcid_on_paired_papers'][key])} | {n(b['orcid_on_paired_papers'][key])} |")
    lines.append(f"| Multiple-ID share among repeated ORCIDs | {pct(a['orcid_on_paired_papers']['multiple_id_share_repeated_orcids'])} | {pct(b['orcid_on_paired_papers']['multiple_id_share_repeated_orcids'])} |")
    lines += ["", "The 6.67% and 14.65% figures are also mapping diagnostics, not validated split rates: the subset is selected and source ORCIDs can be incorrectly attached. They show why the small unconditional percentages cannot establish that splitting is negligible. Neither percentage is a proven floor for population error. Profile-level ORCIDs were not substituted for source ORCIDs. See [OpenAlex's source/profile distinction](https://help.openalex.org/data/authors/orcid/).", "",
              "## 6. Retained methodological decisions", "",
              "**Identity.** Raw names remain an identity-sensitivity diagnostic alongside IDs. We retire any suggestion that this is a correction or a bracket around real people. A net excess of names over IDs cannot establish that the name representation never combines split IDs: splits and homonyms can coexist with spelling variants. The independent audit, not a new unvalidated merger, is the route to a person-level estimate.", "",
              "**Partial merging.** The renewed claim that minority merging generically raises Gini still requires a probability model. It is not implied by partial merging alone. For outputs [1,2,4,8,16,32,64,128,256,512], merging the two smallest of ten keys gives [3,4,8,16,32,64,128,256,512]; Gini falls from 0.70196 to 0.66906. No values coincide after merging. The strict decrease persists under sufficiently small perturbations, so it is not a measure-zero equality case. The review's simulations illustrate their chosen models; their code and seeds were not supplied for reproduction.", "",
              "**Entry and incumbents.** A rising singleton share does not establish an influx of entrants; paper loss can produce the same pattern. The audit JSON includes a 2024 observed-key reference cohort followed into 2025 with zero-output keys retained, and separate observed continuing/appearing distributions. These are accounting checks, not validated career-entry or incumbent-behavior results, because missingness and identity changes also produce apparent zeros and entries. Longer history and identity validation remain necessary.", "",
              "**Uncertainty.** A paper-cluster bootstrap may suit a specified paper-sampling model, but it is not automatically the correct uncertainty calculation. Authors recur across papers, so independent paper clusters are an assumption, not a consequence of the data structure. Neither resampling unit solves identity error or selection. No generic bootstrap interval is attached to these exact frozen-record diagnostics.", "",
              "**Disclosure cutoff.** The stronger zero-day check is confirmed from the original committed page: 7 August 2026 is the only zero Friday; recent Fridays average 158.5 papers with a minimum of 113. The following Saturday is also the only zero Saturday; recent Saturdays average 93.36 with a minimum of 69. This is strong evidence of an incomplete end window. A final complete cutoff needs the ingestion ledger; the owner-maintained disclosure dashboard should not treat those days as established complete observations. No original scan or classification pipeline was changed here.", "",
              "**Later AI design.** [Rambachan and Roth (2023)](https://academic.oup.com/restud/article-abstract/90/5/2555/7039335) is an appropriate addition to the prior-work plan: examine sensitivity to explicitly bounded departures from parallel trends if a credible subfield design is developed. The bounds need substantive justification; the method does not itself establish AI exposure, comparable measurement or absence of confounding. No causal AI analysis is run here.", "",
              "The mathematical accounting and mathematics-bibliometric precedents in the revised protocol are retained. This stage contributes a reproducible measurement audit. It does not establish a change in democratization, elitism or AI effects.", "",
              "## 7. Reproduction and remaining decisions", "",
              "The offline comparison, retention audit, aggregate results and dashboard source are submitted in [draft PR #2](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/2), with the protocol and historical-extension note in [draft PR #3](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/3). This September 16 repository update incorporates the previously supplied review extensions. The branches remain draft contributions for owner review; main is unchanged.", "",
              "The private dashboard supplies the updated offline analysis, reports and frozen acquisition manifest as a downloadable audit package. It includes the original acquisition helper as a separately labelled reference, and the existing mathematics ID list used for the overlap check. The projected metadata snapshot supplied earlier is a separate required input, available as a download in this conversation. A fresh API query would not reproduce that frozen snapshot. External review needs access to those exact bytes or an owner-approved deposit; a hash alone is insufficient.", "",
              "The repository's contribution rules require contributed analysis to run offline and leave acquisition campaigns and main merges to the owner. A repository location for the network acquisition helper requires an explicit owner decision; it should not be slipped into the offline module. No new acquisition, paid API call, arXiv download, pipeline change or main-branch merge occurred.", "",
              "From an analysis checkout containing the supplied updated modules:", "",
              "    python3 -m analysis.retention_audit --snapshot /path/to/frozen_snapshot --output /path/to/results", "",
              "    python3 -m analysis.render_retention_audit --input /path/to/results/retention_audit.json --output /path/to/results", "",
              f"Acquisition manifest SHA-256: `{d['snapshot_manifest_sha256']}`. All cached-page hashes and partition counts were checked. Six new audit fixtures plus sixteen existing focused checks pass (22 total). The archive and raw-source metadata are not committed to the research repository. No manual identity, classifier-gold or full upstream-suite validation is claimed.", "",
              "Next evidence needed: the existing metadata export for exact frame reconciliation, and repeated or archival records that can establish the origin and evolution of the entirely missing-ID bylines. The historical extension follows a declared coverage design; it is not a substitute for resolving the present measurement failure.", ""]
    output.mkdir(parents=True, exist_ok=True)
    (output/"RETENTION_AUDIT.md").write_text("\n".join(lines))
    plot(d, output)


def plot(d, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    rows = d["rolling12"]
    xs = list(range(len(rows)))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 8.2), sharex=True)
    for key, label, color in (("linked_papers", "Linked target-window papers", "#365bc9"),
                              ("paired_papers", "Retained paired papers", "#a76519")):
        axes[0].plot(xs, [r[key] for r in rows], color=color, linewidth=2.5, label=label)
    axes[0].set_ylabel("Papers in window")
    axes[0].yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v/1000:.1f}k"))
    axes[1].plot(xs, [100*r["retention"] for r in rows], color="#a76519", linewidth=2.5)
    axes[1].set_ylabel("Retained (%)")
    for key, label, color in (("all_ids_missing", "Entire byline has no IDs", "#9d3150"),
                              ("some_ids_missing", "Some byline IDs missing", "#7555a7")):
        axes[2].plot(xs, [100*r["state_shares"][key] for r in rows], color=color, linewidth=2.5, label=label)
    axes[2].set_ylabel("Linked papers (%)")
    for ax in axes:
        ax.grid(axis="y", alpha=.18)
        ax.margins(x=.03, y=.2)
    axes[0].legend(frameon=False, fontsize=9, ncol=2)
    axes[2].legend(frameon=False, fontsize=9, ncol=2)
    ticks = [0, 3, 6, 9, 12]
    axes[-1].set_xticks(ticks, [rows[i]["period"] for i in ticks])
    axes[-1].set_xlabel("End of trailing 12-month window; arXiv ID month proxy")
    fig.suptitle("Coverage audit\nParticipation and concentration interpretations on hold", x=.12, y=.98,
                 ha="left", fontsize=17, fontweight="bold")
    fig.text(.12, .015, "Frozen OpenAlex subset · Snapshot: 15 Sep 2026 · Overlapping windows\nMissing-ID states take precedence when another exclusion flag overlaps.\nOpenAlex Mathematics and publication-year limits do not define an arXiv mathematics census.",
             color="#53647b", fontsize=9, linespacing=1.5)
    fig.tight_layout(rect=[0, .10, 1, .91], h_pad=1.5)
    for ext in ("png", "svg"):
        fig.savefig(output/f"retention_audit.{ext}", dpi=180, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.input, args.output)
