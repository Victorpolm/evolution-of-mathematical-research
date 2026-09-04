# ArxivObservatory repository review — iteration 10

**Audit snapshot:** Git commit `da362e58d508492fdba51c3568fe1cd5ea211cde`, tree `ea4f5b3d435bd792ec8fd28e0402e5210abfb330`, committed 2026-08-12 19:49 CEST. The worktree was clean before this review file was added.

**Primary delta reviewed:** the single post-iteration-9 commit `da362e5`, especially taxonomy v2.4 and the revised R4 precedence rules, the real `classify --papers-file` adherence run, campaign authorization/protocol hashing, token and dollar admission, run leases, per-exchange and pre-dispatch attempt provenance, R5 multi-state rollup, final-gold tooling, freeze/release behavior, disclosure control, and publication preparation.

**Audit boundary:** read-only except for creating this report. I did not call a model or provider API, contact arXiv, start or stop a pipeline job, alter the database/corpus/annotation records, operate cloud resources, or publish anything. Restricted annotation material is discussed only in aggregate. I checked current official OpenAI documentation where model behavior and pricing directly affect the imminent paid run; this was not a fresh systematic verification of the scientific bibliography.

## Executive verdict

This revision closes several important iteration-9 findings. The exact v2.4 taxonomy/manual/prompt/schema hashes recorded in `DECISIONS.md` reproduce; non-author-use catalytic contradictions now fail closed on both machine and human paths; OpenAI reasoning effort is explicit; unknown budget campaigns fail closed; campaign identity and cap enter the run protocol; parse re-asks and split failures retain substantially better provenance; physical attempt rows now exist before HTTP dispatch; only the selected provider key is loaded from `.env`; and the replacement adherence run exercised the supported classifier path successfully. All 130 tests pass.

The project is nevertheless **not ready to start the full paid v2.4 classification run**. The remaining blockers are concrete, and three are newly exposed by the real adherence run:

1. **The scientific construct is still contradictory and unsigned.** R4 says intentionally “invoked or incorporated” AI-produced inputs are `author_use`, but then forces every pre-existing AI artifact to `topic_only`, including embeddings reused as input features. Human packet tooltips use a narrower “used to produce the paper” construct. `DECISIONS.md` correctly still marks exact-text owner sign-off as pending.
2. **The adherence run's scope is not part of its identity.** `--papers-file` is applied after protocol creation, and neither its contents nor a hash/count enters the run protocol. The resulting 199-item subset is marked `complete` as though it completely classified the consumed scan run. A partial scoped run can resume with the scope changed or omitted.
3. **The nominal hard dollar cap omits a tariff that occurred in the live run.** The official Luna page lists cache writes at 1.25× input price. The 54-call adherence run reports 174,153 cache-write tokens, but the ledger charges all 174,315 input tokens at the base rate. Recorded spend is $0.0699402; applying the documented cache-write rate gives approximately $0.07864785, a 12.45% undercount. The same mix could let a nominal $50 gate authorize materially more than $50.
4. **Successful responses with missing or malformed usage can settle at $0.** Provider adapters default absent usage fields to zero, and settlement treats zero as authoritative. This is an independent fail-open in the budget boundary.
5. **Lease and campaign checks are not in the business transactions they protect.** A stale worker can dispatch or write after takeover before its in-memory lost event updates; transport retries do not recheck the fence; final status and error writes are unfenced.

The project is also **not ready for the final two-grader gold study**. The only implemented packet builder explicitly labels every project calibration-only; it reads mutable current files rather than the exact scanned artifact, blindly reuses a context cache, fails open when the manifest is missing, has no release/packet/artifact hash chain, does not assign a guaranteed shared double-coded subset, and has no implemented adjudication or design-weighted estimator.

Finally, a frozen scientific release and public launch remain separate no-go decisions. Freeze permits optional evidence gates and no gold gate, stores digests over mutable live tables rather than materialized release members, and the site consumes raw run IDs. The public preview still contains hundreds of singleton/doubleton time cells, ordinary Git history still contains deleted expressive paper-level artifacts, and privacy/governance/licensing/deployment controls remain incomplete.

### Readiness call

| Activity | Readiness at this snapshot |
|---|---|
| Resolve R4 wording and run a frozen two-human-plus-Luna boundary exercise | **Ready now** |
| Full paid Luna v2.4 classification run | **No-go until Gates A and B pass** |
| Final two-grader gold study | **No-go until Gate C is implemented and dry-run** |
| Private inspection of explicitly exploratory aggregates | **Acceptable with restricted access and existing warnings** |
| Frozen scientific release or prevalence claim | **No-go until Gate D** |
| Public Git repository or real-data site | **No-go until Gate E** |
| Three-year population prevalence from current v1 data | **Not identified; the observed v1 frame remains strongly incomplete/selected** |

The shortest safe sequence is: resolve and sign one construct; fix run-scope, tariff/usage admission, and transactional fencing; run the full v2.4 classification; materialize one release candidate; draw a fresh artifact-exact gold sample; adjudicate and estimate under a frozen analysis; then generate disclosure-controlled publication artifacts from that release alone.

## Snapshot and verification

### Automated and integrity checks

- `python3 -m pytest -q -p no:cacheprovider`: **130 passed in 3.10 s**.
- Python AST parsing succeeded for all 36 tracked pipeline/test Python files.
- `python3 -m pip check`: no broken requirements.
- `bash -n`: passed for every tracked shell script.
- `git diff --check 0caa526..HEAD`: passed.
- SQLite `PRAGMA quick_check`: `ok`; `PRAGMA foreign_key_check`: no violations.
- The worktree was clean before this report was created.

The added tests are useful: they cover non-author catalytic rejection, unknown-campaign failure, protocol-bound cap metadata, the byte-count estimator, separate re-ask/failure records, pre-dispatch attempt rows, and error-body normalization. They do not yet cover scoped-run identity/resume, cache-write tariffs, missing/malformed usage, transactional lease takeover, cross-model campaign reservation, immutable campaign amendments, release-only builds, or final-gold chain of custody.

### Point-in-time local data state

The local database appeared quiescent during inspection. These are point-in-time local counts, not a clone-reconstructible release:

- schema version: **7**;
- papers / versions: **235,342 / 418,232**;
- files / artifacts: **169,166 / 187,918**;
- scan runs / items / hits: **4 / 281,870 / 982,232**;
- classification runs / items / evidence edges: **7 / 145,371 / 339,354**;
- render checks: **14,758**;
- human annotations: **150**, all one reviewer and codebook v2.0;
- releases: **0**;
- active run leases: **0**;
- v2.4 production/full-frame classification runs: **0**.

The v1 scan `texv1-20260811T215148` remains partial: 112,447 selected, 110,770 `ok`, 54 unknown-format, 2 incomplete, and 1,621 skipped PDF-in-tar items. The older Luna classification `cls-20260811T220922` remains taxonomy v2.0 and partial: 71,194 items, 71,022 `ok`, and 172 non-ok items.

The new tracked adherence run `cls-20260812T175021` is taxonomy v2.4, API/OpenAI/Luna, clean-code and isolated. It contains 199/199 valid classified snippet groups from 53 papers, with evidence for every item. Its 54 attempts are all HTTP 200, and each currently links a unique settled reservation, request, prompt/response hashes, split path, and snippet hashes. This is a meaningful prospective improvement.

The one campaign has 110 settled spend rows totaling approximately **$0.143533**: 56 historical ad-hoc calls whose missing attempt lineage is now honestly retracted, plus 54 calls in the tracked run. The campaign remains active and has not been closed or reconciled with provider-console billing.

## What is genuinely stronger since iteration 9

The following changes are substantive and should be preserved:

- taxonomy version discipline was respected: v2.4 was created before a full v2.3/v2.4 production run;
- SHA-256 values for `pipeline/taxonomy.py`, `TAXONOMY.md`, the generated prompt, and provider schema exactly match `DECISIONS.md:15-18`;
- non-author-use semantic contradictions now invoke the shared invariant and are rejected rather than silently repaired (`pipeline/classify.py:320-344`);
- OpenAI `reasoning_effort` is explicitly `medium`, `store:false` remains set, and the inference configuration enters protocol metadata;
- unknown campaign IDs fail closed, and approval ID/provider/model/cap/price-snapshot hash are protocol-bound;
- parse re-asks are separate exchanges and failed split nodes retain prompt/response information much more reliably (`pipeline/classify.py:374-503`);
- physical `api_attempts` rows are created before HTTP and updated in the worker thread (`pipeline/llm_api.py:612-683`);
- successful adaptive split children carry deterministic paths and exact ordered snippet hashes;
- the normal tracked adherence run reconciles 54 attempts with 54 unique settled reservations and 199 valid labels;
- selected-provider `.env` loading reduces unnecessary key exposure;
- non-2xx provider errors are normalized without copying arbitrary response bodies;
- paper rollup now preserves an impact set plus `has_contributing_use`, `has_zero_contribution_attempt`, and `has_undetermined_impact` (`pipeline/report.py:183-222`);
- current tracked real-paper result dumps and unrelated Lean files remain quarantined;
- the preview remains tracker-free, `noindex`, visibly unreleased, machine-readable as `do_not_cite`, and explicit about non-affiliation;
- CI action versions remain SHA-pinned, and there is still no automatic deploy path that could silently publish this state.

Several of these fixes are only prospective or only half-wired. The gates below distinguish a repaired producer from a validated consumer.

## Gate A — sign one coherent scientific instrument

### A1. R4 still contains a construct contradiction

The primary definition says `author_use` covers authors who intentionally invoked or incorporated an AI system to produce an input used in conducting or communicating the research (`TAXONOMY.md:56,69-73`). `topic_only` is supposed to cover AI observed as the scientific object with no output consumed outside that observation (`:58,66-68`).

The new precedence rule then says that if the authors did not invoke the system during this research, *any* pre-existing AI-produced artifact is `topic_only` and later tests are skipped (`:87-91`). The decision table explicitly labels “pre-existing published embeddings reused as input features, no invocation” as `topic_only + method_component` (`:111`). But reused input features are incorporated and consumed outside mere observation. These rules cannot all be true simultaneously.

The owner needs to choose and name the construct:

- **active-invocation construct:** only systems executed by the authors during the project count. Reused AI-produced artifacts are outside the numerator, but they should not be called `topic_only` unless AI is actually the topic; add a distinct `external_ai_artifact`/`method_component_out_of_scope` state and remove “incorporated” from `author_use`; or
- **incorporation construct:** intentionally using a pre-existing AI-produced artifact as a research input counts when it serves a non-AI target. Then the table row at `TAXONOMY.md:111` must be `author_use`, while observation/evaluation of AI as the object remains `topic_only`.

This is not cosmetic wording. It changes polarity, denominator interpretation, provider/tool counts, and the public meaning of “AI assistance.” Resolve it before owner sign-off or spending.

### A2. Human and machine graders still see different scope language

The human `TRUE_DISCLOSURE` tooltip says AI was used “in producing this paper,” and `TOPIC_ONLY` says it was “not as a tool used to produce the paper” (`pipeline/annotate.py:34-44`). That language omits the owner-confirmed instrumentation scope—labels, judgments, embeddings, synthetic data, and pipeline code used to conduct the research—and is narrower than the machine prompt.

Generate the grader-facing definitions from the same taxonomy source or embed one frozen instruction block verbatim. A test that vocabulary matches is insufficient when the decision text differs. The final packet must carry the exact manual/prompt/schema hashes, not merely `codebook_version`.

### A3. Exact-text owner sign-off is correctly still pending

`DECISIONS.md:12-14` explicitly says exact committed v2.4 text sign-off remains pending. Preserve that gate. After fixing A1/A2, record one dated decision covering:

- exact taxonomy/manual/prompt/schema hashes;
- primary retrieval scope (`llm`/`generic`, not comprehensive prover/CAS/general-ML detection);
- active-invocation versus incorporation policy;
- R5 attempted/contributing quantities;
- model endpoint, returned-alias limitation, reasoning effort, output cap, and response schema;
- the intended full-run target manifest and budget campaign.

Any semantic edit after sign-off should bump the taxonomy and require a new comprehension check.

### A4. Run a real current-codebook comprehension and repeatability exercise

The existing human labels were created under v2.0. The v2.4 tracked run compares against them; it does not show that either intended human grader understands v2.4 R4/R5.

Before the full run, have both intended graders independently label a small frozen set of synthetic or deidentified vignettes under the exact signed text, blinded to Luna. Cover at least:

- pre-existing embedding reuse versus fresh inference;
- frozen model inside the studied object versus an instrumentation toolchain;
- LLM judge/labeler/synthetic-data generation;
- dual object-of-study and writing/coding roles;
- redundant correct output, explicitly fruitless output, catalytic output, and vague disclosure;
- method-component plus non-author polarities;
- multi-snippet papers with contributing, zero, and undetermined uses together.

Run Luna repeatedly on exactly the same set and report polarity, impact, category, and flag stability—not only binary agreement. Adjudicate misunderstandings, update/bump the manual if needed, then obtain sign-off. This is a measurement-instrument check, not final accuracy evidence.

### A5. The adherence result is encouraging but narrow

Correct interpretation of the available aggregates is:

- calibration: 150 ingested; 149 comparable after one version-skew exclusion; all human labels v2.0 and one reviewer;
- shown-positive precision: 28/32 = 87.5% (development estimate);
- plants: 5/5, a weak process check with a wide interval and easier-than-latent cases;
- FLAG: 0/16; NEG: 0/96;
- v2.4 backward binary concordance: **51/53 model-evaluable papers**, plus **96/96 structural no-snippet papers**;
- combined 147/149 is arithmetically correct but must not be presented as v2.4 accuracy on 149 model calls.

The tracked run is operationally real and much better than the superseded ad-hoc exercise. It is still in-sample, human labels predate R4/R5, and the sample intentionally contains only papers from the calibration project. Treat it as regression/adherence evidence.

### A6. R5 multi-state semantics are not end-to-end

`paper_rollup()` now correctly keeps all observed impacts and overlapping booleans. The consumers do not:

- report named quantities still count only scalar maximum impact (`pipeline/report.py:415-427`);
- report impact tables still use the maximum (`:397-431`);
- site/export code has no use of `impacts_seen`/`has_*` and pools every `author_use` into the headline;
- the human form records one paper-level impact radio value (`pipeline/annotate.py:424-427`).

The adherence aggregate demonstrates the error: among 35 author-use papers, 33 have any contributing use, 2 have an explicit zero-contribution attempt, and 3 have an undetermined use. Both zero-attempt papers also have a contributing use, and one undetermined paper also contributes. Scalar maxima would report zero=0 and undetermined=2.

Define overlapping paper quantities and consume them everywhere:

- `has_any_author_use`;
- `has_contributing_use` and `max_contributing_impact`;
- `has_zero_contribution_attempt`;
- `has_undetermined_impact`.

Let humans record these states per snippet or as explicit overlapping paper flags. Test mixed-state papers in report, JSON, site, sampling, and gold estimation. Never call `zero_contribution` “assistance” without saying the authors reported no contribution.

### Gate A acceptance criteria

- coherent active-invocation/incorporation policy and non-misleading polarity names;
- identical grader/machine rule text and one hash-bound instrument bundle;
- overlapping R5 states implemented in human records and every consumer;
- two-human-plus-Luna frozen comprehension/repeatability matrix;
- dated owner sign-off on the exact bundle, estimands, scope, and inference controls.

## Gate B — make scope, spending, fencing, and provenance enforceable

### B1. `--papers-file` is outside protocol identity and corrupts completeness semantics

`pipeline/classify.py` creates/checks the protocol and classification run before it applies `--papers-file` (`:837-917,929-950`). The protocol contains scan runs and campaign settings but no scope mode, sorted ID membership, count, or manifest hash. The invocation sidecar records only a mutable pathname (`:958-971`).

The defect is realized: `cls-20260812T175021` is marked `complete` while containing 199 of roughly 73,995 classifiable snippet groups and 53 of about 22,205 flagged papers from the consumed scan run. Its sidecar points to an ephemeral `/tmp/.../adherence_papers.txt`; the target preimage is not in the database/protocol. A partial scoped run could resume with the file changed or omitted and silently mix/expand scope.

Introduce an explicit scoped/adherence run type. Before run creation:

- canonicalize, validate, sort, and deduplicate IDs;
- persist an immutable target manifest containing the actual IDs plus hash/count/purpose;
- bind that manifest, scope mode, and intended use into `params_json`, protocol hash, every invocation, and input identity;
- reject any resume scope change;
- use a status such as `complete_scoped`, never `complete` for the full scan;
- make report/freeze refuse scoped runs for population outputs.

Add tests for empty, missing, duplicate, changed, and omitted manifests, partial scoped resume, and report/freeze refusal.

### B2. The live budget ledger omits Luna cache-write pricing

The direct current [official GPT-5.6 Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna) lists base pricing of $0.20/M input and $1.20/M output, matching `pipeline/llm_api.py:48-55`. It also lists cached input and cache writes billed at 1.25× the uncached input rate. The source code's tariff and `_cost_usd()` have only base input/output (`:456-464`).

This mattered in the actual run:

- prompt tokens: 174,315;
- reported cache-write tokens: 174,153;
- completion tokens: 29,231;
- ledger cost at base rates: **$0.0699402**;
- cost using 1.25× for the reported cache-write tokens: approximately **$0.07864785**;
- undercount: approximately **$0.00870765**, or **12.45%** of recorded spend.

Thus the present $50 admission is not a hard $50 account-cost cap. Extend the versioned tariff to all usage classes (uncached input, cached read, cache write, output, long-context multipliers), persist the full tariff hash/evidence, reserve at the worst applicable rate, and settle using validated provider usage details. Reconcile the current campaign with the provider console before authorizing the full run.

### B3. Missing/malformed success usage can settle a billed call at $0

Anthropic, OpenAI, and Google adapters default absent token fields to zero (`pipeline/llm_api.py:710-724,754-768,787-800`). `_settle()` treats any non-`None` count—including zero, negative, boolean, or malformed values not rejected upstream—as authoritative and replaces the reservation (`:544-572`).

A successful billed response without a recognized usage object can therefore lower its durable cost to $0 and keep dispatching beneath the cap. Require provider-specific usage schemas, nonnegative integers with booleans rejected, and internal consistency checks. If usage is missing or inconsistent, keep the full conservative reservation as `unknown_usage` until console reconciliation; never release or reduce it to zero.

### B4. The token proof does not prove the whole dollar envelope

Using UTF-8 prompt bytes is conservative for prompt-text BPE tokens. But `_est_tokens()` adds an unexplained fixed 1,500-token schema/wrapper allowance (`pipeline/llm_api.py:467-474`), while the actual serialized provider body, JSON schema, chat framing, and hidden overhead are outside that proof. More importantly, a token bound at the wrong tariff does not bound dollars.

Either use the provider tokenizer/count endpoint for the complete serialized request plus a documented margin, or derive and test a conservative full-envelope bound. Assert for every settled request that actual billed usage/cost is no greater than its reservation; otherwise latch and preserve the higher amount.

### B5. Campaign authorization is better but not atomic end to end

Unknown IDs now fail closed and normal attach validates provider/model/cap. However:

- each reservation transaction rechecks campaign cap/status but not provider, model, tariff hash, authorized run/scope, or lease holder (`pipeline/llm_api.py:250-282`);
- `call_api()` can be imported and used with no campaign, cap, or ledger, retaining the historical ad-hoc path (`:119-131,173-179,425-438,804-825`);
- `amend-campaign` mutates `purpose` in place (`:884-896`), despite `DECISIONS.md` describing an append-only amendment;
- purpose/owner decision/expiry are not protocol-bound;
- the schema has no owner signature/digest, status constraints, FKs, or attempt↔reservation uniqueness (`pipeline/migrate.py:327-364`).

Make campaign creation an owner-only preparatory operation; make ordinary `call_api()` fail without an active approved campaign (with an explicit test-only unsafe override); revalidate approval/provider/model/tariff/run scope/fence in the same `BEGIN IMMEDIATE` reservation transaction; record append-only signed authorization/amendment events; and terminally close/reconcile campaigns.

Campaign validation also occurs too late in normal setup: classification-run metadata is created before `attach_ledger()` validates active status, provider/model, and CLI cap. A typoed cap, wrong model, or closed campaign can therefore leave a phantom `running` run. Fully validate the campaign and acquire the lease before run creation, or atomically record a reason-coded setup failure. Reject non-finite/invalid caps and missing tariff snapshots at campaign creation.

### B6. Lease checks are not transactional fences

The in-memory `fence.lost` check before `call_api()` and bounded future submission are improvements. They do not protect every physical dispatch:

- `call_api()` may make up to four transport attempts without rechecking the lease between retries;
- a paused old process can wake after takeover but before its keeper updates the local event;
- reservation and attempt transactions carry no lease holder/generation;
- successful stores heartbeat and then write in a separate transaction;
- error-item stores are unfenced;
- after detecting loss, the old process can still unconditionally call `finish_classification_run()` and overwrite a successor's terminal counts/status;
- exceptions between lease acquisition and the executor's `try/finally` can leave the lease until timeout.

Use a monotonically increasing fencing generation. Check `run_id + holder + generation` in the same transaction as every reservation, pre-dispatch attempt, label/error write, attempt linkage, and terminal state transition. Check before each physical retry. Make terminal update a compare-and-swap. Wrap all post-acquisition setup in `try/finally`. Add real multiprocess suspend/takeover/retry/crash tests.

### B7. Attempt durability still has an admission gap

Reservation and pre-dispatch attempt insertion are separate transactions (`pipeline/llm_api.py:477-528,612-636`). A crash or insertion failure between them leaves a reservation with no attempt and no HTTP request. The pre-dispatch row initially lacks prompt hash, ordered snippet hashes, split path, endpoint, logical request ID, and fence token; those are added only after the future returns (`pipeline/classify.py:1028-1062`). A process kill is now charge-visible but the exact request may remain unrecoverable.

Atomically insert the reservation, logical request, and physical attempt admission row before HTTP. Include prompt hash, ordered input hashes, split path, endpoint, run protocol, campaign, and fence generation. Mark dispatch start/response/parse/result as explicit states. If pre-dispatch bookkeeping fails, release or reason-code the reservation because no network request occurred.

### B8. Remaining provider-provenance and secret-minimization limits

All 54 tracked attempts report returned model `gpt-5.6-luna` and no `system_fingerprint`. Record that a rolling alias plus absent fingerprint is not a weight-level snapshot; repeatability checks remain necessary.

Selected-provider `.env` loading is better, but unrelated credentials inherited from the parent environment are not removed. Launch from a scrubbed environment with one project-scoped, spend-limited key. OpenAI refusal text and Google's “no candidates” response excerpt can still reach exceptions/DB/JSONL (`pipeline/llm_api.py:761-765,789-796`); normalize those like other error bodies.

### Gate B acceptance criteria

- immutable hash-bound scoped/full target manifest and honest scoped status;
- complete tariff, empirically reconciled provider billing, and closed pilot campaign;
- missing/malformed usage conservatively charged, never $0;
- owner authorization/provider/model/tariff/scope/fence checked atomically per dispatch;
- every logical/physical request admitted durably with exact input identity before HTTP;
- transactional fence generation on all paid calls, writes, and terminal transitions;
- scrubbed single-key environment and documented rolling-model limitation;
- multiprocess and malformed-usage/tariff regression tests.

## Gate C — implement a real final two-grader gold study

### C1. The production gold path still does not exist

`annotate build` accepts raw scan/classification IDs and hard-codes `intended_use: calibration_only_never_release_validity` plus a CALIBRATION banner (`pipeline/annotate.py:245-299,341-370`). This honesty is a strength, but it means the commands in `GOLD_STUDY.md` and `WORKFLOW.md` cannot create a final validity sample.

Build the final study from an immutable release candidate—not live run IDs—and fail unless scan/classification/campaign/evidence/render/instrument gates pass. A calibration path and a final path should be different explicit modes, with final mode impossible until the release contract is valid.

### C2. Context/PDF/version chain of custody remains unsafe

For hits, `hits_and_path()` selects the current best row from mutable `files`, not the artifact used by the selected scan item (`pipeline/annotate.py:120-138`). `contexts.json` is reused merely because the pathname exists (`:304-321`). Current title/comments and fallback latest version can also introduce later-version text. The manifest contains a codebook version but no manual/prompt/schema hashes and no item artifact/context/PDF/packet hashes (`:284-299`).

This reproduces the mechanism behind the calibration round's version-skew case. Final packets must bind each sample row to release member, scan item, exact artifact ID/SHA/version basis, hit/evidence IDs, rendered PDF SHA/extractor version, context bytes/hash, taxonomy/manual/prompt/schema hashes, reviewer assignment/order, and final packet hash. Rebuild caches only on exact identity; never by existence.

The allocator manifest also contains strata and plant identities and is written beside reviewer packets (`pipeline/annotate.py:284-299`). Keep the unblinded allocator manifest in separate restricted storage; give each reviewer only a blinded, reviewer-specific assignment manifest and its hash. Embedded full PDFs require item-license/legal review and a reviewer confidentiality/no-redistribution agreement; a controlled fetch/view path is preferable where feasible.

### C3. Ingest remains fail-open and under-validated

JSON ingest warns and continues without a manifest, then checks global paper membership rather than reviewer assignment, exact version, codebook/hash, packet/export hash, or release (`pipeline/annotate.py:695-733`). The annotation schema lacks sample/release/manifest/assignment/stratum/probability/evaluability/COI/adjudication fields and a uniqueness constraint.

Make the manifest mandatory. Verify project, release, reviewer, assignment, item/version/artifact, codebook bundle, packet hash, export hash, and one response per assigned item in a single transaction. Reject stale, duplicate, unassigned, wrong-reviewer, or hand-edited identities. Namespace browser storage by packet hash so regenerated packets cannot silently restore old labels.

### C4. Shared double-coding and adjudication are not implemented

Reviewer orders are independently shuffled (`pipeline/annotate.py:268-282`). If each reviewer labels their first 100–150 positions, their overlap is far smaller than 100–150. Manifest a deliberate shared stratified subset and separate single-coded assignments.

The current agreement command selects the first two labels and computes verdict-only raw agreement/kappa (`pipeline/annotate.py:915-943`). It does not bind pairs, handle non-evaluable outcomes, compute axis metrics/CIs, create adjudication records, or implement the anchoring-control sample. The protocol also needs a named third blinded adjudicator; a two-grader design cannot supply someone who produced neither human label for human–machine disagreements.

### C5. The study is not powered for all claimed axes

The sampler has POS/FLAG/NEG strata but no impact or R4-hard stratification (`pipeline/annotate.py:194-242`). POS n=150 can estimate overall precision near 0.9 to roughly ±5 percentage points; it cannot produce confirmatory precision for five impact classes, 17 categories, rare zero/undetermined cases, and all versions/eras/subfields.

Prespecify primary outcomes and pass thresholds. Oversample rare impact/R4-hard/version strata with recorded inclusion probabilities or label per-impact/category results exploratory. Record COI, evaluability reason, PDF opened/version confirmed, search duration/process, plant discovery, and adjudication state.

### C6. Estimators remain prose, not frozen code

`GOLD_STUDY.md:143-154` describes two-phase weighting, bootstrap uncertainty, corrected prevalence, and missingness bounds, but no executable analysis implements them. Before final labels:

- implement and test Horvitz–Thompson/two-phase expansion with actual inclusion probabilities;
- separate precision, false-omission within each sampled arm, and frame sensitivity;
- handle `UNCLEAR`/`INSUFFICIENT_EVIDENCE` as reason-coded non-evaluable outcomes with bounds;
- bootstrap sampling, annotation, and adjudication as prespecified;
- report acquisition/scan missingness separately rather than pretending gold repairs it;
- freeze a synthetic fixture with known truth and expected estimates/CIs.

### C7. Gold cannot identify the full 133,279-paper v1 frame

The current primary frame has approximately 85,742 scan-complete v1-path papers of 133,279, with 10,512 explicit v1 and 75,230 inferred-single-version cases. Roughly 47.5k are outside scan-complete membership. Missingness is outcome-related because multiversion acquisition prioritized previously flagged papers.

A gold sample drawn from scan-complete release members can validate labels for that selected observed frame. It cannot make the unacquired tail representative or turn selected-frame sensitivity into full-frame sensitivity. Resolve the open decision in `DECISIONS.md:182-187`: publish a selected-frame estimand, partial-identification extrema, or a recent fully covered period. Keep explicit-v1 and inferred-v1 strata separate.

### Gate C acceptance criteria

- final builder consumes one immutable release candidate and exact artifact bytes;
- fail-closed manifest/export/ingest with packet and assignment hashes;
- shared stratified double-coded subset, named graders, and third blinded adjudicator;
- overlapping R5 human fields and powered/weighted hard-case strata;
- append-only first-pass/adjudication records with COI/evaluability/process fields;
- frozen executable estimators, CIs, bounds, thresholds, and synthetic end-to-end test;
- public estimand explicitly limited to what the selected acquisition frame identifies.

## Gate D — make a scientific release immutable and statistically honest

### D1. Freeze still allows an unvalidated release

`report --freeze` requires clean/pinned API runs and complete classification, but grounding/render gates are optional, partial/arbitrarily selected scans are allowed, and there is no required gold result, campaign closure, provider-console reconciliation, attempt/spend invariant audit, target-manifest validation, or coverage threshold (`pipeline/report.py:61-124,441-450`). The generated frozen text nevertheless says “validity gates were enforced.” If no gates were requested, that sentence is false.

Define a release policy object with required gates and thresholds. Freeze must reject scoped classification runs, unknown selection manifests, partial coverage beyond the declared policy, unresolved terminal items, missing rendered evidence, unreconciled campaigns, absent gold/adjudication, failed estimator thresholds, and dirty/non-recoverable builder code.

### D2. A release is a digest of mutable queries, not immutable data

The `releases` row stores counts, three set hashes, report hash, and pointers to live runs (`pipeline/report.py:456-494`; `pipeline/migrate.py:254-263`). It does not materialize frame/member/version-basis/artifact/label/evidence/render/gold rows. The schema has no immutability triggers. A later database mutation can regenerate different output under the same nominal release.

Materialize a content-addressed release bundle containing the complete member preimage and all analysis rows/identities needed to reproduce every aggregate. Hash each artifact and a top-level manifest; record generator commit/tree, environment/SBOM, model protocol, campaign reconciliation, taxonomy bundle, gold project/analysis hash, and correction lineage. Make released rows append-only at the database level.

### D3. Freeze records generator provenance too late

The report is written before `db.code_commit()` is inserted into the release (`pipeline/report.py:452-493`). With the default tracked `reports/report.md`, generating output normally dirties the worktree, so the release can record a `-dirty` builder state. Capture and validate clean HEAD/tree before any output; build in an empty staging directory from that exact tree; then atomically materialize and insert the release.

### D4. The site is not a release consumer

`pipeline.build_site` accepts raw scan/classification run IDs and always emits `unreleased_exploratory`; there is no `--release` (`pipeline/build_site.py:578-588`). It reads live tables. Build one release-only path that verifies the top-level manifest and writes into an empty staging directory. The real public site must be byte-for-byte an artifact named by the release, not a later query over its source runs.

### D5. R5/site/report quantities are currently misleading

Until A6 is wired, the report's “contributing” count subtracts only scalar-max zero/undetermined and can classify a mixed contributing+zero paper incorrectly for the zero slice (`pipeline/report.py:415-427`). The site headline pools all `author_use` as “AI assistance” and exposes only scalar impact. Export all overlapping R5 states and give the primary headline a precise construct name such as “papers disclosing attempted or contributing generative-AI/LLM tool use.” Put contributing, explicit-zero, and undetermined counts alongside it.

### D6. Statistical presentation remains exploratory

Wilson intervals are shown as “sampling uncertainty” even though the displayed selected cohort is close to a census of the acquired frame (`pipeline/build_site.py:469-480`). They do not cover acquisition selection, version mixture, classifier error, dependence over time, or codebook uncertainty. State the superpopulation model if intervals are retained, otherwise present descriptive ratios and make measurement/missingness uncertainty primary.

Fine-grained daily/weekly/subfield/provider/category/impact analyses remain unvalidated and multiple. Before scientific release, prespecify primary time granularity, model autocorrelation/composition where inferential claims are made, use shrinkage/multiplicity control for comparisons, and call all other panels exploratory.

### Gate D acceptance criteria

- release policy with mandatory evidence/gold/campaign/coverage/selection thresholds;
- materialized content-addressed member and analysis preimages, database immutability, signed/checksummed manifest;
- clean generator tree captured before staged deterministic output;
- report/site consume only a release ID/bundle;
- overlapping R5 quantities and precise construct names in every artifact;
- declared population/superpopulation estimand and uncertainty components;
- correction/supersession lineage and byte-reproducible double build.

## Gate E — public repository, privacy, disclosure control, and deployment

### E1. Small-cell disclosure control remains a public-data blocker

`suppress_small()` is applied only to selected tool/provider tables (`pipeline/build_site.py:157-165,379-381,443-453`). Categories, impact, and location remain unsuppressed. Exact daily/weekly/subfield-month series are embedded in JavaScript/JSON (`:320-346,517-520`). The current tracked preview contains one explicit category singleton; its embedded series contains 601 positive 1–2 cells, including 417 singletons. Overlapping 3-month/1-year/3-year views enable complementary subtraction.

`noindex` and `do_not_cite` are warnings, not access control. Before any real-data hosting or public clone, adopt one formal disclosure-control policy with minimum denominator and numerator, primary and complementary suppression, coarsened time periods, rare-name rollup, and differencing-attack tests across every HTML/JSON/Markdown/CSV/JS view. Apply it before serialization, not just to visible charts.

### E2. Working-tree quarantine improved; current prose and Git history still conflict with it

Ordinary reachable history still contains deleted `results/*`, `reports/awesome_validation.*`, spotchecks, an instance inventory, and long source excerpts/personal contact data. `PITCH.md:9-14` still contains identifiable pilot IDs and a verbatim paper excerpt; `PITCH.md:59-80` promises both open annotations and aggregate-only output. `DESIGN_PLATFORM.md:10-17,63-67,114` still proposes public per-paper labels/explorer/ODC-BY, conflicting with `DECISIONS.md:176-180`. `pipeline/aws/math_ids.txt` is a 1.8 MB per-paper ID list requiring an explicit frame-manifest/license carve-out or exclusion.

No remote or tags are configured in this clone, which is a valuable opportunity—not proof the history was never shared. Preserve a private canonical archive, then create an allowlisted clean public export or carefully rewrite a disposable clone. Run full-history secret, personal-data, paper-ID, excerpt, local-path, and infrastructure scans; verify a fresh clone/object inventory before first public push. Replace real development cases with synthetic/deidentified cases and maintain an explicit publication matrix for code, aggregate data, frame manifests, per-paper labels, excerpts, gold records, and hashes.

### E3. Provider governance remains an explicit pre-run/publication gate

Removing arXiv IDs from prompts and using `store:false` are good. Snippets are still searchable/re-identifiable, and the scanner processes every text-like archive member before rendered/include-graph validation (`pipeline/scan.py:82-140`), so unused/residual TeX may reach the provider.

Current official OpenAI [data-control documentation](https://developers.openai.com/api/docs/guides/your-data#default-usage-policies-by-endpoint) says API data is not used for training absent opt-in, while default abuse-monitoring may retain content; `store:false` is not itself a zero-data-retention agreement. Before the full corpus run, record organization/project training-sharing state, ZDR/MAM eligibility/status, DPA, region/transfers, subprocessors, retention/deletion, breach/incident route, and approved data categories. Prefer rendered/reachable evidence and minimum spans, or explicitly approve/document residual-source processing.

Define retention/access/deletion for snippets, raw responses, attempt logs, annotation packets, PDFs, databases, WALs, and backups. Normalize remaining refusal/no-candidate provider text before logs.

### E4. Local restricted-data security is unverified

`.env`, databases, backups, corpus/logs, and annotation material appear as mode 0777 on the Z: DrvFS/9p mount. Those POSIX bits neither prove nor disprove Windows access control. Verify actual Windows/inherited share ACLs, BitLocker/encryption, sync/share targets, backups, and account access. Prefer a protected native filesystem and credential manager; launch with one scrubbed provider key.

Prospective parsed submitter storage is removed, but raw OAI archives retain the field and the database still has 235,323 populated legacy submitter values. If there is no documented purpose/legal basis, purge them, `VACUUM`, and expire/rotate backups; otherwise classify and protect the data with a retention schedule.

### E5. Licensing, corrections, and governance remain incomplete

The MIT software scope is clear, but “future released aggregates are intended as CC BY” is not an operative license for current or future data. Add:

- release-level aggregate data license and source/license matrix;
- data dictionary/schema, checksums, CITATION.cff, versioned DOI/release metadata;
- privacy/data-governance notice (controller, purpose, basis, processors, retention, rights, incident contact);
- SECURITY.md and vulnerability reporting;
- correction, appeal, takedown, and immutable supersession policy;
- governance/roles/COI, reviewer confidentiality/data-deletion agreement;
- CONTRIBUTING, CODE_OF_CONDUCT, and changelog;
- explicit funder role/non-role in study design, analysis, publication, and provider choice.

Remove the PITCH excerpt, which contradicts `LICENSE:29-31` (“excerpts ... never redistributed”). Sign the release manifest/tag if feasible. Public audit/version text is stale: README calls review 7 current while site copy says six rounds. Generate it from release metadata rather than hand-maintaining it.

### E6. CI and deployment do not enforce the claimed release process

`.github/workflows/ci.yml:1` claims tests plus site build, but it only installs and runs pytest (`:16-17`). Action SHAs are pinned, which is good. Add:

- `permissions: contents: read`, checkout `persist-credentials:false`, timeout and concurrency cancellation;
- hash-locked dependencies, lint/type/security/dependency/license/SBOM checks;
- migration-from-empty and fixture end-to-end scan/classify/render/gold/release tests;
- deterministic double site build and release-manifest verification;
- public-boundary/full-history secret and disclosure-control/differencing tests;
- HTML/link/schema/CSP/header/browser/accessibility checks.

There is no deployment workflow, so this is a pre-deployment gap rather than a live vulnerability. Deploy only the exact immutable release artifact through a protected environment with manual approval, least-privilege token, preview/rollback, and host headers (CSP, `nosniff`, referrer, frame, permissions, HSTS as appropriate).

### E7. Accessibility and public reach still need a release pass

Static, tracker-free delivery, table alternatives, and focus styles are strong foundations. Remaining issues include chart SVGs with `role=img` but no chart-level accessible name/description, muted 12.5 px text at roughly 3.41:1 contrast, mouse-oriented tooltips, no main landmark/skip link, and no robust no-JS fallback for dynamic series. Run automated and manual keyboard, screen-reader, mobile, high-contrast, reduced-motion, and no-JS checks.

After scientific and governance gates—not before—add canonical/OG/social image/favicon, sitemap/robots release switch, stable methods/validation/privacy/corrections/contact pages, downloadable disclosure-controlled aggregate/schema/checksum bundle, CITATION/DOI, and a media guide that explicitly rejects causal inference and misconduct interpretation.

### Gate E acceptance criteria

- comprehensive primary/complementary disclosure control with reconstruction tests;
- clean allowlisted public tree/history and reconciled publication policy;
- provider/privacy/local-security/retention decisions documented and enforced;
- operative aggregate license, governance, correction, security, and citation package;
- deterministic release CI and protected exact-artifact deployment;
- accessibility, security-header, no-JS, link, and mobile pass;
- public messaging generated from release metadata and limited to validated claims.

## Review-9 finding status summary

| Iteration-9 area | Round-10 status |
|---|---|
| Non-author catalytic machine/human parity | **Fixed and tested** |
| R4 precedence | **Improved, but construct contradiction remains** |
| Exact v2.4 owner sign-off | **Explicitly pending** |
| OpenAI inference effort | **Fixed (`medium` explicit)** |
| Unknown campaign IDs / cap in protocol | **Fixed on normal path** |
| Campaign authorization scope | **Partial: mutable purpose; not atomically rechecked** |
| Hard budget | **Regressed/new evidence: cache-write tariff omitted; missing usage can settle $0** |
| Scoped adherence provenance | **New P0: target outside protocol; false `complete` semantics** |
| Lease fencing | **Improved but non-transactional and retry/final-status races remain** |
| Split/re-ask prompt provenance | **Substantially fixed** |
| Pre-dispatch attempts | **Substantially fixed; admission/linkage atomicity remains** |
| Selected provider key / error bodies | **Improved; inherited keys/refusal paths remain** |
| R5 multi-state rollup | **Producer fixed; report/site/human consumers not fixed** |
| Final release-bound gold | **Not implemented** |
| Immutable release/site consumer | **Not implemented** |
| Small-cell and Git-history publication boundary | **Unchanged blocker** |
| Provider/privacy/governance/licensing/CI/deploy/a11y | **Mostly unchanged blockers** |

## Prioritized next actions

### Before any full paid v2.4 call

1. Resolve active invocation versus incorporation in R4; align human and machine wording.
2. Wire overlapping R5 states through human annotation, report, site, export, and tests.
3. Run the frozen two-human-plus-Luna comprehension/repeatability exercise; record exact owner sign-off.
4. Make the full/scoped target a persisted preimage+hash in protocol; reject scoped runs from report/freeze.
5. Add full Luna tariff classes, validate usage, conservatively handle unknown usage, reconcile and close the pilot campaign.
6. Put campaign/provider/model/tariff/scope and lease generation in each reservation/write transaction; add takeover/retry fault tests.
7. Atomically admit reservation+logical request+attempt before HTTP, with exact prompt/input identity.
8. Complete provider/data-governance approval and run from a scrubbed least-privilege key environment.

### Before final gold begins

1. Materialize one release candidate with artifact-exact membership.
2. Implement final (not calibration) packet build, signed/hash-bound reviewer assignments, and fail-closed ingest.
3. Prespecify a shared stratified double-coded subset and recruit/name the second grader and third blinded adjudicator.
4. Freeze R5-capable human fields, impact/hard-case sampling, estimators, CIs, missingness bounds, and pass thresholds.
5. Pass a synthetic end-to-end packet/export/ingest/agreement/adjudication/estimation test.

### Before public repository/site or scientific claim

1. Implement materialized immutable release and release-only site generation.
2. Apply comprehensive primary/complementary suppression to every artifact and pass reconstruction tests.
3. Publish from a clean allowlisted export/history; reconcile PITCH/DESIGN/LICENSE/DECISIONS.
4. Complete privacy, security, governance, licensing, corrections, citation, and reviewer policies.
5. Harden CI, deterministic packaging, protected deployment, headers, accessibility, and rollback.
6. Release only the estimator/claim supported by the selected v1 frame and adjudicated gold; keep the full-frame acquisition uncertainty explicit.

## Bottom line

Round 10 shows real engineering progress: the supported v2.4 adherence path now has valid structured labels, exact attempt/reservation linkage for completed requests, clean protocol hashes, explicit inference effort, and much better failure provenance. The new run also did exactly what a good preflight should do—it exposed defects before a large spend.

Those defects are material. The current instrument has one unresolved construct contradiction; the scoped run is mislabeled complete and not reproducibly scoped; the dollar cap undercounts an actually used cache-write tariff and can treat missing usage as free; and lease/campaign authority is not transactionally fenced. Fixing these is a prerequisite to the full classification run, not release polish.

Even after the full run, classification completion alone will not validate a public result. Final gold, release materialization, disclosure control, governance, and deployment remain distinct gates. Keeping those gates separate is the clearest path to a result that is scientifically defensible, technically reproducible, ethically proportionate, and credible to the public.
