# Papers versus contributors: first descriptive analysis

Working focus requested on 2026-09-06. This module operationalizes existing
growth-decomposition plans; it does not settle the final corpus or activity
window. Important final choices should be recorded in the broader project's
decision log when settled.

## Question and definitions

Is growth in uploads accompanied by growth in the number of distinct authors?
For a period t, count distinct arXiv paper IDs P_t and distinct OpenAlex author
IDs A_t on **the same retained papers**. Contributors means coauthors, not
uploading accounts. Count each person once within the period, irrespective of
their number of papers. Author IDs remain an imperfect person proxy.

P_t / A_t is mean fractional paper output when complete authorships receive
1/k credit. It is not mean full-count publication participation. If I_t is
the number of authorships, then

    P_t = A_t × (I_t / A_t) / (I_t / P_t).

This separates active-author population, full-count output per author, and
mean team size. It is an accounting identity, not a causal decomposition.
Aggregate ratios cannot isolate within-person productivity changes from entry,
exit, or changing composition, and cannot identify an AI effect.

## Available data and empirical limit

The repository's `pipeline/aws/math_ids.txt`, at revision
`7d1063371ad2825ac3ad622974f6df129d1324f0`, contains 169,394 unique IDs and
no author identities. The monthly series uses ID month as a proxy for first
submission month; this can differ from the exact v1 timestamp near boundaries.
The ID list alone cannot distinguish math-primary from cross-listed papers.
These are counts in the repository manifest, not a validated census of all
arXiv mathematics and not the separate OpenAlex pilot frame.

Use August 2023–July 2026, excluding the partial August 2026 tail. This gives
168,027 IDs, matching the import reconciliation's target count. The two full
calendar years contain 52,081 IDs in 2024 and 55,751 in 2025 (+3,670; +7.05%).
The short series and unaudited external coverage limit interpretation.

Unique-contributor counts and P/A cannot be computed from this manifest.
The pilot's 155,781 paper-author links are repeated participation events,
not 155,781 distinct contributors. Do not combine pilot links with manifest
paper counts: the populations and time windows differ.

## Output and visualization

`analysis.papers_contributors` emits aggregate JSON and CSV for monthly,
trailing 12-month, and complete calendar-year windows. Each rolling author
count is a set union across its window, never a sum of monthly author counts.
There is no career-age lookback requirement for simple within-period counts.

The dashboard shows a paper sparkline and explicit unavailable states for
contributors and P/A. With matched data, compare papers and authors indexed
to 100 in the same first period, on one y scale; show P/A separately. Annotate
first/last values and total change, expose exact values, and keep monthly
fluctuations separate from overlapping 12-month windows. Do not bridge missing
observations. A paper-only series never implies contributor growth.

## Optional author matching and validation

Reuse the existing democratization CSV loader. Headline paper and contributor
counts use the same subset with known, complete, non-truncated authorships
and an identified-author count equal to the reported total. Report frame,
matched, and complete-paper counts/shares. Reject multiple OpenAlex work IDs
for one arXiv ID and conflicting ID/metadata dates. Every excluded loaded
paper has a counted reason. No author identities are emitted.

Rerun the period comparison with different corpus definitions, a blinded
identity audit, stable metadata coverage, and within-subfield comparisons
before interpreting growth in observed IDs as growth in researchers.

## Run offline

From `ArxivObservatory/`:

```bash
python3 -m analysis.papers_contributors \
  --manifest pipeline/aws/math_ids.txt \
  --start-month 2023-08 --end-month 2026-07 \
  --source-label 'Repository mathematics ID manifest' \
  --source-revision 7d1063371ad2825ac3ad622974f6df129d1324f0 \
  --source-blob-sha d419482b8f55f695916798894f517e40069b52e6 \
  --source-url https://github.com/Victorpolm/evolution-of-mathematical-research/blob/7d1063371ad2825ac3ad622974f6df129d1324f0/ArxivObservatory/pipeline/aws/math_ids.txt \
  --output-dir results/papers_contributors
```

Add `--authorships results/paper_authors.csv` for the matched analysis. Raw
metadata remain untracked under the existing contribution rules.
