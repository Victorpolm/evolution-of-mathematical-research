# Supply the existing data for the participation analysis

The full run needs the existing paper metadata and OpenAlex authorship CSV.
The shared repository intentionally excludes those records. The ID manifest
alone cannot identify authors or primary mathematical categories.

On the machine holding Johannes's database, from the ArxivObservatory folder:

    python3 -m analysis.export_metadata \
      --database observatory.db \
      --openalex-csv results/paper_authors.csv \
      --output results/analysis_inputs.zip

Use the actual filename of the already acquired OpenAlex CSV. If it is not
available, omit --openalex-csv; the export will explicitly record that gap.
Attach the resulting ZIP to this conversation. Existing equivalent metadata
exports can be supplied directly; running this helper is not required.

The exporter opens SQLite read-only, streams the papers table and includes
only named bibliographic fields. It omits abstracts, comments, submitter
details, paper content, excerpts, classifications and unrelated CSV columns.
It never queries arXiv/OpenAlex and does not change the source files. The
archive includes row counts, schema information and content hashes.

The raw byline is preserved. Author parsing and alignment with OpenAlex IDs
remain subsequent validation steps; this exporter does not claim to resolve
identities or make the data automatically analysis-ready. All available
history is retained to avoid unnecessarily losing the lookback period.

Keep the metadata ZIP and its contents untracked under results/. Only the
analysis code and aggregate outputs belong in a pull request.
