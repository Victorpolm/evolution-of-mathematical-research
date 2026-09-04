# v1-pure vs mixed-version comparison (2026-08-12)

**Status: UNVALIDATED EXPLORATORY OUTPUT — DO NOT CITE.**

- mixed: scan `tex-20260810T205113` + codex `cls-20260810T211610` (bulk re-rolled 'latest' text)
- v1: scan `texv1-20260811T215148` + Luna `cls-20260811T220922` (pinned v1: fetched + inferred single-version)
- CONFOUND: text version AND model changed together; the cross-tab below
  bounds the joint effect only. Flag set for multi-version papers derives
  from MIXED text (disclosures present only in later revisions of
  unflagged multi-version papers are invisible until the ~46.5k tail is
  fetched under arXiv coordination).

Common scan-ok cohort papers: 85,742. author_use mixed 2,799 vs v1 2,633; both 2,608; mixed-only 191; v1-only 25.

| month | n common | mixed AU | v1 AU | mixed rate | v1 rate |
|---|---|---|---|---|---|
| 2023-08 | 1734 | 1 | 2 | 0.06% | 0.12% |
| 2023-09 | 1690 | 3 | 3 | 0.18% | 0.18% |
| 2023-10 | 1859 | 11 | 8 | 0.59% | 0.43% |
| 2023-11 | 1779 | 6 | 3 | 0.34% | 0.17% |
| 2023-12 | 1767 | 5 | 5 | 0.28% | 0.28% |
| 2024-01 | 1798 | 9 | 6 | 0.50% | 0.33% |
| 2024-02 | 1879 | 6 | 4 | 0.32% | 0.21% |
| 2024-03 | 1981 | 7 | 6 | 0.35% | 0.30% |
| 2024-04 | 1911 | 9 | 6 | 0.47% | 0.31% |
| 2024-05 | 2024 | 6 | 4 | 0.30% | 0.20% |
| 2024-06 | 1821 | 5 | 4 | 0.27% | 0.22% |
| 2024-07 | 1933 | 6 | 3 | 0.31% | 0.16% |
| 2024-08 | 1632 | 11 | 4 | 0.67% | 0.25% |
| 2024-09 | 1966 | 10 | 10 | 0.51% | 0.51% |
| 2024-10 | 2068 | 21 | 17 | 1.02% | 0.82% |
| 2024-11 | 1979 | 10 | 8 | 0.51% | 0.40% |
| 2024-12 | 2138 | 13 | 8 | 0.61% | 0.37% |
| 2025-01 | 1943 | 14 | 11 | 0.72% | 0.57% |
| 2025-02 | 1865 | 13 | 10 | 0.70% | 0.54% |
| 2025-03 | 2140 | 9 | 6 | 0.42% | 0.28% |
| 2025-04 | 2127 | 29 | 21 | 1.36% | 0.99% |
| 2025-05 | 2209 | 30 | 24 | 1.36% | 1.09% |
| 2025-06 | 2122 | 32 | 27 | 1.51% | 1.27% |
| 2025-07 | 2342 | 32 | 30 | 1.37% | 1.28% |
| 2025-08 | 2241 | 37 | 26 | 1.65% | 1.16% |
| 2025-09 | 2574 | 47 | 46 | 1.83% | 1.79% |
| 2025-10 | 2768 | 45 | 44 | 1.63% | 1.59% |
| 2025-11 | 2564 | 50 | 49 | 1.95% | 1.91% |
| 2025-12 | 2778 | 74 | 70 | 2.66% | 2.52% |
| 2026-01 | 2727 | 74 | 68 | 2.71% | 2.49% |
| 2026-02 | 2697 | 92 | 89 | 3.41% | 3.30% |
| 2026-03 | 3378 | 158 | 155 | 4.68% | 4.59% |
| 2026-04 | 3335 | 168 | 161 | 5.04% | 4.83% |
| 2026-05 | 3797 | 304 | 282 | 8.01% | 7.43% |
| 2026-06 | 4237 | 407 | 393 | 9.61% | 9.28% |
| 2026-07 | 4886 | 804 | 781 | 16.46% | 15.98% |
| 2026-08 | 1053 | 241 | 239 | 22.89% | 22.70% |

Mixed-only papers: candidate 'disclosure added in a revision' OR model disagreement.
v1-only papers: candidate 'disclosure removed in a revision' OR model disagreement.
(Per-paper lists stay out of this report — aggregate-only policy.)
