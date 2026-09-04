# Complete repository re-review: ArxivObservatory

**Review date:** 2026-08-10

**Reviewed snapshot:** `46b0060` on `main`, with a clean working tree at the final inspection. The branch advanced from `ac27fc8` to `46b0060` while this review was in progress; the last commit, which makes the AWS filter keep output tar handles open, is included here.

**Relationship to the first review:** this is a fresh, self-contained review of the current repository and live local state, not merely a comment on `review_codex.md`. The earlier review remains useful history. This document explicitly distinguishes fixes, partial fixes, unresolved findings, and new regressions.

**Scope:** all tracked source, specification, planning, report, result, site, distribution, AWS, and auxiliary files; recent Git history; the ignored live SQLite database and its cross-stage relationships; proposed future functions, research work packages, community workflow, public interface, and deployment model. No external service, model, corpus, or EC2 state was mutated.

## Executive verdict

Claude made meaningful progress. The project now has a generated single-page site, a nearly complete July–early-August full-text acquisition, explicit fetch-failure and pending columns, created-date cohorting, raw-rate wording, a 200-paper negative audit, an external-list cross-check, and a much faster official-S3 bulk acquisition path. The site is visually strong, compact, aggregate-facing, tracker-free, and far more legible than the earlier dashboard. The current database also passes SQLite integrity checks.

The central scientific result is nevertheless **not publication-ready**. The public site says that 1,038 of 6,429 papers, or 16.1%, “disclose AI assistance,” that all papers were evaluated, and that scanner recall is about 98%. The implementation cannot support any of those statements as written:

- A successful download is renamed “full-text scanned,” although the database has no per-paper scan-completion or scan-error ledger.
- Reports consume all historical classifier rows rather than one immutable run/model/version/protocol snapshot.
- Destructive rescans have already orphaned 765 stored evidence references. Of the 1,038 headline-positive papers, 104 have no surviving author-use evidence reference.
- The classifier is an unpinned, agentic Codex subprocess. It has no closed response schema or quote-grounding check. Even among classification rows whose referenced hits still exist, 464 promised “verbatim” quotes do not occur in any referenced context.
- The 200-paper audit currently contains two machine-positive rows, not the one claimed by the site; one of those two is self-contradictory and explicitly says the paper contains no generative-AI/LLM disclosure.
- A negative-sample miss fraction is not recall by itself. With 2/200 machine-flagged audit cases, the simple plug-in sensitivity illustration for the current headline frame would be about 95%, with a very wide interval—not 98%—and even that calculation would be invalid without human adjudication and proven scan completion.
- The cohort is defined by first-submission date but uses the latest version available at fetch time. In the headline cohort, 653 of 6,429 artifacts are versions later than v1, producing revision and follow-up-time bias.
- The human-labelled pilot contains only 20 selected development candidates, and the external list is a list of AI-for-mathematics papers rather than a disclosure gold standard. Neither estimates population precision.

**Release recommendation:** keep the site private or label it unmistakably as an unvalidated engineering prototype. Do not promote 16.1%, the July/August difference, the subfield ranking, the 98% recall claim, or any tool/epistemic-impact counts as findings. Do not publish the tracked paper-level excerpts or automated result-bearing labels. A public code alpha can follow repository sanitization, licensing, security documentation, and an honest README. A public scientific-data/site alpha should wait for an immutable rebuild and representative human validation.

The best path remains to make one narrower product excellent: a version-explicit, human-calibrated observatory of **author-reported assistance visible in specified public paper versions**. WP2 detector inference, WP3 error auditing, productivity claims, and conversation-sharing should remain separately governed future studies.

## Decision summary

| Area | Current state | Decision |
|---|---|---|
| Scientific concept | Strong and unusually thoughtful separation of estimands | Preserve; narrow the first release to validated WP1 |
| 16.1% headline | Raw mutable model output over an unproven denominator and mixed versions | Withdraw from public-facing use |
| July/August trend | 39-day exploratory window, partial early August, measurement error and revision bias | Do not describe as a trend |
| Validation | Useful development checks, but no representative human gold set or valid recall estimator | Blocks scientific claims |
| Provenance | Materially corrupted by destructive rescans and unscoped rollups | Blocks any data release |
| Paper-version design | Still paper-keyed in files, reviews, reports, and caches | Blocks the declared longitudinal estimand |
| Site | Visually effective prototype; misleading hierarchy, unsafe generated markup, weak semantics | Demo-only pending rebuild |
| AWS backfill | Official channel and good throughput; crash-unsafe, fail-open, unreproducible, not integrated | Do not treat outputs as a trusted corpus yet |
| Security/privacy | Agentic prompt-injection path, stored-XSS path, expressive-text leakage, no governance package | Blocks public automation/data |
| Deployment | Static architecture is appropriate; no CI, lock, build contract, hosting config, runbook, or rollback | Not deployable reproducibly |
| Public reach | Strong topic and visual hook; lacks trust, citation, correction, methods, and accessibility foundations | Build reach after credibility gates |

### Severity convention

- **Blocker:** must be resolved before the affected public release or study claim.
- **Critical:** can invalidate a central result or irreversibly compromise provenance.
- **High:** likely to cause material scientific, ethical, security, or operational failure.
- **Medium:** important for maintainability, interpretation, accessibility, or scale.

## What changed since `review_codex.md`

### Changes that are genuine improvements

1. **Cohorting uses `papers.created`.** `pipeline/report.py:72-77` now uses the v1 creation date rather than inferring date from the arXiv identifier.

2. **Missing downloads are no longer silently counted as negatives.** `pipeline/report.py:78-109` exposes failed/unfetched strata and a pending column. The intent is correct even though “downloaded” is still incorrectly equated with “scanned.”

3. **Public rate wording is less absolute in one place.** The report calls the number a “raw classifier-positive rate” (`pipeline/report.py:99-109`).

4. **The public-facing site is aggregate-only.** `pipeline/build_site.py` does not render paper rows, and `site/data/disclosures.json` contains aggregates. This is a good default.

5. **Small subfield cells are partly suppressed.** `pipeline/build_site.py:156-162` requires at least 100 papers before displaying a subfield.

6. **The site has a real local generator and a consistent distribution archive.** `pipeline/build_site.py` writes `site/index.html` and the disclosures JSON. The checked ZIP contents match the tracked site files.

7. **The site presentation improved substantially.** The combined submissions/disclosure page has coherent typography, responsive grids, dark-mode variables, hover explanations, a table option for the submission series, and no tracking scripts.

8. **Targeted fetching remains polite and content-hashed.** `pipeline/fetch.py:63-105` requests an explicit version and records SHA-256.

9. **OAI harvests now use per-query archive directories.** `pipeline/harvest.py:138-169` reduces state collision between overlapping harvests.

10. **Several narrow parser fixes landed.** URL-like arguments are partly protected during comment stripping; extra TeX-looking members are sniffed; spaced “Open AI” and hyphenated “language-model” variants were added; malformed classifier JSON gets one retry; the full-paper audit retains a tail slice; and the awesome-list parser refuses implausibly tiny parses.

11. **The AWS path uses the official bulk channel and validates the upstream MD5.** `pipeline/aws/filter_remote.py:33-49` uses requester-pays S3 and compares each downloaded chunk with its manifest MD5. Persistent output handles remove the prior O(n²)-like append/reopen cost.

12. **The current local database is structurally readable.** `PRAGMA quick_check` succeeds; Python sources parse; JSON artifacts parse; and shell syntax checks pass.

### Earlier findings that are only partially addressed

| Earlier issue | Current status | Why it is not closed |
|---|---|---|
| Wrong report denominator | **Partial, still a blocker** | Full frame is no longer used, but successful fetch is falsely treated as completed scan. |
| Created-date cohort | **Fixed locally** | Report window is still hard-coded, `--months` is ignored, and source version is not aligned with v1 date. |
| Fetch failure stratum | **Partial** | Twenty 404s are shown, but unknown/unprocessed/scan-error states remain unobservable. |
| Raw-rate labelling | **Partial** | Method text says raw, while the largest tile and heading assert that papers “disclose AI assistance.” |
| Pending classification | **Partial** | Pending is computed against an unscoped historical rollup; stale labels can make a current item appear complete. |
| URL/comment fix | **Partial** | The regex is not a TeX lexer and still mishandles escaping, verbatim constructs, nested braces, and rendered-file selection. |
| Content sniffing | **Mixed** | It finds some extensionless TeX but expands scanning into residual files, contrary to the stated privacy default. |
| Classifier ID mapping | **Partial** | Missing/bad IDs still fall back to array position at `pipeline/classify.py:153-160`. |
| Classifier retry | **Partial** | Only JSON parse failure retries; schema, length, ID, quote, model, and transport failures remain fail-open. |
| Audit head/tail sampling | **Partial** | It still drops the middle, scans residual members, lacks version/run cache identity, and treats a model as truth. |
| External parser fail-loud | **Partial** | Row-count sanity improved, but source revision/provenance and construct validity remain absent. |
| Aggregate-only public policy | **Partial** | The site is aggregate-only, but tracked `results/` and new `reports/spotcheck_result_bearing.md` still publish per-paper labels and excerpts. |
| Static site plan | **Partial** | A generator exists, but there is no reproducible clean-clone build/deploy/release contract. |

### Regressions or newly exposed failures

1. **Evidence corruption has grown.** The first review found 82 missing hit references across 28 classification rows. The current database has 765 missing references across 268 classification rows and 173 papers. All evidence references are gone for each affected row.

2. **A polished but invalid scientific headline is now the dominant public message.** `site/index.html:129,156-164` elevates 16.1% and ≈98% recall before explaining that any labels are automated. The caveat at `site/index.html:174-175` applies only to “fine-grained splits.”

3. **New paper-level sensitive output was added.** `reports/spotcheck_result_bearing.md:1-153` names 30 papers, prints model-generated high-impact labels and excerpts, and leaves every human verdict blank.

4. **The validation copy is already stale.** The database has two audit positives; `pipeline/sitetext.py:34-38,104-106` and the generated site say one.

5. **Latest-version text is mixed into a v1-date analysis.** Of 6,429 successfully fetched artifacts in the headline cohort, 653 are later than v1. Across all successful fetched files, 668 are later than v1.

6. **The AWS performance optimization enlarges the crash-consistency window.** Output tar streams now remain unclosed throughout the run, but chunks are marked done after only a user-space flush.

7. **Infrastructure inventory is tracked.** `pipeline/aws/instance.txt` contains an EC2 instance ID and public IP. It is not a secret, but it is unnecessary, likely stale, and operationally unsafe to publish.

## Inspection snapshot and empirical integrity checks

The following is a read-only snapshot, not a release manifest:

| Object | Count |
|---|---:|
| Papers | 235,342 |
| Version rows | 418,232 |
| File rows | 6,590 |
| Successful file rows | 6,570 (`6,517` source; `53` PDF-only) |
| Explicit 404 file rows | 20 |
| Scan hits | 21,942 |
| Snippet classifications | 3,344 across 1,969 papers |
| Full-paper negative-audit rows | 200 |
| Human-review rows | 20 |
| Classification evidence references | 9,608 |
| Missing evidence references | 765, affecting 268 rows / 173 papers |
| Live-reference rows whose quote is not in any referenced context | 464 |

For the hard-coded public cohort, math-primary papers created 2026-07-01 through 2026-08-08:

| Quantity | Count |
|---|---:|
| Frame | 6,449 |
| Successful download, called “scanned” by the application | 6,429 |
| Source | 6,378 |
| PDF-only | 51 |
| 404 | 20 |
| Scanner-flagged in selected runs | 1,355 |
| Model rollup `author_use` | 1,038 |
| Unflagged | 5,074 |
| Fetched artifact later than v1 | 653 |
| Headline positives with no surviving author-use evidence | 104 |

The application reports zero pending items because it subtracts every historical paper classification from current flagged papers (`pipeline/report.py:88-90`). That is not a completion audit. A stale classification can “complete” a new scan even when its evidence has been deleted.

The classifier prompt requires the shortest verbatim supporting quote (`pipeline/classify.py:66-70`). Of the 3,344 snippet rows, 268 have entirely orphaned evidence and another 464 have live references but no exact quote match. Thus 732 rows cannot currently satisfy the prompt’s own evidence contract.

The database currently has zero file rows stale relative to each paper’s latest harvested version. This is an accidental snapshot property, not an invariant: `pipeline/fetch.py:111-124` permanently skips any previous successful source/PDF or 404 without comparing its version with `papers.latest_version`.

## Launch blockers

### LB-01 — The 16.1% result has neither a valid denominator nor a validated numerator

`pipeline/report.py:78-82` and `pipeline/build_site.py:135-138` call every successfully fetched source/PDF “scanned.” The schema has no scan attempt/completion table (`pipeline/db.py:18-98`). `pipeline/scan.py` stores hits but no durable record for a successful no-hit scan, parse failure, member skip, timeout, or extractor error. No hit can therefore mean a true negative, an unprocessed paper, a failed scan, or a scanner that silently skipped relevant content.

The numerator is a single unpinned model’s `author_use` label, not a human-confirmed disclosure. The site’s main tile removes “raw classifier-positive” wording and states that the papers disclose assistance (`pipeline/build_site.py:191-199,230-232`). This is materially misleading.

**Required fix:** derive numerator and denominator only from one frozen `analysis_release`. Each paper-version must have a successful immutable fetch, successful scan item, completed classification decision, protocol/model identity, and evidence-integrity status. Public copy must say “automatically classified as containing an author-reported disclosure” until validated estimates are available.

### LB-02 — Destructive rescans have broken the evidence chain

`pipeline/scan.py:136-138` and `pipeline/scan_meta.py:19-23` delete all hits for a reused run name. Classifications retain hit IDs only in opaque JSON (`pipeline/classify.py:167-170`), with no foreign key or normalized evidence table (`pipeline/db.py:60-88`). Reports then consume those stale classifications indefinitely.

This is not theoretical: 765 of 9,608 references are missing, and 104 of 1,038 headline positives have no surviving author-use evidence. The result can no longer be audited from the current database.

**Required fix:** never mutate or reuse a run. Create UUID/content-addressed scan runs and immutable hit IDs; normalize classification-to-hit/span relations with foreign keys; stage run items; publish only after a completeness/integrity transaction; supersede rather than delete. Rebuild all derived labels from source artifacts after migration.

### LB-03 — The repository still cannot represent the declared paper-version unit

The specifications correctly declare paper-version as the unit (`TECH_NOTES.md:22-25`), but:

- `files` is keyed by `(arxiv_id, kind)`, so later versions overwrite history (`pipeline/db.py:48-58`).
- `human_review` is keyed only by `arxiv_id` (`pipeline/db.py:90-97`).
- reports and the site roll up on paper ID only.
- audit rows omit version and hash only the paper ID (`pipeline/audit.py:133-140`).
- targeted fetch skips prior successful rows even when a later version appears (`pipeline/fetch.py:111-124`).
- PDF text caching is keyed only by sibling path, not source hash, PDF version, or extractor (`pipeline/scan.py:110-119`).

The current headline makes the specific design error the documents warn against: it cohorts by v1 date but reads latest-at-fetch text for 653 later-version artifacts. This is differential across the displayed periods: 607/5,346 July artifacts (11.4%) are later than v1, compared with 46/1,083 early-August artifacts (4.2%). Older papers have had more opportunity to add a disclosure, so the monthly comparison is biased even if every scan and label were otherwise perfect.

**Required fix:** key artifacts, derived text, scans, classifications, annotations, and evidence by `(arxiv_id, version, artifact_sha256, protocol_id)`. Choose and preregister either v1 prevalence, fixed-lag latest-version prevalence, or a version-history estimand; do not mix them.

### LB-04 — Validation and the ≈98% recall claim are invalid

The site’s recall claim fails in four ways:

1. The database has two machine positives among 200 audit rows, while the site hard-codes one.
2. One of the two positives is self-contradictory: its own notes say there is no generative-AI/LLM disclosure, while `disclosure_found` is true for ordinary neural-network methodology.
3. An LLM re-read is a second retrieval system, not ground truth, exactly as `TECH_NOTES.md:98-103` says.
4. The miss proportion among sampled negatives is not recall. Sensitivity requires estimated false negatives relative to true positives, with uncertainty and sampling weights.

As an illustration only, 2/200 gives a 1.0% machine-flag rate with a Wilson 95% interval of roughly 0.27%–3.57%. Applying that mechanically to 5,074 headline unflagged papers and 1,038 positives gives a plug-in sensitivity near 95.3%, with a rough induced range near 85.1%–98.7%. These are not valid estimates because neither the positives nor audit cases have representative human truth and scan completion is unknown. They demonstrate why “≈98%” is unjustified.

The “13/13” pilot is a selected 20-candidate development set, not a held-out probability sample. The “28/28” external check is also misdescribed: `pipeline/validate_awesome.py:45-65,85-89` asks whether entries in an AI-for-math list trigger a keyword flag, not whether those papers contain author disclosures or are classified correctly. The actual May–August prefix-frame result is 28 flagged of 29 in-frame entries, not 28/28. `reports/awesome_validation.txt` also reports 14 list entries absent from the database. A narrower July 1–August 8 cohort happens to be 15/15, but that selected set is still not a disclosure gold standard.

**Required fix:** construct a preregistered, double-annotated, representative gold set containing scanner positives and negatives, stratified hard negatives, PDF/source strata, versions, subfields, languages, and time. Blind reviewers, resolve disagreements, report inter-rater reliability and class-specific precision/recall with intervals, and keep the model audit explicitly secondary.

### LB-05 — Reporting combines incompatible histories, protocols, and populations

`paper_rollup()` reads every snippet classification ever stored (`pipeline/report.py:40-63`). Although it accepts a model filter, the caller does not use it (`pipeline/report.py:88`). It has no scan-run, version, prompt, taxonomy, artifact-hash, release, or human-review scope. `author_use` permanently outranks later conflicting labels. Multi-snippet location is not merged.

The headline intersects the rollup with the 6,429 downloaded papers, but the downstream tool/category/impact/location tables loop over all 1,180 author-use papers (`pipeline/report.py:111-142`). The generated impact and location tables therefore total 1,180 while the public headline is 1,038. `--months` is accepted but ignored; dates are hard-coded (`pipeline/report.py:66-76,151-156`).

**Required fix:** make reporting a pure function of a signed release manifest and preregistered analysis specification. Reject a release if stage completeness, evidence, schema, model, taxonomy, human policy, or cohort identity is mixed. Scope every table to its displayed population.

### LB-06 — Untrusted manuscripts are passed to an agentic external processor without a safe boundary

Paper text enters prompts at `pipeline/classify.py:108-115` and `pipeline/audit.py:31-49,111-118`. `pipeline/classify.py:126-138` invokes `codex exec` from the repository, inherits ambient process state, and does not explicitly disable network or all tools. Read-only filesystem mode protects writes; it is not a confidentiality or egress boundary. Thirty unrelated papers share one classification prompt (`pipeline/classify.py:29,192`), so one malicious source can influence 29 other labels.

The actual model is not selected on the command line. `codex-exec-default` is only a mutable bookkeeping label (`pipeline/classify.py:32,126-133,180`). There is no closed JSON schema, enum validation, confidence range, quote grounding, output cap, raw-response provenance, or prompt/taxonomy version. Bad IDs can fall back positionally. Failed batches and audit calls still lead to a zero process exit.

**Required fix:** use a non-agentic structured-output API with tools disabled and a pinned model. Otherwise isolate each paper in an empty-root ephemeral sandbox with no repository/corpus mount, no credentials, no egress, strict CPU/RAM/process/output limits, and one paper per call. Validate a closed schema and exact evidence spans before storage.

### LB-07 — Public artifacts violate the project’s own aggregate-only rule

`TECH_NOTES.md:186-194` and `DESIGN_PLATFORM.md:126-131` require aggregate reporting. The repository nevertheless tracks:

- `reports/spotcheck_result_bearing.md`, with paper IDs, titles, automated high-impact labels, categories, excerpts, and blank verdicts;
- `results/candidate_papers.csv` and `.md`, containing paper-level candidate labels and raw snippets;
- `results/manual_review.md`, containing identifiable judgments;
- `results/ai_ack_hits.*` and `results/ai_ack_report.md`, containing long expressive text and source-only personal/contact material;
- `reports/awesome_validation.json`, containing paper-level buckets and metadata.

This creates copyright, privacy, correction, and reputational risk, especially for “result-bearing” labels. It also undermines the aggregate-only public promise.

**Required fix:** quarantine restricted evidence outside the public Git tree. If the repository has not been publicly distributed, clean sensitive blobs from history before release. Enforce a publication allowlist that can emit only approved aggregate schemas with minimum-cell and disclosure-review rules.

### LB-08 — The generated site has stored-XSS and document-safety defects

`bar_svg()` interpolates unrestricted classifier-derived names and titles directly into SVG text/title elements (`pipeline/build_site.py:59-80,163-176`). A malicious manuscript can prompt a label containing closing markup and script, which a future site build writes to HTML. Report Markdown cells are also unescaped (`pipeline/report.py:116-129`). Embedded JSON at `pipeline/build_site.py:214-217` is not made script-safe (`<`/`</script>` are not escaped). Existing client code uses `innerHTML` (`pipeline/sitetext.py:129-135`; `site/index.html:318,450,473`).

`results/ai_ack_hits.csv` already contains a formula-leading cell, and CSV writers do not neutralize spreadsheet formulas (`arxiv_ai_ack_scan.py:536-551,585-603`). Quoting CSV is not sufficient.

**Required fix:** enforce canonical enums/IDs; HTML/XML/Markdown-escape all display values; place data in external JSON or serialize `<` as `\u003c`; build DOM with `textContent`; neutralize spreadsheet-dangerous prefixes or make Parquet/JSON canonical; add hostile-input tests and a restrictive CSP.

### LB-09 — Archive and PDF processing has no global resource or rendered-content boundary

`pipeline/scan.py:64-102` reads full blobs, performs unbounded decompression, calls `getmembers()`, and imposes no archive member-count, aggregate expanded-byte, ratio, wall-time, disk, or recursion limits. The per-member size check does not bound the archive as a whole. `pdftotext` has no timeout or sandbox (`pipeline/scan.py:110-119`). `pipeline/audit.py:52-74` repeats unbounded archive processing before truncating text.

The comment/URL regex is not a TeX parser. It mishandles `%` after even backslash runs, verbatim-like regions, nested braces, and complex `\href` forms. The scanner still reads residual `.tex`, `.ltx`, and `.txt` members; content sniffing expands this further. That conflicts with `TECH_NOTES.md:46-50`, which says to ignore non-rendered comments and residual files by default.

**Required fix:** stream with strict compressed/expanded/member/ratio/time limits; resolve a rendered include graph with a TeX-aware parser; preserve a separate, ethically approved residual-source mode; sandbox a pinned PDF extractor; bind derived text to input hash and extractor version.

### LB-10 — The AWS bulk job is fast but not a trustworthy resumable pipeline

`pipeline/aws/filter_remote.py` has several failure modes:

- after five failed downloads or an MD5 mismatch it continues; after any number of such failures it prints `ALL DONE` and exits zero (`:33-49,74`);
- it appends paper members directly to monthly tar files and only then records a whole chunk as done (`:51-67`);
- a crash before the done marker causes duplicate members on retry; a crash after the marker but before final tar close can leave a truncated/incomplete archive permanently skipped;
- the new persistent handles are only flushed, not closed and `fsync`ed, before recording completion (`:23-27,64-73`);
- upstream names, ownership, modes, and timestamps are copied without normalization (`:52-60`);
- the manifest size column is ignored, AWS calls have no timeout, and there are no disk/cost limits;
- output files have no SHA-256, per-paper inventory, duplicate/missing report, version identity, or importer;
- `math_ids.txt` is a 169,394-line derived population with no tracked generator/query/source hash and appears to contain papers with any math category rather than a clearly frozen math-primary cohort;
- the chunk manifest ends in July 2026 while the target list contains August IDs;
- there is no code connecting the resulting monthly tars to the artifact ledger or scanner;
- an S3 latest-source snapshot cannot reconstruct v1 text or version transitions without version-specific artifact/member manifests.

`pipeline/aws/instance.txt` also publishes a live-looking instance identifier and public IP, while the repository has no infrastructure-as-code, IAM policy, Security Group, IMDSv2, encryption, logging, budget, termination, or incident runbook.

**Required fix:** write a closed, normalized, content-addressed per-chunk shard in a staging path; validate exact expected membership; close and `fsync`; compute SHA-256; atomically commit a ledger; only then delete inputs and mark complete. Exit nonzero on any failure. Generate and sign manifests reproducibly. Import paper-version/hash metadata before scanning. Remove live infrastructure inventory and audit/terminate the instance and its cloud controls.

### LB-11 — A clean clone cannot reproduce, test, deploy, or correct the result

There is no README, project license, data license, dependency manifest/lock, packaging metadata, migration framework, test suite, CI workflow, build command contract, container, deployment config, runbook, rollback procedure, release manifest, SBOM, signature, security policy, contribution guide, citation file, or correction policy.

`db.connect()` runs `CREATE IF NOT EXISTS` (`pipeline/db.py:101-107`) rather than versioned migrations. The ignored 397+ MB database is the only source of the public aggregates, but a clone cannot reconstruct it from a frozen input manifest. `site/dashboard.html` remains a manually maintained competing source with an obsolete `142` tile, while `build_site.py` relies on brittle string assertions and replacement (`pipeline/build_site.py:219-240`).

**Required fix:** create one documented, locked, deterministic build from a small licensed fixture and from an immutable research release. Add migrations, CI, release provenance, deployment and rollback. Delete or clearly designate competing generated/source artifacts.

### LB-12 — Legal identity, data governance, and community collection remain unresolved

There is no `LICENSE`, dataset licence, NOTICE, privacy notice, controller/contact statement, vendor-processing protocol, retention/deletion policy, correction/appeal/takedown channel, research-ethics determination, or arXiv non-endorsement notice. `DESIGN_PLATFORM.md:10-17` assumes IDs plus derived labels are automatically legally publishable; identifiability, professional effects, item licences, and data-protection duties require a real review. Adopting “ODC-BY” in a planning note (`DESIGN_PLATFORM.md:114`) does not license the dataset.

The “ArxivObservatory” name visually implies official association and does not use arXiv’s capitalization. Clear naming, trademark/brand review, and a prominent independent-project disclaimer remain necessary.

The proposed share-link workflow (`PITCH.md:69-75`) can collect copyrighted paper text, prompts, contributor identity/account details, and provider-specific metadata. Server-side snapshots (`DESIGN_PLATFORM.md:115`) contradict the zero-backend architecture (`DESIGN_PLATFORM.md:18-19`) and create SSRF, malware, moderation, withdrawal, retention, and provider-terms risks.

**Required fix:** obtain institutional legal/data-protection/ethics review; define code/data licensing separately; create governance and correction processes; rename or obtain brand guidance; prefer structured reviewer attestations over conversation capture. Do not build a generic URL fetcher.

## Scientific and statistical review

### 1. Freeze a precise WP1 estimand

The public statistic should be defined before another large run. A defensible primary estimand would be:

> Among math-primary arXiv papers first announced in a preregistered calendar window, what proportion of specified public paper versions contain an author-originated statement that a defined class of generative-AI/agent tool was used in producing that paper, under a frozen evidence and annotation protocol?

Every phrase matters: first announced versus created date; math-primary versus any math cross-list; v1 versus fixed-lag latest; explicit author report versus model inference; generative AI versus proof/CAS/software; and paper versus paper-version.

Recommended primary analysis: v1 text at a fixed publication lag, math-primary by v1 metadata, generative-AI/agent disclosures, one paper-version per row. Recommended secondary analyses: latest version at a fixed later cutoff, disclosures added/removed between versions, cross-listed sensitivity, PDF-only stratum, and other computational-tool families. Never call disclosure prevalence “AI use prevalence”: willingness and norms mediate observation (`TECH_NOTES.md:120-123`).

### 2. Do not generalize from 39 days

July 1–August 8 is useful for instrument development. It cannot establish longitudinal adoption, a structural break, or an August trend. Early August is a short partial month, later versions have differential follow-up, field composition varies, and disclosure norms may be changing. The 22.1% versus 14.9% display should be labelled descriptive pilot output only and withheld until the instrument is validated.

### 3. Separate tool families and ascertainment protocols

The pitch promises LLMs, CAS, custom code, and proof assistants. The current classifier selects only `llm` and `generic` scan tiers (`pipeline/classify.py:78-81`). A “Lean” count can appear when Lean co-occurs in an LLM-triggered context, but this is not systematic proof-assistant ascertainment. The site’s phrase “chatbots, coding assistants, proof tools” overstates coverage.

Build independent, validated retrieval/annotation modules for generative AI, formal proof systems, CAS/numerics, and custom code. Report separate denominators/sensitivity. Do not combine ordinary mathematical software with generative assistance in one prevalence headline.

### 4. Build the gold study before refining charts

The existing 20 human rows are a valuable seed and current rollup agrees on all 13 selected true disclosures. That is development-set recall, not a test estimate. Create a labelled sampling design before the taxonomy is changed further:

- random positive and negative samples from a proven-complete frame;
- oversampled generic phrases, topic papers, citations, names, non-English text, PDF-only sources, no-acknowledgment papers, and residual-file cases;
- two independent trained reviewers per item, blinded to machine label and relevant study hypotheses;
- adjudication and an explicit “insufficient evidence” state;
- class-specific precision, recall, specificity, calibration, and evidence-span agreement;
- Wilson/Jeffreys or design-based intervals as appropriate, plus inter-rater agreement with uncertainty;
- a locked test set held out from lexicon/prompt development.

### 5. Correct the negative-audit estimator

Let `N+` and `N-` be the numbers classified positive and negative in the release, and let a probability sample of `n-` negatives contain `m` human-confirmed misses. Estimate the negative-stratum false-negative fraction with its sampling design, expand it to `N-`, and combine it with the human-calibrated true-positive count to estimate sensitivity. Propagate both positive precision and negative miss uncertainty. If strata are sampled unequally, use weights. If complete scans are not proven, add an unobserved/failed stratum rather than treating it as negative.

Do not call the audit agent ground truth, do not round one or two events to a confident recall percentage, and do not use the same model family for primary classification and “independent” audit without qualification.

### 6. Treat classifier error as the dominant uncertainty

Wilson bands in `pipeline/report.py:26-33` are arithmetically fine for binomial sampling variation. They do not include classifier error, missing artifacts, version mismatch, time-window selection, taxonomy uncertainty, or clustered/multiple labels. For a near-census, the stated superpopulation interpretation must be explicit. The site currently calls the corpus a census while simultaneously presenting sampling-style uncertainty and omitting measurement uncertainty.

Use a measurement-error model based on held-out human validation, report raw and corrected estimates, propagate sensitivity/specificity uncertainty, and include missingness sensitivity bounds. With thousands of papers, classification bias dominates binomial width.

### 7. Avoid raw subfield league tables

`pipeline/build_site.py:156-162` sorts raw subfield rates and masks only `n<100`. This invites overinterpretation, multiple-comparison noise, field-composition bias, differential use of source formats, and differential disclosure norms. The plan promised minimum-cell masking or empirical-Bayes shrinkage (`DESIGN_PLATFORM.md:105-110`); only the first half exists.

Use a preregistered hierarchical model or display all adequately powered fields in canonical order with uncertainty and no winner framing. Adjust or stratify for time, version, team size, source availability, and other prespecified composition factors. Explain that differences are descriptive, not causal.

### 8. Fine-grained role and impact labels need their own validation

The report claims 575 result-bearing papers across its all-history rollup (`reports/report.md:93-100`), yet the 30-paper “human spot-check” contains no completed verdict. Role, location, model string, and epistemic impact are harder than binary disclosure detection and need separate annotation guidance and reliability estimates.

Use ordinal/multilabel adjudication; preserve evidence spans; allow multiple locations; distinguish the paper’s explicit claim from the reviewer’s inference; do not surface exact model names unless present verbatim in verified public rendered text. “Result-bearing” should never be a public paper-level model label.

### 9. External lists are retrieval checks, not validation truth

The awesome list is useful for testing discovery of known AI-for-math activity. Its inclusion criteria differ from author disclosure, it includes papers about AI systems, it changes over time, and the exact source README/revision is not tracked. Pin commit, licence, parser, and source hash; classify list purpose; manually establish which entries truly contain in-scope disclosures. Report coverage buckets without calling them precision or recall.

### 10. Preserve the good WP2 and WP3 guardrails, but delay execution

The documents correctly separate detector-inferred prose modification from explicit disclosure and error auditing (`TECH_NOTES.md:16-28`). Keep WP2 vendor claims independent, validate on pre-LLM math and controlled transformations, freeze model/access date/threshold, and ensure non-native writing is not stigmatized. Treat commercial detector output as a measurement instrument with conflict-of-interest and reproducibility constraints.

WP3 should remain a separate preregistered expert study. Preserve the known-positive versus representative-sample split, cumulative severity scale, blinding, two independent mathematicians, specialist tie-break, and author contact (`TECH_NOTES.md:147-176`). Do not use the current agentic pipeline or community subscription workflow for an error-prevalence claim.

### 11. Update literature and pitch claims before outreach

`PRIOR_ART.md` is a useful map but still reads partly as a search memo rather than a systematic review. Add search databases, dates, strings, inclusion criteria, extraction table, primary-source verification, and conflict-of-interest notes. Separate peer-reviewed results, preprints, company technical reports, company marketing posts, surveys, and secondary news.

The “20% above trend” statement in `PITCH.md:19`/`pitch.tex:26` rests on secondary coverage and an unreproduced chart; reproduce the time-series method or remove it. “Pangram best-in-class” and vendor false-positive claims need neutral attribution and independent benchmark context. In particular, the cited Pangram technical report does not establish an approximately `1e-5` false-positive rate specifically on arXiv mathematics, despite the wording at `TECH_NOTES.md:127-129` and `PRIOR_ART.md:85-89`.

The 13/129 pilot must be described as a selected development/retrieval exercise: the 129 comprises 83 primary math.AG submissions and 46 cross-lists, and only 20 candidates received human review; no probability audit of scanner negatives established a census result. ArxivMathGradingBench is also summarized imprecisely: the primary paper reports 35 papers containing 40 known errors, rather than simply “35 items” (`TECH_NOTES.md:159-163`; `PRIOR_ART.md:116-119`). The 81% researcher-use survey is a highly selected respondent result and cannot be used as a population benchmark for a “disclosure gap” without selection caveats (`PRIOR_ART.md:22-24`). “Gap confirmed” is too strong for a model-assisted web pass without reproducible search methods (`PRIOR_ART.md:1-4,42-45`).

Keep the existing distinction for the Nature word-frequency estimate and the 1.3% citation estimate: both measure constructs different from explicit disclosure. Keep `PITCH.md` and `pitch.tex` generated from one canonical source; they currently duplicate claims manually.

## Implementation and data-system review

### `pipeline/db.py`

**Strength:** compact SQLite spine, WAL, version metadata, and useful file hashes.

**Problems:** no schema version/migrations; no foreign keys, checks, enums, uniqueness for release identities, run/config tables, scan item outcomes, normalized evidence, human annotation history, corrections, or immutable paper-version artifacts. `CREATE IF NOT EXISTS` cannot migrate the live database. `submitter` is collected without a documented purpose.

**Action:** introduce migrations and constraints; use append-only protocol/run/item tables; minimize personal fields; snapshot releases transactionally. SQLite remains suitable for a single-node research pipeline if write ownership is controlled.

### `pipeline/harvest.py` and `pipeline/backfill.sh`

**Strength:** OAI-PMH, polite delay, retry, raw page archives, version histories, per-query state.

**Problems:** `--reparse` globs only `corpus/oai/page_*.xml.gz` and misses the new nested query directories (`pipeline/harvest.py:176-183`). Deleted OAI records are skipped rather than tombstoned. Writes are not content-manifested/atomic as a release. Responses are loaded whole. `backfill.sh` prints complete and exits zero after 20 exhausted attempts (`:11-23`). Chunk endpoints can overlap.

**Action:** recursive manifest-driven reparse; immutable raw-response hash ledger; tombstones; bounded responses/retries; explicit interval semantics; nonzero failed-chunk exit and machine-readable summary.

### `pipeline/fetch.py`

**Strength:** serial/polite targeted fetching, explicit requested version, seeded ordering, SHA-256.

**Problems:** file identity overwrites history; prior ok/404 is terminal across later versions; ID-prefix selection differs from created-date cohort; response bytes are unbounded/in-memory; redirects/host, `Retry-After`, ID/path containment, no-follow writes, and atomic rename are not hardened; unknown 200 bodies can enter as `ok_unknown_format`.

**Action:** artifact-by-version/content hash; compare requested/effective/latest version; retry previously transient and changed-version states; stream/cap; validate arXiv ID and resolved path; restrict redirect hosts; atomic writes; separate terminal withdrawal/no-source/format/error states.

### `pipeline/scan.py` and `pipeline/scan_meta.py`

**Strength:** static archive reads without filesystem extraction; multiprocessing; contexts and rule classes retained.

**Problems:** destructive named runs; no completion/errors; no total resource bounds; partial TeX parsing; residual-file overcollection; no rendered location; silent >10 MB member skip; stale PDF cache; no pinned extractor; metadata scan covers mutable global table.

**Action:** immutable run/items; render-closure parser; bounded streaming; source/PDF strata; exact byte/character evidence spans; deterministic test corpus; per-item failure and nonzero run status.

### `pipeline/lexicon.py`

**Strength:** readable tiered definitions and useful pilot-derived false positives.

**Problems:** regex behavior is not validated across representative text, languages, TeX encodings, version changes, and tool-name ambiguity. Taxonomy and prompt are embedded in code. Current public use covers only LLM/generic tiers while site language implies broader tool coverage.

**Action:** version lexicon/taxonomy separately; golden positive/negative fixtures; Unicode/language review; precision/recall by term/rule/stratum; independent change review; never change lexicon and gold truth together.

### `pipeline/classify.py`

**Strength:** explicit taxonomy draft, checkpoints, response ID coverage check, raw terms/hit IDs stored.

**Problems:** unpinned agentic backend; cross-paper batches; prompt injection; cache hash omits paper/version/member/run/protocol/prompt/taxonomy/model; global cache can skip another paper sharing text; only longest merged context survives; positional ID fallback; no schema/quote validation; failures exit zero; labels have no normalized provenance.

**Action:** one immutable classification item per evidence packet; structured non-agentic call; actual model pin; full protocol hash; strict IDs/schema/enums; exact span verification; durable errors; fail closed; human overrides as new annotations rather than destructive edits.

### `pipeline/audit.py`

**Strength:** seeded sampling and head+tail retention are useful engineering steps.

**Problems:** source downloads without hits are assumed scan-negative; PDF-only excluded; residual files read; middle dropped; archive processing unbounded; model unpinned; reply parsed without schema/evidence validation; cache ignores run/model/version/source/prompt; version omitted; model result treated as recall truth.

**Action:** sample from immutable successful scan items; probability/stratum metadata; human primary labels; independent machine retrieval secondary; full rendered text or documented bounded sampling; versioned evidence and failures.

### `pipeline/report.py`

**Strength:** Wilson implementation, created-date frame, explicit missing/pending intent, raw-rate wording.

**Problems:** false scan denominator, unscoped historical rollup, no human policy, versions collapsed, hard-coded dates, ignored `--months`, cohort leak in distributions, one location, unescaped Markdown, no release manifest or validation adjustment.

**Action:** rewrite as tested pure analysis over one frozen release and protocol. Stop rather than publish on incomplete items, orphan evidence, mixed version/model/run, or unresolved human conflicts.

### `pipeline/build_site.py`, `pipeline/sitetext.py`, and `site/`

**Strength:** clean visual language, aggregate output, no analytics trackers, compact local build, useful explanatory affordances.

**Problems:** inherits invalid analysis; hard-coded window/validation; unsafe markup; brittle template surgery; duplicate/stale source page; no complete HTML document (`doctype`, `html`, `head`, `body`, language, charset, viewport are absent); hover/pointer-dependent disclosure chart; server SVGs lack complete accessible text/table equivalents; no CSP/security headers; no canonical metadata/Open Graph/social card; no real repository/method/correction link; build date but no release ID/hash.

**Action:** generate semantic pages from structured templates; external safe JSON; accessible tables and keyboard/focus behavior; publication-status banner; methods/validation/data/corrections/about/contact pages; release/citation IDs; security headers; one source of truth.

### `pipeline/validate_awesome.py`

**Strength:** explicit buckets and minimum parse-size failure.

**Problems:** source revision/file is untracked; parser format is brittle; threshold 50 is arbitrary; ID-prefix windows; flag presence is misconstrued as disclosure validation; no licence/source hash or human construct check.

**Action:** pin source commit and licence; checked fixture; schema and expected section counts; creation-date matching; manually labelled disclosure subset; describe only retrieval coverage.

### `pipeline/aws/`

**Strength:** official requester-pays channel, upstream checksum verification, memory-light ID set, strong throughput improvement.

**Problems:** no generator/provenance for manifests/IDs; crash-unsafe tar append and resume; failure-success ambiguity; no output manifest/hash/version; unsafe metadata propagation; no importer; infrastructure inventory; no IaC/security/cost/teardown documentation.

**Action:** treat it as an acquisition subsystem with immutable shard jobs and audited cloud infrastructure, not a one-off remote script.

### `arxiv_ai_ack_scan.py`, `WORKFLOW.md`, and legacy `results/`

The legacy path duplicates acquisition, scanning, report, and output semantics and has different safety/provenance rules. It writes expressive snippets and unsafe CSV. `WORKFLOW.md` still describes it as the project workflow.

**Action:** deprecate it explicitly; retain only a sanitized historical pilot fixture or migrate its manually reviewed annotations into the new versioned schema. Remove generated/sensitive outputs from public Git.

## Recommended target architecture

```text
official OAI/S3 inputs
        |
        v
immutable raw manifests + content-addressed paper-version artifacts
        |
        v
protocol registry (cohort, lexicon, parser, model, taxonomy, code commit)
        |
        v
append-only run -> per-item success/error -> normalized hits/evidence
        |
        v
machine annotations + independent human annotations/adjudication
        |
        v
frozen analysis release (manifest, schema, checksums, validation, corrections)
        |
        +--> aggregate public data
        +--> deterministic static site/report
        +--> restricted evidence archive (not public Git)
```

### Minimum logical entities

- `papers` and immutable `paper_versions`;
- `source_artifacts` keyed by version and content hash, with licence and retrieval identity;
- `harvest_runs` / `harvest_items`;
- `scan_protocols`, `scan_runs`, `scan_items`, and `scan_hits`;
- `classifier_protocols`, `classification_runs`, `classification_items`, and validated labels;
- `evidence_spans` with artifact/member and normalized byte/character coordinates;
- `annotation_projects`, independent annotations, adjudications, reviewer training/blinding metadata;
- `analysis_protocols` and immutable `analysis_releases`;
- public aggregate tables with disclosure-control rules;
- correction/supersession ledger.

### Reproducibility contract

Every result must name: Git commit and dirty-state hash; schema and migration version; raw input manifest/checksums; cohort query and timezone/date semantics; requested/effective paper version; artifact hash; extractor and lexicon versions; scan run/item status; prompt/taxonomy/model/API/tool policy; human annotation/adjudication policy; analysis code/config; validation estimates; missing/error strata; release ID; output checksums.

### Scale strategy

SQLite is adequate for single-writer daily operation and research-scale aggregates. The immediate bottleneck is correctness, not database technology. Use content-addressed object storage for corpus/shards, Parquet for immutable release tables, and SQLite/Postgres only for orchestration/annotation state. Partition processing by paper-version hash; make tasks idempotent and fail-closed; publish only complete manifests. Add structured logs, metrics, budget alerts, backups, restore drills, and retention controls before cloud scale.

## Security, privacy, ethics, and licensing

### Threat model

Treat manuscript text, TeX comments, archive members/names, metadata strings, model outputs, community URLs, chart specs, CSV cells, and external PRs as untrusted. Protect four things separately: corpus confidentiality/minimization; pipeline integrity and availability; model/vendor boundary; and public-site/user safety.

### Data minimization and rights

Official bulk access permits computation but does not make all article full text freely redistributable. arXiv’s official bulk guidance states that default licences generally do not authorize third-party redistribution and that tools should link back to arXiv. Store licence per paper-version; keep source private; publish approved derived aggregates; assess whether excerpts are necessary and permitted. Drop `submitter` and source-only personal material unless a documented purpose, lawful basis, access control, and retention schedule exist.

### Author and community fairness

Explicit disclosure is ethically safer than inference, but derived labels can still affect reputation. Require human verification and author correction/response before any paper-level display. Never equate non-disclosure with misconduct. Measure and discuss differential disclosure norms, language, geography, seniority, subfield, tool access, and policy changes. Non-Latin/non-English retrieval should be designed with native-speaker review rather than silently excluded.

### Governance package before public release

- institutional ethics/data-protection/legal determination;
- named controller/maintainer and security/correction contacts;
- separate code, annotation-data, and documentation licences;
- provenance and item-rights policy;
- privacy notice and vendor/subprocessor/data-transfer protocol;
- access, retention, deletion, backup, breach, and takedown procedures;
- author appeal/correction/response and public correction ledger;
- contributor code of conduct, conflict-of-interest and reviewer policy;
- arXiv non-affiliation/brand notice;
- publication allowlist and minimum-cell policy.

### Community workflow

Do not execute external PR code on a persistent corpus runner. Tier 1 should accept declarative, schema-validated analysis/chart specifications only. CI should use minimal permissions, SHA-pinned actions, no fork secrets, isolated previews, resource limits, and protected deployment. Tier 0 should run only a protected reviewed/merged commit in an ephemeral VM/container with read-only necessary corpus, no ambient credentials or egress, two-person approval, and an artifact allowlist. A dedicated user plus `firejail`/`bwrap` alone (`DESIGN_PLATFORM.md:116-117`) is not a sufficient public-runner policy.

Avoid conversation share-link collection. If it is retained, allowlist providers, prohibit generic URL fetching, sanitize on a separate origin, encrypt with short retention and withdrawal support, document provider terms/lawful basis, and add abuse/Sybil/rate-limit/audit controls.

## Deployment and public-impact review

### Keep the static architecture

The static-site decision in `DESIGN_PLATFORM.md:18-19,63-68` is good for cost, privacy, resilience, and public trust. The site should consume signed, versioned aggregate files only. It should not connect to a live operational database or depend on a runtime backend for the initial release.

### Correct the information hierarchy

The current page leads with a definitive 16.1% tile and a “Papers disclosing” heading, while the classifier caveat is subordinate. A trustworthy alpha should lead with status:

1. “Research prototype / validation incomplete” banner;
2. precise estimand and release ID/date;
3. validated headline with raw/corrected/missingness views—or no headline until available;
4. coverage funnel: frame → artifact → scan → classify → human validation;
5. validation panel with sample design and uncertainty;
6. trends/subfields only after those foundations;
7. methods, data dictionary, licence, citation, corrections, and contact.

### Accessibility and web quality

Create a standards-complete document with language, charset, viewport, semantic landmarks, skip link, sensible focus states, accessible SVG titles/descriptions, keyboard-equivalent chart inspection, and visible data tables. Test with automated accessibility tooling plus keyboard and screen reader review. Respect reduced motion. Check color contrast in both themes. Do not make hover-only explanations essential.

Add canonical URL, description, Open Graph/social metadata, favicon, sitemap/robots policy, structured project metadata, and an accessible social card only after claims are stable. Provide downloadable aggregate CSV/JSON/Parquet with schema and citation; a “How to interpret this” page; changelog/correction feed; reproducible methods; and a media guide that explicitly warns against “AI wrote X% of papers.”

### Release and operations

The tracked ZIP matches the current site, which is good, but it preserves broad `777` modes and contains no licence, README, release manifest, checksums, signature, SBOM, provenance, or correction contact. Build reproducibly with normalized timestamps/modes; hash/sign outputs; generate an SBOM/provenance attestation; deploy from protected CI; use preview checks; retain prior releases; define rollback and incident procedures.

If future CDN, Vega, Observable, or DuckDB-WASM dependencies are used, self-host or pin immutable versions/integrity, set CSP, constrain DuckDB extensions/network/filesystem/memory/time, and keep the site functional without third-party trackers.

## Testing and quality plan

There are currently no repository tests. The minimum suite should include:

### Unit and golden tests

- OAI page parsing, deleted records, version dates, resumption, nested reparse;
- arXiv ID/date/category cohort semantics and boundary days;
- fetch response kinds, later-version refresh, 404 recovery, redirects, atomic writes;
- gzip/tar/plain/PDF fixtures, malformed and adversarial archives, compression limits;
- TeX comments with odd/even slashes, verbatim, URL/href nesting, include graphs, encodings;
- lexicon positive/negative/negation/name/notation/multilingual cases;
- snippet merge and complete protocol hash identity;
- strict classifier JSON schema, exact IDs, enums/ranges, hostile strings, quote spans;
- immutable run/integrity and supersession behavior;
- audit sampling/weights and recall-estimator simulations;
- report cohort scoping, version policy, missing strata, human overrides, interval math;
- HTML/XML/Markdown/CSV/script escaping;
- AWS crash/retry/duplicate/missing/checksum/ledger behavior.

### Integration tests

Create a small, licensed/synthetic end-to-end fixture containing source, PDF-only, revision, cross-list, no-hit, hit, error, malicious TeX, malformed archive, non-English disclosure, and human labels. From a clean temporary directory, run harvest/import → fetch fixture → scan → classify stub → annotate → freeze → report → site twice; outputs and hashes must match.

### Property and fuzz tests

Fuzz OAI XML, archives, TeX comment stripping, IDs/paths, classifier JSON, CSV/Markdown/HTML labels, and chart specs. Assert bounded resources, no traversal, no code execution, no broken output, and fail-closed status.

### CI gates

Formatting/lint/type checks; unit/integration/security tests; migration upgrade/downgrade checks; dependency and secret scanning; licence/SBOM checks; schema compatibility; accessibility/link/HTML/CSP tests; reproducible-build comparison; sensitive-path/publication-allowlist check; orphan-evidence query; complete-release gate; signed protected deployment.

## Documentation and repository hygiene

Required top-level files before public code release:

- `README.md` with exact prototype status, non-affiliation, setup, architecture, data boundaries, and reproducibility limitations;
- `LICENSE` and separate data/documentation licence/NOTICE;
- `pyproject.toml` plus a locked dependency file and supported Python/tool versions;
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, governance/maintainer policy;
- `CITATION.cff`, changelog, release/correction policy;
- data dictionary, taxonomy, annotation manual, validation protocol, threat model, privacy/ethics note;
- operations runbook, backup/restore, cloud/IAM/cost/teardown, deploy/rollback.

Resolve document drift:

- `DESIGN_PLATFORM.md` says “nothing implemented” while a site and AWS path now exist, and labels partial fixes as applied.
- `OVERNIGHT_PLAN.md` calls destructive scans idempotent and says all stages checkpoint safely; both are false.
- `OVERNIGHT_PLAN.md:23-29` lists report fixes that were not actually implemented.
- Its token/call budget says roughly 120–150 calls while proposing about 90 classification batches plus 200 single-paper audits.
- `WORKFLOW.md` documents only the legacy path.
- `PITCH.md`, `pitch.tex`, and site copy duplicate and diverge.
- Move time-bound operational notes into dated run records/issues rather than canonical root specifications.
- Archive earlier audits with issue/fix/test/status links rather than leaving multiple disconnected review files.

The `.claude/docs/lean4` and `.claude/tools/lean4` trees are unrelated to this project. Remove/relocate them or explicitly vendor them with source, licence, ownership, security boundary, and reason for inclusion.

## Prioritized roadmap

### Gate 0 — Stop amplification and make the tree safe

1. Mark the site/report as unvalidated or remove the 16.1%, July/August, subfield, result-bearing, and 98% claims.
2. Quarantine paper-level excerpts/labels; decide whether Git history needs cleaning before publication.
3. Remove `pipeline/aws/instance.txt`; inspect/terminate the instance and audit IAM, Security Group, IMDSv2, encryption, logs, and cost.
4. Add README/status/non-affiliation, licences, security and correction contacts.
5. Freeze the current DB as a private forensic snapshot; do not repair it in place or publish further derivatives.

### Gate 1 — Build the immutable engineering core

1. Add migrations and the paper-version/artifact/protocol/run/item/evidence schema.
2. Make every stage append-only, complete/error-aware, content-addressed, and fail-closed.
3. Harden archive/PDF/model boundaries and strict schemas.
4. Repair OAI reparse/backfill failure status and version refresh.
5. Rebuild all current data from frozen inputs; reject orphan evidence.
6. Add locked dependencies, synthetic fixture, tests, CI, and runbook.

### Gate 2 — Freeze and validate WP1

1. Preregister estimand, cohort, version/fixed-lag policy, missingness, taxonomy, and analyses.
2. Create the double-annotated representative gold study and a locked test set.
3. Validate retrieval, binary disclosure, tool family, role, location, and impact separately.
4. Implement measurement-error/missingness uncertainty and negative-audit estimator.
5. Obtain ethics/data-protection/legal/vendor review.

### Gate 3 — Publish a narrow alpha

1. Freeze a signed, citable, aggregate-only release.
2. Generate accessible site/report/data from that exact manifest.
3. Publish validation, limitations, data dictionary, citation, licence, corrections, and non-affiliation.
4. Have an independent statistician/methodologist and security/privacy reviewer sign off.
5. Seek independent replication before strong trend/outreach claims.

### Gate 4 — Scale carefully

1. Convert AWS acquisition into atomic audited shard jobs and import paper-version provenance.
2. Extend WP1 longitudinally with fixed protocols and planned change/version handling.
3. Add declarative community analyses over public aggregate/extracted releases.
4. Monitor drift, corrections, missingness, subgroup performance, cost, and incidents.

### Gate 5 — Separate future studies

Only after WP1 is credible, run separately registered and governed WP2 detector calibration, WP3 reliability audit, productivity/author-linkage analyses, or any volunteer conversation workflow. None should inherit WP1 consent, validation, ethics, or release assumptions automatically.

## Release acceptance checklist

### Scientific

- [ ] Primary estimand, cohort, unit, version/fixed-lag and tool scope preregistered.
- [ ] Complete scan/classification item status; failures/unknowns explicit.
- [ ] Representative double-human gold set and locked test set.
- [ ] Precision/recall/specificity and role/impact reliability with intervals.
- [ ] Correct negative-audit estimator and human adjudication.
- [ ] Measurement and missingness uncertainty propagated.
- [ ] Subfield/trend analyses prespecified and composition-aware.
- [ ] Claims independently reviewed and literature sources verified.

### Provenance and engineering

- [ ] Paper-version artifacts immutable and content-addressed.
- [ ] Run/protocol/model/prompt/taxonomy/code identity complete.
- [ ] No orphan evidence; every quote grounded in a stored span.
- [ ] No mixed release/run/model/version rows.
- [ ] Migrations, locked dependencies, fixtures, tests, CI.
- [ ] Clean clone reproduces report/site checksums.
- [ ] Failures exit nonzero; cloud shards atomic and audited.
- [ ] Signed manifests, backups, restore and rollback tested.

### Security, privacy, ethics, and legal

- [ ] Agentic/untrusted processing isolated; no credentials/egress/cross-paper batches.
- [ ] Archive/PDF/path/network/resource limits tested.
- [ ] HTML/script/Markdown/CSV injection tests pass; CSP deployed.
- [ ] Sensitive paper-level outputs absent from public history/release.
- [ ] Code/data/documentation licences and item-rights policy approved.
- [ ] Privacy/vendor/retention/deletion/breach/correction/appeal procedures published.
- [ ] Ethics/data-protection and arXiv brand/non-affiliation review complete.
- [ ] Community workflows separately threat-modelled and governed.

### Public site and reach

- [ ] Prototype/validation status impossible to miss.
- [ ] Headline wording matches the exact estimand and validation level.
- [ ] Coverage funnel and limitations are prominent.
- [ ] Semantic/accessibility/keyboard/screen-reader tests pass.
- [ ] Methods, validation, data, citation, licence, corrections and contact are live.
- [ ] Release ID/checksum displayed; old releases/corrections retained.
- [ ] Protected reproducible deploy and rollback work.
- [ ] Media guidance prevents “AI wrote X%” misinterpretation.

## File-by-file disposition

| Path/group | Recommended disposition |
|---|---|
| `PITCH.md`, `pitch.tex` | Retain concept; correct pilot/trend/validation claims and generate both from one canonical source. |
| `TECH_NOTES.md` | Strong scientific guardrails; update status, turn promises into enforceable protocols, correct current recall/publication mismatch. |
| `PRIOR_ART.md` | Retain as seed; convert to reproducible systematic evidence table and verify primary sources. |
| `DESIGN_PLATFORM.md` | Retain architecture direction; mark implemented/partial/deferred accurately; replace unsafe runner/share-link assumptions. |
| `OVERNIGHT_PLAN.md` | Archive as a dated run note; it is not accurate documentation. |
| `WORKFLOW.md` | Deprecate or rewrite for the current pipeline. |
| `review_codex.md` and earlier `reports/codex_review_*` | Preserve as historical audits; link findings to issues/fix commits/tests/status. |
| `pipeline/db.py` | Redesign with migrations and immutable version/run/evidence entities. |
| `pipeline/harvest.py`, `backfill.sh` | Keep OAI approach; fix reparse, tombstones, manifests, atomicity and fail status. |
| `pipeline/fetch.py` | Keep polite/versioned request and hashing; repair history/refresh/bounds/atomic path handling. |
| `pipeline/scan.py`, `scan_meta.py` | Keep static extraction concept; rebuild completion/provenance/render/resource model. |
| `pipeline/lexicon.py` | Retain as a versioned instrument only after gold tests and scope separation. |
| `pipeline/classify.py` | Replace agentic default/cache/schema/evidence design before research use. |
| `pipeline/audit.py` | Treat as secondary retrieval experiment; replace recall interpretation with human probability audit. |
| `pipeline/report.py` | Rewrite over a frozen release; current output must not be published. |
| `pipeline/build_site.py`, `sitetext.py` | Retain visual direction; replace data trust, templating, escaping, semantics and hard-coded claims. |
| `pipeline/validate_awesome.py` | Retain as pinned retrieval cross-check, not validation truth. |
| `pipeline/aws/*` | Quarantine operational inventory; rebuild as atomic reproducible acquisition/import subsystem. |
| `arxiv_ai_ack_scan.py` | Deprecate after migrating sanitized pilot labels/fixtures. |
| `site/index.html`, `site/data/disclosures.json` | Demo-only; regenerate from a validated signed release. |
| `site/dashboard.html` | Remove competing stale output or convert to a true source template with no embedded mutable data. |
| `dist/arxiv-observatory-site.zip` | Do not publish; replace with reproducible signed release bundle after validation. |
| `reports/report.md` | Retract as a scientific report; retain privately as a dated unvalidated run artifact if useful. |
| `reports/spotcheck_result_bearing.md` | Restricted review queue only; never public with blank verdicts. |
| `reports/awesome_validation.*` | Pin source/provenance; aggregate-only public summary after construct correction. |
| `results/*` | Remove/quarantine expressive snippets, personal data, and paper-level labels; keep only sanitized licensed fixtures. |
| `.claude/docs/lean4`, `.claude/tools/lean4` | Relocate/remove as unrelated, or explicitly vendor with licence and owner. |

## External operational and policy references

- [Official arXiv bulk-data documentation source](https://github.com/arXiv/arxiv-docs/blob/develop/source/help/bulk_data.md): OAI-PMH is the preferred bulk metadata path; S3 is the accepted complete-corpus path; default article licences generally do not authorize third-party redistribution.
- [arXiv API terms](https://info.arxiv.org/help/api/tou.html)
- [arXiv article licensing guidance](https://info.arxiv.org/help/license/index.html)
- [arXiv brand guidance](https://info.arxiv.org/brand/brand-guidelines.html)
- [AWS Requester Pays documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ObjectsinRequesterPaysBuckets.html)
- [GitHub Actions security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [Swiss FDPIC research and data-protection guidance](https://www.edoeb.admin.ch/en/research-and-data-protection)
- [GDPR official text](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

## Checks performed

- read every current research/specification/planning document and every current pipeline/site source;
- inspected recent Git history and the final clean tree at `46b0060`;
- read-only SQLite schema/count/provenance/version/label/audit queries and `quick_check`;
- Python AST parsing for all project Python files;
- JSON parsing for tracked JSON outputs;
- Bash syntax checks;
- `git diff --check`;
- ZIP listing, metadata inspection, and byte comparison with tracked site outputs;
- HTML structural/duplicate-ID inspection;
- tracked-file/repository-infrastructure inventory;
- CSV formula-prefix inspection;
- current official arXiv/AWS operational guidance review.

No model calls, network corpus downloads, public deployment, destructive Git operation, EC2 login/change, or paper reannotation was performed. This is not legal advice, a formal penetration test, an institutional ethics decision, or independent validation of the scientific labels.

## Bottom line

The project has advanced from a promising feasibility probe to a visually compelling, nearly end-to-end research prototype. That progress makes the remaining distinction more important: it is **not yet an observatory producing defensible public statistics**. The public polish currently outruns the measurement system.

The most valuable next action is not another backfill or chart. Freeze the current state, remove the public claims, redesign the data spine around immutable paper-versions and completed run items, rebuild from source, and run a real human validation study. Once one signed aggregate WP1 release can be reproduced from a clean clone and defended statistically, the site’s design and the project’s public-interest potential can become genuine strengths rather than amplifiers of hidden error.
