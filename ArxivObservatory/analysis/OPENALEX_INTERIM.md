# Interim OpenAlex-only comparison

**Historical extension, 16 September 2026:** the main dashboard now starts with the 2010–2025 P/A comparison. See `reports/historical_participation_20260916/HISTORICAL_PARTICIPATION.md` and `analysis/historical_participation.py`. This document preserves the earlier two-year run and its 15 September coverage audit. The expanded focused runner includes five historical fixtures (27 checks total).

**Current status after the second September 15 reply:** population participation
and concentration interpretations are on hold. The main dashboard presents the
retention audit; the earlier comparison remains archived for reproducibility.
Use `analysis/retention_audit.py` for partial-ID accounting and the new audit,
then `analysis/render_retention_audit.py` for its report and figure. Details and
commands are in `reports/openalex_interim_20260915/RETENTION_AUDIT.md`.

The user requested an OpenAlex-only run on 15 September 2026 while the existing
Observatory database and old pilot CSV remain unavailable. This is a bounded
substitute for the paired identity comparison, not completion of every stage
in the revised historical protocol (draft PR #3).

The two definitions are distinct OpenAlex author IDs and distinct source
`raw_author_name` values. No additional author resolver is introduced.
Normalization is Unicode NFC plus whitespace cleanup, retaining case, accents,
punctuation and initials. Both definitions use identical OpenAlex authorship
slots and identical eligible papers. OpenAlex has already consolidated work
versions; its source byline is not guaranteed to be the arXiv v1 byline.

The acquired population uses OpenAlex's core corpus, `indexed_in:arxiv`,
`primary_topic.field.id:26`, and OpenAlex publication years 2024–2026. It is
partitioned by publication month for complete pagination. Analysis dates come
from arXiv identifiers, January 2024–December 2025. The publication-year query
boundary is a selection limitation, not a substitute upload-date definition.
The 2026 extension captures some later journal versions. Broader or earlier
coverage requires a separately declared extension.

`openalex_names.py` is offline and accepts the frozen projected metadata
snapshot. It verifies page hashes, completed acquisition and every partition's
record count, then checks unique work-to-arXiv mapping. It excludes incomplete
name/ID bylines, provider placeholders, repeated IDs on one byline, possible
collective authors and truncated/100-plus bylines from both definitions.
Repeated name keys retain all byline slots and their fractional credits.

Outputs include monthly, annual and rolling-12-month counts; team-size and
activity distributions; fractional and full-count concentration; within-field
comparisons; and exact descriptive transition and log-growth identities.
The independent identity audit required for stronger interpretation has not
been done. The report labels transition and concentration outputs exploratory.

The existing project manifest supplies a separately reported intersection and
coverage comparison. Its paper totals are never paired with another
population's author denominator. Three- and five-year activity trends, true
career entry, external zbMATH replication, causal attribution and validation
of real-person counts are outside this run.

## Reproduction

Extract the supplied metadata snapshot and run from `ArxivObservatory/`:

    python -m analysis.openalex_names \
      --snapshot /absolute/path/to/snapshot \
      --math-manifest /absolute/path/to/math_ids.txt \
      --output /absolute/path/to/results

    python -m analysis.render_openalex_comparison \
      --input /absolute/path/to/results/openalex_comparison.json \
      --output /absolute/path/to/results

    python -m analysis.retention_audit \
      --snapshot /absolute/path/to/snapshot \
      --output /absolute/path/to/results

    python -m analysis.render_retention_audit \
      --input /absolute/path/to/results/retention_audit.json \
      --output /absolute/path/to/results

Calculation uses only the Python standard library. Figure rendering adds
matplotlib. Raw metadata and the user-authorized free-API session helper remain
outside this repository; contributed analysis code performs no network calls.
Committed outputs contain only aggregates. No paper text was fetched from
arXiv, no paid API account was used, and pipeline/taxonomy files are unchanged.

The seven comparison fixtures, six retention-audit fixtures, and nine existing
paper-count/export tests provide 22 focused offline checks. Run them with:

    python -m pytest tests/test_openalex_names.py tests/test_retention_audit.py tests/test_papers_contributors.py tests/test_export_metadata.py

For an environment without pytest, the same checks run with the standard library:

    python tests/run_participation_checks.py

No full upstream-suite result is claimed. Calculation has no third-party
dependency; the optional figure renderers require matplotlib. The frozen
metadata snapshot is a separate required input: the committed acquisition
manifest and hashes do not replace access to its exact bytes.

See `reports/openalex_interim_20260915/OPENALEX_COMPARISON.md` for empirical
results, query provenance, exclusion counts and prior-work references.

The September 15 review extension computes annual name/ID multiplicity and
source-ORCID coverage on the same cached data. The archived comparison reports
full and fractional Gini, single-appearance shares and the three-factor log
decomposition. The current dashboard instead leads with the retention audit
and unallocated-credit accounting. No paired input population, name normalizer
or person-resolution method changed. See `REVIEW_RESPONSE.md` and
`RETENTION_AUDIT.md` alongside the report for the mathematical corrections.

The root `dashboard/` directory contains the standalone static presentation,
including the graph titles, labelled scales and explanations beneath each
figure. It uses aggregate JSON only and makes no OpenAlex or arXiv API calls.
The earlier availability query has now been followed by the separately frozen historical acquisition. Its report and manifest are in `reports/historical_participation_20260916/`.
