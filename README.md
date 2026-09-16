# evolution-of-mathematical-research

Quantitative study of the evolution, participation, concentration, collaboration, and structure of mathematical research.

## Current checkpoint

The dashboard now opens with **papers per observed contributor, 2010–2025**. It compares distinct raw-name keys with OpenAlex's existing resolved author IDs on exactly the same retained papers. Annual, monthly and rolling 12-month views are available, followed by paper counts, contributor counts and retention.

These are descriptive results for a selected OpenAlex arXiv-linked Mathematics population. They do not establish counts of real people, individual productivity changes or causal AI effects. Names and IDs can both split or combine people; changing metadata completeness remains a limitation.

- [Historical analysis, results and reproduction](ArxivObservatory/reports/historical_participation_20260916/HISTORICAL_PARTICIPATION.md)
- [Earlier 2024–2025 retention audit](ArxivObservatory/reports/openalex_interim_20260915/RETENTION_AUDIT.md)
- [Static dashboard source and local viewing instructions](dashboard/README.md)
- [Revised mathematical method and prior work — draft PR #3](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/3)
- [Analysis and dashboard implementation — draft PR #2](https://github.com/Victorpolm/evolution-of-mathematical-research/pull/2)

The historical metadata query covers publication years 2010–2026; analysis dates come from arXiv ID months in 2010–2025. Annual active-key counts do not require a five-year lookback. Future career-entry measures do, and still require independent identity and coverage validation.

## Reproduction and scope

Analysis code runs offline. From `ArxivObservatory/`, run the 27 focused fixture checks with:

```sh
python tests/run_participation_checks.py
```

Reproducing the empirical aggregates requires the separately supplied frozen metadata snapshot. The committed acquisition manifest records page hashes and counts; it is not a substitute for the original data bytes. Figure rendering additionally requires matplotlib. The dashboard can be viewed from the committed aggregate files alone.

Repository contributions contain code, documentation and aggregates. Raw author records, paper text, databases, credentials and the network acquisition helper are excluded. The upstream AI-disclosure pipeline and taxonomy remain owner-maintained; changes are submitted as drafts for review.
