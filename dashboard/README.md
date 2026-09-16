# Mathematics Research Observatory dashboard

This directory contains the static dashboard source and aggregate data. Each graph has a visible title, labelled axes and a description underneath explaining its measure, denominator, calculation, time window and source. Monthly, rolling-12-month and calendar-year views are available.

The main view is a **coverage audit**, not a validated population trend. It compares linked and retained papers and shows missing author IDs. The repository paper-ID series and the separately reported older pilot remain explicitly distinguished. Contributor series without matching data are labelled unavailable.

## View locally

From the repository root:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8000/dashboard/` in your browser. JavaScript reads the committed JSON files from the same local server; it makes no OpenAlex or arXiv API calls. No package installation or build is required.

The current hosted dashboard is [Mathematics Research Observatory](https://mathematics-research-observatory.tim-gehrunge-2308.chatgpt.site). Access follows the existing private-site permissions; publishing these source files does not change its audience.

## Data and code

- `coverage-audit.js` displays `retention_audit.json`.
- `paper-trends.js` displays the separate `papers_contributors.json` manifest series.
- `app.js` displays the older pilot totals from `data.json` and the methods views.
- `chart-utils.js` supplies the labelled compact charts and legends.
- Markdown files document the audit, historical scope and revised method.

The underlying offline analysis and focused tests are in `ArxivObservatory/analysis/` and `ArxivObservatory/tests/`. See [reproduction instructions](../ArxivObservatory/analysis/OPENALEX_INTERIM.md).

Only aggregate data is included here. The private reproduction archives, raw metadata cache and hosting configuration are intentionally absent. The repository version links to reproduction instructions and an SVG export instead of those private download archives. The dataset remains frozen; the dashboard does not update itself from GitHub or OpenAlex.
