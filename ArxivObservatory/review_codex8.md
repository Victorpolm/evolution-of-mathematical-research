# ArxivObservatory repository review — iteration 8

**Audit snapshot:** Git commit `7ee738602a0f93c6d6fe3c25a67508998bf4238b`, tree `ee50133a099aa2e5192825edc7f8a4b0eca74269`, 2026-08-12 15:38 CEST. The worktree was clean before this review file was created.

**Primary delta reviewed:** everything after the iteration-7 snapshot `6edb339`, especially the quarantine commit `9a11558`, review-7 triage commit `d3b2e6e`, taxonomy v2.2 and its R4/R5 rules, the executable calibration analysis, adaptive classification splitting, API spend reservations and run leases, the v1 scan/classification/render state, report/release logic, generated site, and publication preparations.

**Audit boundary:** read-only except for creating this file. I did not invoke an LLM, contact an API provider or arXiv, start or stop a pipeline job, change the database/corpus/annotation files, operate cloud resources, or publish anything. Restricted calibration material is summarized only in aggregate. I checked current official OpenAI documentation where OpenAI-specific behavior matters; this was not a new systematic verification of the scientific bibliography.

## Executive verdict

The project has again improved substantially. Taxonomy v2.2 is a much better scientific construct than v2.0/v2.1; the calibration headline arithmetic now has an executable source; adaptive splitting addresses the dominant prior truncation failure; prompts no longer include the arXiv ID; OpenAI requests set `store:false`; pre-dispatch spend is visible in SQLite; and the most problematic per-paper result files have left the tracked tree. No v2.2 labels exist yet, so the project still has a clean opportunity to correct the remaining instrument defects without invalidating expensive work.

The project is nevertheless **not ready to begin the full taxonomy-v2.2 classification run today**, and is further from being ready for the final two-grader gold study or public release. The remaining pre-classification blockers are concrete implementation defects, not requests for indefinite polishing:

1. The owner log says the two central v2.2 scope choices are still pending confirmation, while the taxonomy and ledger call the codebook operative/fixed.
2. The model prompt contradicts the strict v2.2 schema: it names the removed impact `none`, omits a required flag, and one retry asks for the wrong top-level shape.
3. Human and machine graders still cannot express the same R4/R5 labels or cross-field invariants—most importantly, humans cannot record `method_component` on `TOPIC_ONLY` cases.
4. The documented per-provider, per-campaign dollar cap does not exist as such. All historical provider spend is pooled, while separate processes can still reserve against the same apparent headroom.
5. Run leasing is race-prone, and adaptive splitting/concurrent attempt logging loses the exact mapping between request, response, spend reservation, and snippets.

The final-gold path remains explicitly unimplemented: `annotate build` still makes calibration-only packets from raw run IDs, re-extracts mutable/current files, reuses unhashed contexts, fails open at ingest, has no shared double-code assignment or adjudication implementation, and cannot consume an immutable release candidate. `report --freeze` is not an adequate substitute: it accepts partial coverage and optional evidence gates, materializes no rows, contains no gold gate, and the site cannot consume a release ID.

My current readiness call is:

| Activity | Readiness |
|---|---|
| Private synthetic R4/R5 comprehension exercise | **Ready after the prompt and human/machine parity defects below are fixed** |
| Full paid Luna taxonomy-v2.2 rerun | **No-go until P0-A and P0-B pass** |
| Final two-grader gold study | **No-go until P0-C is implemented and tested end to end** |
| Private inspection of explicitly exploratory aggregates | **Ready with the existing warnings** |
| Public site or public Git repository | **No-go until P0-D/P0-E, governance, suppression, and history sanitation pass** |
| Validated three-year v1 population-prevalence claim | **Not identified by the current selected/partial v1 frame** |

This is a tractable stop list. I recommend fixing and testing P0-A/P0-B before spending on the rerun, then building the release-candidate/gold path against synthetic fixtures while the rerun executes.

## Snapshot and verification

The local database was quiescent when inspected (no active pipeline process or WAL was visible) and had SHA-256 `68ea1ffa0ae25d5ab6bdb41d96cbecb5e280b79d91afe31773e3729846838102`. This hash describes this local point-in-time file, not a clone-reproducible data release.

### Automated checks

- `python3 -m pytest -q -p no:cacheprovider`: **112 passed in 2.98 s**.
- Python AST parsing succeeded for 34 pipeline/test files.
- `git diff --check 6edb339..HEAD` passed.
- `python3 -m pip check` found no broken requirements.
- `bash -n` passed for every tracked shell script.
- SQLite `PRAGMA quick_check` returned `ok`; no foreign-key violations were found.
- The worktree was clean before this report was added.

Passing tests are a genuine strength, but the test count did not grow for the new high-risk mechanics. There are still no regression tests for prompt/schema parity, adaptive split provenance, run-lease races/fencing, cross-process campaign reservations, calibration analysis, or a release-candidate-to-site end-to-end path.

### Current empirical state

- Schema version: **6**.
- V1 selection: **112,447 papers** = 15,019 explicit-v1 + 97,428 inferred-single-version.
- V1 scan `texv1-20260811T215148`: 110,770 `ok`, 54 unknown-format errors, 2 incomplete, and 1,621 skipped PDF-in-tar items. The run is `partial`.
- V1 Luna taxonomy-v2.0 classification `cls-20260811T220922`: **71,194 items**, 71,022 `ok`, 171 length failures, and 1 ID-coverage failure, spanning 21,423 papers. It is `partial`.
- That run contains 3,680 author-use papers / 6,680 author-use snippet items. At paper level, 3,247/3,680 (88.2%) have at least one exact rendered certification. At item level: 5,495 rendered, 777 fuzzy-review, 260 non-rendered, and 148 quote-too-short.
- The v1 run's spend ledger totals approximately **$21.8125** including conservative failed reservations. All OpenAI history in `api_spend` totals approximately **$21.8138**.
- Human annotations: **150**, all one reviewer and codebook v2.0. There is no second-reviewer, adjudicator, or v2.2 human label.
- Classification runs by taxonomy: v2.0 only. **No v2.2 run exists.**
- Frozen releases: **0**.

For the stated 2023-08-01 through 2026-08-08 math-primary frame, the preliminary v1 report has 85,742 scan-complete papers out of 133,279, with 47,554 unresolved outcomes after classification/evidence states. Its conditional raw-label extrema are about 2.0% to 37.7%. These remain the central population-identification facts.

## What is genuinely stronger since iteration 7

The following changes are real and worth preserving:

- taxonomy was bumped to v2.2 before producing new labels;
- R4 now uses an action/consumed-output decision tree and explicitly allows study and assistant roles to coexist;
- R5 separates `zero_contribution`, `undetermined`, and `not_applicable` rather than overloading `none`;
- the machine validator enforces `zero_contribution != catalytic` and `catalytic => supportive/result_bearing`;
- the exact taxonomy-manual hash now enters the classification protocol identity;
- the core calibration counts are generated by `annotate calibration`, with reason-coded exclusion of the packet-version-skew case;
- the corrected calibration figures are now 150 ingested / 149 comparable, 28/32 shown-positive precision, 5/5 hidden-positive plants, 0/96 same-text NEG misses, and 145/149 binary concordance;
- the calibration and gold documents now correctly describe plants as a process check rather than transportable sensitivity;
- `UNCLEAR` and `INSUFFICIENT_EVIDENCE` are documented as non-evaluable rather than automatic negatives;
- deterministic adaptive bisection exists prospectively for oversized or malformed model batches;
- provider-visible prompts omit the arXiv ID;
- OpenAI calls set `store:false`; Anthropic forced tools use `strict:true`; provider schemas derive from `taxonomy.py`;
- API runs require a positive dollar cap and a budget-approval string and default to the approved OpenAI/Anthropic allowlist;
- each physical dispatch gets a durable pre-dispatch reservation row, and 429 rejections release their reservation;
- a run-lease table exists as the start of paid-work concurrency control;
- current-tree `results/*`, awesome-validation files, the old spot-check file, live instance inventory, and unrelated Lean tooling have been removed/ignored;
- the site remains `noindex`, explicitly `unreleased_exploratory`, machine-readable as `do_not_cite`, tracker-free, and non-affiliated;
- README funding and project AI-use disclosures are materially more candid than the original repository.

Several of these are only prospective: no v2.2 run has exercised the new prompt, bisection, lease, or campaign semantics at scale.

## P0-A. Freeze one internally consistent taxonomy/instrument before the full rerun

### A1. The owner decision is not actually frozen

`DECISIONS.md:8-18` says both central v2.2 choices remain **pending owner confirmation**: active AI instrumentation is in scope under R4, and R5 uses the new impact split. In contrast, `TAXONOMY.md:8-24` calls v2.2 operative and records an owner decision, while `LEDGER.md:247-268` calls the review-7 instrument findings fixed.

This is more than editorial drift. These choices define the numerator and the grader task. Before any label is created:

1. record explicit owner approval of the exact committed codebook text and primary numerator;
2. record hashes for `TAXONOMY.md`, `taxonomy.py`, prompt header, provider schema, validator, and grader instructions;
3. require a new taxonomy version for any semantic edit after sign-off;
4. ensure all runbooks and public descriptions use the same construct.

No v2.2 labels exist, so there is no cost to doing this cleanly now.

### A2. The v2.2 prompt contradicts its native schema

`pipeline/classify.py:74-82` correctly asks for a top-level `{"labels": [...]}` object, but its example and applicability instruction are stale:

- the example flags object contains only `catalytic`, while the strict provider schema requires every current flag, including `method_component` (`pipeline/llm_api.py:223-253`);
- it says to use impact `"none"` when not applicable, but v2.2 has no such value; the valid value is `not_applicable`;
- the local validator accepts omitted flag properties, whereas the provider-native schema requires them;
- the schema-violation retry asks for a corrected JSON **array** (`pipeline/classify.py:430-434`) instead of the required object wrapper.

Strict provider decoding may mask part of this, but confirmatory grading instructions must not conflict with their schema. Generate the output example and applicability rules from the schema, use a single object-shaped contract throughout, and add a snapshot test that proves:

- every required property is present in the example;
- every enum value named by the prompt belongs to the schema;
- retry instructions require the same shape;
- local validation and provider validation require the same fields.

This is an unconditional pre-run blocker.

### A3. Human and machine graders still have different label spaces

Taxonomy v2.2 introduces `method_component` primarily to diagnose R4 steps 1/3 and says it may accompany any polarity (`pipeline/taxonomy.py:169-172`; `TAXONOMY.md:133-139`). Machine validation preserves it on non-author-use labels (`pipeline/classify.py:321-328`). The human path cannot do so:

- all flags appear inside `.usage`, a panel shown only for `TRUE_DISCLOSURE` (`pipeline/annotate.py:387-443`);
- ingest clears every flag for non-TRUE verdicts (`pipeline/annotate.py:591-618`).

Thus humans cannot record `method_component` on the `TOPIC_ONLY` cases it was created to characterize. Human ingest also rejects only `zero_contribution + catalytic`; it still accepts `cosmetic + catalytic` and `undetermined + catalytic`, which the machine validator rejects. Non-disclosure human rows store empty impact rather than canonical `not_applicable`.

Use one shared cross-field validation function for model labels and human exports. Put polarity-independent diagnostics outside the TRUE-only panel. Prefer explicit yes/no/unknown controls to unchecked boxes, so omission is not silently interpreted as false. Add parity tests over every polarity × impact × flag combination.

`report.paper_rollup()` also merges tools, models, categories, impact, and locations across author-use snippets but not flags (`pipeline/report.py:175-184`), making paper-level `catalytic`/`method_component` order-dependent. Define and implement paper-level flag aggregation.

### A4. R4 still needs a sharper active-instrument/fixed-component boundary

The revised action/output framing is much better, but two examples still overlap:

- “embeddings production” is in-scope active instrumentation;
- “LLM word embeddings analyzed as data” is a fixed component/object and topic-only.

The decisive rule should explicitly answer:

1. Was the output newly produced for this study or pre-existing?
2. Was it used to study a non-model target or solely observed/evaluated as the scientific object?
3. Did the authors delegate a research/communication task, or merely execute a fixed component?
4. Can a method-component role and a separately disclosed assistant role coexist? (They should.)

Before sign-off, run a private, non-confirmatory comprehension set through both human graders and Luna. Cover at least frozen encoders, newly generated embeddings, LLM judges/labels, synthetic data, pipeline code, model evaluation, dual object/tool roles, explicitly fruitless attempts, catalytic incorrect output, vague disclosures, and a paper with both contributing and zero-contribution uses. Store only synthetic/deidentified cases; none should enter final gold.

### A5. The measured tool scope must match the public construct

The classifier currently retrieves only `llm`/`generic` scan tiers (`pipeline/classify.py:96-100`). Standalone `ml`, `prover`, and `cas` hits are not comprehensively classified. Taxonomy and site prose still discuss broad AI/ML/prover/CAS tool roles.

The primary estimand should therefore be named something like **explicit disclosed generative-AI/LLM tool use found by the llm/generic retrieval protocol**, unless separate prover/CAS/ML retrieval and validation modules are built. Pure Lean/CAS use must not be implied to be in the measured numerator merely because such tools appear in the taxonomy or dashboard.

### P0-A acceptance test

Do not start the paid run until all of the following pass in CI:

- signed owner decision and taxonomy version/hash bundle;
- prompt/schema/local-validator parity test;
- human/machine cross-field parity matrix;
- human `TOPIC_ONLY + method_component` round-trip test;
- paper-level flag aggregation test;
- two-human-plus-Luna comprehension exercise with disagreements resolved into the frozen manual;
- explicit primary/secondary numerator definitions and tool-family scope.

## P0-B. Make the paid-run budget, lease, and request provenance true—not documentary

### B1. “Per provider per campaign” is not represented or enforced

`DECISIONS.md:14-18` defines budget scope as **per provider per campaign**, with a new approval for the full run. `api_spend` has no campaign or approval column (`pipeline/migrate.py:296-310`). `llm_api.attach_ledger()` sums all historical spend for each provider (`pipeline/llm_api.py:103-128`). The free-form `--budget-approval` string lives only in run params/invocation JSONL, not in spend rows or the protocol hash.

This causes two opposite failures:

- a newly approved $25 v2.2 campaign would inherit about $21.81 of prior OpenAI spend and stop after only about $3.19;
- two processes for different run IDs can load the same historical baseline and independently reserve against the same campaign cap, because admission uses process-local memory and run leases are per run.

Create a durable `budget_campaigns` object with at least approval ID, provider, allowed model/config, cap, tariff hash/as-of date, purpose, owner, expiry/status, and amount already committed. Every spend row must reference it. Reserve by atomically checking settled + conservative-failed + active reservations and inserting the new reservation inside one `BEGIN IMMEDIATE` transaction (or an equivalent serialized provider-campaign lease). Never rely on an in-process lock for a cross-process monetary guarantee.

The price table currently matches the official base Luna price ($0.20/M input, $1.20/M output), but a release-grade tariff record should include all applicable cache/long-context/routing rules and its source/date. See the [official Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

The character heuristic `len(prompt)//3 + 1500` is generous but not a provable token upper bound. Either use an exact/provider-supported count with a conservative output reservation, a truly safe encoded-byte upper bound, or include explicit allowed overshoot in the approved campaign contract. Do not call it a mathematically hard cap without that proof.

### B2. The run lease has race and fencing defects

`_lease_acquire()` selects outside a transaction, then unconditionally upserts (`pipeline/classify.py:499-520`). Two starters can both observe no lease and proceed, with one overwriting the other. Heartbeat and deletion are keyed only by run ID, not by holder, so an old process can refresh or delete its successor's lease. Heartbeats occur after every 25 successful top-level batches rather than on time; a long request/retry/split can exceed the ten-minute stale threshold and be falsely stolen.

Use:

- an atomic conditional acquire transaction;
- a cryptographically random holder/fencing token;
- `WHERE run_id=? AND holder_token=?` on heartbeat, settlement authority, and release;
- a time-driven keeper thread independent of batch success;
- explicit stale-takeover audit rows;
- a final assertion that the process still holds the lease before storing results or charging.

Add multiprocess tests for simultaneous acquisition, stale takeover, old-holder heartbeat/delete, and a call longer than the stale interval.

### B3. Adaptive bisection fixes truncation but breaks response-to-evidence traceability

`classify_batch()` recursively returns raw strings without the child batch or split path (`pipeline/classify.py:396-415`). The main logger then associates every child response with the original parent batch hashes (`:738-742`). Since child responses restart snippet IDs at zero, they cannot be mapped unambiguously back to the exact snippets after the fact.

API attempts are buffered globally and drained by whichever concurrent future completes next (`pipeline/llm_api.py:67,295-298`; `pipeline/classify.py:743-749`). A request ID can therefore be written next to the wrong logical batch. Attempt records also omit prompt/response hashes, split path, ordered snippet hashes, reservation-row ID, retry number, and returned model identity.

Make each logical request and physical attempt a durable row with:

- run, campaign, invocation, parent request, and deterministic split path;
- ordered snippet/item hashes;
- prompt/schema/protocol hash and request-body hash;
- response-body hash and validated-label hash;
- spend-reservation ID;
- provider HTTP request/message/completion ID;
- requested model/config and returned model/snapshot/fingerprint;
- finish/stop reason, usage details, status, retry number, and duration.

Persist the pre-dispatch row before HTTP and update it immediately after the response, not after an unrelated future completes. JSONL can remain a human-readable export, but SQLite should be authoritative.

### B4. Provider inference identity is incomplete

The OpenAI request pins only the rolling model string and does not explicitly set or record reasoning effort; the current official Luna documentation lists reasoning-effort choices and a default. Returned OpenAI `model`/`system_fingerprint` and returned Anthropic model/version are discarded (`pipeline/llm_api.py:439-513`). A model alias plus a requested string is not immutable provenance.

Set all relevant inference controls explicitly, include them in protocol identity, and persist provider-returned identity. If an immutable provider snapshot exists, prefer it; if not, state that limitation and use returned fingerprint/version plus rerun calibration to detect drift. The [official Luna documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna) should be the source of record for supported controls and current pricing.

### B5. Make the rerun completion criterion explicit

The existing v2.0 run's 172 non-ok items show why “almost complete” is not enough: the failures concentrate in unusually complex, snippet-heavy papers. The adaptive algorithm is promising, but it is untested in the fixture suite and has not processed these cases under v2.2.

For the full run, require:

- every classifiable snippet in exactly one terminal state;
- no unresolved length/ID/schema errors before freeze;
- single-snippet terminal failures reported, inspected, and bounded rather than omitted;
- exact input-set and result-set hashes;
- one-to-one reconciliation among logical requests, physical attempts, spend rows, raw-response hashes, classification items, and evidence edges;
- provider-console reconciliation and signed owner acknowledgment of actual spend.

## P0-C. Implement the final-gold path before drawing or opening the confirmatory sample

Round 7's main gold blocker remains open. The current tool is suitable for development calibration only—and it honestly says so—but it cannot support release validity.

### C1. Use an immutable analysis snapshot, not raw run IDs

`annotate build` accepts a scan run and classification run and always writes `calibration_only_never_release_validity` plus a CALIBRATION banner (`pipeline/annotate.py:262-277,319-350`). There is no `--release`/`--snapshot` mode.

Use two stages:

1. **Analysis snapshot / release candidate:** immutable frame membership, selected source artifact, scan item, labels, evidence, render state, missingness, protocol, and acquisition/selection manifests. It makes no validity claim.
2. **Validated release:** references exactly one snapshot plus the frozen gold project, original labels, adjudications, estimator outputs, pass/fail gates, report/site/data hashes, license, and correction lineage.

Gold must sample the first object; the second is created only after validation.

### C2. Bind every packet and verdict to exact source bytes

The calibration's live version-skew failure remains reproducible in code:

- hit contexts are re-extracted from whichever current successful `files` row wins, not the artifact selected by the scan item (`pipeline/annotate.py:98-116`);
- current/latest title/comments metadata can be displayed beside v1 evidence;
- `contexts.json` is reused merely because it exists (`:279-299`);
- version-pinned PDFs are optional;
- manifest, contexts, PDF, item order, packet, and codebook are not mutually hashed/bound;
- localStorage is keyed only by project and reviewer, so a regenerated packet can restore stale answers;
- the unblinded master manifest containing strata and plant identities is co-located with reviewer packets.

The final snapshot and per-reviewer manifest should bind at least:

- snapshot/release-candidate ID and member ID;
- paper ID plus exact scanned version and version basis;
- scan item, selected artifact ID/path/SHA-256, and selection-manifest member;
- evidence hit/context hashes and exact context-construction protocol;
- version-pinned PDF SHA-256, retrieval channel, and render/extractor versions;
- hidden stratum and inclusion probability;
- frozen taxonomy/manual/prompt/schema/validator hashes;
- assigned reviewer, shared/single-coded role, random order, and order hash;
- packet-data and rendered HTML hashes;
- round type, creation commit/tree, and supersession state.

Keep the allocator/plant key in a separate restricted location. Ship each reviewer only their blinded assignment manifest and packet. Include packet hash in the localStorage key and JSON export.

### C3. Ingest must fail closed and preserve original evidence

`ingest_json()` currently warns and continues without a manifest, validates only global paper membership, does not check reviewer assignment/version/codebook/packet/context/PDF hashes, and trusts the export's codebook string (`pipeline/annotate.py:621-670`). The annotations schema lacks release/snapshot/member, sample design, evaluability, conflict-of-interest, search process, packet hash, first-pass/adjudication role, and a uniqueness constraint.

For final gold:

- absence or mismatch of any required manifest/hash must be fatal;
- verify project, round, snapshot, reviewer, assignment, item/version, packet, and codebook exactly;
- insert an immutable export record keyed by export hash;
- enforce uniqueness transactionally for first-pass reviewer × snapshot member;
- retain original first-pass labels forever; adjudication is a distinct role/row;
- capture evaluability/reason, PDF opened/version verified, bounded-search actions/time, plant-search outcome, COI/reassignment, notes, and all axes;
- never silently migrate browser state or old answers to a new packet.

### C4. Prespecify an actual shared double-coded subset and adjudication

Both reviewers currently receive all items in independently shuffled order. If each labels only the first 100-150 positions—as `GOLD_STUDY.md:98-101` suggests—the shared overlap is incidental, not 100-150.

Create a seeded, stratified shared subset and assign the same item set to both graders, with independent order within that set. The manifest must distinguish shared and single-coded items and record completion/stopping rules. Full double coding remains preferable if feasible.

The written adjudication protocol requires someone who produced neither first-pass label for human-machine conflicts and says reviewers do not adjudicate their own disagreement. Two graders cannot satisfy this. Recruit a third blinded adjudicator for disagreements plus a randomized agreed-control sample, or preregister a weaker consensus method and describe its loss of independence honestly.

`agreement` currently takes the first two labels and computes verdict-only percent agreement/kappa. Implement first-pass binary/fine-verdict agreement, axis metrics, intervals, reviewer-pair identity, adjudication worklists/ingest, and control-item flip rates.

### C5. Implement and freeze the estimators before opening labels

The protocol describes design-based estimation but the code does not implement it. Before fielding:

- define binary mappings and non-evaluable handling;
- freeze stratum definitions, inclusion probabilities, finite-population corrections, random seeds, and stopping rules;
- implement precision, FLAG/NEG false-omission, sensitivity, corrected prevalence, and missing-frame bounds;
- propagate both sampling phases with a stratified/finite-population bootstrap or another prespecified interval;
- implement per-impact/category/location metrics only where powered;
- freeze publication thresholds and the treatment of failed/unknown/render-ineligible states.

Non-evaluable outcomes remain missing outcomes within their original design strata, with best/worst-case or modeled sensitivity bounds. They are not automatic negatives and not a new post-sampling stratum.

The 150 POS target can estimate overall precision near 90% to roughly ±5 percentage points; it cannot power 17 category precisions, every impact, rare R5 cases, and every era. Stratify/oversample by impact, era, and prespecified R4/R5 hard-case groups with recorded probabilities, or label those analyses exploratory.

Plants need two phases: blinded bounded-search behavior first, then complete-evidence adjudication for truth. Do not allow a reviewer's search failure to become the gold truth label.

### C6. Current calibration analysis: corrected core, incomplete implementation

The generated current binary results are internally sound:

- 150 ingested; 149 comparable after one reason-coded version-skew exclusion;
- shown POS precision 28/32 = 87.5% (Wilson 71.9%-95.0%);
- hidden machine-positive plants 5/5 (Wilson lower bound 56.6%; process check only);
- FLAG disclosures 0/16 (upper about 19.4%);
- same-text NEG candidates 0/96 (upper about 3.8%);
- binary human-machine concordance 145/149 = 97.3%.

However, `annotate calibration` treats every non-TRUE verdict as a binary negative, including `UNCLEAR` and `INSUFFICIENT_EVIDENCE`, contrary to the protocol. Current numbers happen not to change because neither verdict occurs. It also:

- does not verify its CLI run IDs/reviewer/codebook against the manifest;
- reads all project/reviewer DB rows rather than exact manifest member/version rows;
- hardcodes grounded-only rollup irrespective of manifest render policy;
- counts only plants whose hidden machine rollup is author-use, not all planted cases;
- emits no axis agreement/Jaccard/confusion matrices, design weights, or input hashes.

Therefore `DECISIONS.md` overstates that all calibration aggregates come from the executable command: the impact/category/location claims remain manually derived. Extend the command and mark the older `calibration_summary.md` superseded. These remain development metrics, not release validation or inter-rater reliability.

## P0-D. The freeze/report/site path is not yet a scientific release

### D1. `report --freeze` is a digest record, not an immutable validated snapshot

The freeze gate has improved, but still permits:

- a partial or arbitrarily selected scan with no coverage threshold;
- optional grounding and render gates;
- no acquisition/selection-manifest requirement;
- no final-gold/measurement-quality gate;
- any API model configuration that passes the coarse backend checks;
- a classification run that can list multiple consumed scans, provided the requested scan appears among them.

It then stores counts and hashes of live-query paper sets, not materialized member/label/evidence/render rows (`pipeline/report.py:396-444`). `membership_sha256` hashes only `paper:version`, omitting artifact, version basis, label, evidence, render result, protocol, and gold identity. Database triggers do not make producer rows or release relationships immutable.

There are two fresh correctness defects:

- the manifest describes the category rule as `primary math.*`, while the actual predicate `LIKE 'math%'` deliberately includes `math-ph`;
- the report is written before the release row calls `db.code_commit()`. Writing the default tracked report can itself make the tree dirty, so the stored generator commit may be `<HEAD>-dirty`; the generator's clean commit/tree is not checked before output.

Capture and validate the clean generator HEAD/tree before writing, execute all reads in one snapshot transaction, materialize release membership and relevant row hashes, and commit the release atomically only after every gate and output hash passes. The release statement must enumerate exactly which gates passed rather than saying generically that “validity gates were enforced.”

### D2. The site cannot consume a release and still silently pools R5

`build_site` accepts raw scan/classification IDs and always emits `unreleased_exploratory`; it has no `--release` path (`pipeline/build_site.py:181-196,348-383,578-588`). This is correct for today's preview but not a launch path.

`report.py:370-382` now names attempted-or-contributing and contributing use separately. The site still treats every `author_use`, including `zero_contribution` and `undetermined`, as “AI assistance” and exports only `n_author_use`. Before any v2.2 site:

- export attempted-or-contributing, contributing, explicit-zero, and undetermined counts;
- show the primary numerator clearly in every headline/chart/download;
- define paper-level aggregation: a known contribution should dominate an explicit-zero attempt; `undetermined` applies only when no contribution class is known; explicit-zero should mean all disclosed attempts are explicitly noncontributing;
- never silently pool zero/undetermined into a contributing-assistance phrase.

### D3. The v1 frame does not identify three-year population prevalence

The v1 candidate corpus is intentionally incomplete: 47,554/133,279 frame outcomes remain unresolved in the preliminary report. The missing multiversion tail was selected using prior mixed-version non-flag status and is therefore not demonstrably ignorable. Gold within scan-complete papers can validate classification in that selected observed-v1 frame; it cannot repair acquisition missingness or validate full-frame prevalence.

The public estimand decision at the bottom of `DECISIONS.md` must be resolved before preregistration. Scientifically defensible choices include:

1. a **selected/observed-v1 frame audit**, with explicit inclusion mechanism and no population-generalized headline;
2. full-frame partial-identification bounds plus observed-frame estimates;
3. a fully covered recent period as the primary estimand, with the three-year selected frame secondary;
4. obtaining the coordinated tail later and postponing a population claim.

Do not call the current 2.0%-37.7% extrema bounds on true prevalence: they condition on accepting machine labels for observed papers and omit classification error. Call them **coverage-extreme raw-classifier-positive rates**.

The v1-vs-mixed comparison remains a joint model+version sensitivity analysis, not a version-robustness result, because both model and text version changed and the multi-version subset is outcome-selected.

### D4. Statistical display remains exploratory

Wilson intervals currently describe a hypothetical binomial/superpopulation sampling component, but the observed denominator is close to a captured-frame census. They do not cover frame capture, missingness, model error, version uncertainty, temporal dependence, or selection. State the stochastic/superpopulation interpretation or present them as descriptive binomial reference intervals.

Daily/weekly/monthly/subfield/tool/provider/impact views involve many correlated comparisons without shrinkage, multiplicity control, or axis-specific gold validation. Keep them explicitly exploratory until the confirmatory protocol supports them. The monthly report should also partition scan errors, skipped/fetched-not-in-run, pending, and classification failure by month rather than showing only a scan-complete denominator.

## P0-E. Close the publication, privacy, and small-cell boundary before any public push

### E1. Current-tree quarantine is important but incomplete

Commit `9a11558` removed the worst per-paper result files and unrelated Lean tree from HEAD. However, tracked files still contain corpus-derived paper-level expressive information:

- `PITCH.md:9-14` gives a small pilot result, identifies real pilot papers, and reproduces a verbatim disclosure;
- `TAXONOMY.md:146-156` identifies three real corpus papers and publishes paper-specific R1/R2/R3 judgments;
- `DESIGN_PLATFORM.md:136` names a real human-review/render case;
- code comments/help text identify real papers as operational failure/version-skew examples;
- older specs still promise open per-paper IDs/annotations and community share links, contradicting the binding aggregate-only decision.

This conflicts with `LICENSE:29-31`, `DECISIONS.md:63-67`, and `WORKFLOW.md:96-101`. Replace development cases with synthetic/deidentified examples and remove real IDs from operational comments. Exclude every development/illustration case from confirmatory sampling if it remains identifiable internally.

Create an explicit publication matrix and automated allowlist for:

- source code and synthetic fixtures;
- aggregate reports/site/data;
- paper IDs/hashes;
- machine labels;
- human labels/adjudications;
- source/PDF excerpts;
- annotation performance;
- acquisition and cloud manifests.

Binding decisions must supersede the older open-annotation/platform language, not merely coexist with it.

### E2. Git history remains unsanitized

Deleting files from HEAD does not remove the old `results/*`, awesome-validation files, result-bearing spotcheck, stale distribution ZIP, or instance inventory from Git objects. There is currently no remote or tag, which is an excellent opportunity.

Before first public push:

1. preserve a private canonical/archive copy;
2. create a clean public export or use a history rewrite on a disposable clone;
3. scan full history for secrets, personal/contact data, excerpts, labels, local paths, cloud inventory, and corpus/packet/log artifacts;
4. verify a fresh clone and `git rev-list --objects --all` inventory;
5. rotate anything credential-like if discovered;
6. add a CI publication-boundary/secret scan.

Do not publish the current `.git` merely because the current checkout looks clean.

### E3. Small-cell protection is incomplete and presently leaks singleton events

`suppress_small()` uses a threshold below 3 and applies only to selected tool/provider views. Categories, impact, locations, time series, subfield-month data, reports, and embedded client data remain unsuppressed. The current generated site contains a category with count 1 and hundreds of subfield-month cells with one or two author-use events. Exact daily numerators are embedded in JavaScript. Overlapping full/12-month/3-month views permit complementary differencing even where one table suppresses a cell. Tracked preliminary reports also contain singleton/doubleton cells.

An aggregate can still identify a paper when the source population is public and searchable. Adopt a formal disclosure-control policy across **every** HTML/JSON/CSV/report view:

- minimum positive numerator and denominator, justified by a risk model;
- primary and complementary/secondary suppression;
- consistent coarsening across overlapping time windows/subfields/axes;
- suppression-safe totals and “other” buckets that cannot be differenced;
- minimum frequency or normalization rules for exact model/tool names;
- attack-style tests that attempt reconstruction across every exported view.

Apply the same policy to tracked reports or quarantine them. A `DO NOT CITE` banner does not prevent disclosure.

### E4. Provider and local-data governance are still pre-run gates

Removing the arXiv ID and setting `store:false` are good minimization steps. They do not create zero retention. OpenAI's official data-control documentation says API data are not used for training by default unless opted in, while abuse-monitoring logs may retain prompts/responses for up to 30 days; Modified Abuse Monitoring/Zero Data Retention require approval. Record the institution/account's actual state, DPA, processors/subprocessors, region/transfers, retention/deletion, incident process, and permitted data categories before the full run. See [OpenAI API data controls](https://developers.openai.com/api/docs/guides/your-data).

The scanner can still send up to 2,400 characters from every selected TeX-like archive member before render certification, including unused/residual source. A public paper does not guarantee that every archive member was intended for publication. Prefer rendered-first/minimal evidence where scientifically possible, or document and approve the residual-source protocol. Avoid logging provider error bodies that may echo snippets.

Locally, `.env`, database/backups, corpus/logs, and annotation directories appear mode `0777` under DrvFS. POSIX mode bits may not represent Windows ACLs, so verify the actual Windows ACL/encryption/sharing state rather than assuming either safety or exposure. Move provider secrets to an OS credential store or run-scoped secret mechanism, restrict reviewer packets per reviewer, define backup/access logging and retention/deletion, and do not co-locate unblinded plant manifests with distributed packets.

The OAI harvester retains submitter names without an apparent consumer (`pipeline/harvest.py:79-95`). Drop the field from future harvests and delete/migrate existing copies unless a documented purpose and legal basis is approved.

### E5. Governance/licensing package remains incomplete

The software license and disclosure additions are positive. Before public launch, add at least:

- operative license for each frozen aggregate release (not merely “intended” CC BY);
- per-version arXiv license capture or a clear reason no item-level content is redistributed;
- privacy/data-governance notice (controller, purposes, categories, legal basis, processors, access, retention, rights/objection, breach/incident);
- correction/appeal/takedown and release-supersession ledger;
- SECURITY.md and vulnerability-reporting path;
- governance/roles/conflicts and funder-role/competing-interest statement;
- reviewer confidentiality, COI, secure-transfer, retention/deletion, and consent terms;
- CONTRIBUTING, CODE_OF_CONDUCT, CITATION.cff, CHANGELOG, data dictionary, checksums, SBOM/dependency inventory.

The funding statement should explicitly say whether Google had any role in study design, data collection, analysis, publication decisions, or provider/model choice, because a funder/provider overlap is salient even for an unrestricted gift.

## P1 engineering, reproducibility, and operations

### P1-1. V1 selection provenance is still a sidecar, not release membership

The selection SHA and basis counts reconstruct, but the scan selection sidecar stores no member preimage; the actual artifact IDs are not in `scan_items`; selection identity is not bound into `scan_runs.params_json` or the release; and the sidecar is written before run-ID uniqueness is asserted (`pipeline/scan.py:357-414`). Reusing an ID can overwrite the old sidecar before the DB rejects the run.

Materialize the exact selection in DB in one read snapshot: artifact ID, paper/version, version basis, path/hash, selector/mode, metadata cutoff, and eligibility reason. Validate run-ID uniqueness before any sidecar write, bind the manifest hash into run params, and include it in the release.

Single-version inference also depends on a mutable metadata snapshot. Record the exact version-row snapshot/cutoff that justified `inferred-single-version`.

### P1-2. Scan/archive/converter boundaries remain incomplete

The scanner has meaningful protections: bounded single-gzip expansion, per-member and total selected-text budgets, no filesystem extraction, incomplete statuses, and PDF timeout. Remaining risks include:

- unbounded tar member/header count via `getmembers()`;
- outer blob/monthly member reads into memory without an outer-size/ratio/wall-time budget;
- DB-controlled paths without resolved-path containment;
- persistent tar cache lifecycle;
- converter execution without OS CPU/RAM/process/output sandbox limits;
- broad scanning of every TeX-like member rather than a rendered include graph;
- annotation re-extraction using a less strictly bounded path.

Add member-count/header/compression-ratio/time limits, streaming/capped reads, resolved containment, explicit cache close, and a sandboxed converter. Longer term, use the TeX include graph/rendered text as the disclosure-evidence primary and quarantine unreferenced residuals.

### P1-3. Acquisition and metadata reconstruction still have gaps

The refill authorization truth table and content-diverting artifact writes are good. Remaining items:

- v1 selection/acquisition manifests and attempt ledgers are filesystem sidecars rather than signed/materialized run objects;
- exact terminal outcomes and response metadata are not fully connected to release membership;
- OAI deleted records are ignored rather than tombstoned (`pipeline/harvest.py:54-57`);
- reparse is now recursive, but metadata reconstruction still depends on `INSERT OR REPLACE` current-state semantics;
- per-version license is absent from the artifact/version spine.

Preserve tombstones and immutable harvest manifests, capture per-version licenses, and make clean-clone reconstruction from documented sanctioned inputs demonstrable.

### P1-4. AWS producer remains unsafe to reuse

The importer has strong two-direction reconciliation and the completed local import matched its checksums. The remote producer still appends directly to long-lived monthly tars, can duplicate partial members after a crash, continues after permanent chunk failures, and prints `ALL DONE`/exits success. `overnight_sync.sh` is commendably disabled by default, but its force path still terminates infrastructure after size-only transfer checks rather than producer completion + hash + importer reconciliation.

Do not reuse the producer without closed content-addressed per-chunk shards, fsync/atomic commit, a signed attempt/member ledger, nonzero failure exit, exact end reconciliation, minimal IAM/instance role, encrypted storage, budgets/alarms, and automatic teardown only after local importer success. Infrastructure and recovery/incident controls should be code-defined.

### P1-5. CI/release/deployment still stops at unit tests

`.github/workflows/ci.yml` says “tests + site build” but runs pytest only. Positive: actions are SHA-pinned and no corpus/secrets/deployment are present. Add:

- explicit least-privilege `permissions: contents: read`, `persist-credentials:false`, timeout, and concurrency cancellation;
- exact dev dependency hashes or a documented lock-generation/verification process;
- migration-from-empty and migration-from-old fixtures;
- prompt/schema parity and taxonomy/human parity;
- adaptive split/provenance and multiprocess lease/campaign tests;
- synthetic release-candidate -> packet -> ingest -> adjudication -> estimator -> release -> site E2E;
- deterministic double site build and byte/hash comparison;
- publication-boundary, small-cell reconstruction, secret/history, dependency/license/SBOM checks;
- HTML/link/accessibility/security-header tests;
- a separate protected deployment workflow with preview, approval, immutable artifact, rollback, and drift detection.

### P1-6. Site accessibility/security/reach need a release pass

The static, tracker-free architecture is excellent for privacy, resilience, and cost. Before launch:

- give every SVG a chart-level accessible name/description;
- make tables server-rendered and visible without JavaScript, with a `<noscript>` summary;
- support keyboard/focus/touch interaction, not mouse-only tooltips;
- test screen reader, mobile widths, high contrast, and reduced motion;
- remove remaining `innerHTML` patterns before any contributor-controlled data;
- deploy CSP, `nosniff`, referrer, permissions, frame, and HSTS headers on a capable host;
- add canonical URL, Open Graph/social card, favicon, sitemap/robots behavior by release state, stable methods/validation/correction/contact pages, DOI/CITATION, aggregate download schema and checksums.

Do not optimize reach before claim validity, but prepare versioned releases and a correction feed rather than a mutable headline. The submission-growth tile should remain explicitly contextual/no-causal-claim.

## Review-7 finding status

| Iteration-7 issue | Round-8 status |
|---|---|
| Taxonomy 2.1 ambiguous / needs new version | **Partly fixed:** v2.2 exists; owner sign-off and R4 edge rule still open |
| Human could not record R5 `none` | **Partly fixed:** new impacts appear; human/machine flags/invariants still differ |
| Calibration counts inconsistent/manual | **Core binary counts fixed; axis metrics and non-evaluable implementation remain** |
| Fixed batches repeat truncations | **Prospectively fixed by bisection; provenance/tests and existing 172 failures remain** |
| Budget not durable/hard | **Improved:** durable reservations and mandatory cap; campaign/cross-process semantics still broken |
| Concurrent resume | **Concept added; lease acquisition/heartbeat/release are not safely fenced** |
| Final gold not release-bound | **Unresolved / explicitly deferred** |
| Freeze not materialized/gold-gated | **Unresolved** |
| V1 population not identified | **Unresolved; honest preliminary bounds retained** |
| Per-paper expressive files in HEAD | **Worst files removed; real examples/reports/site cells and history remain** |
| Vendor/privacy/governance | **Some minimization fixed; institutional/account/retention governance unresolved** |
| CI/deploy/accessibility | **Largely unresolved** |

## Recommended sequence from here

### Gate A — before the full v2.2 API run

- [ ] Owner signs the exact R4 instrumentation scope, R5 split, primary numerator, and tool-family scope.
- [ ] Fix all prompt/schema wrapper/enum/required-flag contradictions.
- [ ] Unify human and machine cross-field validation; make `TOPIC_ONLY + method_component` recordable.
- [ ] Define paper-level impact/flag aggregation and site numerator behavior.
- [ ] Complete two-human-plus-Luna synthetic R4/R5 comprehension exercise.
- [ ] Create approved budget campaign object; enforce cap atomically across processes.
- [ ] Replace run lease with atomic acquisition, holder fencing, and time heartbeat.
- [ ] Persist exact logical request / split / physical attempt / spend / response / snippet linkage.
- [ ] Explicitly pin inference settings and record returned provider identity.
- [ ] Add and pass adversarial regression tests for every item above.

### Gate B — before drawing the final gold sample

- [ ] Materialize one immutable analysis snapshot/release candidate from the completed rerun.
- [ ] Bind exact frame, selection, artifacts, labels, evidence, render states, protocols, and missingness.
- [ ] Implement `annotate build --snapshot/--release-candidate`; no raw-run final mode.
- [ ] Build exact-artifact contexts and pinned PDFs; hash every data/packet/order artifact.
- [ ] Separate hidden allocator/plant manifests from reviewer packets.
- [ ] Fail-closed ingest with reviewer/item/version/codebook/packet bindings and uniqueness.
- [ ] Prespecify the shared double-coded subset and recruit the third adjudicator.
- [ ] Implement evaluability, COI, bounded-search, first-pass/adjudication, and all axis fields.
- [ ] Freeze design-weighted estimators, intervals, missingness bounds, publication thresholds, and seeds.
- [ ] Run a full synthetic E2E exercise before exposing the real sample.

### Gate C — before public release/repository

- [ ] Finalize selected-frame/partial-identification versus full-population claim.
- [ ] Create validated release object referencing snapshot + gold + adjudication + estimator outputs.
- [ ] Make report/site consume release ID only and build deterministically from a clean tree.
- [ ] Apply formal primary/complementary small-cell suppression to every artifact/view.
- [ ] Remove/deidentify real development cases; reconcile older specs with aggregate-only policy.
- [ ] Sanitize Git history and verify a fresh public clone.
- [ ] Complete provider/privacy/legal/licensing/correction/security/reviewer governance.
- [ ] Verify workstation/reviewer ACLs, encryption, access, backups, and retention.
- [ ] Run accessibility, security-header, link, mobile, no-JS, and deterministic deploy tests.
- [ ] Publish immutable checksums, aggregate schema, data dictionary, CITATION/DOI, changelog, and correction feed.

## Bottom line

The project is scientifically and technically much stronger than in the first reviews. The current calibration is useful and now mostly described with the right denominators; the v1 acquisition/scan/classification/render chain is a real large-scale accomplishment; and the decision to keep the current site explicitly exploratory is responsible.

The next full classification run should still wait. Three small-looking discrepancies—the stale `none` instruction, the unrecordable human `method_component`, and the absence of a real campaign object—would otherwise make a costly run scientifically inconsistent and financially mis-scoped. The lease/request-provenance defects add avoidable operational risk.

After those are closed, the paid rerun is reasonable. The final gold study must then be treated as a separate engineering deliverable, not as a few new CLI flags: it needs immutable snapshot membership, exact-version packet evidence, prespecified shared assignments/adjudication, fail-closed chain of custody, and executable estimators. Public launch should follow only from that validated release object, under one rigorously enforced aggregate-publication boundary.

