# Exact frozen metadata input

Archive supplied separately: `OpenAlex_Historical_Metadata_2010-2026_2026-09-16.zip`.

- SHA-256: `27fae0c32b68f07c6a6128c9513adee060357d9025249ea09e745e25241e8d6f`
- Size: 65,991,300 bytes.
- Retrieval interval: 16 September 2026, 07:49:48–08:16:21 UTC.
- 413,438 unique works; 204 monthly partitions; 4,241 retained cache pages.
- A paging consistency check found 28 overlaps in mixed cursor/numbered partitions. Reacquiring 407 cursor-prefix pages reconciled all 25 mixed partitions. Every final partition uses one strategy and its unique work count matches the reported total. No duplicated rows were silently dropped to repair pagination.
- At least 5,350 free daily credits remained after reconciliation. No paid allowance was used.

The archive contains public bibliographic bylines and existing identifiers, but no paper text, titles, abstracts, affiliations or API credential. The network acquisition helper is included there, outside the offline contribution. The snapshot is supplied separately; the aggregate-only repository and page hashes alone do not provide access to the original metadata bytes.

Run `python -m analysis.historical_participation` with the extracted snapshot as described in the report. Every page hash, partition count, scope filter and unique-work condition is checked. The original 15 September two-year snapshot remains unchanged.
