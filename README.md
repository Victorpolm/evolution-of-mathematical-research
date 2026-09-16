# evolution-of-mathematical-research

Quantitative study of the evolution, participation, concentration, collaboration, and structure of mathematical research.

## Current checkpoint

The 2024–2025 OpenAlex comparison is a bounded pilot. **Interpretations of population participation and concentration are on hold** because the completeness of author information differs substantially between years.

Start with the [retention audit](ArxivObservatory/reports/openalex_interim_20260915/RETENTION_AUDIT.md). It reports coverage, whole bylines with missing IDs, and publication credit that cannot be allocated to identified authors. The [earlier name/ID comparison](ArxivObservatory/reports/openalex_interim_20260915/OPENALEX_COMPARISON.md) remains available as an archived diagnostic.

- [Analysis, tests and reproduction instructions](ArxivObservatory/analysis/OPENALEX_INTERIM.md)
- [Static dashboard source and local viewing instructions](dashboard/README.md)
- [Revised mathematical method and historical plan — draft PR #3](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/3)
- [Analysis and dashboard implementation — draft PR #2](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/2)

The historical target is metadata from 2010 onward, with main comparisons from 2015 after a five-year lookback and an end year determined by coverage validation. The [historical availability note](dashboard/HISTORICAL_EXTENSION.md) confirms that earlier records exist; it does not represent a completed historical contributor analysis.

## Reproduction and scope

Analysis code runs offline. From `ArxivObservatory/`, run the 22 focused fixture checks with:

```sh
python tests/run_participation_checks.py
```

Reproducing the empirical aggregates requires the separately supplied frozen metadata snapshot. The committed acquisition manifest records page hashes and counts; it is not a substitute for the original data bytes. Figure rendering additionally requires matplotlib. The dashboard can be viewed from the committed aggregate files alone.

Repository contributions contain code, documentation and aggregates. Raw author records, paper text, databases, credentials and the network acquisition helper are excluded. The upstream AI-disclosure pipeline and taxonomy remain owner-maintained; changes are submitted as drafts for review.
