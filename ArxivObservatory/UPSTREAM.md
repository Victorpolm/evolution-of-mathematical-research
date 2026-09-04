# Source, access, and synchronization

This directory is a working snapshot of the private repository
[`schmittj/ArxivObservatory`](https://github.com/schmittj/ArxivObservatory),
copied into Victor Polm's private research repository on 2026-09-04.

## GitHub invitation and access

- GitHub account: `Victorpolm`
- Upstream repository: `schmittj/ArxivObservatory`
- Access observed when the invitation workflow was completed: **read**
- Upstream default branch: `main`
- Local analysis branch used for the new work: `victor/democratization-openalex`

The invitation itself is an account permission managed by GitHub, not a file,
so it cannot be copied into this repository. This note records the relevant
provenance. Access to the upstream private repository still depends on the
permission granted by its owner.

## Included work

The snapshot includes the upstream tracked source tree plus the new offline
democratization study:

- `analysis/democratization.py`
- `analysis/DEMOCRATIZATION.md`
- `tests/test_democratization.py`

The study measures publication growth, active-author participation,
fractional productivity, observed arXiv-mathematics age, output concentration
(top 1%, 5%, and 10% and Gini), and collaboration indicators.

## Deliberately excluded

In accordance with the upstream contribution policy, this copy does **not**
contain paper text, excerpts, per-paper labels, databases, credentials, or the
paper-author OpenAlex CSV and other files under `results/`. Those records must
remain local and untracked. Only offline analysis code, tests, documentation,
and aggregate-safe project files are stored here.

## Sending changes upstream

Treat `schmittj/ArxivObservatory` as the authoritative upstream project. New
work should follow its `CONTRIBUTING.md` and `AGENTS.md`: add analysis modules
and fixture-based tests, do not edit `pipeline/` or `TAXONOMY.md`, and send
changes through a pull request after the owner grants write access or enables
a private-fork workflow.
