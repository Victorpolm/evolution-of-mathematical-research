# ArxivObservatory repository review — iteration 6

**Audit snapshot:** Git commit `e2293d6c5e83b511643922923b4bbbd24dcf0eab`, tree `bfb5b97644228451daca978213efe4586227d258`, 2026-08-11 17:43 CEST. The worktree was clean before this review file was added.

**Primary delta reviewed:** commit `e2293d6` (“Review-5 triage: enforced refill boundary, real USD budgets, native schemas, freeze/resume closure, v1 strata”), including `pipeline/llm_api.py`, API dispatch and validation in `pipeline/classify.py`, v1 acquisition/scanning, release gates, the limitations card, gold-study artifacts, `DECISIONS.md`, and the associated tests. I also re-reviewed the rest of the repository, current generated site/report, live run and acquisition ledgers, specifications, scientific design, cloud/deployment code, CI, privacy, ethics, licensing, and public communication.

**Audit boundary:** read-only except for creating this file. I did not stop or start the active refill, invoke any model, mutate the database or corpus, contact arXiv, operate cloud resources, or deploy the site. I used the network only to check the current official OpenAI structured-output/model/data-control documentation and Anthropic strict-tool documentation. The corpus database and refill ledger were actively changing during the audit, so all empirical observations are explicitly time-bounded and are not a release snapshot.

## Executive verdict

Commit `e2293d6` is another substantial improvement. The following fixes are real and worth preserving:

- the currently running refill was restarted against a finite 2,122-paper flagged target set, and the target hash independently reconstructs correctly;
- the dangerous TeX-altering JSON “repair” was removed;
- OpenAI requests now use a strict native JSON schema, generated from the taxonomy;
- API calls use fixed provider origins, one paper per request, no tools, no redirects, and no ambient proxy or `.netrc` state;
- a within-process locked USD reservation and stop latch now prevent queued logical calls after the latch trips;
- freeze now rejects unpinned model labels, non-API backends, non-isolated classification, and dirty/unknown producer commit labels;
- resume now compares the backend and retries invalid rows;
- v1 provenance can distinguish explicit-v1 from inferred-single-version in the schema and report;
- fuzzy PDF matches are correctly kept out of the exact-rendered gate;
- the old 63-edge evidence gap has been repaired in the live database;
- the public page now has `noindex`, an up-front do-not-cite warning, conditional rather than “true prevalence” coverage wording, and machine-readable exploratory status;
- calibration packets are visibly marked as calibration in HTML;
- the unsafe AWS teardown path is disabled by default;
- all 94 fixture tests pass.

However, the statement that all four review-5 blockers are closed is too strong. Adversarial checks found that each claimed closure is partial:

1. The **active refill invocation** is finite, but the general CLI has two paths that can select the unapproved tail without `--include-unflagged-tail`.
2. The **USD latch** works inside one healthy process for one logical request per reservation, but it resets on resume, does not reserve physical retries, does not reserve concurrent tokens, and overwrites rather than accumulates the persisted usage record.
3. The dangerous **regex repair is gone** and OpenAI strict output is correctly configured, but Anthropic omits its required `strict: true`, the local validator accepts schema-invalid defaults, and valid JSON escapes can still corrupt TeX commands beginning `n`, `r`, or `t`.
4. Several **freeze/resume bypasses are closed**, but a run can still be resumed under changed or dirty code, decoder/schema/endpoint/settings, while freeze certifies only the original run row.

There is also still no release-valid scientific result. The current site remains a deliberately exploratory display of `2,799 / 131,310 = 2.1%` model-positive papers from a partial dirty scan and a dirty, non-isolated Codex run, with no annotations, no final gold study, no exact-render requirement, no v1-complete scan, and no frozen release. The principal database had zero `annotations` and zero `releases` at the audit snapshot.

My recommendation remains: **do not call the current percentage an estimated disclosure prevalence or promote it as a scientific result.** Keep the inspection page explicitly unreleased while closing the finite acquisition, durable budget, strict response, immutable protocol, release-bound gold, and governance contracts below.

## Verification of Claude's four headline claims

| Claimed closure | Audit status | What is genuinely fixed | What remains |
|---|---|---|---|
| Refill “physically cannot enter the tail” | **Partial** | The live 2,122-target invocation appears finite and in-scope. `--flagged-first` without a phase authorization is rejected. | `--v1-refill` alone is unguarded; `--v1-refill --flagged-only` without `--flagged-first` selects the whole remainder while labeling it flagged-only. The runbook documents the unsafe form. |
| `$50/provider` hard budget | **Partial** | A locked pre-dispatch estimate and stop latch work across workers within one process; unknown-price models fail under a USD cap. | Spend resets on every process/resume; transport retries share one reservation; token reservations omit in-flight work; the usage file is overwritten; physical attempts are not fully logged; the cap remains optional. |
| Native schemas and TeX-safe parsing | **Partial** | Regex repair is removed. OpenAI uses strict `json_schema`; schema originates in `taxonomy.py`. | Anthropic forces a tool without `strict: true`; the validator defaults missing required fields and coerces/truncates values; decoded `\nabla`, `\tau`, and `\ref`-style strings can still pass. |
| Freeze/resume closure | **Partial** | Backend, prompt, model, isolation, taxonomy, run set, model pin, API backend, and producer cleanliness have stronger checks. Invalid rows are retryable. | Resume omits code/config/schema/endpoint/budget identity. Sidecar invocations are not freeze-gated. Partial/selected scans and optional evidence gates can still be frozen. Site does not consume a release. |

The additional scientific changes are also mixed:

- the report now distinguishes `v1` and `v1_inferred`, but the site silently merges them;
- source-first v1 selection removes the outcome-conditioned PDF preference, but selection manifests do not contain their member preimage or enter run/release provenance;
- the limitations text is materially better, but it still conflates six known-version render failures with unknown versions, and detailed machine-readable limitations are absent;
- calibration HTML is honestly labeled, but a release-bound gold build, adjudication, estimators, and fail-closed ingest do not yet exist.

## Immediate operational finding: the current job is bounded, but the CLI is not

This finding should be read precisely. I found no evidence that the **currently running** job has entered, or can enter, the unflagged tail under its present target list.

`corpus/logs/v1refill_manifest_20260811T152608.json` records:

- mode `flagged-only`;
- scan run `tex-20260810T205113`;
- 2,122 targets;
- target SHA-256 `5d2a6d6f4704fc8e8d18f8cc7c159bfb96ec730ad22d1eef2440810db9d9dddb`;
- a six-second nominal delay.

The pre-start target set can be reconstructed from the database state, source universe, scan flags, seeded ordering, and attempt ledger. It contains exactly 2,122 IDs and reproduces the recorded hash. Read-only checks during the run found all observed attempt IDs inside that reconstructed target. The apparent overlap seen in one non-transactional live read was an active-write race, not evidence of failed targets; a later coherent check found only successful terminal results. This is a strong practical improvement over review 5.

The generic interface nevertheless fails the decision boundary:

- `pipeline/fetch.py:237-242` enforces authorization only when both `--v1-refill` and `--flagged-first` are present;
- `--v1-refill` alone therefore selects the entire remaining multi-version population at `pipeline/fetch.py:157-180,249-255` with no explicit tail authorization;
- `--v1-refill --flagged-only` without `--flagged-first` is worse: filtering occurs only inside the `if flagged_first` branch at `pipeline/fetch.py:181-197`, but the output and manifest call the result `FLAGGED-ONLY` at `:256-268`;
- `tests/test_review5.py:130-140` covers only the `--flagged-first` refusal and misses both bypasses;
- `WORKFLOW.md:43-48` documents exactly the unsafe unscoped form, with `--flagged-first` optional and neither authorization mode required.

This is a P0 operational defect because it turns the owner decision into a calling-convention convention rather than a safety invariant.

Required fix:

1. Require exactly one explicit refill mode for every `--v1-refill` invocation: a valid `--flagged-only --flagged-first RUN`, or `--include-unflagged-tail` plus a recorded approval/coordination reference.
2. Reject `--flagged-only` without a valid, compatible full-text scan run.
3. Make the two modes mutually exclusive; eliminate “unscoped.”
4. Test the complete argument truth table, including empty/missing/unknown scan runs and `--limit` interactions.
5. Put every target ID, requested version, selection reason, source universe hash, metadata cutoff, command/config, run ID, and terminal outcome into an immutable run-scoped manifest.
6. Make the attempt ledger run/manifest scoped. The current global JSONL and reconciliation can use an older invocation's 404 as a terminal outcome.
7. Emit and hash a final outcome manifest even after interruption/resume, not only after one uninterrupted natural completion.

The current target manifest contains a count and hash, not the target-ID preimage. Independent future verification therefore depends on mutable database state and a global ledger. A hash proves equality only when the exact member list is retained.

## P0 release blockers

### P0-1. API budgets are neither durable nor physical-request hard caps

The within-process reservation design in `pipeline/llm_api.py:219-265` is a useful foundation. Under one healthy process, a lock serializes reservations, an unpriced model is refused under a USD cap, and the stop latch prevents subsequent logical requests after the cap is reached.

The owner decision is a cumulative **per-provider pilot budget**, however, and the implementation does not enforce that contract:

- budget, settled usage, reservations, and stop state live in process globals at `pipeline/llm_api.py:58-65,182-199`;
- `pipeline/classify.py` starts with fresh globals and never reloads earlier spend when `--resume` is used;
- `pipeline/classify.py:605-609` overwrites `<run>.usage.json` rather than appending or merging it;
- each restart, crash recovery, or deliberate resume therefore receives a new full cap;
- `_reserve()` reserves one logical call, while `_post()` can make up to four physical HTTP dispatches at `pipeline/llm_api.py:270-294` after timeout, 429, or 5xx outcomes;
- those retries do not receive separate reservations or idempotency protection, although a timed-out request may have been processed and billed;
- exhausted transport failures create no physical-attempt row, contradicting the module's “every call attempt” claim;
- the token-cap check uses only settled `_usage`, not concurrent token reservations, so multiple workers can each pass the same remaining-token check;
- the input estimate `len(prompt) // 3 + 200` is not a guaranteed tokenizer/schema/tool overhead bound;
- `_settle()` can push actual cost beyond the reservation without latching the overrun;
- `--max-usd-per-provider` is optional, and the documented API command at `WORKFLOW.md:52-59` omits it and still describes only `--max-total-tokens`.

Safe mocked diagnostics reproduced the failure modes without making network calls:

- four simulated retryable transport responses produced four dispatches, no physical-attempt rows, and one logical reservation;
- concurrent calls could reserve a combined token maximum above the configured token cap because in-flight tokens were invisible.

The existing API pilot state also demonstrates the resume-accounting gap. The database held 16 Anthropic and 11 OpenAI classification items, while each surviving usage file described only the last two calls of a resumed invocation. The initial `classification_runs.params_json` still reports the original `limit_batches=5`, and sidecars rather than the run record describe later resumes.

Pricing note: I independently checked the current official model pages. The direct OpenAI Luna page supported the code's `$0.20` input / `$1.20` output per million tokens at audit time, and Anthropic's current Haiku 4.5 pricing supported `$1` / `$5`. I therefore do **not** report the transient cached-search `$1` / `$6` Luna result as a pricing defect. The episode does show why the release must retain the exact source URL, retrieval time, content hash/snapshot, tier assumptions, cached-token rules, and provider invoice reconciliation rather than merely an `asof` string. OpenAI currently prices some cache writes and long-context tiers differently; `_cost_usd()` has no such dimensions.

Required hard-cap design:

- store budget authorization, price snapshot, cumulative reservations, physical attempts, usage, and settlement in transactional append-only database rows;
- reload and lock cumulative provider spend before every resume;
- reserve each physical dispatch, including retries, or use documented idempotency where supported;
- include all in-flight USD and token reservations;
- use provider token counting or a demonstrable upper bound that includes schemas/system overhead;
- latch on either prospective or actual overrun;
- validate finite positive numeric limits (reject NaN/infinity);
- set provider-console spend/rate limits as a second independent control;
- reconcile ledger totals with provider billing before approving another invocation.

### P0-2. “Provider-native schema enforcement” is true for OpenAI, not Anthropic

The new schema generator at `pipeline/llm_api.py:130-167` is a good single-source-of-truth direction. OpenAI's request at `:347-360` uses strict `json_schema` on a fixed Chat Completions endpoint, which matches current official OpenAI Structured Outputs documentation. The current official Luna model page also lists Chat Completions and Structured Outputs support.

Anthropic's tool at `pipeline/llm_api.py:317-324` supplies an `input_schema` and forces tool choice, but omits the tool-level `strict: true`. Anthropic's official strict-tool documentation states that strict schema conformance requires that flag. Forced tool choice guarantees a tool call; it does not by itself guarantee schema-valid input. The module docstring's claim that all providers enforce a native schema is therefore inaccurate.

The local validator does not safely close this gap:

- `pipeline/classify.py:231-260` defaults absent `tools`, `models`, `categories`, `flags`, impact, and location instead of rejecting missing required fields;
- Python booleans pass numeric/int type checks unless explicitly excluded; a boolean confidence can become `1.0`, and a boolean item ID can pass an integer check;
- overlong strings are silently truncated rather than rejected;
- `extract_json()` permits surrounding prose and does not reject duplicate JSON object keys;
- schema arrays and strings lack useful maximum sizes, while local truncation hides provider/schema drift.

A synthetic author-use label missing the declared usage fields was accepted and defaulted to empty/unknown values. This proves that the schema and “fail-closed authority” validator can still disagree.

Required fix:

- add Anthropic tool-level `strict: true` and capture provider-body contract tests;
- reject every absent/null required field locally;
- explicitly reject booleans where integer/number is required and reject non-finite numbers;
- reject, rather than truncate, overlong/noncanonical values;
- parse the entire response document with duplicate-key rejection;
- put size/range constraints in the generated schema and test schema/validator equivalence;
- persist provider response ID, returned effective model, endpoint/API version, finish/stop/refusal reason, schema hash, request hash, response hash, usage, and physical retry number.

### P0-3. TeX strings can still be corrupted by legal JSON escapes

Removing the regex repair closed the specific `\beta`/`\Gamma` repair bug from review 5. The remaining control-character guard at `pipeline/classify.py:140` allows newline, tab, and carriage return, because those characters are ordinarily legal JSON string escapes.

That is unsafe for this domain. A malformed model response containing a single backslash before common TeX commands is valid JSON with a different meaning:

- `\nabla` can decode as a newline followed by `abla`;
- `\tau` or `\text` can decode with a tab;
- `\ref` can decode with a carriage return.

Synthetic diagnostics showed these values can pass validation. Whitespace-normalized quote grounding can then regard the corrupted string as grounded, because the inserted control character is normalized like ordinary spacing. `tests/test_review4.py` correctly covers an illegal `\Gamma` escape but explicitly permits normal newline data, so it misses the domain-specific ambiguity.

Native schema enforcement validates JSON structure, not whether TeX backslashes preserved the source text. The robust solution is to:

- reject every C0 control character in source-derived strings, including newline/tab/carriage return, or encode quotes as offsets into the supplied immutable snippet;
- require exact byte/character-span grounding before an `author_use` label is valid;
- store normalized display text separately from the exact evidence span;
- include regression tests for `\nabla`, `\newcommand`, `\tau`, `\text`, `\ref`, duplicate keys, surrounding prose, and provider refusals.

### P0-4. A classification run can still mix code and protocol revisions

Review-5 closed important holes: resume now checks backend as well as prompt/model/isolation/taxonomy/scan-run set (`pipeline/classify.py:487-509`), and freeze now rejects unpinned labels, dirty/unknown producer labels, non-API backends, and non-isolated runs (`pipeline/report.py:89-122`). Invalid rows are retryable rather than being permanently treated as done.

But a `classification_run` still has one original immutable-looking DB header and a mutable sequence of sidecar resumes:

- resume does not compare the current code commit/tree with the original run;
- it does not compare endpoint/API version, schema hash, validator/decoder version, provider settings, output maximum, pricing/budget configuration, worker strategy, or the full `params_json`;
- the item input hash at `pipeline/classify.py:114-127` omits backend, endpoint, schema, code, and effective protocol;
- later invocation metadata is appended only to `<run>.invocations.jsonl` at `:537-551`;
- freeze reads the original `classification_runs` row and never validates every invocation/attempt sidecar;
- those sidecars are mutable, unhashed, not foreign-keyed to items, and can lose buffered attempts on crash;
- retry records are drained by whichever future completes, without a durable invocation/request/item identity.

Therefore a clean partial API run can be resumed after code, schema, decoder, price, or endpoint changes—even from a dirty worktree—and later pass freeze under the original clean commit label. The backend fix prevents Codex/API mixing, but not protocol mixing.

Required fix:

- define one canonical protocol object containing commit and tree hashes, prompt bytes, taxonomy/schema/validator versions, backend/provider/model endpoint, provider options, output/token settings, pricing snapshot, isolation, scanner input set, and relevant constants;
- hash it into every item input identity;
- on resume, either require exact protocol equality or create a new superseding run;
- persist invocations and pre/post physical attempts in normalized append-only DB tables;
- bind each item/response to exactly one invocation and request;
- require a full resolvable 40-character commit plus tree hash, not merely a 7–40 hex-looking string;
- make freeze validate all invocations and the release-builder's own clean code state.

### P0-5. Freeze can still certify a selected or weakly gated denominator

`pipeline/report.py:61-123` accepts a scan run in `complete` **or `partial`** state. This can be scientifically defensible only if a release contract specifies a full target manifest, a reason-coded frame partition, an allowed missingness threshold, and an estimator that accounts for each excluded state. None is required.

In particular:

- a flagged-only v1 scan is explicitly described as “NEVER a prevalence denominator” in `pipeline/scan.py:294-312`, but nothing in scan-run params or freeze lets `report.py` detect that selection;
- scan-run params at `pipeline/scan.py:218-226` omit `--v1-corpus`, `--flagged`, cohort/months, artifact IDs, target/selection hash, metadata cutoff, and explicit/inferred basis policy;
- the v1 selection sidecar contains a count/hash but not the retained selection lines and is not bound into the scan run or release;
- freeze does not require `--require-grounded` or `--require-rendered`, despite the documented release command doing so;
- it has no required acquisition, version-completeness, gold-validation, calibration, licensing, or provider-policy gates;
- it permits a classification run that consumed multiple scan runs as long as the selected scan is among them;
- the release membership hash at `pipeline/report.py:388-420` is only `paper:version`; it omits version basis, artifact ID/hash, item/evidence/render/gold rows, selection/acquisition manifest, and environment;
- releases are application-enforced summaries, not materialized immutable datasets; there are no DB triggers preventing later mutation;
- `pipeline/build_site.py` accepts raw run IDs, not a release ID, and rereads live tables.

The synthetic freeze contract from the previous review accepted incomplete/selected examples; the new code closes several provenance-label checks but does not close the denominator contract. A scientific release should be one immutable materialized membership, not a promise to re-run queries over mutable state.

### P0-6. PDF-to-text cache reuse can create false provenance

Both `pipeline/scan.py:149-158` and `pipeline/render_check.py:193-201` trust any nonempty sibling `.txt` file without checking which PDF produced it. The scanner then hashes the **current PDF** at `pipeline/scan.py:195-213` while scanning the potentially stale cached text. The render checker similarly associates matches from the cache with the current PDF hash.

If a PDF is replaced or refetched at the same deterministic path, the ledger can assert that evidence came from bytes that were never converted. This is particularly important because `pipeline/fetch.py` uses deterministic versioned paths and because the project treats artifact hashes as the scientific provenance spine.

Fix by making derived text content-addressed and recording `{pdf_sha256, extractor name/version/config, text_sha256}`. Reject any cache without an exact binding. Run `pdftotext` with CPU, memory, process, output-size, and filesystem limits.

### P0-7. No release-bound human validation exists

The current calibration is now much more honestly labeled. `GOLD_STUDY.md:97-109` explicitly retires it from release-validity use; the HTML packets carry a visible calibration banner; the manifest contains `intended_use: calibration_only_never_release_validity`; and legacy Markdown ingest is gated behind `ARXIV_OBS_LEGACY=1`. These are meaningful ethical fixes.

The underlying 500-paper sample remains the old calibration population:

- 127/500 items are outside the public report frame;
- 448/500 have unknown scanned version;
- many packets therefore fall back to mutable `papers.latest_version` and a current PDF rather than the scanned artifact;
- the database has zero ingested annotations;
- the contexts file can be reused merely because it exists (`pipeline/annotate.py:282-299`), even if run, sample, files, extraction code, or artifacts changed;
- the manifest does not bind each item to release ID, scan/classification/evidence item, version basis, artifact/PDF/context/packet hashes, or reviewer assignment.

The final tooling still does not implement the promised release-bound design:

- `annotate build` has no `--release` argument and only optionally accepts cohort and evidence gates;
- it does not call the report/release compatibility contract;
- the POS query at `pipeline/annotate.py:195-208` is not scoped through classification evidence from the selected scan run;
- context is re-extracted from mutable `files`, not the exact scanned artifact;
- JSON ingest warns and proceeds if the manifest is missing (`pipeline/annotate.py:613-629`);
- ingest checks paper membership but not reviewer assignment, exact version, codebook equality, release/run, packet/manifest/context hash, or supersession;
- database annotations lack the required unique/provenance/design fields;
- agreement groups by paper, chooses the first two reviewer rows, covers only verdict, and has no per-axis uncertainty, adjudication record, or weighted estimator.

There is also a new statistical coding issue in the written protocol. `GOLD_STUDY.md:48-55` defines `UNCLEAR` and `INSUFFICIENT_EVIDENCE`, then maps every verdict other than `TRUE_DISCLOSURE` to non-disclosure. That deterministically imputes indeterminate/unreadable outcomes as negatives and can bias precision, sensitivity, and corrected prevalence. These must be reason-coded non-evaluable outcomes, handled by adjudication, bounds, weighting, or a declared missingness model.

The plant/search design remains calibration, not sensitivity estimation:

- plants are machine-selected POS/FLAG candidates rather than independently adjudicated true, findable disclosures;
- they condition on the detector's easier cases and cannot estimate atypical scanner-negative misses;
- bounded search examines selected sections, while the headline detector scans all source members;
- reviewer behavior fields such as PDF opened, queries/locations searched, time, plant found, unreadability, and COI are not captured;
- independent random order does not create the promised 100–150 shared double-coded items unless both reviewers finish nearly everything.

Before the final study, freeze the estimand/instrument, create an explicit shared-overlap assignment powered by stratum and axis, bind exact artifacts and rendered evidence, fail closed on ingest, record adjudication and COI, and implement the declared design-weighted estimators and uncertainty.

### P0-8. Aggregate-only policy is still contradicted by tracked repository artifacts

`DECISIONS.md:61-65` and `WORKFLOW.md:91-99` say public outputs are aggregate-only and that paper-level excerpts/labels remain restricted. The tracked repository still contains expressive paper-level artifacts:

- `results/ai_ack_hits.csv` and `.json`;
- `results/ai_ack_report.md`;
- `results/candidate_papers.csv` and `.md`;
- `results/manual_review.md`;
- `reports/awesome_validation.json`.

These expose IDs, titles, local paths, automated/human labels, and source excerpts. Some older sensitive outputs and cloud inventory also remain in Git history even after deletion/ignore rules. This is a publication, licensing, privacy, professional-reputation, correction, and policy-consistency problem.

Create a clean, allowlisted publication artifact from one release; quarantine paper-level outputs outside public Git; assess history sanitation before making the repository public; and publish only reviewed aggregates with minimum-cell rules, versioned corrections, contact/appeal/takedown procedures, and explicit rights analysis.

### P0-9. The current `2.1%` page remains an inspection artifact, not a prevalence estimate

The latest generated site is much more honest than its predecessors. It has a prominent top warning, `noindex`, non-affiliation language, a known-limitations card, a precise cutoff, conditional coverage-extreme wording, render-status counts, `release_status: unreleased_exploratory`, and `do_not_cite: true`. The static, aggregate-only, tracker-free presentation is a strong product and ethics choice.

The underlying data did not change into a validated measurement:

- scan `tex-20260810T205113` is `partial`, with 166,183 `ok` items, 811 unknown-format errors, nine incomplete items, and 2,162 skipped PDF-in-tar items;
- its code label is `f08502f-dirty`;
- classification `cls-20260810T211610` is a complete but dirty `gpt-5.6-sol@medium` Codex run with `isolate=0` and cross-paper batches;
- the public build requires quote grounding but not rendered evidence;
- the headline is 2,799 model-positive papers among 131,310 scanned cohort papers;
- 124,741/131,310 (95.0%) scanned papers have unknown effective source version;
- 1,741 of the 2,799 counted papers have only unknown-version render status;
- only 901/2,799 counted papers have at least one exact rendered quote; another 151 are fuzzy-review pending, five are known-version non-rendered, and one has a PDF error;
- there are zero human annotations and zero frozen releases.

The site sentence saying all 1,747 uncertified cases “cannot be checked until the version is pinned” is inaccurate (`pipeline/sitetext.py:163-168`). Version pinning is the blocker for 1,741; it is not the reason for five known-version nonmatches or one PDF failure. Separate these reasons in HTML and JSON.

The detached JSON now carries the warning flags, run/gate provenance, source-version strata, a coarse render partition, and unresolved counts. It still lacks a complete limitation object: measurement construct, a decomposition of `unchecked_or_unknown_version` into unknown/nonmatch/PDF-error reasons, validation-round meaning, approved use beyond `do_not_cite`, correction/contact link, release ID, licences, and axis-specific validity. A consumer can still reuse detailed rates and rankings without the human-readable caveats.

`reports/report_3yr_preliminary.md` is likewise risky when detached. It presents a “Prevalence” section and real tables without the explicit top-level **UNVALIDATED / DO NOT CITE** banner that `reports/report.md` has. The generator at `pipeline/report.py:265-277` should make release status inseparable from every report.

The public construct is also broader than the implemented instrument:

- `pipeline/classify.py:84-92` sends only `llm` and `generic` hits to the classifier;
- site copy says chatbots, coding assistants, proof assistants, CAS, ML, and other AI tools are scanned/classified;
- a Lean/CAS term co-occurring with an LLM snippet is not comprehensive proof-assistant/CAS measurement;
- narrow the present headline to explicit generative-AI/LLM/agent disclosures, or build separately retrieved and validated tool-family modules.

The category claim needs correction too. `LIKE 'math%'` includes `math-ph`; the current frame contains 30 `math.*` categories plus `math-ph`, not 31 `math.*` categories. `DECISIONS.md` properly leaves math-ph inclusion open. Resolve it before release and encode the exact category predicate and category snapshot in membership.

Finally, Wilson intervals are not the dominant uncertainty here. This is near-census screening of a captured frame, not a simple random sample. Wilson bands cover a hypothetical Bernoulli sampling component; they do not cover version uncertainty, corpus/scan missingness, classifier measurement error, prompt/model dependence, temporal dependence, or frame definition. Either declare a superpopulation estimand that makes the intervals meaningful or present descriptive ratios and measurement-error intervals after gold validation. Daily/weekly/subfield/provider/tool/agentic rankings should remain explicitly exploratory until axis-specific validation, composition adjustment, shrinkage/multiplicity, and temporal dependence are addressed.

## P1 — high-priority engineering and scientific findings

### P1-1. Artifact rows are append-only, but artifact bytes are not immutable

`pipeline/fetch.py:107-123` writes refetches to deterministic paths such as `src_v1.tar.gz` and `paper_v1.pdf`, then `INSERT OR IGNORE`s an artifact identified by paper/kind/version/SHA at `:125-137`. If a refetch ever returns different bytes, the path is overwritten while the old artifact row and old SHA remain. The row then no longer identifies its claimed bytes.

`pipeline/scan.py:319-330` can retain the earliest equal-ranked artifact row and read the overwritten path, producing a hash mismatch or—if a downstream cache is stale—worse provenance. Current read-only checks found zero paths/logical artifact keys with multiple SHAs, so this is a **latent** defect, not current corruption.

Use content-addressed blob paths, or refuse an overwrite unless the existing bytes match. Store artifact ID directly on every scan item and retain a verified immutable blob inventory in the release.

### P1-2. Unknown-format HTTP 200 responses can satisfy “successful” v1 acquisition

`pipeline/fetch.py:118-137` can store an arbitrary HTTP-200 body as an artifact with `ok_unknown_format`. `select_v1_refill()` treats every version-1 artifact as complete at `:174-178`, and terminal reconciliation treats any version-1 artifact as success at `:293-305`.

Thus an HTML error page, provider interstitial, or unrecognized body can produce a “clean” acquisition and disappear from refill eligibility; the failure surfaces only later in scanning. Only positively validated TeX/tar/PDF content should satisfy acquisition. Quarantine unknown bodies with bounded diagnostics and a retryable/nonterminal reason.

### P1-3. V1 selection is improved but not reproducible end to end

The new `v1_artifact_jobs()` at `pipeline/scan.py:294-351` makes three good changes:

- it consumes the artifacts ledger rather than the mutable `files` table;
- it records `explicit-v1` versus `inferred-single-version` basis;
- it ranks source before PDF, removing an outcome-conditioned GCS-PDF preference.

Point-in-time selection diagnostics were coherent: the full candidate set was approximately 110.6k jobs, predominantly inferred single-version sources, while the flagged subset was approximately 20.3k; only a small number required PDF. No `texv1-*` scan exists yet, so this remains unexecuted release infrastructure.

The provenance is incomplete:

- `write_v1_selection_manifest()` stores count, basis counts, and a digest, not the actual retained selection records/artifact IDs;
- the manifest is not referenced in `scan_runs.params_json` or a release;
- run params omit v1/full/flagged mode, months, prior flag run, source universe, artifact IDs, metadata cutoff, and selection hash;
- selection spans multiple live database queries rather than one frozen read snapshot;
- the sidecar is written before run-ID uniqueness is checked, so reusing an ID can overwrite a prior manifest and then abort;
- metadata-single-version inference depends on mutable OAI metadata and needs a frozen cutoff;
- per-version source licences are still not captured.

The site then loses the distinction that the report correctly keeps: `pipeline/build_site.py:202-209` groups every `version == 1` row as “v1,” while `pipeline/report.py:248-258` separates `v1_inferred`. This contradicts `DECISIONS.md:19-23`. HTML and JSON must show `v1_explicit`, `v1_inferred_single_version`, later, and unknown separately.

The older decision text at `DECISIONS.md:46-48` still says inferred blobs are “never coerced to v1,” while the newer amendment permits them in a distinct inferred stratum. Mark the older statement explicitly superseded to avoid operational ambiguity.

### P1-4. The live evidence backfill is excellent but not reproducible from the repository

The normalized evidence graph is now in strong empirical condition:

- the main run has 73,945 classification items;
- its 172,437 classifiable hits have exactly 172,437 evidence edges;
- API pilots add 22 and 17 edges;
- no inspected evidence edge crossed paper, version, or consumed scan-run boundaries;
- no classification item lacked evidence.

This is a major improvement over the orphaned legacy design.

However, the one-off 63-edge repair exists only as a statement in `LEDGER.md`. Migration v4 adds `version_basis`; it does not contain an idempotent evidence repair. Because the database is ignored, a separate copy cannot reproduce or audit the mutation from tracked code. Add a deterministic repair/audit command or migration, with precondition queries and before/after member hashes.

### P1-5. Prompt and response contracts disagree

The provider schemas require an object shaped like `{"labels": [...]}`, while the classifier prompt still asks for a bare JSON array (`pipeline/classify.py:71-76,130-137`). Strict providers may obey the schema despite the prompt, but the contradiction needlessly increases refusals/re-asks and makes raw-output diagnostics confusing.

Generate the prompt from the same response contract, and add captured-request tests for OpenAI, Anthropic, and Google. Google strips `additionalProperties`; local fail-closed validation remains essential.

### P1-6. Attempt and invocation ledgers are not yet auditable provenance

The sidecars are a useful diagnostic start, but not a release ledger:

- a recorded attempt lacks physical retry number, invocation ID, snippet/input/schema hash, request-body hash, response-body hash, reserved/actual amount, or selected classification-item link;
- `_post()` retries are invisible, and transport exhaustion can produce no attempt row;
- attempts are buffered in memory and drained after whichever batch future completes;
- process crash can lose buffered records;
- failed/re-asked raw responses can be overwritten or discarded;
- JSONL is mutable, unhashed, and not protected by database constraints;
- concurrent resumes have no durable single-run lease and can duplicate paid work.

Persist a pre-dispatch and terminal row for every physical request in SQLite (or another transactional ledger), with a unique request/invocation/item identity and hash-chain or release hash. Treat raw provider text as restricted data with retention/deletion controls.

### P1-7. Network, archive, converter, and path resource boundaries remain incomplete

The scanner has improved substantially: it no longer extracts archives to disk; it caps individual selected members and aggregate selected text; it marks unknown/incomplete/skipped outcomes; single-gzip expansion is bounded; and PDF conversion has a timeout.

Residual attack and reliability surfaces include:

- fetch, harvest, and render paths still read whole HTTP response bodies rather than streaming with compressed/decoded byte limits;
- fetch/render redirects and final origins need consistent allowlisting;
- `Retry-After` needs a bounded policy;
- harvested IDs need strict canonical validation before URL/path construction;
- `read_blob()` accepts database paths and tar member references without resolved-path containment and reads a whole outer file/member;
- tar header/member count, outer archive size, compression ratio, and wall-clock budgets are incomplete;
- open tar handles are not explicitly closed;
- annotation re-extraction diverges from scanner limits and can decompress/iterate broadly;
- `pdftotext` has no OS-level CPU/RAM/process/output sandbox;
- the legacy `arxiv_ai_ack_scan.py` and `pipeline/audit.py` retain weaker paths and should hard-fail outside an explicit forensic mode.

The scanner also intentionally scans all text-like source members, including unreferenced residue and prompt/chat-like filenames. That can find hidden/non-rendered/private material, contrary to the strongest version of taxonomy R3 and `TECH_NOTES.md`'s render/privacy intent. Build a TeX include/render graph or quarantine residual-source findings into a separately approved construct; never merge them into a rendered-evidence headline.

### P1-8. OAI recovery and deletions remain incomplete

`pipeline/harvest.py` writes raw pages into per-query subdirectories, while its offline `--reparse` path still looks only for root-level `page_*.xml.gz`. A clean reconstruction therefore misses nested archives. Deleted OAI records are skipped rather than tombstoning/superseding existing papers, so a withdrawn/deleted record can remain in the frame.

Record immutable harvest runs/pages/query hashes, recurse through the current layout, retain tombstone status, and make the metadata cutoff part of each release.

### P1-9. AWS acquisition has a strong importer but a weak producer/control plane

Strengths:

- official requester-pays bulk source and upstream MD5 checks;
- importer member/tar SHA-256 checks;
- duplicate/extra/missing detection and two-way reconciliation;
- registration refusal on reconciliation failure;
- current local S3 import report previously reconciled 168,027/168,027 with no problems.

Residual risks:

- `pipeline/aws/filter_remote.py` appends directly to long-lived monthly tars before checkpointing; crash can duplicate or truncate members;
- failed downloads can be skipped while the producer still prints `ALL DONE` and exits successfully;
- producer output lacks a durable per-chunk content-addressed commit ledger;
- `pipeline/aws/overnight_sync.sh` is now safely disabled by default, but the override path still uses broad `pkill`, size/lull checks, local rather than remote-content verification, and EC2 termination before import reconciliation;
- provisioning/IAM/security groups/IMDSv2/encryption/logging/budget alarms/backup/restore/teardown are not represented as versioned infrastructure code;
- personal SSH-path operational scripts remain.

Keep the importer. Replace the producer with closed, content-addressed per-chunk shards written to staging, close/fsync/hash/reconcile them, and atomically commit a signed acquisition manifest. Do not enable the teardown override until it verifies that manifest and importer outcome. Use least-privilege instance roles, encrypted storage, SSM or restricted ingress, budgets/alerts, and automatic audited teardown.

## Scientific rigor and analysis design

### Estimand remains incomplete despite choosing v1

The decision that first submitted version is primary is now explicit and the code has a plausible path toward it. Before the first release, specify and freeze:

- observation unit: paper v1, not mutable paper ID;
- metadata/category snapshot at which primary category is assigned;
- exact treatment of math-ph;
- treatment of withdrawn/deleted papers and missing/unavailable v1;
- source-versus-PDF channel precedence;
- explicit versus inferred-v1 policy and sensitivity analysis;
- language/script scope;
- rendered source construct versus residual/ancillary-source construct;
- inclusion/exclusion and missing-data states;
- correction lineage if metadata or source artefacts change.

Current reports and site still roll up by paper ID and current `papers` metadata. That can collapse versions and make category/date scope change after acquisition.

### Denominator and missingness must partition the frame

A release should put every cohort member into exactly one terminal, reason-coded state: acquired/scanned/classified/gated positive or negative; unavailable v1; HTTP terminal; fetch retryable failure; unknown format; omitted from scan selection; scan incomplete/error/skipped; classification pending/error/invalid; evidence ungrounded; render exact/fuzzy/nonmatch/error/unknown-version; human non-evaluable.

Monthly tables should show those states, not just positive/denominator ratios. Missingness varies over time and by source/version channel. Coverage extrema can be reported for the **raw classifier-positive ratio**, but true prevalence remains unidentified until measurement error is estimated. Wilson intervals cannot substitute for that analysis.

### Model choice is a measurement choice

The small API pilots are useful engineering smoke tests, not an accuracy or cost comparison:

- they cover tiny deterministic early-ID slices;
- both runs are partial and carry dirty initial commit labels;
- they have only one positive each;
- no release-bound human reference exists;
- surviving usage files cover only the latest resumes;
- the two models and the old Codex run already disagree on some polarities.

Use the same preregistered, stratified hard-case/positive/flag/negative/version/time/language sample across each provider and independent human adjudication. Estimate polarity and axis-specific performance with uncertainty before choosing a full-run backend. Record the selection rule and avoid optimizing the prompt/model on the untouched final validation sample.

### Taxonomy and observable channel need alignment

The taxonomy's distinctions—author use, result-bearing/supportive/cosmetic, catalytic flag, computation verification, location, tool/model strings—are scientifically valuable. Several require separate validation:

- whether AI-generated formalization followed by kernel verification is result-bearing or supportive;
- ancillary artifact/comment disclosures that cannot be expected in the compiled PDF;
- proof assistants/CAS versus generative AI;
- body/residual source versus rendered text;
- provider/model/tool extraction from arbitrary strings;
- multi-label locations and impacts.

Report each channel's observability and gold validity separately. Do not infer proof-assistant/CAS prevalence from an LLM-triggered retrieval pipeline.

### Prior art is improved, but not a systematic evidence review

The numerical corrections made before review 5 remain strong: current versions/estimands are more accurately described for Patterns and Purposes, the survey's self-selection is disclosed, Andrew Gray is correctly identified, Pangram's scientific-paper FPR is no longer mislabeled as arXiv, ArxivMathGradingBench's papers/errors are distinguished, the 20%-trend source is marked secondary, and the 27% quantity is described as bytes rather than submissions.

This iteration did not re-run a full bibliography verification. `PRIOR_ART.md` appropriately calls itself a scoping rather than systematic search, but it still mixes preprints, product/vendor reports, blogs, LinkedIn announcements, and secondary trend claims. Add a claim ledger with exact version/DOI/archive URL, access date, source class, checked claim, reviewer, and verification status. Do not describe NBER/RAID/bioRxiv or the full bibliography as independently verified until they are.

## Ethics, privacy, licensing, and governance

### External API data governance is not yet documented

The direct API is a major security improvement over giving an agentic CLI repository and corpus read access. It also creates a clear external-processing relationship: identified arXiv IDs and source snippets are sent to providers.

OpenAI's current official data-controls documentation says API inputs/outputs are not used for model training by default, while abuse-monitoring logs may be retained for up to 30 days unless an approved organization uses more restrictive controls. This does not replace a project decision. Before a full run, document:

- controller/processor roles and lawful/ethical basis;
- provider DPA, subprocessors, region/transfers, retention, deletion, incident, and zero-data-retention eligibility/configuration;
- whether request storage is disabled where supported;
- why identifiers are necessary and whether they can be pseudonymized;
- treatment of hidden/unrendered source material;
- credential scope/rotation and provider-side budgets;
- raw request/response access, encryption, retention, deletion, and breach procedures.

Official references checked for this review:

- OpenAI Structured Outputs: <https://developers.openai.com/api/docs/guides/structured-outputs>
- OpenAI Luna model and current pricing: <https://developers.openai.com/api/docs/models/gpt-5.6-luna>
- OpenAI API data controls: <https://developers.openai.com/api/docs/guides/your-data>
- Anthropic strict tool use: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use>

### Data minimization and local access remain unresolved

The metadata database retains submitter information for nearly every paper, while downstream analysis does not use it. Either justify it in a data inventory or stop collecting it and migrate/delete historical values. Gold packets contain identified PDFs and large source contexts. The database, `.env`, logs, contexts, packets, and manifests appeared mode `0777` in this DrvFS environment; Unix mode bits may not reflect Windows ACL exposure, so verify actual host/cloud ACLs, encryption, backups, access logging, and reviewer-specific least privilege.

Gold reviewers need confidentiality, training, COI/reassignment, compensation, access/deletion, and incident protocols. Do not colocate all reviewer assignments/plants with all PDFs/contexts in generally accessible storage.

### Licensing and public governance remain launch blockers

The repository still lacks a tracked:

- `LICENSE` and code/data/document licence separation;
- `NOTICE` and third-party attribution;
- `PRIVACY.md` / retention and vendor-processing policy;
- `SECURITY.md` and responsible disclosure process;
- governance/conflict/adjudication policy;
- correction, appeal, objection, and takedown process;
- `CITATION.cff` and release citation/version policy;
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, changelog, and maintainership/ownership controls.

`DESIGN_PLATFORM.md` still asserts that IDs plus derived labels are legally publishable; `PITCH.md` still contemplates open annotations; both conflict with the owner-approved aggregate-only rule. ArXiv items can have different licences by item/version, and the artifact schema does not bind the applicable licence to each version. Obtain institutional legal/ethics/data-protection review before any paper-level public output, and record the determination rather than treating it as self-evident.

The `.gitignore` statement that “arXiv license forbids redistribution” is also overbroad: rights vary by paper/version. Replace it with a precise project policy and retain artifact-level rights metadata.

## Public site, reach, and deployment

### Strong foundation

The static, no-tracker, no-third-party-runtime architecture is excellent for privacy, resilience, cost, and public trust. The page is visually compact, the new warning is prominent, dynamic disclosure labels are escaped, JSON-in-script is made script-safe, small subgroups are masked, non-affiliation is explicit, and the current exploratory page is noindexed. Keep these choices.

### Site is still not release-derived or reproducible

`pipeline/templates/dashboard.html` contains a hard-coded submissions series and harvest date. `pipeline/build_site.py` substitutes selected text and appends disclosure material rather than rebuilding every datum from one release. The site can therefore mix submission metadata from one snapshot with disclosure metrics from another.

The builder:

- accepts run IDs instead of `release_id`;
- queries live tables rather than materialized release membership;
- hard-codes `unreleased_exploratory` rather than deriving state;
- uses build time/current state in output;
- lacks a deterministic canonical JSON/HTML/ZIP packaging contract;
- has no protected deploy job, host configuration, security headers, rollback, or post-deploy verification.

Build exactly one allowlisted `dist/` from a frozen release and signed manifest. Normalize ordering, timestamps, file modes, and JSON; generate every date/count/series from the same snapshot; include checksums, SBOM, code/data licence, methods, citation, limitations, correction lineage, and release ID; test a second build byte-for-byte; deploy only that artifact through a protected environment with rollback. There is currently no `dist/` release.

### Accessibility remains pre-release quality

Residual issues include:

- SVG charts have `role=img` but lack a complete accessible name/description;
- hover interactions are mouse-oriented, with incomplete keyboard/touch equivalence;
- generated tables need `<thead>` and scoped headers;
- `minmax(420px, 1fr)` can overflow narrow phones;
- muted text contrast was measured below 4.5:1 on light backgrounds;
- some template code still uses `innerHTML` even though current values are controlled;
- no skip link, comprehensive landmarks, reduced-motion/high-contrast checks, or tested focus behavior.

Add HTML validation, axe/accessibility tests, keyboard/touch tests, mobile layouts, contrast checks, accessible chart table equivalents, CSP/security headers, link checking, and manual screen-reader testing.

### Reach work should follow credibility gates

After a validated release exists, add a stable canonical URL; methods, downloadable aggregate schema, release/correction/citation pages; Open Graph/social image; sitemap/robots; media guide; clear plain-language uncertainty; and an explicit non-affiliation/contact footer. Avoid optimizing reach around an uncalibrated headline. A correction feed and versioned release are more valuable than a mutable viral percentage.

Future community share-link and OpenAlex author/career profiling features remain separate high-risk projects. A generic server-side URL fetcher would add copyright, prompt/account data, SSRF/malware, consent, moderation, retention, and provider-terms risk. Prefer structured reviewer attestations, and require a separate ethics/privacy/measurement protocol before author/affiliation profiling.

## CI, tests, packaging, and repository hygiene

The 94-test suite is fast and valuable. GitHub Actions are pinned to full commit SHAs, Python 3.12 is explicit, and runtime dependency versions are pinned. The current code compiled, shell scripts parsed, `pip check` passed in the implementation audit, and the database passed integrity/foreign-key checks in a coherent read-only snapshot.

Coverage gaps align closely with the newly found failures. Add tests for:

- every refill mode/argument combination and unknown/empty/incorrect flag run;
- retained target-member and terminal reconciliation manifests;
- unknown-format HTTP 200 not satisfying acquisition;
- content-addressed artifact overwrite behavior;
- physical retry reservation/accounting and exhausted transport logging;
- concurrent token/USD reservations and cross-process resume state;
- single-run lease and duplicate paid work;
- resume under changed commit/schema/endpoint/config;
- Anthropic `strict: true` and captured provider request bodies;
- all required fields, duplicate keys, bool/nonfinite/oversize values;
- TeX `n/r/t` JSON escapes and exact evidence spans;
- PDF-cache input-hash binding;
- flagged-only scan refusal as a prevalence release;
- site/report parity for `v1_inferred` and all unresolved states;
- release-only site build and deterministic double build;
- malicious archive/path/Markdown/HTML/CSV inputs;
- accessibility, links, CSP, and migration/reconstruction fixtures.

`.github/workflows/ci.yml:1-2` says “tests + site build,” but runs only pytest. It also lacks explicit least-privilege permissions, checkout credential disabling, timeout/concurrency, supported-Python matrix, lint/type/security/licence/SBOM scans, migration/E2E fixture, reproducibility check, and deploy separation. `requirements.lock` pins versions but has no hashes. System dependencies (`pdftotext`, Codex, AWS CLI) are not version-locked in a reproducible environment.

Other hygiene items:

- README still points to `review_codex4.md` as the current independent audit;
- `WORKFLOW.md` documents an unsafe refill, omits the USD cap, and later still describes Codex/bulk batching as preferred despite the API decision;
- `LEDGER.md` overstates “real budgets,” native schemas, and persisted-per-run accounting;
- 14 unrelated Lean-specific files remain tracked under `.claude/`; remove, relocate, or document their provenance/licence/security boundary;
- root-local ignored email files, credentials, DB/WAL, corpus, and packets reinforce the need for a clean publication checkout rather than publishing this working directory;
- the legacy executable and reports should be clearly marked forensic-only or removed from operational entry points.

## Status against review 5

### Fixed or materially improved

- The live refill was restarted with a finite, correctly reconstructed 2,122-target flagged manifest.
- Regex JSON repair was removed.
- OpenAI strict structured output is correctly configured.
- Direct API is non-agentic, one-paper, tools-free, fixed-origin, no-redirect, and ambient-network-state-free.
- A locked pre-dispatch USD reservation and within-process stop latch exist.
- Unpinned-label, unknown/dirty producer label, non-API backend, non-isolation, empty consumed-run, and incomplete-classification freeze checks improved.
- Resume compares backend and treats invalid rows as retryable.
- Source-first v1 selection and `version_basis` reporting exist.
- Fuzzy rendered matches are demoted to review queue.
- Main evidence lineage is empirically complete at 172,437/172,437.
- Site warning/noindex/machine status/conditional coverage/render caveats improved.
- Calibration HTML and manifest state that the current round cannot validate a release.
- Unsafe AWS overnight teardown is disabled by default.
- Requests floor was updated; 94 tests pass.

### Partial

- Refill safety: live invocation safe; generic CLI and runbook unsafe.
- Budgets: within-process logical reservation; not cumulative, retry-hard, token-concurrent, or fully audited.
- Native schema: OpenAI strict; Anthropic non-strict and local validator permissive.
- TeX repair: old corruption removed; legal `n/r/t` JSON escape corruption remains.
- Resume/freeze: selected labels/backend checks improved; full code/protocol/invocation identity missing.
- V1: artifact scanner and report strata exist; no run, immutable selection, release binding, site parity, or licence chain.
- Gold: candid calibration framing and safer HTML; no release-bound sample/ingest/adjudication/estimators.
- Public limitations: much stronger but incomplete/misgrouped and separable from detailed JSON/results.
- Release: summary row exists; no materialized immutable consumer or release-built site.

### Unresolved or newly identified

- No scientific release, final human gold, or validated estimate.
- Artifact paths can overwrite bytes under old rows.
- Unknown-format artifacts can satisfy refill success.
- PDF text cache can be falsely bound to a different PDF hash.
- Physical API retries and cross-process spend are not bounded/audited.
- Selected/partial scans and optional evidence gates can freeze.
- Site merges inferred v1 with explicit v1.
- Paper-level tracked artifacts conflict with aggregate-only policy.
- Archive/network/converter resource boundaries remain incomplete.
- OAI reparse/tombstones, AWS producer/IaC, CI/deploy chain, accessibility, licences, privacy, correction, and governance remain open.

## Point-in-time data snapshot

At `2026-08-11T16:11:59Z`, one read-only transaction observed:

| Object | Count / status |
|---|---:|
| papers | 235,342 |
| versions | 418,232 |
| files | 169,166 |
| artifacts | 183,360 and increasing |
| scan runs / items / hits | 3 / 169,423 / 547,763 |
| classification runs / items / evidence edges | 3 / 73,972 / 172,476 |
| render checks | 8,078 |
| annotations | 0 |
| releases | 0 |

The principal runs were:

- `tex-20260810T205113`: `partial`, 169,165 declared items, 820 counted errors, `f08502f-dirty`;
- `cls-20260810T211610`: `complete`, 73,945 items, backend `codex`, `gpt-5.6-sol@medium`, `isolate=0`, `f08502f-dirty`;
- `cls-20260811T143729`: partial Anthropic API pilot, 16 items, initial code `d1d2c47-dirty`;
- `cls-20260811T143858`: partial OpenAI API pilot, 11 items, initial code `d1d2c47-dirty`.

The database was in WAL mode and the active refill changed artifact and ledger counts throughout the review. These values are a diagnostic snapshot, not a database hash or release. The implementation audit obtained `PRAGMA quick_check=ok` and no foreign-key violations in a coherent read-only snapshot.

Tracked generated artifact hashes at this commit:

- `site/index.html`: `e1bf7a0faa42a8db059715daf8bc1b8035139bc84fc57aa7e3b79c1d5a07f8dd`
- `site/data/disclosures.json`: `931a54dd6db87d113f69cde1ce7fec8b82c015cc32039d148124e681d1c3a7c0`
- `reports/report.md`: `996f2e4755c0a7963130a3a13bc7e9f6df4fe497039a8b5eb886a62590e079e1`
- `review_codex5.md`: `92c901a3c9335394b4b891cb740b34e1238ce2f756262083d173d0dff28dd0b2`

## Recommended sequence

### Before any new refill invocation

1. Close every refill-mode truth-table bypass and fix `WORKFLOW.md`.
2. Retain the exact current target list and final per-target outcomes under a run ID; do not rely on a digest plus mutable reconstruction.
3. Treat unknown formats as failures and make blobs content-addressed.
4. Let the currently bounded job finish/reconcile if the owner still intends it; do not infer from this review that it has entered the tail.

### Before any further paid pilot/resume

1. Make budget/usage/attempt state transactional and cumulative across processes.
2. Reserve every physical retry and all in-flight tokens; enforce a run lease.
3. Add Anthropic `strict: true`; make local validation genuinely fail-closed.
4. Reject all source-string controls or use exact immutable evidence spans.
5. Canonicalize and hash the entire classification protocol; resume only an exact match.
6. Reconcile the pilot ledger with provider consoles and retain the price/source snapshot.

### Before a v1 analysis run

1. Resolve math-ph and freeze the metadata/category cutoff.
2. Persist exact artifact-member selection in one DB snapshot, including basis and licences.
3. Make PDF-derived text hash-bound.
4. Run full-frame—not prior-positive/flagged-only—v1 scanning with terminal reason-coded coverage.
5. Run one clean, pinned, approved API classification protocol with durable attempts and exact evidence.
6. Exact-render/adjudicate the release construct; keep residual/ancillary channels separate.

### Before a scientific release

1. Materialize one immutable release membership with all artifact/item/evidence/render/gate/missingness/protocol hashes.
2. Require grounded and exact-rendered evidence or record a deliberate, named alternate construct.
3. Draw a fresh final gold sample from that exact release, with shared overlap, exact versions/artifacts, fail-closed ingest, adjudication, COI, and powered estimators.
4. Estimate precision, sensitivity/miss rates, corrected prevalence, version and missingness uncertainty; validate every displayed axis.
5. Build site/report/data solely from `release_id`; test deterministic reconstruction.
6. Complete institutional privacy/ethics/legal/vendor/licensing review and the governance/correction package.
7. Publish only an allowlisted aggregate artifact from a clean repository/history boundary.

## Verification performed

- Reviewed commit `e2293d6` and the complete tracked repository.
- Ran the fixture suite with cache/bytecode disabled: **94 passed**.
- Compiled project Python and syntax-checked operational shell scripts.
- Ran Git whitespace/status checks; the worktree was clean before this file.
- Inspected SQLite read-only; the implementation audit verified quick-check and foreign-key integrity.
- Reconciled classification/evidence counts and current run metadata.
- Reconstructed the live 2,122-target refill set/hash and checked observed attempts against it without mutating the job.
- Exercised refill argument/selection combinations without network access.
- Used mocked/no-network transports to test retry accounting and concurrent budget behavior.
- Tested validator/control-character edge cases with synthetic strings.
- Checked tracked site/report hashes and generated-data provenance.
- Checked current official OpenAI/Anthropic response-schema, model-pricing, and data-control documentation.

I did **not** perform penetration testing, a formal legal/ethics determination, full secret-history scanning, provider invoice access, arXiv coordination, cloud inspection, a full bibliography re-verification, model calls, or a stable physical database hash. The active WAL means empirical counts must be treated as time-bounded observations.

## Bottom line

`e2293d6` closes several concrete sub-bugs and makes the exploratory artifact more honest. It does not yet close the four blocker **contracts** under restart, retry, adversarial argument combinations, provider variance, or release reconstruction. The most important near-term fixes are small and testable: make refill modes exhaustive, make spend/attempts cumulative and physical-request scoped, enable strict Anthropic plus strict local validation, and make resume/freeze depend on one canonical protocol.

The larger scientific bar remains unchanged: one full-frame v1-defined immutable release, exact evidence/render lineage, release-bound human validation, explicit missingness/measurement uncertainty, and a governed aggregate publication. Until that exists, the current `2.1%` should remain labeled exactly as it is in the machine status: **unreleased exploratory, do not cite**.
