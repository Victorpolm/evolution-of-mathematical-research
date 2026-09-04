# Complete repository review: ArxivObservatory

**Review date:** 2026-08-09

**Reviewed commit:** `0807af9` on `main`

**Scope:** all 46 tracked files, the tracked pilot outputs, the live SQLite state and ignored corpus/cache structure, the research specifications, future work packages, platform plan, and proposed deployment/community model.

## Executive verdict

This is a promising research project with a stronger conceptual foundation than its present software and public presentation suggest. The documents make several unusually good choices: they separate explicit disclosure from linguistic detection and mathematical-error auditing; identify the paper-version as the intended unit; recognize domain shift, misclassification uncertainty, and disclosure-selection effects; call for a human gold standard and negative audit; avoid treating detector output as misconduct evidence; and propose a cautious, aggregate-first ethics policy.

The repository is nevertheless a **research prototype, not a releasable observatory**. The current database, classifier output, dashboard, and tracked result files cannot yet support prevalence, trend, tool-share, epistemic-impact, or recall claims. The most serious problem is not merely missing polish: the implemented numerator and denominator describe different observed populations, version identity is lost, mutable scans have already orphaned stored evidence, and failures are routinely indistinguishable from negative observations. Scaling the current pipeline would make the result more precise-looking without making it valid.

**Release recommendation:** do not present the current `142` dashboard value, a report produced by `pipeline/report.py`, or the `13/129` pilot as a validated population estimate. Do not publish the existing tracked snippets or per-paper detector/error labels. A public source-code alpha is reasonable only after the name/branding, licensing, sensitive artifacts, security notice, and status language are fixed. A public scientific-data alpha should wait for the WP1 release gates in this review.

The right near-term strategy is narrower than the current roadmap:

1. Make **WP1 explicit author-reported disclosures** reproducible and valid.
2. Release a small, human-verified, aggregate-only alpha with complete coverage and validation documentation.
3. Expand WP1 longitudinally and seek independent replication.
4. Treat WP2, WP3, author-productivity analysis, and the volunteer model-sharing workflow as separate later studies with separate protocols and governance.

## Decision summary

| Area | Current state | Release decision |
|---|---|---|
| Scientific framing | Strong draft concepts; several claims and estimators need correction | Continue, but preregister exact WP1 estimands before the main run |
| Current pilot | Useful discovery/development set; not a validated census | Report as exploratory candidate-retrieval exercise only |
| Data/provenance | Mutable, incomplete, paper-level in key places | Block scientific release |
| Classifier/audit | Unpinned external agent, weak cache identity, no strict evidence validation | Block use in headline statistics |
| Human validation | 20 candidate reviews, one apparent reviewer, no negative probability audit | Block prevalence/recall claims |
| Public artifacts | Long source excerpts, emails, identifiable labels | Remove or quarantine before making the repository public |
| Dashboard | Attractive prototype, but hard-coded, unaudited, potentially misleading and unsafe to automate | Keep private/demo-only until generated from a frozen release |
| Engineering | No package manifest, lock, migrations, tests, CI, release build, or runbook | Block operational deployment |
| Security/privacy/legal | No documented threat model, vendor-processing protocol, privacy process, or project/data license | Block public data and community workflow |
| Public reach | Good narrative hook; missing trustworthy landing pages, citation/reuse paths, and correction channel | Build after the scientific release contract |

### Severity convention

- **Blocker:** must be resolved before the affected public release or study.
- **Critical:** can directly invalidate a central result or irreversibly compromise provenance.
- **High:** likely to cause material scientific, ethical, security, or operational failure.
- **Medium:** important for maintainability, interpretation, accessibility, or scale, but can follow the core blockers.

## What was inspected

The review covered:

- Research and planning documents: `PITCH.md`, `pitch.tex`, `TECH_NOTES.md`, `PRIOR_ART.md`, `DESIGN_PLATFORM.md`, and `WORKFLOW.md`.
- The legacy end-to-end prototype: `arxiv_ai_ack_scan.py`.
- Every current pipeline module: database, harvesting, fetching, lexicon, metadata/full-text scans, LLM classification, negative audit, reporting, external-list validation, and backfill script.
- The only site artifact, `site/dashboard.html`.
- All nine tracked files under `results/` and all three earlier reviews under `reports/`.
- All 13 unrelated Lean/Codex helper files under `.claude/`.
- Repository and delivery infrastructure, including what is absent.
- A read-only inspection of the live, ignored `observatory.db`, corpus/cache sizes, recorded hashes, and stage relationships.

The live database was being backfilled during the review; counts changed while it was inspected. The following is therefore an **inspection snapshot, not a release manifest**:

| Object | Snapshot count |
|---|---:|
| Papers | 149,180 |
| Version rows | 262,802 |
| File-ledger rows / distinct papers | 1,437 / 1,437 |
| Successful file rows | 1,436 (`1,425 ok`, `11 ok_pdf_only`) |
| Scan hits | 8,320 |
| Snippet classifications | 1,227 across 838 papers |
| Human-review rows | 20 |
| Missing hit references retained by classifications | 82 references across 28 classifications |

For the report's default May–August 2026 range, there were 16,166 math-primary papers when selected by arXiv-ID prefix, 16,061 when selected by actual v1 creation date, and only 1,436/1,431 respective papers with a successful fetched file. Thus a report that divides current classified positives by the full frame implicitly treats roughly 91% of the full-text frame as negative before it has been observed. The database passed `PRAGMA quick_check`; this is a logical/provenance problem, not evidence of SQLite page corruption.

Static checks also found that all Python files parse/import in the local environment, the current stored label JSON is syntactically valid, and the embedded dashboard totals are internally consistent. There are no repository tests to establish behavioral correctness.

## Important strengths to preserve

1. **The three estimands are conceptually separated.** `TECH_NOTES.md:16-21` correctly distinguishes explicit disclosure, population linguistic estimates, and document/passage detector output. That distinction should become a schema and publication boundary, not just prose.

2. **The intended paper-version unit is scientifically appropriate.** `TECH_NOTES.md:22-25` recognizes that disclosure can be added or removed and that revisions are analytically meaningful.

3. **Validation is treated as central in the plan.** The proposed gold corpus, held-out evaluation, negative audit, taxonomy freeze, class-specific precision/recall, and human ground truth in `TECH_NOTES.md:92-104` are the correct instincts.

4. **The statistical notes recognize the dominant risks.** Misclassification uncertainty, adaptive-sampling honesty, composition shifts, and the inability to infer that disclosed AI use causes errors are all explicitly acknowledged in `TECH_NOTES.md:106-123`.

5. **WP2 and WP3 have valuable guardrails.** The proposed math-domain detector calibration, controlled transformations, separate known-positive and representative error samples, cumulative severity scale, independent critique, double expert adjudication, and lower-bound wording are strong starting points (`TECH_NOTES.md:125-176`).

6. **Acquisition contains good foundations.** Requests are serial and polite, targeted e-print URLs are version-pinned, OAI pages are archived, query directories are separated, downloaded bytes and SHA-256 are recorded, and tar archives are scanned without filesystem extraction in the new pipeline.

7. **Several earlier defects were actually repaired.** Recent commits improved transient fetch retry eligibility, tar detection, TeX accent normalization, lowercase LLM matching, negation licensing, per-query OAI archives, SQLite thread use in the audit, and response-ID mapping. Keeping the prior reviews in the history provides useful development traceability.

8. **The dashboard has a useful visual direction.** It is small, self-contained, tracker-free, responsive, offers chart/table modes, and explicitly labels its second panel exploratory and selection-biased. Those qualities should survive the rebuild.

9. **Bulk/private data are ignored.** `.gitignore` correctly excludes the corpus, paper cache, SQLite/WAL files, mail, and LaTeX build products. No committed credential was found.

## Launch blockers

### LB-01 — Current prevalence and dashboard numbers are not valid estimates

**Evidence:** `pipeline/report.py:66-97` constructs the denominator from every paper in an ID-prefix frame. It never requires a successful acquisition, a completed scan, or a completed classification. `paper_rollup()` at `pipeline/report.py:40-63` reads all historical snippet classifications, is not restricted to the requested scan runs unless a caller supplies a model label (the caller does not), ignores human review, and collapses versions to paper ID. The selected scan runs constrain only the `flagged` diagnostic count. The site then promotes 142 records as disclosures and a “floor” at `site/dashboard.html:112-116`, although `site/dashboard.html:141-149` later says they are unaudited model classifications with strong selection bias.

**Why this matters:** unobserved, failed, pending, or stale records become implicit negatives, while stale positives from other protocols can enter the numerator. The `142` count is neither a lower bound nor an upper bound: false positives can make it too large and missing metadata disclosures can make it too small.

**Required action:** reports must consume one immutable release manifest and include only paper-versions whose required stages completed under the named protocol. If only a probability subsample receives full text or human review, use a documented two-phase/design-weighted estimator. Human adjudication must override model labels according to a declared rule. The page must call the current objects “preliminary model-classified metadata candidates,” not disclosures, prevalence, or a floor.

### LB-02 — The implementation does not preserve the declared paper-version unit

**Evidence:** `files` is keyed by `(arxiv_id, kind)` (`pipeline/db.py:48-57`); a successful old file prevents `pipeline/fetch.py:111-124` from fetching a newly harvested version. Paths are versionless. `human_review` permits one row per arXiv ID (`pipeline/db.py:90-97`). Classification uniqueness and report rollups do not preserve version identity. Metadata stores only the latest title/abstract/comments and `scan_meta.py` labels them as the latest version.

**Why this matters:** the planned v1 rate, latest-at-cutoff rate, “ever disclosed,” disclosure additions/removals, and revision dynamics cannot be reconstructed. A row can silently claim to describe the latest version while containing earlier text.

**Required action:** make `(arxiv_id, version)` part of every acquisition, extraction, scan, classification, sampling, review, and release key. Store immutable version-specific metadata and bytes. State separately whether each estimand is v1, latest as of a fixed cutoff, all versions, or paper-level ever-disclosed.

### LB-03 — Scan runs are destructive and have already broken evidence provenance

**Evidence:** `pipeline/scan.py:119-143` and `pipeline/scan_meta.py:19-44` delete every hit for a user-supplied run name, then write replacements. Full-text results are committed paper by paper; worker errors are printed only. There is no run manifest or per-paper completion row. Classifier records store hit IDs only inside JSON (`pipeline/classify.py:161-165`), without a foreign key or scan-run field, and reports retain all old labels. The live database already contains 82 missing hit references affecting 28 of 1,227 classifications. A metadata invocation can also reuse `tex-v1` and erase a full-text run.

**Why this matters:** evidence can disappear while a stale label continues to affect public counts; a crash looks like a valid zero-hit run; and a run name does not identify code, lexicon, input, or configuration.

**Required action:** runs and evidence must be append-only and content-addressed. Add run manifests, stage/type namespaces, config/code/lexicon/prompt hashes, input cohort hashes, per-item states, and a terminal `complete` state. Normalize snippet-to-hit and classification-to-snippet relations with foreign keys. Build in staging and publish atomically only after completeness checks.

### LB-04 — Tracked outputs redistribute source excerpts and identifiable labels

**Evidence:** `results/ai_ack_hits.{csv,json}`, `results/ai_ack_report.md`, `results/candidate_papers.{csv,md}`, and `results/manual_review.md` contain long excerpts from papers/source, email addresses and affiliations captured in snippets, and paper-level automated or human labels. This contradicts `PITCH.md:67`, `TECH_NOTES.md:44-50,188-194`, and `.gitignore`'s stated no-full-text policy. Most arXiv article rights remain with submitters; arXiv's metadata terms do not make article text generally redistributable ([arXiv API terms](https://info.arxiv.org/help/api/tou.html), [licensing guidance](https://info.arxiv.org/help/license/index.html)).

**Why this matters:** public Git history is hard to retract, snippets can contain personal data or non-rendered residue, and paper-level labels are searchable assertions about identifiable authors.

**Required action:** quarantine or remove expressive excerpts from the tracked/public tree and assess whether history must be cleaned before launch. Public releases should contain IDs, version, hashes, taxonomy values, source location type, aggregate counts, and links—not raw contexts. Permit only minimal quotations after item-license and necessity review. Add automated excerpt/PII/secret checks and a public/internal field-level publishability matrix.

### LB-05 — Untrusted manuscripts are sent to an unpinned agentic external processor

**Evidence:** `pipeline/classify.py:108-138` sends identified snippets to `codex exec`; `pipeline/audit.py:31-49,105-112` can send up to 180,000 source characters. The command does not select a fixed model; `codex-exec-default` is merely a mutable label. Sandbox `read-only` prevents writes but allows the agent to read repository/corpus content. Paper text is concatenated directly after instructions and can contain prompt injection. Provider, model snapshot, executable version, region, retention, parameters, prompt/schema hashes, raw response, and data-processing basis are not recorded.

**Why this matters:** a malicious or accidental instruction in a paper can manipulate labels or induce data disclosure, vendor drift makes results irreproducible, and sending source/residual content to a subscription service may violate the intended privacy/licensing protocol.

**Required action:** use a non-agentic structured-output API or an approved local model with tools disabled. Run it in an empty, ephemeral filesystem with only the minimal input, no corpus/repository mount, no ambient credentials, and no network beyond the single provider call. Pin and record provider/model snapshot, parameters, API/executable version, prompt/schema hash, input hash, response hash, timestamps, and processing terms. Obtain institutional vendor/privacy review and adversarially test prompt injection.

### LB-06 — There is no scientific ground truth or registered analysis capable of supporting the claims

**Evidence:** the 20 `human_review` rows represent review of retrieved candidates, apparently by one reviewer; there is no negative probability sample, double annotation, codebook version, independent labels, adjudication table, agreement calculation, or held-out test. `pipeline/audit.py` uses one model as the supposed negative audit ground truth. The planned 200–400 gold corpus and preregistration do not exist in the repository.

**Why this matters:** candidate precision can be explored, but pipeline recall and population prevalence remain unknown. LLM agreement is not human ground truth.

**Required action:** finalize a codebook with boundary cases; conduct independent, blinded dual annotation and adjudication; construct probability-sampled negatives as well as enriched positives; hold out time/subfield strata; register the cohort, primary estimands, inclusion probabilities, model/rule freeze, missingness handling, and inference before examining the main outcomes.

### LB-07 — Project identity and legal/open-science terms are unresolved

**Evidence:** there is no `LICENSE`, data license, `CITATION.cff`, privacy notice, terms, correction policy, or institutional role statement. The project name uses “arXiv” as the leading element and the dashboard can look official. The official brand guidance restricts third-party project names that imply or tend to imply an arXiv connection and requires an acknowledgement/non-endorsement for API-derived products ([arXiv name and logo guidelines](https://info.arxiv.org/brand/brand-guidelines.html)).

**Why this matters:** the promise that code and annotations are “open” is currently false in the legal sense, and the name creates a material affiliation/brand risk. This review cannot determine whether permission would be granted.

**Required action:** seek written arXiv authorization for the current name or rename before public launch; add the prescribed acknowledgement and an explicit independent/not-endorsed statement. Obtain institutional review for code, documentation, and derived-data licenses, privacy/legal basis, and the distinction between arXiv metadata and project-created annotations.

### LB-08 — The dashboard is not safe or complete as a public scientific interface

**Evidence:** `site/dashboard.html` is the only site file; no generator connects it to a frozen dataset. It has no doctype, document language, charset, viewport, semantic page structure, methodology/data/contact/correction navigation, canonical metadata, or no-JavaScript fallback. The JSON and several labels flow through `innerHTML` (`site/dashboard.html:165-166,228,338-361,389-414`); future paper/model-derived values containing `</script>` or markup can become stored XSS. Charts/tooltips are largely mouse-only, SVGs lack title/description and keyboard interaction, the impact display lacks a data table, and muted text/series colors need contrast testing.

**Why this matters:** automation would turn currently controlled strings into an injection surface, and the interface does not let readers audit denominators, coverage, uncertainty, provenance, or corrections. Raw subfield counts invite volume-confounded rankings.

**Required action:** generate schema-validated external JSON with `<` safely encoded, use `textContent`/DOM construction, deploy a strict CSP and security headers, and test with hostile fixture strings. Build semantic, keyboard-accessible charts with equivalent tables. Put “what this measures / does not measure,” coverage, validation, uncertainty, release ID, methods, download, citation, correction, and contact links next to every headline result.

### LB-09 — A clean clone cannot reproduce, test, or deploy the project

**Evidence:** there is no README, package/dependency manifest or lock, declared Python/runtime version, migration framework, test suite, CI workflow, formatter/linter/type configuration, build generator, container/environment definition, deployment workflow, runbook, backup procedure, release tooling, `LICENSE`, contribution policy, security policy, or citation metadata. Runtime requirements such as `requests`, `pdftotext`, SQLite features, and `codex` are undeclared. `pipeline/db.py:18-98` runs `CREATE TABLE IF NOT EXISTS` rather than versioned migrations.

**Why this matters:** results depend on an undocumented local machine and mutable services; schema changes cannot be replayed; deployment promises in `DESIGN_PLATFORM.md:88-96` are not implemented.

**Required action:** add a locked package and system-dependency definition, migrations, deterministic fixture pipeline, CI quality gates, documented operations, and a site/release build from a named immutable data artifact before claiming reproducibility or availability.

### LB-10 — Operational stages fail open and untrusted files have no global resource bounds

**Evidence:** `fetch.py`, `scan.py`, `classify.py`, and `audit.py` print item/batch failures but return exit code zero; `pipeline/backfill.sh:11-23` continues after 20 failed attempts and prints “backfill complete.” Fetch reads whole responses into memory, accepts unknown HTTP-200 content as terminal success, and lacks total byte/content-type limits. Gzip/tar processing has no total expansion/member-count bound. `pdftotext` has no timeout/sandbox and its cache is not bound to source hash, version, or extractor version.

**Why this matters:** an orchestrator/CI system will publish partial runs as successful, while oversized or malformed remote artifacts can exhaust resources or attack native parsers.

**Required action:** persist item failures, use retryable/terminal classes, and return nonzero unless the requested completeness policy is met. Stream to atomic temporary files with size/hash/type validation. Bound compressed and decompressed bytes, members, nesting, CPU and wall time. Sandbox native parsers and content-address all derivatives.

### LB-11 — The proposed public data and volunteer workflow contradict the stated ethics and architecture

**Evidence:** `PITCH.md:77-80` and `TECH_NOTES.md:186-194` promise aggregate-only reporting and no per-paper accusations, while `DESIGN_PLATFORM.md:10-17` proposes a public arXiv-ID table containing classification and human-review labels. IDs directly identify authors. The “zero-backend” plan at `DESIGN_PLATFORM.md:18-19` cannot implement the assignment, authentication, submission, share-link validation, moderation, withdrawal, and abuse controls required by the volunteer workflow in `PITCH.md:69-75`.

**Why this matters:** detector/non-disclosure/error labels create reputational risk; asking volunteers to upload assigned papers and expose share links creates licensing, vendor-retention, consent, conflict, and research-participant issues.

**Required action:** keep detector, non-disclosure, and reliability results aggregate-only with minimum-cell suppression. Consider row-level publication only for human-verified explicit statements and only as neutral document-content observations with correction/appeal. Defer the volunteer workflow pending an ethics determination and build it, if justified, as a controlled first-party service rather than a public share-link collection.

### LB-12 — Several headline literature claims require correction or stronger evidence

**Evidence and required corrections:**

- The “math arXiv volume ~20% above its 15-year trend” statement in `PITCH.md:19`, `pitch.tex:26`, and `PRIOR_ART.md:133-140` rests on secondary coverage of an X chart, not a reproducible analysis. Remove it from the headline or reproduce it from official data with seasonality, nonlinear alternatives, policy/structural breaks, category composition, prediction intervals, and code.
- `TECH_NOTES.md:127-129` and `PRIOR_ART.md:85-89` attribute an approximately `1e-5` arXiv false-positive rate to Pangram's cited technical report. That report's held-out scientific-paper result is not an arXiv-math validation and reports a different value. Correct the attribution; treat vendor claims as claims, and make target-domain calibration decisive ([Pangram report](https://arxiv.org/abs/2402.14873), [NBER benchmark](https://www.nber.org/papers/w34223)).
- `TECH_NOTES.md:162-163` and `PRIOR_ART.md:116-119` describe ArxivMathGradingBench as 35 items; the paper describes 35 research papers containing 40 known errors. Correct the unit ([primary paper](https://arxiv.org/html/2605.20531)).
- The 81% survey statement is accurate only as “81% of respondents”: 816 retained respondents came from a highly selected recruitment process and were not a representative mathematics sample. Keep this caveat adjacent to the claim ([survey](https://arxiv.org/html/2411.05025v1)).
- The 1.3% foundation-model result concerns cited adoption and includes non-LLM foundation models; it is not an estimate of writing assistance. The current “different estimand” warning is essential ([primary paper](https://arxiv.org/abs/2511.21739)).
- The prior-art file is a model-assisted scoping pass, not a systematic review. Replace “gap confirmed” with “gap identified in this scoping search” until databases, queries, dates, inclusion criteria, screening decisions, quality appraisal, and independent verification are archived.

## Scientific and statistical review

### 1. Define the WP1 estimands before writing more pipeline code

“AI use in mathematics” is not one measurable quantity. The project already knows this, but the report/site schema needs to enforce it. At minimum, preregister these separate estimands:

1. **Version-level explicit disclosure prevalence:** the proportion of in-frame paper-versions whose rendered document or official arXiv metadata contains an author statement that a named or unnamed tool was used in producing that version.
2. **v1 disclosure prevalence:** the same property specifically in the first version. This avoids survivorship and revision feedback but requires retaining v1 source/metadata.
3. **Latest-at-cutoff prevalence:** the property in the latest version available at a predeclared data cutoff, not “whatever is latest when rerun.”
4. **Paper-level ever-disclosed prevalence:** whether any observed version has such a statement. This is not interchangeable with a version rate.
5. **Disclosure transition rates:** added, removed, or materially changed disclosures conditional on at least two versions and a fixed observation window.
6. **Author-reported role distributions:** the role that the statement reports, not an independently established causal contribution by the tool.
7. **Metadata-visible candidate rate:** useful as an operational screening measure, but not equivalent to full-document disclosure prevalence.

For each, specify the target population, sampling frame, unit, time origin, primary versus cross-listed category rule, treatment of withdrawals/deletions, version censoring, and whether multiple categories are primary, secondary, or fractional. Cross-listed papers should not be casually described as “math.AG submissions”: they appeared in a math.AG announcement stream but can have another primary category.

### 2. Correct the pilot description

The pilot is valuable as a development sample, but the current headline overstates it. The tracked data contain 83 primary new submissions and 46 cross-listings, totaling 129 entries from eight math.AG mailing days. The 20 keyword-positive candidates received manual review; 13 were marked true. There was no random audit of retrieval negatives, so recall is unknown.

The defensible wording is approximately:

> Across eight arXiv announcement days in the math.AG mailing, including 83 primary new submissions and 46 new cross-listings, the prototype retrieved 20 candidates and one manual review pass confirmed explicit AI-use statements in 13. This is an exploratory development sample; retrieval recall has not been measured.

Report the strata separately: 8/83 primary math.AG papers (9.6%, Wilson 95% interval about 5.0%–17.9%) and 5/46 cross-lists, as well as 13/129 (10.1%, about 6.0%–16.5%) only if the combined announcement-stream estimand is explicitly desired. These intervals express sampling variation under a simple-binomial framing; they do not account for unknown retrieval error or selection of dates. “Census” is appropriate only for the listed announcement entries and observed candidate adjudication, not for true disclosures.

The specific paper ID and verbatim statement in `PITCH.md:12-14` add little scientific value to a collaborator pitch and increase reputational/licensing exposure. Keep a restricted evidence register; use a paraphrased, permission-cleared example publicly if a concrete example is essential.

### 3. Build a real annotation and validation study

The proposed 200–400 paper-version gold corpus should be designed by precision targets, not chosen as a convenient range. Rare tool and role classes—especially result-bearing or severe-error categories—will have too few examples in a simple random sample. Use two linked sets:

- An **enriched development/validation set** with diverse known positives, hard negatives, ambiguous language, residual-only mentions, paper-topic mentions, non-use statements, multiple languages/translation contexts, every source format, and prompt-injection fixtures. This estimates class-conditional behavior only with explicit reweighting; it is not a prevalence sample.
- A **probability sample from the target frame**, including scanner positives and negatives with recorded inclusion probabilities, to estimate prevalence and population error. Oversampling can be stratified by scanner score/source/subfield/time, but weights and finite-population counts must be retained.

Annotation requirements:

- A versioned codebook with operational definitions, counterexamples, rendered-evidence rules, and policies for ambiguous/partial statements.
- At least two trained, independent, blinded annotators per primary validation item; conflicts of interest and paper familiarity recorded before labels are revealed.
- A separate adjudicator or specialist tie-breaker; never overwrite original judgments.
- Immutable annotation events with annotator pseudonym, assignment, codebook version, timestamps, confidence/reason, evidence location and source hash.
- Agreement reported for the actual structure: class-specific agreement, multi-label agreement, and weighted ordinal agreement where applicable. A single Cohen's kappa is not enough and can be misleading for rare labels.
- Sensitivity, specificity, precision, negative predictive value/false-omission rate, calibration, and confidence intervals by major stratum; a confusion matrix and error analysis; a held-out temporal/subfield evaluation after the lexicon/prompt freeze.
- Annotator training/qualification and a sample-size/power calculation tied to desired interval widths for primary classes.

The `human_review` schema must support multiple reviewers and adjudication. The Markdown table in `results/manual_review.md` is not a scientific annotation system.

### 4. Repair the recall design and estimator

`pipeline/audit.py:1-6` says the fraction of missed disclosures among scanner negatives estimates scanner recall. It does not. A negative audit directly estimates the **false-omission rate**, `FN / (FN + TN)`, in the audited negative pool. Sensitivity/recall is `TP / (TP + FN)` and additionally requires a valid estimate of true positives in the target population.

A defensible two-phase design is:

1. Define an immutable completed first-stage run over a known frame.
2. Sample from each first-stage output stratum (for example high/medium/low score and nominal negative), with known probabilities.
3. Apply the same human reference standard to sampled positives and negatives.
4. Estimate stratum-level error and expand it to the frame with design weights; bootstrap or analytically propagate phase-one and validation uncertainty.
5. Treat acquisition/extraction failures as missing process states, never negatives. Report them separately and perform a prespecified missingness sensitivity analysis.

If sensitivity/specificity correction is used, the simple Rogan–Gladen expression can be unstable, exceed logical bounds, and assumes validation performance transports across field, year, source type, language, tool and section. Prefer a stratified two-phase estimator, joint bootstrap, or Bayesian measurement-error/latent-class model with transparent priors and sensitivity analyses. Do not allow a large unvalidated corpus to swamp validation uncertainty.

### 5. Make the sampling frame reproducible

OAI `from`/`until` restrict record modification datestamps, not v1 submission dates. A selective OAI backfill therefore includes old papers modified in the window; the live database indeed contains v1 dates back to 1991 while its harvested OAI datestamps begin in 2024. Use OAI for incremental updates and deletion records, but construct historical submission cohorts from a complete bootstrap such as the official metadata dump and filter by version date.

For longitudinal work:

- Freeze a frame release with exact input page/object manifests and cutoff timestamp.
- Define subject scope using primary category at the relevant version/cutoff and separately characterize cross-list exposure.
- Retain tombstones and withdrawal status rather than silently keeping or dropping records.
- Record every paper-version's eligibility, selection probability, acquisition outcome, and censoring state.
- Avoid arXiv-ID month prefixes as dates; use parsed v1/version timestamps.
- Account for clustered dependence among versions of the same paper and, for author analyses, among papers/authors. Use cluster-robust or hierarchical inference rather than treating every version as independent.
- Standardize temporal comparisons for changing subfield composition, and prespecify the baseline distribution.
- Distinguish discovery/exploration from confirmatory charts; address multiplicity with a small registered core or appropriate false-discovery/familywise control rather than selectively narrating dozens of subgroups.

### 6. Refine the WP1 taxonomy

The broad cross-tool ambition is appealing, but the code currently implements only a small fraction of the taxonomy in `TECH_NOTES.md:74-90`. The classifier only acts on `llm` and `generic`; numerical software, custom code, search/retrieval, visualization and several specialized categories are absent or incomplete. CAS names are highly ambiguous, and `Sage` is a strong unconditional match despite the notes naming “Sage as a name” as a known false positive.

Recommended construct changes:

- Separate **tool as object of study**, **tool as scientific instrument**, and **tool as production assistance** before assigning roles.
- Replace “epistemic impact” in public labels with **author-reported contribution role** unless independent evidence supports the stronger inference.
- Avoid “cosmetic” for translation and substantial language mediation; it can minimize real labor and disadvantage multilingual authors. “Language/style assistance” is clearer and less normative.
- Rename “disclosure quality” to **disclosure completeness under this schema**. Variable community rules do not justify a compliance score.
- Permit `unknown`, mixed, and ambiguous values; keep roles multi-label.
- Freeze a machine-readable taxonomy/lexicon version before evaluation. Every label should carry that version.
- Co-design boundary cases with mathematicians across subfields, research-integrity/metascience expertise, and scholars familiar with multilingual academic writing.

The lexicon should be a high-recall retriever, not a verdict engine. Test every term against labeled rendered and residual contexts, report per-term yield/precision, and make additions on a development corpus before evaluating a frozen release.

### 7. WP2 detector study: worthwhile only with stronger independence and fairness controls

The best part of the WP2 plan is the insistence on target-domain calibration. Preserve it and add:

- Multiple detector families, including open baselines; do not make a single proprietary vendor the measurement definition.
- Exact detector product/model/version, API date, threshold, text normalization, chunking/aggregation, language and refusal behavior frozen before outcome analysis.
- Separate calibration, threshold-selection, and final test splits. Do not tune on the same pre-LLM math set used to report false-positive performance.
- Controlled, paired transformations made from mathematics prose: grammar correction, translation, style rewrite, partial generation, mixed human/model edits, and different model families/decoding settings. Preserve a human original and document the intervention.
- Error metrics by subfield, section, formula density, original language/translation, length, LaTeX/PDF extraction path, template, editing intensity and model family, with worst-group uncertainty. Do not infer sensitive demographic attributes from names.
- The disclosure × detector cross-tab only for roles plausibly visible to a prose detector, exactly as the notes already propose.
- Independent replication and explicit disclosure of vendor funding, data access, authorship and conflicts. Proprietary outputs should be called auditable under a frozen protocol, not independently reproducible.

Detector scores must never become paper-level allegations or author rankings. A detector measures similarity under a benchmark-specific decision rule, not authorship, policy compliance, deception, or misconduct.

### 8. WP3 reliability audit: preserve the framing, postpone the prevalence claim

The distinction between a known-positive benchmark and a representative prevalence sample is scientifically sound. The cumulative S0–S5/U rubric and “discoverable under the audit protocol” lower-bound language are also good. Before execution, add:

- An operational definition of “pure math,” eligible version and publication status.
- A precision-based sample-size calculation for each primary cumulative threshold. A 100–300-paper pilot is unlikely to estimate rare S4/S5 outcomes tightly.
- A fixed scrutiny budget per paper: model calls, time, tools/search access, context, stopping rules, retries/refusals and permitted external sources.
- Blinded specialist matching, independent adjudication, conflicts/recusal, nonresponse handling, and a preregistered rule for author responses. Authors can supply evidence but should not unilaterally define truth.
- A private, time-split known-error benchmark to reduce contamination from public benchmark memorization.
- Clear separation between flags, independently confirmed issues, author-contested cases, and unresolved `U` cases.
- A correction/appeal process and careful notification timeline before any case is public.
- Licensed access for review sources; MathSciNet text should not be assumed redistributable or reusable for model processing.

WP3 has a substantially different harm profile, expert burden, validation model, and publication norm from WP1. It should have a separate protocol, ethics review, repository/release boundary, and paper.

### 9. Author/productivity and “market share” analyses need restraint

OpenAlex disambiguation is useful, not solved. Validate linkage error across naming systems, affiliations, career stages and fields; propagate match uncertainty; permit correction/opt-out; and do not publish author-level rankings. Avoid inferring gender, nationality, ethnicity or English proficiency from names. Any productivity association is descriptive and vulnerable to selection, team composition, cohort and field confounding.

“Tool market share” is also misleading because only disclosed tools are visible, disclosure propensity differs, and papers can name multiple tools. Use **share of named tools among observed explicit disclosures**, with multi-label denominators and uncertainty.

### 10. Upgrade the literature review

Turn `PRIOR_ART.md` into a living evidence table with fields for citation/DOI, version, population, years, unit, estimand, method, validation, headline result, limitations, conflicts/funding, license/access, and last verification date. Archive search databases, exact queries, dates, deduplication, inclusion/exclusion decisions, and reviewer verification. Label the current document a scoping review. Use primary sources for scientific claims and reproduce high-leverage descriptive claims in-repo where feasible.

Useful claim qualifications already established by this audit include:

- The Nature study's “up to 9%” is a population-level word-frequency estimate, not a per-paper authorship verdict ([Nature Human Behaviour](https://www.nature.com/articles/s41562-025-02273-8)).
- The 81% survey result is a respondent statistic from a strongly self-selected, non-math-specific sample.
- The cited-foundation-model study measures cited adoption, including vision models, not undisclosed LLM writing.
- “To Err Is Human” reports model-flag and selected validation results, not confirmed population error prevalence ([primary paper](https://arxiv.org/html/2512.05925v1)).
- The closest arXiv detector precedent sampled Pangram and calibrated its pre-LLM false positives on CS rather than mathematics; this preserves the value of math-specific calibration but narrows novelty claims.

## Implementation and data-system review

### 1. `pipeline/db.py`: a useful spine, but not a research ledger

Positive foundations are the compact schema, SQLite WAL mode, parameterized values, SHA fields, and separation of metadata, versions, files, hits, classifications and human review. SQLite is entirely reasonable for a single-machine 5k–20k-paper WP1 run.

The schema does not yet enforce its scientific meaning:

- Paper-version identity is missing from primary/unique keys as described in LB-02.
- There are no foreign keys, `CHECK` constraints, controlled vocabularies, non-null requirements for completed objects, or referential deletion policy.
- There are no run/protocol/cohort/item-state tables, so absence of a positive hit is overloaded to mean not selected, not acquired, failed, skipped, negative, or deleted.
- Classifier labels are opaque JSON blobs. This is acceptable for retaining raw provider output, but publishable normalized values, evidence and status need constrained tables.
- Human review overwrites history and cannot represent assignments, two reviewers, adjudication, codebook version or recusal.
- `connect()` runs DDL and requests WAL even for readers; there is no read-only release mode, schema version, migration history, backup/snapshot logic or compatibility check.
- Paths and database location are hard-coded to the checkout. There is no environment/config object separating source, operational state, cache and releases.
- Common frame/run/version queries lack matching composite indices; `substr(arxiv_id,1,4)` prevents normal date-index use.
- Full contexts are duplicated per hit, inflating storage and making redaction/correction hard.

Use a migration tool and schema version from the first public release. Enable foreign keys explicitly, validate at insertion boundaries, and take a SQLite backup/snapshot before every release. PostgreSQL is unnecessary for the initial trusted single-writer pipeline; immutable Parquet/JSON release artifacts should handle public analytics. Move to a service database only if a real multi-user backend is introduced.

### 2. `pipeline/harvest.py`: preserve raw-page archiving, fix cohort and state semantics

Good choices include OAI-PMH, a descriptive user agent, serial requests, long timeouts, raw gzipped pages, and per-query directories. Remaining problems:

- Deleted OAI records are discarded at `harvest.py:54-58`, so previously stored records never receive a tombstone.
- `reparse()` at `harvest.py:176-183` globs only legacy root pages and ignores all current per-query subdirectories.
- A successfully completed state has a null token but no immutable completion marker/query manifest; rerunning begins the same query again under continued page numbering.
- State and page writes are not atomic and carry no checksums, response headers, endpoint, code/parser version or complete query fingerprint.
- `INSERT OR REPLACE` overwrites current metadata and `harvested_at`; it does not retain a history of version-specific metadata snapshots or prove that the newer OAI datestamp won.
- The retry parser accepts only integer `Retry-After`, not the valid HTTP-date form; it accepts zero. The observed backfill log contained repeated zero-second 503 retries, which can hammer the service. There is no jitter or minimum/maximum wait.
- XML and response sizes/record counts are unbounded. Use bounded responses and a hardened XML parser.
- `from_date`/`until_date` enter directory names without format validation, and upstream arXiv IDs are not validated before later becoming filesystem paths.
- The user agent exposes a personal Gmail address rather than an institutional role address.

Implement an immutable `harvest_run` manifest, atomically write page/state files, store page hashes and OAI request/response metadata, record deletions, reject stale upserts, and allow reparsing only an explicit run. Validate dates and `^\d{4}\.\d{4,5}$` IDs. Enforce at least the official one-request-per-three-seconds/single-connection behavior and respectful capped backoff ([arXiv API terms](https://info.arxiv.org/help/api/tou.html)). For historical cohorts, bootstrap from a complete official dump and use OAI only for updates ([arXiv bulk access](https://info.arxiv.org/help/bulk_data.html)).

### 3. `pipeline/backfill.sh`: never claim success after exhausted failure

The chunking and patient 12-minute retry concept are sensible. The script lacks `set -euo pipefail`, does not verify `cd`, does not retain a failure flag, proceeds after all 20 attempts fail, and always prints “backfill complete” with success. Make every chunk an explicit job with a durable state/manifest. Exit nonzero if any requested chunk is incomplete and print a machine-readable summary. The Python harvester should own retry/resume policy where possible; the shell wrapper should orchestrate, not reinterpret success.

### 4. `pipeline/fetch.py`: good politeness and hashing, incomplete identity and containment

Good features are serial access, a four-second delay, seeded order, version-pinned request URLs, retries, byte counts and SHA-256. The claim that a partial fetch is an unbiased sample is true only for the particular shuffled eligible list and limit; the eligibility list, seed, inclusion probability and execution cutoff must be stored to make that fact usable.

Required fixes:

- Key and path objects by version and content hash. A new version must generate new work.
- Stream downloads to a same-filesystem temporary file with a compressed-byte limit, redirect/host allowlist, content-length/type/magic validation, hash during transfer, `fsync`, and atomic rename.
- Do not record `ok_unknown_format` as a successful terminal source. Quarantine it and require explicit parsing/coverage status.
- Cap and correctly parse `Retry-After`, add jitter and a minimum server-respectful wait, and distinguish retryable from terminal errors.
- Validate arXiv IDs before path construction; resolve paths and prove they remain under the configured object-store root. Reject separators, control characters and symlinks; use safe no-follow writes.
- Record acquisition attempts separately from immutable assets, including URL, redirects, status, headers, version, expected/observed checksum, bytes, error class and tool version.
- Prefer official bulk objects/manifests for the main sample and verify authoritative checksums when available ([arXiv S3 access](https://info.arxiv.org/help/bulk_data_s3.html)). Keep `export.arxiv.org` for small targeted pulls. Deprecate legacy downloads from main article endpoints.
- Return nonzero or a formal partial status when requested files fail; do not let stdout be the only error ledger.

### 5. `pipeline/scan.py`: static archive access is good; rendered-evidence and safety are missing

Scanning tar members without extraction avoids path traversal and small-file churn. The scanner also excludes comments in the common case and retains source member names/locations, which are useful internal evidence.

However:

- Every `.tex`, `.ltx` and `.txt` member is scanned, including unused drafts, examples, reviewer material and private residue. This violates the documented default and permits residual-only evidence to become a paper label.
- Ancillary names are recorded only if the suffix is non-text; an empty `claude-transcript.tex` is missed, while treating any ancillary artifact as ordinary evidence raises privacy concerns.
- Individual members over 10 MiB are silently skipped; there is no total member count, total expanded bytes, compression ratio, filename length, recursion, CPU or wall-time limit. Single-file `gzip.decompress` is unbounded.
- `(?<!\\)%.*` gets TeX escaping parity wrong: `%` after an even number of backslashes begins a comment but is retained. Regex stripping is also not verbatim-aware.
- One invalid UTF-8 byte causes an entire member to be decoded as Latin-1, corrupting otherwise valid Unicode.
- The scanner's normalized offsets are not durable source locators. `normalize()` changes characters before offsets/contexts are saved.
- `pdftotext` is a native parser invoked without timeout or sandbox. An empty/failed extraction can become a negative, and its cache is not keyed by source hash/version/parser version.
- Worker errors, large-member skips and empty extraction are printed but not stored. A zero-hit paper has no positive proof of completed coverage.
- Each regex independently scans the full text. This is acceptable for the pilot, but a combined literal matcher plus targeted regex/context pass would scale better and be easier to profile.

Build a static, non-executing root-document and `\input`/`\include` dependency graph, or verify candidate text against rendered PDF. Record residual-only and artifact-only findings in a restricted quarantine that cannot promote public labels. Use a real tested TeX lexer for comments/verbatim, bounded archive readers, per-member hashes, explicit `complete/partial/error` coverage, and sandboxed pinned PDF extraction. Never execute submission TeX or included code.

### 6. `pipeline/lexicon.py`: useful seed, not yet a validated instrument

The tiered `Term` abstraction, shared scanner, context licensing, retained known-false-positive class and normalization step are good building blocks. The current rules remain a hand-built development lexicon:

- Only LLM/generic hits reach the classifier; the documented full tool taxonomy is not implemented.
- Common words and names such as Sage, Maple, Singular, Lean, Google, agent and model create context-dependent ambiguity. Some supposedly strong terms still need domain-specific disambiguation.
- A known-false-positive regex spanning multiple words can downgrade a legitimate intervening hit.
- A negation, acknowledgment or usage cue anywhere in a wide window can be incorrectly attached to another nearby term.
- Source normalization and one-window context do not respect sentences, sections, macros or rendered ordering.
- No lexicon version is stored, and there are no unit/golden tests, per-term metrics, change-control process or frozen release.

Represent the lexicon as versioned data with term IDs, aliases, tier, context/FP rules, provenance and rationale. Add a labeled fixture for every rule and every known collision. Measure incremental yield and precision when adding a term; freeze the lexicon before held-out evaluation.

### 7. `pipeline/classify.py`: cache and evidence semantics are unsafe

Batch checkpointing, output-length checks, and the recent attempt to map echoed IDs are useful. Critical defects remain:

- `input_hash` covers only source kind, terms and context. It omits paper, version, member, scan run, source hash, code, prompt, schema and model. The global `done` set can skip identical boilerplate in another paper or silently reuse output after protocol changes.
- Nearby hits are merged, but only the longest original context is retained. Other merged hits can be absent from the sent snippet.
- Missing or malformed response IDs fall back to positional indices; IDs need to be mandatory and unique.
- The parser extracts the first bracketed JSON array and validates only count/coverage. It accepts arbitrary enum values, fields, list lengths, confidence values, oversized strings and invented quotes. Inspection found 85 of 1,227 returned quotes absent from all stored source contexts.
- A batch mixes up to 30 unrelated papers, so one injected document can influence 29 other labels and the provider sees a broader set than necessary.
- The mutable default model is not pinned, while the database implies it is an identity.
- Failed batches are printed, not durably stored, and the command exits zero.
- The Markdown/report pipeline later trusts model strings as data, creating presentation and CSV risks.

Hash the canonical complete input envelope and protocol. Require structured output with `additionalProperties: false`, enums, ranges and length/item limits. Require exact IDs, normalized evidence quotes that are substrings of the supplied text, and source offsets/hashes. Quarantine invalid output. Process one paper at a time when possible; never mix security domains for cost convenience. Retain restricted raw responses for audit, but publish only validated normalized fields. A model prediction must not directly become a public reputational label.

### 8. `pipeline/audit.py`: the current “full-paper” audit is neither full nor a recall estimator

In addition to the statistical error discussed above:

- Files are concatenated in archive order and cut at 180,000 characters, systematically risking loss of end matter and acknowledgments.
- PDF-only papers are excluded and residual TeX files are included.
- The negative pool proves only that a successful source file exists and no positive hit row exists; it cannot prove that the named scan completed.
- Sampling is reproducibly shuffled, but inclusion probabilities, pool manifest and selected version/source hashes are not stored.
- Completion deduplication uses only paper ID; the saved hash is only the paper ID and omits run, version, model, source and prompt.
- Results are not consumed by `report.py`; failures still leave the process successful.
- The model is the sole judge and can return fabricated quotes/fields without validation.

Replace this module with the human-anchored two-phase audit described above. Machine full-document review can remain a second retrieval method, operating over bounded root-reachable chunks with explicit tail/acknowledgment coverage, but it is not ground truth.

### 9. `pipeline/report.py`: arithmetic primitives are sound, population logic is not

The Wilson implementation and zero-denominator guard are correct, and set-based paper counts prevent multiple hits from directly double-counting a numerator. Those local properties do not repair the cohort mismatch in LB-01.

Further issues:

- The docstring says creation-date frame, but the query uses ID prefixes.
- The classifier model, protocol, version and scan relation are not fixed.
- `human_review` and negative-audit results are ignored.
- The highest-ranked historical polarity wins; a stale positive is effectively permanent.
- Multi-snippet author-use labels merge tools/models/categories and maximum impact, but retain an arbitrary first location and do not represent multiple disclosure locations.
- Tool/category/impact tables are calculated over every historical author-use paper, not necessarily the requested month/frame.
- Markdown values are not escaped, so arbitrary provider strings can corrupt or inject markup.
- The report does not show acquisition, scan, classification, validation or missingness denominators, release ID, data cutoff, sample weights, uncertainty from measurement, or suppression rules.

Rewrite reporting as a pure function over an immutable public release table plus a predeclared analysis specification. Fail closed if manifest, schema, stage completeness, frame totals, validation version or expected invariants are absent.

### 10. `pipeline/scan_meta.py`: fast screening needs a cohort and completion ledger

Scanning metadata is a sensible cheap first signal. It currently scans every current `papers` row, has no date/cohort argument or snapshot, deletes a named run, carries current metadata as the latest version, records only positives, and cannot establish which rows completed. Make it consume a frozen cohort and versioned metadata snapshot through the same immutable run framework as full text.

### 11. `pipeline/validate_awesome.py`: external validation can silently validate nothing

The concept of cross-checking a known-positive external list is good, but `ROW_RE` requires a specific bold Markdown row format that the referenced upstream table no longer uses. Zero parsed entries still produces a valid-looking output and success. The window is again inferred from ID prefix, and external-list inclusion is not a ground-truth disclosure label.

Use a pinned source commit/hash and robust parser with schema/row-count sanity bounds; fail if zero or unexpectedly few rows are parsed. Record source version/license, distinguish list membership from disclosure evidence, and manually review unmatched/missed cases under the validation codebook.

### 12. `arxiv_ai_ack_scan.py` and `WORKFLOW.md`: deprecate the divergent legacy path

The legacy script successfully demonstrated the idea and produced the pilot. It now duplicates acquisition, extraction, lexicon, classification, caching and output behavior with different semantics from `pipeline/`:

- Downloads are unversioned and use main `arxiv.org` article/e-print endpoints, so reruns can retrieve different bytes and do not follow the documented scaled-access plan.
- Downloads/decompression and native PDF parsing are unbounded/unsandboxed.
- It extracts and scans all small TeX-like residual files, has the same TeX `%` parity bug, silently skips files over 5 MB, and has no per-paper coverage ledger.
- Source/PDF duplicates are emitted as separate hits; raw snippets and local paths flow into tracked Markdown/CSV/JSON.
- CSV cells are not neutralized for spreadsheet formulas. A tracked snippet at `results/ai_ack_hits.csv:54` already begins with `=`, demonstrating the issue. Quoting CSV syntax does not stop Excel/LibreOffice evaluation.
- Markdown escaping handles only pipes/newlines, not raw HTML.
- Network/scan errors are written into `errors.json` but the process returns zero.
- `WORKFLOW.md` documents only this obsolete path and names `ai_mention_in_acknowledgements`, a status the current script never emits.

Keep a tag or archived fixture for pilot reproducibility, then remove it from the supported execution path. Port only necessary, tested features to `pipeline/`; make `WORKFLOW.md` a current operator runbook. Publish Parquet/JSON as canonical machine data and, if CSV is offered, generate a separately labeled spreadsheet-safe export that prefixes formula-leading cells after whitespace/control normalization.

### 13. Local permissions and data-at-rest controls are not enforced

In this workspace the database, corpus directory, paper directory and fetch log were mode `0777`, likely influenced by the mounted filesystem, but the code relies entirely on ambient umask. These stores can contain source residue, personal information and model outputs. Production must create service directories as `0700`, files/database/WAL/backups as `0600`, use a dedicated least-privilege account, encrypt managed backups, avoid shared personal accounts, log administrative access, and document retention/deletion/incident recovery. Tests should assert effective permissions where the platform supports them.

## Recommended target architecture

The three-layer idea in `DESIGN_PLATFORM.md` is proportionate if the boundaries are made real:

```text
official metadata/bulk objects
        |
        v
immutable raw store + checksums/tombstones
        |
        v
version catalog and frozen cohort manifests
        |
        v
bounded extraction -> immutable scan run -> validated machine labels
        |                                      |
        +---------------- human sampling/review/adjudication
                                               |
                                               v
                              frozen internal analysis snapshot
                                               |
                              publishability/redaction/QA gate
                                               |
                                               v
                       immutable aggregate release + DOI/checksums
                                               |
                                               v
                                    generated static website
```

### Minimum logical entities

- `papers` and immutable `paper_versions`, including version-specific metadata snapshots and tombstones.
- Content-addressed `assets` plus `acquisition_attempts`; never overwrite bytes.
- `cohorts`, `cohort_items`, strata, eligibility and inclusion probabilities.
- Versioned `protocols` for acquisition, extraction, lexicon, classifier, annotation and analysis; each has canonical config and code/container hashes.
- Append-only `runs` and `run_items` with `pending/running/succeeded/partial/failed/skipped`, timestamps, error class and input/output hashes.
- Deduplicated `document_members`/render graph, `snippets`, `scan_hits`, and normalized evidence spans.
- Raw restricted `model_responses`, validated `classifications`, and explicit evidence junctions.
- `annotation_assignments`, immutable reviewer `annotations`, `adjudications`, conflicts and codebook versions.
- `samples`/selection events so every probability and validation estimate can be reconstructed.
- `releases`, input/run manifests, aggregate tables, checksums, supersession/correction ledger and publication-policy version.

The run identifier should be a digest of a canonical manifest, with a human alias only for convenience. Every downstream run must name exact upstream completed run IDs. No stage should infer success from missing rows.

### Storage and scale

- Use a content-addressed local/object store for source/PDF bytes and immutable compressed raw OAI pages. An official S3 bootstrap is preferable for historical scale; targeted export pulls remain useful for small gaps.
- SQLite plus WAL is sufficient for a controlled single-writer WP1 pipeline if releases are built from a backup snapshot. Add bounded transactions and composite indices. Use PostgreSQL only for a later authenticated community application.
- Export restricted internal analysis snapshots and public aggregate releases separately. Parquet is suitable for research reuse; compact JSON/CSV aggregates are suitable for the site.
- Parallelize CPU-bound extraction/scan across immutable jobs, not database mutation. Workers write isolated result bundles; one validated writer commits them or publishes a new partition.
- Bound queue depth, bytes, RAM, CPU, wall time, members and model tokens/cost. Add circuit breakers based on failure/error rate and a run budget requiring explicit approval to exceed.
- Profile before optimizing. The current approximately 100 regex passes per text will scale linearly; a literal multi-pattern matcher followed by targeted regex/context classification is a likely future improvement, but correctness and run provenance come first.

### Release contract

Each scientific release should have a stable semantic version and DOI, never be overwritten, and contain:

- Manifest JSON with release ID, cutoff, code commit, container/lock hashes, input cohort and upstream run IDs/hashes.
- Data dictionary, taxonomy and codebook versions.
- Aggregate tables and uncertainty, with explicit numerators, denominators, weights, missingness and suppression.
- Validation report and prespecified acceptance gates.
- Machine-readable provenance for every published column.
- Checksums/signatures, SBOM, citation file and separate code/data licenses.
- Limitations, privacy/publication policy, processor list, contact and correction/appeal link.
- A correction/withdrawal ledger. A correction creates a new release and marks affected older releases as superseded; it never silently replaces bytes.

Use Zenodo as the canonical versioned, citable dataset from the first scientific release and mirror identical checksummed assets in a GitHub Release. A viewer such as Hugging Face may be an optional mirror, not a competing canonical source.

## Security, privacy, licensing and ethics review

### 1. Threat model

Treat all of the following as untrusted:

- OAI metadata fields, identifiers until validated, titles/comments/abstracts and deletion state.
- Article archives, filenames, TeX/PDF bytes, decompression structure, source comments and ancillary files.
- Text inside a paper, including instructions addressed to a model or tool.
- Model responses, tool/model names, quotes, JSON and confidence values.
- Community PRs, chart/query specs, dependencies, workflows, share links and contributor claims.
- External-list Markdown and every future data mirror.

Protected assets include the non-redistributable corpus, source residue, personal data, provider credentials, institutional systems, unpublished labels/evidence, annotation identities, budgets, release signing credentials, and the integrity of scientific results. A read-only filesystem protects only against writes; it does not stop reading, exfiltration, network calls, child processes, denial of service or manipulated scientific output.

### 2. Model execution isolation

Prompt wording is not a security boundary. If any agentic CLI is retained for research experimentation, each paper should run under a disposable UID in an ephemeral empty-workdir container/VM, with only a minimal redacted input mounted, no repository/corpus mount, an allowlisted environment, no general network, no secrets, read-only root, tmpfs output, process/CPU/RAM/file/token/time caps, and whole-process-group termination. Do not batch unrelated papers. Add canary/injection fixtures and quarantine suspicious output, but use a non-agentic structured-output service or local inference for the production classifier.

The processor protocol must name provider, controller/processor roles, region/transfers, retention, training opt-out, access control, incident procedure and deletion. A personal subscription is not an adequate production research-processing arrangement. Data minimization means sending the smallest rendered passage necessary and never concatenated residual source by default.

### 3. Untrusted-file and path hardening

- Stream and cap network responses; limit redirects to expected HTTPS arXiv hosts.
- Validate magic and supported format before an asset is marked usable.
- Enforce per-member and total uncompressed bytes, compression ratio, member count, pathname length, recursion/nesting, output bytes, CPU, RAM, PIDs and wall time.
- Use a hardened XML parser and response/record limits for OAI.
- Sandbox pinned, patched Poppler/`pdftotext` and any archive/native parser in a networkless disposable process.
- Validate IDs and all database-derived paths, resolve them, and assert containment under the configured root. Reject symlinks and use atomic no-follow writes.
- Never compile/execute submitted TeX, scripts, binaries or macros.
- Store parser/extractor versions and hashes so a security upgrade produces a new derivative rather than silently reusing an old cache.

### 4. Output injection and browser security

The current dashboard's XSS sink is dormant because its literal values look benign; automation will make it exploitable. Move data to schema-validated external JSON or serialize `<` as `\u003c`, create DOM nodes with `textContent`, and never concatenate untrusted HTML. Escape raw HTML in generated Markdown. Use a restrictive Content Security Policy, `object-src 'none'`, `base-uri 'none'`, `form-action 'none'`, strict MIME/nosniff, referrer policy and minimal connect/image sources. Prefer no inline script/style so CSP remains enforceable.

CSV requires a separate security treatment. Canonical Parquet/JSON avoids spreadsheet execution. A spreadsheet-safe CSV must prefix any cell whose first non-whitespace/control character is `=`, `+`, `-` or `@`, and tests must cover formula and DDE/URL cases. Make it explicit that raw CSV is not safe to open interactively.

### 5. Public/internal publishability matrix

Adopt and enforce a field-level policy before producing another report:

| Data | Internal restricted | Public default |
|---|---|---|
| Descriptive arXiv metadata | Yes, with provenance | Permitted under applicable metadata terms, linked and attributed |
| Article/source/PDF bytes | Yes, access-controlled and retained only as needed | Never redistributed by default |
| Raw snippets/quotes/source paths/comments/ancillary names | Restricted evidence only | No; exceptional minimal quote after license/necessity review |
| Model raw responses/prompts | Restricted, because they can echo source/PII | No |
| Machine detector/non-disclosure/error label keyed to paper | Restricted | No |
| Human-verified explicit disclosure keyed to paper | Restricted by default | Only after policy/legal/ethics approval, neutrally worded and correctable |
| Aggregate disclosure/validation statistics | Yes | Yes, after completeness, validation, uncertainty and disclosure-control gates |
| Rare subgroup/time cells | Yes | Suppress or combine below a predeclared minimum |
| Annotator/contributor identity | Controlled | Only with consent; otherwise pseudonymous/aggregate |

ArXiv IDs are not anonymous: they resolve directly to papers and authors. Treat paper-level data as identifiable and potentially reputational even when it contains no conventional contact field.

### 6. Privacy and research governance

Before public data or participant recruitment, obtain an ETH/institutional ethics and privacy determination rather than assuming a research exemption. Document the controller, legal basis, purpose limitation, data minimization, retention, processors/transfers, access roles, data-subject rights as applicable, DPIA/risk assessment, breach response and contact. Useful starting points are the [Swiss FDPIC research guidance](https://www.edoeb.admin.ch/en/research-and-data-protection) and, where applicable, [GDPR definitions and rights](https://eur-lex.europa.eu/eli/reg/2016/679/oj).

Create correction, objection, appeal and takedown procedures with response targets and an escalation owner. Preserve scientific reproducibility through immutable corrections/supersession notices rather than refusing correction or silently editing an old asset. Document conflicts of interest for maintainers, annotators, model/detector vendors and authors whose papers are reviewed.

### 7. Community experiment

The current proposal would make volunteers research participants and data processors: they receive assigned papers, upload them to commercial accounts, and share model conversations. Risks include vendor retention/training, copyright, volunteer identity leakage, paper text in public links, unequal subscription access, prompt/model drift, unverifiable expertise, conflicts, harassment, adversarial/Sybil submissions, uncompensated labor and inaccessible participation.

If pursued after WP1:

- Obtain an ethics determination and participant consent/debriefing plan, particularly for seeded known-error tasks.
- Provide a controlled first-party interface with approved API/local processing; do not require public conversation share links.
- Define compensation/credit, withdrawal, retention, accessibility, moderation and safeguarding.
- Train and qualify contributors, stratify/match expertise, record conflicts, double assign and independently adjudicate.
- Authenticate/rate-limit while collecting the minimum identity data.
- If links are ever accepted, allowlist exact HTTPS provider hosts, never server-fetch arbitrary URLs, strip tokens, prevent redirects/SSRF, and render them safely with explicit consent.
- Keep contributions out of public statistics until they pass the same reference-standard and provenance gates as staff annotations.

### 8. Licensing and attribution

Choose separate, institutionally approved licenses for source code, documentation and project-created data; add a `NOTICE` for third-party material and dependencies. Do not imply that arXiv's CC0 descriptive metadata status automatically licenses project annotations or paper excerpts. Link each paper back to arXiv, preserve item licenses internally, and add the official arXiv acknowledgement/non-endorsement required for API-based products. Record terms for OpenAlex, detector/model providers and release hosts.

### 9. Governance and sustainability

The design currently anchors trusted compute and an AWS fallback to one person's accounts. That is a bus-factor and correction-risk problem. Before operation, require:

- Institution-owned storage/service identities and role email rather than personal Gmail in automated user agents.
- At least two authorized maintainers and two-person approval for Tier-0/release changes.
- CODEOWNERS/protected branches and explicit scientific, security and data-steward roles.
- Documented funding/vendor relationships and conflict policy.
- Encrypted backup, restore drill, credential rotation, incident runbook and cold-start recovery tested by a second maintainer.
- A maintenance/deprecation policy and budget/cost alerts.

## Platform, deployment and public-impact review

### 1. Keep the static architecture, narrow the claims

A static site generated from small precomputed aggregates is the correct v1 architecture: inexpensive, cacheable, auditable, accessible without an account, and structurally separated from the corpus. A full browser-side annotation table is not needed for the public-interest goal and increases privacy and bandwidth risk. DuckDB-WASM should be an opt-in advanced explorer over a disclosure-controlled, sharded public dataset with a no-WASM fallback—not a dependency for primary pages.

The current community-assignment idea cannot be “zero backend.” If ever built, it needs a separately threat-modeled authenticated backend, moderation and data governance. Do not compromise the clean static public site to force both products into one architecture.

### 2. Public information architecture

Build a small set of durable routes, each generated from the same release manifest:

- `/` — one carefully worded headline finding, validation/coverage summary, latest release and plain-language limits.
- `/explore` — precomputed core charts with filters, uncertainty and equivalent tables.
- `/methodology` — estimands, cohort, collection, taxonomy, validation, statistics, source/license handling and reproducibility.
- `/data` — DOI, release notes, schema, checksums, licenses, citation and example queries.
- `/about` — team, institutions, funding, conflicts, governance and required arXiv non-endorsement.
- `/corrections` — correction/appeal/takedown process and machine-readable ledger.
- `/updates` — release/changelog feed, including RSS/Atom.

Every chart should display or link the release ID and contain: the exact question, numerator, denominator, population/unit/time, data cutoff, coverage/missingness, validation status, interval definition, suppression, a one-sentence interpretation, and a “does not show” statement. Provide downloadable chart data and a stable share URL. Never lead with a sensational count and reveal the caveat later.

### 3. Correct dashboard language and comparisons

- Replace “with AI-use disclosure” with “preliminary model-classified metadata candidates” until human validation.
- Remove “floor.”
- Do not rank raw subfield counts without denominators. Show rates only for sufficiently covered/validated strata, with intervals; retain volume context.
- Rename “market share” to “share of named tools among observed explicit disclosures.”
- Present author-reported role, not established epistemic causation.
- Mark right-censored/incomplete edge periods and withhold them from trend lines rather than filling them with zeros.
- Place validation and coverage at the visual top, not in a distant footnote.
- Separate a preregistered “core findings” area from a clearly labeled exploratory/community gallery.

### 4. Accessibility and resilience

Add a valid semantic document (`doctype`, `html lang`, charset, viewport, landmarks, headings), skip link, visible keyboard focus, sufficient light/dark contrast, reduced-motion support and responsive reflow. SVGs need useful titles/descriptions; every interaction must work with keyboard/touch; tooltips need focus behavior and should not be the sole carrier of values. Each chart needs a semantic caption and equivalent data table with headers/caption. Announce control changes accessibly, and provide meaningful content without JavaScript. Test with axe or equivalent plus manual keyboard and screen-reader passes.

### 5. Discoverability, credibility and reach

Trustworthy reach is more valuable than viral reach for this topic. Add canonical/description/Open Graph metadata, a sitemap, robots policy, RSS/Atom, `Dataset`/`ResearchProject` structured metadata, DOI and `CITATION.cff`. Supply a short methods explainer, classroom/press-safe chart embeds, alt text and a plain-language glossary. Consider translations only after the English claims are stable and budget review by native speakers.

Launch through mathematics societies/newsletters, MathOverflow where appropriate, institutional communications, research-integrity/metascience networks, and direct data integrations/links with relevant infrastructure such as zbMATH/OpenAlex—without implying endorsement. Invite an external statistics/metascience review and an independent reproduction before a broad press launch.

Measure success by reuse and trust: dataset downloads, DOI citations, external replications, chart embeds, repeat engagement, subfield/annotator coverage, method-page readership, correction turnaround and contributor retention. Avoid optimizing for provocative clicks or paper/author rankings. Use no analytics by default or privacy-preserving aggregate analytics with a transparent notice and no cross-site tracking.

### 6. Safe community PR model

Tier 1 should be structurally **data-only**: schema-validated query and chart-spec files in an allowlisted directory, pinned to a public release hash. Reject arbitrary code, SQL extensions, local-file/network access, external chart URLs and unbounded queries. Require expected-result tests, estimand/limitations metadata and domain/statistical review for promotion into “core findings.” Run PR validation on disposable GitHub-hosted runners with read-only minimal tokens, no secrets and no corpus.

Tier 0 must never execute contributor code on a persistent corpus-holding host merely because a PR was reviewed. Execute only a protected merged commit SHA with two-person approval in an ephemeral networkless VM/container, read-only corpus snapshot, disposable writes, no long-lived credentials, quotas and allowlisted outputs. Treat a new extractor as hostile code. Never use privileged `pull_request_target` for untrusted content; protect workflow/build/security files, pin Actions to full commit SHAs, lock/hash dependencies, generate an SBOM, sign/checksum releases, and isolate preview deployments from the production origin.

### 7. Deployment and operations requirements

The repo currently has no deployable site root (`site/dashboard.html` is not `index.html`), generator or workflow. A safe static deployment should be reproducible locally and in CI:

1. Verify a named release manifest/checksums/schema/signature.
2. Generate pages and external data files from that release only.
3. Run data-contract, statistical-invariant, security, accessibility and link tests.
4. Produce a content-addressed site artifact and preview.
5. Require review for production, deploy atomically, retain the previous artifact, and smoke test.
6. Support one-command rollback without rebuilding mutable data.

The operator runbook needs harvest/fetch/scan/classify/review/release prerequisites, stage health, retry semantics, completeness thresholds, budget limits, freeze/cutoff steps, backup/snapshot, rollback, correction, incident handling, credential rotation and disaster recovery. Monitor acquisition lag, stage success/coverage, unexpected zero/yield changes, validation drift, queue/cost, site availability, integrity hashes and correction SLA. Never monitor raw paper text or sensitive model output in public logs.

## Testing and quality plan

There are currently no tests, fixtures, CI or declared quality tools. The first engineering milestone should establish a small deterministic end-to-end corpus made entirely from synthetic or explicitly licensed material; public CI must never need the private corpus.

### Unit and golden tests

- OAI parsing: normal records, multiple versions, old IDs if supported, deletion, missing fields, namespaces, malformed/oversized XML, resumption token and datestamp precedence.
- Acquisition state: transient/permanent errors, retry-after seconds/date/zero/huge values, redirect/host rejection, new-version refresh, hash mismatch, HTTP-200 error bodies, unknown type, byte limits and atomic restart.
- Archive scanning: tar/gzip/single TeX/PDF-only, uncompressed tar, path names, member/count/ratio/total limits, corrupted/truncated archives, Unicode mixed errors and deterministic ordering.
- TeX evidence: even/odd backslash before `%`, verbatim environments, escaped percent, root/include graph, ignored residuals, acknowledgments/thanks/footnotes/appendices, large-member partial status and rendered-location verification.
- Lexicon: at least one true/false/boundary case per term and context/FP rule, collisions such as Claude/Sage/GAP/Lean/AI notation, negation scope, multilingual/accent cases and frozen version checks.
- Snippet construction: merging must preserve the union/evidence for every hit, stable source offsets, deterministic hashes and source/run/version isolation.
- Classifier adapter: reordered/missing/duplicate/out-of-range IDs, non-array JSON, extra fields, wrong enums/types/confidence, oversized output, absent/fuzzy quote, injection text, timeout/refusal, cache separation and exact protocol identity.
- Report/statistics: creation-date cohort, paper-version handling, run/model/human precedence, incomplete stage refusal, weighted totals, Wilson edge cases, measurement-error simulation, multiple locations, suppression and escaping.
- External-list parser: pinned upstream fixtures, normal/bold table variants, zero-row failure and source hash.
- CSV/Markdown/site escaping: formula-leading cells including whitespace/control prefixes, raw HTML and `</script>` strings.

### Integration and property/fuzz tests

- A tiny synthetic OAI → fetch fixture → extract → scan → classify stub → dual review → release → site pipeline with known expected hashes and aggregates.
- Interrupted/resumed runs at every stage; no partial run may become publishable.
- Re-running the same manifest is idempotent; changing any version, byte, config, prompt, model or code hash creates a distinct result.
- Referential checks prove every public label has an existing completed source/evidence path and every denominator item has an explicit terminal state.
- Concurrency tests for SQLite writer boundaries, snapshots and rollback.
- Property/fuzz testing for OAI XML, archive layouts, TeX comment lexing, JSON responses, path containment and aggregate invariants.
- Adversarial archive/compression/PDF and prompt-injection fixtures in isolated, resource-limited CI jobs.
- Estimator simulation under stratification, unequal inclusion, clustering, false positives/negatives, missingness and rare classes; nominal interval coverage should be demonstrated.

### Site tests

- Schema and totals: chart data sum to release aggregates and use the named release hash.
- Hostile metadata/model strings cannot create markup/script/style/URL execution.
- CSP, headers, dependency integrity, link checking and no external trackers.
- Automated accessibility plus manual keyboard, screen-reader, zoom/reflow, high-contrast/light/dark checks.
- Visual regression at representative viewports, no-JS content and downloadable table equivalence.
- Preview/production artifact identity and rollback smoke test.

### CI gates

A sensible baseline is a locked Python 3.12 package with `pytest`, coverage focused on critical logic, `ruff` formatting/linting, a strict enough type checker for boundary/data models, migration checks, dependency/vulnerability scanning, SBOM generation and site validation. Pin CI actions by commit SHA. “Tests pass” is necessary but not a scientific gate; release CI must also verify manifest completeness, referential integrity, validation thresholds, suppression, claim text and approval signatures.

## Documentation and repository hygiene

### Required top-level material

Add:

- `README.md`: one-sentence scope; current status; prominent “no validated public prevalence estimate yet”; architecture; quick start with synthetic fixture; data access; methods/docs map; citation; licensing; security/privacy; correction/contact.
- `LICENSE` for code, a separate dataset license/terms, and `NOTICE` for third-party content.
- `pyproject.toml` plus a reproducible lock and declared Python/system dependencies.
- `CITATION.cff`, contribution guide, code of conduct, security policy and governance/maintainer file.
- `docs/methodology.md`, codebook/taxonomy, data dictionary, threat model/privacy notice, release policy, correction policy and operator runbook.
- Architecture decision records for the paper-version unit, immutable runs, publication boundary, model provider, release home and site stack.
- Changelog/release notes and a machine-readable status/provenance manifest.

### Resolve document drift

- `PITCH.md` says it mirrors canonical `pitch.tex`, but the files already differ. Generate one representation from the other or add a parity check. Correct the pilot and literature claims in both.
- `TECH_NOTES.md` calls only the legacy script the prototype, while a second pipeline and dashboard now exist. Split stable protocol decisions from brainstorming, mark implementation status per section and link registered protocol versions.
- `DESIGN_PLATFORM.md` accurately says it is mostly unimplemented, but its per-paper/public/legal assumptions and zero-backend community conflict need revision. Turn it into accepted/rejected architecture decisions rather than a promise list.
- `WORKFLOW.md` documents the legacy path only. Replace it after deprecation with the supported pipeline/release runbook and failure semantics.
- `PRIOR_ART.md` should become a reproducible scoping/evidence review and have a dated update cadence.

### Earlier audits

The three files under `reports/` are useful, but they contain absolute local links and Codex session-resume identifiers and are not a maintainable issue tracker. Move durable audits to `docs/audits/` or link findings to tracked issues with status, commit and regression test.

| Earlier review | Status at this audit |
|---|---|
| `codex_review_1.md` | Several tactical fixes landed (retry eligibility, tar detection, accent/lowercase/negation cases, query directories). Core version identity, run completeness, cohort dates, deletion handling, rendered-source privacy, comment parity, large-member/ancillary status and FP-scope issues remain. |
| `codex_review_2_analysis.md` | SQLite thread use was fixed and ID mapping improved, but IDs still fall back positionally. The report, cache identity, snippet union, audit estimator/truncation/dedupe, nested reparse, external parser and location problems remain. |
| `codex_review_3_platform.md` | It correctly identifies public-label, trusted-runner, identifiable-ID, sustainability, proprietary reproducibility, release/correction and browser-explorer risks. None is implemented yet; incorporate them into revised architecture and release gates. |

Do not mark a finding fixed merely because code changed; add its regression test and verify old artifacts/data are migrated or invalidated.

### Unrelated `.claude` material

The five Lean guidance files and eight Lean utilities under `.claude/` are unrelated to this project's product or research pipeline, lack visible origin/version/license metadata, and one document references a missing `lean-lsp-server.md`. `smart_search.sh` transmits queries to third-party services, and other utilities execute Lean tooling on inputs. They expand the trusted code/privacy surface and confuse repository scope. Remove or relocate them to an independently licensed/tooling repository or plugin. If intentionally retained, explain why, add provenance/licenses/tests and constrain network/execution to trusted Lean inputs.

## Prioritized roadmap

The order below is intentionally gated. Scaling, additional work packages and outreach should not run ahead of evidence integrity.

### Gate 0 — Make the repository safe to share

Actions:

1. Freeze public promotion of current numeric dashboard/model results and label every existing artifact prototype/unvalidated.
2. Decide the name with arXiv/institutional input; rename or obtain authorization and add required acknowledgement/non-endorsement.
3. Remove/quarantine tracked article excerpts, personal data and paper-level labels; decide whether public history needs rewriting and document any purge.
4. Add code/data/document licenses, privacy/security contacts, project status and correction policy.
5. Remove/relocate unrelated `.claude` tooling and designate the legacy script unsupported.
6. Correct the pilot, trend, Pangram and benchmark-count claims in both pitch versions and prior art.

Exit criteria:

- A public clone contains no prohibited snippets/PII/per-paper detector/error output.
- Branding, licenses, status, attribution/non-endorsement and contacts are institutionally approved.
- The current dashboard is private/demo-only or plainly states candidates, provenance and non-validity.

### Gate 1 — Establish the reproducible WP1 engineering core

Actions:

1. Package/lock the environment and add migrations, configuration, synthetic fixtures and CI.
2. Implement the immutable paper-version, asset, cohort, protocol, run-item, evidence, reviewer/adjudication and release schema.
3. Migrate or explicitly invalidate the current DB; do not silently treat stale rows as the new schema.
4. Fix OAI tombstones/state/reparse and bootstrap a correct historical frame.
5. Implement versioned content-addressed fetch, bounded/sandboxed parsing, rendered-document extraction and explicit coverage.
6. Replace agentic classification with an isolated pinned structured-output adapter and strict evidence/schema validation.
7. Rewrite report/site generation to fail closed on one frozen snapshot.

Exit criteria:

- The synthetic end-to-end release is deterministic from a clean clone.
- Every cohort item has an explicit stage state; no orphan evidence/labels exist.
- Reusing a human alias cannot delete a run; protocol/input changes produce new IDs.
- Partial/error stages exit nonzero or emit a formal non-publishable status.
- Resource, path, injection and escaping tests pass in CI.

### Gate 2 — Validate and preregister WP1

Actions:

1. Co-design/freeze the taxonomy and annotation codebook.
2. Perform power/precision calculations; build enriched development and probability validation samples.
3. Train, independently double-code and adjudicate; retain original judgments.
4. Freeze lexicon/classifier/protocol on development data; run held-out temporal/subfield validation and a human negative audit.
5. Preregister cohort, estimands, sampling, missingness, estimators, primary contrasts, subgroup/multiplicity plan and release gates.
6. Seek external methods/ethics/privacy review.

Exit criteria:

- Class-specific performance and uncertainty meet predeclared thresholds for headline categories.
- Negative/pipeline-positive population errors can be estimated with known inclusion probabilities.
- The main outcome period/data have not been used for tuning.
- An independent reviewer can reconstruct the estimand and analysis from the protocol.

### Gate 3 — Publish a trustworthy WP1 alpha

Actions:

1. Freeze the cohort/cutoff and run all stages to explicit terminal states.
2. Build and review a disclosure-controlled aggregate release; generate the site from it.
3. Publish Zenodo DOI plus identical checksummed GitHub Release, methods, validation, limitations, schema, citation and correction ledger.
4. Run scientific invariants, privacy, security, accessibility, browser and rollback checks.
5. Conduct a quiet expert beta before press/outreach.

Exit criteria:

- Site, downloads and paper tables cite the identical release hash/DOI.
- Headline numerator/denominator/coverage/weights/uncertainty reproduce exactly.
- No incomplete/right-censored cells are presented as observations.
- Correction/appeal and incident channels are staffed and tested.
- A second maintainer can restore and redeploy the last release.

### Gate 4 — Scale and replicate WP1

Actions:

1. Expand to the registered 5k–20k paper-version sample and historical strata via sanctioned bulk channels.
2. Monitor target-domain performance and label drift without tuning the frozen evaluation release.
3. Obtain an independent institutional replication or at least reproduce a major release on separately operated infrastructure.
4. Add carefully governed community chart specs and outreach; measure reuse/trust, not clicks.
5. Only then add version-transition and author-disambiguation analyses with their own validation.

Exit criteria:

- Scale tests and cost/storage/backup plans are demonstrated.
- No important stratum falls below prespecified coverage/validation bounds without visible qualification.
- An external reproduction or audit has been published with discrepancies resolved transparently.

### Gate 5 — Separate later studies

- **WP2:** registered multi-detector math calibration, independent/vendor-COI safeguards and aggregate-only reporting.
- **WP3:** separately governed, adequately powered, specialist-adjudicated reliability study with private time-split benchmark and author appeal.
- **Community experiment:** only after ethics approval and a controlled service/privacy/security design; not as a share-link shortcut.

These should not be coupled to routine WP1 dashboard deployment. A failure or controversy in a detector/error study should not compromise the disclosure observatory's data or governance.

## Release acceptance checklist

No public scientific release should proceed unless every applicable item is true:

### Scientific

- [ ] Target population, unit, cutoff, inclusion/exclusion, version rule and primary estimands are registered.
- [ ] Frame comes from a complete, frozen manifest; OAI datestamps are not mistaken for submission dates.
- [ ] Inclusion probabilities, clustering, missingness and multiplicity are handled as preregistered.
- [ ] Human reference standard is independent, double-coded and adjudicated.
- [ ] Class-specific validation and measurement uncertainty meet predeclared thresholds.
- [ ] No model or rule was tuned on the held-out main outcome set.
- [ ] Pilot/exploratory results are visibly separated from confirmatory results.

### Provenance and engineering

- [ ] Every public row/aggregate traces to existing versioned inputs, completed run items and validated evidence.
- [ ] Code, environment/container, dependencies, taxonomy, prompt/model and analysis are pinned and hashed.
- [ ] Database schema migrations and snapshot/backup integrity pass.
- [ ] All requested-stage failures are explicit; the release builder fails closed.
- [ ] Clean-clone synthetic end-to-end and release reproduction tests pass.
- [ ] A second maintainer has reproduced or restored the release.

### Security, privacy and ethics

- [ ] No article text, residual source, personal data or prohibited row-level label leaks into public artifacts/logs.
- [ ] External processing and participant protocols have institutional approval and documented terms.
- [ ] Untrusted files/models/PRs run in enforced isolation with resource limits.
- [ ] JSON/HTML/Markdown/CSV injection and path/archive adversarial tests pass.
- [ ] Small-cell disclosure control and public/internal schema policy are enforced automatically.
- [ ] Correction, objection/appeal, takedown, retention and incident processes are operational.

### Public site and open science

- [ ] Branding permission/rename, arXiv acknowledgement/non-endorsement and licenses are complete.
- [ ] Site and data identify the same immutable DOI/release hash and checksum.
- [ ] Every headline exposes denominator, coverage, validation, uncertainty and limitations.
- [ ] Accessibility, no-JS, CSP/security-header, link and browser tests pass.
- [ ] Citation, schema, methods, downloads, changelog and correction ledger are public.
- [ ] Rollback to the prior artifact has been tested.

## File-by-file disposition

This section accounts for every tracked file at the reviewed commit.

### Root project files

| File | Review and recommended disposition |
|---|---|
| `.gitignore` | Good exclusion of corpus/cache/DB/mail/build artifacts. Add virtual environments, environment/secrets files, raw model responses, restricted annotation/evidence exports, database backups/snapshots and release staging. Do not hide synthetic fixtures or public release manifests. |
| `PITCH.md` | Compelling integrated question and ethical intent. Correct pilot frame/recall, remove or reproduce the 20%-trend claim, remove specific quoted paper evidence, qualify prior-art statistics, and update branding. Generate from/into the canonical pitch source. |
| `pitch.tex` | Useful one-page collaborator format, but already drifts from Markdown and repeats unsupported/currently unvalidated headlines. Keep one canonical content source and compile/test the derivative. |
| `TECH_NOTES.md` | Strongest project document. Preserve the estimand separation, validation principles, domain calibration and WP3 design; update implementation status, estimator/annotation details, version schema, security/vendor protocol, terminology and corrected citations. Split registered protocol from exploratory notes. |
| `PRIOR_ART.md` | Valuable scoping pass and honest correction of novelty overclaims. Not a systematic review; add reproducible search/evidence table and correct Pangram/ArxivMathGradingBench/trend claims. Remove “gap confirmed” until independently verified. |
| `DESIGN_PLATFORM.md` | Static three-layer direction is sound. Revise the unsupported public row-level/legal assumption, trusted-runner model, canonical release choice, governance, browser explorer and zero-backend/community conflict. Convert key choices to architecture decisions with status. |
| `WORKFLOW.md` | Obsolete because it documents only the legacy email pipeline and includes a nonexistent status label. Replace with the supported manifest-driven operator/release runbook after migration. |
| `arxiv_ai_ack_scan.py` | Useful historical prototype, now a divergent and unsafe production path. Archive/tag for pilot provenance, port tested features, then deprecate/remove from supported execution. Its direct/unversioned downloads, residual scanning, resource limits, output leakage and CSV/Markdown safety must not be carried forward. |

### Pipeline package

| File | Review and recommended disposition |
|---|---|
| `pipeline/__init__.py` | Empty package marker is harmless. Add package/version metadata through `pyproject.toml`; do not put runtime initialization here. |
| `pipeline/db.py` | Replace ad hoc schema creation with versioned migrations and the immutable paper-version/run/review/release model. Add FKs, constraints, indices, read-only/snapshot connections and configured paths/permissions. |
| `pipeline/harvest.py` | Keep OAI/raw-page approach. Add tombstones, nested explicit reparse, immutable atomic manifests/state, stale-upsert protection, bounded/hardened XML, validated IDs/dates and correct respectful backoff. |
| `pipeline/backfill.sh` | Keep chunk/resume concept; fail nonzero after exhausted retries, check working directory, summarize chunk states and preferably delegate durable orchestration to Python/job ledger. |
| `pipeline/fetch.py` | Keep serial version-pinned requests, deterministic order and hashes. Make objects versioned/content-addressed; stream/cap/validate atomically; enforce path containment; quarantine unknowns; store attempts; expose incomplete status. |
| `pipeline/lexicon.py` | Treat as a seed retrieval lexicon. Externalize/version/freeze it, complete taxonomy deliberately, add golden collision tests and per-term validation, and improve scope/context parsing. |
| `pipeline/scan.py` | Preserve non-extracting tar access. Implement rendered root/include graph, bounded/sandboxed parsing, correct TeX lexing/encoding, immutable run items and explicit partial/error coverage. Quarantine residual/ancillary evidence. |
| `pipeline/scan_meta.py` | Retain as cheap screen but make it consume a frozen cohort/metadata snapshot under the same immutable completion framework; no named-run deletion or global current-table scan. |
| `pipeline/classify.py` | Replace agentic default with isolated pinned structured output; hash the entire protocol/input identity, preserve all hit contexts, enforce exact IDs/schema/evidence, persist failures/raw audit output restrictively and fail closed. |
| `pipeline/audit.py` | Replace as the stated recall estimator. Machine full-document retrieval may remain secondary, but sampling and ground truth must be human-anchored, probability-based, versioned, complete and statistically integrated. |
| `pipeline/report.py` | Rebuild as a pure, tested analysis over one frozen release snapshot. Enforce cohort/stage/model/version/human policy, weights/missingness/measurement uncertainty, escaping and publication gates. |
| `pipeline/validate_awesome.py` | Pin and robustly parse the external list, fail on implausible/zero rows, use creation dates and treat membership as a retrieval cross-check—not truth. Add licensed fixtures. |

### Site

| File | Review and recommended disposition |
|---|---|
| `site/dashboard.html` | Visually promising prototype, not a public site or generated research artifact. Correct claims, remove hard-coded data, fix XSS/accessibility/semantic/metadata gaps and generate a complete multi-page static site from a signed release. Add `index.html`/build/deploy/rollback. |

### Earlier review artifacts

| File | Review and recommended disposition |
|---|---|
| `reports/codex_review_1.md` | Preserve as historical audit after removing local absolute links/session metadata or place in an audit archive. Link each finding to issue, fix commit and regression test; many core findings remain. |
| `reports/codex_review_2_analysis.md` | Same. Two tactical fixes landed; most scientific/provenance findings remain or are only partially addressed. |
| `reports/codex_review_3_platform.md` | Strong threat/governance critique of the future design. Incorporate it into formal architecture/release policies; do not leave it as disconnected prose. |

### Tracked result artifacts

| File | Review and recommended disposition |
|---|---|
| `results/new_papers.csv` | Generated pilot frame containing identifiable metadata and local mail provenance. Move to restricted/reproducible input manifest; if publicly released, strip local filenames, add provenance/schema/license and use a versioned data release rather than Git source. |
| `results/new_papers.json` | Same disposition as CSV; JSON can remain a synthetic/test fixture only if replaced with licensed/minimized data. |
| `results/ai_ack_hits.csv` | Contains long article text, paths/personal data and a live formula-leading cell. Remove from public/tracked tree and history as appropriate; retain only restricted evidence. |
| `results/ai_ack_hits.json` | Same expressive-text and paper-level leakage at greater volume. Restricted evidence only, with retention/access/redaction controls. |
| `results/ai_ack_report.md` | Publishes long snippets, emails/addresses and paper labels. Remove from public history as appropriate; replace with aggregate validated release report. |
| `results/candidate_papers.csv` | Paper-level automated labels and raw snippets; restricted review queue only, never a public data release. |
| `results/candidate_papers.md` | Same, including unnecessary reproduction of email/postal details in a false-positive source snippet. Remove/quarantine. |
| `results/manual_review.md` | Identifiable paper-level human judgments without full annotation provenance or appeal. Migrate to restricted annotation system; public aggregate only under current ethics policy. |
| `results/errors.json` | Empty generated output has no value in source control. Future errors belong in immutable run-item records/log bundles with redaction, not a mutable tracked file. |

### Unrelated Lean/Codex material

All of the following are out of scope for ArxivObservatory and should be removed/relocated or explicitly vendored with provenance, license, security boundary and maintenance owner:

- `.claude/docs/lean4/axiom-elimination.md`
- `.claude/docs/lean4/compiler-guided-repair.md`
- `.claude/docs/lean4/lean-lsp-tools-api.md` (also references missing `lean-lsp-server.md`)
- `.claude/docs/lean4/proof-golfing.md`
- `.claude/docs/lean4/sorry-filling.md`
- `.claude/tools/lean4/analyze_let_usage.py`
- `.claude/tools/lean4/check_axioms.sh`
- `.claude/tools/lean4/count_tokens.py`
- `.claude/tools/lean4/find_golfable.py`
- `.claude/tools/lean4/search_mathlib.sh`
- `.claude/tools/lean4/smart_search.sh` (makes external search requests)
- `.claude/tools/lean4/sorry_analyzer.py`
- `.claude/tools/lean4/suggest_tactics.sh`

### Ignored/local state inspected

- `observatory.db*`: logically inconsistent provenance despite a successful SQLite quick check; live/mutable and not a release source. Snapshot, migrate or rebuild after the schema redesign.
- `corpus/`: approximately 891 MB during inspection and actively growing; keep private, make immutable by content/version, enforce permissions/retention/backups and do not serve from the site.
- `papers/`: approximately 249 MB of legacy pilot assets/extractions; private and redundant with the new corpus path. Migrate necessary versioned hashes/evidence, then retire according to retention policy.
- Repository total was approximately 1.5 GB because ignored operational data were live. The tracked source is small; storage architecture, not Git, should own the corpus.

## External evidence checked for this review

Primary/official operational and policy references:

- [arXiv API terms and metadata license](https://info.arxiv.org/help/api/tou.html)
- [arXiv article licensing guidance](https://info.arxiv.org/help/license/index.html)
- [arXiv bulk-data guidance](https://info.arxiv.org/help/bulk_data.html)
- [arXiv S3 bulk access](https://info.arxiv.org/help/bulk_data_s3.html)
- [arXiv name and logo guidelines](https://info.arxiv.org/brand/brand-guidelines.html)
- [Swiss FDPIC research and data-protection guidance](https://www.edoeb.admin.ch/en/research-and-data-protection)
- [GDPR official text](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

Scientific claim checks highlighted above:

- [Large-scale evidence of LLM-modified scientific prose, Nature Human Behaviour](https://www.nature.com/articles/s41562-025-02273-8)
- [Researcher LLM-use survey](https://arxiv.org/html/2411.05025v1)
- [Foundation-model adoption study](https://arxiv.org/abs/2511.21739)
- [Closest arXiv/Pangram precedent](https://arxiv.org/html/2601.17036v1)
- [Pangram technical report](https://arxiv.org/abs/2402.14873)
- [NBER detector benchmark](https://www.nber.org/papers/w34223)
- [To Err Is Human](https://arxiv.org/html/2512.05925v1)
- [ArxivMathGradingBench](https://arxiv.org/html/2605.20531)
- [Secondary coverage of the unreproduced 20%-above-trend chart](https://officechai.com/ai/mathematical-articles-on-arxiv-have-risen-20-over-trend-in-2026/)

## Bottom line

The project should continue. Its central WP1 question is timely, publicly useful and methodologically tractable, and the planning documents already contain many of the right scientific instincts. The key is to stop treating the current hackathon artifacts as a nearly finished observatory. They are a successful feasibility probe that exposed the right taxonomy, data-access route and engineering problems.

The five highest-leverage next moves are:

1. Sanitize the public tree and resolve name/licensing/governance.
2. Redesign around immutable paper-versions, protocols, runs, item completion and evidence.
3. Build the human reference standard and preregister the two-phase WP1 analysis.
4. Produce one deterministic, aggregate-only, citable release and generate the site from it.
5. Seek independent replication before scaling claims or launching WP2/WP3/community participation.

If those gates are enforced, ArxivObservatory—or a renamed successor—can become a rigorous and unusually informative public metascience resource. If they are bypassed, scale and polished visuals will amplify measurement error, privacy risk and reputational harm rather than knowledge.

## Review limitations

This was a repository and local-state audit, not legal advice, a formal penetration test, an institutional ethics determination, or independent reannotation of every paper. The live backfill meant database counts were not frozen. I did not run external model calls, mutate the corpus, deploy the site, or reproduce literature analyses whose data/code are absent. Those limitations strengthen rather than relax the recommendation to gate public claims on an immutable release and independent human/methods review.
