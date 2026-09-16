# Contributor populations and the most prolific decile

Computed offline from the same frozen OpenAlex metadata and exactly the same paired papers as the historical participation analysis. All outputs describe observed keys, not validated people. No additional API requests or identity-merging algorithm.

## Why papers per contributor can be less than one

One paper with three distinct contributors gives P/A = 1/3, although each contributor coauthored one paper. P/A is mean fractional paper credit, not mean coauthored papers.

Let S_p contain all k_p returned author slots of retained paper p, and g_m(s) map a slot to a raw-name key or an OpenAlex author ID. Define

$$c^{(m)}_{it}=\sum_{p\in t}\sum_{s\in S_p}\frac{\mathbf{1}\{g_m(s)=i\}}{k_p},\qquad f^{(m)}_{it}=\sum_{p\in t}\mathbf{1}\{i\in g_m(S_p)\}.$$

Then sum_i c_it = P_t. Full coauthored-paper counts f_it count each key once per paper; their sum J_t can exceed P_t. For names, J_t can be less than byline-slot count I_t when several slots have the same string. Earlier archived slot-based statistics remain unchanged.

## Three denominators / time horizons

- P_t/A_t: papers in a year or window divided by distinct keys active on those same papers.
- P_t/A_all: the same papers divided by the union of keys observed anywhere in 2010–2025. Keys inactive in t contribute zero. This is a fixed retrospective pool, not the active research workforce.
- P_all/A_all: all retained papers over 2010–2025 divided by that union. This is a 16-year total per key, not an annual rate.

A_all is computed independently for each identity definition and is never a sum of annual counts. Changing the study endpoints changes A_all. With a fixed denominator, the P_t/A_all trend has exactly the same percentage changes as paper counts; it cannot separate growth in participation from output.

Retained papers in the full study: **300,011**.

| Identity definition | Full-study distinct keys | P_all/A_all | Mean coauthored papers over whole study |
|---|---:|---:|---:|
| Distinct raw names | 231,929 | 1.2935 | 2.6870 |
| OpenAlex author IDs | 178,730 | 1.6786 | 3.4868 |

## Annual denominator comparison

| Year | Papers | Active names | Active IDs | P/active names | P/active IDs | P/all names | P/all IDs |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2010 | 10,724 | 15,051 | 12,741 | 0.7125 | 0.8417 | 0.0462 | 0.0600 |
| 2011 | 12,024 | 17,125 | 14,781 | 0.7021 | 0.8135 | 0.0518 | 0.0673 |
| 2012 | 13,159 | 19,079 | 16,364 | 0.6897 | 0.8041 | 0.0567 | 0.0736 |
| 2013 | 14,493 | 21,338 | 18,346 | 0.6792 | 0.7900 | 0.0625 | 0.0811 |
| 2014 | 15,392 | 23,320 | 19,898 | 0.6600 | 0.7735 | 0.0664 | 0.0861 |
| 2015 | 16,507 | 25,292 | 21,575 | 0.6527 | 0.7651 | 0.0712 | 0.0924 |
| 2016 | 17,224 | 26,922 | 23,104 | 0.6398 | 0.7455 | 0.0743 | 0.0964 |
| 2017 | 18,301 | 28,893 | 24,943 | 0.6334 | 0.7337 | 0.0789 | 0.1024 |
| 2018 | 18,983 | 30,446 | 26,394 | 0.6235 | 0.7192 | 0.0818 | 0.1062 |
| 2019 | 20,305 | 33,158 | 28,819 | 0.6124 | 0.7046 | 0.0875 | 0.1136 |
| 2020 | 23,462 | 39,162 | 34,406 | 0.5991 | 0.6819 | 0.1012 | 0.1313 |
| 2021 | 23,620 | 38,959 | 34,979 | 0.6063 | 0.6753 | 0.1018 | 0.1322 |
| 2022 | 24,459 | 37,586 | 36,705 | 0.6507 | 0.6664 | 0.1055 | 0.1368 |
| 2023 | 25,482 | 39,125 | 38,592 | 0.6513 | 0.6603 | 0.1099 | 0.1426 |
| 2024 | 24,157 | 41,471 | 40,763 | 0.5825 | 0.5926 | 0.1042 | 0.1352 |
| 2025 | 21,719 | 38,019 | 37,291 | 0.5713 | 0.5824 | 0.0936 | 0.1215 |

## Most prolific decile

Rank active keys separately for each identity definition, time window and measure. Fractional credit is the primary concentration measure; coauthored-paper counts are a sensitivity view. The whole-study decile is ranked on cumulative 2010–2025 output. Annual/window deciles are re-ranked each period, not a fixed set of contributors followed through time.

Use an exact top-decile mass of 0.1 A. At the cutoff, allocate the remaining membership weight proportionally across all tied keys; there is no arbitrary name/ID tie-break. Fractional scores rounded to 12 decimal places define ties only; unrounded values determine output. The JSON records the threshold, strictly-above count, tied count and common boundary weight.

$$S_{10,t}^{(m)}=\frac{\sum_i w_{it}x_{it}}{\sum_i x_{it}},\qquad \sum_i w_{it}=0.1A_t,\qquad \frac{\bar{x}_{\mathrm{top10},t}}{\bar{x}_{\mathrm{other90},t}}=\frac{9S_{10,t}}{1-S_{10,t}}.$$

For fractional output, the share denominator is P. For full counts, it is J, the sum of key–paper participations, not a count of distinct papers. A single coauthored paper can contribute to several keys. Equal output for all keys would give a 10% share and a mean ratio of 1.

### Annual top-decile shares

| Year | Fractional: names | Fractional: IDs | Coauthored: names | Coauthored: IDs |
|---|---:|---:|---:|---:|
| 2010 | 27.76% | 29.99% | 22.76% | 26.17% |
| 2011 | 28.08% | 29.93% | 22.89% | 26.07% |
| 2012 | 27.63% | 29.80% | 23.16% | 26.61% |
| 2013 | 27.78% | 29.99% | 23.05% | 26.50% |
| 2014 | 27.26% | 29.78% | 22.63% | 26.21% |
| 2015 | 27.06% | 29.63% | 22.41% | 25.97% |
| 2016 | 26.94% | 29.56% | 22.37% | 25.92% |
| 2017 | 27.09% | 29.82% | 22.53% | 25.98% |
| 2018 | 26.95% | 29.92% | 22.62% | 26.08% |
| 2019 | 27.06% | 29.93% | 22.67% | 26.11% |
| 2020 | 28.48% | 31.40% | 23.31% | 26.56% |
| 2021 | 28.87% | 31.00% | 23.88% | 26.62% |
| 2022 | 30.33% | 30.28% | 25.83% | 26.29% |
| 2023 | 30.36% | 30.10% | 26.00% | 26.19% |
| 2024 | 28.94% | 28.74% | 23.60% | 24.01% |
| 2025 | 27.26% | 27.35% | 22.49% | 22.91% |

### Full-study cumulative ranking

| Identity | Ranking measure | Top 10% share | Top 10% mean | Other 90% mean | Mean ratio |
|---|---|---:|---:|---:|---:|
| Names | fractional | 46.56% | 6.0229 | 0.7681 | 7.84 |
| Names | coauthored | 43.28% | 11.6300 | 1.6934 | 6.87 |
| IDs | fractional | 52.02% | 8.7321 | 0.8949 | 9.76 |
| IDs | coauthored | 49.16% | 17.1401 | 1.9698 | 8.70 |

## Descriptive findings and limits

- Under distinct names, the annual top-decile fractional share changes from 27.76% in 2010 to 27.26% in 2025 (-0.51 percentage points). The cumulative whole-study share is 46.56%.
- Under OpenAlex IDs, the annual top-decile fractional share changes from 29.99% in 2010 to 27.35% in 2025 (-2.64 percentage points). The cumulative whole-study share is 52.02%.

The whole-study and annual concentration measures have different exposure lengths and membership rules. Their levels should not be read as a change over time. A top-decile share describes concentration of recorded output; it does not measure research quality, contribution effort or a causal AI effect. Changing retention, OpenAlex coverage, field composition, team size and identity splits/merges can affect comparisons. The two identity definitions are sensitivity analyses, not lower/upper bounds on people. Current metadata can differ from original arXiv bylines.

## Provenance and reproduction

Snapshot manifest SHA-256: `41a458965e5a494f50a31450dea733c86310a288810f0dd02a791ce1ffddb1d3`.

The analysis verifies every compressed metadata page and reproduces P, A and slot counts for all 16 annual, 192 monthly and 181 rolling windows of the historical baseline. Metadata was retrieved on 16 September 2026; analysis dates come from arXiv ID months. Source scope: OpenAlex works indexed in arXiv, primary field Mathematics (26), publication years 2010–2026, with arXiv ID dates 2010–2025. Ambiguous work-to-paper links and incomplete paired bylines remain excluded exactly as documented in the historical analysis.

```sh
python -m analysis.contributor_populations --snapshot /path/to/frozen-cache \
  --baseline reports/historical_participation_20260916/historical_participation.json \
  --out reports/contributor_populations_20260916
```
