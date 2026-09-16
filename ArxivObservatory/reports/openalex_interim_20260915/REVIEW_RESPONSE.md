> **Earlier response.** Superseded on dashboard presentation and extended by RETENTION_AUDIT.md after the second reply.

# Response to the methodological review

15 September 2026. This responds to the supplied independent review of commit
`7d1063371ad2825ac3ad622974f6df129d1324f0`. It separates the original AI-disclosure
study from the subsequent OpenAlex participation analysis. The review is useful,
but several proposed remedies would introduce unjustified conclusions.

## 1. What the project can currently claim

The defensible question is: **How do paper counts, observed participation and
publication-credit distributions change, and how sensitive are those changes
to identity definitions and data coverage?** Neither the disclosure series nor
the participation series identifies an effect of AI or establishes whether
mathematics became more democratic or elitist.

The reviewer examined main and the original disclosure dashboard. The new
[analysis in draft PR #2](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/2)
and [revised mathematical protocol in draft PR #3](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/3)
were outside that revision. The
[participation dashboard](https://mathematics-research-observatory.tim-gehrunge-2308.chatgpt.site)
is a separate artifact. This explains the “never run” finding; it also exposes
a real communication problem while the reviewed main branch remains unchanged.

Publication update, 16 September 2026: the revisions described here and the
subsequent retention audit are submitted in draft PR #2; the revised protocol
is in draft PR #3. The earlier private review package remains an archived
deliverable. Main-branch integration remains an owner review decision.

We acquired and froze 83,017 OpenAlex works and ran both definitions on the
same 45,365 eligible arXiv-linked papers dated 2024–2025 by identifier month.
The separate resumable acquisition helper is included with the supplied
metadata snapshot. Repository analysis runs offline, as its contribution
policy requires. These are OpenAlex Mathematics records, not a census of
arXiv primary mathematics or the mathematical workforce.

| Current result | 2024 | 2025 |
|---|---:|---:|
| Uniquely linked papers before byline exclusions | 24,978 | 25,462 |
| Papers retained for both identity definitions | 23,756 | 21,609 |
| Retained share | 95.11% | 84.87% |
| OpenAlex author IDs on retained papers | 40,258 | 37,190 |
| Distinct raw names on retained papers | 40,831 | 37,875 |
| Distinct raw names when only the missing-ID rule is relaxed | 43,760 | 44,816 |

The paired name change is −7.24%; the broader name change is +2.41%. The
missing-ID restriction changes the sign of the observed name trend. It does
not validate either count as people. The review's assertion that ID coverage
improves over time does not hold for these two upload cohorts.

## 2. Useful additions implemented from this review

We reran the frozen metadata offline. Existing paper, author and credit totals
are unchanged. Annual mapping diagnostics, full versus fractional concentration,
single-appearance shares and numerical log-growth terms are now explicit in
the report and dashboard. No additional person resolver was introduced.

| Annual mapping diagnostic, paired population | 2024 | 2025 |
|---|---:|---:|
| Names associated with multiple IDs | 1,722 | 1,838 |
| Share of authorship slots in those name groups | 9.23% | 10.40% |
| IDs associated with multiple names | 2,613 | 2,817 |
| Share of authorship slots in those ID groups | 14.02% | 16.02% |
| Slots carrying a source-supplied ORCID | 4.28% | 8.18% |
| Recorded source ORCIDs associated with multiple IDs | 5 / 2,216 | 29 / 3,699 |

Mappings are rebuilt within each year. Percentages use all paired authorship
slots, not unique keys. Full multiplicity distributions and denominators are
in the aggregate JSON. These are **mapping ambiguity diagnostics**, not measured
collision or identity-error rates. The apparent change also depends on coverage,
activity and which records enter each period.

| Definition | Full Gini, 2024 → 2025 | Fractional Gini, 2024 → 2025 | Share appearing once, 2024 → 2025 |
|---|---:|---:|---:|
| OpenAlex IDs | 0.2111 → 0.1925 | 0.3841 → 0.3683 | 78.39% → 80.38% |
| Distinct names | 0.2039 → 0.1822 | 0.3840 → 0.3660 | 79.42% → 81.73% |

Both Ginis decline in the selected data. This cannot establish a decline in
elitism. The share appearing once is an activity statistic, not a career-entry
rate. One appearance means one authorship occurrence in the retained year;
there are no repeated within-paper name keys in this particular paired sample.

## 3. Mathematical corrections to the recommendations

### Keep the accounting, with the right denominator

For a fixed eligible paper population and identity convention, let P be papers,
A active keys and I authorship slots. Then

\[
P=A\frac{I/A}{I/P},\qquad
\Delta\log P=\Delta\log A+\Delta\log(I/A)-\Delta\log(I/P).
\]

This exact accounting remains central. It is descriptive, not a causal model.
The new runner preserves byline slots and allocates 1/k for a k-slot paper.
It excludes incomplete, repeated-ID, flagged-group and truncated/100-plus
bylines from both paired definitions.

The review correctly identifies a defect in the legacy `democratization.py`
partial-byline path. If a ten-person paper has six identified authors, those
six receive 0.6 paper equivalents in total, not the whole paper. A proper
partial-byline implementation must retain the 0.4 unallocated credit and
report allocated credit per identified author separately from P/A. Merely
changing `1/len(identified)` to `1/total` while retaining old labels and
conservation assumptions is insufficient. Unknown team sizes cannot be made
known by a fallback. That legacy path is not used for the current results and
must be corrected before reuse; the paired restriction itself does not remove
selection bias.

### Names and IDs are not bounds on people

Both representations can split one person and combine different people.
Moreover, raw-name groups and ID groups have a many-to-many relationship;
neither is a guaranteed refinement of the other. The current method uses
source `raw_author_name`, preserving initials, accents, case and punctuation
after NFC/whitespace normalization. It does not collapse profile display names
or reduce everyone to surname and initial. OpenAlex describes its existing
[disambiguation signals and limitations](https://help.openalex.org/data/authors/disambiguation/).

Accordingly, we retain **two sensitivity specifications**, without a confidence
band or a claimed upper/lower bound on true author counts.

There is a second problem with the proposed bound interpretation. Even valid
interval endpoints moving upward do not identify an increase. A true count
can fall from 20 to 11 while its valid interval changes from [10,20] to [11,21].
Without additional joint restrictions, an increase is guaranteed if the later
lower bound exceeds the earlier upper bound. Agreement in the direction of
two proxy curves is much weaker.

### Merging and entry do not have universal effects on Gini

For nonnegative outputs with a positive sum, use the ordinary population Gini

\[
G(x)=\frac{\sum_i\sum_j|x_i-x_j|}{2n\sum_i x_i}.
\]

Simple exact examples contradict the review's directional claims:

| Operation | Before | After | Gini change |
|---|---|---|---:|
| Merge two equal keys | [1,1,1] | [1,2] | 0 → 1/6 |
| Merge two smaller keys | [1,1,2] | [2,2] | 1/6 → 0 |
| Add a one-paper entrant | [3,3] | [1,3,3] | 0 → 4/21 |
| Add a one-paper entrant | [1,1,3] | [1,1,1,3] | 4/15 → 1/4 |

Thus the count and mean directions under a pure merge at fixed P do not imply
the same direction for concentration. Nor does rising entry mechanically raise
Gini. Singleton status does not establish entry in the first place.

Full counting measures authorship participation; fractional counting measures
allocated paper credit. Team-size variation can separate their distributions.
This is a difference between estimands, not necessarily an estimator defect.
Divergence warrants examining team structure, composition and identity; it does
not uniquely identify a collaboration mechanism. Paired mean team size actually
falls from 2.261 to 2.221 in our current sample.

### Use ORCID and additional matching rules for validation, not automatic correction

Source-supplied ORCIDs provide useful audit candidates. Profile ORCIDs propagated
through the same author-resolution system are not independent reference labels;
[OpenAlex documents the distinction](https://help.openalex.org/data/authors/orcid/).
The selected ORCID subset cannot directly calibrate the whole population.
Different ORCIDs sharing a name can be legitimate homonyms, rather than an
OpenAlex merge error. One ORCID attached to several IDs is a suspected split
to investigate, not an adjudicated error.

We will not correct headline counts from these two aggregate probabilities.
Nor is a new merger proven better because names share one coauthor, institution,
subfield or adjacent activity years. Such rules can generate candidates, but
require independent adjudication and assessment of transitive false merges.
The existing plan remains a stratified probability audit plus a separate
high-output-tail audit, retaining unresolved cases and sampling weights.

## 4. Original disclosure dashboard: the coverage criticism is substantiated

We independently parsed `script#data` and `var RATE` from
[`site/index.html` at the reviewed commit](https://github.com/Victorpolm/evolution-of-mathematical-research/blob/7d1063371ad2825ac3ad622974f6df129d1324f0/ArxivObservatory/site/index.html).
Frame counts were summed by Monday-start week and matched to scanned counts.
The review's frame/scanned totals are reproducible; its “year” groups use the
year of the week start, not exact calendar-year boundaries. Pearson correlation
is 0.8882. A standard average-rank treatment of ties gives Spearman 0.8407,
slightly different from the supplied 0.844. This small difference does not
change the coverage concern. Correlation alone does not establish its mechanism.

| Week-start year | Frame | Scanned | Coverage | Positive machine labels |
|---|---:|---:|---:|---:|
| 2023, observed portion | 16,309 | 8,829 | 54.14% | 18 |
| 2024 | 41,217 | 23,363 | 56.68% | 75 |
| 2025 | 43,774 | 27,603 | 63.06% | 336 |
| 2026, observed portion | 31,979 | 25,947 | 81.14% | 1,895 |

If every observed machine label were correct, and only unscanned outcomes were
unknown, the elementary missing-outcome range would be

\[
[c p_{obs},\ c p_{obs}+1-c].
\]

It is 0.110%–45.975% for 2023 and 5.926%–24.788% for 2026. These ranges overlap
widely, so under this information alone the sign of the frame-wide change is
not identified. They are **conditional coverage extremes**, not validated
bounds on true disclosure prevalence: classifier errors and unresolved evidence
gates require additional treatment. The
[original report already makes this distinction](https://github.com/Victorpolm/evolution-of-mathematical-research/blob/7d1063371ad2825ac3ad622974f6df129d1324f0/ArxivObservatory/reports/report_v27_full.md).

The scanner predicate accepts explicit v1 artifacts as well as artifacts with
one known version. Older papers have had more opportunity for revision, but
single-version status is not determined by elapsed time alone. “One known
version” also depends on metadata completeness. The claim that every scanned
2023 paper was never revised does not follow: explicit v1 artifacts are eligible
for revised papers too. Version provenance by cohort and acquisition selection
still need investigation. Reweighting only helps under stated missingness,
coverage and positivity assumptions; it is not an automatic cure.

The original page should display scan coverage and conditional extremes beside
the observed-label rate, preserve its unvalidated status, distinguish disclosure
from AI use, state primary-category scope and document observation cutoff
completeness. Two zero-count days alone do not establish an incomplete harvest.
Gold-standard classification and source checks of extracted tool names remain
necessary; unfamiliar names alone are not evidence of hallucination. We did
not perform those annotations or change the owner-maintained scan pipeline.

## 5. Historical and causal extensions

Three- and five-year windows remain useful once the required history is present.
Two years cannot supply them. A reference cohort must be selected using prior
history and followed with zero-output years retained; restricting to authors
still active later selects survivors. A full 1992 harvest is not required for
every research question: the proposed 2010 history/2015 headline start remains
subject to coverage validation.

Preserve the mathematical and prior-work foundations. Hulek and Teschke,
Grossman, and Fanelli and Larivière provide concrete precedents for populations,
time windows, identification and counting conventions, as detailed in the
[revised protocol](https://github.com/Victorpolm/evolution-of-mathematical-research/blob/docs/revised-method-prior-work-20260906/ArxivObservatory/analysis/STATISTICAL_RESEARCH_PLAN.md). Reproducing
definitions and, where accessible, their released data is more valuable than
claiming that our name rules outperform established disambiguation.

The proposed subfield difference-in-differences is a possible later design.
It still needs a defensible pre-period exposure measure, an estimand, comparable
measurement, credible untreated trends and treatment of other shocks, spillovers
and changing field composition. Post-2022 disclosure is not exogenous exposure.
Passing pretrend tests does not establish parallel trends; low power and
selection on passing a test can undermine inference. See
[Roth (2022), *Pretest with Caution*](https://www.jonathandroth.com/assets/files/roth_pretrends_testing.pdf).
Failure of a particular specification should be reported, without searching
post hoc for one that passes.

Exact counts for the frozen records have no sampling uncertainty relative to
those records. Inference beyond them needs a sampling or stochastic model;
an independent-author bootstrap does not resolve shared-paper dependence,
identity errors or selective exclusions. Uncertainty from a probability-sampled
validation audit is a separate, meaningful object.

## 6. Disposition of the sixteen recommendations

| Review items | Disposition |
|---|---|
| 1–3: disclosure coverage, version selection, framing | Substantiated concern; proposed owner-run coverage/provenance additions, with the qualifications above. Separate from this OpenAlex dashboard. |
| 4: acquisition | Completed for the bounded interim population; resumable helper and metadata snapshot are supplied outside the offline repository. |
| 5: denominator | Current paired runner uses full returned slots. Legacy partial-byline code still needs the allocated/unallocated-credit correction before reuse. |
| 6 and 8: longer windows and history | Retained in the protocol, not executable from the present two-year paired corpus. Longer history needs a defined frame and coverage audit. |
| 7: concentration comparison | Full and fractional Gini, top shares and single-appearance shares now visible; causal interpretation corrected. |
| 9: three-factor decomposition | Exact identity already computed; signed numerical log terms now displayed explicitly. |
| 10: third estimator and bounds | Reject the bounds claim and presumed improvement of an unvalidated third merger. Retain the two agreed sensitivity definitions. |
| 11: annual ambiguity | Implemented with within-year multiplicities, slot-weighted shares and denominators. |
| 12: ORCID correction | Source-ORCID diagnostics implemented. Independent audit remains pending; no automatic count correction. |
| 13: classifier validation | Still needed for substantive disclosure estimates; not performed in this contributor analysis. |
| 14: AI design | Deferred as a separately specified study; pretrend tests alone cannot validate it. |
| 15: frame reconciliation | Manifest overlap has been measured. Exact primary-category/byline reconciliation still requires the existing metadata export. |
| 16: decisions | This response and the protocol addendum record the broader-study choices. Owner-maintained disclosure decisions are proposed rather than silently changed. |

Priority: obtain the existing per-paper metadata needed to reconcile the frames,
audit time-varying identification and exclusions, then extend the historical
series. The immediate output is a transparent descriptive analysis of observed
keys, with measurement sensitivity as a substantive finding.

Validation: all 83,017 cached works were reread with partition/count/hash checks;
all accounting identities reconcile; 16 focused offline tests pass. The new
fixture checks within-year versus pooled mappings and slot denominators.
No full upstream-suite, manual identity or classifier-validation result is claimed.
