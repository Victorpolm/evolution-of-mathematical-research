# Statistical research plan: democratization and changing structure of mathematics

## 1. Research motivation

The broad project asks how mathematical research is changing during the rise
of generative AI. The initial idea has two parts.

### Axis A — Production and democratization

1. Is the growth in arXiv mathematics caused by more people participating, or
   by the same people publishing more?
2. What is the academic-age distribution of active authors?
3. Is publication output becoming more or less concentrated among the most
   productive authors?
4. Are papers becoming shorter, so that more papers represent a fragmentation
   of roughly the same amount of work?

### Axis B — Collaboration and knowledge structure

1. How are collaboration rates and team sizes changing?
2. Are authors publishing across a wider range of mathematical fields?
3. Are new collaborations bridging previously separated areas of mathematics?
4. Is AI associated with stronger links between researchers and fields, or
   with weaker human collaboration?

Paper length, reference counts, field breadth, and collaboration are **not
direct measures of quality**. They describe mathematical practice and
knowledge structure. A separate quality study would require a defensible
outcome such as expert evaluation, later influence, or correction rates.

The first study should focus on Axis A because its estimands are clearer and
its data requirements are manageable.

## 2. Primary question

> Is growth in arXiv mathematics driven by broader participation, or by
> increased and increasingly concentrated output among already-active authors?

Evidence consistent with democratization would combine several observations:

- active authors grow at least as fast as papers;
- the share of new or early-career authors rises;
- output concentration falls or remains stable;
- participation broadens across subfields and, when data permit, institutions
  and countries;
- entry is persistent rather than consisting only of one-off submissions.

No single indicator is sufficient.

## 3. Unit of observation and study period

The working input is a metadata-only table with one row per paper-author pair.
At minimum it needs:

- stable paper and arXiv identifiers;
- arXiv submission year and preferably month;
- primary arXiv mathematics category;
- stable OpenAlex author identifier;
- number of authors on the paper;
- author first-observed publication and arXiv-mathematics years;
- OpenAlex match and authorship-completeness diagnostics.

The preferred acquisition window is 2010–2025, with headline analysis
beginning in 2015. The earlier years provide lookback for entry and age
calculations. Incomplete 2026 data should not be compared with complete years.

OpenAlex's publication date may describe a journal version rather than the
arXiv upload. Submission time should therefore come from the arXiv record or
identifier whenever possible.

## 4. Author identity

Raw author-name strings are not reliable person identifiers. Spelling
variants, name changes, transliteration, initials, and homonyms would bias
active-author counts, entry, productivity, and concentration.

The primary analysis therefore uses OpenAlex author IDs and reports:

- paper matching rate;
- authorship-slot identification rate;
- share of papers with complete identified authorships;
- ambiguous and unmatched counts;
- OpenAlex truncation indicators.

Headline estimates should use complete identified authorships. Sensitivity
analyses should compare that frame with all usable matches. A blinded audit of
author disambiguation is required before publication.

## 5. Fractional authorship and publication growth

For paper \(p\) with \(k_p\) authors, author \(i\) receives \(1/k_p\)
fractional paper. Author \(i\)'s output in year \(t\) is

\[
y_{it}=\sum_{\substack{p\text{ in year }t\\i\in p}}\frac{1}{k_p}.
\]

Then total fractional output equals the number of papers:

\[
P_t=\sum_i y_{it}=A_t\overline{y}_t,
\]

where \(A_t\) is the number of active authors and
\(\overline{y}_t=P_t/A_t\). This decomposes publication growth into:

- **extensive margin:** change in the number of active authors;
- **intensive margin:** change in mean fractional output per active author.

For two dates, log growth decomposes as

\[
\Delta\log P=\Delta\log A+\Delta\log\overline{y}.
\]

Because fractional output is affected by team size, the analysis must also
report full-count papers per author and explicit collaboration measures. The
decomposition is descriptive, not causal.

## 6. Concentration of publication output

The phrase "first decile of publishers" should be operationalized as the
**top productivity decile**, meaning the most productive 10% of active
authors. "First decile" can otherwise mean the bottom 10%.

Let \(T_{q,t}\) contain the top \(\lceil qA_t\rceil\) authors ranked by
fractional output in year \(t\). The top-\(q\) share is

\[
C_{q,t}=\frac{\sum_{i\in T_{q,t}}y_{it}}{\sum_i y_{it}}.
\]

Report \(q=0.01,0.05,0.10\). The top 10% alone can conceal increasing
concentration among the top 1%.

Also calculate:

- Gini coefficient of annual author output;
- Lorenz curves for selected benchmark years;
- median and upper quantiles of author output;
- fraction of active authors with only one paper;
- optional Herfindahl concentration as a sensitivity measure.

Ties at a cutoff require a predeclared rule. Fractional allocation of a tied
group at the boundary avoids arbitrary author-ID ordering. Compute
concentration using both fractional and full paper counts.

## 7. Entry and observed academic age

Keep two concepts separate:

1. **Global observed academic age:**
   \(t-\text{first OpenAlex work year}_i\).
2. **Observed arXiv-mathematics age:**
   \(t-\text{first observed arXiv-math year}_i\).

The second measures tenure in the observed arXiv-mathematics system, not a
person's true career age. Both are left-censored without a long lookback.

Primary yearly statistics:

- median observed age and the 25th/75th percentiles;
- shares with observed age 0–1, 0–3, and 0–5 years;
- fractional share of output produced by these groups;
- persistence of entrants after two, three, and five years.

A five-year minimum lookback is a reasonable initial gate. Authors first seen
at the acquisition boundary must not automatically be called new researchers.

## 8. Collaboration measures

The first study should include easy collaboration indicators because they
help interpret fractional productivity:

- mean and median authors per paper;
- single-author paper share;
- shares with 2, 3–5, and 6+ authors;
- total authorship slots;
- full-count versus fractional-count productivity.

A later network study can add distinct collaborators per author, new coauthor
pairs, collaboration persistence, cross-field coauthor edges, network
modularity, and assortativity by mathematical field.

## 9. Mathematical subfields and standardization

Produce all main statistics pooled across mathematics, separately by primary
arXiv category, and standardized to a fixed category distribution. Otherwise,
a growing subfield with different authorship norms can create the appearance
of democratization or concentration across mathematics as a whole.

For fixed field weights \(w_f\), a direct standardized statistic is

\[
S_t^{std}=\sum_f w_fS_{ft}.
\]

Weights could use the 2015 paper shares or pooled 2015–2019 shares. Small
categories should be grouped or suppressed using a predeclared threshold.

## 10. Graph plan

### Figure 1 — Indexed growth decomposition

Set 2015 to 100 and plot papers, active authors, fractional papers per active
author, and optionally full-count papers per author. This is the main
democratization figure.

### Figure 2 — Entry and observed age

Plot median observed arXiv-math age with an interquartile band, plus the share
with observed age at most three years.

### Figure 3 — Concentration

Plot annual top 1%, 5%, and 10% output shares and the Gini coefficient. Add
Lorenz curves for 2015, 2020, 2023, and 2025.

### Figure 4 — Collaboration

Plot the single-author share, team size, and shares with 2, 3–5, and 6+
authors.

### Figure 5 — Field heterogeneity

Use small multiples for major categories instead of one crowded panel.

Every graph must state whether author output is fractional or full counted and
display retained/matched coverage.

## 11. Statistical uncertainty and robustness

The data are close to a census of the selected frame, so conventional
sampling p-values are not the main uncertainty. The important uncertainties
are measurement and cohort construction:

- author disambiguation;
- unmatched or incomplete authorships;
- incomplete recent-year coverage;
- left-censored first-publication dates;
- arXiv/OpenAlex date differences;
- changing category composition;
- full versus fractional counting;
- the entry threshold and field-classification errors.

Required sensitivity analyses:

1. complete high-confidence authorships versus all usable matches;
2. fractional versus full publication counts;
3. entry thresholds of 1, 3, and 5 years;
4. lookback periods of 3, 5, and 10 years where possible;
5. pooled versus field-standardized results;
6. exclusion of incomplete years;
7. arXiv-category membership versus OpenAlex Mathematics classification.

Monthly estimates should use a 12-month rolling window. Annual headline
estimates should use complete calendar years.

## 12. Interpretation framework

| Pattern | Interpretation |
|---|---|
| Active authors grow as fast as or faster than papers | Broader participation |
| New-author share and entrant persistence increase | More durable entry |
| Median observed age falls | Participation shifts toward newer authors |
| Top 1/5/10% shares and Gini fall | Output becomes less concentrated |
| Papers rise, authors lag, and concentration rises | Expansion is concentrated |
| Team sizes rise while fractional output per author falls | Collaboration explains part of paper growth |
| Pooled change disappears after field standardization | Field composition drove the aggregate trend |

These patterns describe the measured system; they do not prove that AI caused
the change.

## 13. Relation to AI

ArxivObservatory identifies **author-disclosed AI use**, not all AI use.
Disclosure depends on both usage and willingness to disclose.

An initial comparison can examine whether disclosed-AI papers differ in team
size, author age, new-author participation, prior productivity, field breadth,
and new or cross-field collaborations. Match or stratify by month, category,
team size, and career stage. Report associations. A simple before/after-2022
comparison does not identify a causal effect.

First establish the historical trend in mathematics independently of AI
labels. The disclosure comparison is a second stage.

## 14. Paper length, references, and quality

Source-archive byte size is not a reliable paper-length measure. Better
candidates are PDF page count, extracted word/token count, bibliography
length, theorem/proposition count if validated, and appendix length.

Reference statistics should include references per paper and per page,
standardized by field and year. Neither longer papers nor more references
imply higher quality. These belong under research practice and knowledge
structure unless separately validated as quality indicators.

## 15. Priority order

1. Publication-growth decomposition and top 1/5/10% concentration.
2. Entry, observed academic age, and entrant persistence.
3. Team size and single-author trends.
4. Field-standardized versions of the first three analyses.
5. Cross-field collaboration network.
6. Paper length and reference structure.
7. A separately designed quality study.
8. AI-disclosure association and any later causal design.

The first four items form the initial democratization paper.

## 16. Current implementation and pilot

The imported snapshot contains:

- `analysis/democratization.py`;
- `analysis/DEMOCRATIZATION.md`;
- `tests/test_democratization.py`.

It produces aggregate annual CSV output, a provenance manifest, and an SVG
overview. It uses the Python standard library and runs offline on fixtures.

The bounded 2023–2025 OpenAlex pilot was a technical validation, not a
scientific result. It queried 77,949 candidate works, retained 69,166 usable
arXiv-ID-dated mathematics works, created 155,781 identified paper-author
links, and found 8,042 authorship slots without an OpenAlex author ID. The
missing identities and short window make it unsuitable for headline claims.

The full historical analysis requires the longer acquisition window and a
documented coverage audit.

## 17. Planned aggregate output

The annual output should contain:

```text
year
primary_category
counting_method
number_of_papers
number_of_active_authors
fractional_output_per_author
full_count_output_per_author
new_author_share_1y
new_author_share_3y
new_author_share_5y
median_observed_math_age
top_1_percent_output_share
top_5_percent_output_share
top_10_percent_output_share
gini_author_output
single_author_share
median_team_size
mean_team_size
complete_authorship_paper_share
openalex_author_id_coverage
```

No per-author rankings or paper-level labels should be committed.

## 18. Repository and upstream workflow

The authoritative upstream remains `schmittj/ArxivObservatory`. Follow its
`CONTRIBUTING.md` and `AGENTS.md`: never commit paper content, databases,
credentials, or per-paper labels; do not modify `pipeline/` or `TAXONOMY.md`;
add analysis as new modules with fixture-based tests; and submit changes by
Pull Request once suitable upstream access is available.
