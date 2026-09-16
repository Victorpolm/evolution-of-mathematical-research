# Mathematics Research Observatory dashboard

This directory contains the static dashboard source and aggregate data. Each graph has a visible title, labelled axes and a description underneath explaining its measure, denominator, calculation, time window and source. Monthly, rolling-12-month and calendar-year views are available.

The first graph is **Papers per observed contributor, P/A**, for 2010–2025. Its two lines use distinct names and OpenAlex resolved author IDs on identical retained papers. The other historical graphs show the component counts and coverage. A broader partial-byline table keeps missing credit unallocated. All measures describe observed keys in a selected population, not validated people.

The earlier 2024–2025 audit, repository paper-ID series and separately reported older pilot remain explicitly distinguished. Their source snapshots are preserved.

## View locally

From the repository root:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8000/dashboard/` in your browser. JavaScript reads the committed JSON files from the same local server; it makes no OpenAlex or arXiv API calls. No package installation or build is required.

The current hosted dashboard is [Mathematics Research Observatory](https://mathematics-research-observatory.tim-gehrunge-2308.chatgpt.site). Access follows the existing private-site permissions; publishing these source files does not change its audience.

## Data and code

- `historical-trends.js` displays `historical_participation.json` and supplies the default view.
- `coverage-audit.js` displays `retention_audit.json`.
- `paper-trends.js` displays the separate `papers_contributors.json` manifest series.
- `app.js` displays the older pilot totals from `data.json` and the methods views.
- `chart-utils.js` supplies the labelled compact charts and legends.
- Markdown files document the audit, historical scope and revised method.

The underlying offline analysis and focused tests are in `ArxivObservatory/analysis/` and `ArxivObservatory/tests/`. See the [historical report and reproduction instructions](../ArxivObservatory/reports/historical_participation_20260916/HISTORICAL_PARTICIPATION.md) and the [earlier pilot instructions](../ArxivObservatory/analysis/OPENALEX_INTERIM.md).

Only aggregate data is included here. The private reproduction archives, raw metadata cache and hosting configuration are intentionally absent. The repository version links to reproduction instructions and an SVG export instead of those private download archives. The dataset remains frozen; the dashboard does not update itself from GitHub or OpenAlex.
