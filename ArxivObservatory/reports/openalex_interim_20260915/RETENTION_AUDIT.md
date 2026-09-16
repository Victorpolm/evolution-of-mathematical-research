# Retention audit and response to the second review

15 September 2026. **Population participation and concentration interpretations are on hold.** The dashboard now leads with coverage diagnostics. Earlier author-count and Gini comparisons remain archived measurements of selected records, not findings about the direction of change in mathematics.

The main concern in the reply is accepted: the exclusion rule changes the observed paper trend, and qualifying a contributor-decline headline is insufficient. We now diagnose that selection directly and allocate missing credit explicitly. The cause of missing IDs has been narrowed but not established; no adjustment here neutralizes it.

## 1. What causes the observed retention gap?

| Linked-paper state | 2024 | 2025 | Change in share of linked papers |
|---|---:|---:|---:|
| Retained for paired identity comparison | 23,756 | 21,609 | -10.240 pp |
| Entire byline has no IDs | 206 | 2,090 | +7.384 pp |
| Some byline IDs missing | 1,000 | 1,752 | +2.877 pp |
| Other byline exclusions | 16 | 11 | -0.021 pp |
| All uniquely linked target-window papers | 24,978 | 25,462 | — |

States are mutually exclusive, with missing-ID states taking precedence when another exclusion flag overlaps. They describe where retained coverage is lost; they do not establish a causal missingness mechanism.

Entirely unidentified bylines account for **7.38 percentage points** of the **10.24-point** retention decline. The missing source IDs are null/absent, rather than the two known provider placeholders. This is substantial absence of identification at the paper level, not just isolated unidentified coauthors.

The absence is concentrated in late 2025: November and December contain 1,577 of the 2,090 entirely unidentified bylines (75.45%). Such bylines account for 855/2,792 linked November papers (30.62%) and 722/3,135 December papers (23.03%). The monthly series locates this concentration; it does not establish indexing lag as its cause.

### Team size and subfield

Retention declines even within fixed returned team sizes. The following rows use all uniquely linked papers at each team size, before byline exclusions.

| Returned team size | 2024 papers | 2024 retention | 2025 papers | 2025 retention |
|---|---:|---:|---:|---:|
| 1 | 7,496 | 97.91% | 7,855 | 88.03% |
| 2 | 8,369 | 96.30% | 8,526 | 85.96% |
| 3 | 5,663 | 93.94% | 5,655 | 83.04% |
| 4 | 2,217 | 91.25% | 2,205 | 80.63% |
| 5 | 657 | 87.21% | 691 | 78.73% |
| 6 | 260 | 81.54% | 251 | 74.90% |

Using the same pooled paper weights for exact-team-size × OpenAlex-primary-subfield cells gives standardized retention of **95.26% versus 85.04%**. Common cells cover 99.84% and 99.90% of usable bylines. The gap therefore remains within those observed strata; a different mix of team sizes and subfields does not explain it away. This is a diagnostic of retention, not a correction of unique-author counts.

| OpenAlex subfield | 2024 linked papers | 2024 retention | 2025 linked papers | 2025 retention |
|---|---:|---:|---:|---:|
| Algebra and Number Theory | 2,907 | 95.63% | 2,327 | 85.73% |
| Applied Mathematics | 4,595 | 95.87% | 5,058 | 84.66% |
| Computational Mathematics | 220 | 94.55% | 347 | 79.25% |
| Discrete Mathematics and Combinatorics | 970 | 94.85% | 1,637 | 82.35% |
| Geometry and Topology | 5,433 | 95.58% | 5,791 | 85.81% |
| Mathematical Physics | 6,335 | 95.41% | 5,776 | 85.65% |
| Modeling and Simulation | 639 | 94.37% | 637 | 82.89% |
| Numerical Analysis | 1,382 | 93.05% | 995 | 87.54% |
| Statistics and Probability | 2,318 | 92.67% | 2,793 | 82.53% |
| Theoretical Computer Science | 179 | 94.41% | 101 | 88.12% |

### Indexing lag is a hypothesis, not an established explanation

The frozen projection contains work update dates but no creation/indexing dates or historical byline states. An update timestamp is not an indexing clock. This single snapshot cannot recreate what both cohorts looked like at equal time since indexing. Publication-year and metadata-update-month retention tables are supplied in the JSON as diagnostics, without interpreting either timestamp as first indexing.

The next discriminating evidence is repeated or archived metadata for the same papers: when IDs were absent, added, replaced or lost, by source and cohort. Equal follow-up would improve a specifically defined comparison, but matching ages or overall retention rates alone does not equalize who is missing. Randomly discarding additional retained papers would not repair selective loss. A U-shaped historical completeness curve is also a hypothesis to test, not a demonstrated property of this snapshot.

## 2. Exact paper accounting, and what normalization cannot show

For linked papers L and retained fraction c, paired papers R satisfy \(R=Lc\), hence

\[\Delta\log R=\Delta\log L+\Delta\log c.\]

| Natural-log change, 2024 to 2025 | Value |
|---|---:|
| Linked paper count | +0.019192 |
| Retention fraction | -0.113917 |
| Sum: retained paper count | -0.094725 |

The paper sign reversal is exactly explained by this accounting: linked counts rise 1.94% while retained counts fall 9.04%. This does not allocate the change in distinct authors to causes; unique keys recur across papers. The review's retention-only simulation establishes a possible mechanism, not that its assumed mechanism generated these records.

The separate normalization argument needs correcting. \(A/P\) and \(P/A\) are reciprocals; a rising \(A/P\) while total A falls is not a contradictory estimate of the same quantity. Counts and ratios answer different questions. Dividing by retained papers is not a missingness correction.

## 3. Partial-ID accounting: keep the unallocated credit

Use every returned byline that passes the non-ID rules, including papers with some or all IDs missing. For each k-slot byline, assign 1/k to each valid ID and retain 1/k as unallocated for each unidentified slot. For truncated, collective, repeated-ID or otherwise unusable bylines, retain one whole unallocated paper equivalent. No synthetic unknown author is inserted into a count or Gini.

| Coverage / accounting quantity | 2024 | 2025 |
|---|---:|---:|
| Papers with usable returned bylines | 24,957 | 25,443 |
| Papers with unusable bylines | 21 | 19 |
| Observed valid IDs on usable bylines | 42,030 | 40,115 |
| Raw name keys on the same usable bylines | 43,760 | 44,816 |
| Paper credit allocated to valid IDs | 24,376.286 | 22,698.981 |
| Unallocated credit: missing IDs | 580.714 | 2,744.019 |
| Unallocated credit: unusable bylines | 21 | 19 |
| Total unallocated credit | 601.714 | 2,763.019 |
| Mean allocated credit per observed ID | 0.580 | 0.566 |
| Usable papers / observed IDs (different ratio) | 0.594 | 0.634 |

\[P_{linked}=C_{identified}+U_{missing\ IDs}+U_{unusable\ byline}.\]

Within usable bylines, \(\bar f_{identified}=(P_{usable}-U_{missing\ IDs})/A_{identified}\), which is not \(P_{usable}/A_{identified}\) when credit is unallocated.

These identities reconcile for each month and each year. k remains the returned slot count, not an independently verified original-arXiv byline. The counts of missing people, their distribution of output and complete-population concentration remain unknown. Partial credit makes the missing contribution visible; it does not restore the missing identities.

The new partial path is `analysis/retention_audit.py`. The legacy `democratization.py` partial-byline output is not used and must not be treated as a corrected entry point.

## 4. The upstream reduction is mostly the declared time-window filter

| Acquisition-to-analysis stage | Works / papers |
|---|---:|
| Acquired OpenAlex works, publication years 2024–2026 | 83,017 |
| One modern arXiv ID outside the 2024–2025 target window | 32,552 |
| Ambiguous: multiple arXiv IDs | 20 |
| No unique modern arXiv ID | 5 |
| Uniquely linked papers in the target window | 50,440 |
| Retained paired papers after byline exclusions | 45,365 |

Of the 32,552 outside-window works, 30,062 have 2026 arXiv IDs and 2,490 have older IDs. Calling the entire 39% reduction unexplained attrition is incorrect. The acquisition included 2026 publication dates to capture later published versions; not every acquired work was intended to enter the two upload cohorts. The JSON breaks the stages down by OpenAlex publication year. Ambiguous/no-ID records cannot be assigned to a target upload cohort without additional evidence.

This accounting does not establish external coverage: OpenAlex Mathematics differs from arXiv primary mathematics, and relevant works outside the query's publication-year limits can be omitted. The existing manifest overlap remains a separate check. We now consistently distinguish acquired works, linked target-window papers, usable bylines and retained paired papers.

## 5. ORCID: the observation opportunity matters

The reply interprets 5/2,216 and 29/3,699 as low measured split rates. Most denominator ORCIDs, however, occur on only one retained paper. Cross-paper splitting cannot be observed without repeated observations of the same source ORCID.

| Source-ORCID diagnostic on paired papers | 2024 | 2025 |
|---|---:|---:|
| Distinct recorded source ORCIDs | 2,216 | 3,699 |
| ORCIDs observed on at least two papers | 75 | 198 |
| Those repeated ORCIDs associated with multiple IDs | 5 | 29 |
| Multiple-ID share among repeated ORCIDs | 6.67% | 14.65% |

The 6.67% and 14.65% figures are also mapping diagnostics, not validated split rates: the subset is selected and source ORCIDs can be incorrectly attached. They show why the small unconditional percentages cannot establish that splitting is negligible. Neither percentage is a proven floor for population error. Profile-level ORCIDs were not substituted for source ORCIDs. See [OpenAlex's source/profile distinction](https://help.openalex.org/data/authors/orcid/).

## 6. Retained methodological decisions

**Identity.** Raw names remain an identity-sensitivity diagnostic alongside IDs. We retire any suggestion that this is a correction or a bracket around real people. A net excess of names over IDs cannot establish that the name representation never combines split IDs: splits and homonyms can coexist with spelling variants. The independent audit, not a new unvalidated merger, is the route to a person-level estimate.

**Partial merging.** The renewed claim that minority merging generically raises Gini still requires a probability model. It is not implied by partial merging alone. For outputs [1,2,4,8,16,32,64,128,256,512], merging the two smallest of ten keys gives [3,4,8,16,32,64,128,256,512]; Gini falls from 0.70196 to 0.66906. No values coincide after merging. The strict decrease persists under sufficiently small perturbations, so it is not a measure-zero equality case. The review's simulations illustrate their chosen models; their code and seeds were not supplied for reproduction.

**Entry and incumbents.** A rising singleton share does not establish an influx of entrants; paper loss can produce the same pattern. The audit JSON includes a 2024 observed-key reference cohort followed into 2025 with zero-output keys retained, and separate observed continuing/appearing distributions. These are accounting checks, not validated career-entry or incumbent-behavior results, because missingness and identity changes also produce apparent zeros and entries. Longer history and identity validation remain necessary.

**Uncertainty.** A paper-cluster bootstrap may suit a specified paper-sampling model, but it is not automatically the correct uncertainty calculation. Authors recur across papers, so independent paper clusters are an assumption, not a consequence of the data structure. Neither resampling unit solves identity error or selection. No generic bootstrap interval is attached to these exact frozen-record diagnostics.

**Disclosure cutoff.** The stronger zero-day check is confirmed from the original committed page: 7 August 2026 is the only zero Friday; recent Fridays average 158.5 papers with a minimum of 113. The following Saturday is also the only zero Saturday; recent Saturdays average 93.36 with a minimum of 69. This is strong evidence of an incomplete end window. A final complete cutoff needs the ingestion ledger; the owner-maintained disclosure dashboard should not treat those days as established complete observations. No original scan or classification pipeline was changed here.

**Later AI design.** [Rambachan and Roth (2023)](https://academic.oup.com/restud/article-abstract/90/5/2555/7039335) is an appropriate addition to the prior-work plan: examine sensitivity to explicitly bounded departures from parallel trends if a credible subfield design is developed. The bounds need substantive justification; the method does not itself establish AI exposure, comparable measurement or absence of confounding. No causal AI analysis is run here.

The mathematical accounting and mathematics-bibliometric precedents in the revised protocol are retained. This stage contributes a reproducible measurement audit. It does not establish a change in democratization, elitism or AI effects.

## 7. Reproduction and remaining decisions

The offline comparison, retention audit, aggregate results and dashboard source are submitted in [draft PR #2](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/2), with the protocol and historical-extension note in [draft PR #3](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/3). This September 16 repository update incorporates the previously supplied review extensions. The branches remain draft contributions for owner review; main is unchanged.

The private dashboard supplies the updated offline analysis, reports and frozen acquisition manifest as a downloadable audit package. It includes the original acquisition helper as a separately labelled reference, and the existing mathematics ID list used for the overlap check. The projected metadata snapshot supplied earlier is a separate required input, available as a download in this conversation. A fresh API query would not reproduce that frozen snapshot. External review needs access to those exact bytes or an owner-approved deposit; a hash alone is insufficient.

The repository's contribution rules require contributed analysis to run offline and leave acquisition campaigns and main merges to the owner. A repository location for the network acquisition helper requires an explicit owner decision; it should not be slipped into the offline module. No new acquisition, paid API call, arXiv download, pipeline change or main-branch merge occurred.

From an analysis checkout containing the supplied updated modules:

    python3 -m analysis.retention_audit --snapshot /path/to/frozen_snapshot --output /path/to/results

    python3 -m analysis.render_retention_audit --input /path/to/results/retention_audit.json --output /path/to/results

Acquisition manifest SHA-256: `ca20dba9b006468c3a0d24fb2bde3937659fd37c66b4310e87555228ab14a47b`. All cached-page hashes and partition counts were checked. Six new audit fixtures plus sixteen existing focused checks pass (22 total). The archive and raw-source metadata are not committed to the research repository. No manual identity, classifier-gold or full upstream-suite validation is claimed.

Next evidence needed: the existing metadata export for exact frame reconciliation, and repeated or archival records that can establish the origin and evolution of the entirely missing-ID bylines. The historical extension follows a declared coverage design; it is not a substitute for resolving the present measurement failure.
