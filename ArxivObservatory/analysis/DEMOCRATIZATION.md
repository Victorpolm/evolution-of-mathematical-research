# Democratization of arXiv mathematics — analysis protocol

## Question

Is growth in arXiv mathematics driven by broader participation or by higher
and more concentrated output among already-active authors?

This is a descriptive study of production, participation, and collaboration.
It does not identify an effect of AI and does not measure paper quality.

## Input boundary

`analysis.democratization` consumes an untracked metadata-only CSV with one
row per paper-author pair. Required columns are:

```text
work_id,arxiv_id,publication_year,author_id,primary_subfield,
authorships_total,authorships_missing_id
```

The year and optional month must be derived from the arXiv identifier. OpenAlex
`publication_date` can describe the journal version of record rather than the
arXiv submission. Raw records belong under gitignored `results/`; never commit
the paper-author file, personal names, paper text, snippets, or per-paper
labels.

OpenAlex source/field IDs used for acquisition:

- arXiv source: `S4306400194`
- Mathematics field: `26`

The Mathematics field is an OpenAlex topic classification, not the exact
arXiv `math.*` category frame. A final analysis must quantify coverage against
an owner-provided exact arXiv-math ID manifest.

## Estimands

For a paper with `k` authors, every author receives fractional output `1/k`.
This makes author output sum exactly to the number of papers. For each year and
scope, the analysis reports:

- papers and active OpenAlex author IDs;
- fractional papers per active author;
- share of authors first observed that year and with observed age 0–3;
- mean/median team size and solo/3+-author paper shares;
- top 1%, 5%, and 10% shares of fractional author output;
- Gini coefficient of fractional output;
- full-count concentration as a sensitivity analysis;
- OpenAlex reference-count summaries as bibliographic-practice diagnostics,
  not quality measures.

The top decile contains `ceil(0.10 * active authors)` authors, ranked anew
within each year and scope. A later persistence analysis should separately
track a fixed baseline elite cohort.

## Age limitation

The calculated age is **observed arXiv-math age**: years since an OpenAlex
author ID first appears in the supplied arXiv-math data. It is not global
academic age. Authors already active before the first input year are
left-censored. The CLI requires a five-year lookback by default and reports
the left-censored share, but this does not eliminate intermittent-publication
bias. A stronger extension needs complete historical works or an external
career-start field.

## Running offline

```bash
python3 -m analysis.democratization \
  --input results/democratization_openalex/paper_authors.csv \
  --output-dir results/democratization_openalex/aggregates \
  --analysis-start 2015 \
  --analysis-end 2025 \
  --minimum-lookback 5
```

The command creates aggregate-only `annual_metrics.csv`,
`democratization_overview.svg`, and `methodology.json`. Incomplete calendar
years should be excluded from headline comparisons.

## Validity and sensitivity requirements

Before interpretation:

1. compare the OpenAlex-derived arXiv IDs with the exact owner-provided frame;
2. report match, omission, duplicate, and 100-author-truncation rates;
3. inspect OpenAlex author-disambiguation errors on a blinded sample;
4. require complete author-ID coverage for headline concentration metrics and
   report both the retained-paper share and missing-authorship-slot share;
5. repeat concentration with fractional and full counting;
6. standardize results to a fixed subfield composition;
7. vary the new-author threshold and historical lookback;
8. distinguish annual top-decile concentration from persistence of a fixed
   top-author cohort;
9. label all AI-era comparisons as descriptive unless an identification
   strategy is separately justified.

OpenAlex API mechanics and data definitions:

- <https://help.openalex.org/api/>
- <https://help.openalex.org/api/authentication/>
- <https://help.openalex.org/api/paging/>
- <https://help.openalex.org/data/authors/>
- <https://help.openalex.org/data/works/attributes/>
