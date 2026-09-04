# ArxivObservatory repository review — iteration 11

**Audit snapshot:** Git commit `5a95eabb1aa60285ffb18d7d212682bcbb90fdc0`, tree `56d87806670905b6e95b37dbc774d2b52e502408`, committed 2026-08-13 13:03 CEST. The worktree was clean before this review file was added.

**Primary delta reviewed:** commits `43cf8be`, `9c8f1fc`, and `5a95eab` after the iteration-10 snapshot, especially taxonomy v2.5/v2.6 and the delegation criterion; the v2.6 comprehension and 150-paper adherence exercises; scoped-run identity; four-class budget accounting; atomic spend/attempt admission; run-lease fencing; R5 overlapping states; human annotation parity; freeze/release behavior; and the still-open publication boundary.

**Audit boundary:** read-only except for creating this report. I did not call a model/provider API, start or stop a pipeline job, alter the database, corpus, annotations, campaign, or cloud state, contact arXiv, or publish anything. Restricted annotation material is discussed only in aggregate. I checked current official OpenAI documentation where pricing and data controls directly affect the proposed paid run; I did not repeat a systematic verification of the scientific bibliography.

## Executive verdict

This is another meaningful improvement. The v2.6 instrument is much shorter and more coherent than the v2.3–v2.5 precedence stack; its exact taxonomy/manual/prompt/schema hashes reproduce; the human polarity descriptions are generated from the same source as the model prompt; scoped adherence runs now have immutable target identity and cannot feed population reports; response usage fails closed; reservations and pre-dispatch attempts are admitted atomically; model/campaign/holder checks occur in admission; R5 overlapping paper states reach the report and site; and the current suite has **146 passing tests**.

The repository is nevertheless **not ready to start the full paid v2.6 classification run**. Four pre-run blockers are direct consequences of the new taxonomy and should be fixed before spending:

1. **The v2.6 comprehension result is misreported.** Polarity and scalar impact were stable in all 16 synthetic cases, but flags were stable in only **13/16**, categories in **14/16**, and all recorded axes in only **11/16**. `DECISIONS.md` says polarity/impact/flags were 16/16 stable. The tracked summary even labels the instrument “v2.5.”
2. **R5 is still lossy within one merged snippet.** The provider schema emits one scalar impact per snippet. A snippet containing both contributing and explicitly fruitless/vague uses cannot preserve the full set; the synthetic `mixed_states` expectation is recorded but never evaluated. Paper rollup only recovers multiple states when they happen to be split into separate classifier items.
3. **The new `external_ai_artifact` diagnostic is dropped downstream.** `paper_rollup()` special-cases only `method_component`. In the live v2.6 scoped check, all papers carrying the new diagnostic—**2 of 2**—lose it in rollup.
4. **The campaign tariff is not actually the tariff bound by the run.** The active campaign stores an obsolete two-rate snapshot, while reservation and settlement use the mutable live Python table. That table also prices Luna cached reads at `$0.25/M`; the current official page says `$0.02/M` cached input and `$0.25/M` cache writes. This is conservative for the cap but makes the ledger and provider reconciliation wrong.

Exact owner sign-off and the human half of the v2.6 comprehension exercise are explicitly pending. Because v2.6 substantively narrows the numerator, the two intended graders should complete the boundary exercise **before**, not in parallel with, the expensive run. A disagreement at that point should produce v2.7 rather than a post-hoc reinterpretation of v2.6 labels.

The project is also **not ready for the final two-grader gold study**. The only builder still hard-codes every packet as calibration-only, reads mutable current files instead of the scanned artifact, blindly reuses cached contexts, fails open without a manifest, does not bind exports to packets or reviewer assignments, provides no guaranteed shared double-coded subset, and has no adjudication or design-weighted estimator implementation. Two graders are sufficient for first-pass reliability, but the project’s own anchoring protocol still needs a third blinded adjudicator for disagreements.

A frozen scientific release and public launch remain later, separate no-go decisions. Release rows are mutable-query digests rather than materialized analysis data; evidence/gold/campaign gates are optional; the site consumes run IDs; public small-cell control remains incomplete; a latent DOM-XSS sink remains; and governance/history/licensing/deployment work is unfinished.

### Readiness call

| Activity | Readiness at this snapshot |
|---|---|
| Correct v2.6 instrument tests and run a two-human-plus-Luna comprehension exercise | **Ready now and required next** |
| Full paid v2.6 classification of the selected v1 scan | **No-go until Gates A and B pass** |
| Final two-grader gold study | **No-go until Gate C is implemented and dry-run** |
| Private inspection of explicitly exploratory data | **Acceptable with restricted access and existing warnings** |
| Frozen scientific release or prevalence claim | **No-go until Gate D** |
| Public Git repository or real-data site | **No-go until Gate E** |
| Three-year math-arXiv population prevalence | **Not identified by the selected/incomplete v1 frame** |

The shortest safe path is: correct and human-test the instrument; fix multi-state and diagnostic aggregation; sign one exact bundle; close the old campaign and create a fresh tariff-authoritative full-run campaign; finish transactional fencing/provider governance; run classification; materialize a release candidate; build and dry-run final gold from exact artifacts; adjudicate and estimate; then generate disclosure-controlled public artifacts from that release alone.

## Snapshot and verification

### Automated and integrity checks

- `python3 -m pytest -q -p no:cacheprovider`: **146 passed in 3.39 s**.
- Python AST parsing succeeded for all 37 tracked pipeline/test Python files checked.
- `python3 -m pip check`: no broken requirements.
- `bash -n`: passed for all tracked shell scripts.
- `git diff --check da362e5..HEAD`: passed.
- SQLite `PRAGMA quick_check`: `ok`; `PRAGMA foreign_key_check`: no reported violations in the immutable read-only snapshot.
- The worktree was clean before this report was created.

The new tests cover scoped report refusal, generated human definitions, external-artifact validation/ingest, R5 human fields, class-aware usage validation, unknown-usage settlement, cache-write charging, campaign-required calls, atomic reservation/attempt insertion, transactional store fencing, credential scrubbing, and provider error minimization. Important gaps align closely with the findings below: there is no test for the official cached-read price, campaign-snapshot authority, terminal-state takeover, external-artifact paper rollup, multi-impact output within one snippet, comprehension-summary correctness, final-gold chain of custody, or release-only generation.

### Point-in-time local data state

The database appeared quiescent during the final snapshot. Counts are local state, not a clone-reconstructible release:

- schema version: **8**;
- papers / versions: **235,342 / 418,232**;
- files / artifacts: **169,166 / 187,918**;
- scan runs / items / hits: **4 / 281,870 / 982,232**;
- classification runs / items / evidence edges: **9 / 145,769 / 340,270**;
- render checks: **14,758**;
- human annotations: **150**, all one reviewer/project and codebook v2.0;
- API attempts: **255**;
- releases: **0**;
- active run leases: **0**;
- full/population v2.6 classification runs: **0**.

The v2.6 scoped run `cls-20260813T110056` is correctly marked `complete_scoped`: 199/199 valid items from 53 papers, 458 evidence links, 55 responded attempts/reservations, and no target leakage. It produces 35 paper-level `author_use` labels. Its target preimage contains 150 canonical IDs and matches the recorded hash. This is a strong supported-path exercise.

It is still development evidence: the run records `9c8f1fc-dirty`, only 194/199 quotes are grounded, render status is unchecked, it is in-sample, and its human comparator is the old one-reviewer v2.0 calibration. Report/freeze correctly refuse it.

The active campaign contains approximately **$0.41682055** in ledgered spend. It remains open and unreconciled. Its stored purpose stops at v2.5, while its spend includes v2.6 work; its snapshot contains only base input/output rates. There are also historical/correction spend rows not paired with physical attempt rows, so it should remain a development campaign rather than become the full-run authority.

The v1 scan remains partial: 112,447 selected papers, 110,770 `ok`, 54 unknown-format, 2 incomplete, and 1,621 skipped PDF-in-tar items. The three-year report frame remains much larger than the scan-complete v1 cohort. A “full run” here can mean complete classification of the selected v1 scan; it cannot mean complete coverage of the three-year math-primary submission frame.

## What is genuinely stronger since iteration 10

The following improvements are substantive and should be preserved:

- the v2.6 taxonomy/manual/prompt/schema hashes in `DECISIONS.md` reproduce exactly;
- the delegation criterion gives the owner’s intended construct a shorter, inspectable rule rather than accumulating case precedence;
- taxonomy version discipline was respected before any full v2.6 run;
- human polarity descriptions now come directly from `taxonomy.POLARITIES`;
- the annotation manifest records the taxonomy/manual/prompt/schema bundle hashes;
- machine and human validators share cross-field invariants, including non-author catalytic rejection;
- scoped targets are canonicalized before protocol creation, with count/hash in protocol and full preimage in the run row;
- scoped runs terminate as `complete_scoped`, and report/freeze refuse them;
- missing/malformed usage retains the conservative reservation rather than settling at zero;
- reservation and pre-dispatch attempt identity commit together in one `BEGIN IMMEDIATE` transaction;
- admission revalidates campaign status/provider/model and the lease holder;
- provider attempts retain request/returned-model/fingerprint/usage and input hashes on the supported classifier path;
- selected-provider credential loading removes unrelated provider keys from the process environment;
- IDs are omitted from provider prompts, OpenAI requests use `store:false`, redirects/ambient proxy state are disabled, and raw error/refusal bodies are minimized;
- report and site now expose overlapping contributing/zero/undetermined paper counts rather than deriving them by scalar subtraction;
- the exploratory site remains tracker-free, `noindex`, visibly unreleased, and machine-readable as `do_not_cite`;
- CI actions remain SHA-pinned, and no automatic deploy can silently promote the current state.

Several are producer-level repairs without the corresponding consumer or release gate. The sections below make that distinction explicit.

## Gate A — finish and sign the v2.6 measurement instrument

### A1. The tracked comprehension claim is wrong

`DECISIONS.md:26-35` says the 16 synthetic v2.6 cases were “16/16 polarity/impact/flags stable” and “16/16 as intended.” The source artifact does not support that statement:

- polarity stable: **16/16**;
- scalar impact stable: **16/16**;
- flags stable: **13/16**;
- categories stable: **14/16**;
- every recorded axis stable: **11/16**;
- exact authored expected flag set: **44/48 repetitions**, with only 13/16 vignettes matching on all three runs.

The unstable flags occur precisely at new R4 boundaries: fresh machine-generated features, a perplexity instrument, and a dual-role case. `annotation/comprehension_v26/stability.md` visibly marks those `N`, yet its header says “instrument: taxonomy v2.5,” and its prose reduces “matches expected” to polarity. The JSON’s `polarity_matches_expected` field does not test expected impact or flags; `mixed_states.expected.impacts_any` is not tested at all.

The JSON’s `spent_usd` value is also cumulative campaign spend through the exercise, not the exercise’s incremental cost. Label it accordingly or compute the increment from the bound reservation rows; otherwise even this small dev artifact cannot be reconciled without external context.

Correct the generated table, the decision log, and every downstream claim before sign-off. Add an executable checker that hashes the vignette set and instrument, validates all expected fields, reports per-axis exact agreement/stability, and fails when prose claims exceed the computed result. The current result is encouraging for polarity, but it is evidence that the new diagnostic boundary is not yet stable.

### A2. The delegation construct is coherent but narrower than “AI use” or “AI assistance”

The owner has deliberately chosen a defensible construct: `author_use` requires both active invocation during the research and a delegated intellectual role traditionally performed by researchers (`TAXONOMY.md:20-52`). Fresh embeddings, feature vectors, scores, and reused AI artifacts are excluded as non-delegated inputs.

That is not equivalent to “whether the authors actually used an AI system,” despite the purpose text at `TAXONOMY.md:3-6`. Authors who run a frozen model to produce research features really did use AI; v2.6 intentionally excludes that use from the numerator. Likewise, `topic_only` now includes AI used as a research instrument or data source even when AI is not the paper’s topic. The polarity name therefore hides a substantive state.

There are two acceptable ways forward:

1. add a distinct polarity such as `nondelegated_ai_input` / `ai_instrument_or_artifact_use`; or
2. retain `topic_only`, but make every human/public description say it includes actual instrumental/artifact use and always report `external_ai_artifact` as a separate slice.

The current gold definition is directly stale: `GOLD_STUDY.md:48-50` describes `TOPIC_ONLY` as AI “not used for this paper.” Public/report copy also continues to say “AI assistance” or “authors used generative-AI tools” without the delegation qualifier (`pipeline/build_site.py:485-502,553-562`). The primary estimand should be named precisely, for example:

> Scanner-visible disclosure of actively invoked generative-AI/LLM systems performing delegated, traditionally human intellectual work in the conduct or communication of the paper.

Report non-delegated instrument/artifact use alongside it, not inside an apparently “no use” residual bucket.

The classifier’s first sentence still primes the task as measuring “DISCLOSED AI assistance” (`pipeline/classify.py:58-62`). Replace that with the exact estimand too: priming the model with a broader everyday term and then asking it to apply a narrower technical rule is avoidable construct noise.

### A3. The human-counterfactual boundary still needs operational examples

“A human could have done the work” is useful intuition, but the current rules still leave adjacent outputs underdetermined:

- similarity labels are delegated human judgment, but similarity scores are machine-only measurement;
- numerical/symbolic computation is an `author_use` category, while model scores are excluded instrument output;
- LLM labeling is delegated, but a classifier’s discrete class output could also be described as an instrument reading;
- synthetic data is delegated human-type work, while pre-existing AI-generated data is an external artifact;
- “traditionally human” can vary by field and level of abstraction.

The rule “judge the role, not the mechanical operation” is the right direction. Make it a short dataflow decision grid: what research question was delegated, what semantic judgment or mathematical task was requested, what output was consumed, and whether the output is merely a fixed representation/measurement of a model. Include paired adversarial cases for scores versus judgments, AI numerical computation versus instrument readings, fresh versus reused synthetic data, dual roles, and model components. The three observed flag-instability cases should be mandatory exercises, not quietly treated as success.

### A4. Attempted use is a small logical exception to the primary definition

The v2.6 definition requires that AI output “entered the conduct or communication” of the paper (`TAXONOMY.md:20,30-38`), but R5 includes an explicitly fruitless attempt whose output made no contribution and was not used (`:113-144`). Both owner choices can coexist, but the text should say so explicitly: a disclosed invocation undertaken for a delegated role qualifies as attempted use even when no output entered the final process; `zero_contribution` is the named exception to the output-consumption clause.

Without that sentence, a literal grader can correctly reason that the R5 case fails the main conjunction. This is exactly the kind of ambiguity the two-human comprehension check should catch.

### A5. R5 remains lossy within a classifier item

The provider schema contains one `epistemic_impact` scalar per snippet (`pipeline/llm_api.py:461-498`). The classifier may merge nearby hits into one snippet. When one merged context discloses a contributing use plus an explicitly fruitless attempt or vague use, the model has no field in which to return the secondary state.

`paper_rollup()` now constructs `impacts_seen` and the overlapping `has_*` fields, but only by unioning scalar labels across **separate** classifier items (`pipeline/report.py:192-231`). It cannot recover information collapsed within one item. The synthetic `mixed_states` vignette demonstrates the gap: its expected data list multiple impacts, while the check evaluates only the maximum `result_bearing` value.

Before the full run, add schema-visible overlapping state fields—for example `impacts_present`, or `has_explicit_zero_attempt` and `has_undetermined_use`—and validate their consistency with the scalar maximum. Use the same representation in machine labels, human forms, paper rollup, report/site, and gold analysis. The current human-only `r5_states` checkboxes have no machine counterpart, so “one label space” remains only partial.

Any prompt/schema/manual change here should get a fresh protocol hash and, if semantics or grader instructions change, a taxonomy version bump (preferably v2.7). Re-run the synthetic and scoped checks under the final bundle.

### A6. `external_ai_artifact` is lost in paper rollup

The validator and human ingest correctly preserve `external_ai_artifact` for non-author polarities. Downstream, `paper_rollup()` only carries `method_component` when a higher-ranked polarity replaces a prior label or when a lower-ranked snippet contributes a diagnostic (`pipeline/report.py:180-191,215-219`). The new flag is omitted from both branches.

This is realized, not theoretical: the v2.6 scoped run has seven flagged snippets across two papers, and current rollup reports the diagnostic on **zero** papers. Both are lost. Since v2.6’s construct depends on separating delegated use from non-delegated AI inputs, losing every observed diagnostic makes the exclusion unauditable.

OR every polarity-independent diagnostic across every eligible snippet, independent of row order, winner polarity, and evidence gating. Add permutation tests with mixed `author_use`, `topic_only`, `method_component`, and `external_ai_artifact` snippets. Sampling and public/report slices should consume the preserved state.

### A7. Human/model rule parity is improved but not yet frozen

The basic polarity tooltips now use the exact `taxonomy.POLARITIES` strings—a real fix. The model prompt additionally receives the detailed R1–R5 decision block and boundary conventions. A reviewer who receives only the generated packet sees compact tooltips and a textual reference to `TAXONOMY.md`, not necessarily the exact frozen manual bytes or a mandatory acknowledgement that they read them.

There are also two current semantic/text drifts despite `TAXONOMY.md:6-8` claiming a unit test keeps the copies in sync:

- machine `author_use` includes “authors **(or collaborators)**” (`pipeline/taxonomy.py:53-65`), while the manual and owner decision say authors. Collaborator use can change the numerator; decide and state the scope in both places;
- the machine `method_component` description still references “R4 steps 1/3” (`pipeline/taxonomy.py:191-194`), while v2.6 routes that state in step 4. That stale string is injected into the provider prompt.

`tests/test_taxonomy.py` checks version/vocabulary/token presence, not semantic equivalence. Generate shared rule blocks from structured data where possible and add exact expected-text/hash tests for every grader-facing block.

For the final instrument exercise and gold packets:

- embed or package the exact manual, not a mutable filename reference;
- display its hash and instrument version in the packet;
- require reviewers to confirm the manual hash before export;
- include the full R4/R5 decision procedure and examples, not only polarity summaries;
- define how human `yes/no/unsure` diagnostic answers map to machine booleans and non-evaluable states;
- reject contradictory combinations such as an explicit “no” answer plus the same flag in a hand-edited export.

### A8. Human comprehension and exact owner sign-off must precede the full run

`DECISIONS.md:37-40` correctly records two open gates: end-to-end owner reading/sign-off and the human half of the exercise. It currently allows the human half to proceed in parallel with the full rerun. That is too risky after a substantive v2.5→v2.6 scope change and the newly observed flag/R5 gaps.

Have both intended graders independently code the exact frozen vignette set under the candidate final manual, blinded to Luna. Report polarity, scalar and overlapping impacts, categories, both diagnostic flags, and confidence/unclear outcomes. Resolve disagreements without showing machine labels, revise/bump if needed, then sign the exact taxonomy/manual/prompt/schema/vignette hashes. Only then launch the full run.

### Gate A acceptance criteria

- corrected, executable comprehension report with honest per-axis results;
- precise estimand name and non-misleading treatment of instrumental/artifact use;
- explicit R5 attempted-use exception and a practical delegation decision grid;
- multi-state R5 schema shared by machine, human, rollup, and outputs;
- order-independent preservation of all polarity-independent diagnostics;
- both intended graders independently pass/adjudicate the frozen vignettes;
- dated owner sign-off on the exact final bundle and primary quantities.

## Gate B — make the paid full run financially, transactionally, and ethically closed

### B1. The campaign snapshot is hashed but not authoritative

A new campaign stores `price_snapshot_json`, and the classifier hashes that string into its protocol. However:

- `attach_ledger()` validates only approval/provider/model/cap/status;
- `get_campaign()` returns the snapshot as an opaque string;
- admission checks provider/model/cap but not snapshot completeness/equality;
- `_price()`, reservation, and settlement use the mutable module-level `PRICES_USD_PER_MTOK`, not the campaign snapshot (`pipeline/llm_api.py:149-202,269-350,544-567,647-771`).

The live campaign exposes the defect. Its stored snapshot has only `{input: 0.2, output: 1.2}`, while v2.5/v2.6 calls were charged with the later four-class table. The run protocol therefore binds one tariff identity and applies another.

Do not reuse this campaign for the full run. Reconcile and close it, then create a fresh v2.6/v2.7 campaign whose snapshot contains every billed class, source/as-of/account evidence, long-context multipliers, and model endpoint. Parse and validate it at attach; recheck its hash in each admission transaction; use the parsed snapshot—not global code constants—for both reservation and settlement. A tariff change should require a new campaign or signed amendment/protocol, not silently change an active campaign’s accounting.

### B2. Luna cached reads are priced incorrectly

`pipeline/llm_api.py:53-57` sets both `cached_input` and `cache_write` to `$0.25/M` and says both are 1.25× base. The current direct [official GPT-5.6 Luna page](https://developers.openai.com/api/docs/models/gpt-5.6-luna) lists:

- input: **$0.20/M**;
- cached input: **$0.02/M**;
- output: **$1.20/M**;
- cache writes: **1.25× base input = $0.25/M**.

The hard cap is conservative because `$0.25` remains the worst input rate. The ledger is still wrong. The v2.5/v2.6 comprehension calls contain 130,338 cached-read tokens; pricing them at `$0.25` rather than `$0.02` overstates recorded spend by approximately **$0.02998**. Correct the rate, archive/hash authoritative tariff evidence, and reconcile historical/correction rows against provider billing.

The current campaign total of about `$0.41682` is therefore a conservative ledger figure, not a verified account charge. Do not quote it as actual spend until reconciliation.

### B3. The active campaign’s authority does not match the proposed run

The active campaign began as a 150-case adherence campaign and was amended through v2.5. Its current purpose/event history does not mention v2.6, yet it already funded v2.6 work and `DECISIONS.md` contemplates using it for the confirmatory rerun. `amend-campaign` updates the current purpose in place while appending an event, so calling the authority itself append-only is inaccurate.

Create a fresh full-run approval rather than repeatedly stretching the pilot. Bind owner, purpose, exact scan/target protocol hash, model, inference controls, tariff snapshot hash, cap, expiry, and allowed run IDs. Campaign creation/amendment/closure should be tamper-evident; schema constraints/FKs/triggers or a signed owner approval artifact should protect the authority from ordinary DB writers.

Closure should fail while reservations are unresolved and should record provider-billed dollars plus an explicit reconciliation tolerance, not only a free-text note. The old campaign has historical/correction spend rows without one-to-one attempt lineage; that is acceptable as documented development history, not as a clean release campaign.

Closure itself is currently racy: it computes ledger spend before opening its write transaction, while a request admitted just before closure can still settle afterward. The resulting “final” amount and reconciliation note can therefore cease to be final. Close admission atomically, require no active authorized run lease and no `reserved` rows, wait for every admitted request to reach a terminal state, and then append a distinct provider-console reconciliation event and amount. Repeated closure/reconciliation should be rejected or represented as an explicit superseding event.

### B4. Final run state still has a lease takeover race

Result and error stores are now holder-checked, and paid admission verifies the holder inside the reservation transaction. This is a strong repair. The final `finish_classification_run()` call remains unconditional (`pipeline/classify.py:1208-1226`; `pipeline/runs.py:81-86`). The keeper can discover lease loss after the last result store while the local `lease_lost` boolean remains false; the old process can then overwrite a successor’s terminal status/counts.

The migration adds a `generation` column, but acquisition never increments it and no business row uses it. Either remove the misleading claim or implement a real monotonically increasing fencing generation. Terminal status must be a compare-and-set in the same transaction as a durable holder/generation check. Attempt-linkage updates at `classify.py:1156-1170` should also be tied to the request/holder state; post-response accounting should remain append/reconciliation-safe without allowing stale mutation of another worker’s logical record.

Add a multiprocess fault test that pauses the old process immediately before finalization, lets a successor take over and complete, then resumes the old process. The successor’s state must remain authoritative and no duplicate paid dispatch or label write may occur.

### B5. Classification does not freeze or validate its scan target

Before creating the run, the classifier binds scan-run IDs but does not require that each run exists, is terminal/accepted, or has a frozen complete item/hit preimage. It then classifies whatever matching `scan_hits` happen to exist and can mark zero or a transient subset complete (`pipeline/classify.py:904-978,1015-1035,1208-1226`). A typo, a still-running scan, or later-added hits can therefore produce a misleading terminal classification.

For the paid run, validate each consumed scan run and its policy first. Materialize/hash the complete ordered classifier-input preimage (paper/version/member/snippet/evidence IDs and hashes), bind it into the protocol, and require terminal valid classification items to partition that target exactly. The known v1 scan may remain policy-accepted `partial` with explicit reason-coded exclusions, but its selected membership and hit set must be immutable before payment.

### B6. The v2.6 adherence evidence is development-only

The supported path is now coherent: target preimage and protocol match, every classification item has evidence, every paid request in the run has an attempt/reservation mapping, and the scoped status prevents publication use. Preserve this.

Do not overstate it:

- code commit is `9c8f1fc-dirty` and cannot be reconstructed as a clean tree;
- the exercise is in-sample and only 53 papers reached the model;
- all human labels are v2.0 and one reviewer;
- polarity is stable relative to v2.5, but scalar impact changes on 5/35 author-use papers and full observed impact sets on 6/35;
- 5 quotes are not grounded and no render gate was applied;
- the returned model remains a rolling alias and system fingerprints are absent in the current attempts.

`TAXONOMY.md:203-206` should say “no full/population production run under v2.2–v2.6; scoped development labels exist” rather than implying no labels exist at all.

### B7. Provider and local-data governance remain pre-run gates

The technical boundary is better: direct non-agentic requests, strict schema, no arXiv ID, selected-key scrubbing, `store:false`, fixed endpoint, no redirects, and no ambient proxy/netrc.

The snippets are still searchable and re-identifiable. The scanner reads every text-like archive member before rendered/include-graph validation (`pipeline/scan.py:82-140`), so unused/residual TeX can reach the provider. Removing the arXiv ID does not make that content anonymous.

Current official [OpenAI API data-control documentation](https://developers.openai.com/api/docs/guides/your-data) says API data is not used for training absent opt-in, while default abuse-monitoring retention may retain content and modified/zero-retention controls require approval; prompt caching has its own retention behavior. `store:false` is useful but not a zero-retention agreement.

Before corpus dispatch, record and approve:

- the actual organization/project training-sharing setting;
- ZDR/MAM eligibility and state;
- DPA, region/transfers, subprocessors, retention/deletion, and incident route;
- exact allowed data categories and whether residual source is permitted;
- minimum/rendered-only context policy;
- access/retention/deletion for snippets, responses, attempts, PDFs, annotation packets, DB/WAL, logs, and backups.

Local `.env`, databases, corpus, logs, backups, and annotation files appear mode `0777` through DrvFS/9p. Those bits do not establish the underlying Windows ACL either way. Verify inherited ACL/share/sync/BitLocker/backup state, use a least-privilege spend-limited project key, and preferably run restricted data from a protected native filesystem/credential store.

Legacy submitter data also remains: future parsed rows omit it, but the database and raw OAI archives/backups retain old values. Purge/VACUUM/expire copies if there is no justified purpose, or document and protect the retained data.

### B8. “Full classification” must be scoped honestly

The intended v1 input is still a selected, incomplete acquisition frame. A clean complete v2.6 run can classify every classifiable snippet in that scan; it cannot recover the roughly 47.5k three-year cohort papers outside scan-complete v1 membership or undo the outcome-related flagged-first acquisition design.

Name the operation “full classification of the selected v1 scan,” preserve explicit-v1 versus inferred-single-version strata, and keep full-frame acquisition extrema separate. Gold can estimate measurement properties in release membership; it cannot make the missing tail representative.

### Gate B acceptance criteria

- old campaign reconciled and closed; fresh exact-scope full-run campaign;
- correct cached-read/write prices and immutable authoritative tariff snapshot;
- campaign purpose/owner/scope/expiry/tariff bound and tamper-evident;
- no unresolved reservations and provider-console reconciliation procedure;
- holder/generation fenced terminal transition and takeover fault tests;
- terminal accepted scan and immutable full classifier-input preimage;
- provider account/privacy/minimum-text decision documented;
- verified local ACL/key/retention controls;
- run and public language limited to the selected v1 scan/frame.

## Gate C — implement the final two-grader gold study before fielding it

### C1. The only builder is intentionally calibration-only

`pipeline.annotate build` still hard-codes `intended_use = calibration_only_never_release_validity` and a prominent calibration banner (`pipeline/annotate.py:245-385`). It accepts raw scan/classification run IDs, not a materialized release, and does not validate clean/terminal/unscoped compatible runs.

This is a useful safety guard. `GOLD_STUDY.md` and `WORKFLOW.md` nonetheless present the same command as the final study path. Do not remove the guard until a separate release-bound command exists. A final builder should accept exactly one release-candidate ID, verify its policy and hashes, and refuse exploratory/scoped/dirty/partial inputs.

### C2. Packet evidence is not bound to the scanned artifact

Context extraction queries the current `files` row, not the exact artifact SHA selected by the scan (`pipeline/annotate.py:120-138`). If `contexts.json` exists, it is reused solely by existence (`:319-336`). The manifest has an instrument bundle but no per-item artifact/context/PDF/packet hash. A NULL scan version can still fall back to mutable current metadata/PDF state.

Packets also display current `papers.title` and especially `papers.comments` (`pipeline/annotate.py:259-267,363-369,625-634`). Those are latest mutable metadata, not necessarily metadata contemporaneous with the v1 artifact. A disclosure added to later-version comments can contaminate a v1 human verdict even if the PDF is eventually pinned. Bind version-specific metadata and its hash, or omit any field that cannot be proven contemporaneous with the target artifact.

The exact version-skew failure that invalidated one calibration item can recur. For every final item, bind:

- release member and scan/classification/evidence IDs;
- effective version and version basis;
- artifact ID, SHA, format, and permitted license/access path;
- context bytes/hash and extraction algorithm/version;
- PDF bytes/hash and renderer version/status;
- taxonomy/manual/prompt/schema hashes;
- reviewer assignment/order and final packet hash.

Never reuse a cache unless its complete identity hash matches. The reviewer must see exactly the bytes the classifier’s evidence came from.

### C3. Blinding and access control are not separated

The builder puts `manifest.json`—including strata, plant identities, and full assignment—beside `contexts.json`, PDFs, and both reviewer packets in the same output directory. A comment says reviewers should not open the manifest; that is not blinding or access control. The files inherit default permissions.

Use an owner-only allocator store and separate reviewer-specific packages. Each reviewer should receive only their assigned blinded packet/PDFs plus a signed/hash-bound assignment manifest. Apply restrictive ACLs, log distribution/return/deletion, and use a reviewer confidentiality/no-redistribution/COI agreement. Avoid embedding whole PDFs unless rights and secure delivery are resolved; version-pinned reviewer fetching or a controlled viewer may be preferable.

### C4. Browser state and exports are not packet-bound

The localStorage key is only `annot:<project>:<reviewer>` (`pipeline/annotate.py:498-503`). Regenerating a project after sample, artifact, packet, or codebook changes silently restores old state into the new packet. The export contains project/reviewer/codebook version and paper entries, but no manifest, assignment, packet, manual, or artifact hash.

Namespace state by packet digest and embed the digest in every export. A changed packet should require an explicit migration/archival flow, never silent carry-over. Preserve immutable first-pass exports before any adjudication.

### C5. Ingest remains fail-open and under-validates

If the manifest is absent, ingest warns and continues (`pipeline/annotate.py:747-799`). If present, it validates global paper membership only. It does not verify reviewer-specific assignment, item version, exact codebook/bundle, packet/export digest, release, or artifact. It trusts the incoming codebook string.

It also accepts contradictory diagnostic answers such as `external_ai_artifact=no` plus a true flag, permits blank `yes/no/unsure` controls, and does not reject redundant/contradictory R5 scalar-plus-“also” states. TRUE labels may omit category/location fields. Require the explicit canonical fallbacks (`unspecified` category and `unknown` location) instead of silently accepting empty sets. The schema has no unique assignment/export/adjudication identity or release/design provenance.

Make the manifest mandatory and ingest one export transactionally after verifying every identity. Add database uniqueness and append-only constraints for `(project, round, release_member, reviewer, first_pass)`. Reject wrong reviewer, wrong version, stale packet, unknown/missing item, duplicate within export, contradictory fields, and unassigned IDs. Store inclusion probability/stratum, COI, evaluability/search fields, packet/export hashes, and adjudication lineage.

### C6. The shared double-coded subset is not implemented

Each reviewer currently receives the entire sample in an independently shuffled order (`pipeline/annotate.py:268-282`). `GOLD_STUDY.md:98-101` says reviewer 2 can label the first 100–150 positions. If both stop at their own first `k` of 500, expected overlap is only `k²/500`: about 20 at `k=100` and 45 at `k=150`, not 100–150.

Allocate an explicit stratified shared subset, place it at blinded randomized positions for both reviewers, and record the assignment probabilities. Assign the remaining items singly or fully double-code them. Power the shared subset for polarity and the primary axes, not only an aggregate kappa.

### C7. Two graders do not satisfy the existing adjudication protocol

Two independent graders can estimate inter-rater reliability. The protocol says reviewers do not adjudicate their own disagreements and requires human–machine conflicts to be reviewed by someone who supplied neither label (`GOLD_STUDY.md:117-133`). A joint session is not equivalent to an independent third pass and conflicts with the anchoring-control objective.

Recruit a third blinded adjudicator, or formally change and preregister a weaker consensus protocol. Mix disagreements with a random agreed-item control set, hide machine labels, preserve both first-pass labels, and measure adjudicator flip rates. Implement adjudication assignment/ingest/status rather than relying on a printed worklist.

### C8. Agreement and estimators remain incomplete

`annotate agreement` selects the first two reviewer rows, computes exact verdict agreement/kappa, and prints disagreements (`pipeline/annotate.py:976-1004`). It has no reviewer-pair contract, axis metrics, CIs, equivalence/non-evaluable handling, adjudication storage, design weights, or thresholds.

The estimator section of `GOLD_STUDY.md:143-154` is still prose. Before seeing final labels, implement and test:

- stratum-specific precision and false-omission estimates;
- Horvitz–Thompson/two-phase expansion from recorded inclusion probabilities;
- selected-frame sensitivity and corrected prevalence with uncertainty;
- finite-population/design bootstrap over sample and adjudication;
- reason-coded `UNCLEAR`/`INSUFFICIENT_EVIDENCE` bounds, never negative imputation;
- polarity and per-axis agreement/kappa with bootstrap CIs and rare-class caveats;
- overlapping R5 quantities, not scalar maxima;
- explicit acquisition/scan missingness extrema outside release membership.

Create a synthetic fixture with known totals/labels and exact expected estimates/CIs. Make the analysis command produce a hash-bound result that freeze can verify.

### C9. Sampling power and the public estimand need prespecification

POS/FLAG/NEG sampling can estimate overall precision and omission in the selected release frame. POS `n=150` is not guaranteed to support five impact states, 17 categories, new R4 instrument/artifact cases, time/subfield comparisons, and rare result-bearing/zero/undetermined quantities.

Oversample rare impact and R4-hard strata with known probabilities, or explicitly call those axes exploratory. Prespecify primary outcomes and pass thresholds. Plants remain a bounded-search process check, not a transportable sensitivity estimate. The negative-search protocol is restricted to standard disclosure locations, while plant selection currently draws arbitrary POS/FLAG cases; a body-only planted disclosure may be impossible to find under the assigned protocol. Either restrict plants to preverified eligible locations/search terms or use a sufficiently complete full-paper search, and name the resulting search-sensitivity estimand separately from whole-source scanner sensitivity.

Gold drawn from scan-complete release membership validates that selected frame only. It cannot identify the full 133,279-paper frame when roughly 47.5k remain outside scan-complete v1 membership. Keep selected-frame validity and full-frame acquisition bounds separate.

### Gate C acceptance criteria

- distinct final builder consuming one immutable release candidate;
- exact artifact/PDF/context/instrument/packet identity for every item;
- owner-only allocator and restricted reviewer-specific blinded packages;
- packet-hash browser/export binding and fail-closed transactional ingest;
- explicit stratified shared double-coded subset and immutable first passes;
- two named graders plus a third blinded adjudicator/control sample;
- COI/evaluability/search/plant/version-confirmation fields;
- executable frozen weighted estimators, CIs, bounds, and pass thresholds;
- complete synthetic end-to-end dry run before real final labels.

## Gate D — make a scientific release immutable and statistically honest

### D1. Freeze still permits an unvalidated result

Freeze requires a clean, pinned, isolated complete API classification run, and now refuses scoped runs. It still permits:

- partial/arbitrarily incomplete scan coverage;
- optional rather than mandatory quote grounding/render certification;
- no final gold/adjudication/estimator gate;
- an active or unreconciled campaign;
- no attempt/spend/tariff invariant audit;
- no acquisition/selection manifest policy or missingness threshold.

The generated language says validity gates were enforced even when none were requested. Define a release-policy object with mandatory requirements and numerical thresholds. Freeze should verify the exact campaign closure, full target selection, evidence/render results, gold analysis hash and pass criteria, unresolved outcomes, and approved missingness estimand.

### D2. A release is still a digest of mutable queries

The `releases` table stores pointers, counts, set hashes, and report hash (`pipeline/report.py:472-510`; `pipeline/migrate.py:254-263`). It does not materialize frame members, versions/bases, artifacts, labels, evidence, render rows, gold labels, weights, or aggregate cells. There are no immutability triggers. Later mutations can change a regenerated site under the same nominal release.

Materialize a content-addressed release bundle with the complete preimage needed for every output. Include generator commit/tree/environment, target/acquisition manifests, member/version/artifact rows, classification protocol and exact labels/evidence, render results, campaign reconciliation, taxonomy bundle, gold assignments/adjudication/analysis, aggregate cells, and correction lineage. Hash each artifact and a top-level manifest; make released database rows append-only.

### D3. Generator provenance is captured too late

The report is written before `db.code_commit()` is stored in the release. With the default tracked `reports/report.md`, generation normally dirties the tree and can stamp `-dirty`. Capture and validate clean HEAD/tree before output; build in an empty staging directory from that exact tree; atomically insert/materialize only after all bytes and hashes pass.

### D4. The site is not a release consumer

`pipeline.build_site` accepts scan/classification run IDs and queries live tables; it has no `--release` and always emits exploratory status (`pipeline/build_site.py:181-196,348-393,600-610`). Implement a release-only builder that verifies the manifest and writes one allowlisted staged artifact. The deployed bytes must be exactly those named by the release, not a later live query.

### D5. Statistical interpretation remains preliminary

The current site’s Wilson intervals are described as sampling uncertainty even though the observed scan-complete selected frame is nearly a finite-frame census. They do not cover acquisition selection, measurement error, version basis, dependence over time, or codebook uncertainty. Either declare a superpopulation/independence model or present descriptive ratios and make gold/acquisition uncertainty primary.

Daily/weekly/subfield/provider/category/impact panels remain multiple exploratory analyses without axis-specific validation, composition adjustment, temporal dependence modeling, shrinkage, or multiplicity control. Prespecify the primary time scale and comparisons; label all other panels exploratory.

### D6. Current public copy still mixes careful and misleading construct names

The new disclosure card carefully distinguishes attempted/contributing/zero/undetermined states. The hero tile still says all `author_use` papers disclose “AI assistance” (`pipeline/build_site.py:560-562`), which includes explicit zero contribution and excludes real non-delegated instrument use under v2.6. Generate one canonical construct name and definitions from the release taxonomy; use it in HTML, JSON, reports, tooltips, and metadata.

### Gate D acceptance criteria

- mandatory release policy for selection/coverage/evidence/render/gold/campaign;
- content-addressed materialized member/analysis preimage and database immutability;
- clean generator identity captured before deterministic staging;
- report/site consume only a release ID/bundle;
- precise delegation/R5 construct language in every artifact;
- declared finite-frame/superpopulation estimand and uncertainty components;
- byte-reproducible double build and correction/supersession lineage.

## Gate E — public repository, disclosure control, governance, and deployment

### E1. Small-cell protection remains incomplete

`suppress_small()` is applied only to tools/providers (`pipeline/build_site.py:157-165,389-391,453,463`). Categories, impact, location, and exact daily/weekly/subfield-month series remain unsuppressed. The tracked preview contains one explicit category singleton and 601 positive time/subfield cells of size 1–2, including 417 singletons. Overlapping 3-month/1-year/3-year horizons permit complementary subtraction.

`noindex` and `do_not_cite` are warnings, not access controls. Before public hosting or a public clone, implement one disclosure-control layer applied before every HTML/JSON/Markdown/CSV/JS serialization: minimum denominator and positive numerator, rare-name rollup, coarser time, primary and complementary suppression, consistent totals, and adversarial reconstruction tests across overlapping views. Apply the same policy to tracked reports, not only charts.

### E2. The dashboard contains latent DOM-XSS sinks

Generator-side JSON escaping protects the `<script>` context. The template later inserts series/category-derived strings into `innerHTML` for chips, hover tooltips, and tables (`pipeline/templates/dashboard.html:217-230,358-373,382-392`). Script-context escaping does not sanitize a later HTML-context insertion. Current category codes are mostly controlled, so this is latent rather than a demonstrated exploit; malformed or contributor-controlled metadata could make it active.

Build DOM nodes and assign `textContent`, whitelist ISO date/category grammar, and add hostile-value tests. Deploy with a workable CSP plus `nosniff`, referrer, frame, permissions, and HSTS headers where supported.

### E3. Current-tree policy and reachable Git history still conflict

The current tree properly ignores `.env`, DB, corpus, annotations, and the old expressive result dumps. Ordinary reachable history still contains deleted paper-level labels, long excerpts/contact information, validation buckets, spotchecks, and infrastructure inventory. `PITCH.md` still includes identifiable pilot IDs and a verbatim excerpt, and promises open annotations while also promising aggregate-only output. `DESIGN_PLATFORM.md` still proposes public per-paper labels/explorer/ODC-BY against the binding aggregate-only decision. `pipeline/aws/math_ids.txt` is a 1.8 MB paper-ID frame requiring an explicit publication/license carve-out or removal.

No remote or tag is configured in this clone, which is an opportunity—not proof the history was never shared. Preserve a private canonical archive and publish from an allowlisted clean export/new history, or rewrite a disposable clone. Run full-history secret, PII, paper-ID, excerpt, local-path, and infrastructure scans; verify a fresh clone/object inventory. Maintain a publication matrix covering source code, public documentation, frame manifests, aggregates, gold metrics, item labels, excerpts, hashes, and operational records.

### E4. Licensing, privacy, corrections, and governance remain incomplete

The MIT software license, non-affiliation statement, funding, and AI-use disclosure are good foundations. “Future released aggregates are intended as CC BY” is not an operative data license. The repository still lacks a complete public package:

- release-level aggregate data license and source/license matrix;
- data dictionary/schema/checksums and `CITATION.cff`/DOI metadata;
- privacy/data-governance notice (controller, purpose, basis, processors, access, retention, rights, incident route);
- `SECURITY.md` and vulnerability reporting;
- correction, appeal, takedown, and immutable supersession policy;
- governance/roles/COI and reviewer confidentiality/deletion agreement;
- contributing/code-of-conduct/changelog documents;
- explicit funder role/non-role in design, analysis, publication, and provider choice.

Remove the PITCH excerpt, which contradicts the statement that paper excerpts are never redistributed. Generate the visible audit version and release status from release metadata; README/site counts of review rounds are stale and disagree.

### E5. CI and deployment do not enforce the release story

`.github/workflows/ci.yml` says “tests + site build” but only installs dependencies and runs pytest. Action SHAs are pinned, which is good. Add:

- explicit `permissions: contents: read`, checkout `persist-credentials:false`, timeout, and concurrency cancellation;
- hash-locked dependencies and dependency/license/SBOM/security checks;
- migration-from-empty and fixture end-to-end classify/render/gold/release tests;
- deterministic double site build and release-manifest verification;
- public-boundary, history-secret, small-cell/differencing, and DOM-XSS tests;
- HTML/schema/link/CSP/header/browser/accessibility checks.

There is no deploy workflow, so this is a pre-deploy gap, not a live deployment-token vulnerability. Deploy only the exact immutable release artifact through a protected environment with manual approval, least-privilege token, preview, rollback, and host-level security headers.

### E6. Accessibility and reach still need a release pass

Static tracker-free delivery, focus styles, and table equivalents are strengths. Remaining issues include chart SVGs with `role=img` but no chart-level accessible name/description, muted 12.5 px text around 3.41:1 contrast, pointer-oriented tooltips, no main landmark/skip link, and no robust no-JS fallback for dynamic series.

Run automated and manual keyboard, screen-reader, mobile, high-contrast, reduced-motion, and no-JS checks. After scientific/governance gates pass, add canonical/OG/social image/favicon, sitemap/robots release switch, stable methods/validation/privacy/corrections/contact pages, a downloadable disclosure-controlled aggregate/schema/checksum bundle, CITATION/DOI, and explicit no-causality/no-misconduct messaging.

### Gate E acceptance criteria

- comprehensive primary/complementary disclosure control with reconstruction tests;
- all dynamic HTML paths text-safe and deployed security headers;
- clean allowlisted public tree/history and reconciled publication policy;
- provider/local privacy and retention controls documented/enforced;
- operative license, citation, governance, security, and correction package;
- deterministic release CI and protected exact-artifact deploy;
- accessibility, no-JS, mobile, link, and header pass.

## Iteration-10 finding status summary

| Iteration-10 area | Round-11 status |
|---|---|
| R4 invoked/incorporated contradiction | **Resolved by deliberate v2.6 delegation construct** |
| Construct naming / `topic_only` semantics | **New/partial: actual instrument use is hidden under `topic_only`** |
| Human polarity wording parity | **Improved: generated from taxonomy; full rulebook/packet binding remains** |
| Exact owner sign-off | **Explicitly pending** |
| Two-human comprehension | **Not done** |
| Machine comprehension | **Partial and misreported: 16/16 polarity/impact, 13/16 flags** |
| R5 overlapping paper states | **Report/site/human improved; single-snippet machine representation still lossy** |
| `external_ai_artifact` diagnostic | **Validator fixed; paper rollup drops 2/2 observed papers** |
| Scoped target identity/status/report refusal | **Fixed and empirically verified** |
| Missing/malformed usage fail-closed | **Fixed** |
| Four-class pricing | **Partial: cache writes added; cached-read rate wrong** |
| Campaign authorization | **Partial: snapshot not authoritative; old campaign scope/reconciliation stale** |
| Reservation + attempt admission | **Substantially fixed atomically** |
| Lease/store fencing | **Substantially improved; terminal transition and generation remain open** |
| Provider key/error minimization | **Improved; account governance/residual-source risk remains** |
| Final release-bound gold | **Not implemented** |
| Immutable release/site consumer | **Not implemented** |
| Small-cell and history boundary | **Unchanged public blocker** |
| Governance/licensing/CI/deploy/a11y | **Mostly unchanged public blockers** |

## Prioritized next actions

### Before any full paid v2.6/v2.7 classification call

1. Correct the v2.6 comprehension generator, table, and decision-log claims; inspect the three flag failures.
2. Add machine-visible overlapping R5 states and validate all expected vignette axes.
3. Preserve/OR `external_ai_artifact` in paper rollup and test all ordering/gating combinations.
4. Reconcile the `topic_only` name/public definitions and add explicit attempted-use exception/boundary cases.
5. Have both intended graders independently complete the exact frozen vignette exercise; adjudicate misunderstandings.
6. Bump/version as needed and record final owner sign-off on taxonomy/manual/prompt/schema/vignette/estimand hashes.
7. Correct cached-read pricing; reconcile and close the pilot; create a fresh snapshot-authoritative full-run campaign.
8. Fence terminal status with holder/generation and pass takeover/retry fault tests.
9. Record provider/account/privacy/minimum-text decisions and run with a verified least-privilege key/ACL environment.

### Before final gold begins

1. Materialize one release candidate with exact member/artifact/evidence/render identities.
2. Implement a separate final-gold builder and restricted reviewer-specific hash-bound packets.
3. Bind browser state/export/ingest to release, assignment, version, artifact, instrument, and packet hashes.
4. Allocate a prespecified stratified shared subset and recruit/name a third blinded adjudicator.
5. Freeze overlapping R5 human fields, COI/evaluability/search process, impact-hard sampling, estimators, CIs, bounds, and pass thresholds.
6. Pass a synthetic end-to-end build/export/ingest/agreement/adjudication/estimation test.

### Before public repository/site or scientific claim

1. Implement materialized immutable release and release-only site generation.
2. Apply comprehensive primary/complementary suppression and pass reconstruction tests.
3. Publish a clean allowlisted tree/history; reconcile PITCH/DESIGN/LICENSE/DECISIONS.
4. Complete privacy, security, governance, licensing, corrections, citation, and reviewer policies.
5. Harden deterministic CI, protected deployment, headers, accessibility, and rollback.
6. Release only the construct and selected-frame estimand supported by adjudicated gold; keep acquisition uncertainty explicit.

## Bottom line

Round 11 contains real engineering progress. The scoped classifier path now has strong input identity, valid structured outputs, atomic spend/attempt admission, and a scope-specific status that population reports refuse; the taxonomy is shorter; human descriptions derive from machine definitions; and R5 paper counts are much more honest. Crucially, no full v2.6 run has started, so the project still has a clean opportunity to fix the instrument without discarding an expensive result.

The preflight has done its job by exposing three taxonomy-specific data losses before launch: overstated flag stability, an inability to encode co-located mixed R5 states, and total downstream loss of the new external-artifact diagnostic in the current scoped data. Together with the non-authoritative campaign tariff and pending human/owner sign-off, these justify a firm pause on the full paid run.

Once Gates A and B pass, the classification run itself can proceed. That is not authorization for claims. Final gold, release materialization, disclosure control, governance, and deployment remain separate gates. Keeping those stages separate is the best route to a result that is scientifically interpretable, reproducible, financially controlled, ethically proportionate, and credible when it eventually becomes public.
