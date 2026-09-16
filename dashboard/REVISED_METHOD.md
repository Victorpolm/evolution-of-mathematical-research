# Revised method: participation, collaboration and mathematical publication output

Protocol: 2026-09-06; review addenda: 2026-09-15; repository update: 2026-09-16. The original sections below retain
the mathematical and prior-literature foundations. The addendum records the
bounded OpenAlex run and decisions following the second supplied review.
The historical P/A calculation is now available; independent person-level validation and the broader research program remain incomplete.

## Contributor populations and top-decile extension, 16 September 2026

The original headline ratio uses contributors active in the same year or window: $P_t/A_t$. One paper with three contributor keys gives $P/A=1/3$, even though each key coauthored one paper. The dashboard now also shows $P_t/A_{all}$ using the union of keys on all retained 2010–2025 papers, and $P_{all}/A_{all}$ for the whole sixteen-year total. The fixed pool includes zero output for keys inactive in a given year. It is not the active research workforce; its annual trend has the same percentage changes as paper counts. Full-study keys are never calculated by summing annual counts.

An offline extension reuses exactly the same 300,011 paired papers and verifies agreement with the historical baseline in all 389 windows. The full-study union contains 231,929 raw-name keys or 178,730 OpenAlex author IDs. Whole-study P/A is 1.2935 per name and 1.6786 per ID, spanning sixteen years rather than a single year.

The most prolific decile is ranked separately under fractional paper credit and full coauthored-paper counts, for both identity definitions. Annual, monthly and rolling rankings use keys active within each window. A separate cumulative ranking uses all output over the whole study; it is not an average of annual deciles or a fixed cohort followed over time. Fractional credit remains 1/k per returned slot. Full coauthored-paper counts award one paper per distinct key per paper, so repeated raw-name slots count once. Their total J can differ from the byline-slot total I used in earlier archived tables; those tables remain unchanged.

The top group has exactly 0.1 A population weight. Cutoff ties share the remaining membership proportionally, with fractional scores rounded to 12 decimals for tie identification only. Output sums use unrounded credit. Fractional top-decile share divides by P; full-count share divides by J, not the distinct-paper count. The ratio of top-decile mean output to the other 90% mean is $9S/(1-S)$ when S is the top-decile share. All cutoff counts, tie weights, means and totals are available in the aggregate JSON.

In 2025 the annual top-decile fractional share is 27.35% using IDs and 27.26% using names. Across the whole study the cumulative shares are 52.02% and 46.56%, respectively. The different exposure lengths and ranking populations prevent interpreting the gap between annual and cumulative shares as a time trend. These are descriptive observed-key results; identity, coverage and high-output-tail validation remain outstanding. The mathematical and prior-literature foundations below remain intact.

Implementation and the full report are in [analysis draft PR #2](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/2): `analysis/contributor_populations.py` and `reports/contributor_populations_20260916/CONTRIBUTOR_POPULATIONS.md`. All calculations reuse the frozen September 16 metadata; no additional API requests were made.

## Historical P/A implementation, 16 September 2026

The user authorized free-quota acquisition with an OpenAlex API key and requested that the first visible graph be papers per observed contributor, P_t/A_t, under both identity definitions. The new frozen extraction queries publication years 2010–2026; the descriptive analysis covers arXiv ID dates 2010–2025. The offline historical module and aggregate report are submitted in draft PR #2.

Calendar-year counts begin in 2010 because annual active-key counts do not need a lookback. The five-year lookback remains relevant to future entry/returner measures. The first graph uses existing OpenAlex resolved IDs and minimally normalized raw-name keys on identical retained papers. It is followed by P, A and retention, plus annual partial-byline credit accounting, within-subfield aggregates and exact growth identities. Monthly and rolling 12-month views recompute distinct-key unions over each window.

This is an observed-record comparison, not validation of people or a new identity resolver. The earlier coverage finding remains a limitation: changing retention can affect P/A, and agreement between definitions cannot remove shared selection. A single extraction, even with creation and update dates retained, does not recover historical byline states at equal indexing age. Concentration, career entry and AI effects require their separate designs and validation. The mathematical and prior-work sections below remain unchanged.

See [draft PR #2](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/2) for `analysis/historical_participation.py` and `reports/historical_participation_20260916/HISTORICAL_PARTICIPATION.md`. The older checkpoint sections below document what was known before this extraction.

## Historical window clarification, 16 September 2026

The two-year OpenAlex run is a bounded technical pilot. The existing repository
ID manifest spans August 2023–July 2026, so 2024 and 2025 are its only full
calendar years. That practical boundary is not a scientific reason to start
the historical study in 2024. Retain the provisional metadata target from
2010 onward and main comparisons from 2015 through the latest validated full
year. Annual paper and active-author counts can also be reported from 2010 if
coverage permits; entry and returner measures need adequate lookback.

A September 15 OpenAlex group-count query found 330,421 candidate works with
publication years 2010–2023 under the same Mathematics and arXiv-indexing
filters. These are acquisition-sizing counts, not arXiv upload-year counts or
contributor results. At that checkpoint, no historical work-level backfill had been collected. See the
[extension note and recorded query](../reports/historical_extension_20260915/HISTORICAL_EXTENSION.md)
for availability, observed request allowance and the coverage checks required
before adding earlier years. More history does not repair selective missingness
by itself.

Every displayed graph should state its measure, unit, time window, denominator,
source and calculation. The updated dashboard provides a title above each
graph and an explanation below it, keeps unavailable series explicitly empty,
and identifies overlapping rolling windows. Its source and aggregate data are
submitted with the implementation in draft PR #2.

## Second September 15 reply: coverage takes priority

Population participation and concentration interpretations are suspended. The
main dashboard at that checkpoint presented a coverage audit; earlier identity-comparison
charts are retained only in archived diagnostic outputs. The research question
and the mathematical/prior-work foundations below remain the longer-term plan.

The frozen-data audit identifies 206 entirely unidentified bylines in 2024 and
2,090 in 2025. Their changing share contributes 7.38 percentage points to the
10.24-point retention difference. November–December contain 1,577 of the 2025
cases. Common-weight standardization by exact returned team size and OpenAlex
primary subfield still yields retention of 95.26% versus 85.04%. This describes
the pattern; it is not a causal diagnosis of indexing lag or a selection fix.

The operational partial-ID path is now `analysis/retention_audit.py`. For every
usable k-slot byline, valid IDs receive 1/k and unidentified slots contribute
1/k to an unallocated-credit total. Entirely unusable bylines retain one whole
unallocated paper equivalent. Thus linked paper totals reconcile with allocated
credit, missing-ID credit and unusable-byline credit. Unknown people are never
represented by one artificial author. Mean allocated credit per identified ID
is explicitly separate from papers per identified ID. This path supersedes use
of the legacy prototype for incomplete metadata; it does not recover missing
people or validate the returned team size against arXiv v1.

The original ORCID proportions have limited repeated-observation opportunity:
only 75 of 2,216 source ORCIDs in 2024 and 198 of 3,699 in 2025 occur on two or
more paired papers. Among these, 5 and 29 map to multiple IDs. These selected
mapping proportions are not adjudicated split rates or population floors.
Retain names as an identity-sensitivity diagnostic and make the independent
stratified audit the route toward person-level estimates.

For cohort checks, select keys using baseline history and retain zero observed
follow-up counts. The new diagnostic follows 2024 keys into 2025 and separates
observed appearing/continuing keys, while explicitly allowing coverage loss and
identity changes to generate these states. It does not identify career entry or
incumbent behavior. Do not infer entry from an annual singleton share.

The 83,017-to-50,440 reduction is accounted for: 32,552 works fall outside the
declared 2024–2025 arXiv-ID window, 20 have ambiguous multiple IDs and five have
no unique modern ID. The outside-window works include 30,062 with 2026 IDs.
Keep these query/date filters distinct from byline exclusions and external
coverage. The accurate terms are acquired works, uniquely linked target-window
papers, usable returned bylines and retained paired papers.

A single snapshot of current bylines cannot reconstruct equal-elapsed-indexing
comparisons. Collect repeated or archival metadata, preserve source and
snapshot provenance, and inspect additions, losses and reassignment of IDs.
Equal ages or retention rates alone do not guarantee comparable selection.
The hypothesis of poor coverage at both historical endpoints must be assessed
empirically; it is not inferred from two upload cohorts.

Neither majority nor minority partial merging determines the direction of
Gini without specifying the output distribution and which groups merge.
The review's conditional claim still fails, for example, when the two smallest
keys in [1,2,4,8,16,32,64,128,256,512] become 3: Gini falls from 0.70196 to
0.66906, with no coincident values. A strict change persists in a neighborhood.
Ratios A/P and P/A are reciprocal descriptions, not alternative corrections
of the same count estimand.

A paper-cluster bootstrap requires an explicit sampling/dependence model;
authors recurring across papers prevent treating it as a universal remedy.
For a later credible difference-in-differences study, add sensitivity to
substantively justified departures from parallel trends following
[Rambachan and Roth (2023)](https://academic.oup.com/restud/article-abstract/90/5/2555/7039335).
This does not by itself supply exogenous AI exposure or comparable measurement.

## Addendum: September 15 review and interim run

The review of main commit `7d10633` concerns the legacy participation prototype
and the upstream AI-disclosure dashboard. The subsequent
[draft analysis PR #2](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/2)
contains an executed OpenAlex comparison on 45,365 paired papers from 2024–2025,
following a complete, frozen acquisition of 83,017 works. Its population is
OpenAlex-classified Mathematics indexed in arXiv, restricted by publication-year
query and arXiv-ID month. It does not replace the preferred primary-subject
arXiv frame. References below to unavailable database audits and longer history
remain applicable; the two-year paired comparison is no longer merely planned.

The observed raw-name trend reverses from −7.24% to +2.41% when only the missing-ID
gate is relaxed. Annual paired retention is 95.11% and 84.87%. Coverage is an
empirical limitation, not a problem solved by requiring complete bylines.
The new runner preserves every returned slot and excludes flagged/100-plus,
incomplete or repeated-ID bylines. The legacy partial-byline runner must not be
used to allocate the whole credit of a paper to only its identified authors.
For k total slots and m identified slots, allocate m/k to those authors and
report 1−m/k as unallocated; unknown k must remain unknown. With incomplete
allocation, the mean allocated credit is not automatically P/A.

We adopt the following clarifications from a critical reading of the review:

1. Display full-count and fractional concentration together, accompanied by
   team-size and activity distributions. Fractional credit measures allocated
   paper output, not effort. Disagreement between counting conventions does
   not uniquely identify its cause.
2. Rebuild name-to-ID and ID-to-name mappings within each year; report their
   multiplicity distributions and affected authorship-slot shares with explicit
   denominators. These are ambiguity diagnostics, not validated error rates.
   This addition has been computed from the frozen data.
3. Retain the two agreed identity definitions as sensitivity specifications.
   Reject the review's proposed bounds on people and concentration. Both can
   split and merge; even pure aggregation can lower Gini, as [1,1,2] → [2,2]
   demonstrates. Agreement of two proxy trends is not identification of a
   real-person trend. Even genuinely bounded counts can fall when both interval
   endpoints rise: 20 → 11 is consistent with [10,20] → [11,21].
4. A one-paper author may be an incumbent. Adding a one-paper entrant can lower
   Gini: [1,1,3] has Gini 4/15, while [1,1,1,3] has Gini 1/4. Keep the planned
   longer windows and reference cohorts with zero-output follow-up retained.
5. Source ORCID can identify audit candidates; profile-propagated ORCID is not
   an independent standard. Selected-subset multiplicities cannot directly
   correct the full population. Additional coauthor/institution/subfield rules
   require validation before being described as an improved estimator.
6. Preserve the exact growth identities and publish their numerical terms.
   No independent-author bootstrap is added without a target population and
   dependence model. Measurement validation is the immediate uncertainty task.
7. Treat disclosure coverage separately from authorship coverage. Missing-outcome
   extremes conditional on correct observed machine labels are not bounds on
   true disclosure prevalence allowing classifier error. Version-selection
   mechanisms and classifier validation require the existing owner-run data.
8. A subfield difference-in-differences remains a possible later design, subject
   to a credible exposure definition, counterfactual trends, spillovers and
   composition. A successful pretrend test is not sufficient validation;
   pretests can have low power and selection on passing can distort inference.
   [Roth (2022)](https://www.jonathandroth.com/assets/files/roth_pretrends_testing.pdf)
   provides the methodological basis for that caution.

The closest mathematics bibliometric studies and their methods remain in §2.
The first-stage contribution is transparent descriptive accounting and a
measurement-sensitivity assessment. No democratization, elitism or AI effect
is established by the current short, selectively covered comparison.

## 1. Research question and contribution

How do changes in mathematical paper uploads relate to changes in observed
participation, publication activity and team size? Our initial population is a
specified set of arXiv papers, not all employed mathematicians or all
mathematical research. Broader participation and a more even distribution of
publication credit are separate questions.

The first study will combine a transparent accounting of publication growth
with a sensitivity analysis of author identification. The comparison agreed
with the user is retained: distinct recorded names versus OpenAlex author IDs,
on identical papers and time windows. We do not presume to outperform
OpenAlex's disambiguation.

The contribution must be positioned as an extension and assessment of existing
mathematics bibliometrics. Comparing papers and authors is already established
in the literature. Our proposed additions are an auditable arXiv population,
explicit continuing-author/entry/exit accounting, comparable activity windows,
and an assessment of how measurement choices change the conclusions. Novelty
of this combination remains to be established against further related work.

## 2. Prior work: what was actually done, and what we adopt

| Study | Data and method checked in the original source | Consequence for this study |
|---|---|---|
| [Hulek and Teschke (2023), *How do mathematicians publish? – Some trends*](https://ems.press/content/serial-article-files/29073) | Used a June 2023 zbMATH snapshot, retaining the 96.5% of authorships classified as unambiguous. Compared annual active authors and documents, lifetime-output thresholds, and team sizes in ten MSC groups. This retained share is not an independently established accuracy rate. | Closest substantive precedent. Reuse its distinction between publication growth, collaboration and community size. Audit exclusion effects; lifetime thresholds condition on accumulated history and disadvantage recent entrants. Authors appearing in several subject groups cannot be added to obtain a unique global total. |
| [Grossman (2005), *Patterns of Research in Mathematics*](https://www.math.buffalo.edu/mad/stats/2005.research.patterns.pdf) | Used Mathematical Reviews records from approximately 1940–1999, with person identification maintained by MR. Compared decade-specific papers, authors, publication participation and team sizes; used primary MSC groupings for the later period and adjusted historical classification changes. | Preserve explicit observation windows, distinguish cumulative from period-specific counts, and examine collaboration and subfield composition. His study is a descriptive predecessor, not a controlled estimate of individual productivity change. |
| [Fanelli and Larivière (2016), *Researchers' Individual Publication Rate Has Not Increased in a Century*](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0149504) | Selected 41,427 Web of Science author profiles, including 492 in mathematics, using surnames with at least three initials and restricted geographic coverage. Profiles had to span at least 15 years; outcomes covered the first 15 years. They compared full counts, a collaboration-adjusted ratio and first-author counts across entry cohorts, and audited 50 randomly selected names. They found no overall century-long increase after adjustment, with variation across disciplines and periods. | This is a selected, persistent-career sample, not all active authors. Borrow fixed career exposure and validation; do not copy its exclusions as a representative population design. Its adjusted ratio differs from our paper-by-paper fractional credit. First-author position is not our contribution measure. |
| [Fegley and Torvik (2013), *Has Large-Scale Named-Entity Network Analysis Been Resting on a Flawed Assumption?*](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0070299) | Applied name-based splitting and lumping to disambiguated biomedical and patent datasets and examined changes in network statistics. | Name simplification is a stress test, not a reliable bracket around truth. Their estimated effects cannot be transferred numerically to arXiv mathematics. Assess errors for each statistic we intend to interpret. |
| [Beckenbach, Hulek and Teschke (2024), *The extension of zbMATH Open by arXiv preprints*](https://ems.press/content/serial-article-files/47210) | Defined an arXiv subset using historical overlap with published mathematics. Matched works by DOI first, then title/author/abstract similarities with a random-forest classifier trained using DOI matches. Discussed weaker author assignments for preprints and distinguished unpublished entries from published records. | Examine existing zbMATH links before inventing a matcher. Work-matching validation does not establish person-identification accuracy. Any external published-literature comparison must exclude preprint-only entries and account for publication delays. |

Where the released data permit, first reproduce the definitions behind Hulek
and Teschke's publication/author and team-size figures. Their article supplies
a [data deposit reference](https://doi.org/10.5281/zenodo.8234415); those files
have not been retrieved or reproduced in this revision. A current snapshot
would be an updated analysis, not an exact reproduction of their snapshot.

## 3. Mathematical accounting

Fix a corpus, a time window and an author-identification method. Let
\(\mathcal P_t\) be its papers and \(\mathcal A_t\) its active authors.
Initially assume complete bylines and one occurrence of a person per paper.

\[
P_t=|\mathcal P_t|,\qquad A_t=|\mathcal A_t|,
\qquad n_{a,t}=\sum_{p\in\mathcal P_t}\mathbf 1\{a\in p\}.
\]

For team size \(k_p\), define authorship incidences

\[
I_t=\sum_{p\in\mathcal P_t}k_p
   =\sum_{a\in\mathcal A_t}n_{a,t},\qquad
\bar k_t=I_t/P_t,\qquad \bar n_t=I_t/A_t.
\]

The exact identities are

\[
\boxed{P_t=A_t\frac{\bar n_t}{\bar k_t}},\qquad
\boxed{\frac{P_t}{A_t}=\frac{\bar n_t}{\bar k_t}}.
\]

Report the measured counts \(P_t,A_t,I_t\), alongside mean team size
\(\bar k_t\) and mean publication participation \(\bar n_t\). These contain
three algebraic degrees of freedom, not five independent outcomes. This does
not assert statistical independence of the three underlying counts.

Equal fractional credit is

\[
f_{a,t}=\sum_{p\ni a}\frac{1}{k_p},\qquad
\sum_a f_{a,t}=P_t,\qquad \bar f_t=P_t/A_t.
\]

Thus mean fractional credit is exactly the papers/authors ratio. Its
distribution across authors supplies additional information; its mean is not
an additional independent productivity measure. Equal division is a
transparent convention conserving paper totals, not a measurement of effort
or a claim that it is the only defensible credit convention. Full
participation counts remain useful. We will not infer contribution from
byline order or assume every mathematics paper is alphabetically ordered.

**Correction to the supplied critique:** at fixed \(\bar n_t\), increasing
\(\bar k_t\) lowers \(P_t/A_t\). At fixed \(P_t,A_t\), adding coauthors
raises both \(\bar k_t\) and \(\bar n_t\), leaving \(P_t/A_t\) unchanged.
There is no unconditional direction without specifying what remains fixed.

For positive totals in adjacent periods,

\[
\Delta\log P=\Delta\log A+\Delta\log\bar n-\Delta\log\bar k.
\]

This is descriptive accounting; the terms are not independent causal effects.

The prior-study adjustment also requires care. In general,

\[
\frac{n_a}{n_a^{-1}\sum_{p\ni a}k_p}
\ne \sum_{p\ni a}\frac{1}{k_p}.
\]

For two papers with team sizes 1 and 3, the left side is 1 and the right side
is \(4/3\). An exact comparison with the earlier study must reproduce its
denominator convention; it cannot silently substitute our conserved credit.

## 4. Continuing authors, entry and exit

For adjacent non-overlapping calendar years define

\[
C_t=\mathcal A_t\cap\mathcal A_{t-1},\quad
E_t=\mathcal A_t\setminus\mathcal A_{t-1},\quad
X_t=\mathcal A_{t-1}\setminus\mathcal A_t.
\]

Then

\[
\boxed{
P_t-P_{t-1}=
\underbrace{\sum_{a\in C_t}(f_{a,t}-f_{a,t-1})}_{\text{continuing-author credit change}}
+\underbrace{\sum_{a\in E_t}f_{a,t}}_{\text{entry credit}}
-\underbrace{\sum_{a\in X_t}f_{a,t-1}}_{\text{exit credit}}.
}
\]

Make this a central explanatory figure after longitudinal identity validation.
Show the three signed components in paper equivalents and their sum. Also
report \(|C_t|,|E_t|,|X_t|\), and reconcile
\(A_t-A_{t-1}=|E_t|-|X_t|\). Avoid percentage contributions when net growth
is close to zero; signed contributions can exceed 100% when components offset.

The continuing-author term includes changes in team sizes and fractional
allocation. It is not a pure measure of additional individual research work.
Changing database coverage or identity assignments can also create apparent
entry and exit. The raw-name version measures continuing, entering and exiting
name keys, and must be labelled accordingly.

Two complete adjacent years suffice for this identity. More history is needed
to partition \(E_t\) into authors first observed in the available history and
authors returning after a gap. Use **first observed in this corpus**, never
“first-ever researcher.” A disappearance means no observed paper during that
window, not retirement. Changes of field can generate field entry and exit.

## 5. Existing data and the first audit

The [import reconciliation](../reports/s3_import.json) documents 168,027 paper
IDs with archive members for August 2023–July 2026. That is an acquisition
frame, not yet a verified primary-mathematics census. The separate 2023–2025
OpenAlex pilot documented 69,166 usable works, 155,781 identified authorship
links and 8,042 unidentified authorship slots. Its numerator and denominator
must not be combined with the larger manifest population.

Johannes's database already has fields for arXiv ID, created date, raw authors,
categories, primary category and DOI. Reuse existing metadata and matches.
The first aggregate audit must report, by submission month:

1. Papers by recorded primary category, including missing/unknown categories.
2. Primary-mathematics, cross-listed-only and alias-category membership.
3. Missing dates, unparsable author lists and incomplete or group bylines.
4. OpenAlex work-match and authorship-slot identification rates.
5. Papers with complete, aligned, non-truncated authorships; exclusions by reason.
6. Retention and team-size distributions by category, to expose selective loss.

For paired author-method comparisons, retain exactly the same papers and
aligned arXiv authorship slots. Keep the full-frame paper curve separately
labelled. Completeness restrictions can select against recent work or large
teams; they are a reproducibility rule, not a cure for selection bias.

The database and raw pilot CSV are absent from the shared source snapshot by
the existing [contribution policy](../CONTRIBUTING.md). The owner can run the
offline aggregate audit or provide a metadata-only export. This revision does
not infer the audit results from the manifest size and does not start a new
download. The requested analysis awaits access to those records.

## 6. Corpus definitions and version handling

The preferred headline specification is **primary-subject mathematics**, with
an explicit, versioned alias crosswalk. It is a proposal to fix before inspecting
the substantive trends. The broader specification includes any mathematics
category, including cross-listings. Neither is intrinsically an invalid corpus;
they describe different populations.

| Alias-equivalent subject labels | Treatment |
|---|---|
| `math.IT`, `cs.IT` | One information-theory subject; inclusion is declared explicitly. |
| `math.NA`, `cs.NA` | One numerical-analysis subject. |
| `math.ST`, `stat.TH` | One statistics-theory subject. |
| `math.MP`, `math-ph` | One mathematical-physics subject. |

Verify the crosswalk against the [arXiv taxonomy](https://arxiv.org/category_taxonomy)
and historical category metadata. Preserve the recorded primary label and all
category tags. An alias does not create a second paper or an additional field
membership. The proposed primary-subject definition includes these
mathematics-labelled subject groups regardless of which equivalent label is
stored; report literal `math.*` primary counts as a separate diagnostic.

Compare primary-subject mathematics, any-mathematics membership, and a narrower
primary-subject specification excluding the four alias groups above. The last
is a deliberately changed subject scope, not automatically a cleaner estimate.
Show individual categories as well, including GM/HO and information theory,
rather than attributing any difference to “contamination.” The external
editorial mathematics corpus provides another scope comparison.

Count one arXiv ID once, at its first-submission timestamp. Revisions and
cross-listings are not new papers. Use ID month only as a flagged fallback.
Record withdrawals separately under a fixed retention rule: for an upload
estimand, retain the original submission if its metadata are available.

Freeze extraction date, source versions, categories and authorship metadata.
The current harvested author list need not be the v1 byline. Describe the
main analysis as first-submission-dated papers with bylines from the frozen
metadata; assess v1/current-byline differences where archived data permit.
Never substitute journal-publication dates for arXiv submission dates.

## 7. Identity comparison and validation

**Main paired comparison.** Count (a) name keys with only Unicode NFC and
whitespace normalization, preserving initials, accents, punctuation and case;
and (b) OpenAlex author IDs. Keep raw strings and the normalizer version.
OpenAlex's existing model supplies the grouping; no new person resolver is
assumed. Unknown and deleted placeholder IDs are not people. The provider
[documents its signals, ID replacement and special IDs](https://help.openalex.org/data/authors/disambiguation/).

Paper matching and author alignment are different tasks. A published version
can have a changed byline. A match to its DOI alone does not assign its author
IDs to every arXiv author position. Flag additions, removals and ambiguous
alignments; do not merge on a shared name alone.

Preserve individual byline slots before grouping. Two different coauthors can
have the same recorded name on one paper. In the name specification, count
their slots separately for \(I_t\) and allocate both fractional credits to the
name key. Then \(I_t/A_t\) means authorship occurrences per name key, not
necessarily distinct papers per person. Silently converting a byline to a set
of names would corrupt team size and the accounting identities. Repeated
OpenAlex IDs within a byline require review rather than automatic deduplication.

**Additional diagnostics, not a replacement for the two main methods:**

- Surname plus first initial, where structured parsing is reliable, can expose
  sensitivity to aggressive name collapsing. It is not a lower bound on people.
- ORCID-supported and zbMATH-linked cases can support an identity audit.
  Distinguish source-supplied ORCID from a profile-level ORCID propagated by a
  disambiguation model; [OpenAlex documents that distinction](https://help.openalex.org/data/authors/orcid/).
  Agreement is evidence, not infallible or necessarily independent truth.
- ORCID-only cases are selected. Compare methods on the same eligible cases;
  do not divide all papers by the small ORCID-author population. If allocating
  output only to those authors, retain original team-size denominators and
  report their allocated credit, not the whole corpus paper count.

Use two complementary audits: a probability sample stratified by period,
name frequency, initials-only records, missing identifiers and first-observed
status; and a targeted audit of the high-output tail before concentration is
interpreted. Retain selection probabilities for population-error estimates.
Audit suspected splits and merges, including works outside a sampled profile
when necessary. High-output inspection alone cannot estimate population-wide
author-count error. Preserve unresolved cases and independent review decisions.
Sample sizes should follow the desired precision and tail coverage, not a
claim that a convenient 100 profiles validates everything. Do not infer
ethnicity or nationality from names; use observable ambiguity features.

Freeze one OpenAlex snapshot for all historical publication years. The July
2023 replacement of IDs is a break between identifier regimes, not an automatic
break at publication year 2023 inside a single recent snapshot. If archived
snapshots are available, compare partitions of the same historical authorship
records across snapshots. Separate newly indexed works from changed author
assignments and global renumbering. Worse resolution for new authors is a
hypothesis to audit, not an established error rate.

## 8. Time windows, observed activity and cohorts

The existing 36-month frame supports a technical pilot and, subject to matching
coverage, the complete calendar-year comparison 2024 versus 2025. It supplies
one complete three-year window, not a series of independent three-year
observations, and supplies no five-year window. Recent 2026 series remain
provisional until completeness is audited. Excluding an arbitrary last month
alone does not establish complete coverage.

For a longer study, retain the earlier provisional target of metadata from
2010 onward and headline years from 2015 through the latest validated complete
year. Earlier available history is useful for lookback, but a full 1992 harvest
is not a prerequisite for every estimand. Final start/end years depend on a
documented coverage audit, not a convenient historical break.

Compare active-author counts over 1-, 3- and 5-year windows where feasible.
Deduplicate over each whole window; never sum annual unique-author counts.
Report both total \(I(T)/A(T)\) and its annualized value \(I(T)/(T A(T))\).
Neither measures a workforce including people with no observed publications.
Use non-overlapping years for the primary transition decomposition. Rolling
windows are useful visual summaries, but neighbouring points overlap and are
not independent replications.

Report the frequency distribution
\(h_{j,t}=\#\{a:n_{a,t}=j\}\), with counts and shares, particularly at
\(j=1,2,3\), and the fuller distribution rather than only its mean. Do not
use Good–Turing or Chao estimates as counts of unobserved mathematicians;
publication events do not automatically satisfy their sampling assumptions.

Later cohort comparisons will hold observed career exposure fixed, keep
zero-output follow-up years and avoid requiring future publication to remain
in the sample. Define cohorts by first observed publication with a fixed
lookback and flag the left boundary. Only use cohorts with complete follow-up
for a given horizon. Cohort tables do not identify separate age, period and
cohort effects: period equals cohort plus observed age.

## 9. External coverage and subfield composition

arXiv use is part of what we observe. Its growth alone does not establish
growth of all mathematical output. Use zbMATH Open's published corpus as a
mathematics-specific external comparison when accessible; MathSciNet is another
possible source if access permits. The [zbMATH API description](https://ems.press/content/serial-article-files/33042)
documents work and author interfaces. Access through an institution is not
assumed from the user's affiliation.

A better posting-coverage diagnostic than a ratio of unrelated annual totals is

\[
q_{y,s}=\frac{\#\{\text{eligible published zbMATH works in year }y,
\text{ field }s\text{ linked to an arXiv version}\}}
{\#\{\text{eligible published zbMATH works in year }y,\text{ field }s\}}.
\]

Use mature publication cohorts or a common follow-up horizon, distinguish
preprint-only entries, and report matching and publication lags. Changing
indexing policies and link coverage still affect this diagnostic; it is not
an unbiased correction factor for the total research population. Do not
confound journal year in this diagnostic with submission year in our main series.

Report within-subfield trends before interpreting pooled changes. Assign each
paper to a single declared primary subject for additive paper accounting.
Authors can occur in several fields, so global author totals must be set
unions. Standardize paper-level quantities, such as team size, to a fixed
declared field distribution when informative. Author-level standardization
needs its own author weights or disjoint reference classification; weighting
field ratios by paper shares does not reconstruct the global author ratio.

## 10. Uncertainty and specification displays

Exact counts in a frozen observed dataset need no conventional sampling error
bars. Measurement uncertainty, exclusions and external generalization remain.
Probability-sampled validation can have sampling intervals; any temporal or
superpopulation interval needs an explicit model and dependence assumptions.

Predeclare a manageable grid, recording infeasible cells explicitly:

| Dimension | Core comparison |
|---|---|
| Corpus | Primary-subject, any-mathematics, narrower primary-subject scope |
| Identity | Normalized recorded names and OpenAlex IDs, on the same papers |
| Activity window | 1, 3, 5 years where complete data exist |
| Output convention | Full authorship participation and conserved fractional credit |
| Coverage | Complete aligned papers, plus separately labelled broader-frame diagnostics |
| Field and recent cutoff | Within-field results; validated mature cutoff and provisional recent extension |

Show identified curves or a specification range within comparable targets.
Different activity windows and populations belong in separate panels. A fan
of specifications is not a confidence interval, and the fraction of curves
with positive growth is not a probability that growth is positive. If a sign
changes across reasonable definitions, report that instability as a result.
Always expose matched/retained denominators and missing periods.

## 11. Concentration: second stage

Retain top 1%, 5% and 10% shares, Lorenz curves, Gini and output quantiles.
Add a fixed top-N share (initially N=100 where the population is large enough)
to distinguish relative rank from a fixed number of authors. Declare tie rules;
fractional allocation of tied boundary groups avoids ID-dependent rankings.

Add Theil T when a disjoint group decomposition is needed. For nonnegative
credit \(x_a\), population \(N\), and positive mean \(\mu\),

\[
T=\frac1N\sum_a\frac{x_a}{\mu}\log\frac{x_a}{\mu}.
\]

Use the continuous extension \(0\log0=0\). For disjoint groups with output
shares \(s_g=N_g\mu_g/(N\mu)\),

\[
T=\sum_g s_g T_g+\sum_g s_g\log(\mu_g/\mu).
\]

Zero-output groups contribute zero to these weighted terms. Entry cohorts
form a natural disjoint grouping. Overlapping field memberships do not; an
explicit partition or a separately derived allocation is required. Theil
complements Gini rather than replacing all other summaries.

Compare the active-author distribution with a fixed reference cohort selected
using pre-period history and followed with zero-output years retained. This
answers a different question and excludes later entrants by design; it is not
the population of all mathematicians. A retrospective surrounding-window
population is another labelled sensitivity analysis only where both endpoints
are observed.

Entry can change concentration with no change in incumbents' output, but the
direction is not universal. For example, Gini falls from about 0.490 for
outputs [1,100] to 0.437 for [1,50,100], although 50 is below the old mean.
Short-window singleton concentration also behaves differently under full
and fractional credit because team sizes can vary.

## 12. Interpretation and later questions

Increasing observed participation does not, alone, establish lower barriers
to a research career. Publication counts and fractional credits do not measure
effort, quality, importance or causal productivity. Composition, posting
propensity, field changes and collaboration must remain visible in the account.

AI is a later research question. An association with disclosed AI use requires
its own design and reflects disclosure as well as use. A uniform subfield
trend is not a falsification of an AI effect, and a larger change in allegedly
AI-adjacent fields would not establish one. Such predictions need independent
exposure measures and justified identifying assumptions. Pre/post-2022 alone
is insufficient.

Keep career-stage composition, persistence and concentration as planned
extensions once identity measurement is adequate. Paper length, references,
field breadth and collaboration networks remain later descriptive modules.
Preserve a separate design for any quality study.

## 13. Execution sequence and deliverables

1. Discuss this protocol and the closest prior studies; fix the corpus rules,
   naming normalization and distinction between pilot and historical study.
2. Run the aggregate metadata and matching audit on the existing database.
   Attempt a definitions-level reproduction of the closest published study
   when its released data are available.
3. Freeze the paper frame, byline source, identity snapshot and feasible
   periods. Document excluded records and validate author parsing/alignment.
4. Produce paired name/ID counts and the exact paper/author/incidence account.
   Audit identity errors across periods before interpreting person trends.
5. Produce the continuing/entry/exit decomposition for validated adjacent
   years; add returner and cohort analyses only with sufficient history.
6. Extend the historical window through the owner's data workflow if required;
   then evaluate 3-/5-year windows and external posting coverage.
7. Audit the high-output tail and produce concentration statistics.
8. Update the existing website with validated aggregates and specification
   controls. Show papers and author series indexed to a common baseline,
   team sizes and participation separately, and the signed transition
   decomposition. Keep compact sparklines with exact values available.

Retain work, authorship-slot, author-year, author-window and transition tables.
Each output needs source snapshot, corpus rule, date rule, identity method,
window, credit convention, coverage and exclusion counts. Work-level and
authorship-level identifiers remain untracked under the contribution policy.

The current aggregation prototype is not an implementation of all this
protocol. Raw-name alignment, longitudinal decomposition, snapshot-drift
audits and the additional concentration diagnostics require implementation.
This revision checks formulas on synthetic examples only; it does not supply
new contributor estimates or rerun empirical analyses. No owner decisions in
the upstream AI-disclosure pipeline or taxonomy are changed by this proposal.

## Appendix A. What the activity-window illustration does and does not show

For a fixed underlying population with illustrative Poisson publication
incidences \(N_i(T)\) of mean \(\lambda_iT\),

\[
\mathbb E[A_{obs}(T)]=\sum_i(1-e^{-\lambda_iT}),\qquad
\mathbb E[I(T)]=T\sum_i\lambda_i.
\]

Under finite sums and positive total rate, the ratio of these expectations
tends to 1 as \(T\to0\). It is not generally
\(\mathbb E[I(T)/A_{obs}(T)]\); windows with no active author also need
handling. The model is an illustration, not an assumption that coauthors'
publication events are independent Poisson processes.

Fixed-window comparisons validly describe observed active authors even when
the distribution changes. Interpreting them as changes in individual rates
requires separating composition from within-person change. Adding people with
low fixed rates changes the population's rate distribution even if no
incumbent changes rate. This motivates the frequency tables, window
comparisons and observed-cohort analysis; it does not identify the unseen zeros.

## Appendix B. Disposition of the supplied critique

| Proposal or assertion | Decision and reason |
|---|---|
| Keep exact incidence/fractional identities | Adopt; mean fractional credit is derived, while its distribution is informative. |
| Larger teams mechanically raise P/A | Correct the sign conditional on fixed participation; no unconditional direction. |
| Replace aggregate ratios with continuing/entry/exit accounting | Add that account centrally; retain useful derived ratios. Neither is causal or immune to measurement error. |
| Three years cannot support any transition decomposition | Adjacent-year observed transitions are feasible; first-observed/returner distinctions and long windows need more history. |
| Window selection and low-output mass matter | Adopt frequency distributions, equal-exposure comparisons and explicit populations; do not estimate the unseen workforce with unvalidated capture models. |
| Any-math is not mathematics; alias removal is always cleaner | Reject the categorical claim. Define alternative scopes explicitly and audit composition. |
| Raw strings and initials provide bounds around true authors | Reject as bounds. They are informative stress tests with both splitting and merging errors. |
| Backward extension necessarily crosses the OpenAlex 2023 break | Correct: using one recent snapshot for all publication years avoids mixing old and new ID regimes. |
| Audit the top instead of a random sample | Use both, because author totals/entry and tail concentration have different validation needs. |
| Entry always raises Gini | Reject the universal direction; composition effects depend on the distributions. |
| Census data make every confidence interval meaningless | Avoid sampling bars for deterministic frame counts; retain justified uncertainty for validation samples or explicit stochastic targets. |
| Cohort tables solve age-period-cohort identification | They improve comparisons but do not remove the exact age-period-cohort relation. |
| AI-adjacent versus other fields is a ready-made falsification test | Do not adopt without an independently justified mechanism and exposure design. |
| Engage prior work before running the analysis | Adopt; Hulek–Teschke is a particularly close mathematics-specific precedent, alongside the other studies above. |
| Harvest everything immediately | Reuse and audit existing data first. Extend only to meet a specified estimand and through the established acquisition workflow. |
