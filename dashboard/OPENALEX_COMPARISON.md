> **Archived comparison.** Population participation and concentration interpretations are on hold following the second review. See RETENTION_AUDIT.md for the current coverage audit.

# OpenAlex comparison: mathematics papers and active author keys

Computed 15 September 2026. **Interim descriptive analysis, 2024 versus 2025.**

**The main finding is unequal coverage.** Linked papers before the authorship gate increase by **+1.94%**, but retention falls from **95.11% to 84.87%**. Additional exclusions more than offset that increase: the paired paper count falls by **-9.04%**. Most exclusions involve missing author IDs. An apparent decline among retained author keys cannot establish a decline in the full mathematics community.

On the same retained papers, paper counts changed by **-9.04%**, active OpenAlex IDs by **-7.62%**, and distinct recorded names by **-7.24%**.

Papers per author key changed by **-1.53%** using IDs and **-1.94%** using names. These quantities describe a selected OpenAlex-covered population. They do not establish population-wide or individual productivity changes.

## Main results

| Measure | 2024 | 2025 | Change |
|---|---:|---:|---:|
| Paired papers | 23,756 | 21,609 | -9.04% |
| OpenAlex author IDs | 40,258 | 37,190 | -7.62% |
| Distinct raw-name keys | 40,831 | 37,875 | -7.24% |
| Authorship slots | 53,707 | 48,004 | -10.62% |
| Mean team size I/P | 2.261 | 2.221 | -1.74% |
| Mean participation I/A — IDs | 1.334 | 1.291 | -3.25% |
| Mean participation I/A — names | 1.315 | 1.267 | -3.64% |
| Papers per ID P/A | 0.590 | 0.581 | -1.53% |
| Papers per name P/A | 0.582 | 0.571 | -1.94% |

Both methods use exactly the same papers and OpenAlex authorship slots. The paper numerator and team sizes are identical across methods. Counts represent active author keys, not uploading accounts, and neither definition is a reliable bound on the number of real people.

## Population, dates and coverage

Retrieved **83,017 unique OpenAlex works** from its default core corpus using `indexed_in:arxiv`, `primary_topic.field.id:26`, and OpenAlex publication years 2024–2026. The query was partitioned by publication month and fully paginated. Each partition's retrieved count is required to equal its reported population count; cached page hashes are verified before analysis.

The analysis then extracts modern arXiv IDs from OpenAlex location URLs, arXiv OAI location identifiers or arXiv DOIs. Versions collapse to one ID. Exactly one arXiv ID per work and one OpenAlex work per arXiv ID are required. We retain IDs with months January 2024 through December 2025. The ID month is an upload-month proxy, not a verified first-submission timestamp. We never use a journal-publication date as the upload date.

The 2026 publication-year extension captures some later published versions of 2024–2025 uploads. Nevertheless, the query can omit relevant uploads assigned an OpenAlex publication year before 2024 or after 2026. OpenAlex Mathematics is a topic-based classification; it is not the arXiv primary-category definition in the longer-term protocol. Expansion-corpus works are outside this query.

| Upload year | Unique linked papers | Paired papers | Retention among linked papers |
|---|---:|---:|---:|
| 2024 | 24,978 | 23,756 | 95.11% |
| 2025 | 25,462 | 21,609 | 84.87% |

Retained papers have a nonempty byline, valid non-placeholder IDs and raw names at every returned slot, no repeated ID on one paper, no truncation flag, fewer than 100 slots, and no simple collective-name flag. This checks the supplied metadata; it cannot prove that a source byline is correct or complete. OpenAlex caps returned authorships at 100. Its byline may describe the published version, rather than arXiv v1. [OpenAlex authorships](https://help.openalex.org/data/authorships/), [work dates](https://help.openalex.org/data/works/attributes/).

Exclusion reasons are nonexclusive:

| Reason | Papers |
|---|---:|
| missing or placeholder author id | 5,048 |
| possible group name | 14 |
| repeated id in byline | 27 |
| truncated or 100plus byline | 12 |

### Name-only check of the ID-availability restriction

To isolate this selection effect, retain all the other byline rules and relax only the requirement for a valid ID at every slot. These broader paper and name counts form a separate population; they are not substituted into the main paired comparison.

| Measure | 2024 | 2025 | Change |
|---|---:|---:|---:|
| Papers | 24,957 | 25,443 | +1.95% |
| Distinct names | 43,760 | 44,816 | +2.41% |
| Papers / name | 0.570 | 0.568 | -0.45% |

Any difference from the paired name result demonstrates sensitivity to ID-availability selection in the observed data. It does not validate names as real-person identities or fix OpenAlex/arXiv coverage.

Before the byline gate, work-link diagnostics were:

| Diagnostic | Records or groups |
|---|---:|
| candidate works | 83,017 |
| arxiv id outside window | 32,552 |
| multiple arxiv ids | 20 |
| no unique modern arxiv id | 5 |
| unique arxiv papers in window | 50,440 |
| duplicate work rows | 0 |

### Overlap with the existing project mathematics ID list

This is a separate selection check using the previously available manifest. It is not an independent arXiv census, and its larger paper totals are never divided by this subset's author counts.

| Upload year | Project manifest | Linked overlap | Paired overlap | Paired / manifest |
|---|---:|---:|---:|---:|
| 2024 | 52,081 | 21,565 | 20,639 | 39.63% |
| 2025 | 55,751 | 22,362 | 19,079 | 34.22% |

Within the intersection with that project manifest, paired papers change by -7.56%, IDs by -4.27%, and names by -3.94%. This is a narrower population, reported as a scope sensitivity check.

### OpenAlex publication years for the retained upload cohorts

| Upload year | OpenAlex publication-year counts, before byline exclusions |
|---|---|
| 2024 | 2024: 22,732; 2025: 550; 2026: 1,696 |
| 2025 | 2024: 166; 2025: 21,834; 2026: 3,462 |

## Two author definitions

**Disambiguated version:** group authorship slots by OpenAlex author ID. OpenAlex already uses name, coauthorship and other information to resolve people; we add no new merging algorithm and make no claim to outperform it.

**Distinct-name version:** use `authorships.raw_author_name` after Unicode NFC and whitespace normalization only. Preserve case, accents, punctuation, initials and name order. Never substitute `author.display_name`, which belongs to the resolved profile. This is distinct-name counting within OpenAlex's already consolidated works, not raw untouched arXiv bylines.

The same person can have several names or IDs, while different people can share a name or be mistakenly assigned one ID. OpenAlex can therefore both combine name variants and separate identical names. A name-count versus ID-count difference is neither a correction factor nor an error rate. [OpenAlex disambiguation](https://help.openalex.org/data/authors/disambiguation/).

| Mapping diagnostic, both years pooled | Count |
|---|---:|
| name keys | 67,704 |
| id keys | 65,813 |
| authorship slots | 101,711 |
| names associated with multiple ids | 4,461 |
| ids associated with multiple names | 7,346 |
| slots in names with multiple ids | 14,719 |
| slots in ids with multiple names | 24,841 |
| raw orcid slots | 6,228 |
| distinct raw orcids | 5,708 |
| raw orcids associated with multiple ids | 53 |

These mapping patterns have not been manually adjudicated. Source-supplied ORCIDs describe a selected subset; profile ORCIDs are not independent validation. Longitudinal identity and high-output-tail audits remain outstanding.

### Annual mapping ambiguity

Each mapping is rebuilt within its calendar year on the paired papers. Shares below use all paired authorship slots in that year, so frequent keys have proportionate weight. A shared name can represent different people; an ID with several names can correctly join spelling variants. Neither pattern alone identifies an error.

| Year | Names with multiple IDs | Slots in those name groups | IDs with multiple names | Slots in those ID groups | Source-ORCID slot coverage | Source ORCIDs with multiple IDs |
|---|---:|---:|---:|---:|---:|---:|
| 2024 | 1,722 | 9.23% | 2,613 | 14.02% | 4.28% | 5 |
| 2025 | 1,838 | 10.40% | 2,817 | 16.02% | 8.18% | 29 |

The JSON includes the full distributions of distinct IDs per name and names per ID, the slot numerators, and source-ORCID denominators. Pooled mappings need not equal the sum of annual mappings. ORCID multiplicity supplies audit candidates; it does not calibrate population error or correct the headline counts.

## Mathematical accounting

For papers \(P\), distinct author keys \(A\), and byline incidences \(I\), mean team size is \(\bar k=I/P\), mean participation is \(\bar n=I/A\), and

\[P=A\bar n/\bar k,\qquad \Delta\log P=\Delta\log A+\Delta\log\bar n-\Delta\log\bar k.\]

Each slot on a \(k_p\)-author paper receives \(1/k_p\) credit. Credits sum to \(P\), so mean fractional credit equals \(P/A\). Shared-name coauthors keep separate slots and both credits accumulate to the name key. Thus name-based \(I/A\) counts occurrences per name key, not necessarily distinct papers per person.

All accounting and credit-conservation checks pass for every annual, monthly, rolling-12-month, subfield and manifest-overlap result. Overlapping windows deduplicate author keys across their whole duration; unique-author counts are never summed across periods or subfields.

| 2024 to 2025 log-growth term | OpenAlex IDs | Distinct names |
|---|---:|---:|
| Change in log active keys | -0.079269 | -0.075150 |
| Change in log incidences per key | -0.032990 | -0.037109 |
| Minus change in log mean team size | +0.017534 | +0.017534 |
| Sum: change in log papers | -0.094725 | -0.094725 |

These are additive natural-log changes, not independent causal contributions or percentage-point changes.

### Exploratory transition identity

Continuing keys occur in both years, appearing keys only in 2025, and disappearing keys only in 2024. The following signed paper-equivalent terms add to the paper change. They are an accounting diagnostic before independent longitudinal identity validation; appearing keys are not established career entrants.

| Term | OpenAlex IDs | Distinct names |
|---|---:|---:|
| continuing keys | 11,635 | 11,002 |
| appearing keys | 25,555 | 26,873 |
| disappearing keys | 28,623 | 29,829 |
| continuing credit change | -609.290 | -679.638 |
| appearing credit | 13,251.636 | 13,711.416 |
| disappearing credit | -14,789.345 | -15,178.778 |
| paper change | -2,147 | -2,147 |

Team changes, changing corpus membership, coverage and identity assignments all affect these terms. Disappearance does not establish retirement. There is no sufficient lookback for true career entry, returning-author histories, or a five-year activity comparison.

## Subfield sensitivity

Papers have one primary OpenAlex subfield; people can occur in several. These counts should not be added to recover the global author count.

| Subfield | 2024 papers | 2025 papers | Paper change | ID change | Name change |
|---|---:|---:|---:|---:|---:|
| Algebra and Number Theory | 2,780 | 1,995 | -28.24% | -27.57% | -27.25% |
| Applied Mathematics | 4,405 | 4,282 | -2.79% | -7.63% | -5.82% |
| Computational Mathematics | 208 | 275 | +32.21% | +27.62% | +28.41% |
| Discrete Mathematics and Combinatorics | 920 | 1,348 | +46.52% | +43.27% | +44.90% |
| Geometry and Topology | 5,193 | 4,969 | -4.31% | -5.93% | -6.64% |
| Mathematical Physics | 6,044 | 4,947 | -18.15% | -20.91% | -21.06% |
| Modeling and Simulation | 603 | 528 | -12.44% | -12.90% | -14.19% |
| Numerical Analysis | 1,286 | 871 | -32.27% | -32.49% | -32.17% |
| Statistics and Probability | 2,148 | 2,305 | +7.31% | +5.76% | +5.07% |
| Theoretical Computer Science | 169 | 89 | -47.34% | -50.16% | -50.16% |

## Exploratory concentration

Full counting measures authorship participation; fractional counting divides each paper's credit by team size. They answer different distributional questions. Neither measures effort, quality or elitism. Top-percent shares allocate a fractional rank at the boundary. Both remain sensitive to identity errors, team structure, the active-key population and selective exclusions.

| Year / definition | Full-count Gini | Fractional Gini | Single-appearance keys | Single-appearance share |
|---|---:|---:|---:|---:|
| 2024 / OpenAlex IDs | 0.2111 | 0.3841 | 31,557 | 78.39% |
| 2024 / Distinct names | 0.2039 | 0.3840 | 32,428 | 79.42% |
| 2025 / OpenAlex IDs | 0.1925 | 0.3683 | 29,893 | 80.38% |
| 2025 / Distinct names | 0.1822 | 0.3660 | 30,954 | 81.73% |

A single appearance means one authorship occurrence in the retained year, not first-ever publication. No paired paper in this snapshot repeats a normalized name within its byline, so here one occurrence also means one retained paper. Both Ginis decline under both identity definitions, while coverage changes substantially. That is a property of this selected dataset, not evidence that mathematics became less elitist.

Team-size variation can change fractional credit without changing full counts. A divergence warrants investigation of collaboration, composition and identity; it does not uniquely identify a mechanism. Mean paired team size falls from 2.261 to 2.221 in this run.

| Year / definition / convention | Gini | Top 1% | Top 5% | Top 10% | Top 100 |
|---|---:|---:|---:|---:|---:|
| 2024 / OpenAlex IDs / full | 0.2111 | 4.65% | 14.81% | 23.83% | 1.66% |
| 2024 / OpenAlex IDs / fractional | 0.3841 | 5.84% | 18.25% | 28.54% | 2.13% |
| 2024 / Distinct names / full | 0.2039 | 4.78% | 14.88% | 23.53% | 1.69% |
| 2024 / Distinct names / fractional | 0.3840 | 6.04% | 18.64% | 28.87% | 2.20% |
| 2025 / OpenAlex IDs / full | 0.1925 | 4.33% | 14.46% | 22.82% | 1.59% |
| 2025 / OpenAlex IDs / fractional | 0.3683 | 5.48% | 17.58% | 27.23% | 2.04% |
| 2025 / Distinct names / full | 0.1822 | 4.31% | 14.42% | 22.46% | 1.58% |
| 2025 / Distinct names / fractional | 0.3660 | 5.50% | 17.63% | 27.22% | 2.01% |

Activity-frequency and team-size-frequency tables are in the aggregate JSON. Exact frozen-data counts do not need conventional sampling error bars. Measurement uncertainty and generalization remain; this report does not supply a validated confidence interval for real-person counts. Resampling author keys independently would not resolve splitting, homonyms or missing-byline selection.

## Connection to prior work

[Hulek and Teschke (2023)](https://ems.press/content/serial-article-files/29073) provide the closest mathematics-specific precedent: annual documents, active authors and collaboration in zbMATH. Their retained unambiguous assignments are a coverage restriction, not an independently established identity accuracy rate. We preserve their separation of output, participation and team size, while displaying both identity definitions.

[Grossman (2005)](https://www.math.buffalo.edu/mad/stats/2005.research.patterns.pdf) used Mathematical Reviews person identification and long observation windows to examine publication and collaboration. This two-year OpenAlex comparison is a shorter, differently covered extension; it cannot establish the same historical conclusions.

[Fanelli and Larivière (2016)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0149504) compared selected long-career profiles at fixed career exposure. That is a different population and design. We do not impose future-publication survival as an inclusion criterion or interpret byline order as mathematical contribution.

[Fegley and Torvik (2013)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0070299) show why name splitting and lumping can alter measured patterns. Their domain-specific effects are not numerical accuracy estimates for this corpus. [Beckenbach, Hulek and Teschke (2024)](https://ems.press/content/serial-article-files/47210) distinguish arXiv work matching from author assignment in zbMATH integration. That distinction motivates the byline and version caveat here.

This run does not reproduce those source datasets. The revised longer-term protocol remains the reference for independent validation, broader historical acquisition and cohort work. No AI effect, research-quality change, or democratization claim is identified by this interim analysis.

## Reproducibility

- Retrieval began: 2026-09-15T11:29:16.093883+00:00
- Retrieval ended: 2026-09-15T11:55:32.489010+00:00
- Acquisition manifest SHA-256: `ca20dba9b006468c3a0d24fb2bde3937659fd37c66b4310e87555228ab14a47b`
- Normalizer: nfc-whitespace-v1; case, initials, accents, punctuation preserved
- Offline calculation: `analysis/openalex_names.py`; rendering: `analysis/render_openalex_comparison.py`.
- Snapshot contains only selected public bibliographic metadata, cached page hashes and acquisition details. No paper text was downloaded.
- The initial run and review extensions are submitted in draft analysis PR #2, with the revised protocol in draft PR #3. Main remains unchanged pending owner review.
- Seven comparison fixtures exercise identity ambiguity, window-specific mapping diagnostics and conservation, alongside nine existing analysis/export tests; all 16 pass. No claim is made about unavailable upstream tests.

To rerun from the extracted snapshot:

    python -m analysis.openalex_names --snapshot /path/to/snapshot --output /path/to/results --math-manifest /path/to/math_ids.txt

    python -m analysis.render_openalex_comparison --input /path/to/results/openalex_comparison.json --output /path/to/results
