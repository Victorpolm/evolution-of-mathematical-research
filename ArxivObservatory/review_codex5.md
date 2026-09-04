# ArxivObservatory repository review — iteration 5

**Audit snapshot:** Git commit `3cb48c86ba01f777cb071e8d2b8fb04ac1efaddb`, tree `ca4404dbe1884648abc48dd360fb68aca54d075e`, 2026-08-11 16:41 CEST. The worktree was clean at the beginning and end of the audit, before this review file was added.

**Primary deltas reviewed:** `pipeline/llm_api.py`; API/Codex dispatch, validation, and JSON repair in `pipeline/classify.py`; review-4 triage commit `7ee7516`; limitations-card commit `d1d2c47`; and the dated owner log in `DECISIONS.md`. I also re-reviewed the rest of the repository, current generated artifacts, local run ledgers, the preliminary gold-study materials, acquisition and cloud scripts, tests, CI, specifications, public communication, and governance documents.

**Audit boundary:** read-only except for creating this review. I did not stop or start the live refill, invoke a model or external API, mutate the database/corpus, contact arXiv, operate cloud resources, or deploy the site. The database and refill log were actively changing during the review, so empirical counts below are explicitly point-in-time observations, not a frozen data release.

## Executive verdict

The new changes are substantial and mostly point in the right direction. In particular:

- the direct API backend removes the agent CLI's repository/tool access and structurally sends one paper per request;
- the owner-decision log makes deliberate risk choices much easier to distinguish from accidental drift;
- the scanner can now select version-1 artifacts;
- release freezing rejects several previously accepted unsafe states;
- fuzzy PDF matches are no longer treated as exact rendered evidence;
- the public site is much more candid about its exploratory status, source-version mixture, and run provenance;
- the stale public dashboard and distribution ZIP have been removed from the publish root;
- 84 tests pass, and the normalized evidence ledger is in strong condition.

These improvements do **not yet establish a scientifically validated or reproducible release**. The current `2.1%` site remains an exploratory inspection artifact derived from a partial dirty scan, a dirty non-isolated Codex run, mostly unknown source versions, no human annotations, no final gold study, no render requirement, and no frozen release.

Four issues should be treated as immediate operational or release blockers:

1. `DECISIONS.md` says the live v1 refill automatically pauses after the approved flagged phase, but the implementation has no such pause and the running job was configured for the full 65,708-item queue.
2. The API token guard checks spending only after paid responses and pre-submits all work, so it cannot enforce the stated `$50/provider` pilot budget.
3. Freeze and resume contracts still admit protocol substitution: an API run can be resumed through Codex, the approved backend is not freeze-gated, and two unpinned/unknown provenance forms pass current checks.
4. The new JSON-repair regex silently corrupts common TeX commands beginning with valid JSON escape letters while allowing the classification to remain `ok`.

My recommendation is therefore:

- keep calling the current website a **public inspection snapshot**, never a prevalence estimate or scientific release;
- intervene operationally before the v1 refill reaches the unapproved tail;
- repair the paid-call scheduler, parser, resume identity, and freeze gates before another full model run;
- build the final human validation sample from one exact, immutable release;
- publish scientific claims only from that release, with a deterministic site build and complete governance package.

The owner can deliberately accept more publication risk than this recommendation. `DECISIONS.md` now records that choice well. The remaining requirement is to make the chosen boundary technically accurate, machine-enforced, and inseparable from every exported number.

## Immediate operator action: the documented v1 pause is not implemented

This is the most time-sensitive finding because the job appeared to be live throughout the audit.

`DECISIONS.md:8-13` says:

- fetch the roughly 9,100 scanner-flagged papers first;
- automatically pause at that phase boundary; and
- do not enter the roughly 56,000-paper tail until arXiv coordination is complete.

The implementation does something else:

- `pipeline/fetch.py:180-190` orders flagged jobs first and then appends all unflagged jobs to the same list;
- `pipeline/fetch.py:228-247` iterates through that entire list, with no boundary sentinel, stop, confirmation, approval ID, or phase-specific maximum;
- `WORKFLOW.md:43-48` documents this `--flagged-first` command as though it implements the decision.

At one point in the audit the selector returned 58,980 remaining targets: 2,253 flagged followed by 56,727 tail targets. `corpus/v1refill.log` declared a 65,708-item queue and was progressing at roughly 6.7k/65.7k with an estimated six days remaining. The database's `export-v1` count and WAL advanced during inspection. The running process appears to predate the new JSONL attempt logger, and no `corpus/logs/v1refill_attempts.jsonl` existed, so its failed/404 attempts are not durably represented by the new code.

I did not stop the process because that would be an operational mutation outside this review. The owner/operator should independently verify and enforce the boundary now.

Required implementation:

- make `--flagged-only` the safe, finite command;
- materialize and hash the exact target manifest before starting;
- hard-stop when that manifest is exhausted;
- require a separate, conspicuous command such as `--include-unflagged-tail --approval-id ...` for the tail;
- persist run ID, target set, requested version, channel/URL, attempts, HTTP outcome, byte/hash result, timestamps, approval, and terminal reconciliation;
- exit nonzero if any target lacks a terminal reason-coded outcome.

Priority ordering is not a pause control. Until this is fixed, `DECISIONS.md` and `WORKFLOW.md` overstate the safeguard.

## Decision-to-enforcement audit

`DECISIONS.md` is one of the most useful additions in this iteration. It should now become the source for automated acceptance tests rather than remaining prose alone.

| Owner decision | Current status | Evidence and needed change |
|---|---|---|
| Pause v1 refill after flagged phase | **Contradicted** | `fetch.py` only sorts flagged first and then processes the tail. Add a hard finite target boundary and an explicit separately approved tail command. |
| v1 is the primary estimand | **Partially implemented** | A v1 artifact scanner exists, but no `texv1-*` run exists; exact selection provenance, frozen metadata/category scope, missing-v1 policy, and per-version licences are absent. |
| NULL-version S3 rerolls remain a separate stratum and are never coerced to v1 | **Contradicted by implementation** | `scan.py:290-327` infers version 1 for NULL-version S3 artifacts when current metadata shows only one version. Either amend the decision to allow a documented `v1_inferred_single_version` stratum or do not coerce it. |
| Public inspection before second-order corrections, with prominent limitations | **Deliberate but only partly contained** | Banner and card exist, but results precede the full limitations card, JSON can be detached from caveats, and the card incorrectly presents coverage extrema as bounds on true prevalence. |
| Direct non-agentic API, one paper per request | **Implemented for new API calls; not release-enforced** | API mode has no tools and forces one-paper isolation. Freeze still accepts isolated Codex, resume can switch backend, and the current main result still comes from non-isolated Codex. |
| Up to $50 per OpenAI and Anthropic provider for pilots | **Not implemented** | The current global token counter is post-hoc, process-local, model-agnostic, not priced in dollars, and cannot stop queued calls. |
| Current `gold-3yr-prelim` is calibration only | **Correctly documented; artifacts incompletely marked** | `GOLD_STUDY.md` is candid, but packet/manifest names still say “gold,” and the immutable artifacts lack a prominent never-use-for-validity status. |
| Final gold comes from exact release membership | **Not implemented** | Annotation build accepts run IDs, not a release, and re-reads mutable files/metadata. |
| Aggregate-only public outputs | **Visible site complies; repository does not** | Tracked `results/*` and `reports/awesome_validation.json` retain paper IDs, excerpts, paths, and judgments. Older expressive files remain in Git history. |
| Static tracker-free site | **Implemented** | Preserve this strong privacy and resilience choice. |
| math-ph inclusion | **Open** | Current `LIKE 'math%'` includes math-ph. Resolve before any frozen release and encode the exact category predicate in the release manifest. |
| Second reviewer, tail route, full-run backend | **Open** | These are appropriately listed. Add owners, due dates, evidence, and machine-testable exit criteria. |

## P0 — release and validity blockers

### P0-1. The current site is an unreleased exploratory artifact, not a scientific estimate

The generated artifacts candidly disclose many of their limitations:

- scan `tex-20260810T205113` is `partial`, built from `f08502f-dirty`;
- classification `cls-20260810T211610` is complete but built from `f08502f-dirty` with `isolate=0`;
- report gate is quote grounding only, not rendered evidence;
- the headline is 2,799 model-positive papers among 131,310 scanned papers (`2.1%`);
- 124,741/131,310 scanned papers, about 95%, have unknown effective source version;
- the database has zero annotations and zero releases.

The top banner and detailed report provenance are real improvements. They do not correct the measurement. The headline still derives from an old agentic, cross-paper batched run and is not calibrated against an appropriately sampled human reference set.

The limitations card appears after the headline, rate chart, trend, subfield, tool, category, location, provider, and agentic panels (`site/index.html:138-268`; card thereafter). A screenshot or machine consumer can easily separate a result from the caveat. The JSON export is even easier to reuse without context.

If the owner retains the public-inspection decision, the minimum containment should be:

- put a compact limitations block immediately before the first number and repeat its status in every chart/table download;
- add `release_status: "unreleased_exploratory"`, `do_not_cite: true`, limitation codes, exact run statuses, gate status, render-valid count, unresolved counts, and correction/contact link to `site/data/disclosures.json`;
- add `noindex` and a visible exploratory watermark while no release exists;
- suppress fine-grained rankings and provider/tool comparisons until their axes are human-validated;
- never describe the raw percentage as the population disclosure prevalence.

Prefer a synthetic demonstration until the first gated release.

### P0-2. The limitations card states an invalid prevalence bound

`pipeline/sitetext.py:162-165` and the generated site say the overall rate is bounded between `2.1%` and `3.6%`. These are **coverage-only extrema of the raw classifier-positive rate**, obtained by treating all unresolved papers as negative or positive while accepting the model labels as truth.

Because precision and sensitivity are explicitly unknown, true disclosure prevalence is not identified by that interval. False positives can lower it below 2.1%; false negatives among scanned negatives can raise it beyond the coverage-only upper endpoint. The preliminary Markdown report correctly notes that classifier and version errors are additional.

Replace the site wording with something like:

> Conditional on treating the current model labels as correct, the raw classifier-positive rate is 2.1% if all unresolved papers are non-positive and 3.6% if all are positive. Human measurement error and source-version uncertainty are not included, so this is not a bound on true prevalence.

The site formula in `pipeline/build_site.py:413-420` also omits pending and classification-failed papers from its unresolved count. That happens not to change the present output because those counts are zero, but the generator accepts partial runs and is wrong generically. Reuse the report's exact reason-coded unresolved partition.

### P0-3. Most headline positives are not certified as rendered evidence

Fuzzy-match demotion is correctly fixed: 241 historical fuzzy matches are now `rendered_fuzzy`, and `--require-rendered` accepts only exact rendered evidence. Preserve this.

The current public snapshot does not enable that gate. Among the 2,799 grounded headline-positive papers at audit time:

- 901 had at least one exact rendered quote;
- 151 had only fuzzy rendered matches;
- 1,741 had only unknown-version evidence;
- 6 had only other non-rendered, short-quote, or PDF-error states.

Thus 1,898/2,799, or 67.8%, lacked exact rendered certification. This is a first-order construct and privacy limitation, not a minor footnote. It should appear prominently in the HTML and JSON.

The card also says unknown-version bulk text is “some later revision.” Unknown means it may be v1 **or** later; the direction is not known. Use “unknown revision, potentially later.”

### P0-4. API budget enforcement cannot stop queued spending

The new backend has an optional `--max-total-tokens`, but it does not implement the owner-approved `$50/provider` boundary:

- `pipeline/llm_api.py:92-101` accounts only after a provider has returned and incurred cost;
- `pipeline/classify.py:514-516` submits all batch futures at once;
- a `BudgetExceeded` exception is handled like an ordinary completed batch failure at `classify.py:519-525`;
- already queued futures continue to send calls and discover the exceeded budget only after their own paid responses;
- totals are process-local and reset on resume;
- input and output tokens are added without provider/model price differences;
- usage and cap are printed but not persisted in the run manifest;
- missing usage is treated as zero;
- ambiguous transport failures may be retried even if the provider processed and billed the request.

This is a monitoring counter, not a hard budget.

Required design:

1. materialize the exact pilot request set before dispatch;
2. maintain durable provider-specific request, input-token, output-token, retry, and cost ledgers;
3. snapshot the applicable price schedule and currency;
4. reserve estimated input plus the configured maximum output before each call;
5. submit incrementally with bounded in-flight concurrency and a shared stop event;
6. cancel work that has not begun when the cap is reached;
7. require an explicit approval record to raise each provider cap;
8. reconcile console/provider billing after the run.

As a time-stamped reference, OpenAI's official model page listed `gpt-5.6-luna` at $0.20/million input tokens and $1.20/million output tokens when checked on 2026-08-11. Prices are mutable, so the run must store the exact price snapshot rather than relying on a live page. See [OpenAI's gpt-5.6-luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

### P0-5. Freeze hardening has direct bypasses

Commit `7ee7516` genuinely fixed several previous defects: freeze now rejects an empty consumed-run list, dirty run stamps, `isolate=0`, and incomplete classification; it performs critical pending/failure checks before writing the report (`pipeline/report.py:88-113,356-369`).

The remaining bypasses are material:

- model pinning checks `.endswith("(unpinned)")`, but `classify.py:453-455` constructs `codex-default(unpinned)@<effort>`, which passes;
- `db.code_commit()` returns literal `unknown` on Git failure, and this truthy string passes the “dirty/unknown” check;
- freeze checks `isolate`, not `backend`, so an isolated Codex agent run passes despite the decision to use direct API;
- arbitrary mutable model aliases pass as pinned; the returned effective provider model is discarded;
- partial scans with arbitrarily low or selected coverage can freeze;
- grounding and rendering gates are optional;
- there is no required acquisition manifest, version completeness rule, gold metric, human-error threshold, approved provider/data-processing state, licence inventory, or exact environment identity;
- the release builder's own worktree may be dirty; only producer-run stamps are checked;
- the release stores counts and set/report hashes over mutable live tables, not immutable materialized membership;
- the site still consumes raw run IDs rather than a `release_id`.

Reject `unknown`, parse the unpinned state as a structured field, and verify full commits exist. Freeze should consume a single exact acquisition/scan/classification/render/gold protocol; require the approved backend; enforce declared coverage/missingness and version policies; materialize every release member and artifact; and generate the site only from that immutable release.

### P0-6. Resume can silently mix API and Codex protocols

`pipeline/classify.py:460-479` compares model label, prompt hash, isolation, taxonomy, and scan-run list when resuming. It does not compare:

- stored backend/provider;
- code commit;
- endpoint/API version;
- native schema and decoding contract;
- effective request parameters;
- reasoning/temperature settings;
- batch and worker configuration;
- token/cost budget;
- provider data-handling mode.

An isolated Codex run can therefore resume through API, or an API run through Codex, if its model label and other checked fields match. The run continues to advertise only its initial backend and clean/dirty stamp. The input hash also omits backend and effective API protocol.

This is already visible at a lower level: the Anthropic pilot's stored `limit_batches=5` does not explain all nine calls/papers seen across resumptions because invocations are not recorded separately.

Create an immutable `classification_invocations`/`model_attempts` ledger and hash the entire effective protocol. Either forbid heterogeneous resumes or create a new superseding run. Treat only `status='ok'` items as done; current `status NOT LIKE 'error%'` also makes invalid rows permanently non-retryable.

### P0-7. Regex JSON repair silently corrupts TeX

`pipeline/classify.py:140-154` tries to repair unescaped backslashes by doubling only backslashes whose next character is not one of JSON's legal escape initials (`"\\/bfnrtu`). This fails exactly where TeX and JSON overlap.

A read-only diagnostic demonstrated:

- `\beta` becomes a backspace followed by `eta`;
- `\frac` becomes form-feed followed by `rac`;
- `\text` becomes tab followed by `ext`;
- `\newcommand` begins with a newline;
- `\nabla x` can decode to a newline plus `abla x` and, in a matching context, remain `quote_grounded=true`;
- `\usepackage` remains a parse failure because `\u` is reserved but incomplete;
- only an illegal JSON escape such as `\Gamma` takes the intended repair path.

The current test covers `\Gamma` and therefore misses the dangerous cases. A corrupted quote can be stored as `status='ok'` because grounding is not a validity requirement and the later release gate is optional.

Do not repair malformed model JSON with a regex. Prefer provider-native schema-constrained output and reject malformed responses. If a backward-compatibility repair remains, it needs a real JSON lexer and exhaustive tests for every JSON escape initial, surrogate/Unicode cases, fences, trailing text, duplicate keys, and TeX commands. Persist every failed raw attempt rather than overwriting it during retry.

### P0-8. The v1 scan path is useful but cannot yet prove its estimand

`pipeline/scan.py:290-338` fixes the previous complete disconnect: it can select explicit v1 artifacts and infer version 1 for a metadata-single-version bulk artifact. Read-byte SHA verification remains strong.

No v1 scan has actually been run. More importantly, the run ledger records only worker count, number of jobs, and resource budgets (`scan.py:218-226`). It does not record:

- `--v1-corpus` versus legacy corpus mode;
- full-frame versus `--flagged` selection;
- months, category predicate, or prior scan used to define flagged papers;
- exact artifact IDs, channels, paths, and hashes selected;
- explicit-v1 versus inferred-single-version basis;
- metadata snapshot hash/cutoff;
- tie-breaking policy;
- acquisition-manifest identity.

This opens a selected-denominator trap: a flagged-only, prior-positive-enriched scan can be clean and complete, yet `report.py` accepts arbitrary scan coverage and could report it as prevalence. `--flagged` is an acquisition/calibration subset, never a prevalence denominator.

The NULL-version inference also contradicts the absolute wording in `DECISIONS.md`. At audit time, about 102,000 metadata-single-version papers could receive inferred v1 status. The inference is scientifically defensible if current metadata truly shows a sole v1, but it must be a distinct, frozen stratum, not silently identical to fetched v1.

Further selection details need resolution:

- 919 version-1 papers had more than one explicit artifact with differing hashes; equal-priority choice should be deterministic and recorded by artifact ID;
- 263 single-version papers had an outcome-conditioned `gcs-pdf` v1 artifact plus a NULL-version S3 source, and explicit-first selection can choose the PDF based on prior render-positive work;
- category membership currently comes from mutable latest metadata;
- withdrawn/missing-v1 handling and the metadata cutoff are not preregistered;
- current `LIKE 'math%'` includes math-ph, an explicitly open decision;
- per-version arXiv licence is not stored.

Build and hash a complete scan job manifest with inclusion reason, artifact ID/SHA, exact version basis, category-at-cutoff, and expected terminal status before launching `texv1-*`.

### P0-9. The final gold-study path still does not consume a release

This iteration correctly reframes `gold-3yr-prelim` as a calibration/pilot that must never produce release-validity metrics. Optional cohort/category filters and JSON membership checks are useful partial fixes.

The production contract still does not match `GOLD_STUDY.md`:

- `annotate.py` claims to draw from a frozen release, but the CLI has no `--release`;
- cohort/category dates and evidence gates are optional;
- examples in `WORKFLOW.md:75-79` and `GOLD_STUDY.md:132-149` omit the new cohort filters;
- the build does not call `report.run_info` or verify run compatibility, completeness, clean code, isolation, backend, grounding, or rendering;
- positive selection is not scoped through evidence from the chosen scan run;
- contexts are re-extracted from mutable `files.path`, not the scanned artifact;
- a NULL scan version can fall back to the current latest PDF;
- existing `contexts.json` is reused based on file existence alone;
- the manifest lacks release, item, evidence, version, artifact, context, PDF, and packet hashes.

The current local manifest still represents the entire scan universe, not the report cohort, and it contains 500 calibration items. There are zero ingested annotations. Packet names still say `gold-3yr-prelim` without a prominent immutable “CALIBRATION ONLY — NEVER RELEASE VALIDITY” marker.

Final gold must accept exactly one `release_id`, materialize its eligible item/evidence IDs, and fail closed unless every sample item has exact frozen provenance. Draw a new untouched sample after the instrument, estimand, overlap, and adjudication rules are locked.

### P0-10. Annotation ingest and estimation are not yet a valid gold pipeline

JSON ingest checks project/reviewer and, when found, paper membership. It does not verify reviewer assignment, exact version, codebook, release, artifact/context/PDF/packet hash, manifest signature, or protocol identity. If the manifest is absent it warns and proceeds. Markdown fallback bypasses the manifest and structured schema and is still the documented workflow.

The annotations schema has no unique paper-version-reviewer-project constraint, release/run/sample binding, stratum/inclusion probability, packet hash, COI, adjudication, or supersession provenance. Agreement groups by paper rather than immutable paper-version, chooses a pair opportunistically, evaluates verdict only, and provides no confidence intervals or axis-level reliability.

The double-coding protocol is also not implemented. Reviewers receive independent shuffles; the first 100 positions overlap by only 16 items and the first 150 by 41, not the promised shared 100–150. Create an explicit shared overlap assignment, powered by stratum and critical axis.

The planted-item design can test interface/search adherence but cannot directly estimate negative-arm sensitivity:

- plants are machine-selected POS/FLAG candidates, not adjudicated true, findable disclosures;
- conditioning on scanner detection and conventional phrasing creates spectrum/verification bias;
- the bounded acknowledgment/first-page/declaration search is narrower than the all-source classifier construct;
- “deflating” observed prevalence by a detection rate is mathematically underspecified and likely points in the wrong direction.

Record whether the PDF opened, search duration, sections and queries inspected, plant found, unreadability, COI, and protocol deviation. Implement design-weighted estimators, precision/sensitivity/FNR correction, uncertainty propagation, adjudication, and per-axis reliability before a final sample is fielded.

## Direct API backend: material progress and remaining contract gaps

### What is genuinely fixed

The direct API path is materially safer than `codex exec`:

- no model tools are supplied;
- API mode forces `isolate=True`;
- `make_batches` confines one request to one paper;
- the model cannot browse the repository/corpus or read ambient local files;
- API keys are gitignored and intentionally not logged;
- transport certificate verification remains enabled;
- validation and a retry path exist;
- two small pilot runs completed without invalid stored items.

This removes the most severe cross-paper agent/tool boundary from review 4 for future API runs. It does not retroactively repair the public main run.

### It is JSON-prompted output, not provider-enforced structured output

`pipeline/llm_api.py:1-13` calls the path “structured-output,” but provider request bodies at `llm_api.py:129-199` send ordinary text prompts. They specify neither a JSON schema nor an OpenAI `response_format`/Responses text-format schema. The local parser/validator is therefore the only structural control.

OpenAI documents Structured Outputs as schema adherence rather than merely valid JSON; use a strict native schema and explicitly handle refusal/incomplete states. See [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

The provider prompt also puts taxonomy instructions and hostile manuscript text in one user message. The API removes local exfiltration and cross-paper contamination, but a manuscript can still instruct the model to mislabel its own paper. Use the strongest available system/developer instruction, place manuscript text in a clearly typed data field, and maintain an adversarial prompt-injection evaluation set.

### Endpoint, model, and response provenance are not reproducible

The OpenAI path first tries Chat Completions, changes token parameter after one kind of 400, then falls back to Responses on 400/404 (`llm_api.py:147-179`). The effective endpoint is not fixed or recorded. OpenAI's current documentation recommends the Responses API for reasoning models; choose one route and pin its contract rather than selecting at runtime from error text. See [OpenAI's current model-use guidance](https://developers.openai.com/api/docs/guides/latest-model).

Across providers, the code discards:

- response/request ID;
- returned effective model/snapshot;
- endpoint and API version actually used;
- finish/stop reason, incomplete reason, refusal, and safety status;
- system fingerprint where available;
- full usage breakdown, including cached/reasoning tokens;
- retry history and timing;
- provider headers useful for support/reconciliation.

The API pilot rows are partial and stamped `d1d2c47-dirty`. They cover only a handful of deterministic early-arXiv-order papers, not a preregistered cross-provider/human sample. On overlapping snippets the two pilots already disagreed on several polarities, underscoring that model choice is a measurement choice, not an implementation detail.

Pin the endpoint, model snapshot where the provider exposes one, reasoning/temperature settings, schema bytes, maximum output, and decoder. Persist every attempt and the returned identity. A marketing model ID alone is not sufficient proof of immutability.

### Transport and key handling need a stricter boundary

`load_env()` accepts arbitrary variables from the repo-root `.env`, while module-level `requests.post/get` honors ambient proxy, `.netrc`, and CA-bundle configuration. Redirects are not explicitly disabled, response bodies are fully buffered, and provider error snippets can flow into stored/printed exceptions. The local `.env` appeared mode `0777`; DrvFS mode bits do not prove the underlying Windows ACL, so actual access controls require verification.

Use a dedicated `requests.Session` with:

- `trust_env=False` unless a reviewed proxy is intentionally required;
- fixed allowlisted origins and `allow_redirects=False`;
- an allowlist of accepted `.env` key names;
- bounded response/error sizes and total wall time;
- capped/jittered `Retry-After` handling;
- explicit idempotency/retry policy;
- OS secret storage or verified restrictive ACLs.

Repeated 429/5xx responses currently end with a misleading `last=None`, and a timeout does not prove the provider did not process or bill the request.

### Vendor data governance is still absent

The API sends an identified arXiv ID and an exact source excerpt to an external provider. Some excerpts may come from unrendered or residual archive members. The repository contains no documented provider decision covering retention, abuse monitoring, training controls, subprocessors, regional transfer, deletion, incident response, author rights, or institutional approval.

For OpenAI specifically, the official data-controls page says API data is not used to train models by default, but abuse-monitoring logs may be retained for up to 30 days; some endpoint state has separate retention, and Zero Data Retention/Modified Abuse Monitoring require eligibility. The Responses fallback should explicitly set and document `store:false` if that is the chosen policy. See [OpenAI API data controls](https://developers.openai.com/api/docs/guides/your-data).

Perform an equivalent provider-specific review for Anthropic before choosing a full-run backend. Record the selected settings and legal/ethical approval in the release manifest. Minimize excerpts and prefer rendered-source evidence where the construct permits it.

### Validator semantics remain looser than their documentation

Beyond JSON repair:

- missing arrays, flags, and location can default to empty/unknown rather than being rejected;
- overlong strings are silently truncated rather than rejected;
- a JSON boolean used as confidence can become numeric `1.0` because Python booleans are integers;
- the first parse-failed raw response is overwritten by retry;
- a failed schema retry can also lose its raw response;
- quote grounding is recorded but is not required for `status='ok'`.

Make the schema canonical and fail closed. Keep immutable attempt rows separate from selected outcomes. Add hostile and property-based tests for types, omissions, duplicate IDs, overlength, booleans-as-numbers, Unicode/control characters, refusals, max-token truncation, and quote spans.

## Scientific and statistical review

### The primary estimand still needs a fully executable definition

The owner has now chosen first submitted version as primary. Before the first release, specify and encode:

- exact date interval and metadata cutoff;
- category rule at a defined time, including the math-ph decision;
- paper versus paper-version unit;
- explicit v1, inferred-single-version, unknown-reroll, withdrawn, missing, and unreadable strata;
- source versus rendered-document observability;
- what counts as an explicit generative-AI disclosure;
- whether ancillary/non-rendered files belong to the construct;
- missing-data and measurement-error estimators;
- frozen inclusion/exclusion manifest and correction lineage.

`report.py` and `annotate.py` still use mutable latest paper metadata for category/date operations and roll up by paper ID. A v1 text estimand paired with latest category metadata needs an explicit rationale or a frozen historical metadata rule.

### The current 2.1% is a raw model-output ratio

The current frame was 133,279 papers, with 131,310 scanned and 1,969 outside the successful scan denominator. The model marked 2,799 grounded papers positive. This is useful engineering telemetry, not yet a population estimate, because:

- source version is unknown for about 95% of the denominator;
- 67.8% of headline positives lack exact rendered certification;
- the classifier has no representative human precision/sensitivity estimate;
- missingness is not ignorable by construction;
- the underlying run is dirty and non-isolated;
- the frame/category definition remains partly open;
- the site reports axes beyond the validated retrieval scope.

Wilson intervals around the raw fraction do not cover model error, missingness, version bias, temporal dependence, or frame uncertainty. Because this is close to a census of a captured frame, a sampling interval also needs a declared superpopulation/stochastic estimand. The corrected `±0.08 percentage point` arithmetic is better than the old `±1`, but its interpretation remains too broad.

Report the raw ratio, reason-coded missingness bounds, and measurement calibration separately. Propagate human-label and missing-data uncertainty after the final gold study.

### Trend and subgroup panels are exploratory

Monthly missingness varies over time, and the report's month table does not make every missing/error stratum partition the frame alongside the rate. Version composition, corpus acquisition, model behavior, and disclosure conventions can all change over time.

Subfield/tool/provider/agentic/impact panels have no axis-specific gold validation, composition adjustment, shrinkage, multiplicity control, temporal-dependence model, or preregistered hypothesis family. A minimum `n=100` alone does not make rank order reliable. Suppress or label these as exploratory until their retrieval and labeling performance are separately measured.

The site also overstates scope. `classify.py:84-92` sends only `llm` and `generic` hit tiers to the classifier, while public copy describes comprehensive ML, coding-assistant, proof-assistant, prover, and CAS coverage. A Lean/CAS term co-occurring with an LLM snippet is not a validated proof-tool prevalence instrument. Narrow the present headline to explicit generative-AI/agent disclosure and develop separate validated modules for CAS/provers/custom code.

### Source scanning still exceeds the render-first privacy/construct promise

The scanner reads all text-like archive members, including potentially unreferenced residues, comments, prompt/chat filenames, and ancillary material. This can improve raw recall, but it does not establish that text was visible in the submitted paper and can expose material outside the publication construct.

The include/comment heuristics are not a TeX parser: escaped-percent handling, nested braces, include graphs, conditionals, generated files, and verbatim contexts remain difficult. The scientific protocol should either:

- use a render/include graph and exact PDF evidence as the primary construct; or
- define a separate source-archive disclosure construct, quarantine residual evidence, and obtain explicit privacy/licence approval.

Keep exact rendered, fuzzy-needs-review, source-only, ancillary, and unknown-version outcomes separate.

### Prior-art corrections are a real improvement

The factual corrections identified in iteration 3/4 remain present: corrected Patterns v2 numbers, survey-selection caveat, Andrew Gray attribution/estimand, Pangram domain/FPR, ArxivMathGradingBench item count, secondary-source trend caveat, and the 27%-of-bytes clarification. Preserve these.

The bibliography remains explicitly non-systematic and mixes preprints, product reports, blogs, and social announcements. Add a claim ledger with exact version/DOI/archive URL, access date, evidence type, independent-verification status, and the precise proposition each citation supports. An assertion of exact v2 should link an exact archived/versioned source rather than only a mutable abstract page.

This iteration's external verification was limited to official API documentation; I did not repeat the earlier full primary-source checks, and earlier access-blocked NBER/RAID/bioRxiv references remain unverified by this audit.

## Data, provenance, and pipeline integrity

### Strong current properties

At the audited point in time:

- SQLite `quick_check` passed;
- foreign-key check returned zero violations;
- every classification item had at least one evidence edge;
- no cross-paper/version evidence edge was found;
- no evidence edge pointed outside the consumed scan runs;
- all 167,003 non-null main-run scan artifact hashes resolved to a same-paper artifact;
- official S3 import reconciliation remained exact at 168,027/168,027, with no reported missing/extra/duplicate members;
- all 241 historical fuzzy successes were demoted out of exact-rendered status.

This normalized run/evidence lineage is one of the repository's strongest engineering foundations.

### Historical evidence dedup fix is prospective only

`classify.store_results` now preserves evidence edges during dedup. The historical main run still links 172,374 of 172,437 classifiable hits: 63 expected edges were not backfilled. Every affected item retains at least one correct same-paper/version/run edge, so this does not appear to change the paper headline, but exact snippet provenance remains incomplete.

Backfill through a deterministic integrity migration or explicitly mark the old run as pre-fix and ineligible for release.

### Run/release data should be immutable in the database

Immutability currently depends on application discipline. Run rows and release summaries lack database triggers/status transition constraints, and a release does not materialize the exact source rows it certifies. The builder performs multiple reads from a live database rather than one stable snapshot transaction.

Add:

- append-only invocation/attempt/evidence records;
- constrained state transitions;
- immutable terminal runs and releases enforced by triggers or separate immutable storage;
- exact release-member, artifact, evidence, render, gold, and output-asset rows;
- a logical snapshot/transaction boundary;
- signed/checksummed release and correction manifests.

### Acquisition/reconstruction gaps remain

The recursive OAI reparse fix is good. Deleted OAI records are still skipped rather than stored as tombstones, so reconstructed metadata can retain stale papers. Submitter data is retained for almost the entire corpus without a stated scientific need.

The artifact schema lacks per-version licence. arXiv permits version-specific licence choices, so the release cannot infer redistribution/publication rights from a current paper-level field. Capture licence with each version/artifact or restrict public output until rights are resolved.

## Security, resource boundaries, and cloud operations

### Archive/PDF safeguards improved, but limits are incomplete

Good controls now include streaming capped single-gzip decompression, no tar filesystem extraction, per-member and selected-text budgets, durable incomplete/unknown statuses, read-byte SHA checks, and a PDF conversion timeout.

Remaining boundaries:

- tar member/header count and outer compressed-blob size are unbounded;
- `tarfile.getmembers()` materializes the full header list;
- database paths are not always resolved against an allowlisted corpus root;
- full outer files/members and some HTTP bodies are buffered;
- tar cache handles are not explicitly closed;
- compression ratio and total scan wall time are not bounded;
- `pdftotext` has no OS sandbox/RLIMIT/output quota;
- cached `.txt` output is trusted by path/existence, not `{PDF SHA, extractor/version, output SHA}`;
- render-check status lacks an immutable algorithm/tool-version identity.

Add hostile archive/PDF fixtures and enforce containment, member count, compressed/expanded size, ratio, process, output, and time limits.

### AWS ingestion reconciliation is strong; producer and teardown remain unsafe

The official requester-pays source, upstream MD5 checking, local tar/member hashes, and two-way importer reconciliation are strong. The existing imported corpus reconciled cleanly in this audit.

The producer remains crash-unsafe:

- `filter_remote.py` appends directly to long-lived monthly tars;
- a crash before the chunk marker can duplicate partial members;
- a crash after a marker can preserve truncated output;
- failures are skipped, yet the program can print `ALL DONE` and exit zero;
- fsync/atomic shard commitment and a durable exact ledger are absent.

`pipeline/aws/overnight_sync.sh` remains executable despite being documented as unsafe. It uses broad process killing, treats two equal remote/local size listings 60 seconds apart as completion, does not verify producer done state or hashes/import reconciliation, and can terminate EC2 before the local data is proven complete. It lacks strict shell mode and account/region/tag/instance validation.

Disable or hard-fail this script until it verifies a signed producer manifest and completed local import before teardown. Replace append-open outputs with closed content-addressed per-chunk shards, fsync and atomically commit each ledger entry, and exit nonzero on every gap.

No reproducible IaC/IAM/security-group/IMDSv2/encryption/budget/alarm/logging/restore/automatic-safe-teardown configuration is tracked. Add it before another cloud acquisition.

## Ethics, privacy, legal, and governance

### The governance log is a strong start, not a governance system

Add owner, decision ID, date, expiry/review date, rationale, affected estimand, implementation control, acceptance test, evidence link, and supersession relation to each decision. CI should verify that operational decisions have corresponding controls.

The repository still lacks a tracked:

- software licence and NOTICE;
- data/document licence and per-version rights policy;
- SECURITY.md and vulnerability-reporting process;
- privacy, retention, access, deletion, and incident policy;
- scientific governance/adjudication/correction/appeal/takedown policy;
- CONTRIBUTING, CODE_OF_CONDUCT, CITATION.cff, and changelog/release ledger;
- institutional ethics, DPO/privacy, legal, and vendor-processing determination.

These are launch controls for a project that makes potentially reputational statements about identifiable researchers, not cosmetic repository files.

### Aggregate-only policy conflicts with tracked content and older specifications

The visible site is aggregate-only. The tracked repository still contains expressive per-paper artifacts in `results/*` and `reports/awesome_validation.json`, including IDs, titles, snippets, local paths, automated labels, and human judgments. Previously deleted sensitive artifacts and cloud-instance details remain in Git history.

This conflicts with:

- `DECISIONS.md`'s aggregate-only rule;
- `WORKFLOW.md`/`DESIGN_PLATFORM.md` aggregate publication sections;
- `PITCH.md:67` promising open annotations;
- `DESIGN_PLATFORM.md:10-17` asserting that IDs and derived labels are legally publishable without a documented analysis.

Choose one policy, update every spec, enforce a public-output allowlist, quarantine expressive data outside public Git, and assess history rewrite before repository publicity. Provide a correction/objection channel even for aggregate outputs.

### Corpus and reviewer data controls are not established

Local `.env`, database, corpus, PDF, context, and annotation packet paths appeared broadly permissioned under DrvFS. Linux mode bits do not establish Windows ACL behavior, so verify the actual host and cloud ACLs, encryption at rest, backup access, reviewer separation, audit logs, and deletion schedule.

Gold packets contain identifiable PDFs and extensive contexts. Distribute only assigned, minimized packets through restricted per-reviewer storage. Record reviewer training, confidentiality, COI, compensation, access, and deletion. Do not co-locate all assignments and full packet material in a broadly accessible directory.

The corpus stores submitter fields for roughly 235,000 papers without an articulated need. Minimize or remove them unless they serve a preregistered analysis with approved governance.

Language sensitivity also remains unstated: non-Latin disclosures are deferred in design notes, while the public measurement lacks a language-scope limitation. Disclose and validate this before broad claims.

## Public site, accessibility, deployment, and reach

### Current strengths

- static, tracker-free, no third-party runtime dependency;
- valid document wrapper in the current generated site;
- clear non-affiliation and do-not-cite banner;
- escaped dynamic SVG labels and script-safe JSON;
- table alternatives for many charts;
- exact cutoff and run provenance;
- stale dashboard moved outside `site/`;
- stale ZIP removed;
- current publish root is small and aggregate-oriented.

These are excellent product choices to preserve.

### Remaining public-document risks

- chart-level `role=img` lacks a complete accessible name/description;
- chart interaction remains primarily pointer-based;
- `minmax(420px, ...)` can overflow narrow devices;
- dynamic `innerHTML` remains an unsafe future pattern if data becomes contributor-controlled;
- Markdown/CSV exports remain injection surfaces; spreadsheet cells beginning `=`, `+`, `-`, or `@` need a separate safe export;
- there is no CSP/security-header deployment configuration;
- no automated accessibility, keyboard/touch, high-contrast, reduced-motion, link, HTML, or hostile-data test exists;
- set/Counter/tie ordering can still make top-N site output nondeterministic;
- site build is not tied to a release or checked byte-for-byte in CI.

After scientific release gates—not before—add a canonical URL, repository link, methods/limitations/correction/contact pages, citation metadata, Open Graph/social card, favicon, sitemap/robots policy, stable aggregate schema, and release ID/hash. Credibility and correction discoverability will improve reach more than premature promotional optimization.

Seek arXiv brand/trademark guidance and use the official “arXiv” capitalization consistently.

## Tests, CI, dependencies, and deployment

The local suite passed: 84 tests in under three seconds. Python compilation, shell syntax, SQLite integrity checks, JSON parsing, and `git diff --check` also passed. This is meaningful progress.

Coverage remains narrow relative to the release risk:

- no mocked `llm_api` provider/HTTP tests;
- no native structured-output/refusal/finish-state tests;
- no concurrent budget/cancellation/persistence tests;
- no backend-resume substitution test;
- no TeX/JSON legal-escape regression tests beyond `\Gamma`;
- no flagged-only/prevalence-release refusal test;
- no end-to-end fixture from acquisition through immutable release/site;
- no deterministic double site build;
- no hostile archive/PDF/Markdown/HTML/CSV tests;
- no AWS failure/teardown simulation.

`.github/workflows/ci.yml` says “tests + site build” but only installs and runs pytest. Actions are SHA-pinned, which is good. Add least-privilege `permissions`, job timeout/concurrency, supported Python matrix, package installation, lint/type checking, secret/dependency/licence/SBOM scanning, migration/release fixture tests, site determinism, and accessibility/link checks.

`requirements.lock` pins Requests 2.34.2 but has no hashes, while `pyproject.toml` allows Requests 2.31 and can install below the intended security floor. Align the package constraint and use hash-locked reproducible dependencies. Pin/document Poppler, SQLite, AWS CLI, tar/gzip, and any browser/accessibility tools in a container or environment lock.

There is still no protected deployment chain, host-header configuration, rollback, post-deploy verification, signed manifest, SBOM, or provenance attestation. Generate the site from a `release_id`, compare deterministic bytes in CI, and deploy only that allowlisted artifact through a protected environment.

## Review-4 issue status

| Review-4 issue | Iteration-5 status |
|---|---|
| v1 artifacts unusable by scanner | **Substantially fixed in code**; no v1 scan yet, exact selection manifest absent, inference/decision conflict introduced |
| Mass v1 acquisition boundary | **Still critical**; new owner pause is not implemented and the job appeared live |
| Exploratory 2.1% site | **Honesty materially improved**; scientific no-go remains, and coverage bound wording is wrong |
| Wrong gold frame/version | **Partial**; optional cohort filters and membership check added, but defaults/docs/release/artifact binding remain unsafe |
| Agentic classifier boundary | **Promising new fix for future runs**; direct API is non-agentic and one-paper, but current result unchanged and new budget/transport/resume/parser gaps exist |
| Destructive/mutable provenance | **Strong normalized lineage**; release is still hashes over mutable tables and old run has 63 missing dedup edges |
| Freeze accepts unsafe runs | **Several bypasses fixed**; partial/selected scans, backend, pin parsing, unknown commit, gates, gold, and materialization remain |
| Fuzzy accepted as rendered | **Fixed** |
| Gzip bomb | **Single-gzip path fixed**; tar/header/path/PDF limits remain |
| Stale dashboard and ZIP | **Fixed in current tree** |
| Site tool grounding | **Partly fixed**; retrieval scope and report tool/model strings remain overbroad |
| Prior-art numeric errors | **Fixed and retained** |
| CI/deployment | **Tests expanded and green**; CI/release/deployment chain remains skeletal |
| AWS producer/teardown | **Documented but not fixed** |
| Legal/governance | **Decision log added**; substantive licence/privacy/security/correction package absent |

## Point-in-time empirical snapshot

Because the database was live, use these only to understand audit coverage. Around 2026-08-11 15:05 UTC:

| Item | Observation |
|---|---:|
| Papers / versions | 235,342 / 418,232 |
| Files | 169,166 |
| Artifacts | approximately 182,986 and increasing |
| Scan runs / items / hits | 3 / 169,423 / 547,763 |
| Classification runs / items / evidence edges | 3 / 73,966 / 172,407 |
| Render checks | 8,078 |
| Human annotations | 0 |
| Frozen releases | 0 |
| v1 scan runs | 0 |

Main exploratory scan statuses were 166,183 `ok`, 811 `unknown-format`, 9 incomplete, and 2,162 skipped PDF-tar items. The main classifier had 73,945 items. The two API pilots were small, partial, dirty runs and are not release candidates.

Artifact fingerprints at this Git snapshot:

- `site/index.html`: SHA-256 `4038ecb8577e18ed4beeb1635e3dbdf42312f0e44475b58e049616a36411ae0c`;
- `site/data/disclosures.json`: SHA-256 `3f2a5ca11a061bfcd0ddf70bd0df1a18e6c0786615f84befa8cb74a4cc354e10`;
- `reports/report_3yr_preliminary.md`: SHA-256 `7ec42b40356c31417e8c271b15b6aae7b6a095b689f13d68c539f70e2af310eb`;
- `review_codex4.md`: SHA-256 `be02fc1e0453853393361ada00ce088fc58704e3ab937944de28d2e91d9af433`;
- `dist/`: absent.

## Prioritized implementation roadmap

### Before the refill reaches the flagged boundary

1. Independently stop/verify the live process at the approved boundary.
2. Add `--flagged-only`, an exact target manifest, hard maximum, terminal reconciliation, and an explicit separately approved tail command.
3. Reconcile or preserve outcome information from the pre-ledger live process as far as logs permit.

### Before another paid API pilot

1. Replace regex JSON repair with native strict schemas and fail-closed parsing.
2. Implement durable per-provider monetary budgets with pre-dispatch reservation and bounded in-flight calls.
3. Lock backend, endpoint, model/effective snapshot, schema, parameters, code, and data-handling state into immutable invocation identity.
4. Fix resume so protocols cannot mix and invalid rows remain retryable or force a superseding run.
5. Harden HTTP/key handling and persist request IDs, usage, stop/refusal state, retries, and costs.
6. Complete provider privacy/retention/legal review.
7. Run the same preregistered stratified pilot set across providers, old classifier, and humans.

### Before a v1 prevalence run

1. Resolve math-ph, explicit versus inferred v1, category cutoff, withdrawn/missing, and licence policies.
2. Freeze acquisition and metadata manifests.
3. Materialize exact artifact IDs/hashes and selection reasons; prohibit outcome-conditioned channel choice.
4. Run a complete, clean `texv1-*` scan with terminal reason-coded outcomes.
5. Run one approved, pinned, direct-API classification protocol with exact quote grounding.
6. Render-check the exact paper versions and adjudicate fuzzy/failed evidence.

### Before final human validation

1. Create one immutable candidate release and sample only its exact membership.
2. Freeze the codebook/instrument and draw a new untouched sample.
3. Generate a powered shared double-coded subset and independent remainder.
4. Bind assignment, item, version, artifact, evidence, context, PDF, packet, reviewer, and codebook hashes.
5. Fail closed on ingest; remove production Markdown parsing.
6. Add COI, adherence, adjudication, weighted estimators, precision/sensitivity/FNR, axis reliability, and uncertainty propagation.

### Before calling anything a scientific release

1. Enforce backend, clean/full commit, model snapshot, exact acquisition/scan/render/gold, version, coverage, and governance gates.
2. Materialize immutable release rows and build the site only from `release_id`.
3. Put correct limitations before every number and inside every machine-readable export.
4. Run deterministic clean-clone/E2E/site/accessibility/security checks in CI.
5. Complete licence, privacy, vendor, ethics, correction, appeal, security, and deployment controls.
6. Publish a signed manifest, aggregate schema, methods card, correction lineage, and stable citation.

## Verification performed

Read-only/local checks included:

- full tracked-file and Git-delta inspection;
- focused source and specification review across pipeline, site, annotation, cloud, tests, and governance paths;
- `84 passed` with bytecode/cache disabled;
- Python compile checks;
- `bash -n` for operational shell scripts;
- `git diff --check`;
- SQLite `quick_check` and foreign-key check;
- run/item/evidence/artifact consistency queries;
- point-in-time cohort, version, render, gold, release, and v1-refill queries;
- generated JSON/HTML and artifact hash checks;
- local synthetic diagnostics for JSON/TeX parsing and freeze/resume contracts;
- targeted tracked-tree/history secret and expressive-artifact checks;
- official OpenAI documentation review for structured output, model/API guidance, current model pricing, and API data controls.

This was not a penetration test, formal legal opinion, institutional ethics review, accessibility conformance audit, cloud account audit, provider invoice reconciliation, or exhaustive external bibliography replication. The live database means counts after the stated times may differ. No obvious tracked API/AWS/private-key secret was found in targeted checks, but that is not a formal secret scan.

## Bottom line

Iteration 5 materially improves the project. The direct API backend, decision log, v1 scanner, freeze checks, fuzzy demotion, site caveats, evidence normalization, and expanding tests are all worth preserving.

The next milestone should not be “publish the 2.1% more confidently.” It should be: **make one complete owner decision executable from acquisition through immutable release, and make every published number cryptographically and scientifically traceable to it**.

Until that exists, the current site can serve as a deliberately risk-accepted engineering inspection snapshot, but not as a validated estimate of AI disclosure prevalence.
