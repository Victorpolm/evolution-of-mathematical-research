# Interim OpenAlex-only comparison

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

Calculation uses only the Python standard library. Figure rendering adds
matplotlib. Raw metadata and the user-authorized free-API session helper remain
outside this repository; contributed analysis code performs no network calls.
Committed outputs contain only aggregates. No paper text was fetched from
arXiv, no paid API account was used, and pipeline/taxonomy files are unchanged.

The six new fixture tests can be collected by pytest alongside existing tests.
They also run as standard-library `unittest.FunctionTestCase` instances in
environments without pytest. The focused run covers 15 tests including the
existing paper-count and metadata-export checks. The unavailable full upstream
checkout was not reconstructed just to claim its test suite ran.

See `reports/openalex_interim_20260915/OPENALEX_COMPARISON.md` for empirical
results, query provenance, exclusion counts and prior-work references.
