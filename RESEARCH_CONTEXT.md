# RESEARCH_CONTEXT.md

_Last updated: 2026-09-16_

The detailed first-stage proposal is the
[revised statistical research plan](ArxivObservatory/analysis/STATISTICAL_RESEARCH_PLAN.md).
It incorporates a mathematical and prior-literature review, preserves the
paired recorded-name/OpenAlex-ID comparison, and distinguishes the existing
three-year pilot from a longer historical study. The historical and validation
stages remain proposals; the bounded OpenAlex comparison below has now run.

## Current empirical checkpoint

**After the second September 15 reply, population trend interpretations are
on hold.** The main dashboard is now a coverage audit. Earlier contributor and
concentration charts are withdrawn from its primary view and retained in the
archived diagnostic output.

The new audit finds 206 entirely unidentified bylines in 2024 and 2,090 in 2025,
accounting for 7.38 percentage points of the 10.24-point retention gap. Of the
2025 entirely unidentified bylines, 1,577 occur in November–December. Retention
remains 95.26% versus 85.04% after standardizing on common exact-team-size and
subfield cells. This locates the problem; it does not establish indexing lag
or neutralize selection. The snapshot has no indexing-history clock.

`analysis/retention_audit.py` implements partial-ID credit with explicitly
unallocated missing-ID and unusable-byline credit. It also reports upstream
date-window filtering, repeated-observation ORCID diagnostics and baseline
observed-key cohorts with zero follow-up retained. The mathematical and
prior-work protocol remains intact. The updated offline code, aggregate results
and frozen acquisition manifest are submitted in draft analysis PR #2; the
revised method is submitted in draft PR #3. Raw source metadata remains a
separate input. Main-branch integration remains an owner review decision.

The 2024–2025 interval is a technical pilot, not the intended historical scope.
Those are the only full calendar years in the existing August 2023–July 2026
repository ID window. The historical target remains metadata from 2010 onward,
with main comparisons from 2015 after a five-year lookback, subject to coverage
validation. An aggregate OpenAlex availability check on September 15 found
330,421 candidate works with publication years 2010–2023 under the same field
and indexing filters. Those are not upload-year counts or contributor estimates;
the historical work-level backfill has not been collected. See the
[historical extension note](ArxivObservatory/reports/historical_extension_20260915/HISTORICAL_EXTENSION.md).

A frozen OpenAlex-only run now compares minimally normalized source names with
existing OpenAlex author IDs on identical eligible papers for 2024–2025.
It is available in [draft analysis PR #2](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/2)
and the [participation dashboard](https://mathematics-research-observatory.tim-gehrunge-2308.chatgpt.site).
This is separate from the upstream AI-disclosure dashboard reviewed at main
commit `7d10633`; both new analysis and method documents remain in draft PRs.

The main finding is coverage sensitivity: paired byline retention falls from
95.11% to 84.87%. The paired raw-name count falls 7.24%, but relaxing only the
missing-ID rule gives a 2.41% increase. Neither result establishes the direction
of change in real-person participation. Names and IDs remain two specifications,
not upper/lower bounds or validated corrected counts.

The response to the second review adds annual name/ID mapping diagnostics,
source-ORCID coverage, full versus fractional concentration, single-appearance
shares and explicit log-growth terms. It preserves the mathematical identities
and prior-work comparison. Exact arXiv primary-category reconciliation,
independent identity validation, longer history and any AI causal design remain
outstanding. See the protocol's September 15 addendum for the methodological
decisions and the analysis PR for the full response.

## 1. Research program

### Working theme

**The evolution and democratization of mathematical research**

The broad objective is to understand quantitatively how the mathematical research ecosystem has changed over time.

The initial focus is the distribution of research production:

- How much has mathematical publication output grown?
- How much of that growth comes from more researchers versus more output per researcher?
- Has participation in mathematical publishing broadened?
- Has publication output become more evenly distributed or more concentrated among highly productive authors?
- How has the career-age composition of publishing mathematicians changed?

Later extensions may study collaboration, interdisciplinarity, article length, reference practices, and eventually possible changes associated with widespread AI adoption.

The AI question is not part of the initial identification strategy. It should be approached only after establishing a credible historical baseline.

---

## 2. Main research question

The current central question is:

> **Has mathematical research become more broadly distributed across researchers over time, or has publication output become increasingly concentrated among a relatively small set of highly productive mathematicians?**

The term **democratization** should be operationalized rather than used normatively.

For the first stage, distinguish two notions:

### Participation democratization

Has the number and breadth of people participating in mathematical publishing increased?

### Productivity democratization

Has mathematical research output become more evenly distributed across active researchers?

Geographic, institutional, and career-stage democratization are possible later extensions.

---

## 3. Core decomposition of publication growth

For one fixed corpus, window and author-identification method, let
\(P_t\) be paper count, \(A_t\) active-author count and \(I_t\) authorship
incidences. With mean team size \(\bar k_t=I_t/P_t\) and mean publication
participation \(\bar n_t=I_t/A_t\), the exact identity is

\[
P_t=A_t\frac{\bar n_t}{\bar k_t},
\qquad
\Delta\log P=\Delta\log A+\Delta\log\bar n-\Delta\log\bar k.
\]

For equal paper-level fractional credit
\(f_{a,t}=\sum_{p\ni a}1/k_p\), \(\sum_a f_{a,t}=P_t\) and its
mean is exactly \(P_t/A_t\). The mean is therefore a derived quantity;
the distribution of fractional credit remains informative. At fixed
\(\bar n_t\), larger teams lower \(P_t/A_t\).

The revised protocol also accounts for adjacent-year paper changes through
continuing-author credit change, entry credit and exit credit. These are
descriptive identities, not causal effects or direct measures of research
effort. Entry means newly observed activity relative to the previous window;
distinguishing first-observed authors from returners requires lookback.

Coverage, identity errors, field composition and changing arXiv participation
must be assessed before interpreting these quantities as changes in people
or publication behavior.

---

## 4. Initial empirical modules

### 4.1 Publication growth

For each year \(t\), measure

\[
P_t = \#\{\text{mathematics papers published in year }t\}.
\]

Study:

- annual paper counts,
- growth rates,
- log-scale growth,
- broad-field decomposition if classification quality permits.

---

### 4.2 Active-author population

For each year \(t\), measure the population of authors participating in mathematics.

A simple definition is

\[
A_t = \#\{\text{authors with at least one mathematics paper in year }t\}.
\]

Alternative definitions using rolling 3-year or 5-year windows should be compared.

The final active-author definition has not yet been fixed.

---

### 4.3 Output per researcher

Initial descriptive quantities include

\[
\frac{P_t}{A_t}.
\]

Because papers may have multiple authors, also measure author-paper incidences

\[
I_t =
\sum_{p \in \mathcal P_t}
n_p,
\]

where \(n_p\) is the number of authors on paper \(p\).

Then

\[
\frac{I_t}{A_t}
\]

measures mean publication participations per active author.

Both full-counting and fractional-counting publication activity should be studied.
Their distributions answer different questions; mean fractional output is already
\(P_t/A_t\), not an additional independent outcome.

For fractional counting, an author on a paper with \(n_p\) authors receives \(1/n_p\) paper-equivalents.

---

## 5. Concentration of mathematical output

This is the highest-priority substantive module after the basic growth decomposition.

For each year or multi-year window:

1. define the active-author population,
2. compute author productivity,
3. rank authors by productivity,
4. measure how total output is distributed across the ranking.

### Main statistics

Track publication shares produced by:

- top 1%,
- top 5%,
- top 10%,
- top 20%,
- bottom 50%.

For example,

\[
S_{10,t}
=
\frac{
\text{output of the top 10\% of active authors}
}{
\text{total author output}
}.
\]

Also compute:

- Lorenz curves,
- Gini coefficients,
- productivity quantiles,
- fraction of authors with exactly one publication,
- possibly top 0.1% output shares.

Because productivity is heavy-tailed, means should not be used as the sole summary statistic.

Useful distributional views include:

- median and upper quantiles,
- log-scale histograms,
- complementary CDFs,
- rank-frequency plots.

---

## 6. Career age and cohorts

A second major module is the career-age composition of publishing mathematicians.

The initial proxy is

\[
\text{observed career age}_{i,t}
=
t-\text{first observed publication year}_i.
\]

This should be described as **years since first observed publication**, not literal academic age.

Potential analyses:

- median observed career age by year,
- distribution by year,
- shares in 0–5, 6–10, 11–20, and 20+ year groups,
- cohort analysis by first observed publication year,
- productivity at comparable career ages across cohorts,
- entry and persistence of new authors.

Potential persistence measures include the probability that a first-time observed author publishes again within 2, 5, or 10 years.

---

## 7. Later research modules

These are part of the broader program but are not the immediate priority.

### 7.1 Article length

Question:

> Are there more mathematical papers partly because manuscripts have become shorter?

Possible measures:

- page count,
- word/token count,
- section count,
- other manuscript-length proxies.

OpenAlex may be insufficient for this. arXiv is likely a more useful data source.

The better formulation is to study the **distribution of mathematical manuscript length over time**, rather than only mean length.

### 7.2 Collaboration

Measure:

- mean and median authors per paper,
- share of single-author papers,
- shares of papers with 2, 3+, 5+, or 10+ authors,
- collaboration trends by mathematical area.

### 7.3 References

Study references per paper over time.

Historical reference coverage must be validated before interpreting trends.

### 7.4 Research breadth / interdisciplinarity

Question:

> Are individual mathematicians publishing across a broader range of mathematical areas than before?

Candidate metrics include:

- number of distinct fields/topics,
- entropy of an author's field distribution,
- effective number of fields,
- eventually distance-weighted measures of research breadth.

### 7.5 Cross-field collaboration

Distinguish personal research breadth from collaboration between researchers with different prior research profiles.

A possible future statistic is the mathematical distance between coauthors' pre-collaboration research areas.

---

## 8. Long-term AI question

A later-stage question is:

> Has widespread AI adoption changed mathematical research production, collaboration, or interdisciplinarity?

Possible mechanisms include faster literature search, easier learning of adjacent fields, improved coding/computation, easier writing, and lower barriers to cross-field work.

However, a simple pre/post-2022 comparison is not enough for causal attribution.

Potential confounders include:

- pre-existing secular trends,
- COVID-era effects,
- changes in arXiv usage,
- database coverage changes,
- generational changes,
- shifts in mathematical field composition,
- publication incentives.

The historical analyses in the initial project are intended to establish the baseline needed before this question can be addressed seriously.

---

## 9. Primary data source

For the first-stage study, **arXiv defines the paper population** and
**OpenAlex supplies the initial author-identity layer**. Compare OpenAlex IDs
with recorded-name counts on the same papers. zbMATH Open supplies a
mathematics-specific prior study and a proposed external coverage/identity
comparison; it is not assumed to provide infallible person identities.

Relevant objects include:

- works,
- authors,
- authorships,
- publication dates,
- cited works,
- topics/fields,
- institutions,
- venues/sources.

Potential complementary sources include:

- arXiv,
- Crossref,
- Semantic Scholar,
- zbMATH,
- MathSciNet where access and licensing permit.

OpenAlex is a measurement system rather than ground truth.

---

## 10. Definition of the mathematics corpus

A central unresolved methodological issue is how to define a mathematics paper.

Candidate approaches include:

- OpenAlex field classification,
- OpenAlex topic classification,
- mathematics-journal/source classification,
- arXiv mathematics categories,
- combinations of the above.

The definition must be tested for historical stability.

Changes in OpenAlex classification or indexing should not be mistaken for changes in mathematical research itself.

This is one of the first pieces of the pipeline that needs empirical validation.

---

## 11. Main measurement risks

### Author disambiguation

OpenAlex may merge distinct people or split a single researcher into multiple author profiles.

This can directly affect:

- author counts,
- productivity,
- concentration,
- observed career age,
- interdisciplinarity,
- collaboration networks.

Extreme productivity profiles and implausibly long careers should therefore be inspected.

### Historical coverage

Older works and metadata may be less completely indexed.

Coverage diagnostics should include, by year where possible:

- share of works with author IDs,
- DOI coverage,
- reference coverage,
- topic/field coverage,
- institution coverage,
- source coverage.

Some analyses may need to be restricted to a period with sufficiently stable metadata.

### Left truncation

The first publication observed in OpenAlex may not be the researcher's true first publication.

This particularly affects observed career-age estimates.

### Field-composition effects

Aggregate changes can arise because the relative sizes of mathematical subfields change, even if publication behavior within each field is stable.

Important aggregate findings should eventually be decomposed by broad mathematical area.

### Coauthorship inflation

Full counting gives every author one publication credit and therefore increases total author-publication events as collaboration grows.

Important productivity and concentration results should therefore be compared under full and fractional counting.

---

## 12. Units of analysis

The project will need several distinct analytical tables.

### Work level

One row per paper.

### Authorship level

One row per author-paper pair.

### Author-year level

One row per author per year.

### Author-window level

One row per author per multi-year analysis window.

### Cohort level

Authors grouped by first observed publication year.

The unit of observation must remain explicit in every analysis.

---

## 13. Current hypotheses

These are hypotheses, not established findings.

### H1

The number of mathematical papers has increased substantially.

### H2

The number of active mathematical researchers has increased substantially.

### H3

Publication activity per active researcher has increased.

### H4

Mathematical publication output may have become more concentrated among highly productive researchers.

The opposite remains possible and must be allowed by the analysis.

### H5

Coauthorship has increased and the share of single-author papers has declined.

### H6

Researchers may publish across a broader range of mathematical topics than in earlier periods.

### H7

Cross-field collaboration may have increased.

### H8

Mathematical manuscripts may have become shorter.

### H9

Reference lists may have become longer.

No hypothesis should be treated as a result until it has been tested and subjected to robustness checks.

---

## 14. Minimum viable first study

A coherent first paper/study should focus on:

> **The growth and concentration of mathematical research production.**

Core analyses:

1. mathematics papers per year,
2. active mathematical authors per year,
3. author-paper incidences per year,
4. output per active author,
5. author productivity distributions,
6. top 1%, 5%, 10%, and 20% output shares,
7. Lorenz curves,
8. Gini coefficients,
9. years-since-first-observed-publication distributions,
10. cohort/entry analysis,
11. metadata coverage diagnostics,
12. robustness to counting convention, active-author definition, time window, and mathematics-corpus definition,
13. continuing-author, entry and exit credit accounting for validated adjacent years.

Team size belongs in the core accounting. Extended collaboration networks,
article length, references, interdisciplinarity, and AI remain secondary until
this core analysis is credible.

---

## 15. Initial figure set

The first analysis should aim to produce:

1. **Mathematics papers per year**
2. **Active mathematical authors per year**
3. **Publication activity per active author**
4. **Author productivity distributions for selected periods**
5. **Top-productivity-group output shares over time**
6. **Lorenz curves for selected periods**
7. **Gini coefficient over time**
8. **Distribution of years since first observed publication**
9. **Entry and persistence of new authors**
10. **OpenAlex coverage diagnostics over time**

---

## 16. Important robustness dimensions

The main findings should eventually be checked under:

- 1-year, 3-year, and 5-year active-author definitions,
- annual versus multi-year analysis windows,
- full versus fractional publication counting,
- alternative definitions of the mathematics corpus,
- exclusion of suspicious author profiles,
- restriction to periods with stable metadata coverage,
- broad-field decomposition.

A result that depends strongly on one arbitrary specification should be reported as unstable.

---

## 17. Current project state

The project is currently in the **research-design and data-acquisition/pipeline stage**.

What has been established so far:

- The broad research program concerns the historical evolution of mathematical research.
- The first substantive focus is democratization/concentration of mathematical publishing.
- arXiv is the initial paper frame and OpenAlex the initial author-ID layer.
- The main first-wave statistics and methodological risks have been identified.
- Concentration should be measured with top shares, Lorenz curves, Gini coefficients, and the full productivity distribution rather than a single statistic.
- Publication growth should be decomposed into researcher-population growth, researcher productivity, and coauthorship.
- Career age should initially be measured as years since first observed publication.
- Causal claims about AI are explicitly outside the first-stage analysis.

No substantive empirical result has yet been established merely by inclusion in this document.

---

## 18. Immediate next steps

### 1. Validate the mathematics corpus

Audit the existing arXiv metadata and establish a reproducible mathematics
corpus with explicit primary-category, cross-listing and alias rules. Assess
historical stability and matching to OpenAlex before interpreting trends.

### 2. Build coverage diagnostics

Determine the time range over which OpenAlex metadata is adequate for longitudinal analysis.

### 3. Build the core analytical tables

At minimum:

- works,
- authorships,
- author-year activity.

### 4. Produce the basic growth decomposition

Calculate:

- papers/year,
- unique authors/year,
- authorships/year,
- output per active author.

### 5. Produce concentration statistics

Calculate:

- productivity quantiles,
- top output shares,
- Lorenz curves,
- Gini coefficients.

### 6. Add observed-career-age and cohort analysis

Study:

- years since first observed publication,
- new-author entry,
- persistence,
- cohort productivity.

Only after these components are stable should the project expand substantially toward article length, references, interdisciplinarity, or AI.
