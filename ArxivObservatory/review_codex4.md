# ArxivObservatory repository review — iteration 4

**Review date:** 2026-08-11 (Europe/Zurich)

**Reviewed snapshot:** `b4207cbf9df707e4f7db889d158c679b3ce38bef` (`b4207cb`; tree `13ab7e4d1e166115dcc030ecaa1cea8efd1b1699`). The worktree was clean before this requested review file was created.

**Comparison baseline:** iteration 3 reviewed `c2a63882511a293e00858cd687e3bc501c2805c9` (`c2a6388`). Thirteen subsequent commits changed 32 tracked files, adding 3,563 lines and removing 365.

**Scope:** all 90 tracked files; the live SQLite schema and aggregate state; S3 acquisition records; current scan, classification, render, annotation, report, site, and distribution artifacts; tests and CI; specifications, research plans, taxonomy, prior-art notes, governance and ethics claims, AWS/deployment scripts, and relevant Git history. This was a read-only audit except for creating this review. I did not stop or start jobs, fetch papers, invoke a classifier, alter the database/corpus, contact arXiv, mutate cloud services, or publish anything.

**Dynamic-data warning:** `observatory.db` was being modified during the review. The `export-v1` artifact count rose repeatedly and the WAL timestamp advanced. Database counts below are therefore point-in-time observations, not a frozen release. At 2026-08-11 13:21:42 UTC, a canonical summary contained 182,307 artifacts and had SHA3-256 `d840aa7b79e424ed17366edca2c3e83e657ea78fcec942c0b5a5570ca75219e9`. The database itself was not hashed while live.

## Executive verdict

The data is now here in a meaningful engineering sense. The project successfully reconciled and registered a 168,027-paper S3 corpus, scanned 169,165 papers into an append-only run, classified 73,945 evidence snippets with normalized hit lineage, and rebuilt a much more informative aggregate site. This is a major advance over iteration 3, when no end-to-end v2 result existed. The current architecture is worth completing.

It is not yet a valid scientific release. The displayed 2.1% is a **raw automated-classifier result from a partial, dirty-code, non-isolated run**. There are zero human annotations and zero frozen releases. In the headline cohort, 124,741 of 131,310 scan-complete papers (95.0%) have an unknown source version; only 5,901 are known v1 and 668 are known later versions. The site applies quote grounding but not the required rendered-evidence gate. Of 8,078 author-use snippets, only 1,363 are marked rendered; 6,695 have unknown source version, and 20 have other non-rendered/error/short statuses. The polished dashboard must therefore remain private or unmistakably an exploratory demo.

The intended v1 remedy is currently disconnected from the analysis pipeline. `fetch --v1-refill` stores successful v1 blobs only in `artifacts`, while `scan --corpus` selects only `files`. At the observed snapshot, all 6,203 target papers with a newly/previously available v1 artifact lacked a scan item for that v1 artifact hash. Completing the current long-running refill would not make those blobs analyzable without an artifact-driven scan importer/manifest and a fresh scan and classification.

The current 500-paper gold packet is also not a gold study for the public estimate. It samples the entire 166,183-paper scan-complete universe, not the 131,310-paper math-primary report cohort. Only 373 of 500 sampled papers are in the headline population; 127 (25.4%) are outside it. Most sampled versions are unknown, and packet construction can substitute the paper's mutable latest PDF. The search-plant protocol was changed after packet work began, no annotations have been ingested, and the promised adjudication and design-weighted estimators do not exist.

The best defensible near-term product remains narrow:

> A version-explicit, human-calibrated observatory of author-reported generative-AI/agent assistance visible in a specified rendered arXiv math-primary paper-version.

CAS/proof-assistant measurement, detector-inferred prose modification, author-level productivity analysis, error auditing, and community conversation collection should remain separate studies until each has its own instrument, validation, and governance.

### Release decision

| Deliverable | Decision now | Reason |
|---|---|---|
| Private engineering and pilot annotation | Continue | The new data spine and acquisition work are valuable |
| Public source-code alpha | Possible after repository sanitation, licensing, setup/security documentation, and safe defaults | Code can be shared without asserting numerical results |
| Current `site/` or `dist/` | **Do not deploy** | No release; partial/dirty/non-isolated run; mixed/unknown versions; render and gold gates absent; artifacts disagree |
| 2.1%, weekly/daily trend, subfield ranks, tools/providers/agentic share, impact split | **Do not promote or cite** | Exploratory model output without the required measurement-error study |
| Current 500-item packet | Treat as instrument pilot only | Wrong population/version binding; protocol changed; no completed double review/adjudication |
| WP2 detector study, WP3 reliability audit, community share-link service | Keep in design phase | Different estimands and materially greater ethical/security obligations |

## Snapshot and verification

### Repository checks

- `python -m pytest -q -p no:cacheprovider`: **73 passed**.
- Project Python compilation: passed.
- Shell syntax checks for tracked operational scripts: passed.
- SQLite `PRAGMA quick_check`: `ok`.
- SQLite `PRAGMA foreign_key_check`: no reported violations.
- Schema version: 3, matching code head.
- Git worktree: clean before `review_codex4.md` was added.
- No obvious tracked credential/private-key material was found in targeted inspection. This was not a penetration test or formal secret scan.

The tests are useful and several directly encode earlier review regressions. They remain fixture/unit tests; they do not prove a clean-clone reconstruction, a safe model boundary, an end-to-end release, a correct gold estimator, deterministic packaging, or deployment safety.

### Live database at the point-in-time snapshot

| Object | Count / state |
|---|---:|
| papers / version rows | 235,342 / 418,232 |
| mutable `files` rows | 169,166 |
| immutable artifact rows | 182,307 and increasing during review |
| scan runs / scan items / hits | 3 / 169,423 / 547,763 |
| classification runs / items / evidence edges | 1 / 73,945 / 172,374 |
| render checks | 8,078 |
| v2 annotations / frozen releases | **0 / 0** |

Artifact channels were approximately 168,027 `s3-bulk`, 6,570 `legacy-files`, 6.2k and rising `export-v1`, 1,505 `gcs-pdf`, and 2 ordinary `export` artifacts. The changing v1 count is why this table is deliberately approximate for that channel.

### Main full-text scan

Run `tex-20260810T205113` records lexicon 2.1, code `f08502f-dirty`, 12 workers, and terminal status `partial`:

| Item status | Count |
|---|---:|
| `ok` | 166,183 |
| `skipped:pdf-tar-member` | 2,162 |
| `error:UnknownFormat` | 811 |
| `incomplete:members-skipped` | 9 |
| total | 169,165 |

The item ledger is a real improvement. Every one of the 167,003 non-null scan hashes resolves to an artifact for the same paper/hash; the 2,162 null hashes are exactly the skipped PDF-in-tar stratum. The run's stored `n_errors=820` excludes the 2,162 declared skips, so consumers must use the item ledger rather than that one summary number.

For the public report's math-primary 2023-08-01 through 2026-08-08 cohort:

| Source-version stratum among 131,310 scan-complete papers | Count | Share |
|---|---:|---:|
| unknown | 124,741 | 95.0% |
| v1 | 5,901 | 4.5% |
| later than v1 | 668 | 0.5% |

### Main classification and render state

Run `cls-20260810T211610` records backend `codex`, model label `gpt-5.6-sol@medium`, taxonomy 2.0, `isolate=0`, code `f08502f-dirty`, 73,945 valid items, no stored errors, and status `complete`. All items have evidence edges into the intended scan run. Its parameters still say `"limit_batches": 3` even though later resumes processed the full run, demonstrating that the run manifest describes only its start, not its actual multi-session execution.

Quote grounding is strong but not complete: 73,573 labels have a grounded quote and 372 do not. Author-use render states are:

| Render state | Author-use snippets |
|---|---:|
| `unknown_version` | 6,695 |
| `rendered` | 1,363 |
| `non_rendered_evidence` | 17 |
| `quote_too_short` | 2 |
| `pdf_error` | 1 |

Of the 1,363 accepted rendered matches, 241 are fuzzy rather than exact/dehyphenated. `CROSSCHECK.md:30-33` says all fuzzy matches require review, but `pipeline/render_check.py:107-138,259-276` currently promotes a score at the threshold directly to `rendered`.

### Current report, site, and package

`reports/report_3yr_preliminary.md` uses the above runs, requires quote grounding, and reports:

- frame: 133,279 math-primary papers;
- scan-complete denominator: 131,310;
- 1,968 scan errors/incomplete/skipped plus one fetch failure;
- 2,799 grounded model-positive papers; and
- raw pooled classifier rate: about 2.1%.

The report is commendably candid about partial/dirty/non-isolated provenance and gives version-stratified tables. The website suppresses too much of that context.

Current artifact hashes:

| Artifact | SHA-256 prefix |
|---|---|
| `site/index.html` | `2d39885beb507b36…` |
| `site/data/disclosures.json` | `43bd9cebaa1da589…` |
| `reports/report_3yr_preliminary.md` | `fccbd478ce4e41f4…` |
| `dist/arxiv-observatory-site.zip` | `3719e66cc90e1673…` |
| ZIP-embedded `index.html` | `e5fc305976a52a5f…` |
| ZIP-embedded `data/disclosures.json` | `3df4de314b3157ec…` |

The ZIP is the old 16.1% site, not the current 2.1% site. It also embeds local timestamps and mode 0777 entries and has no release manifest, checksums, README, or license. It must not be distributed.

## What was genuinely improved since iteration 3

These changes are substantial and should be preserved:

1. **The S3 corpus is present and reconciled.** `reports/s3_import.json` records 168,027 of 168,027 target members with zero reported reconciliation problems. The local monthly SHA list matches the report's archive hashes.
2. **A real large v2 scan and classification now exist.** This eliminates the prior review's central “no end-to-end v2 data” problem.
3. **Artifact-to-scan provenance is unusually strong.** Every non-null hash in the main scan resolves to a same-paper artifact, and every classification item has normalized evidence edges.
4. **Scan completeness is more honest.** Unknown formats and member-budget omissions demote items; the current run is correctly labeled partial. `report.py` recomputes item-state coverage.
5. **Cross-run numerator contamination was fixed.** `pipeline/report.py:101-160` scopes classification items through evidence hits to the selected scan run.
6. **Coverage partitioning improved.** The report now includes fetched-but-absent, scan-error, fetch-failed, unfetched, pending, and classification-failure states and uses any-success fetch aggregation.
7. **Classifier validation improved.** Literal JSON booleans are enforced; IDs and enums are fail-closed; invalid/failed items are durable; quote grounding is recorded; errors affect exit status.
8. **Fetch hygiene improved.** Requests is upgraded to 2.34.2, ambient `.netrc`/proxy trust is disabled for fixed origins, gzip detection is fixed, and normal fetch writes `files` and `artifacts` in one transaction.
9. **The website was rebuilt.** It is now a complete HTML document, aggregate-only in its visible result layer, tracker-free, better escaped, more interactive, and prominently labeled a non-affiliated, unvalidated prototype.
10. **Annotation UX and basic safety improved.** HTML packets escape untrusted text, expose taxonomy-driven controls, autosave/export structured JSON, constrain reviewer filenames, validate most enums, and use idempotent ingest for existing paper/reviewer rows.
11. **The gold design has useful pilot ideas.** Disjoint POS/FLAG/NEG strata, recorded inclusion probabilities, seeded order, plant items, and explicit distinction between false-omission rate and recall are good foundations.
12. **Prior-art corrections were applied.** The previously identified errors in Patterns and Purposes, Gray attribution/estimand, Pangram FPR/domain, ArxivMathGradingBench size, survey generalizability, foundation-model wording, the secondary 20%-trend claim, and the 27%-bytes claim are materially improved.
13. **Several release-contract regressions have tests.** The suite grew from 70 to 73 passing tests and now covers more report scoping and validation behavior.
14. **Legacy high-risk entry points are disabled by default.** `arxiv_ai_ack_scan.py` and `pipeline/audit.py` now require an explicit legacy escape hatch.

These improvements justify an orderly completion of the current architecture. They do not validate the numerical output.

## Highest-priority blockers

### P0-1 — The active v1 acquisition is both operationally inappropriate and unusable by the scanner

`pipeline/fetch.py:143-176` selects every multi-version paper in the corpus ID list that lacks a v1 artifact. In the full three-year ID universe, 65,844 papers have multiple known versions. At the point-in-time snapshot, only 6,203 of that target had any v1 artifact, leaving roughly 59,600. At the nominal four-second delay this is a multi-day, roughly 60,000-request historical crawl of `export.arxiv.org`.

That conflicts with the project's own acquisition policy: `TECH_NOTES.md:30-39` reserves direct export pulls for at most a few hundred papers and specifies sanctioned bulk channels for historical acquisition. The job should be reviewed immediately by the owner and, before continuation, coordinated with arXiv or replaced by an approved version-aware bulk strategy. This audit did not stop it.

Even successful completion would not achieve the v1 estimand:

- refill mode writes only `artifacts` (`pipeline/fetch.py:70-74,126-136`);
- `pipeline.scan.corpus_jobs()` selects only successful rows from `files` (`pipeline/scan.py:269-283`);
- all observed `export-v1` paths lacked a matching `files` input and no later scan run exists; and
- all observed v1 artifact hashes lacked a corresponding v1 scan item.

Failures are also invisible: connection errors, 404s, HTTP failures, and exhausted retries are deliberately not persisted in refill mode (`pipeline/fetch.py:77-103,138-140`). There is no acquisition-run manifest with a declared input set, attempts, terminal outcomes, rate/budget policy, or completion proof. A restart cannot distinguish “never attempted” from “failed repeatedly.”

The empirical claim that S3 source chunks represent the latest version 12–23 months after announcement appears only in a commit message and code comment (`pipeline/fetch.py:145-147`). No reproducible calibration script, sample, raw size-match ledger, uncertainty analysis, or signed source manifest is tracked. `pipeline/aws/import_s3.py:15-19` still describes the bulk data as approximately fixed-lag while registering every version as NULL.

Required fix:

1. Decide and preregister the primary version estimand and acquisition policy.
2. Create an immutable `acquisition_runs`/attempt ledger with target paper-version, channel, attempt state, response status, bytes/hash/format/license, rate policy, and completion manifest.
3. Make scans consume an explicit artifact manifest keyed by artifact ID, paper, effective version, and SHA—not the mutable `files` convenience table.
4. Validate exact version from authoritative metadata/content where possible; never infer v1 from a rerolled bulk blob.
5. Use an arXiv-approved route for the historical backfill and retain documented permission/coordination.
6. Only then start a new clean v1 scan, classification, render check, and release. The current run cannot be retroactively upgraded.

### P0-2 — The current 2.1% site is exploratory, not a release

The current public-shaped artifacts derive directly from arbitrary run IDs (`pipeline/build_site.py:167-182`) and there are zero rows in `releases`. The selected scan is partial and dirty; the selected classification is dirty and non-isolated; the build requires quote grounding but not rendering. The site presents 2,799 of 131,310 as an overall result even though 95.0% of the denominator has an unknown source version and most positive snippets cannot be version-render checked.

The report's missingness is visible, but its scientific consequence is not. If the 1,969 non-scan-complete/fetch-failed cohort papers are treated as unknown rather than negative, the elementary all-negative/all-positive identification region is approximately 2.10% to 3.58% of the full 133,279-paper frame. That range is far wider than the displayed binomial interval and still excludes classification/version error.

`pipeline/build_site.py:343` and the generated page say the overall Wilson uncertainty is “plus/minus about 1 point.” For 2,799/131,310, the Wilson half-width is about **0.08 percentage points**, not one percentage point. More fundamentally, this is nearly a census of the captured frame; a binomial interval requires a stated superpopulation or stochastic-process interpretation and covers none of source-version uncertainty, nonresponse/missingness, measurement error, serial dependence, or taxonomy error.

The page's prototype/do-not-cite banner is good, but it is not a release control. A large polished headline can be screenshotted independently of the caveat. Until the release gates below pass, replace real-result values with a synthetic demo or keep the result site private.

### P0-3 — The current gold sample targets the wrong frame and often the wrong version

`GOLD_STUDY.md:9-25` promises a sample from one frozen release and report cohort. `pipeline/annotate.py:172-215` instead samples every `status='ok'` paper in the scan run. It does not take cohort dates or a category rule, consume a release, call `report.run_info`, verify run compatibility/completeness, or constrain POS through the chosen scan's evidence edges.

The empirical mismatch is decisive:

| Current 500-item sample | All | Math-primary/report-population | Outside |
|---|---:|---:|---:|
| POS | 150 | 101 | 49 |
| FLAG | 50 | 23 | 27 |
| NEG | 300 | 249 | 51 |
| total | 500 | 373 | **127** |

The sample's recorded frame is 166,183 scan-complete papers (POS 3,995; FLAG 18,210; NEG 143,978), whereas the headline denominator is 131,310 math-primary papers. Applying the packet's inclusion weights would estimate a different population.

Version binding is also invalid for a final study. Of the 500 items, 448 have NULL scan version; 183 of those currently have a latest version greater than v1. When scan version is NULL, packet/PDF construction falls back to current `papers.latest_version` (`pipeline/annotate.py:287-303,500-529`). Reviewers can therefore judge a version that is not known to be the artifact scanned and classified. Contexts are re-extracted from the current `files.path`, not the scan artifact (`pipeline/annotate.py:98-116`), and `contexts.json` is reused merely because it exists (`pipeline/annotate.py:257-274`).

The manifest lacks per-item scan item/evidence IDs, scanned version, artifact SHA, context hash, PDF SHA, cohort/release identity, reviewer assignment hash, and packet hash. JSON ingest checks the asserted project/reviewer but does not load that manifest or reject unassigned paper IDs, wrong versions, duplicate IDs within the file, wrong codebook, or mismatched packet (`pipeline/annotate.py:574-608`). The fallback Markdown parser remains delimiter-based and accepts arbitrary item IDs/fields (`pipeline/annotate.py:611-651`). The annotations schema has no run/release/sample/stratum/inclusion-probability/manifest binding or uniqueness constraint (`pipeline/migrate.py:239-252`).

The study instrument also changed after work began:

- `GOLD_STUDY.md:69-92` says search-honesty plants were added from reviewer feedback on 2026-08-11;
- the manifest excludes plants from the first 60 positions, consistent with protecting already-started work;
- the 40 plants are machine POS/FLAG cases (34/6), not yet adjudicated known, findable disclosures;
- the bounded search looks only in standard disclosure locations while the headline scanner searches all selected source text; and
- packet forms do not record whether the PDF was opened, search terms/sections, time, plant detection, unreadability, or conflict of interest.

Plants conditioned on easy scanner detection cannot by themselves identify search sensitivity for atypical scanner-negative disclosures. “Deflating” negative misses by a plant detection rate is not a specified estimator and may have the wrong direction. Machine positives that turn out not to be true/findable cannot remain in its denominator.

The double-review plan is internally inconsistent. `GOLD_STUDY.md:41` says two independent reviewers per item, while lines 89–92 permit only the first 100–150 positions of independently shuffled packets. With the actual orders, the first 100 positions overlap on only 16 papers and the first 150 on 41, not 100–150; the protected first 60 overlap on none. Agreement code then groups only by paper, picks the first two reviewers, evaluates verdict only, has no CI or axis metrics, and returns success with no pairs (`pipeline/annotate.py:654-693`). Adjudication and the design-weighted prevalence/sensitivity/bootstrap estimators are not implemented. The database contains zero annotations.

Treat the present packet as usability/training data only. After the estimand and release are frozen, draw a new untouched sample from exact release membership; create an explicit shared double-coded subset stratified/powered for the intended axes; bind every review to artifact/context/PDF and assignment hashes; implement conflicts, adjudication, estimators, and uncertainty; and keep instrument-development cases out of final evaluation.

### P0-4 — The primary classifier run used the unsafe, scientifically weaker execution mode

The current classification is not merely missing an optional hardening flag. It processed the entire analysis with `isolate=0`, so batches of up to 30 papers shared one agent call (`pipeline/classify.py:40,312-322`). Untrusted manuscript text is concatenated into the agent prompt (`pipeline/classify.py:123-130`) and passed to `codex exec -s read-only` from the repository's inherited working directory and environment (`pipeline/classify.py:141-158`). A read-only filesystem prevents writes; it does not prevent prompt-directed reads of other repository/corpus files, exposure of ambient state, cross-paper influence, tool use, or provider egress.

The runbook says analysis runs use `--isolate` (`WORKFLOW.md:43-46`), yet neither classifier defaults nor freeze enforce it. This is both a confidentiality boundary and a validity boundary: a malicious or accidental instruction in one paper can affect labels for up to 29 others. The item's input hash includes its own snippet and an `isolate` bit but not the other members of its actual batch (`pipeline/classify.py:107-120`), so it does not identify the effective non-isolated prompt.

Model pinning is only a mutable CLI model string plus reasoning label. Release provenance lacks the Codex CLI/binary version, system/developer prompt, provider snapshot/build, decoding/configuration details, request ID, container/runtime identity, policy/tool configuration, and response-log hash. The actual run is stamped `f08502f-dirty`, so even the source tree that produced it is not recoverable from Git.

Resume semantics compound the problem. Resume compares prompt hash, model label, isolation, taxonomy, and scan-run set, but not `code_commit`, `params_json`, executable version, batch/merge constants, or environment (`pipeline/classify.py:410-429`). Only the first invocation's parameters and code stamp are retained (`pipeline/classify.py:431-437`). The live manifest still claims `limit_batches=3` although resumes produced 73,945 items. There is no per-resume attempt ledger or per-item producing code/runtime identity. Invalid rows are also treated as done by the resume filter and cannot be repaired without a new run.

The response schema is much better than before, but not strict enough for fine-grained public claims:

- overlong tools/models/quotes are silently truncated rather than rejected (`pipeline/classify.py:196-224`);
- declared keys such as tools/models/location/flags may be missing and default silently;
- non-author-use usage fields are coerced/cleared while the row remains valid;
- confidence is a model self-report, not a calibrated probability; and
- only the evidence quote is grounded, not the tool/model/category/impact/location fields.

This last point is empirically important. Across author-use snippet labels:

| Claimed verbatim field | Entries | Exact case-insensitive occurrence in sent snippet | Not found in sent snippet |
|---|---:|---:|---:|
| tool strings | 8,051 | 7,732 | **319** |
| model strings | 4,038 | 3,946 | **92** |

Only 6,049 tool entries and 2,810 model entries occur in the supporting quote itself. Some unsupported labels recur many times. The report title “Exact model strings as written” and site “Tools named” are therefore not warranted without field-level grounding and normalization review.

There is also a small lineage loss: the run has 172,437 classifiable hits but 172,374 linked hit edges, a difference of 63. All items still have at least one edge and there are no cross-paper/version/run edges. The likely mechanism is that the snippet hash omits offset, repeated identical contexts collide, and an existing `ok` item triggers `continue` before newly encountered hit edges are inserted (`pipeline/classify.py:107-120,343-361`). Preserve all evidence edges even when content-identical snippets deduplicate.

Nearby-hit merging also unions hit terms/IDs while retaining only the longest single stored context (`pipeline/classify.py:77-104`). A label can therefore be associated with several hits whose actual surrounding evidence was not all sent. Build one deterministic union window or split the cluster, and store exact per-hit spans within the submitted text.

Required fix:

- Prefer a non-agentic structured-output API with tools disabled and a genuinely immutable model snapshot.
- Otherwise run one paper per call in an ephemeral empty-root worker with a minimal environment, no repository/corpus mount, no ambient credentials, explicit egress allowlisting, and CPU/RAM/process/output/time limits.
- Make isolation and a safe backend a release invariant, not operator guidance.
- Hash the full effective request, including batch composition and every prompt/config byte; record every invocation/resume and provider/tool/runtime identity.
- Reject rather than truncate malformed fields and ground every field advertised as verbatim/named.
- Establish a documented vendor DPA/subprocessor/retention/deletion/transfer policy for manuscript text and responses.

### P0-5 — Freeze is still a mutable manifest, not a scientific release

The freeze contract improved, but it remains too permissive (`pipeline/report.py:60-98,326-372`). It accepts:

- a `partial` scan with arbitrarily poor coverage;
- an empty `classification_runs.scan_runs_json`, which is treated as compatible with any selected scan;
- dirty or unknown code stamps;
- a non-isolated classifier;
- unknown artifact versions;
- no grounding or rendering gates;
- no completed render-check run/algorithm identity;
- no gold project or minimum validation metrics; and
- no acquisition manifest or license completeness.

A synthetic check confirmed that `freeze=True` accepts a partial TeX run containing an `incomplete:members-skipped` item together with a complete nominally pinned classifier whose consumed-run list is empty. The current real run is not frozen, but the contract could bless it.

The report is written before pending/classification-failure freeze checks (`pipeline/report.py:326-338`). A rejected freeze can therefore still overwrite or leave behind a plausible report file. Other gate checks likewise need to happen before output mutation.

The release row then stores counts, three `paper:version` set hashes, and a report hash. It does not materialize or identify:

- complete frame membership and every terminal outcome;
- artifact IDs, paths, byte hashes, effective versions, and licenses;
- scan items/hits and classification items/evidence edges;
- exact labels and human overrides;
- render-check records and tool/normalizer identities;
- acquisition manifests;
- model requests/responses/log hashes;
- gold sample, adjudications, estimators, and metrics;
- report/site/JSON/package members and hashes;
- environment/SBOM/container identity; or
- correction/supersession lineage.

`build_site` cannot consume a `release_id`; it rereads mutable live tables from raw run IDs. `papers`, `files`, `classification_items.render_status`, and run status can change. Runs themselves are “immutable” only by convention: `pipeline/runs.py:48-86` updates rows, schema statuses/transitions are not constrained, and there are no immutability triggers. A paper/version membership hash also cannot detect different bytes at the same version.

Fetch storage is path-based rather than content-addressed and writes bytes before artifact insertion (`pipeline/fetch.py:107-136`). A later refetch can overwrite a path referenced by an old artifact row. No such multiple-hash path was found in the current state, but the contract permits it.

Implement a distinct release builder that:

1. Loads one preregistered analysis protocol and a stable acquisition snapshot.
2. Validates all gates before writing output.
3. Materializes canonical sorted release rows, including exact paper-version-artifact/evidence/render/human membership.
4. Writes into a fresh staging directory using a supplied release timestamp.
5. Generates report, site, aggregate data, manifest, SBOM, checksums, and package exclusively from that snapshot.
6. Rebuilds and byte-compares the release from a clean environment.
7. Atomically promotes only an allowlisted artifact set.
8. Makes published release records immutable and supports signed correction/supersession records.

### P0-6 — Rendered-evidence and source-privacy rules are not enforced in the displayed analysis

Taxonomy rule R3 says impact labels attach only to evidence in rendered text (`TAXONOMY.md:67-71`). The platform design likewise says every positive must match the version-pinned compiled PDF before counting (`DESIGN_PLATFORM.md:136-151`). The current report/site uses `require_grounded=true` and `require_rendered=false`. It therefore violates the project's own evidence definition.

This matters beyond a formal gate. The scanner reads every selected text-like archive member, not the rendered TeX include graph (`pipeline/scan.py:82-136`), and explicitly treats chat/prompt-like ancillary filenames as hits (`pipeline/scan.py:40-43,105-109`). It removes several common non-rendered constructs, which is useful, but regex stripping cannot establish renderedness and does not exclude unreferenced residual files. The public aggregate currently includes ancillary and other source-only locations while reporting impact labels governed by R3.

Only 1,363 of 8,078 author-use snippets are currently marked rendered. Most cannot be checked because their source version is unknown. Fuzzy matches are accepted automatically even though the cross-check plan requires review. A match somewhere in PDF text also does not prove it corresponds to the source occurrence or semantic label. Comments-field and ancillary-artifact evidence require channel-specific rules; neither necessarily appears in the PDF.

The render implementation remains mutable and under-specified:

- no render-check run manifest identifies algorithm/normalizer/pdftotext versions;
- `classification_items.render_status` is updated in place;
- cached PDF text is trusted by path/existence, not `{PDF SHA, extractor ID/version, output SHA}`;
- PDF retrieval buffers complete bodies and follows redirects;
- native `pdftotext` has a timeout but no OS sandbox, memory/output cap, or process limit; and
- fuzzy score ≥0.80 is a final acceptance rather than `needs_review` (`pipeline/render_check.py:107-138,190-198,259-276`).

Make render checking an immutable run over exact versioned artifacts. Use exact/dehyphenated matches as automatic evidence only; route fuzzy matches to blind human adjudication. Record byte/character spans, source and PDF hashes, extractor/container version, and algorithm parameters. Define separate observability policies for PDF body, arXiv comments metadata, and permitted ancillary artifacts. Residual/unrendered source must stay out of ordinary disclosure counts and restricted under a specifically approved protocol.

## Detailed implementation and data review

### Acquisition: strong imported result, unsafe producer lifecycle

The S3 importer is one of the best pieces of the repository. It performs two-direction ID reconciliation, hashes tars and members, rejects unknown formats, detects duplicates, checks the papers ledger, and normally refuses registration on any problem (`pipeline/aws/import_s3.py:58-217`). The tracked report says the present acquisition found all 168,027 target members with zero errors, and the 36 local monthly archive checksums match it. This concrete success should be preserved.

The remote producer is not crash-consistent or fail-closed (`pipeline/aws/filter_remote.py:23-74`):

- it appends members directly to long-lived monthly tars;
- a crash before `done.txt` can duplicate a partially appended chunk on retry;
- only a userspace flush precedes the done marker; no close/fsync/atomic shard commit occurs;
- final download or MD5 failures are logged and skipped;
- it still prints `ALL DONE` and exits zero after such failures; and
- upstream size, disk/cost/output/member limits and a complete durable ledger are absent.

The new `pipeline/aws/overnight_sync.sh` adds a serious teardown risk. It declares success after two remote/local **size-list** matches only 60 seconds apart (`:16-34`), without proving all expected chunks completed, checking producer exit/done state, comparing remote/local hashes, or running importer reconciliation. It then kills the session and requests EC2 termination (`:41-48`). A producer lull can resemble completion. The initial broad `pkill -f "rsync.*math_"` may also kill unrelated matching processes. The script lacks strict shell mode, account/region/tag identity checks, termination wait/verification, and a nonzero exit when termination fails.

This acquisition happened to reconcile; the automation remains unsafe for the next one. Produce closed content-addressed per-chunk shards in staging, validate exact membership and bytes, close/fsync/hash, atomically commit a ledger entry, and exit nonzero on every gap. Transfer and compare cryptographic hashes, run the importer in reconciliation mode, archive the full signed manifest, and only then terminate a positively identified instance.

`pipeline/aws/README.md` is stale: it references a missing `provision.sh`, calls the implemented importer pending, and claims all material cloud operations are code. There is no tracked IaC or documented least-privilege instance role, IAM policy, security group, IMDSv2 enforcement, encrypted volume policy, budgets/alarms, central logs, restore/incident procedure, account/region verification, or automatic verified teardown. The scripts depend on personal SSH/AWS state.

### Metadata harvesting and ordinary fetching still fail reconstruction contracts

`pipeline/harvest.py` writes new OAI pages below `corpus/oai/<run_key>/page_*.xml.gz` (`:138-169`), while `--reparse` searches only `corpus/oai/page_*.xml.gz` (`:176-183`). It therefore ignores the current nested archive layout and cannot reconstruct the database from stored pages. Deleted OAI records are skipped rather than tombstoned (`:54-57`), so a previously known paper can remain active indefinitely.

OAI IDs are not strictly validated before they enter URLs, database keys, and downstream paths. Harvest requests buffer complete XML responses, inherit ambient session environment, follow redirects, and have no compressed/decoded size or final-origin limit. Raw page/state writes are not atomic or manifest-bound.

`pipeline/backfill.sh` still prints “backfill complete” and exits success even if a chunk fails all 20 attempts (`:11-23`). It has no strict shell mode or final failed-chunk list.

Ordinary `fetch.select_todo()` treats any prior successful source/PDF or prior 404 as terminal without comparing `files.version` to `papers.latest_version` (`pipeline/fetch.py:179-192`). It therefore will not refresh a paper when OAI observes a new version. Successful unknown-format HTTP bodies are stored with `ok_unknown_format`; the scanner later surfaces them as errors, but acquisition should reject them as successes. Network responses are buffered without a byte cap, redirects/final host are not constrained, and writes are direct rather than temporary+fsync+rename.

Add strict modern/legacy arXiv-ID validation at ingestion, OAI tombstones, recursive manifest-driven reparse, streamed response limits, allowed-origin redirect checks, atomic raw page/blob/state writes, version-aware eligibility, and durable acquisition attempts.

### Scanner resource boundaries and coverage

The scanner has important safeguards: it never extracts tar members to the filesystem, hashes bytes actually read, caps individual selected members and total selected text, has a PDF timeout, and records unknown/incomplete/skipped outcomes. Its current throughput is excellent.

Remaining hostile-input/scalability gaps:

- `gzip.decompress(data)` expands the entire single-gzip payload before enforcing the 200 MiB limit (`pipeline/scan.py:87-99`), allowing a gzip bomb to exhaust memory first.
- `TarFile.getmembers()` materializes an unbounded header/member list; no member-count, header, compression-ratio, wall-time, or total outer-blob limit exists (`:100-103`).
- `read_blob()` trusts DB paths, does not enforce resolved containment, reads an entire plain file/tar member, and leaves cached tar handles open for worker lifetime (`:157-173`).
- PDF-in-tar members are skipped rather than extracted, creating 2,162 exclusions (1,258 in the headline frame).
- PDF text caches are path/existence-based, not input-hash/tool-version bound (`:145-154`).
- Native PDF conversion lacks an OS/resource sandbox and output quota.
- TeX selection is extension/content-sniff based, not a rendered include graph; some rendered `.sty/.cls` or unusual members can be missed while unreferenced residual `.tex` can be scanned.
- The percent-comment regex mishandles some even/odd backslash cases, and brace-naive URL protection can be defeated by nested arguments (`:44-60`).
- An external interruption can leave a run permanently `running`; there is no outer finalization/recovery state.

Bound compressed and decoded streams before allocation; iterate tar headers with explicit count/ratio/time budgets; enforce path containment; close caches; sandbox and content-bind converters; support PDF members; and capture an explicit member inventory/include graph. A release should declare source/PDF/unsupported strata and a maximum missingness policy rather than infer quality from run status alone.

### Database, migrations, indexing, and immutability

The versioned migration mechanism, backups, schema-behind/ahead checks in `db.connect`, foreign keys, and append-only evidence tables are real strengths. Current quick/FK/integrity checks are clean.

Remaining structural issues:

- “append-only” is not enforced with triggers/permissions; run rows and render statuses update in place.
- `scan_hits.scan_run` is not a foreign key and some status vocabularies/transitions are unconstrained.
- NULL-version uniqueness semantics can permit logical duplicates without application guards.
- `annotations` lacks its required identity/lineage constraints.
- `scan_hits` lacks a composite run/paper/version access path; `classification_evidence` lacks a reverse index on `scan_hit_id`.
- Annotation already needs `INDEXED BY` to avoid a measured multi-second-per-paper plan (`pipeline/annotate.py:102-109`), indicating query/index design is at its limit.
- `db.connect()` rejects a future schema, but the migration CLI reports `ver >= HEAD_VERSION` as “up to date” rather than refusing it.
- WAL plus a 1.8 GB live database has no consistent snapshot/backup protocol, restore drill, retention rule, or release checkpoint.

Add database-enforced immutable states, exact foreign keys/unique constraints, required composite indexes, explicit run-attempt/release-member tables, and tested online snapshot/restore procedures. Release generation must use one consistent read transaction or an immutable database snapshot, never a database changing underneath it.

## Scientific and statistical review

### 1. Freeze one primary estimand in code, documentation, and data

Commit `724271e` says the v1 estimand was adopted, but the decision is not consistently represented. `README.md:3-13` still says no preregistered estimand; `LEDGER.md:156-166` still calls the choice pending; `WORKFLOW.md` contains no v1 acquisition-to-artifact-manifest scan command; the site/report remain mixed-version; and the release schema cannot express the acquisition/version policy rigorously.

A defensible primary estimand is:

> Among math-primary arXiv papers first submitted in a prespecified interval, what proportion have, in the rendered text of the version-1 artifact acquired under a documented protocol, an explicit author statement that a generative-AI/agent system assisted production of that paper?

Secondary estimands can include:

- the latest version at one common fixed follow-up cutoff;
- disclosure added, removed, or changed between exact versions;
- comments-field disclosure as a separate metadata channel;
- PDF-only/unsupported/missing strata and worst-case bounds;
- cross-listed mathematics as a sensitivity population; and
- separately validated CAS, proof-assistant, and custom-computation instruments.

Do not describe the outcome as prevalence of AI use. It is prevalence of **visible author reporting captured by a specified instrument**, jointly determined by actual use, disclosure norms, artifact/version, author interpretation, and detector sensitivity.

Current report structures are paper-keyed (`pipeline/report.py:118-160,181-185`), so a run containing more than one version of a paper would collapse them. A version-history study needs `(arxiv_id, version, artifact_id)` as the analysis key throughout sampling, rollup, human review, release membership, and reporting.

### 2. The present trend is confounded by version observability and measurement error

The current curve rises from near zero in 2023–24 to 15.0% in July 2026 and 22.3% in the partial August window. This may contain a strong real signal, but its magnitude is not yet identified:

- 95.0% of the denominator has unknown source version, concentrated in older S3 months;
- known v1/later availability is concentrated in recent months;
- the S3 blobs appear to be rerolled at varying lag, but the calibration is untracked;
- older and newer papers have different follow-up opportunity for disclosure edits;
- the scanner/classifier vocabulary may have time-dependent false positives/negatives;
- failures and PDF-only exclusions vary by source format/month; and
- no human error study estimates differential sensitivity/specificity by time.

Keep the transparent version-stratified table in `reports/report_3yr_preliminary.md`; make it primary on every exploratory view. Do not pool unknown, v1, and later artifacts into a headline until the version policy is fixed and missingness/measurement assumptions are explicit.

### 3. Validation must match every public claim family

The proposed POS/FLAG/NEG probability sample is a sound outline for overall system precision and missed-disclosure estimation once correctly release-bound. It does not automatically validate:

- weekly or daily trend shape;
- subfield ranks/differences;
- tool/model/provider/agentic shares;
- category, impact, location, and catalytic labels;
- v1-versus-later changes;
- non-English or unusual disclosure forms; or
- CAS/prover/custom-code coverage.

Errors may vary along every one of those dimensions. Either suppress fine-grained claims until adequately double-reviewed samples exist, or prespecify a hierarchical measurement-error model and allocate validation across the dimensions it estimates. Do not promote a point estimate merely because a global precision estimate looks high.

For release stratum `h`, a simple design-based truth-total estimator is

`T_hat = Σ_h N_h (y_h / n_h)`

with prevalence `T_hat/N`, a finite-population/design-respecting variance or bootstrap, and explicit treatment of uncertain/insufficient cases. Candidate precision and false-omission rate come from their proper strata. Sensitivity requires combining estimated true positives and false negatives; it is not `1 - miss fraction among model negatives`.

Report at least:

- raw classifier-positive rate;
- human-corrected prevalence with interval;
- positive predictive value and system sensitivity with intervals;
- missing-outcome identification bounds;
- version/source-format strata;
- inter-rater agreement and adjudication rate per axis; and
- sensitivity analyses for ambiguous verdict handling.

Wilson intervals can describe a simple proportion under a stated sampling/superpopulation model. They must not be presented as total uncertainty when measurement, version, missingness, selection, and temporal dependence dominate.

### 4. Scope is narrower than the public copy

The classifier selects only scan hits with `tier IN ('llm','generic')` (`pipeline/classify.py:77-85`). The author-use taxonomy is explicitly AI/LLM (`pipeline/taxonomy.py:18-31`). A Lean/CAS/prover mention is classified only when it happens to co-occur with an LLM/generic trigger; the pipeline is not a comprehensive census of proof assistants, symbolic computation, or custom code.

Nevertheless, `pipeline/build_site.py:339-342`, `pipeline/sitetext.py`, the pitch, and chart labels describe chatbots, coding assistants, proof tools, CAS, and broader computational mediation together. Narrow the current headline to explicit generative-AI/agent disclosure. Build separate lexicons, negative samples, label rules, render checks, and gold studies for CAS/prover/custom-code families before comparing them.

Taxonomy boundary cases also need further adjudication. For example, AI-generated formalization plus independent kernel verification does not automatically resolve whether the epistemic impact is supportive or result-bearing; the role of the generated content, retained argument, human specification, and independent verification all matter. Do not let one model's paper-level maximum turn a nuanced multi-role statement into a high-stakes public label without axis-specific human review.

### 5. Exploratory rankings need statistical restraint

The site ranks subfields by raw rate with only `n >= 100` (`pipeline/build_site.py:203-209,287-291`). It offers daily/weekly/monthly and 3-month/1-year/3-year windows, multiplying opportunities for volatile patterns. It uses no shrinkage, multiplicity control, temporal dependence model, composition adjustment, or minimum positive count. Short-window subfield and provider rankings are especially unstable.

Before public comparison:

- preregister primary time granularity and contrasts;
- use complete periods and show partial-period status;
- apply minimum denominator and numerator/privacy thresholds;
- use partial pooling or uncertainty-ranked rather than raw-ranked displays;
- adjust or at least disclose multiplicity;
- decompose composition change versus within-subfield change; and
- publish underlying aggregate cells and code for every chart.

Keep daily controls for internal exploration, not as an invitation to infer daily societal changes from sparse classifier counts.

### 6. Development checks are not gold validation

The legacy 30-item spot check, 200-paper agent audit, and external “awesome AI for math” list remain useful kink-finding exercises only:

- the single-reviewer spot check is selected development data, not blinded evaluation;
- the agent audit is neither human truth nor a direct sensitivity estimator;
- the external list tests whether known entries receive a keyword flag, not whether the disclosure taxonomy is correct; and
- all were used during instrument development, so they cannot serve as untouched final evaluation.

`pipeline/sitetext.py:34-43` still describes the agent audit and says the classifier gets only a “small fraction” wrong despite no human estimate. Remove the latter language. Put development checks on a methods page, clearly separated from final gold metrics.

## Annotation, research ethics, privacy, and governance

### Human annotation operations

The HTML interface is much safer and more usable than the iteration-3 Markdown-only boundary. It escapes manuscript metadata/excerpts, has structured controls, autosave, JSON export, path-confined reviewer names, and taxonomy enum checks. Those are meaningful fixes.

Production annotation still needs:

- immutable per-reviewer assignment and packet manifests;
- exact release/version/artifact/context/PDF hashes;
- a shared powered double-code subset;
- uniqueness on project/release/item/version/reviewer;
- transactional ingest that updates duplicate detection within the file;
- codebook/manifest membership validation;
- explicit COI/recusal/reassignment and unreadability fields;
- reviewer training and calibration records;
- protocol-adherence fields for negative search;
- adjudicator identity and append-only adjudication rows;
- per-axis agreement, uncertainty, and design-weighted estimators; and
- separate instrument-development and locked-evaluation projects.

Browser state is keyed only by project/reviewer (`pipeline/annotate.py:390-405`), so a regenerated packet can inherit old answers. Key it by packet hash and warn/refuse on mismatch. Project is embedded into inline JavaScript without the same `<` escaping used for item arrays, creating an operator-controlled `</script>` injection route. Remove the Markdown ingestion path from production; its globally parsed `## ITEM`/field delimiters remain unsafe around hostile text.

Embedding hundreds of untrusted PDFs directly into a local browser packet increases PDF-viewer attack surface and distributes more copyrighted material than necessary. Prefer a patched sandboxed viewer or separate access to exact versioned PDFs; minimize local copies and document deletion.

### Manuscript and reviewer-data confidentiality

The project stores OAI submitter names, abstracts/comments, full source/PDF artifacts, exact snippets, raw model responses, reviewer assignments, notes, and locally embedded PDFs. No tracked policy defines purpose limitation, minimization, access roles, encryption, backup/restore, retention/deletion, access logging, incident response, vendor processing, international transfer, reviewer confidentiality, or breach response.

Observed database/corpus/packet files report mode 0777. On DrvFS those bits may not describe the effective Windows ACL, so neither “0777” nor `.gitignore` establishes protection. Verify and document NTFS ACLs, full-disk/volume encryption, backup access, shared-machine boundaries, and deletion behavior.

Collecting `papers.submitter` (`pipeline/harvest.py:79-95`) needs a stated research purpose. If not required, stop collecting it and remove it from future snapshots. Raw responses and snippets sent to a model need an institutional determination covering the provider's terms, retention, training use, subprocessors, confidentiality, and transfer location.

### Publication and correction boundary

The repository still tracks paper-level expressive artifacts in `results/` and `reports/awesome_validation.json`: IDs/titles, source paths, long excerpts, automated/human judgments, and locally derived labels. `TAXONOMY.md:82-106` names individual illustration papers with single-reviewer development judgments. These conflict with `WORKFLOW.md:73-81` and the aggregate-only owner decision.

The newer sensitive spot-check file and AWS instance file were removed/ignored, but remain recoverable in Git history. Removing a current file is not history sanitation. Before a public repository:

1. Define a machine-enforced allowlist for publishable aggregate schemas.
2. Move all per-paper expressive/reviewer/model data to access-controlled storage.
3. Assess with institutional counsel whether Git history must be rewritten; coordinate before any destructive rewrite.
4. Capture artifact-level arXiv version/license and permitted use.
5. Publish a correction/appeal/takedown policy and versioned correction ledger.
6. Avoid paper-level public labels until legal/ethical review and, for high-stakes claims, human verification/author-contact policy are approved.

CSV is an additional security boundary. Legacy exports pass cells directly, and a tracked cell begins with `=`. CSV quoting does not prevent spreadsheet formula execution. Make typed JSON/Parquet canonical and produce a separately labeled spreadsheet-safe CSV that neutralizes leading whitespace/control characters followed by `=`, `+`, `-`, or `@`.

### Missing legal and community governance

There is still no tracked project/code license, data/documentation license, NOTICE, SECURITY policy, privacy/retention policy, governance document, CONTRIBUTING guide, code of conduct, CITATION metadata, changelog, corrections policy, or responsible-disclosure process. A planning sentence mentioning ODC-BY does not grant a license.

`DESIGN_PLATFORM.md:10-17` asserts that IDs plus derived labels are legally publishable. That is not self-establishing: paper-level professional/reputational effects, identifiability, database rights, version-specific arXiv licenses, model-derived content, and data-protection/ethics obligations require competent review. “Open annotations” in `PITCH.md:67` also conflicts with aggregate-only commitments at `PITCH.md:77-80` and `DESIGN_PLATFORM.md:126-131`.

Seek institutional legal, research-ethics, data-protection, information-security, and arXiv-brand/trademark review before public launch. The independent/non-affiliated disclaimer is excellent and should remain, but the project name/visual treatment can still imply affiliation.

### Future features require separate protocols

The community workflow in `PITCH.md:69-75` asks volunteers to upload a paper to a provider and return conversation share links. It conflicts with the zero-backend design and would introduce third-party disclosure of paper content, prompts/account metadata, provider terms, consent/withdrawal, moderation, link rot, malicious URLs, SSRF if fetched server-side, and seeded-case deception concerns. A share link does not reliably prove model/prompt/config identity.

Prefer structured reviewer attestations and locally validated response records. If the service is pursued, design it as a separate human-subject/community-data system with authentication, assignment integrity, consent, privacy notice, retention/deletion, abuse response, and no generic server-side URL fetcher.

OpenAlex-based author/affiliation/career-age/productivity profiling (`DESIGN_PLATFORM.md:55-59`) similarly needs a separate measurement and ethics protocol. Disambiguation error and career/affiliation inference can create sensitive, misleading comparisons. Do not bolt it onto WP1 merely because the metadata is accessible.

WP2 prose detection and WP3 error auditing are also distinct studies. Detector-inferred writing can imply undisclosed conduct; paper-error labels are high-stakes. They need independent preregistration, validity studies, expert adjudication, reporting thresholds, appeal/correction policy, and access controls. Keep them out of the current release schema until those gates exist.

## Website, public communication, and reach

### What is working

The current source site is visually polished, fast, static, aggregate-only in its visible result layer, free of analytics/trackers and runtime third-party dependencies, and much more transparent than earlier versions. It has a prominent prototype/non-affiliation/do-not-cite warning, provenance text, accessible table alternatives for many charts, theme controls, responsive high-level layout, and useful time/subfield exploration. These are strong choices for privacy, resilience, and public comprehension.

The report is especially good at exposing partial/dirty/non-isolated provenance and separate v1/later/unknown tables. That degree of candor should become the website's default, not remain in a technical artifact.

### Three incompatible deployable artifacts

The repository currently contains:

1. `site/index.html`: the current 2.1% preliminary page;
2. `site/dashboard.html`: a stale directly addressable template/fragment with an obsolete “142” result and no current warning; and
3. `dist/arxiv-observatory-site.zip`: the older 16.1% site.

If `site/` is published wholesale, the stale dashboard is public. If the ZIP is shared, it publishes a radically different result. Move templates outside the publish root; delete or quarantine old distributions; generate into a clean staging directory; and deploy an exact allowlist from one release manifest.

### Site provenance is insufficient

`site/data/disclosures.json` records scan/classification IDs, model/taxonomy/lexicon, and evidence-gate booleans. It omits or underexposes:

- release ID and release-manifest hash;
- scan status and code commit;
- classification code commit and `isolate=0`;
- source-version composition;
- scan/fetch/classification missingness;
- render-state distribution and fuzzy-review status;
- human validation project/results;
- acquisition manifest/license policy; and
- hashes for every displayed aggregate/data artifact.

The website should not build from a non-release. Once releases exist, put a compact “What exactly is measured?” card beside the headline and a persistent version/missingness/validation summary above exploratory charts.

### Derived provider and agentic panels are unvalidated

The new provider/agentic section is generated by hand-maintained regexes (`pipeline/sitetext.py:73-122`). It has no gold labels or test corpus. In `pipeline/build_site.py:292-307`, `n_named` counts every named tool, including proof assistants/CAS later excluded from provider groups. Those papers can then land in “chat/other only,” although the copy contrasts agentic systems with chat assistants. A broad `copilot|agent` expression can also misclassify ordinary names/phrases.

Keep verbatim grounded tool strings in internal diagnostics, build a reviewed normalization table with version/provenance and “unknown/unmapped,” and validate provider/agentic mapping on a human-labeled sample. Suppress market-share/agentic comparisons until then.

### Reproducibility and determinism

Site generation still depends on set iteration and `Counter.most_common()` tie order (`pipeline/build_site.py:182,191-218,258-260,278-318`). Tied labels and top-N cutoffs can change under a different `PYTHONHASHSEED`. It embeds `date.today()`, and template mutation relies on brittle literal assertions/replacements of `site/dashboard.html` rather than a complete canonical data/template build.

The embedded submission-history blob is manually tracked rather than generated from a release data asset. Public JSON does not contain all provider/agentic/window panels, so it cannot reproduce every rendered claim.

Reader-facing methods language says the observations run “to today,” while the current data stop on 2026-08-08 and the page was generated on 2026-08-11. Always expose the exact data cutoff and whether the last period is partial.

Sort all outputs by explicit canonical keys such as `(-count, normalized_label)`, use a release timestamp/`SOURCE_DATE_EPOCH`, generate every displayed value from one canonical aggregate file, normalize ZIP member order/mode/timestamp, and add a CI test that builds twice under different hash seeds and compares bytes.

### Accessibility and web security

Improvements include a real document skeleton, language/viewport metadata, escaped SVG labels, `<`-safe embedded item arrays, `textContent` in the newer tooltip path, real buttons, and table alternatives.

Remaining issues:

- disclosure SVGs have `role="img"` but no overall accessible name/description;
- important hover interactions are pointer-only;
- no skip link, semantic `<main>`/`<footer>`, live-region feedback, or reduced-motion handling exists;
- `minmax(420px,1fr)` panels can overflow narrow phones;
- some dynamic tables/chips still use `innerHTML`, safe only while all inputs remain controlled;
- no automated accessibility/HTML/link test or documented keyboard/screen-reader/mobile test exists;
- inline CSS/JS complicates a strict CSP; and
- no deployment configuration supplies CSP, `frame-ancestors`, `object-src`, referrer, nosniff, or permissions headers.

Use DOM construction instead of `innerHTML`, label/describe every SVG, make every data point keyboard/touch accessible or expose the table by default, add axe/Pa11y plus manual screen-reader/mobile checks, and define/test security headers at the actual host.

### Reach should follow credibility, not precede it

After validation, improve public usefulness with:

- a stable methods page linked at every chart;
- release ID/hash/date and downloadable aggregate schema;
- a clear distinction among disclosure, use, and detector inference;
- short plain-language “how to read this” and limitations boxes;
- citation metadata and a reproducible citation string;
- corrections/appeals/version history and an RSS/Atom correction feed;
- canonical URL, Open Graph/social card, favicon, sitemap/robots, and schema metadata;
- an accessible press/media note discouraging misconduct interpretations; and
- a working repository, contact, privacy, and governance link.

Do not optimize shareability of fine-grained rankings before uncertainty and correction mechanisms are ready. The strongest outreach story is a transparent methods-first release with reusable aggregates, not a mutable dramatic percentage.

## CI, packaging, deployment, and supply chain

### CI remains narrower than its comment

`.github/workflows/ci.yml:1-17` says “tests + site build,” but only installs dependencies and runs pytest. Action commits are SHA-pinned, which is good, and the job has no corpus/secrets. Missing controls include:

- `permissions: contents: read`;
- job timeout/concurrency cancellation;
- Python 3.10–3.12 matrix despite the declared range;
- `pip install .` and packaging validation;
- lint, type checking, SAST, secret/dependency/license scans;
- hostile archive/gzip/PDF/HTML/Markdown/CSV fixtures;
- migration from realistic older schema;
- fetch/harvest/AWS producer/import/teardown tests;
- classifier resume/attempt-history and interruption tests;
- clean-clone fixture end-to-end scan→classify-mock→render-mock→gold→release→site test;
- site build, standards, accessibility, link and CSP tests;
- deterministic release/ZIP rebuild and tracked-artifact drift check; and
- SBOM/provenance/attestation output.

Normal pull-request CI executes contributor Python. The current no-secret/no-corpus runner keeps the direct risk modest, but it contradicts `DESIGN_PLATFORM.md:133-134`'s blanket claim that external PRs structurally cannot execute code. Never promote PR artifacts directly into trusted corpus/model/deployment workflows.

### Dependencies and environment

`requirements.lock` now pins current Python dependencies, including Requests 2.34.2 and pytest 9.0.2. This resolves the prior Requests version concern. The lock has no hashes or resolver provenance. `pyproject.toml` has no build system, console entry points, authors, license, URLs, or complete metadata.

Codex CLI/model behavior, SQLite, Poppler/pdftotext, AWS CLI, tar/gzip implementation, OS libraries, browser, and cloud image remain unpinned. These materially affect classification, rendering, acquisition, and packaging. Define a reproducible container/environment with hashed Python wheels and system packages; record an SBOM and tool versions in releases.

### No deployment chain exists

There is no tracked hosting/deploy configuration, protected environment, preview policy, provenance attestation, domain/header configuration, rollback procedure, health check, or artifact drift monitor. GitHub Pages is discussed but not implemented. The ZIP is manually stale.

Implement a release-only deployment workflow:

`validated release snapshot → deterministic build → security/accessibility checks → signed checksums/attestation → protected manual approval → allowlisted upload → post-deploy hash/header/link check → rollback pointer`

Do not give corpus/model/AWS credentials to pull-request jobs. Use separate protected identities for acquisition, analysis, and static deployment.

## Specifications, plans, and documentation

### Cross-document drift

The documents are thoughtful but no longer describe one executable system:

- `README.md:11` still points readers to `review_codex2.md` as current and says immutable provenance is absent rather than partial.
- `LEDGER.md:156-167` says the large v2 rebuild and estimand choice are pending even though data/classification/refill work ran; other “done” claims overstate strict gold/release behavior.
- `WORKFLOW.md:43-58` requires isolate, rendered evidence, and freeze, but the checked-in results violate all three and the tools do not enforce them.
- `WORKFLOW.md:79-81` calls `files` frozen forensic history even though import/fetch/scan still mutate/use it.
- `WORKFLOW.md:13-14` says reports/site are pure functions of one scan and classification run; site/report do read live mutable metadata/status and site is not release-bound.
- `GOLD_STUDY.md` promises a frozen cohort, all-item double review, adjudication and estimators that the current command/schema do not implement; the later partial-double-review section conflicts with the earlier rule.
- `pipeline/aws/README.md` references a missing provisioner and labels the importer pending.
- `DESIGN_PLATFORM.md:10-17` proposes public paper-level extracted labels and calls them legally publishable, conflicting with aggregate-only decisions and unreviewed law/ethics.
- `PITCH.md:60-80` simultaneously promises open annotations and aggregate reporting.
- The static-site/no-backend architecture conflicts with the future assignment/submission/share-link service.
- `OVERNIGHT_PLAN.md` is correctly marked superseded; keep obsolete operational plans out of active runbooks.

Convert `LEDGER.md` into a concise decision/status log with date, owner, evidence, and acceptance test. Separate “implemented,” “executed,” “validated,” and “released.” Generate current run/release tables from machine manifests rather than hand-editing status prose.

### Prior art

The iteration-3 primary-source corrections are now reflected well. In particular, the revised notes distinguish the updated Patterns and Purposes v2 numbers, the self-selected survey sample, foundation-model-use rather than citation-only mining, Andrew Gray's actual estimand, Pangram's held-out scientific-paper FPR, 35 papers/40 errors in the grading benchmark, the unreproduced secondary trend claim, and bytes rather than submission share in the arXiv-source study.

Retain the caveats:

- `PRIOR_ART.md` is a non-systematic landscape review, not a systematic review;
- some sources are vendor/blog/LinkedIn announcements rather than independent scientific evidence;
- exact paper versions and access dates should be pinned in a bibliography ledger;
- NBER, RAID, and bioRxiv items were not independently verified in the earlier selective primary-source pass; and
- the title/date and “current” statements will age quickly.

For a publication, create a structured bibliography with exact version/DOI/URL/access date, evidence type, population, estimand, sample, and limitations. Re-run primary-source verification shortly before submission.

### Repository hygiene

The root remains cluttered by legacy outputs and unrelated `.claude/docs/lean4` / `.claude/tools/lean4` trees. Either document their provenance, ownership, license, and security role, or move/remove them before public release. Keep templates, generated artifacts, restricted data, and source code in clearly separate top-level locations.

Use a clean public repository/export rather than assuming `.gitignore` turns the current research workspace into a safe public tree. The ignored database, corpus, packets, logs, backups, local email/pitch artifacts, and historical Git objects need an explicit publication review.

## Iteration-3 status map

| Iteration-3 issue | Version-4 status |
|---|---|
| No end-to-end v2 data | **Resolved for engineering:** large import/scan/classification now exist; not a release |
| P0-1 stale legacy site | **Partial:** current source site rebuilt; stale dashboard and ZIP remain; site unfrozen |
| P0-2 incomplete scans called complete | **Substantially fixed:** item states/run partial honest; PDF exclusions and coverage gate remain |
| P0-3 cross-scan report leakage | **Fixed in report/site:** evidence-scoped and tested; still present in gold POS sampling |
| P0-4 weak freeze | **Partial:** pending/only-failed/duplicate ID checks added; partial/dirty/non-isolated/ungated/unvalidated still accepted |
| P0-5 non-materialized release | **Unresolved:** releases remain live-table manifests; none exist |
| P0-6 gold integrity | **Partial/new blocker:** better UI/strata/plants, but wrong cohort/version and no release/manifest/estimator binding |
| P0-7 agentic manuscript boundary | **Unresolved and exercised at scale:** actual run was non-isolated |
| P0-8 expressive tracked outputs | **Unresolved** |
| Version policy | **Decision claimed but execution broken:** v1 refill not scanner-consumable and mostly incomplete |
| Render validation | **Partially executed:** 1,363 rendered author-use snippets; most unknown; gate off; fuzzy auto-accepted |
| S3 acquisition | **Successful import, unsafe producer/teardown process** |
| Prior-art factual corrections | **Substantially resolved** |
| Requests/proxy issue | **Resolved in fetch/render; harvest still lacks equivalent controls** |
| Site escaping/empty cohorts | **Substantially resolved in generator** |
| Tests/dependency pins/CI | **Improved:** 73 green tests and pins; no E2E/site/release/deploy assurance |
| Governance/licensing/privacy | **Unresolved** |

## Prioritized delivery plan

### Immediate operational containment — now

1. Review the mass `export.arxiv.org` v1 job with the owner; pause or continue only under an approved/documented acquisition policy. Preserve its current successful artifact ledger and do not delete data.
2. Mark the current scan/classification/report/site explicitly “exploratory engineering output”; do not deploy or circulate the ZIP.
3. Remove `site/dashboard.html` and the stale ZIP from any publish/deploy allowlist.
4. Take a consistent SQLite/WAL snapshot and record the active acquisition target/progress/command/code/environment before further schema or data changes.
5. Do not ingest the current packet as final gold. Preserve it as instrument-pilot data with that status.

### Gate A — acquisition and version spine

- Freeze the primary v1 and secondary version estimands in a machine-readable protocol.
- Obtain/record an approved historical acquisition route.
- Add immutable acquisition runs/attempts and per-artifact version/license/provenance.
- Make scan jobs consume exact artifact manifests, including v1 refill artifacts and PDF-in-tar members.
- Reconcile every target paper into one reason-coded terminal acquisition state.
- Add recursive OAI reparse, tombstones, strict IDs, response bounds, and atomic storage.
- Reproduce and publish the S3 reroll-lag calibration method/data internally.

**Acceptance:** a clean query proves exact artifact/version/hash/license and terminal state for every frozen frame member; a clean-clone fixture reconstructs the manifest.

### Gate B — safe, reproducible extraction and classification

- Finish archive/PDF resource/path/sandbox hardening.
- Run a new scan from the exact versioned artifact manifest at a clean commit/container.
- Classify with a safe non-agentic backend or enforced one-paper empty-root isolation.
- Record every invocation/resume, full effective prompt/config/runtime, request identity, and log hash.
- Ground quoted evidence plus all claimed verbatim tool/model strings.
- Run immutable exact-version render checks; human-review fuzzy matches.
- Resolve or explicitly bound every error/unsupported state.

**Acceptance:** all release-eligible positives satisfy the registered evidence channel and render policy; no dirty/unknown/non-isolated execution can pass the release contract.

### Gate C — locked human validation

- Materialize the release cohort first.
- Draw a new sample from exact release membership with correct inclusion probabilities.
- Bind item/version/artifact/context/PDF/packet/assignment hashes.
- Define a shared stratified double-coded subset with enough power for claimed axes.
- Record COI, unreadability, search process, plant status/outcome, and protocol adherence.
- Implement signed manifest-aware ingest, database uniqueness, adjudication, per-axis agreement/CIs, finite-population estimators, missingness bounds, and bootstrap uncertainty.
- Keep instrument-development cases and final evaluation separate.

**Acceptance:** independent rerun of estimator code from released aggregate/adjudicated inputs reproduces every validation and corrected-prevalence number; no current annotator knows final stratum/machine labels during review.

### Gate D — immutable release and publication

- Build a materialized release snapshot with complete membership and hashes.
- Generate report/site/data/package only from `release_id` in a fresh staging directory.
- Include release timestamp, code/container/SBOM/model/tool/acquisition/gold identities and all output hashes.
- Build twice under different hash seeds and byte-compare.
- Run standards, accessibility, link, hostile-input, CSP/header, and package-drift tests.
- Publish only aggregate allowlisted files; remove/quarantine stale and expressive artifacts.
- Establish institutional legal/ethics/privacy/security approval, licenses, correction/takedown, and incident policies.

**Acceptance:** a protected deployment verifies the exact signed manifest on the host and can roll back to the prior release without touching the research database.

### Gate E — responsible public growth

- Launch with one conservative validated headline and visible limitations/version/missingness.
- Provide methods, aggregate downloads, citation, correction feed, contact, and governance pages.
- Add subfield/tool/impact/provider views only as their axis-specific validation clears prespecified thresholds.
- Maintain a public release/correction ledger; never silently mutate past numbers.
- Scope and preregister WP2, WP3, author profiling, and community contribution systems independently.

## Concrete release checklist

A numerical release should fail closed unless every answer is “yes”:

- [ ] Is the estimand and source-version policy frozen and machine-readable?
- [ ] Is every frame member in exactly one reason-coded acquisition/scan/classification state?
- [ ] Does every scanned item reference an immutable artifact ID, exact version, byte hash, and license?
- [ ] Are missing/unsupported rates below a preregistered threshold, with identification bounds reported?
- [ ] Were scan/classification/render stages run from clean, reproducible code/environment identities?
- [ ] Was model execution isolated/tools-off with confidentiality controls and a complete invocation ledger?
- [ ] Are all headline evidence quotes grounded and rendered under the registered channel policy?
- [ ] Were fuzzy render matches adjudicated rather than auto-certified?
- [ ] Is the final gold sample drawn from exact release membership and locked after instrument freeze?
- [ ] Are double review, COI, adjudication, agreement, weighted estimators, and uncertainty complete?
- [ ] Are every displayed axis and comparison supported by relevant validation or clearly suppressed?
- [ ] Is the release a materialized immutable snapshot consumable without live research tables?
- [ ] Do report, site, JSON, ZIP, manifest, SBOM, and checksums derive deterministically from that snapshot?
- [ ] Does CI reproduce and verify bytes, accessibility, links, headers, and package contents?
- [ ] Are only aggregate allowlisted artifacts public, with minimum-cell/privacy rules?
- [ ] Are code/data/document licenses, privacy/security/governance, correction/takedown, and incident policies approved?
- [ ] Is deployment protected, hash-verified, monitored for drift, and rollback-capable?

## Final assessment

Iteration 4 is the strongest engineering state of the project so far. The S3 reconciliation, per-item scan ledger, artifact hashes, normalized evidence links, scoped report queries, explicit version strata, strict failure visibility, green fixture tests, improved site, and candid provenance are all valuable. The project has moved from a fragile hackathon demonstration to a credible research-infrastructure prototype.

The next step is not another more polished headline. It is to close the measurement chain. The current result still combines unknown versions, partial coverage, an unsafe non-isolated model run, optional rendering, no final human truth study, and no release object. The new v1 data path and gold workflow each contain a cross-stage mismatch that would invalidate the intended remedy if left uncorrected.

If the team first makes exact artifacts scan-consumable, runs a clean isolated/rendered pipeline, fields a release-bound locked gold study, materializes a deterministic release, and establishes governance, ArxivObservatory can become scientifically valuable and unusually transparent. Publishing the current 2.1% or current packet as validated would spend that credibility before it has been earned.
