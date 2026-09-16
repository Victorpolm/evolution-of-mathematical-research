# Extending the observation window

This note preserves the 15 September 2026 availability check and design.

**16 September update:** the historical metadata acquisition and descriptive 2010–2025 P/A calculation are now implemented in draft PR #2. The dashboard opens with papers per observed contributor under both identity definitions. Calendar-year counts start in 2010; five-year lookback concerns later entry/returner measures. The main graph is accompanied by component counts, annual coverage and partial-byline sensitivity accounting. Person-level validation remains outstanding. See `reports/historical_participation_20260916/HISTORICAL_PARTICIPATION.md` in the implementation PR. The paragraphs below describe the earlier planning checkpoint.

## Why the current comparison is 2024–2025

The existing repository paper-ID manifest covers August 2023–July 2026 after excluding its incomplete August 2026. Thus 2024 and 2025 are its only full calendar years. The subsequent OpenAlex comparison was scoped to those two arXiv upload years as a bounded technical pilot. Its acquisition queried OpenAlex publication years 2024–2026, including some later journal versions, before selecting arXiv IDs dated 2024–2025.

That pilot boundary is a practical scope decision, not a scientific argument for starting the study in 2024, and not a limit on OpenAlex's historical availability. Two adjacent years cannot establish a long-term trend or an earlier baseline for an AI-related question. Their changing author-data completeness also prevents a straightforward population interpretation.

The separate 2023–2025 pilot displayed in Project overview comes from previously reported aggregate counts. Its underlying records are not available in this workspace. It must not be combined with either the repository manifest or the September 15 OpenAlex audit.

## The historical target

The existing protocol proposes collecting metadata from **2010 onward**, with the main historical comparison beginning in **2015** and ending at the latest validated complete year. This retains at least five years of prior observations for identifying first-observed and returning author keys.

Annual paper and active-author counts do not themselves require five years of lookback: they can be shown from 2010 if coverage permits. Entry, returner and persistence measures require additional history and, for persistence, comparable follow-up. Neither a five-year lookback nor a current author ID establishes a person's true career start. The start and end dates remain conditional on documented coverage, not on a convenient historical breakpoint.

Use both distinct raw-name keys and existing OpenAlex-resolved author IDs, preserving the same eligibility and paper population for their direct comparison. Neither is a verified count of people; this project does not claim to outperform OpenAlex disambiguation.

## Availability check performed

One anonymous OpenAlex group-count query at **22:03 UTC on 15 September 2026** used:

`indexed_in:arxiv,primary_topic.field.id:26,publication_year:2010-2023`

grouped by OpenAlex `publication_year`. It returned **330,421 candidate works** across all 14 years. The exact response and rate-limit headers are preserved in `historical_preflight.json`.

These are **OpenAlex publication-year counts**, not arXiv upload-year counts, not the validated mathematics frame, and not contributors. No historical work-level records were downloaded in this check, and these aggregates have not been spliced into the current upload-based graphs. Some older arXiv IDs already found in the 2024–2026 publication-year query are a selected set of later publications; they do not supply a representative historical series.

At 100 records per page, separate yearly retrieval would need at least **3,311 list requests**, before retries, boundary checks or additional linkage work. The response reported **999 anonymous requests remaining**. Therefore the full backfill could not fit into that remaining allowance. These are allowances observed at the stated time, not a permanent claim about the account or API.

OpenAlex documents a free key with ten times the anonymous daily budget. Another route is staged collection within the free allowance, or an existing project metadata export containing historical paper IDs and authors. No paid account, key creation, scheduled job or historical harvest was started here. Source: [OpenAlex authentication and limits](https://help.openalex.org/api/authentication/).

## What must happen before earlier results appear

1. Obtain historical work-level metadata, retaining names, existing author IDs, complete returned bylines, arXiv identifiers, field labels and provenance. Prefer one frozen OpenAlex snapshot for all years; otherwise record the bounded acquisition interval and audit revision effects. Preserve the original pilot unchanged for comparison.
2. Reconstruct upload months from the arXiv IDs and handle journal/preprint version links consistently. OpenAlex publication dates are an acquisition tool, not interchangeable with upload dates. Reconcile coverage with an exact historical arXiv mathematics frame when available.
3. Measure matching, byline completeness, missing IDs, unallocated credit and field composition for each year. A longer series does not automatically resolve the current missingness problem.
4. Compute both identity approaches on the same paper sets, alongside the partial-ID accounting sensitivity. Deduplicate identities over whole annual, three-year and five-year windows; never sum annual distinct-author counts to obtain a multi-year count.
5. Publish comparable years with explicit coverage warnings. Keep observed first appearance separate from actual career entry, and descriptive historical changes separate from causal claims about AI.

## Graph presentation updated

Every displayed chart now has a visible title above it and a description below it. Each description states what is counted, the denominator where relevant, how the quantity was calculated, the time-window definition and the source. The compact line charts include labelled zero-based scales, dates, units and legends. Monthly views are the default; rolling views explicitly show that points represent overlapping 12-month windows.

The repository graphs extend back to August 2023 for paper counts only. Their missing contributor series remain labelled as unavailable. The OpenAlex audit still covers 2024–2025; earlier contributor results remain pending collection and validation.
