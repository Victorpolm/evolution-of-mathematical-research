# ArxivObservatory repository review — iteration 3

**Review date:** 2026-08-10 (Europe/Zurich)

**Reviewed snapshot:** `c2a63882511a293e00858cd687e3bc501c2805c9` (`c2a6388`; the worktree was clean before this requested review file was created)

**Comparison baseline:** the snapshot reviewed in `review_codex2.md` (`46b0060`)

**Scope:** all 86 tracked files; the current code, tests, generated site and distribution ZIP, reports/results, specifications, pitch, prior-art survey, research and gold-study plans, AWS/deployment material, recent Git history, and the structure and consistency of the ignored live SQLite/corpus/annotation state. I did not send manuscripts to a model, alter cloud services, download papers, or edit project code.

## Executive verdict

The latest changes are substantial and directionally correct. This is no longer merely the same hackathon pipeline with better wording. The repository now has versioned migrations, run and item ledgers, normalized evidence links, explicit scan-error states, run-scoped reporting, source-version strata, model pinning and one-paper isolation options, stricter label validation, a render-truth layer, a serious gold-study design, an S3 reconciliation importer, 70 fixture tests, CI, a dependency file, an operator runbook, and a prominent prototype/non-affiliation warning. These improvements should be preserved.

The project is nevertheless **not ready to release scientific results or deploy the current numerical site**. The central reason is unusually concrete: the live database has not completed the new pipeline even once. It contains two 129-paper v2 scan pilots, but **zero v2 classification runs/items, render checks, annotations, or frozen releases**. The tracked 16.1% site, report, and distribution ZIP remain products of the corrupted legacy analysis. The current artifacts therefore do not demonstrate the new design.

Several cross-stage contracts also remain open. A scan with skipped rendered material can be marked `complete`; a report can combine a denominator from one scan with labels from another; classification failures and pending outcomes can remain in the denominator; a release can be frozen without evidence gates, isolated model calls, clean-code provenance, or human calibration; and the site accepts a still weaker live-run contract. The “immutable” release is currently a small manifest over mutable live tables, not a reconstructable dataset snapshot.

The recommended near-term product remains narrow:

> A version-explicit, human-calibrated observatory of **author-reported generative-AI/agent assistance visible in a specified rendered arXiv paper-version**.

Computer-algebra/proof-assistant tracking can become a separately validated instrument. Detector-inferred writing, mathematical-error auditing, author-productivity analysis, and the volunteer conversation-sharing workflow should remain separate studies with separate protocols, permissions, and governance.

### Release decision

| Deliverable | Current decision | Why |
|---|---|---|
| Private engineering work | Continue | The new architecture is worth completing |
| Public source-code alpha | Possible after repository sanitation, licensing, setup/security documentation, and disabling unsafe legacy entry points | Code can be shared without asserting results |
| Public numerical dashboard/data | **Block** | No end-to-end v2 release or representative human calibration exists |
| 16.1%, weekly trend, subfield ranking, tool/model share, impact split | **Do not promote or cite** | They remain legacy, mixed-version, model-only outputs |
| WP2 detector study, WP3 reliability audit, volunteer share-link service | Keep in research-design phase | Different estimands and materially higher ethical/security risk |

## Snapshot and checks

Since the previous review, nine commits changed 45 files with 4,519 insertions and 590 deletions. Important new files include `pipeline/migrate.py`, `pipeline/runs.py`, `pipeline/taxonomy.py`, `pipeline/render_check.py`, `pipeline/annotate.py`, `pipeline/aws/import_s3.py`, `GOLD_STUDY.md`, `CROSSCHECK.md`, `LEDGER.md`, `WORKFLOW.md`, `pyproject.toml`, `requirements.lock`, tests, and CI.

The live database at review time contained:

| Object | Count / state |
|---|---:|
| papers / version rows | 235,342 / 418,232 |
| current `files` rows / successful files | 6,590 / 6,570 |
| `artifacts` rows | 6,571 |
| v2 scan runs / items | 2 / 258 |
| v2 classification runs / items / evidence links | 0 / 0 / 0 |
| render checks / v2 annotations / releases | 0 / 0 / 0 |
| legacy classification rows / legacy human-review rows | 3,544 / 49 |

Both v2 scan pilots have 129 `ok` items and NULL versions. The earlier pilot has no artifact hashes; the later has hashes, but only 27 of 129 resolve to an `artifacts` row for the same paper/hash. Both runs are stamped from dirty, older commits (`b9a9910-dirty` and `6db2ddf-dirty`). They are engineering smoke tests, not release evidence.

Read-only checks performed during this review:

- `python3 -m pytest -q -p no:cacheprovider`: **70 passed in 1.69 s**.
- Shell syntax checks for `pipeline/backfill.sh` and `pipeline/aws/sync_home.sh`: passed.
- All main pipeline CLI help/import probes: passed.
- SQLite `PRAGMA quick_check`: `ok`; `PRAGMA foreign_key_check`: no reported violations.
- Migration status: live schema version 3, matching code head 3.
- Targeted synthetic contract diagnostics reproduced mixed-run reporting and acceptance of an incomplete item inside a run marked complete.
- Targeted validator diagnostics reproduced `{"catalytic": "false"}` becoming `True`.
- Targeted acquisition diagnostics reproduced a valid large single-gzip TeX response being classified `unknown` because only its first 65,536 compressed bytes are decompressed.
- `bar_svg([])` and `line_svg([], [], [], [])` both raise `ValueError`, so the site cannot render a legitimate zero-positive/thin cohort.

Passing tests establish useful local correctness, but they do not establish a valid analysis or release. The missing coverage is mostly at stage boundaries, hostile-input boundaries, and full end-to-end reconstruction.

## What was genuinely fixed since review 2

The following are meaningful improvements, not cosmetic changes:

1. **A real migration mechanism now exists.** `pipeline/migrate.py` versions the schema, backs up an existing database, applies additive migrations, and `pipeline/db.py:43-51` refuses a database behind the expected version.
2. **No-hit is no longer inherently treated as scanned.** `scan_runs` and `scan_items` record one outcome per submitted job; `pipeline/report.py:150-155` uses only selected-run `status='ok'` rows as its scanned denominator.
3. **New scan IDs are guarded against reuse.** The new code no longer performs the destructive delete-and-repopulate behavior that orphaned legacy evidence (`pipeline/runs.py:27-45`).
4. **Classification provenance is far stronger.** A classification run records scan-run set, model label, prompt hash, taxonomy, parameters, isolation mode, code stamp, and durable per-snippet status. `classification_evidence` normalizes hit links with foreign keys.
5. **Response attribution is now ID-based and fail-closed.** `pipeline/classify.py:248-274` rejects missing/duplicate/wrong IDs rather than silently using positional output.
6. **The taxonomy has a versioned machine source.** `pipeline/taxonomy.py` drives both prompt definitions and enum validation, with a human companion in `TAXONOMY.md`.
7. **Evidence gates exist.** Quote grounding is recorded, and `pipeline/render_check.py` checks version-pinned compiled PDF text with exact/dehyphenated/fuzzy methods. The report can require grounding and rendering.
8. **Report scoping and missingness language improved.** `pipeline/report.py` takes explicit run IDs and dates, separates v1/later/unknown source strata, reports fetch/scan/classification problems, scopes downstream tables to the cohort, escapes Markdown, and labels pooled results as raw mixed-version classifier positives.
9. **A credible validation plan now exists.** `GOLD_STUDY.md` correctly recognizes that candidate precision and scanner misses require stratified sampling, two reviewers, adjudication, and design-based estimation.
10. **The new site generator escapes classifier-derived SVG/JSON values and supplies table alternatives.** These changes at `pipeline/build_site.py:72-94,143-153,271-274` and the `textContent` tooltip in `pipeline/sitetext.py:123-159` are good.
11. **Bulk acquisition has a serious importer gate.** `pipeline/aws/import_s3.py` hashes archives/members, reconciles IDs both directions, detects duplicates/extras/missing/unknown formats, and normally refuses registration on problems.
12. **Repository basics started to appear.** README, runbook, dependency metadata, tests, and SHA-pinned GitHub Actions are all welcome.

These improvements justify completing v2 rather than starting over. They do not justify carrying forward the legacy numerical outputs.

## Highest-priority release blockers

### P0-1 — The checked-in site and ZIP are stale legacy artifacts, not v2 outputs

The strongest fact in this review is the mismatch between code and deliverables:

- The database has no v2 classification data or release, yet `site/index.html:119-165` foregrounds 1,038 of 6,429 papers (16.1%).
- `site/data/disclosures.json` lacks the run/model/taxonomy/gate provenance fields that the new generator writes at `pipeline/build_site.py:208-220`.
- `site/index.html` starts with `<title>` rather than a doctype/document skeleton and still lacks the disclosure table alternatives. The new generator would add these at `pipeline/build_site.py:301-305`, proving the artifact was not rebuilt after the code changed.
- The checked-in site still says “28/28” at `site/index.html:202-205`, while current source copy says 28 of 29 at `pipeline/sitetext.py:105-111`. More importantly, that external-list flag rate is not disclosure-classification accuracy at all.
- `site/dashboard.html:102-116` remains a second directly addressable, unbannered fragment with the obsolete “142” metadata result. A host that publishes the whole `site/` tree publishes it too.
- The current index, JSON, and ZIP-embedded copies have different SHA-256 hashes. The ZIP contains local timestamps, mode 0777 files, and no README, license, release manifest, checksums, or signature.
- `reports/report.md` now has an honest warning banner, but its 1,038-paper analysis is explicitly a legacy mutable-run artifact.

The banner “validation incomplete; do not cite” is necessary and helpful, but it does not neutralize a large polished headline that can be screenshotted or quoted without context. Replace real-result pages with a synthetic demo or keep the entire site private until a validated release exists. Move templates outside the publish root.

### P0-2 — A scan can be marked complete despite skipped rendered material

`pipeline/scan.py:176-188` correctly maps large/budget-skipped members and PDF-in-tar items to non-OK item states. However, `n_err` increments only for exceptions at `pipeline/scan.py:234-236`, and run status is set from `n_err` alone at `pipeline/scan.py:255-260`. A run containing `incomplete:members-skipped` or `skipped:pdf-tar-member` items can therefore be `complete` and exit zero.

`pipeline/report.py:84-95` trusts the run-level status when freezing. A synthetic test confirmed that `run_info(..., freeze=True)` accepts a complete scan with an `incomplete:members-skipped` item.

The fix is not necessarily to demand zero missing papers. It is to distinguish:

- complete execution of the declared input manifest;
- successful extraction of a paper-version;
- explicitly excluded/unsupported strata;
- failed/unknown outcomes; and
- an analysis-specific coverage threshold.

Freeze should independently reconcile the expected manifest to items, recompute statuses/counts, and fail on unexplained gaps. Any deliberate exclusions must be preregistered and reported as missing, not hidden behind a `complete` run label.

### P0-3 — A release can count labels from a different scan run

The classifier accepts multiple scan runs (`pipeline/classify.py:369-370,417`). Classification items do not carry a direct source scan-run column; lineage exists only through evidence edges. `pipeline/report.py:80-83` merely checks that the chosen denominator scan appears somewhere in the classification run’s list, while `paper_rollup()` at `pipeline/report.py:99-135` reads every item in that classification run.

A synthetic database reproduced the failure: a classification run consumed `scan-a` and `scan-b`; the selected `scan-a` denominator had zero flags, yet an author-use item from `scan-b` produced a 100% author-use rate against `scan-a`.

This can also mix metadata and full-text protocols or different source versions. Require exactly one full-text scan run for a prevalence release, or join every classification item through `classification_evidence` to the selected run, paper-version, scan item, and artifact. Assert that every numerator item is eligible under the selected release protocol. Metadata evidence can be intentionally combined, but only through an explicit composite analysis manifest rather than an untyped list.

### P0-4 — “Freeze” is not yet a scientific release gate

`pipeline/report.py:60-96,283-313` currently fails some unsafe cases, but still allows a frozen release with:

- incomplete/skipped scan items mislabeled by the run as complete;
- pending or partially classified papers;
- classification evidence from another consumed scan run/version;
- no `--require-grounded` or `--require-rendered` gate;
- non-isolated 30-paper model batches;
- `unknown` or `*-dirty` code stamps;
- unknown artifact versions;
- no human-validation project or calibration metrics;
- no independently recomputed item/hit/evidence counts; and
- no requirement that upstream runs existed and were terminal before classification began.

The site calls the weaker non-freeze contract and accepts partial/unpinned runs (`pipeline/build_site.py:156-170,320-330`). It does not show pending or classification-failure counts.

Make publication a separate command that consumes a validated `release_id`, not arbitrary run IDs. The gate should enforce the registered estimand, input cohort, clean immutable code/container/tool identities, exact scan/classification/render completion, safe model boundary, required evidence policy, human-validation status, disclosure thresholds, and a fully materialized output manifest.

### P0-5 — Releases are hashes over mutable tables, not reconstructable snapshots

The release manifest contains counts, three paper-set hashes, and a report hash. It omits the member lists, paper/version/artifact IDs and hashes, classification-item IDs, evidence edges, render-check identities, frame rows, acquisition manifest, model request identities, tool versions, and site/data/package hashes. There is no release reader or verifier, and `build_site` cannot consume a release.

Important inputs remain mutable:

- `papers` and `files` are live tables used by reporting;
- `classification_items.render_status` changes on render-check redo (`pipeline/render_check.py:266-275`);
- run status changes on supersession;
- artifact paths can point to overwritten files; and
- a report path is written before the release row is inserted, so reusing a path or duplicate release ID can overwrite a previously referenced report.

The report embeds today’s date, so identical inputs rebuilt on another day produce different bytes. `db.code_commit()` is sampled after the report write and can mark a release dirty merely because the report itself is tracked.

Materialize a release directory or database/Parquet snapshot with a canonical sorted manifest. Include every membership row and content hash, protocol files, code/container/tool/model identities, validation estimates, generated artifact hashes, and a deterministic timestamp supplied by the release. Make it append-only at the storage layer and verify it from a clean clone before deployment.

### P0-6 — The gold-study tooling is not yet bound to a release or safe annotation record

The protocol document is substantially better than the implementation. `pipeline/annotate.py:132-162` samples all `ok` papers in raw run IDs; it does not load a release, enforce a cohort/category/version policy, validate compatible terminal runs, or check that the classification run consumed the scan run. A local ignored smoke manifest actually names `cls-nonexistent`, which the command accepted.

Version and evidence identity are not preserved:

- contexts are re-extracted from current mutable `files.path`, not the scanned artifact/hash (`pipeline/annotate.py:81-97`);
- NULL scan versions are replaced by current `papers.latest_version` or v1 (`pipeline/annotate.py:178-206`);
- reviewer links are unversioned `/abs/<id>` links;
- metadata is the current paper row, not a version-frozen record; and
- `member_texts()` reads every regular archive member up to 10 MiB without the scanner’s file selection or total budget (`pipeline/annotate.py:37-63`).

The sampling strata can overlap when a POS label comes from a metadata run but the selected full-text run has no corresponding flag: `neg = scanned - flagged` does not subtract POS. The later assignment silently overwrites the earlier stratum. The manifest also lacks per-item version/artifact/hash/inclusion-probability bindings.

Human-review integrity is incomplete:

- packets reveal retrieval status because NEG items have no highlighted excerpts while flagged items do;
- an untrusted manuscript can close a Markdown fence, inject raw HTML/remote images, or insert a fake `## ITEM …` marker;
- global regex ingestion at `pipeline/annotate.py:226-257` does not verify code fences, manifest membership, assignment, packet hash, project, or reviewer;
- reviewer names enter output filenames without path confinement;
- only the top-level verdict is validated; categories/impact/tools/location are arbitrary strings;
- duplicate re-ingest is allowed; and
- agreement conflates versions and silently uses the first two reviewers (`pipeline/annotate.py:276-303`).

The promised adjudication workflow, HARD stratum, design-based estimator, uncertainty intervals, axis-level reliability, and correction from gold labels to prevalence are not implemented.

Use a signed/data-only JSON manifest with opaque item IDs and a separate structured response file. Bind every item to release, paper-version, artifact hash, reviewer assignment, and packet hash; escape rendered review views; validate every enum; make ingestion idempotent; and implement adjudication and estimators before fielding the study.

### P0-7 — Hostile paper text still reaches an agentic process with repository access

Untrusted source text is interpolated directly into an agent prompt (`pipeline/classify.py:123-130`). `call_codex()` launches `codex exec --skip-git-repo-check -s read-only` from the repository and inherits the current working directory and environment (`pipeline/classify.py:141-155`). Read-only prevents writes; it does not provide confidentiality, prevent prompt-driven reads of other repository/corpus files, remove ambient credentials, or establish controlled vendor egress.

`--isolate` limits prompt co-tenancy to one paper only when selected. It is optional, as is the model (`pipeline/classify.py:367-386`), and freeze does not require isolation. The exact response has no byte cap, and snippets/responses are retained without an access, encryption, retention, deletion, subprocessor, or international-transfer policy. The legacy full-paper `pipeline/audit.py` retains the same agentic boundary on much more source text.

Prefer a non-agentic structured-output API with tools disabled and a pinned immutable model snapshot. If the agentic CLI remains, run one paper per process in an empty-root ephemeral container/VM with a minimal environment, no repository/corpus mount, no ambient credentials, deny-by-default network except the explicit model endpoint, and CPU/RAM/process/output/time limits. Record the exact request/response/protocol identity and establish institutional vendor/data-processing approval.

### P0-8 — Paper-level expressive artifacts still violate the stated publication boundary

The repository still tracks `results/ai_ack_hits.csv`, `results/ai_ack_hits.json`, `results/ai_ack_report.md`, `results/candidate_papers.*`, and `results/manual_review.md`. These expose paper IDs/titles, automated or human labels, source paths, and long snippets. `reports/awesome_validation.json` maps titles/IDs to per-paper buckets. `TAXONOMY.md` also names individual example papers.

This conflicts with `PITCH.md:67,79-80`, `TECH_NOTES.md:46-50,188-194`, `WORKFLOW.md:73-81`, and the current aggregate-only owner decision. Removing `reports/spotcheck_result_bearing.md` and `pipeline/aws/instance.txt` from the current tree was good, but both remain in Git history; deletion is not history sanitation.

Before making the repository public:

- remove all expressive per-paper outputs from the public tree and published packages;
- define a schema allowlist for aggregate release artifacts;
- review whether history rewriting is legally/ethically necessary, coordinating before any destructive rewrite;
- keep restricted evidence in access-controlled storage with retention and deletion rules; and
- implement a correction/takedown channel and versioned correction ledger.

## Scientific validity review

### 1. Freeze the estimand before rebuilding

The project still has not selected its primary version policy (`LEDGER.md:113-123`). The current historical headline cohorts papers by first-submission date but reads the latest version available at fetch time. In the 6,429-paper legacy headline cohort, 653 artifacts are later than v1: 607/5,346 July papers versus 46/1,083 early-August papers. That differential follow-up can create an apparent trend even with a perfect classifier.

Recommended primary estimand:

> Among math-primary arXiv paper-versions first submitted in a prespecified interval, what proportion contain, in the rendered text of **v1 acquired at a fixed lag**, an explicit author statement that a generative-AI/agent system assisted production of that paper?

Recommended secondary estimands:

- latest version at a common fixed follow-up cutoff;
- disclosure added/removed between versions;
- PDF-only and unknown-version strata;
- cross-listed sensitivity analysis; and
- other computational-tool families under separate instruments.

Never describe this as prevalence of AI use. It measures visible author reporting, jointly determined by use, disclosure norms, author interpretation, and the instrument.

### 2. The current gold sample is not sufficient for all displayed claims

The proposed POS/FLAG/NEG design can estimate overall system error if it is release-bound and correctly implemented. It does not automatically validate weekly trends, subfield rankings, impact classes, tool/model shares, locations, or version-change estimates. Error rates can vary by month, version, subfield, source format, language, disclosure genre, tool family, and model-prompt protocol.

For a release with strata `h`, estimate the total true disclosures using the design weights, for example

`T_hat = sum_h N_h * (y_h / n_h)`, with prevalence `T_hat / N`,

and use a stratified finite-population variance or a prespecified design-respecting bootstrap. Estimate candidate precision, false-omission rate, and system sensitivity from the appropriate strata; do not call the proportion of misses among sampled scanner-negatives “recall.” Report bounds or missing-outcome sensitivity analyses for fetch, scan, and classification failures.

If trends/subfields are public goals, either allocate enough double-reviewed gold data within those dimensions or fit and validate an explicitly prespecified hierarchical measurement-error model. A 300-paper NEG sample is useful for overall rare misses but cannot establish high recall in every subfield/month.

### 3. Negative review must be independent and version-pinned

The packet gives flagged items highlighted retrieval hints while NEG items generally have no excerpts. Reviewers can infer the negative stratum, and unequal retrieval assistance can lower apparent misses. An unversioned arXiv link may also show a later paper than the sampled artifact.

Use two distinct tasks:

- **candidate adjudication:** reviewers may receive retrieval contexts to estimate precision and label axes efficiently;
- **negative full-paper audit:** reviewers receive the same version-pinned rendered PDF workflow for every item, without machine highlights or scanner status, and follow a documented exhaustive section protocol.

Both should be double reviewed, conflicts/recusals recorded, disagreements adjudicated, and reviewer training/calibration separated from the locked evaluation sample.

### 4. Existing “validation” numbers remain development checks

- The 28/30 result-bearing spot-check is a useful random quality check, but it is one reviewer judging quotes from selected classifier-positive papers. Call it an apparent PPV development check, provide a binomial interval, and do not generalize it to prevalence or other axes.
- The external awesome-ai-for-math list is a convenience/construct cross-check. `pipeline/validate_awesome.py:45-65,85-89` only asks whether an entry has a keyword flag; it does not verify an author disclosure or the classifier. The tracked output also contains 14 not-in-DB and one in-frame-not-flagged entry.
- The 200-paper audit used another unpinned agent, not blinded human ground truth. Its 2 flags estimate neither recall nor a validated false-negative rate.
- The legacy 13-paper pilot used one manual pass over a small, selected recent sample. It demonstrates feasibility and taxonomy variety, not population prevalence or calibrated accuracy.

Remove these numbers from the public validation panel until they are described as development diagnostics with immutable source/protocol manifests.

### 5. Report unresolved outcomes rather than treating them as negatives

`pipeline/report.py:150-176` keeps every scan-complete paper in the rate denominator even when its flagged snippets are pending or all classifications failed. A paper with one valid topic-only snippet and one failed snippet can also be treated as resolved. Public prevalence should require complete outcome ascertainment or show lower/upper bounds and a resolved-outcome estimand.

The coverage partition is also incomplete: a paper that has a successful current `files` row but is absent from the selected scan run is neither scan error, fetch failure, nor `unfetched` (`pipeline/report.py:156-160`). This allows most of a cohort to disappear from the coverage sentence when a small pilot run is selected. Add `fetched_not_in_run` and ensure every frame member occupies exactly one acquisition/scan/outcome state.

### 6. The public uncertainty display does not match the main uncertainty

Wilson bands quantify binomial/superpopulation variation in the raw classifier-positive proportion. This is close to a census of the acquired cohort, while classifier/retrieval error and missingness dominate. The current site admits that limitation, which is good, but the shaded band remains the only quantitative uncertainty and visually overstates epistemic precision.

After validation, display uncertainty propagated from the stratified human audit and missing-data sensitivity. If Wilson bands remain, name the hypothetical sampling interpretation and visually subordinate them to measurement uncertainty.

### 7. Current weekly/subfield displays are exploratory

`pipeline/build_site.py:175-197` groups by first-submission week, then drops every week with fewer than 200 scanned papers. That data-dependent rule can hide holidays/edge weeks and retains a partial first week if it happens to exceed 200. The subfield view ranks raw rates after a minimum `n=100` filter without multiplicity or measurement-error uncertainty.

Predefine complete calendar windows, expose partial periods, show numerator/denominator and coverage, avoid selective week omission, and use uncertainty/shrinkage for many subfield comparisons. Do not narrate short July/early-August differences as adoption change.

### 8. Tool/model/category/impact counts need their own validation

Only LLM/generic hits enter `merge_snippets()` (`pipeline/classify.py:81-85`). A Lean/CAS-only disclosure is absent, so site language about proof tools and any cross-tool comparison are selection-biased. Tool/model strings are not independently grounded to the snippet, and render matching only establishes that a quote appeared, not that the model’s category/impact/tool interpretation is correct.

The paper rollup gives any author-use snippet permanent priority, takes maximum impact, and unions categories/locations without human override (`pipeline/report.py:99-135`). These are defensible candidates for a prespecified paper-level rule, but not validated facts. Validate each axis, define conflict/dual-use rules, and integrate adjudicated human outcomes or design-based correction.

## Detailed implementation review

### Schema, migrations, and run management

Strengths:

- Additive migrations and a live schema-version table are a large improvement.
- Foreign keys are enabled by `db.connect()`.
- Run IDs are guarded against accidental reuse.
- Per-item errors and evidence edges are explicit.

Remaining issues:

- “Immutable” is an application convention, not a database property. Runs, classification items, render statuses, and releases can be updated/deleted; there are no terminal-state triggers or write-once constraints.
- `scan_hits` remains the legacy table and has no foreign key to `scan_runs`/`scan_items`. The new evidence table links to hits, but the hit itself does not enforce its run or artifact identity.
- `scan_items.artifact_sha256` is not an artifact foreign key. A hash alone cannot select the path/version/channel that was scanned.
- `UNIQUE(run_id, arxiv_id, version)` and artifact uniqueness do not deduplicate NULL versions in SQLite.
- Statuses and count invariants are mostly unconstrained strings. Run finish methods do not verify current state or affected row count.
- A partial replacement can mark the last good run superseded (`pipeline/runs.py:48-59`), after which `run_info` rejects the old run. Supersede only after a replacement passes its acceptance gate.
- `db.connect()` rejects schemas behind head but accepts schemas ahead of the code. Require exact compatibility or an explicit supported range.
- The one-per-day backup path at `pipeline/migrate.py:310-325` reuses an existing backup, so a second migration attempt that day may not snapshot the actual pre-operation database.
- `synchronous=NORMAL` is acceptable for throughput but release/manifest commits should use stronger durability and verified backups.

### Metadata harvest and backfill

The per-query raw-page directories are good, but `pipeline/harvest.py:176-183` still reparses only root `corpus/oai/page_*.xml.gz`; the live cache has many nested pages. Deleted OAI records are skipped rather than tombstoning prior state (`pipeline/harvest.py:54-60`). A completed query’s state is not marked complete, so rerunning can restart the query and append another numbered copy.

Raw pages/state writes are not atomic or hashed in a harvest-run manifest, dates and IDs are not validated, and `INSERT OR REPLACE` can erase fields. `pipeline/backfill.sh:11-23` still prints “backfill complete” and exits success after every chunk exhausts 20 failures.

Required: immutable harvest manifests, recursive reparse by manifest, tombstones, atomic response/state writes, boundary tests, validated IDs/dates, and nonzero automation exits.

### Targeted fetch and artifact identity

Version-pinned URLs and successful-byte hashes are strengths. The main version defect is unchanged: `pipeline/fetch.py:123-136` treats any prior success or 404 as terminal without comparing `files.version` to `papers.latest_version`. Later revisions will never be fetched automatically.

`fetch_one()` writes directly to a fixed paper path before the DB transaction (`pipeline/fetch.py:88-117`). A crash can leave partial/unledgered bytes; fetching another version can overwrite a path still referenced by an older artifact row. Files must be content-addressed/versioned and written temp → fsync → atomic rename before registration.

Other issues:

- `gzip.decompress(data[:65536])` misclassifies valid larger single-gzip TeX responses (`pipeline/fetch.py:37-50`).
- Unknown HTTP-200 bodies are stored as `ok_unknown_format`; the scanner now rejects them, but acquisition should not call them success.
- Bodies are loaded without a size limit; redirects/final host and Retry-After are not bounded.
- Overall fetch exits zero even when papers fail (`pipeline/fetch.py:157-167`).
- 404 should be version-specific/retryable when metadata changes.
- Artifact records do not snapshot the applicable arXiv license or verified effective version.

### Full-text scanner and privacy boundary

The no-filesystem-extraction approach, per-member limit, total selected-byte limit, timeout, and explicit unknown/incomplete item states are all useful.

Remaining correctness/resource defects:

- single-gzip data are fully decompressed before checking 200 MiB (`pipeline/scan.py:87-99`);
- outer blobs, tar header count, compression ratio, wall time, and open-tar cache are unbounded;
- large `.bbl`, `.def`, `.inc`, `.txi`, `.ldf`, or extensionless rendered-looking files are silently skipped because only `.tex/.ltx/.txt` produce a `skipped-large` note (`pipeline/scan.py:111-130`);
- comment stripping mishandles `%` after an even number of backslashes and does not model nested conditionals, `\verb`, or TeX inclusion semantics;
- every plausible TeX-like residual file is scanned without a rendered include graph, contrary to the privacy default;
- ancillary filenames are treated as evidence without rendered verification and can themselves contain adversarial text;
- bulk PDF members are deliberately skipped; and
- `pdf_to_text()` trusts a nonempty sibling cache by path, not PDF hash/version/extractor identity (`pipeline/scan.py:145-154`).

Use a streaming bounded archive reader, explicit member inventory, include/render graph or compiled-PDF evidence policy, and sandboxed content-addressed PDF extraction.

### Classifier

The ID mapping, taxonomy enums, confidence range, quote requirement, retry, durable error rows, full-ish input hash, model option, and per-paper batching option are material improvements.

The validator is still not as strict as its documentation:

- missing arrays/location/flags are accepted through defaults;
- overlong strings are silently truncated rather than rejected (`pipeline/classify.py:193-200`);
- `bool(v)` accepts non-booleans and turns string `"false"` into true (`pipeline/classify.py:222-228`);
- model names remain on non-author-use labels even when other usage fields are cleared;
- an ungrounded author-use quote is still `status='ok'`; grounding is merely a later optional gate; and
- tools/models are not checked as substrings/evidence spans.

`merge_snippets()` still associates all hit IDs/terms in a cluster with only the longest one of their contexts (`pipeline/classify.py:77-104`), so some linked evidence may never have been sent to the model. Build a union window or separate snippets with exact spans.

Resume checks scan set/prompt/model/taxonomy/isolation but not starting code commit or recorded parameters (`pipeline/classify.py:388-407`). Non-isolated output depends on neighboring snippets, while the per-snippet hash omits batch composition. Exact raw response text is logged in an ignored JSONL, but the DB `raw_response` stores only the parsed label object, contrary to schema comments.

Require a JSON Schema with literal types/required fields, exact evidence spans, immutable request IDs and full batch/prompt hashes, safe backend isolation, and a non-optional release policy.

### Render-truth checks

The exact/dehyphenated matching, TeX argument handling, short-quote rejection, fallback sources, timeout, hashes, and append-only check rows are thoughtful improvements.

Remaining issues:

- there is no render-check run/protocol manifest for matcher version, threshold, code commit, PDF extractor version, completion, or input set;
- a fuzzy score ≥0.80 is immediately `rendered`, although `CROSSCHECK.md` says fuzzy cases require review;
- cached PDF/text is trusted by path/nonzero size rather than stored hashes and extractor identity;
- non-404 client responses can collapse into a terminal no-PDF result;
- “every anchor occurrence” is capped at 20 (`pipeline/render_check.py:124-135`);
- native PDF parsing is not sandboxed or output-bounded; and
- redo mutates the effective classification status, changing live release inputs.

Treat fuzzy as `needs_review`, give render checks their own immutable run/item records, bind all caches to hashes/tool versions, and make releases reference exact check IDs.

### Reporting and release generation

The selected-run denominator, date frame, version strata, scoped downstream tables, escaping, explicit raw-rate label, and membership hashes are all good directions.

In addition to the P0 contract findings:

- `files` status is collapsed through a dictionary with potentially both src and PDF rows, so one row can overwrite another nondeterministically (`pipeline/report.py:156-160`).
- the frame comes from mutable latest paper metadata rather than release membership;
- paper rollup is paper-ID rather than paper-version keyed;
- human annotations never affect labels or estimates;
- release IDs do not protect output paths from overwrite;
- no atomic write is used; and
- Markdown escaping still permits model-created links/images/social engineering. Prefer canonical machine data and render controlled vocabulary labels only.

### Site generator

The static, tracker-free architecture is a strong product/privacy choice. The source-level escaping and table additions are good.

Remaining problems:

- it reads a large static `site/dashboard.html` whose submission series is not generated anywhere in the repository and ends 2026-08-08, despite copy saying “to today” (`pipeline/build_site.py:276-305`, `pipeline/sitetext.py:97-100`);
- brittle string assertions/replacements depend on the literal obsolete `142` template;
- it builds from live run IDs, not a release;
- it defaults evidence gates off and permits partial/unpinned runs;
- it omits pending/classification-failure and source-version-stratum displays;
- weekly edge selection is data-dependent;
- set iteration plus `Counter.most_common()` makes tied output order nondeterministic (`pipeline/build_site.py:171,198-220`);
- `CATLBL` retains removed `ideation_conjecture` and omits new v2 categories (`pipeline/build_site.py:127-133`);
- location copy says one per paper although code counts multiple;
- empty/thin/zero-positive cohorts crash;
- writes are non-atomic; and
- the ZIP is not generated or checked by the build.

Generate both submission and disclosure data from one release, sort all output canonically, use a deterministic packager (`SOURCE_DATE_EPOCH`, normalized paths/modes/timestamps), test zero/sparse/hostile values, and deploy only an allowlisted artifact.

### AWS/bulk acquisition and operations

The official requester-pays path, upstream MD5 verification, persistent monthly handles, and local two-way importer gate materially improve feasibility.

The remote producer remains fail-open and crash-unsafe (`pipeline/aws/filter_remote.py:23-74`): failed downloads/checksums are skipped, output is appended to open tars, only user-space flush occurs before `done.txt`, and the script still prints `ALL DONE`/exits zero. A crash can duplicate or truncate members. It ignores manifest size, has no AWS CLI timeout/disk/member/cost bound, and produces no durable full ledger.

The importer has no tests, reads each member fully, can crash on malformed `math_*.tar` names, says `registered: true` even when registration was refused, discards the full member ledger from the report, and records effective version NULL. `INSERT OR IGNORE` into `files` also leaves a prior src 404 row in place, making a newly registered S3 source artifact invisible to `corpus_jobs()`.

`pipeline/aws/README.md` references a nonexistent `provision.sh` and calls the present importer pending. `sync_home.sh` validates counts rather than hashes, uses a personal key path, and leaves termination manual. There is no tracked IAM policy, instance profile, IaC, IMDSv2/EBS/region/account check, budget alarm, logging/metrics, incident path, or automatic teardown.

Produce content-addressed closed per-chunk shards, close/fsync/hash before a durable done record, fail nonzero on any gap, and preserve a signed acquisition manifest. Define the whole cloud lifecycle as least-privilege idempotent code, with encrypted storage, budgets/alarms, and automatic termination.

### Tests, packaging, CI, and clean-clone reproducibility

Seventy passing fixture tests are a substantial step. The tests are strongest around pure lexicon/taxonomy/matcher functions and a tiny report fixture.

Missing coverage includes:

- fetch/redirect/body/version/404/atomic-write behavior;
- OAI deletion/resumption/reparse/recovery;
- archive bombs, member inventory, even-backslash comments, residual render graph, PDF cache identity;
- classifier subprocess boundary, literal JSON types, multiple runs, partial snippets, resume across code/parameter changes;
- annotation manifest/injection/idempotency/adjudication/estimators;
- render-run completion/cache/redo/fuzzy review;
- S3 producer/importer crash recovery;
- release reconstruction and tamper detection;
- site zero/sparse/hostile/accessibility cases; and
- a clean-clone end-to-end fixture build.

`.github/workflows/ci.yml:1-17` claims “tests + site build” but runs tests only. The action revisions are commendably SHA-pinned. Add `permissions: contents: read`, timeouts/concurrency, Python 3.10–3.12 coverage, `pip install .`, lint/type/security/secret/license/SBOM checks, hostile fixtures, site/accessibility/link checks, migration upgrade tests, and byte-for-byte release/package reconstruction. Never expose corpus/cloud credentials to untrusted pull-request code.

`requirements.lock` pins the requests stack but not pytest, lacks hashes, and cannot identify Codex, pdftotext, SQLite, tar/PDF libraries, OS, or AWS CLI. `pyproject.toml` lacks license/authors/URLs/build-system/entry points. Add a reproducible environment/container and record the exact image/tool digests in releases.

The lock also retains `requests==2.32.3`. Requests’ official advisory marks versions below 2.32.4 affected by CVE-2024-47081, in which a specially crafted URL plus a trusted environment can select `.netrc` credentials for the wrong host. The project mostly constructs official fixed-origin URLs, which limits direct exposure, but follows redirects and inherits ambient request configuration. Upgrade to a current tested release and set `Session.trust_env=False` wherever ambient proxies/`.netrc` are not intentionally required. The newer `extract_zipped_paths` advisory does not affect standard Requests use and that utility is not used here; this is a dependency-hygiene finding, not evidence of a demonstrated credential leak. ([Requests release history](https://requests.readthedocs.io/en/latest/community/updates/), [official advisory](https://github.com/psf/requests/security/advisories/GHSA-9hjg-9r4m-mvj7))

## Documentation and plan consistency

The specifications contain many strong research instincts, but operational truth is spread across historical plans, current design, and aspirational ledger claims.

### README and runbook

`README.md` is honest but too small for a public code alpha and already stale. It says immutable provenance is absent even though a partial v2 spine exists, links review 2 as the current audit, and gives no installation, sample run, architecture, data boundary, supported platform, release verification, contribution, citation, license, or security instructions.

`WORKFLOW.md` is a useful start, but:

- says reports/site are functions of one scan and classification run although multi-run mixing is allowed;
- says legacy `files` is frozen while fetch/import/scan still write/read it (`WORKFLOW.md:79-81`);
- treats model pin/isolation and evidence gates as operator discipline rather than enforced release requirements;
- includes a placeholder `rsync` step; and
- has no publish/deploy/rollback/correction procedure.

### Ledger and historical plans

`LEDGER.md` is valuable as a work log, but several DONE claims describe source code rather than tested deliverables: complete HTML, release provenance, strict schema, scan completeness, immutable artifacts, and the gold workflow are partial. It correctly admits at `LEDGER.md:113-130` that the v2 rebuild, estimand, second reviewer, PDF-only support, site rebuild, and legacy result quarantine remain pending. Treat those admissions as the operative status.

`OVERNIGHT_PLAN.md` still instructs destructive legacy `tex-v1` reuse and an invalid recall estimator. Mark it prominently **superseded/historical** so an operator cannot follow it. Likewise, hard-disable or archive `arxiv_ai_ack_scan.py` and `pipeline/audit.py`; a runbook deprecation sentence is insufficient when executable paths still produce unsafe outputs.

### Research/design documents

- `DESIGN_PLATFORM.md:3-4` says almost nothing is implemented, now stale; elsewhere it treats IDs/derived labels as automatically legally publishable and leaves the canonical data home open.
- The promised public extracted-data layer, Parquet/CSV schema, chart specs, release assets, GitHub Pages deployment, and CI analysis path do not yet exist.
- `PITCH.md`/`pitch.tex` still say annotations will be open and promote a volunteer conversation-share-link workflow, conflicting with aggregate-only policy and the static/no-backend architecture.
- The pitch’s “precision and recall are known” language runs ahead of the current development checks.
- `PRIOR_ART.md` is a useful start but is an AI-assisted narrative survey, not a reproducible search. Add bibliographic records/DOIs, search databases/queries/dates, inclusion rules, archived source snapshots, claim-level citations, and periodic review. Replace “gap confirmed” with appropriately bounded novelty language until a systematic search and collaborator review are complete.
- `TAXONOMY.md` is thoughtful, but named paper examples and a single-reviewer 28/30 history conflict with aggregate-only public posture; the doc/code test checks names, not definition text.
- `CROSSCHECK.md` correctly calls AI passes kink-finding rather than ground truth. Its tool/network/read-only assumptions are not enforced by code, and its results need a distinct annotation namespace excluded from human validity estimates.

### Selective primary-source audit of prior-art claims

The prior-art bibliography was not exhaustively re-reviewed, but a selective check of primary sources found several material errors that should be corrected before circulating the pitch or methods as scholarly work:

- `PRIOR_ART.md:19-21` cites v1 of “Patterns and Purposes.” The current v2 explicitly says it corrects original data issues and reports **135 declarations among 8,633 articles**, ChatGPT at **73.3%**, readability at **57.8%**, and grammar checking at **19.3%**—not 168/8,859, 77%, 51%, and 22%. Cite an explicit version and maintain a literature-update date. ([primary source](https://arxiv.org/abs/2502.00632))
- `PRIOR_ART.md:38-40` names “Glynn”; the author is **Andrew Gray**. More importantly, that study uses shifts in LLM-associated keywords to estimate assisted writing; it is not a population study of explicit disclosures, so “<0.1% disclosure” is the wrong estimand. ([primary source](https://arxiv.org/pdf/2403.16887))
- `PRIOR_ART.md:85-89` and `TECH_NOTES.md:127-129` say Pangram claims roughly `1e-5` false positives “on held-out arXiv.” Its Table 6 reports **0.04% (`4e-4`) for held-out Scientific Papers** and **0.001% (`1e-5`) for News**; it does not identify the scientific-paper domain as arXiv. The current statement is a 40-fold numerical/domain misquotation. Also label this as a vendor-authored technical report, not independent validation. ([primary source](https://arxiv.org/html/2402.14873))
- `PRIOR_ART.md:116-119` and `TECH_NOTES.md:159-163` should describe ArxivMathGradingBench as **35 research papers containing 40 known errors**, not simply “35 items.” Its labels cover author-identified errors, so apparent false positives may include real but previously unknown errors. ([primary source](https://arxiv.org/html/2605.20531))
- `PRIOR_ART.md:25-28`, `PITCH.md:16-18`, and `pitch.tex:26` reduce the foundation-model study to “citation mining finds 1.3% use.” The paper classifies documented use/customization from in-text evidence and includes a broader foundation-model family, including vision models. Treat its mathematics result as a different operational measure, not generative-AI disclosure prevalence. ([primary source](https://arxiv.org/abs/2511.21739))
- The **81% of 816 respondents** in `PRIOR_ART.md:22-24` is reported correctly, but “survey evidence of the disclosure gap” overgeneralizes a self-selected sample: 107,346 verified authors were emailed, click-through was about 1.6%, and the final sample was 40% computer science and 79% men. Use it as respondent-reported attitudes/behavior, not a population denominator or quantitative disclosure-gap estimate. ([primary source](https://arxiv.org/html/2411.05025))
- `PRIOR_ART.md:136-138` and both pitches use a “20% above trend” claim backed only by a secondary OfficeChai article. Remove it or independently reproduce it from a versioned arXiv metadata query with code and uncertainty.
- `PRIOR_ART.md:150-152` should say that **27% of submission bytes/data on average** were unnecessary in the cited study, not imply that 27% of files or submissions were residual. This finding strengthens the need for a rendered-text boundary. ([primary source](https://arxiv.org/abs/2601.11385))
- Product announcements and LinkedIn posts (such as alphaXiv/Pangram) may establish product existence, but should be separated typographically from preprints, peer-reviewed evidence, and independently reproduced results.
- Licensing must be artifact-version-specific: arXiv states that different versions of one work can carry different licenses. A paper-level license field is insufficient. ([arXiv licensing guidance](https://info.arxiv.org/help/license/index.html))

Other sampled numerical claims—including the Kousha acknowledgement study, Nature word-frequency result, 124,461-paper direct precedent, medical disclosure/detector comparison, and selected error-audit figures—were consistent with the checked sources subject to the estimand caveats already noted. NBER, RAID, and bioRxiv references were not all independently accessible during this pass; do not call the bibliography fully verified. Create a claim ledger containing source version, access date, exact supporting table/section, project paraphrase, and reviewer status.

Separate the repository into:

1. a versioned/preregistered protocol and estimand;
2. stable operator/release documentation;
3. clearly archived hackathon plans and legacy outputs; and
4. future-study concept notes that cannot be confused with implemented functionality.

## Ethics, legal, privacy, and governance

The ethical framing is stronger than average for an early prototype, particularly the separation of explicit disclosure, detector inference, and error auditing; the aggregate-only intent; and the warning against misconduct narratives. Implementation must now match that framing.

### Required before any public release

1. **Institutional determination.** Obtain research-ethics/data-protection/legal review or a written exemption determination. Public source does not eliminate professional/reputational effects, default-license restrictions, or third-party processing duties.
2. **Data inventory and minimization.** Document why authors, submitter, source snippets, model responses, reviewer identities, IP/infra records, and artifacts are collected; who can access them; retention/deletion; encryption/backups; and incident response. `submitter` appears unused and may be unnecessary.
3. **Vendor protocol.** Document model provider, terms, subprocessor/retention/training settings, transfer location, legal basis, approved content boundary, and deletion process. Full-paper agent audits are especially difficult to justify.
4. **Publication policy.** Specify aggregate-only schemas, minimum cells, no per-paper detector/error flags, whether human-verified self-disclosures ever appear row-level, author correction/appeal/takedown, and correction versioning.
5. **Reviewer governance.** Training, expertise matching, conflicts/recusal, compensation, confidentiality, withdrawal, adjudication, and quality monitoring.
6. **Security/privacy controls.** Least privilege, separate corpus/analysis/publish environments, encryption/ACL verification, audit logs, secret management, backup restore drills, incident reporting, and data deletion.
7. **Licensing.** There is no tracked `LICENSE`, data/document license, NOTICE, or rights manifest. A plan to use ODC-BY grants nothing. License project code explicitly, license only derived data the project has authority to license, and never redistribute arXiv full text/default-license material.
8. **Governance files.** Add `SECURITY.md`, `CONTRIBUTING.md`, code of conduct, `CITATION.cff`, correction policy, privacy/methods statement, release changelog, and maintainer/reviewer roles.

The ignored DB and backup report mode 0777 on this DrvFS workspace. Unix mode bits may not represent Windows ACLs, so do not infer either safety or exposure from that number; verify actual host/share ACLs and encryption before involving collaborators or cloud compute.

The name/disclaimer improvement is helpful, but obtain brand guidance for “ArxivObservatory”/arXiv visual identity before launch.

### Future high-risk functions

The volunteer share-link service in `PITCH.md:69-75` conflicts with the static architecture and would introduce authentication, consent/withdrawal, copyrighted paper/prompt content, account metadata, provider terms, malicious URLs/SSRF, malware, moderation, and retention. Prefer structured reviewer attestations and never build a generic server-side share-link fetcher without a separate threat model and approval.

OpenAlex-based author/affiliation/career-age productivity work also requires a separate identity-resolution, fairness, privacy, and causal-inference protocol. WP2 detector inference and WP3 error judgments must remain permanently separated from disclosure labels and governed as higher-harm studies.

## Public product, communication, and reach

The current visual design is compact, legible, tracker-free, and potentially effective. The best route to reach is credibility-first, not a more dramatic headline.

After scientific release gates pass, publish:

- a landing page that leads with the precise estimand, release ID/date, coverage, human-validation result, and “what this does not measure”;
- stable Methods, Data, Validation, Limitations, Corrections, About/Contact, Citation, and Changelog pages;
- downloadable aggregate chart data and schema with checksums/DOI;
- complete numerator/denominator/missingness/tooltips and accessible tables for every chart;
- version-stratified and measurement-error-aware trends;
- shareable URLs and static social cards that include the caveat/release ID;
- canonical/OG/schema metadata, favicon, sitemap/robots, repository/data links, and correction contact;
- keyboard/touch/screen-reader support, semantic landmarks, focus styles, narrow-phone layout, high-contrast/reduced-motion checks, and manual accessibility review; and
- privacy-preserving, optional aggregate analytics only if there is a concrete outreach question.

Do not use “small fraction” for unmeasured classifier error (`pipeline/sitetext.py:40-43`). Do not make a noisy subfield leaderboard the primary public view. Optimize success for reproducible reuse, expert participation, citations to a validated release, correction responsiveness, and trust—not page views alone.

The current site still uses several `innerHTML` paths for submission controls/tooltips/tables. Current inputs appear controlled, so this is not an observed stored-XSS exploit today, but DOM construction should be used consistently before future contributor-controlled chart specs/data. Add a strict deployment CSP/headers policy and avoid third-party runtime dependencies.

CSV should not be the canonical expressive export. A tracked legacy CSV contains a cell beginning with `=`, which spreadsheet software can interpret as a formula even when CSV-quoted. Use JSON/Parquet canonically and generate a separately tested spreadsheet-safe CSV that neutralizes leading `=`, `+`, `-`, and `@` after whitespace/control characters.

## Prioritized implementation roadmap

### Gate 0 — Stop legacy publication now

- Keep the current numerical site and ZIP private, or replace them with clearly synthetic data.
- Move `dashboard.html` out of the publish root.
- Remove/quarantine tracked per-paper snippets/labels and assess Git history.
- Add hard-fail guards to legacy scanner/audit/report paths.
- Mark `OVERNIGHT_PLAN.md`, legacy reports, and historical outputs superseded.

**Acceptance:** a public-tree allowlist contains no real paper-level expressive data and no legacy headline; package inspection confirms it.

### Gate 1 — Make artifact and run identity real

- Store immutable content-addressed artifacts at versioned paths with effective/requested version, source channel, license, byte count, hash, retrieval manifest, and derived-file identities.
- Make scan items reference artifact IDs; introduce a new run-bound hit/evidence schema.
- Validate upstream terminal state before classification begins.
- Make run completion a reconciliation over an immutable expected-input manifest.
- Prevent unsafe terminal-state mutation/supersession in schema/application code.

**Acceptance:** a crash/retry/version-refresh test cannot overwrite history, duplicate NULL identities, orphan evidence, or mark an incomplete run complete.

### Gate 2 — Establish the safe processing boundary

- Stream/cap downloads and archive expansion; validate IDs/paths/redirects/hosts.
- Inventory members and rendered inclusion; record every skip.
- Bind PDF text to PDF hash and extractor/container digest; sandbox native parsers.
- Use non-agentic structured output or an empty-root, no-credential, one-paper isolated model worker.
- Require literal JSON Schema and exact evidence spans.

**Acceptance:** malicious archive, PDF, TeX prompt, Markdown packet, oversized response, path, and CSV fixtures fail safely without cross-paper/repository disclosure.

### Gate 3 — Implement one immutable end-to-end v2 release candidate

- Decide/preregister v1 fixed-lag versus fixed-follow-up estimand.
- Import/fetch the exact cohort and reconcile all acquisition states.
- Run one clean scan protocol, pinned isolated classification, immutable render-check run, and release materialization.
- Export a deterministic release snapshot plus report/site/package from `release_id` only.
- Verify from a clean clone/container and compare bytes.

**Acceptance:** every numerator item traces to one cohort paper-version, artifact hash, scan item/hit, classification request, grounded/rendered evidence check, and protocol identity; coverage states partition the frame exactly.

### Gate 4 — Complete the human gold study and estimator

- Freeze signed assignments against the release.
- Conduct two independent version-pinned reviews, with a genuinely blind negative full-paper arm.
- Adjudicate all disagreements and record conflicts/training.
- Implement design-weighted estimates, intervals, missingness bounds, and axis-level reliability.
- Keep development/calibration data separate from the locked evaluation set.

**Acceptance:** a preregistered analysis produces reproducible precision/false-omission/sensitivity/prevalence estimates with uncertainty and reviewer-flow accounting; no AI cross-check is used as ground truth.

### Gate 5 — Public scientific/data/site release

- Enforce validation, clean code/tool identities, evidence gates, coverage policy, and release schema in the publication command.
- Publish deterministic aggregate data, methods, limitations, validation, correction policy, license, citation, checksums, and DOI.
- Add CI rebuild/drift/accessibility/security checks and a protected Pages deployment with rollback.
- Deploy only the allowlisted release artifact, never the source template/tree.

**Acceptance:** the deployed bytes match the signed release manifest and a clean-clone rebuild; every public number maps to released aggregate data and validation metadata.

### Gate 6 — Scale and broaden only after Gate 5

- Add daily incremental manifests, monitoring, alerts, budgets, backups/restore, and automatic cloud teardown.
- Extend time coverage to support the stated longitudinal question.
- Validate CAS/prover/code instruments separately.
- Treat WP2, WP3, productivity, and community functions as new studies with new approval gates.

## Suggested immediate issue list

If only the next ten issues are opened, use these:

1. **Remove/replace legacy real-result site, ZIP, dashboard fragment, and paper-level outputs.**
2. **Make scan-run completion and release freeze independently reconcile all expected item states.**
3. **Eliminate multi-scan numerator leakage; bind each classification to one selected scan item/artifact/version.**
4. **Materialize deterministic releases and make report/site/package consume `release_id` only.**
5. **Decide and preregister the paper-version/follow-up estimand.**
6. **Bind gold sampling/packets/ingest to a signed release and implement adjudication/estimators.**
7. **Replace or truly isolate the agentic Codex boundary; enforce isolation/model/evidence gates in publication.**
8. **Make fetch/artifact/derived-text storage content-addressed and revision-aware.**
9. **Bound archive/network/PDF work and repair AWS/OAI/backfill fail-open recovery.**
10. **Add LICENSE, public README/setup, governance/security/privacy/correction docs, full CI/release/deploy reconstruction.**

## Repository-wide file disposition

| Area | Recommendation |
|---|---|
| `pipeline/{db,migrate,runs}.py` | Retain and strengthen with artifact/run FKs, state invariants, exact schema compatibility, immutable release tables/triggers |
| `pipeline/{harvest,fetch}.py`, `backfill.sh` | Retain after recursive manifests, tombstones, version refresh, bounded/atomic I/O, failure exit fixes |
| `pipeline/{scan,scan_meta,lexicon}.py` | Retain v2 direction; add rendered member inventory, streaming bounds, cache identity, complete run reconciliation, separate tool-family validation |
| `pipeline/{classify,taxonomy}.py` | Retain structured taxonomy; replace/isolate agentic backend, enforce literal schema/evidence spans/full request identity and release requirements |
| `pipeline/render_check.py` | Retain concept; add immutable run protocol, exact cache/tool binding, fuzzy-review state, sandbox |
| `pipeline/annotate.py`, `GOLD_STUDY.md` | Retain design; rebuild packet/ingest identity boundary, release/cohort/version binding, blinding/adjudication/estimation |
| `pipeline/report.py` | Retain selected-run/version-stratum work; fix coverage partition, unresolved outcomes, multi-run leakage, human correction, snapshot-only build |
| `pipeline/build_site.py`, `sitetext.py` | Retain static/privacy approach; rebuild from release, generate all data, deterministic/sparse-safe/accessibility-tested output |
| `pipeline/aws/*` | Retain importer/S3 direction; replace producer with crash-correct shards/ledger and complete least-privilege IaC/lifecycle |
| `pipeline/audit.py`, `arxiv_ai_ack_scan.py` | Hard-disable/archive as historical or fully port to v2 and safe boundary; do not leave supported executables |
| `results/*`, current `reports/report.md`, `reports/awesome_validation.*` | Remove from public deliverables; preserve only in restricted historical storage if justified |
| `site/*`, `dist/*` | Withhold/replace now; later generate deterministically from validated release and deploy allowlisted bytes only |
| `PITCH.md`, `pitch.tex`, `TECH_NOTES.md`, `PRIOR_ART.md`, `DESIGN_PLATFORM.md` | Keep, but separate registered decisions from concepts; correct validation/open-data/community claims and add reproducible citations/status |
| `README.md`, `WORKFLOW.md`, `LEDGER.md` | Expand/correct; make one source of operational truth and clearly mark historical documents |
| tests/CI/package files | Strong start; add integration, hostile-input, release, site, ops and reproducibility coverage plus real lock/tool environment |
| `.claude/docs/lean4`, `.claude/tools/lean4` | Unrelated to this project; remove/relocate or document provenance, license, ownership, and security purpose |

## Final assessment

The repository has advanced materially since iteration 2. The new work addresses the right abstractions: observation is an item state, evidence needs normalized lineage, source version matters, model output is not ground truth, rendered text is the ethical oracle, and public releases need provenance. The 70 passing tests show that these ideas are beginning to become executable software.

The remaining problem is no longer simply “add tests and caveats.” It is to make the guarantees compose. Today, each stage contains pieces of the right contract, but the seams still permit incomplete scans, cross-run labels, mutable release inputs, unsafe model/annotation boundaries, and publication of stale legacy bytes. The live system has not yet produced one v2 classification or release, so scientific readiness cannot be inferred from architecture alone.

Complete one narrow, clean, version-pinned, human-calibrated release from acquisition manifest through deployed bytes. If that release can be independently reconstructed, audited, corrected, and explained without relying on the legacy 16.1% result, ArxivObservatory will have crossed the important threshold from a compelling prototype to a credible public metascience instrument.
