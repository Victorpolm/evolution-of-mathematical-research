# Historical papers per observed contributor

Computed from a frozen OpenAlex snapshot retrieved on 16 September 2026. These are descriptive measurements of recorded names and IDs in a selected arXiv-linked Mathematics population, not validated counts of people.

## First graph and estimand

For each period t, P_t counts retained papers and A_t counts distinct contributor keys on those exact papers. We compute P_t/A_t twice: raw-name keys without additional entity resolution, and OpenAlex's existing resolved author IDs. We do not create a new merging algorithm. Neither definition is a bound on people.

Each complete k-slot byline allocates 1/k to each slot, so total credit equals P_t and its mean over distinct keys is P_t/A_t. This is not the average full-count papers someone coauthored (I_t/A_t), and changes need not reflect individual productivity.

## Annual results

| Year | Linked papers | Retained P | Retention | Distinct names | OpenAlex IDs | P/names | P/IDs |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2010 | 12,615 | 10,724 | 85.01% | 15,051 | 12,741 | 0.7125 | 0.8417 |
| 2011 | 14,111 | 12,024 | 85.21% | 17,125 | 14,781 | 0.7021 | 0.8135 |
| 2012 | 15,611 | 13,159 | 84.29% | 19,079 | 16,364 | 0.6897 | 0.8041 |
| 2013 | 17,049 | 14,493 | 85.01% | 21,338 | 18,346 | 0.6792 | 0.7900 |
| 2014 | 18,170 | 15,392 | 84.71% | 23,320 | 19,898 | 0.6600 | 0.7735 |
| 2015 | 19,565 | 16,507 | 84.37% | 25,292 | 21,575 | 0.6527 | 0.7651 |
| 2016 | 20,352 | 17,224 | 84.63% | 26,922 | 23,104 | 0.6398 | 0.7455 |
| 2017 | 21,632 | 18,301 | 84.60% | 28,893 | 24,943 | 0.6334 | 0.7337 |
| 2018 | 22,714 | 18,983 | 83.57% | 30,446 | 26,394 | 0.6235 | 0.7192 |
| 2019 | 23,681 | 20,305 | 85.74% | 33,158 | 28,819 | 0.6124 | 0.7046 |
| 2020 | 26,164 | 23,462 | 89.67% | 39,162 | 34,406 | 0.5991 | 0.6819 |
| 2021 | 24,798 | 23,620 | 95.25% | 38,959 | 34,979 | 0.6063 | 0.6753 |
| 2022 | 25,272 | 24,459 | 96.78% | 37,586 | 36,705 | 0.6507 | 0.6664 |
| 2023 | 26,257 | 25,482 | 97.05% | 39,125 | 38,592 | 0.6513 | 0.6603 |
| 2024 | 25,390 | 24,157 | 95.14% | 41,471 | 40,763 | 0.5825 | 0.5926 |
| 2025 | 25,577 | 21,719 | 84.92% | 38,019 | 37,291 | 0.5713 | 0.5824 |

## Work-to-paper reconciliation

| Acquisition / linkage stage | Works or papers |
|---|---:|
| Unique acquired works | 413,438 |
| Outside 2010–2025 arXiv ID dates | 34,428 |
| No unique modern arXiv ID | 289 |
| Multiple arXiv IDs on one work | 463 |
| Works in ambiguous multiple-work/arXiv groups | 39,300 |
| Uniquely linked target-window papers | 338,958 |
| Paired papers after byline checks | 300,011 |

The date filter is distinct from failed linkage and from byline exclusions. The JSON breaks outside-window records down by arXiv ID year and all stages down by OpenAlex publication year.

| Year | Mapped arXiv paper IDs | Ambiguous version-link groups | Paired / mapped paper IDs |
|---|---:|---:|---:|
| 2010 | 13,628 | 1,013 | 78.69% |
| 2011 | 15,268 | 1,157 | 78.75% |
| 2012 | 16,888 | 1,277 | 77.92% |
| 2013 | 18,489 | 1,440 | 78.39% |
| 2014 | 19,835 | 1,665 | 77.60% |
| 2015 | 21,429 | 1,864 | 77.03% |
| 2016 | 22,252 | 1,900 | 77.40% |
| 2017 | 23,537 | 1,905 | 77.75% |
| 2018 | 24,736 | 2,022 | 76.74% |
| 2019 | 25,736 | 2,055 | 78.90% |
| 2020 | 28,198 | 2,034 | 83.20% |
| 2021 | 26,024 | 1,226 | 90.76% |
| 2022 | 25,356 | 84 | 96.46% |
| 2023 | 26,265 | 8 | 97.02% |
| 2024 | 25,390 | 0 | 95.14% |
| 2025 | 25,577 | 0 | 84.92% |

Mapped paper IDs count distinct in-window arXiv IDs on works with one parsable modern ID, before excluding IDs linked to multiple OpenAlex works. The byline retention denominator in the first table excludes those ambiguous groups. Neither retention percentage measures coverage of all arXiv mathematics.

## What the records show

- 2010–2025: P/A using raw names changes from 0.7125 to 0.5713 (-19.82%).
- 2010–2025: P/A using OpenAlex IDs changes from 0.8417 to 0.5824 (-30.80%).
- Retained papers change +102.53%; observed ID counts +192.69%; raw-name counts +152.60%. Thus contributor-key counts grow faster than retained papers under both definitions.
- Mean returned team size increases from 1.793 to 2.220 (+23.83%). The collaboration identity P/A = (I/A)/(I/P) separates this accounting term from full-count coauthored-paper participation.
- Coauthored-paper incidences per raw name, I/A: 1.278 to 1.268 (-0.72%). This is a different measure from fractional P/A, still subject to identity and coverage limitations.
- Coauthored-paper incidences per OpenAlex ID, I/A: 1.509 to 1.293 (-14.32%). This is a different measure from fractional P/A, still subject to identity and coverage limitations.
- Retention ranges from 83.57% to 97.05%. These changes in selection must accompany the ratios; dividing by authors does not correct them.

The agreement or disagreement between the two identity definitions is a sensitivity diagnostic. Shared selection, homonyms, spelling variants and split/merged IDs can affect both series. No real-person trend or causal effect of AI is established.

## Coverage and partial bylines

The JSON also reports annual raw-name and identified-ID counts before missing-ID paper exclusions, retaining all otherwise usable bylines. Missing slots keep 1/k unallocated credit; unusable bylines keep one whole paper equivalent. Allocated credit + missing-ID credit + unusable-byline credit equals all linked papers. Allocated credit per identified ID is reported separately from P/A. This broader sensitivity does not recover missing people or correct selection.

| Year | Usable papers / names | Usable papers / observed IDs | Allocated credit / ID | Unallocated / linked credit |
|---|---:|---:|---:|---:|
| 2010 | 0.7008 | 0.9768 | 0.8388 | 14.18% |
| 2011 | 0.6951 | 0.9446 | 0.8124 | 14.02% |
| 2012 | 0.6871 | 0.9394 | 0.8021 | 14.67% |
| 2013 | 0.6746 | 0.9169 | 0.7876 | 14.13% |
| 2014 | 0.6616 | 0.8995 | 0.7715 | 14.26% |
| 2015 | 0.6556 | 0.8902 | 0.7628 | 14.36% |
| 2016 | 0.6447 | 0.8668 | 0.7434 | 14.27% |
| 2017 | 0.6382 | 0.8530 | 0.7322 | 14.20% |
| 2018 | 0.6277 | 0.8444 | 0.7168 | 15.14% |
| 2019 | 0.6131 | 0.8059 | 0.7021 | 12.89% |
| 2020 | 0.5926 | 0.7418 | 0.6761 | 8.89% |
| 2021 | 0.5977 | 0.6959 | 0.6722 | 3.45% |
| 2022 | 0.6431 | 0.6718 | 0.6607 | 1.72% |
| 2023 | 0.6436 | 0.6641 | 0.6546 | 1.47% |
| 2024 | 0.5711 | 0.5963 | 0.5825 | 2.39% |
| 2025 | 0.5683 | 0.6354 | 0.5672 | 10.82% |

Usable papers / observed IDs counts all usable papers in the numerator, including those with unidentified slots. It is not mean fractional credit per observed ID. The allocated-credit column retains that distinction.

## Acquisition and analysis rules

- 413,438 unique OpenAlex works acquired; 338,958 uniquely linked target-window papers.
- Query: indexed_in:arxiv, primary_topic.field.id:26, publication years 2010–2026; 204 monthly partitions, 100 results/page, selected fields, at most 10 requests/second. All partitions fit within the 10,000-result basic-paging limit; each complete partition uses one paging strategy. Completed cursor partitions were retained; mixed partitions were reconciled by re-fetching their cursor prefix using numbered pages. Unique work counts were required to match each partition total. Credentials stayed in memory; only the free daily allowance was used.
- Analysis dates: arXiv ID months January 2010–December 2025, a proxy for initial submission month. OpenAlex publication dates can refer to later journal versions. The query catches only versions with publication years 2010–2026; it is not a census of all arXiv mathematics and does not establish primary arXiv category membership.
- Require exactly one modern arXiv ID per work; exclude all works in ambiguous multiple-work/one-arXiv groups. Count an arXiv paper once, irrespective of version.
- Paired papers require nonempty complete names and usable IDs, no repeated ID within a byline, no group-name flag, no truncation flag, and fewer than 100 slots. The returned byline is not independently validated as the original arXiv byline.
- Name normalization: nfc-whitespace-v1; case, initials, accents, punctuation preserved. Equal strings are counted together; this does not establish that they represent one person.
- Calendar years and rolling 12-month windows recompute contributor unions; they do not sum monthly distinct counts. No smoothing or imputation is applied. All 16 years are shown; a five-year lookback is relevant to future entry analyses, not required to define annual active-key counts.
- Every page hash, scope filter and partition count was checked before analysis. API retrieval is a bounded interval, not a transactional database snapshot. Created/update dates are retained, but one extraction cannot reconstruct historical byline completeness at equal elapsed time since indexing.
- Exact frozen-record counts have no sampling interval here. Identity error and selective missingness need external validation; a bootstrap would not resolve them.

## Mathematics and prior work

P = A × (I/A) / (I/P); Δlog P = Δlog A + Δlog(P/A). For linked papers L and retention c, P = Lc. Both decompositions are checked numerically and saved for every adjacent year. These identities describe accounting, not mechanisms. Mean team size and annual subfield results are available in the JSON.

The revised method and its discussion of Hulek & Teschke (2023), Grossman (2005), Fanelli & Larivière (2016), and author-disambiguation studies remain the foundation. See analysis/STATISTICAL_RESEARCH_PLAN.md in the repository, relative to ArxivObservatory. This run implements the narrower papers/contributors question; entry, concentration and AI effects need their own validation and design.

## Reproduce offline

```bash
cd ArxivObservatory
python -m analysis.historical_participation --snapshot /path/to/openalex-historical-20260916 --output /path/to/results
python tests/run_participation_checks.py
```

The raw projected cache is supplied separately as a metadata snapshot, not committed to GitHub. acquisition_manifest.json pins all page hashes. The acquisition helper is included in that snapshot; contributed analysis remains offline.
