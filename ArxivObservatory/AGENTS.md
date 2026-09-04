# Guidance for AI agents working in this repo

This project measures author-disclosed AI assistance in arXiv math papers.
Read `CONTRIBUTING.md` first; its Hard boundaries are binding for you:

- Never commit paper text, excerpts, per-paper labels, databases, or
  credentials. Committed outputs are aggregate-only.
- Never call paid APIs (OpenAI, Anthropic, …) and never fetch from arXiv.
  All contributed code runs offline.
- Do not edit `pipeline/` or `TAXONOMY.md` — propose changes in the PR
  description instead. Add analysis as new modules + tests.
- Build/test: `python3 -m pytest tests/` (fast, no network, no data).
- The real database is not in this repo. Reconstruct the data format from
  `pipeline/db.py` and build fixture DBs the way `tests/conftest.py` does.
