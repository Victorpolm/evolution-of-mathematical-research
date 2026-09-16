"""Render an aggregate OpenAlex comparison as a report and shareable figure."""
import argparse
import json
from pathlib import Path


def fmt(v, places=0):
    return "—" if v is None else f"{v:,.{places}f}"


def delta(a, b):
    return "—" if not a else f"{(b/a-1)*100:+.2f}%"


def render(source, output):
    d = json.loads(source.read_text())
    a, b = d["annual"]
    names = {"ids": "OpenAlex IDs", "names": "Distinct names"}
    rows = [("Paired papers", a["papers"], b["papers"], 0),
            ("OpenAlex author IDs", a["ids"]["authors"], b["ids"]["authors"], 0),
            ("Distinct raw-name keys", a["names"]["authors"], b["names"]["authors"], 0),
            ("Authorship slots", a["authorship_slots"], b["authorship_slots"], 0),
            ("Mean team size I/P", a["mean_team_size"], b["mean_team_size"], 3),
            ("Mean participation I/A — IDs", a["ids"]["incidences_per_author"], b["ids"]["incidences_per_author"], 3),
            ("Mean participation I/A — names", a["names"]["incidences_per_author"], b["names"]["incidences_per_author"], 3),
            ("Papers per ID P/A", a["ids"]["papers_per_author"], b["ids"]["papers_per_author"], 3),
            ("Papers per name P/A", a["names"]["papers_per_author"], b["names"]["papers_per_author"], 3)]
    lines = ["# OpenAlex comparison: mathematics papers and active author keys", "", "Computed 15 September 2026. **Interim descriptive analysis, 2024 versus 2025.**", "",
             f"**The main finding is unequal coverage.** Linked papers before the authorship gate increase by **{delta(a['quality']['linked_papers'],b['quality']['linked_papers'])}**, but retention falls from **{100*a['quality']['retention']:.2f}% to {100*b['quality']['retention']:.2f}%**. Additional exclusions more than offset that increase: the paired paper count falls by **{delta(a['papers'],b['papers'])}**. Most exclusions involve missing author IDs. An apparent decline among retained author keys cannot establish a decline in the full mathematics community.", "",
             f"On the same retained papers, paper counts changed by **{delta(a['papers'], b['papers'])}**, active OpenAlex IDs by **{delta(a['ids']['authors'], b['ids']['authors'])}**, and distinct recorded names by **{delta(a['names']['authors'], b['names']['authors'])}**.", "",
             f"Papers per author key changed by **{delta(a['ids']['papers_per_author'], b['ids']['papers_per_author'])}** using IDs and **{delta(a['names']['papers_per_author'], b['names']['papers_per_author'])}** using names. These quantities describe a selected OpenAlex-covered population. They do not establish population-wide or individual productivity changes.", "",
             "## Main results", "", "| Measure | 2024 | 2025 | Change |", "|---|---:|---:|---:|"]
    lines += [f"| {label} | {fmt(x,p)} | {fmt(y,p)} | {delta(x,y)} |" for label,x,y,p in rows]
    lines += ["", "Both methods use exactly the same papers and OpenAlex authorship slots. The paper numerator and team sizes are identical across methods. Counts represent active author keys, not uploading accounts, and neither definition is a reliable bound on the number of real people.", "",
              "## Population, dates and coverage", "",
              f"Retrieved **{d['diagnostics']['candidate_works']:,} unique OpenAlex works** from its default core corpus using `indexed_in:arxiv`, `primary_topic.field.id:26`, and OpenAlex publication years 2024–2026. The query was partitioned by publication month and fully paginated. Each partition's retrieved count is required to equal its reported population count; cached page hashes are verified before analysis.", "",
              "The analysis then extracts modern arXiv IDs from OpenAlex location URLs, arXiv OAI location identifiers or arXiv DOIs. Versions collapse to one ID. Exactly one arXiv ID per work and one OpenAlex work per arXiv ID are required. We retain IDs with months January 2024 through December 2025. The ID month is an upload-month proxy, not a verified first-submission timestamp. We never use a journal-publication date as the upload date.", "",
              "The 2026 publication-year extension captures some later published versions of 2024–2025 uploads. Nevertheless, the query can omit relevant uploads assigned an OpenAlex publication year before 2024 or after 2026. OpenAlex Mathematics is a topic-based classification; it is not the arXiv primary-category definition in the longer-term protocol. Expansion-corpus works are outside this query.", "",
              "| Upload year | Unique linked papers | Paired papers | Retention among linked papers |", "|---|---:|---:|---:|"]
    for r in d["annual"]:
        q=r["quality"]
        lines.append(f"| {r['period']} | {fmt(q['linked_papers'])} | {fmt(q['paired_papers'])} | {100*q['retention']:.2f}% |")
    lines += ["", "Retained papers have a nonempty byline, valid non-placeholder IDs and raw names at every returned slot, no repeated ID on one paper, no truncation flag, fewer than 100 slots, and no simple collective-name flag. This checks the supplied metadata; it cannot prove that a source byline is correct or complete. OpenAlex caps returned authorships at 100. Its byline may describe the published version, rather than arXiv v1. [OpenAlex authorships](https://help.openalex.org/data/authorships/), [work dates](https://help.openalex.org/data/works/attributes/).", "",
              "Exclusion reasons are nonexclusive:", "", "| Reason | Papers |", "|---|---:|"]
    lines += [f"| {k.replace('_',' ')} | {fmt(v)} |" for k,v in sorted(d["quality"]["reasons_nonexclusive"].items())]
    x,y=d["raw_name_coverage_diagnostic"]["annual"]
    lines += ["", "### Name-only check of the ID-availability restriction", "",
              "To isolate this selection effect, retain all the other byline rules and relax only the requirement for a valid ID at every slot. These broader paper and name counts form a separate population; they are not substituted into the main paired comparison.", "",
              "| Measure | 2024 | 2025 | Change |", "|---|---:|---:|---:|",
              f"| Papers | {fmt(x['papers'])} | {fmt(y['papers'])} | {delta(x['papers'],y['papers'])} |",
              f"| Distinct names | {fmt(x['name_keys'])} | {fmt(y['name_keys'])} | {delta(x['name_keys'],y['name_keys'])} |",
              f"| Papers / name | {fmt(x['papers_per_name'],3)} | {fmt(y['papers_per_name'],3)} | {delta(x['papers_per_name'],y['papers_per_name'])} |", "",
              "Any difference from the paired name result demonstrates sensitivity to ID-availability selection in the observed data. It does not validate names as real-person identities or fix OpenAlex/arXiv coverage."]
    lines += ["", "Before the byline gate, work-link diagnostics were:", "", "| Diagnostic | Records or groups |", "|---|---:|"]
    lines += [f"| {k.replace('_',' ')} | {fmt(v)} |" for k,v in d["diagnostics"].items()]
    lines += ["", "### Overlap with the existing project mathematics ID list", "",
              "This is a separate selection check using the previously available manifest. It is not an independent arXiv census, and its larger paper totals are never divided by this subset's author counts.", "",
              "| Upload year | Project manifest | Linked overlap | Paired overlap | Paired / manifest |", "|---|---:|---:|---:|---:|"]
    for r in d.get("manifest_overlap",{}).get("annual",[]):
        lines.append(f"| {r['period']} | {fmt(r['manifest_papers'])} | {fmt(r['linked_overlap'])} | {fmt(r['paired_overlap'])} | {100*r['paired_fraction_of_manifest']:.2f}% |")
    overlap=d.get("manifest_overlap",{}).get("annual",[])
    if len(overlap)==2:
        x,y=overlap
        lines += ["", f"Within the intersection with that project manifest, paired papers change by {delta(x['papers'],y['papers'])}, IDs by {delta(x['ids']['authors'],y['ids']['authors'])}, and names by {delta(x['names']['authors'],y['names']['authors'])}. This is a narrower population, reported as a scope sensitivity check."]
    lines += ["", "### OpenAlex publication years for the retained upload cohorts", "", "| Upload year | OpenAlex publication-year counts, before byline exclusions |", "|---|---|"]
    for year,counts in d["publication_year_by_upload_year"].items():
        lines.append(f"| {year} | "+"; ".join(f"{k}: {v:,}" for k,v in counts.items())+" |")
    lines += ["", "## Two author definitions", "",
              "**Disambiguated version:** group authorship slots by OpenAlex author ID. OpenAlex already uses name, coauthorship and other information to resolve people; we add no new merging algorithm and make no claim to outperform it.", "",
              "**Distinct-name version:** use `authorships.raw_author_name` after Unicode NFC and whitespace normalization only. Preserve case, accents, punctuation, initials and name order. Never substitute `author.display_name`, which belongs to the resolved profile. This is distinct-name counting within OpenAlex's already consolidated works, not raw untouched arXiv bylines.", "",
              "The same person can have several names or IDs, while different people can share a name or be mistakenly assigned one ID. OpenAlex can therefore both combine name variants and separate identical names. A name-count versus ID-count difference is neither a correction factor nor an error rate. [OpenAlex disambiguation](https://help.openalex.org/data/authors/disambiguation/).", "",
              "| Mapping diagnostic, both years pooled | Count |", "|---|---:|"]
    for key,value in d["identity_diagnostics"].items():
        if isinstance(value,int): lines.append(f"| {key.replace('_',' ')} | {value:,} |")
    lines += ["", "These mapping patterns have not been manually adjudicated. Source-supplied ORCIDs describe a selected subset; profile ORCIDs are not independent validation. Longitudinal identity and high-output-tail audits remain outstanding.", "",
              "### Annual mapping ambiguity", "",
              "Each mapping is rebuilt within its calendar year on the paired papers. Shares below use all paired authorship slots in that year, so frequent keys have proportionate weight. A shared name can represent different people; an ID with several names can correctly join spelling variants. Neither pattern alone identifies an error.", "",
              "| Year | Names with multiple IDs | Slots in those name groups | IDs with multiple names | Slots in those ID groups | Source-ORCID slot coverage | Source ORCIDs with multiple IDs |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for r in d["annual"]:
        q=r["identity_diagnostics"]
        lines.append(f"| {r['period']} | {q['names_associated_with_multiple_ids']:,} | {100*q['share_of_slots_in_names_with_multiple_ids']:.2f}% | {q['ids_associated_with_multiple_names']:,} | {100*q['share_of_slots_in_ids_with_multiple_names']:.2f}% | {100*q['raw_orcid_slot_share']:.2f}% | {q['raw_orcids_associated_with_multiple_ids']:,} |")
    lines += ["", "The JSON includes the full distributions of distinct IDs per name and names per ID, the slot numerators, and source-ORCID denominators. Pooled mappings need not equal the sum of annual mappings. ORCID multiplicity supplies audit candidates; it does not calibrate population error or correct the headline counts.", "",
              "## Mathematical accounting", "",
              r"For papers \(P\), distinct author keys \(A\), and byline incidences \(I\), mean team size is \(\bar k=I/P\), mean participation is \(\bar n=I/A\), and", "", r"\[P=A\bar n/\bar k,\qquad \Delta\log P=\Delta\log A+\Delta\log\bar n-\Delta\log\bar k.\]", "",
              r"Each slot on a \(k_p\)-author paper receives \(1/k_p\) credit. Credits sum to \(P\), so mean fractional credit equals \(P/A\). Shared-name coauthors keep separate slots and both credits accumulate to the name key. Thus name-based \(I/A\) counts occurrences per name key, not necessarily distinct papers per person.", "",
              "All accounting and credit-conservation checks pass for every annual, monthly, rolling-12-month, subfield and manifest-overlap result. Overlapping windows deduplicate author keys across their whole duration; unique-author counts are never summed across periods or subfields.", "",
              "| 2024 to 2025 log-growth term | OpenAlex IDs | Distinct names |", "|---|---:|---:|"]
    for key,label in (("authors","Change in log active keys"),("incidences_per_author","Change in log incidences per key"),("minus_mean_team_size","Minus change in log mean team size"),("papers","Sum: change in log papers")):
        lines.append(f"| {label} | {d['transitions_exploratory']['ids']['log_decomposition'][key]:+.6f} | {d['transitions_exploratory']['names']['log_decomposition'][key]:+.6f} |")
    lines += ["", "These are additive natural-log changes, not independent causal contributions or percentage-point changes.", "",
              "### Exploratory transition identity", "",
              "Continuing keys occur in both years, appearing keys only in 2025, and disappearing keys only in 2024. The following signed paper-equivalent terms add to the paper change. They are an accounting diagnostic before independent longitudinal identity validation; appearing keys are not established career entrants.", "",
              "| Term | OpenAlex IDs | Distinct names |", "|---|---:|---:|"]
    for key in ("continuing_keys","appearing_keys","disappearing_keys","continuing_credit_change","appearing_credit","disappearing_credit","paper_change"):
        lines.append(f"| {key.replace('_',' ')} | {fmt(d['transitions_exploratory']['ids'][key],3 if 'credit' in key else 0)} | {fmt(d['transitions_exploratory']['names'][key],3 if 'credit' in key else 0)} |")
    lines += ["", "Team changes, changing corpus membership, coverage and identity assignments all affect these terms. Disappearance does not establish retirement. There is no sufficient lookback for true career entry, returning-author histories, or a five-year activity comparison.", "",
              "## Subfield sensitivity", "", "Papers have one primary OpenAlex subfield; people can occur in several. These counts should not be added to recover the global author count.", "",
              "| Subfield | 2024 papers | 2025 papers | Paper change | ID change | Name change |", "|---|---:|---:|---:|---:|---:|"]
    for s in d["subfields"]:
        x,y=s["annual"]
        lines.append(f"| {s['subfield']} | {fmt(x['papers'])} | {fmt(y['papers'])} | {delta(x['papers'],y['papers'])} | {delta(x['ids']['authors'],y['ids']['authors'])} | {delta(x['names']['authors'],y['names']['authors'])} |")
    lines += ["", "## Exploratory concentration", "",
              "Full counting measures authorship participation; fractional counting divides each paper's credit by team size. They answer different distributional questions. Neither measures effort, quality or elitism. Top-percent shares allocate a fractional rank at the boundary. Both remain sensitive to identity errors, team structure, the active-key population and selective exclusions.", "",
              "| Year / definition | Full-count Gini | Fractional Gini | Single-appearance keys | Single-appearance share |", "|---|---:|---:|---:|---:|"]
    for r in d["annual"]:
        for m in names:
            count=r[m]["activity_frequency"].get("1",0)
            lines.append(f"| {r['period']} / {names[m]} | {r[m]['full_distribution']['gini']:.4f} | {r[m]['fractional_distribution']['gini']:.4f} | {count:,} | {100*count/r[m]['authors']:.2f}% |")
    lines += ["", "A single appearance means one authorship occurrence in the retained year, not first-ever publication. No paired paper in this snapshot repeats a normalized name within its byline, so here one occurrence also means one retained paper. Both Ginis decline under both identity definitions, while coverage changes substantially. That is a property of this selected dataset, not evidence that mathematics became less elitist.", "",
              "Team-size variation can change fractional credit without changing full counts. A divergence warrants investigation of collaboration, composition and identity; it does not uniquely identify a mechanism. Mean paired team size falls from 2.261 to 2.221 in this run.", "",
              "| Year / definition / convention | Gini | Top 1% | Top 5% | Top 10% | Top 100 |", "|---|---:|---:|---:|---:|---:|"]
    for r in d["annual"]:
        for m in names:
            for convention in ("full", "fractional"):
                c=r[m][convention+"_distribution"]
                lines.append(f"| {r['period']} / {names[m]} / {convention} | {c['gini']:.4f} | {100*c['top_1_share']:.2f}% | {100*c['top_5_share']:.2f}% | {100*c['top_10_share']:.2f}% | {100*c['top_100_share']:.2f}% |")
    lines += ["", "Activity-frequency and team-size-frequency tables are in the aggregate JSON. Exact frozen-data counts do not need conventional sampling error bars. Measurement uncertainty and generalization remain; this report does not supply a validated confidence interval for real-person counts. Resampling author keys independently would not resolve splitting, homonyms or missing-byline selection.", "",
              "## Connection to prior work", "",
              "[Hulek and Teschke (2023)](https://ems.press/content/serial-article-files/29073) provide the closest mathematics-specific precedent: annual documents, active authors and collaboration in zbMATH. Their retained unambiguous assignments are a coverage restriction, not an independently established identity accuracy rate. We preserve their separation of output, participation and team size, while displaying both identity definitions.", "",
              "[Grossman (2005)](https://www.math.buffalo.edu/mad/stats/2005.research.patterns.pdf) used Mathematical Reviews person identification and long observation windows to examine publication and collaboration. This two-year OpenAlex comparison is a shorter, differently covered extension; it cannot establish the same historical conclusions.", "",
              "[Fanelli and Larivière (2016)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0149504) compared selected long-career profiles at fixed career exposure. That is a different population and design. We do not impose future-publication survival as an inclusion criterion or interpret byline order as mathematical contribution.", "",
              "[Fegley and Torvik (2013)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0070299) show why name splitting and lumping can alter measured patterns. Their domain-specific effects are not numerical accuracy estimates for this corpus. [Beckenbach, Hulek and Teschke (2024)](https://ems.press/content/serial-article-files/47210) distinguish arXiv work matching from author assignment in zbMATH integration. That distinction motivates the byline and version caveat here.", "",
              "This run does not reproduce those source datasets. The revised longer-term protocol remains the reference for independent validation, broader historical acquisition and cohort work. No AI effect, research-quality change, or democratization claim is identified by this interim analysis.", "",
              "## Reproducibility", "",
              f"- Retrieval began: {d['source']['started_at']}", f"- Retrieval ended: {d['source']['finished_at']}",
              f"- Acquisition manifest SHA-256: `{d['acquisition_sha256']}`", f"- Normalizer: {d['normalizer']}",
              "- Offline calculation: `analysis/openalex_names.py`; rendering: `analysis/render_openalex_comparison.py`.",
              "- Snapshot contains only selected public bibliographic metadata, cached page hashes and acquisition details. No paper text was downloaded.",
              "- The initial run and review extensions are submitted in draft analysis PR #2, with the revised protocol in draft PR #3. Main remains unchanged pending owner review.",
              "- Seven comparison fixtures exercise identity ambiguity, window-specific mapping diagnostics and conservation, alongside nine existing analysis/export tests; all 16 pass. No claim is made about unavailable upstream tests.", "",
              "To rerun from the extracted snapshot:", "",
              "    python -m analysis.openalex_names --snapshot /path/to/snapshot --output /path/to/results --math-manifest /path/to/math_ids.txt", "",
              "    python -m analysis.render_openalex_comparison --input /path/to/results/openalex_comparison.json --output /path/to/results", ""]
    lines = ["> **Archived comparison.** Population participation and concentration interpretations are on hold following the second review. See RETENTION_AUDIT.md for the current coverage audit.", ""] + lines
    output.mkdir(parents=True,exist_ok=True)
    (output/"OPENALEX_COMPARISON.md").write_text("\n".join(lines))
    plot(d, output)


def plot(d, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    fig,axes=plt.subplots(4,1,figsize=(10.5,11.2),sharex=True)
    x=list(range(len(d["rolling12"])))
    specs=[("papers","Paired papers",None),("authors","Active author keys",["ids","names"]),("papers_per_author","Papers / author key",["ids","names"])]
    for ax,(metric,label,methods) in zip(axes[:3],specs):
        for m in methods or [None]:
            values=[r[m][metric] if m else r[metric] for r in d["rolling12"]]
            color={None:"#365bc9","ids":"#087f83","names":"#7555a7"}[m]
            name={None:"Papers","ids":"OpenAlex IDs","names":"Distinct names"}[m]
            ax.plot(x,values,color=color,lw=2.5,ls="--" if m=="names" else "-",label=name)
            ax.scatter([x[-1]],[values[-1]],color=color,s=20)
        ax.set_ylabel(label)
        ax.grid(axis="y",alpha=.18)
        if metric!="papers_per_author": ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v/1000:.1f}k"))
        ax.margins(x=.03,y=.22)
        ax.legend(loc="best",frameon=False,ncol=2)
    retention=[100*r["quality"]["retention"] for r in d["rolling12"]]
    axes[3].plot(x,retention,color="#a76519",lw=2.5,label="Paired papers / all uniquely linked papers")
    axes[3].set_ylabel("Authorship retention (%)")
    axes[3].grid(axis="y",alpha=.18)
    axes[3].margins(x=.03,y=.22)
    axes[3].legend(loc="best",frameon=False)
    ticks=[0,3,6,9,12]
    axes[-1].set_xticks(ticks,[d["rolling12"][i]["period"] for i in ticks])
    axes[-1].set_xlabel("End of trailing 12-month window (arXiv ID month proxy)")
    fig.suptitle("Mathematics papers and participation\nAuthor-count trends depend on coverage",x=.12,y=.98,ha="left",fontsize=18,fontweight="bold")
    fig.text(.12,.015,"Same eligible papers in both methods · OpenAlex Mathematics, arXiv-linked subset · Snapshot: 15 Sep 2026\nQuery uses OpenAlex publication years 2024–2026; analysis uses arXiv ID months 2024–2025.\nOverlapping windows; observed author keys are not validated counts of real people.",fontsize=9,color="#53647b",linespacing=1.5)
    fig.tight_layout(rect=[0,.09,1,.92],h_pad=2)
    for ext in ("png","svg"):
        fig.savefig(output/f"openalex_comparison.{ext}",dpi=180,facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    render(args.input,args.output)
