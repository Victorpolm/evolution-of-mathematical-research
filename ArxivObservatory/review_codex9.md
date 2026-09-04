# ArxivObservatory repository review — iteration 9

**Audit snapshot:** Git commit `0caa5260bc2db17c4098da34c37d79c33f2ea236`, tree `c186feda77c064ff90bc0dcfe1e9d85eeea57dad`, committed 2026-08-12 16:44 CEST. The worktree was clean before this review file was created.

**Primary delta reviewed:** everything after the iteration-8 snapshot `7ee7386`, especially owner confirmations in `d5305d9`, the review-8 triage in `0caa526`, taxonomy v2.3 and its R4 boundary tests, the 150-case Luna adherence exercise, prompt/schema parity, human-label controls, campaign-scoped spending, run leases, adaptive request provenance, final-gold tooling, freeze/release behavior, disclosure controls, and publication preparation.

**Audit boundary:** read-only except for creating this file. I did not invoke a model or provider API, contact arXiv, start or stop a pipeline job, alter the database/corpus/annotation records, operate cloud resources, or publish anything. Restricted calibration files are described only in aggregate. I checked current official OpenAI documentation where OpenAI-specific behavior materially affects the planned run; this was not a new systematic verification of the scientific bibliography.

## Executive verdict

This revision fixes a substantial portion of iteration 8. The v2.3 instrument has a coherent object-shaped prompt and strict provider schema, all flags are required, the R4 examples are deidentified, human reviewers can express `method_component`, spend admission is now atomic and campaign-scoped, lease acquisition is transactional and holder-specific, successful adaptive splits retain their ordered snippet hashes, and the exact taxonomy/prompt/schema hashes in `DECISIONS.md` match the repository. The full v2.3 run has not begun, which is fortunate: the remaining faults can still be corrected without invalidating expensive confirmatory labels.

The project is nevertheless **not ready to launch the full paid v2.3 classification run yet**. Four issues are immediate blockers:

1. `DECISIONS.md` explicitly says owner sign-off of the exact v2.3 text is still pending. The 150-case adherence exercise is useful development evidence, but it does not substitute for that sign-off: only 53/149 comparable papers had model-evaluable snippets, all human labels are v2.0, and the two remaining disagreements show impact instability on repeat calls.
2. A budget approval is still partly self-authorizing. `attach_ledger()` creates an unknown campaign ID from command-line values; campaign ID/cap/tariff are absent from the classification protocol hash, so a resumed run can switch to a fresh campaign and exceed the intended authorization.
3. The lease is not a spend/write fence. All futures are submitted at once, and workers do not verify the holder inside the reservation or result transaction; queued/running paid work can continue after takeover.
4. Request provenance is incomplete exactly on failures and retries. Failed split nodes lose prompt hashes, a parse re-ask collapses two prompts into one record, physical attempt rows are persisted only after a future returns, and the actual adherence exercise produced 56 spend rows but zero `api_attempts`.

The project is also **not ready for the final two-grader gold study**. The production annotation path is still hard-coded as calibration-only, is not release/artifact/hash bound, reuses mutable contexts, fails open without a manifest, does not assign a deliberate shared double-coded subset, and has no implemented adjudication/weighted-estimation chain.

Finally, neither the public site nor the Git repository is release-ready. Freeze is a digest over mutable live tables rather than an immutable materialized release; the site consumes raw run IDs; disclosure suppression leaves hundreds of singleton/doubleton time cells; tracked prose still contains real-paper examples; deleted expressive artifacts remain in Git history; and the privacy/governance/deployment package remains incomplete.

### Readiness call

| Activity | Readiness at this snapshot |
|---|---|
| Owner review of the exact v2.3 wording and a small synthetic comprehension check | **Ready now** |
| Full paid Luna v2.3 rerun | **No-go until Gates A and B below pass** |
| Final two-grader gold study | **No-go until Gate C is implemented and dry-run end to end** |
| Private inspection of explicitly exploratory aggregates | **Ready with current warnings and access controls** |
| Frozen scientific release / public prevalence claim | **No-go until Gate D** |
| Public Git repository or public site | **No-go until Gate E** |
| Three-year population prevalence from the current v1 data | **Not identified: 47,554 frame outcomes remain unresolved** |

The shortest safe sequence is: close A/B, perform the full v2.3 rerun, construct one immutable candidate release, draw and adjudicate a fresh release-bound gold sample, then build publication artifacts only from that validated release.

## Snapshot and verification

### Automated checks

- `python3 -m pytest -q -p no:cacheprovider`: **122 passed in 2.93 s**.
- Python AST parsing succeeded for all 35 tracked pipeline/test Python files.
- `python3 -m pip check` reported no broken requirements.
- `bash -n` passed for all tracked shell scripts.
- The worktree was clean before this report was added.
- `git diff --check 7ee7386..HEAD` found only an extra blank line at the end of the newly added `review_codex8.md`; no production-code whitespace error was reported.

The larger test suite is a real improvement. It now exercises prompt/schema parity, successful split mapping, campaign admission, and holder-specific lease mechanics. It still lacks the negative/race/crash tests identified below.

### Current empirical state

The local database appeared quiescent during inspection and had SHA-256 `67fd477986c5e03ba035612b55f54214005add93c2e3e0e3556ae3a2d8cd2e34`. This is only a hash of this local 2.9 GB file, not a clone-reconstructible release.

- Schema version: **7**.
- Papers / versions: **235,342 / 418,232**.
- Files / artifacts: **169,166 / 187,918**.
- Scan runs / items / hits: **4 / 281,870 / 982,232**.
- Classification runs / items / evidence edges: **6 / 145,172 / 338,896**.
- Render checks: **14,758**.
- Human annotations: **150**, all from the calibration round and codebook v2.0.
- Releases: **0**.
- Active run leases: **0**.
- Taxonomy-v2.3 classification runs: **0**.

The latest v1 scan `texv1-20260811T215148` remains `partial`: 112,447 selected papers, 110,770 `ok`, 54 unknown-format, 2 incomplete, and 1,621 skipped PDF-in-tar items. The existing Luna run `cls-20260811T220922` is taxonomy v2.0 and remains `partial`: 71,194 items, 71,022 `ok`, and 172 non-ok items.

The new campaign `JS-2026-08-12-v22-rerun-50USD` is active. The adherence exercise created 56 settled spend rows totaling **$0.073593** (54 main calls plus 2 detail calls). It created no corresponding `classification_runs` rows and the entire database currently contains **zero `api_attempts` rows**. This matters because the exercise is being used to support exact-text sign-off while bypassing the provenance path it purports to exercise.

For the primary 2023-08-01 through 2026-08-08 math-primary frame, the preliminary v1 report still has **85,742 scan-complete papers out of 133,279**, leaving **47,554 unresolved** after the selected acquisition/classification/evidence states. The displayed approximately 2.0%–37.7% extrema are conditional raw-model-label coverage extremes, not bounds on true disclosure prevalence.

## What is genuinely stronger since iteration 8

The following changes are substantive and should be preserved:

- taxonomy version discipline was respected: semantic text changes produced v2.3 before any v2.2/v2.3 production labels;
- the committed taxonomy, manual, prompt, and provider-schema hashes exactly match the bundle recorded in `DECISIONS.md:15-20`;
- the primary prompt and re-ask now require the same `{"labels": [...]}` object, use `not_applicable`, and generate all required flag keys;
- strict provider schemas and local required-field checks are materially closer to parity;
- R4 now supplies explicit new/pre-existing, target, and delegation tests, and tracked illustration cases are deidentified;
- the human UI has an explicit yes/no/unsure `method_component` control outside the author-use-only panel;
- calibration analysis correctly treats `UNCLEAR` and `INSUFFICIENT_EVIDENCE` as non-evaluable;
- paper-level reporting now ORs flags rather than taking an arbitrary snippet's value;
- `budget_campaigns` and campaign-linked spend rows exist; durable reservation admission uses `BEGIN IMMEDIATE` and correctly excludes earlier pilot spend;
- run-lease acquire, heartbeat, and delete are transactionally improved and holder-specific;
- successful adaptive split children carry deterministic split paths and ordered snippet hashes;
- provider-returned model/fingerprint fields exist prospectively;
- arXiv IDs are omitted from provider prompts, OpenAI requests use `store:false`, redirects are disabled, and ambient proxy/`.netrc` trust is disabled;
- current-tree `results/*`, awesome-validation files, the old spotcheck, instance inventory, and unrelated Lean tooling have been quarantined;
- the site remains tracker-free, `noindex`, visibly unreleased, machine-readable as `do_not_cite`, and explicit about non-affiliation;
- action SHAs are pinned in CI, and there is still no automatic deployment path that could accidentally publish an invalid result.

These gains reduce risk, but several are only prospective. No production v2.3 run or release has exercised the revised path.

## Gate A — freeze and validate one scientific instrument

### A1. Exact v2.3 owner sign-off is still explicitly pending

`DECISIONS.md:8-20` records the correct hash bundle but says in capitals that owner sign-off of the exact committed text is pending. That is the authoritative state. `TAXONOMY.md` and parts of `LEDGER.md` describe the instrument as operative/fixed, so the repository currently has two status signals.

Do not infer approval from a code commit or adherence score. Record the owner's approval of the exact four hashes, primary numerator, R4 scope, R5 attempted-use treatment, and OpenAI inference configuration in one dated decision. Any later semantic edit must bump the taxonomy and invalidate the planned run before it starts.

### A2. The 150-case adherence headline overstates the evidence

The useful result is narrower than “147/149 agreement”:

- all 150 human verdicts were made under codebook v2.0, not v2.3;
- one packet-version-skew item is correctly non-comparable, leaving 149;
- only **53/149** comparable papers had snippets sent to v2.3 Luna;
- Luna and the human binary verdict agree on **51/53** of those model-evaluable papers;
- the other **96/96** are structural no-snippet negatives that cannot test the new prompt, schema, R4, or R5;
- therefore 147/149 is a combined pipeline-adherence number, not model agreement on 149 newly classified cases and certainly not an accuracy estimate.

The two detailed re-asks of the residual disagreements changed impact relative to the main adherence call (`undetermined` to `result_bearing` in one case and `supportive` to `cosmetic` in another). One change crosses the contributing/unknown reporting boundary. The Markdown and JSON summaries do not fully expose this repeat-call instability.

Report the adherence exercise as development-only with separate denominators: **51/53 model-evaluable binary agreement** and **96/96 structural no-snippet concordance**. Add a repeatability table for polarity, impact, categories, and flags. Do not use this in-sample exercise as a pass/fail validity estimate.

Before full launch, both human graders should independently label a small, frozen, deidentified v2.3 comprehension set that deliberately targets R4/R5 boundaries. Compare them with Luna, discuss disagreements, revise the manual if necessary, then obtain exact-text owner sign-off. This is an instrument check, not the final gold sample.

### A3. The adherence exercise is not reproducible through the claimed pipeline

The restricted artifacts contain 54 logical main-call records and two detail-call spend rows, but there is no tracked deterministic adherence command, no matching classification run, and no `api_attempts` record. Nevertheless the adherence note says campaign/lease/provenance mechanics ran live.

That statement should be corrected. Either rerun the exercise through a first-class, tracked command that creates a proper run, invocation, request, attempt, and spend chain, or explicitly register it as an exceptional development experiment with input/output hashes and limitations. It should not be the evidence that the production provenance path works.

### A4. Human/machine validation still differs on a legal input

`pipeline/classify.py:320-342` invokes shared cross-field invariants only for `author_use`. For a model response such as `topic_only + catalytic`, it records a warning, clears the catalytic flag, and returns a non-null clean label. `store_results()` then stores status `ok` (`pipeline/classify.py:501-510`). Human ingest rejects the same combination via `taxonomy.cross_field_problems(False, ...)` (`pipeline/annotate.py:671-679`).

This is both parity and fail-closedness failure: a semantic schema violation is silently repaired on the machine path. Apply shared invariants to every polarity before coercion, return invalid on contradiction, and re-ask. Add an exhaustive parity matrix over every polarity × impact × flag combination, including non-author-use catalytic labels.

### A5. R4's three boundary tests still need precedence and tie handling

The new R4 questions are helpful, but `TAXONOMY.md:75-88` says to “answer all three” without defining what happens when they point in different directions. A pretrained/frozen model newly executed to study a non-AI target can be:

- a pre-existing fixed component (topic-only side),
- used against a non-AI target (author-use side), and
- not plausibly a delegated research task (topic-only side).

The current text could classify ordinary use of a frozen encoder either way. Define precedence or a small decision table. At minimum cover: frozen encoders, newly generated embeddings, LLM judges/labels, synthetic data, inference-only components, generated pipeline code, dual object-and-assistant roles, redundant but correct suggestions, explicitly fruitless attempts, and vague disclosures. Use `unclear` where the text genuinely cannot establish the relation.

### A6. Pin inference behavior as part of the measurement instrument

`pipeline/classify.py:759-765` records OpenAI reasoning effort and temperature as “provider-default”; the request sets neither. Current official Luna documentation says reasoning effort supports several values and defaults to medium, but a rolling default is not an immutable scientific setting. Set the intended supported value explicitly, record it in the request/protocol, and include it in the comprehension/adherence exercise. Persist the returned model and provider fingerprint on every attempt.

The current base tariff in code ($0.20/M input, $1.20/M output) matches the direct [official Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna) observed during this audit. Because model aliases, defaults, and tariffs are mutable, archive/hash the authoritative campaign-time page or account tariff and reconcile actual billing rather than relying on a source-code constant alone.

### A7. The measurement scope remains narrower than the prose

Classification input is limited to `llm`/`generic` retrieval tiers (`pipeline/classify.py:96-100`). Standalone ML, proof-assistant, and CAS hits are not comprehensively classified. The primary construct should therefore be named as explicit disclosed generative-AI/LLM use found by this retrieval protocol. Treat prover/CAS/general-ML modules as future, separately validated instruments.

For v2.3, public/reporting numerators must also distinguish:

- disclosed attempted-or-contributing author use;
- contributing use (`cosmetic`, `supportive`, `result_bearing`);
- explicit `zero_contribution`;
- `undetermined` impact.

Calling all four simply “AI assistance” obscures R5 and can imply a contribution the authors denied.

### Gate A acceptance criteria

- dated owner approval of the exact v2.3 hash bundle and inference controls;
- a frozen R4 precedence/decision table and deidentified boundary exercise;
- two-human-plus-Luna comprehension results, clearly development-only;
- human/machine parity test for every polarity/impact/flag combination;
- semantic contradictions rejected and re-asked, never silently cleaned;
- tracked, reproducible adherence command with full run/request/attempt/spend lineage;
- explicit primary and secondary numerators and honest tool-family scope.

## Gate B — make paid execution authorization, fencing, and provenance enforceable

### B1. An unknown approval ID currently creates its own authority

Campaign accounting is much stronger, but authorization is not. `pipeline/llm_api.py:131-143` inserts a missing `budget_campaigns` row using caller-supplied approval ID, provider, model, cap, and purpose. A typo—or an arbitrary new string—therefore grants a fresh active cap rather than failing.

Campaign identity is also absent from the canonical protocol object at `pipeline/classify.py:741-770`. Resume checks only that protocol hash (`:772-789`), then attaches whatever approval ID and cap appear on the new command line (`:801-812`). The same scientific run could consume multiple independently auto-created $50 campaigns.

Require campaigns to be created in a separate owner-authorized step. Classification must fail if the ID is unknown. Bind approval ID, provider, requested model/config, cap, tariff hash/date, purpose/scope, owner authorization record, expiry, and campaign status into the run protocol and resume identity. A run must never switch campaign.

The current campaign row's purpose is “150-case v2.3 adherence check (in-sample dev),” while `DECISIONS.md:21-26` extends the same ID to the full confirmatory rerun. Split the campaigns or append an explicit signed scope amendment before launch; do not let runtime code silently ignore a changed purpose.

### B2. The dollar cap can still overshoot its nominal hard boundary

Atomic durable admission correctly counts campaign reservations across processes. However `_est_tokens()` is `len(prompt)//3 + 1500` (`pipeline/llm_api.py:406-417`), not a proven upper bound for arbitrary TeX/Unicode tokenization. Settlement can replace the reservation with a larger actual cost and only latch after spend exceeds the cap (`:477-505`).

Use an exact tokenizer/provider count where available, or a demonstrably conservative byte/codepoint upper bound plus maximum output. Make the authorized contract explicit about any unavoidable final-request overshoot. Include cache-write/read and long-context pricing rules in the tariff snapshot even if the present prompts are below the long-context threshold. Reconcile provider-console spend at campaign close.

### B3. The holder-specific lease does not fence the work it protects

Lease acquire/heartbeat/delete are now holder-specific and transactional—a real fix. But all futures are submitted immediately (`pipeline/classify.py:863-865`). Workers and recursive split calls never check the holder before `_reserve()`/HTTP, and `store_results()` has no holder predicate (`:942-943`). The main thread notices `lease.lost` only when a future completes (`:868-876`); cancellation cannot stop running futures, and the executor waits for them.

There is a second failure mode: repeated keeper database errors are ignored (`:624-633`), so a process can lose its lease after the stale horizon without setting `lost`.

Put `run_id + holder/fencing generation` into the same durable transactions as campaign reservation, attempt creation, and result storage. Each worker must check a stop/fence callback before every physical dispatch and split. Submit only a bounded number of futures. Treat heartbeat uncertainty beyond a short grace period as lost. Wrap the entire acquired-lease lifetime in `try/finally` so exceptions cannot leave it until timeout.

### B4. Failed split and re-ask provenance is still ambiguous

Successful split children now map correctly, but the failure path does not:

- when `_classify_once()` raises, `classify_batch()` records the failed parent/child with `prompt=None, raw=None`, losing the exact prompt hash (`pipeline/classify.py:447-458`);
- `_attempt()` may make two distinct calls after a parse/control-character failure (`:358-367`) but returns only the second raw response;
- `_classify_once()` then emits one logical request record for those two calls (`:461-467`), so both physical attempts inherit the first prompt hash and the first response is lost;
- failed schema retries preserve their retry prompt but not a response hash (`:470-484`).

Create one logical-request row per distinct prompt, including parse re-asks and schema retries. Construct/persist the prompt record before calling the provider; update it with response/error afterward. Failed split nodes must retain their prompt hash, ordered snippet hashes, split path, and attempt links.

### B5. Physical attempt provenance is delayed and incomplete

Spend reservations are durable before dispatch, but `api_attempts` rows are buffered in thread-local memory and inserted only after the full future returns (`pipeline/classify.py:892-941`). A crash, lease loss, malformed response, or process kill can leave a charge/reservation with no request provenance. That is exactly what the adherence exercise currently demonstrates: 56 settled spend rows, zero attempt rows.

Retryable 429/5xx/transport errors are also recorded as endpoint `transport-failure` with null HTTP status and near-zero duration because `_Retryable` discards the response metadata and `call_api()` starts a fresh timer at catch time (`pipeline/llm_api.py:510-528,688-697`). Successful HTTP responses that fail parsing/refusal/shape handling may settle conservatively while losing known usage or an attempt record.

Before HTTP, insert a durable attempt linked to campaign, reservation, run, invocation, logical request, fence token, requested model/config, endpoint, and attempt number. After HTTP, update the same row with both HTTP request ID and completion/message ID, status, returned model/fingerprint, finish reason, usage, response hash, duration, and normalized error class. Do not persist provider body excerpts in general logs.

### B6. The documented reconciliation invariant is wrong

`WORKFLOW.md:70-78` describes `classification_items ↔ api_attempts ↔ api_spend` as settling 1:1. Cardinality is not 1:1: a logical request can contain several snippets and can have several physical retries; a crash can legitimately leave a conservative reservation without a completed attempt.

Implement and gate explicit relational invariants instead:

- every physical dispatch has exactly one pre-dispatch reservation;
- every returned physical dispatch updates exactly one attempt row;
- every logical request maps an ordered snippet set and one or more attempts;
- every successful label maps to the request/attempt/protocol that generated it;
- every reservation is settled, released with a reason, or remains a named reconciliation exception;
- campaign totals reconcile to provider billing within a declared tolerance.

### B7. Provider credentials and error data are broader than necessary

`classify` calls `load_env()` before selecting the provider, and that function loads every allowlisted provider key from repo-root `.env`. An OpenAI-only run therefore exposes Anthropic and Google credentials to the same process. Load only the selected provider's project-scoped, spend-limited credential and keep unrelated keys out of the run environment.

Normalize HTTP errors before console/DB/JSONL output. Current provider errors can persist the first 300 characters of a response body, which may echo submitted content. Establish retention/deletion rules for prompts, responses, snippets, attempts, and backups before the full run.

### Gate B acceptance criteria

- pre-created, owner-authorized campaign; unknown IDs fail closed;
- campaign/cap/tariff/purpose bound to protocol and immutable across resume;
- explicit Luna inference settings and returned-model provenance;
- durable request and attempt rows created before dispatch;
- exact mapping across split/re-ask/retry paths, spend, and snippets;
- lease fencing in reservation, dispatch, and result transactions;
- crash/retry/takeover/provider-console reconciliation command;
- multiprocess and fault-injection tests proving the cap and fence;
- provider-specific least-privilege credential loading.

## Gate C — implement the final two-grader gold study as a release-bound experiment

### C1. The only packet builder is still calibration-only

`pipeline/annotate.py:245-370` accepts raw scan/classification run IDs and hard-codes `calibration_only_never_release_validity` plus a calibration banner. There is no `--release` mode, no frozen release-member input, and no gate that verifies clean/complete compatible runs, exact cohort, evidence requirements, campaign, or instrument bundle.

This candor is preferable to accidentally calling the current packets gold, but it means the final study described in `GOLD_STUDY.md` does not yet exist. Build it as a separate mode or command that consumes exactly one immutable release candidate and refuses arbitrary run IDs.

### C2. Reviewers can still see text/metadata from the wrong artifact or version

Context extraction reads the current mutable `files` row rather than the artifact selected by the scan (`pipeline/annotate.py:98-116`). An existing `contexts.json` is reused merely because the path exists. Unknown scanned versions can fall back to current `latest_version`, and comments/title metadata are current. PDFs are optional. This recreates the exact version-skew defect that invalidated one calibration pair.

For each gold item, bind and verify:

- release member and stratum;
- paper ID and exact scanned version/basis;
- selected artifact ID, kind, path-independent content hash, and license;
- evidence hit/item IDs and rendered-status record;
- exact excerpt/context bytes and hash;
- exact PDF bytes/extractor identity/hash (or a reason-coded unavailable state);
- taxonomy/manual/prompt/schema hash;
- reviewer assignment/order and packet hash.

Never reuse a cache unless this complete identity matches. Reviewer-visible metadata must be from the same version or explicitly marked as later/current and excluded from evidentiary judgment.

### C3. Manifest and ingest remain fail-open and insufficiently bound

The master manifest contains strata/plant identities alongside packet material and has no per-reviewer immutable assignment bundle. Packet `localStorage` is keyed only by project and reviewer, so regenerating a project can silently restore stale judgments into a changed packet.

JSON ingest warns and proceeds when the manifest is absent (`pipeline/annotate.py:695-703`). When present, it checks only global paper membership—not reviewer assignment, exact version, release, codebook hash, context/PDF/packet hash, export hash, or packet generation. It trusts the submitted codebook version. The annotations schema lacks uniqueness and the design/provenance fields needed for a probability study.

Make the master allocator private and produce a signed/hashed, blinded assignment manifest per reviewer. Namespace browser state and exports by packet hash. Fail closed if any manifest or hash is missing/mismatched; ingest all-or-nothing transactionally; reject wrong reviewer/version/codebook/assignment and duplicate items. Add DB keys/fields for release, round, stratum, inclusion probability, assignment, packet/export hashes, evaluator status, COI, search process, plant status, and adjudication lineage.

### C4. The shared double-coded subset is not allocated

Reviewer order is independently shuffled, while `GOLD_STUDY.md:98-101` says reviewer 2 can label the first roughly 100–150 positions. Two independent prefixes do not produce a 100–150-item shared subset; expected overlap is far smaller. Explicitly sample and record a shared, stratified, powered overlap, then independently randomize its presentation order within each packet. Assign remaining items singly according to the estimator design.

### C5. Adjudication requires a coherent third-person design

The protocol says reviewers never adjudicate their own disagreements, permits a joint session for human–human disagreements, and requires a reviewer who supplied neither label for human–machine disagreements (`GOLD_STUDY.md:117-130`). With only the two primary graders, those rules cannot all hold.

Name and train a third blinded adjudicator before packet launch. Re-blind disagreements among random agreed controls as proposed, capture the adjudicator's independent verdict before revealing prior labels, and preserve every first-pass row. Define what happens to `UNCLEAR`, `INSUFFICIENT_EVIDENCE`, unreadable PDFs, COIs, and unresolved adjudications.

### C6. The estimator/power implementation is absent

Current `agreement` computes verdict-only raw agreement/kappa from the first two available rows; it has no reviewer-pair binding, axis metrics, CIs, weighting, adjudication, or non-evaluable treatment. `annotate calibration` is useful but is not the final estimator. It does not verify its run arguments against the manifest, emits no impact/category/location metrics, and its plant statistic covers hidden machine-positive plants rather than a general search-sensitivity estimand.

Implement and test before annotation:

- finite-population/inclusion weights by stratum;
- adjudicated precision overall and by prespecified impact strata;
- expanded false-omission totals and sensitivity with uncertainty;
- corrected prevalence with acquisition/scan/non-evaluable bounds;
- axis agreement/IRR with CIs and rare-class caveats;
- bootstrap or another prespecified two-phase variance estimator;
- process metrics for search time, PDF opened/version verified, sections/queries checked, plant found, unreadability, and COI;
- deterministic, machine-readable analysis outputs with all input hashes.

The POS n=150 may support overall precision near 0.9, but not reliable precision for five impact classes and 17 categories without impact/hard-case oversampling. Power the quantities you plan to publish; label the rest exploratory.

### C7. Define the frame that “sensitivity” refers to

The gold frame is scan-complete release members (`GOLD_STUDY.md:21-36`). That can estimate retrieval/classification performance within captured papers, not sensitivity across the entire 133,279-paper acquisition frame. Keep acquisition missingness as a separate partial-identification problem. The statement that 0/300 NEG misses gives about a 1.2% upper bound applies to the sampled NEG-arm miss probability before design weighting, not directly to overall sensitivity.

Resolve `DECISIONS.md:151-152` before preregistration: is the primary result a selected observed-v1 cohort, partial-identification bounds for the three-year frame, or a shorter nearly complete window? Gold validation cannot repair outcome-dependent missing acquisition.

### C8. R5 needs a multi-state paper rollup

`report.py` selects one scalar maximum impact. A paper containing both a contributing use and an explicitly fruitless attempt becomes only the maximum; similarly, `undetermined` disappears when another snippet has a contributing impact. That contradicts the promise that zero-contribution and undetermined slices are never silently pooled.

Store/derive at paper level at least:

- `has_author_use`;
- `has_contributing_use`;
- `has_zero_contribution_attempt`;
- `has_undetermined_impact`;
- `max_contributing_impact`.

Use these explicit states in sampling, validation, report, site, and corrected estimators. Prespecify whether the headline includes attempts, contributions, or both.

### Gate C acceptance criteria

- immutable release-candidate input and exact item/artifact/evidence/PDF/context/codebook hashes;
- private allocator plus hashed reviewer-specific blinded assignments;
- packet-hash-bound browser state/export and fail-closed transactional ingest;
- deliberate stratified shared overlap and named independent adjudicator;
- COI/evaluability/search/plant/version-confirmation fields;
- weighted estimators, CIs, missing-frame bounds, and powered targets frozen in code;
- multi-state R5 paper rollup;
- malicious-input, wrong-version, stale-cache, wrong-reviewer, duplicate, and end-to-end synthetic tests.

## Gate D — make freeze a real immutable, validated release

### D1. Freeze can certify an unvalidated partial measurement

`run_info(..., freeze=True)` permits a partial scan and requires neither grounding nor rendering (`pipeline/report.py:91-124`). CLI gates are optional. Freeze does not require:

- a full/approved selection manifest or a maximum unresolved threshold;
- v1/artifact/version-basis completeness;
- quote grounding and exact render certification;
- final gold metrics/pass thresholds;
- approved campaign closure and provider-billing reconciliation;
- complete request/attempt/spend lineage;
- signed owner acknowledgement of remaining missingness.

The report nevertheless says “validity gates were enforced.” Record the exact gates and their values; never use that sentence when the list is empty. A partial-identification release can be legitimate, but it needs an explicitly approved frame/missingness contract rather than the generic state `partial`.

### D2. A release is only hashes of mutable-query results

`pipeline/report.py:437-466` stores counts and a few set hashes. It does not materialize release members, selected artifact/version basis, labels, evidence, render decisions, gold rows/metrics, acquisition states, or complete protocol/attempt provenance. There are no database triggers making source rows immutable. Re-running a live query is not equivalent to reading a frozen release.

Create append-only release-member/result tables or a content-addressed immutable snapshot. Include exact frame and every reason-coded terminal state, selected artifact/evidence/render rows, final effective labels, instrument and environment hashes, gold sample/metrics, campaign/attempt reconciliation, output artifact hashes, correction lineage, and release-builder identity. Sign a manifest and verify it independently from a fresh clone/data snapshot.

### D3. The generator commit can mark itself dirty

`report --freeze` writes the report before calling `db.code_commit()` for the release record (`pipeline/report.py:433-475`). The default report path is tracked, so a normal successful generation makes the worktree dirty and can stamp `<HEAD>-dirty`. Capture and validate a clean full commit/tree before output, run the complete build from that identity, stage artifacts elsewhere, then atomically publish and record their hashes.

### D4. The site still bypasses releases

`pipeline/build_site.py:181-184,578-588` accepts raw scan/classification IDs and always emits `unreleased_exploratory`; it cannot consume a release ID. Keep that route as a private preview, but add a distinct production command that accepts only a validated immutable release, refuses unresolved gates, emits all machine-readable limitations/licensing/provenance, and builds into an empty staging directory. Byte-compare two builds before deployment.

### D5. The primary v1 frame remains only partially identified

Within the 133,279-paper primary frame, only 85,742 are scan-complete in the current v1 path; 47,554 are unresolved. The selected v1 cohort consists of 10,512 explicit-v1 and 75,230 inferred-single-version `ok` papers. Human validation can estimate classifier error in this observed selected cohort but cannot turn it into full-frame prevalence.

Valid release choices include:

- a clearly named selected-frame disclosure audit;
- full-frame partial-identification ranges, with measurement uncertainty layered on them;
- a shorter period with near-complete v1 acquisition;
- waiting for an authorized tail-acquisition strategy.

Do not describe a selected/flag-influenced v1 analysis as three-year math-arXiv prevalence.

### Gate D acceptance criteria

- exact owner-approved frame and missingness policy;
- all required evidence/gold/campaign/provenance gates mandatory and machine checked;
- materialized/content-addressed immutable release membership and results;
- clean builder identity captured before generation;
- signed release manifest with artifact hashes and correction lineage;
- site/report built only from `release_id` in deterministic staging;
- independent fresh-snapshot reproduction and integrity verification.

## Gate E — privacy, disclosure control, governance, and public delivery

### E1. Small-cell disclosure remains a concrete reidentification risk

`_suppress_small()` is applied to selected tool/provider tables but not categories, impact, or location. Exact daily, weekly, and subfield-month series are embedded in HTML/JSON. The current tracked output contains an unsuppressed category cell below 3 and **601 positive time/subfield cells of size 1–2, including 417 singletons**. Overlapping three-month, one-year, and three-year views enable complementary differencing.

This can identify a paper by joining a date/subfield/tool cell back to public arXiv metadata. A denominator threshold does not protect a numerator of one. Define a disclosure-risk policy across every HTML, JSON, CSV, report, review, and downloadable aggregate:

- minimum numerator and denominator;
- complementary/secondary suppression across overlapping margins/windows;
- coarser time/category grouping where necessary;
- rare-label/model-name roll-up;
- release-time attack tests that attempt differencing and joins.

Apply suppression before serialization, not only to the visible table. `noindex` and “do not cite” are warnings, not access controls.

### E2. Current tracked prose and Git history still cross the aggregate-only boundary

The quarantine commit is a major improvement, but the current tree still contains identifiable development material: `PITCH.md:9-14` names real pilot papers and includes a verbatim disclosure excerpt; older design text promises public per-paper labels/annotations; code/help comments retain a few real case IDs; and `pipeline/aws/math_ids.txt` is a 1.86 MB per-paper frame manifest whose publication status/licensing is not explicitly decided.

Deleted `results/*`, awesome-validation, spotcheck, site ZIP, and infrastructure inventory remain in reachable Git history. Some contained long source excerpts and contact/address data. Before the first public push:

1. define an explicit public-artifact allowlist/matrix (software, docs, frame IDs, aggregate tables, validation metrics, per-paper labels, excerpts, hashes);
2. replace real development cases with synthetic/deidentified examples and reconcile `PITCH.md`, `DESIGN_PLATFORM.md`, `TECH_NOTES.md`, `WORKFLOW.md`, `DECISIONS.md`, and `LICENSE`;
3. produce a clean public history/export from a private canonical archive;
4. scan the full object database for keys, excerpts, contact data, paper-level judgments, paths, and cloud inventory;
5. verify a fresh clone contains only allowlisted material.

There is no configured remote or tag locally, so this is an unusually good moment to sanitize. Confirm separately whether any prior history was ever pushed.

### E3. Provider governance is not yet approved

Good security changes include identifier minimization, one-paper API isolation, tools disabled, strict schema, fixed origins, no redirects, `trust_env=False`, and `store:false`. They do not establish a complete confidentiality/legal basis. Up to 2,400 characters can still come from residual/unrendered TeX members before render checking; stripping the arXiv ID does not necessarily deidentify distinctive text.

Before corpus dispatch, record the organization/project settings and institutional decision covering training opt-in, abuse-monitoring retention, ZDR/modified monitoring eligibility, DPA, subprocessors, region/transfers, deletion, incident response, and permitted data categories. OpenAI's current [API data-controls documentation](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint) states that API data is not used for training absent opt-in, while default abuse-monitoring logs may retain content; `store:false` is not by itself zero retention.

Prefer rendered/reachable evidence as the provider input or explicitly approve the residual-source risk. Define access/retention/deletion for raw snippets, model responses, request logs, spend data, annotation packets, and backups.

### E4. Local data/key isolation is not demonstrated

The repo-local `.env`, database/backups, corpus/logs, and annotation material appear mode `0777` through DrvFS. That does not prove they are world-accessible on Windows, but it means POSIX mode is not evidence of restriction. Verify Windows ACLs, encryption/BitLocker, synchronization/share configuration, backup destinations, and secret-manager scope. Keep provider keys outside the repository and load only the selected provider's spend-limited project key.

The database still holds roughly 235,323 historical submitter values. New parsing drops the field, but raw OAI archives retain it. If submitter identity has no documented purpose, purge it from live/backup copies (including vacuum/rekey implications) and define archive retention/access; otherwise document its legal basis and controls.

### E5. The governance/publication package remains incomplete

The MIT software license and scope notes are welcome. Aggregate data are only described as “intended” CC BY; that is not an operative release license. Before publication, add:

- release-level aggregate data license and source/license matrix;
- `CITATION.cff`, DOI/tag/version policy, data dictionary, schema, checksums, and changelog;
- privacy/data-governance notice (controller, purpose/legal basis, processors, access, retention, rights, incidents);
- `SECURITY.md` and vulnerability-reporting process;
- corrections, appeals, takedown, supersession, and public error-ledger policy;
- governance/roles/COI, contributor/code-of-conduct, reviewer confidentiality/retention agreement;
- explicit funder-role and competing-interest statement, including whether Google influenced design, analysis, publication, or provider/model choice.

Do not describe the AI-assisted review rounds as independent human review. The human owner retained final responsibility; Codex/Claude supplied AI-system audits and implementation assistance.

### E6. CI and deployment remain skeletal

`.github/workflows/ci.yml` says “tests + site build” but only installs and runs pytest. Actions are SHA-pinned and no deployment exists—good containment. Add:

- explicit `permissions: contents: read`, checkout `persist-credentials:false`, timeouts, and concurrency cancellation;
- hash-locked dependencies, dependency/license/SBOM and secret/history scans;
- migration-from-empty and fixture end-to-end classify/release/gold tests;
- campaign/lease/retry/crash/fencing fault injection;
- release-only site build twice with byte equality;
- publication-boundary and complementary-suppression tests;
- HTML/schema/link/browser/accessibility/security-header checks;
- a separately protected, manually approved deployment job that accepts only a signed release artifact and supports rollback.

### E7. Accessibility and reach should follow scientific credibility

The static, tracker-free design and table alternatives are strong. Remaining issues include SVGs without chart-level accessible names/descriptions, mouse-centric tooltips, hidden/JS-dependent tables, no robust no-JS summary, narrow-screen `minmax(420px)` overflow risk, and muted 12.5px text around 3.4:1 contrast. Run automated and manual keyboard, screen-reader, no-JS, mobile, zoom, high-contrast, and reduced-motion checks.

For launch, add a canonical URL, release-aware robots/sitemap, Open Graph/social card, favicon, stable methods/validation/privacy/correction/contact pages, DOI/citation metadata, aggregate download with schema/license/checksums, and chart-level accessible summaries. Keep `noindex` and `do_not_cite` until all scientific and governance gates pass.

### Gate E acceptance criteria

- allowlisted clean public tree/history, verified from a fresh clone;
- suppression and complementary-differencing tests across every public artifact;
- approved vendor/privacy/local-access/retention controls;
- operative data license and governance/correction/security/citation package;
- deterministic signed release artifact and protected rollback-capable deployment;
- accessibility/security-header/browser pass;
- public claims generated from the validated release, never hand-maintained previews.

## Additional engineering and reproducibility debt

These are not all blockers for the immediate v2.3 rerun, but they matter before scale or public release:

- Artifact rows can still point to deterministic paths whose bytes could be overwritten; make blobs content-addressed or refuse mismatched overwrite.
- Scan selection manifests should persist their full member/artifact preimage in immutable DB rows, not only count/hash sidecars.
- Archive handling still needs outer compressed-size, member-count/header, decompression-ratio, total-wall-time, and converter sandbox limits; PDF text caches should bind input SHA + extractor version + output SHA.
- The scanner examines every text-like archive member rather than a rendered TeX include graph, creating both false-positive and privacy risk.
- OAI deleted records should become tombstones, and offline reparse must recurse through the actual per-run archive layout.
- Per-version arXiv licenses are not captured with artifacts.
- The AWS producer/sync path remains less crash-safe and fail-closed than the importer; infrastructure/security/teardown are not fully code-defined.
- Legacy `pipeline/audit.py` and `arxiv_ai_ack_scan.py` retain weaker scientific/resource boundaries and should hard-fail or be clearly removed from operational entry points.
- Preliminary tracked reports contain stale wording and unsuppressed small cells; quarantine or regenerate them under the same publication policy.
- README/site review-count and “current review” text are stale; derive public provenance from one release metadata source.

## Recommended execution order

1. **Stop before the paid run.** Fix A4, B1, B3–B5; add the corresponding negative/race/crash tests.
2. **Freeze the instrument.** Resolve R4 precedence and R5 paper rollup, run a two-human/Luna v2.3 comprehension matrix, reconcile adherence outputs/provenance, then record exact owner sign-off and inference controls.
3. **Authorize one campaign.** Pre-create a scoped full-run campaign, archive tariff/account settings, use one provider-specific key, test lease takeover and spend reconciliation, then launch.
4. **While classification runs, build Gate C/D on synthetic fixtures.** Materialize a release candidate, implement hashed packet assignment/ingest/adjudication/estimators, and prove the complete chain without touching confirmatory labels.
5. **Resolve the primary public estimand.** Selected observed-v1 cohort, explicit partial identification, a more complete short window, or an authorized tail—not an ambiguous prevalence headline.
6. **Draw fresh final gold only after release-candidate freeze.** Two independent graders, deliberate overlap, third adjudicator, exact artifact binding, prespecified weighted analysis.
7. **Publish only the validated release.** Sanitize history, enforce disclosure controls, complete governance/licensing/privacy, generate deterministic signed artifacts, and deploy through protected approval.

## Bottom line

Iteration 9 is a meaningful advance. The project now has a much more credible taxonomy bundle, atomic campaign accounting, stronger leases, a useful in-sample smoke test, and a healthier public-tree boundary. The remaining issues are unusually well localized—and this is precisely the right moment to fix them, because **there are still zero v2.3 production labels and zero releases**.

My recommendation is a short, explicit no-go on the full run until owner sign-off, human/machine parity, campaign authorization binding, true lease fencing, and durable request/attempt provenance are complete. Once those pass, the classification run itself can proceed while the independently larger gold/release/publication gates are implemented. Do not let the encouraging 147/149 development headline collapse those distinct stages.
