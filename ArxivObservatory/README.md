# ArxivObservatory

**Research prototype — validation incomplete. Do not cite any figures.**

An independent metascience project (not affiliated with arXiv) measuring
author-reported AI assistance in mathematics papers on arXiv. Currently a
private engineering prototype: the pipeline (metadata harvest, polite
full-text acquisition, keyword scan, LLM classification, site generation)
runs end-to-end on the full 3-year corpus, but its outputs remain
unvalidated automated-classifier estimates: the calibration annotation round
is complete, the instrument is at taxonomy v2.8, a full v1-pinned
classification run (v2.7) has completed over the selected scan (pre-tail; a final
run over the completed v1 acquisition is still ahead), and the two-reviewer
gold study and frozen release remain open. The immutable
run/artifact/evidence spine is in place. See `review_codex12.md` for the
current adversarial AI-assisted audit (earlier iterations:
`review_codex2.md`–`review_codex11.md`), `LEDGER.md` for finding-by-finding
status, and `DESIGN_PLATFORM.md` for the roadmap.

Pitch: `PITCH.md` / `pitch.tex`. Contact: Johannes Schmitt
(johannes.schmitt@math.ethz.ch). License: MIT for the software (see
`LICENSE`; arXiv paper content is never redistributed and future released
aggregates are intended as CC BY 4.0).

## AI use in this project

This project both measures and uses AI, and discloses its own use fully:

- **Claude Code (Claude Fable 5, Anthropic)**: code generation for the
  pipeline and website, conducting data retrieval and analysis runs,
  assisting with study design and the choice of key metrics.
- **codex CLI (GPT-5.6 Sol, OpenAI)**: seven rounds of extensive adversarial
  code/methodology review (an AI-system audit, not human peer review) (`review_codex*.md`) and, as `gpt-5.6-sol@medium`,
  the exploratory bulk snippet classification.
- **gpt-5.6-luna (OpenAI API)**: the v1-pinned snippet classification run.
- The human owner retained final responsibility and sign-off on all
  scientific-validity decisions (`DECISIONS.md`) and performed the human
  annotation; AI contributed to design and metric choices as described.

## Funding

This work was supported by an unrestricted gift from Google Ireland Limited
to ETH Zurich, supporting work related to "Research on Evals", administered
through the ETH Zurich Foundation, and by the Swiss National Science
Foundation grant 10009122, "Beyond Benchmark Scores: Analyzing AI Reasoning
on Research-Level Mathematics". J.S. was also supported by SwissMAP.
