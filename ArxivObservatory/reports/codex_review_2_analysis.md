Found 14 concrete correctness defects, ranked below.

### Critical

1. **[audit.py:90](/mnt/z/ArxivObservatory/pipeline/audit.py:90), [audit.py:101](/mnt/z/ArxivObservatory/pipeline/audit.py:101), [audit.py:112](/mnt/z/ArxivObservatory/pipeline/audit.py:112), [audit.py:118](/mnt/z/ArxivObservatory/pipeline/audit.py:118), [audit.py:133](/mnt/z/ArxivObservatory/pipeline/audit.py:133)** — Worker threads use the main thread’s default SQLite connection, so every nonempty audit raises `sqlite3.ProgrammingError`; failures are caught but still included in `len(sample)`, producing a false “0 missed in N audited negatives” result.  
   Fix: Resolve paths before launching workers or open one read-only connection per worker, and use a successful-result counter as the denominator.

2. **[report.py:68](/mnt/z/ArxivObservatory/pipeline/report.py:68), [report.py:74](/mnt/z/ArxivObservatory/pipeline/report.py:74), [report.py:78](/mnt/z/ArxivObservatory/pipeline/report.py:78), [report.py:89](/mnt/z/ArxivObservatory/pipeline/report.py:89)** — The prevalence denominator includes every frame paper without requiring selected-run scan completion or complete classification of all flagged snippets, so unscanned and pending/failed classifications are silently treated as non-disclosures and prevalence is biased downward.  
   Fix: Persist per-paper run coverage and classification completion, then restrict the denominator to fully observed papers or use an explicit two-phase sampling estimator.

### High

3. **[validate_awesome.py:25](/mnt/z/ArxivObservatory/pipeline/validate_awesome.py:25), [validate_awesome.py:31](/mnt/z/ArxivObservatory/pipeline/validate_awesome.py:31)** — `ROW_RE` requires `**[title](url)**`, whereas the [current upstream README](https://github.com/seewoo5/awesome-ai-for-math#readme) uses ordinary table links, so entries are silently skipped and the recall cross-check can contain zero papers.  
   Fix: Parse normal Markdown table cells with optional emphasis and fail loudly if no data rows or implausibly few rows are parsed.

4. **[report.py:40](/mnt/z/ArxivObservatory/pipeline/report.py:40), [report.py:78](/mnt/z/ArxivObservatory/pipeline/report.py:78), [report.py:93](/mnt/z/ArxivObservatory/pipeline/report.py:93)** — `runs` scopes `flagged` but not `paper_rollup`, and no model is selected, so stale classifications from other runs/models can enter the author-use numerator even when the paper is not flagged by the requested runs.  
   Fix: Store immutable run/model/snippet provenance and filter the rollup to exactly the requested runs and one explicitly selected model.

5. **[report.py:68](/mnt/z/ArxivObservatory/pipeline/report.py:68), [report.py:89](/mnt/z/ArxivObservatory/pipeline/report.py:89)** — The documented `created`-date cohort is instead filtered and grouped by arXiv-ID prefix, assigning papers to incorrect months and admitting papers created outside the window.  
   Fix: Derive the cohort and month from `papers.created`, with normalized date bounds.

6. **[classify.py:149](/mnt/z/ArxivObservatory/pipeline/classify.py:149), [classify.py:150](/mnt/z/ArxivObservatory/pipeline/classify.py:150)** — Responses are zipped positionally to snippets and their supplied `id` is discarded, so a same-length reordered JSON response silently attaches labels to the wrong papers and corrupts prevalence.  
   Fix: Validate unique integer IDs covering `0..len(batch)-1` and map each response object back by ID.

7. **[classify.py:87](/mnt/z/ArxivObservatory/pipeline/classify.py:87), [classify.py:88](/mnt/z/ArxivObservatory/pipeline/classify.py:88), [classify.py:97](/mnt/z/ArxivObservatory/pipeline/classify.py:97)** — Nearby hits are merged but only the single longest original context is retained, so disclosures around other merged hits—especially chained hits spanning well beyond one window—never reach the classifier.  
   Fix: Union overlapping context windows or split groups whenever their complete span would exceed `SNIPPET_MAX`.

8. **[classify.py:102](/mnt/z/ArxivObservatory/pipeline/classify.py:102), [classify.py:169](/mnt/z/ArxivObservatory/pipeline/classify.py:169), [db.py:87](/mnt/z/ArxivObservatory/pipeline/db.py:87)** — The hash omits paper, version, member, scan run, and prompt protocol while the completed set is global by hash, so identical boilerplate can cause later papers/snippets to be skipped and changed versions or prompts to reuse stale labels.  
   Fix: Give every snippet an immutable paper/version/run/member identity and separately key reusable content labels by a hash that includes the prompt/schema/model protocol.

9. **[audit.py:71](/mnt/z/ArxivObservatory/pipeline/audit.py:71), [audit.py:77](/mnt/z/ArxivObservatory/pipeline/audit.py:77), [scan.py:119](/mnt/z/ArxivObservatory/pipeline/scan.py:119)** — Audit negatives are defined as downloaded sources lacking hits, but no evidence shows that each source was successfully processed by the named run, so restricted, interrupted, or failed scans enter the audit as scanner negatives and inflate estimated misses.  
   Fix: Sample only from a persisted `(scan_run, arxiv_id)` completion table with successful full-source coverage.

10. **[audit.py:5](/mnt/z/ArxivObservatory/pipeline/audit.py:5), [audit.py:91](/mnt/z/ArxivObservatory/pipeline/audit.py:91), [audit.py:133](/mnt/z/ArxivObservatory/pipeline/audit.py:133)** — The missed-disclosure fraction among scanner negatives estimates `FN/(FN+TN)`, not scanner recall `TP/(TP+FN)`, so the module’s stated recall interpretation is statistically invalid.  
    Fix: Expand the sampled miss rate over the full negative population to estimate `FN`, obtain validated `TP` from flagged papers, and report `TP/(TP+estimated_FN)` with an appropriate sampling interval.

11. **[audit.py:52](/mnt/z/ArxivObservatory/pipeline/audit.py:52), [audit.py:68](/mnt/z/ArxivObservatory/pipeline/audit.py:68)** — “Full-paper” text is an archive-order concatenation truncated to its first 180,000 characters, silently dropping later files/sections and systematically missing end-of-paper disclosures in long submissions.  
    Fix: Audit all source in bounded chunks or use coverage-preserving section-aware sampling that explicitly includes acknowledgments, appendices, and document tails.

12. **[harvest.py:163](/mnt/z/ArxivObservatory/pipeline/harvest.py:163), [harvest.py:176](/mnt/z/ArxivObservatory/pipeline/harvest.py:176), [harvest.py:179](/mnt/z/ArxivObservatory/pipeline/harvest.py:179)** — Harvest now writes pages under per-query subdirectories, but `reparse()` still globs only root-level legacy pages, so new archives are ignored while stale shared archives may overwrite current metadata.  
    Fix: Require a run/query selection and reparse only pages listed by that run’s completed state or manifest.

### Medium

13. **[audit.py:93](/mnt/z/ArxivObservatory/pipeline/audit.py:93), [audit.py:125](/mnt/z/ArxivObservatory/pipeline/audit.py:125), [audit.py:129](/mnt/z/ArxivObservatory/pipeline/audit.py:129)** — Audit completion is checked across every run and model, while the stored hash contains only the paper ID and stores neither run nor source version, so a prior audit suppresses valid re-auditing after scanner, model, or paper changes.  
    Fix: Store and deduplicate by scanner run, audit model/protocol, paper version, and full input-content hash.

14. **[report.py:54](/mnt/z/ArxivObservatory/pipeline/report.py:54), [report.py:57](/mnt/z/ArxivObservatory/pipeline/report.py:57), [report.py:110](/mnt/z/ArxivObservatory/pipeline/report.py:110)** — Multiple author-use snippets merge tools/models/categories and impact but not location, leaving the unordered first snippet’s location and undercounting papers disclosing in multiple places.  
    Fix: Roll locations up as a deduplicated multi-label set, or define and apply a deterministic paper-level location hierarchy.

### Checked and found sound

- Wilson interval formula, zero-denominator guard, and `a_month/n_math` division.
- Paper sets prevent duplicate scan hits or snippets from double-counting prevalence numerators.
- Batch length failures reject the whole batch and write no partial classification rows.
- Current stored snippet labels had valid JSON, polarity enums, array field types, and confidence ranges.
- `fetch.py::select_todo` correctly leaves transient errors eligible while treating successful rows and 404s as terminal.
- Distinct `from`/`until` harvest queries now have isolated write directories and state; the regression is specifically in reparsing them.
- No files were modified.

Codex session ID: 019fe6e5-1314-7802-86f4-dcc3338ec85a
Resume in Codex: codex resume 019fe6e5-1314-7802-86f4-dcc3338ec85a
