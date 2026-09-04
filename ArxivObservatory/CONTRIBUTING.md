# Contributing

Private collaboration repo for ArxivObservatory (see `README.md`). Suggested
reading order: `README.md` → `DESIGN_PLATFORM.md` (architecture) →
`TAXONOMY.md` (classification instrument) → `DECISIONS.md` (owner rulings).

## Hard boundaries (binding for humans and their AI agents)

1. **No paper content in commits.** Never commit arXiv full text, excerpts,
   snippets, or per-paper label/quote listings. Committed outputs are
   aggregate-only (tables, plots, counts). The repo is private, but it is
   held to the same bar as the public policy. `corpus/`, `papers/`,
   `annotation/`, `results/`, `backups/` and all databases are gitignored —
   keep it that way.
2. **No credentials.** `.env`, API keys, and `verdicts_*.json` never land in
   git; keys are never echoed into logs or command lines.
3. **No paid API calls, no arXiv fetching.** Classification campaigns and
   corpus acquisition are owner-approved, budget-capped operations run by
   the owner. Contributed analysis code must run offline on fixture data.
4. **`pipeline/` and `TAXONOMY.md` are owner-maintained.** Methodology
   changes require an owner decision (`DECISIONS.md` entry) — propose them
   in a PR description or an issue instead of editing. Contribute analysis
   as new modules plus tests.
5. **PRs only.** `main` is merged by the owner after review.

## Getting started without the database

The real database is not in the repo (by policy — it contains corpus
content). The data *format* is fully reconstructible from code:

- Schema and migrations: `pipeline/db.py` (see also `pipeline/migrate.py`).
- The test suite builds small synthetic fixture databases — see
  `tests/conftest.py` and e.g. `tests/test_report.py` for the pattern.
- Run everything: `python3 -m pytest tests/` (fast, no network, no data).

Workflow for real numbers: develop your analysis against a fixture DB and
submit it in a PR; the owner runs accepted code against the real database
and returns **aggregate** outputs in the review thread. A scrubbed
metadata-only snapshot (no paper text) may be provided later if this loop
proves too slow.

## What a good analysis PR looks like

- A new module (e.g. `analysis/<topic>.py`) + a test exercising it on a
  fixture DB + a few sentences in the PR: the question, the estimand, the
  denominator, and what the aggregate output looks like.
- No schema migrations, no edits to `pipeline/`, and flag any new
  dependency explicitly (the current codebase is deliberately light).
- Mind the methodology docs: prevalence claims have gates (see
  `GOLD_STUDY.md`) — exploratory analysis is welcome, but label it as such.

Questions → open an issue.
