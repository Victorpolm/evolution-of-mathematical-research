# ArxivObservatory repository review — iteration 7

**Audit snapshot:** Git commit `6edb339917373a9642473ac7e54962586244e7fb`, tree `66247da4fcceadb860917500883c82bfbb923a8d`, 2026-08-12 14:39 CEST. The worktree was clean before this review file was added.

**Primary delta reviewed:** everything after the iteration-6 snapshot `e2293d6`, especially the review-6 triage (`1863ffe`), the v1 scan and Luna classification outputs, rendered-evidence checks, API budget/attempt ledger, the v1/mixed comparison, taxonomy v2.1 and rules R4/R5 (`d61c107`, `54dfd0d`), the completed owner-labelled calibration round, `GOLD_STUDY.md`, `DECISIONS.md`, licensing/funding/AI-use disclosures, generated reports/site, and the publication plan. I also re-reviewed the rest of the tracked repository and the local restricted calibration artifacts.

**Audit boundary:** read-only except for creating this file. I did not invoke a model, contact arXiv or a provider, alter the corpus/database, start or stop a job, operate cloud resources, publish the site, or inspect provider billing consoles. Local calibration files were treated as restricted and are summarized only in aggregate. I checked the current official OpenAI Luna model page and API data-control documentation; other bibliography claims were not re-verified in this iteration.

## Executive verdict

The project has crossed an important engineering threshold. The v1 artifact path now runs at scale; the selection hash reconstructs; classification uses a direct, one-paper, tools-free API path with native schemas; physical attempts and conservative spend are ledgered; render checking completed without remaining PDF errors; and the calibration round has produced genuinely useful evidence about the instrument. These are substantial, verifiable improvements.

The project is nevertheless **not ready to start the confirmatory full taxonomy run or the final two-grader gold study today**. This is now less about broad architecture and more about a short list of measurement-contract defects that must be closed before expensive or irreversible work begins:

1. **The human instrument cannot record taxonomy v2.1 R5.** The model accepts `author_use + epistemic_impact=none`, while the annotation form omits `none` and ingest rejects it.
2. **R4/R5 are not yet an operationally stable construct.** R4 conflicts with “author use in any role,” R5 can coexist with the logically contradictory `catalytic=true`, vague disclosures have no `undetermined` impact, and the sole R5 development example is a mixed object-of-study/redundant-output case.
3. **Two materially different R4 definitions share the same version `2.1`.** The final codebook must receive a new version and a hash before any new labels are produced.
4. **The final-gold software path does not exist.** Every packet is hard-coded as calibration-only; evidence is re-extracted from mutable files rather than the scanned artifact; caches, browser state, exports, and ingest are not bound to immutable packet/version/codebook hashes; and no estimator/adjudication implementation exists.
5. **The proposed Luna rerun will repeat known systematic truncations.** The v2.0 run has 171 output-length failures plus one ID failure across seven papers, while batching remains fixed at up to 30 snippets with no deterministic split/retry tree.
6. **`report --freeze` is not an immutable, validated release.** It can accept partial or selected scan coverage and optional evidence gates; it stores summary hashes over mutable queries; it has no gold-study gate; and neither the site nor annotation builder consumes a release ID.
7. **The available v1 corpus does not identify three-year population prevalence.** In the headline frame, 47,554 of 133,279 papers are unresolved and the raw-label coverage extrema are 2.0%–37.7%. The missing tail is deliberately deferred, but that decision changes what may honestly be claimed.
8. **The public-repository boundary is currently violated.** Tracked results contain paper-level labels, long source excerpts, and even copied contact/address material, contrary to the aggregate-only decision and the new license notes.

My readiness call is therefore:

| Activity | Readiness |
|---|---|
| Private R4/R5 comprehension dry-run on synthetic/development cases | **Ready after the human `none` path and cross-field invariants are fixed** |
| Fresh full Luna classification | **No-go until taxonomy v2.2, adaptive splitting, durable run lease/reservations, and an explicit full-run spend approval are frozen** |
| Final two-grader gold | **No-go until release-candidate sampling, exact artifact binding, shared assignment, fail-closed ingest, and adjudication/estimators exist** |
| Public inspection of methods/clearly partial aggregate output | **Possible under the owner decision, but must not be framed as three-year prevalence** |
| Validated scientific release or public repository push | **No-go until validation, immutable release, privacy/licensing/governance, and history sanitation are complete** |

This is a finite and tractable pre-run list. I would not spend the next full-run dollar or expose the final gold sample until the P0 checklist at the end of this review passes in CI.

## What is genuinely stronger since iteration 6

The following changes are real and should be retained:

- all 2,122 approved flagged-phase v1 refill targets now have v1 artifacts, and the target hash is reproducible;
- refill modes have an explicit truth table, target-member manifests, content-suffixed artifact paths, and terminal reconciliation;
- v1 scanning consumes the artifact ledger and records explicit-v1 versus inferred-single-version basis;
- the v1 selection of 112,447 papers reconstructs exactly to SHA-256 `82a021c66ea94c1197285ebe7edad61b4b4727fa2107b6980997666af14625a7`;
- source selection is source-first, eliminating the earlier outcome-conditioned preference for render-acquired PDFs;
- API classification is non-agentic, one paper per request, tools-free, fixed-origin, no-redirect, and `trust_env=False`;
- OpenAI uses strict `json_schema`, Anthropic now uses strict forced-tool input, and both derive their schema from `taxonomy.py`;
- every C0 control character is rejected, closing the `\\nabla`/`\\tau`/`\\ref` TeX corruption found in iteration 6;
- resume identity includes a canonical protocol hash with commit, prompt, taxonomy, schema, model, run set, and batching constants;
- physical retries receive separate reservations, in-flight token/USD reservations are counted, and 429 rejections release their reservation;
- the database has a durable provider-spend ledger; the current v1 run's settled/failed-reserved outcomes reconcile internally;
- evidence lineage is complete for the repaired historical run;
- render checking distinguishes exact matches from fuzzy review candidates and recovered from transient filesystem `EINVAL` errors;
- the v1/mixed comparison prominently states its model/version confounding;
- the calibration is blinded, explicitly development-only, randomly ordered, and has exposed useful taxonomy and packet-version failure modes;
- math-ph inclusion and the primary category predicate are now owner decisions rather than silent drift;
- the site remains `noindex`, machine-readable as `unreleased_exploratory`, and visibly says do not cite;
- funding and project AI use are disclosed, and a software license now exists;
- the fixture suite grew from 94 to **112 passing tests**.

These changes make a credible confirmatory pipeline achievable. They do not themselves make the current v1 labels a validated estimate.

## P0-1. Freeze taxonomy v2.2 before any full rerun or final annotation

### The model and human graders currently have different label spaces

Taxonomy v2.1 defines disclosed-but-fruitless use as `author_use` with impact `none` (`TAXONOMY.md:47-52`; `pipeline/taxonomy.py:124-127`). The classifier validator explicitly permits it (`pipeline/classify.py:301-305`). The human path does not:

- the HTML form lists only `cosmetic`, `supportive`, and `result_bearing` (`pipeline/annotate.py:396-400`);
- the ingest validator rejects `TRUE_DISCLOSURE + impact=none` (`pipeline/annotate.py:597-604`);
- the packet legend says only “rules R1/R2” (`pipeline/annotate.py:410`);
- `GOLD_STUDY.md:47,56-57` still says codebook v2 and rules R1-R3.

Starting the final study in this state would force the two human graders to map a valid model outcome into a different impact class, mechanically biasing impact agreement and any R5 estimate. This is an unconditional stop condition.

### R4 needs an observable role test, not “assistant in producing the paper”

The current definitions say both:

- `author_use` means the authors used AI “in producing THIS paper, any role” (`TAXONOMY.md:28`); and
- a model used as a component of the studied system/method is `topic_only` unless it has a separate assistant role (`TAXONOMY.md:36-46`).

Those statements are not operationally equivalent. Code generation, computation, formalization, synthetic-data production, model-based labeling, and evaluation are all research-method components, yet they are also explicit author-use categories. “Assistant” is anthropomorphic and does not settle whether an automated LLM judge, frozen encoder, embedding generator, code generator inside a benchmark pipeline, or synthetic-data model counts.

The calibration exposed this rather than resolving it: three machine positives were rejected as component/object cases, while another model/component-type case was labelled a true disclosure by the human under v2.0. The final rule needs to classify the action and consumed output, not the paper's prose style.

I recommend a two-stage decision tree:

1. **Was an AI/LLM merely mentioned, cited, benchmarked, or analyzed as the scientific object?** If yes and no output was used outside that observation, code `subject_only`/`topic_only`.
2. **Did the authors intentionally invoke or incorporate the system to produce an input used in conducting or communicating this research?** This includes prose, search, ideas, proofs, code, computations, labels, synthetic data, judgments, or formalization. If yes, it is an in-scope tool-use role unless the owner deliberately excludes a named method-component class.
3. **Was a pretrained model merely a fixed component/input of the experimental object, with no disclosed delegated research task or consumed generative output?** Code a diagnostic `research_method_component_out_of_scope`, not `topic_only`.
4. **Can roles coexist?** Yes. A paper may study an LLM and separately use it for writing/coding; preserve both roles and let the prespecified headline mapping decide inclusion.
5. **If the text does not reveal which relation applies, use `unclear`, not an inferred role.**

The key owner decision is whether active AI instrumentation—LLM labels, judgments, embeddings, synthetic data, or generated benchmark code—is within “author-reported AI assistance.” Either answer is defensible if prespecified. Calling real operational use `topic_only` is not informative enough for audit or public explanation. A diagnostic relation field is cleaner than forcing every relation into one polarity.

Before freeze, both graders and Luna should independently code a small, non-confirmatory edge-case set covering:

- a frozen encoder as the studied architecture;
- embeddings analyzed as data;
- an LLM judge/labeler used in a non-AI paper;
- synthetic-data generation;
- code generation for an experimental pipeline;
- a proof assistant or LLM formalizer used to certify a result;
- a paper that studies an LLM and separately uses one for writing;
- a redundant answer obtained only after the human result was complete;
- an unsuccessful query whose output was not retained;
- an incorrect answer that catalyzed a successful search.

Do not draw these examples from the confirmatory sample, and do not identify real development papers in the public codebook.

### R5 needs contribution status, `undetermined`, and cross-field invariants

R5 is conceptually useful: an explicitly unsuccessful attempt is still disclosure behavior. But the current representation conflates three states:

- explicit zero contribution from an attempted use;
- insufficient information to infer impact;
- “not applicable” for every non-author-use polarity.

Those should not all be `none`. Add either:

- a contribution field such as `contribution_status = contributing | explicit_zero | undetermined | not_applicable`; or
- distinct impact values `zero_contribution`, `undetermined`, and `not_applicable`.

Then enforce at least these invariants in the generated schema, local validator, human form, and tests:

- explicit zero contribution implies `catalytic=false`;
- `catalytic=true` implies at least supportive impact under R2;
- non-author-use implies `not_applicable`, not R5 zero contribution;
- vague author-use cannot be forced into `cosmetic`, `supportive`, `result_bearing`, or explicit zero; it is `undetermined`;
- R5 task categories describe the attempted task, while impact records the explicitly zero contribution;
- every public numerator states whether attempted-zero cases are included.

The current validator accepts `impact=none` together with `catalytic=true`; the new test even begins from a catalytic label and asserts that changing impact to `none` is valid (`tests/test_classify.py:57-62`). That combination contradicts R2's causal-contribution definition and must be rejected.

The development example motivating R5 is not a clean sole exemplar. The interaction occurred after the authors' solution concepts were derived; one answer independently suggested a model later presented, other answers failed, and outputs were also reported as study observations. Zero *causal novelty* may be defensible, but the case mixes object-of-study, redundant output, and attempted assistance. Use several synthetic or deidentified canonical cases and blinded adjudication, not one special-case narrative.

### Do not pool R5 into “contributing assistance” silently

`TAXONOMY.md:51-52` says zero-contribution cases are “never pooled with contributing use.” The report currently defines the numerator from all `author_use` papers (`pipeline/report.py:238-240,350-372`). Unless this changes, the implementation contradicts the codebook.

Publish two explicitly named quantities if R5 remains in scope:

1. **disclosed attempted-or-contributing AI tool use**, including explicit-zero attempts; and
2. **disclosed contributing AI tool use**, excluding explicit-zero attempts and reporting undetermined separately.

The phrase “AI assistance” should refer to the second quantity unless the page immediately defines the broader attempted-use construct.

### Version 2.1 is already ambiguous; the final wording must be 2.2 or later

`pipeline/taxonomy.py:7-9` requires a version bump for every change to definitions or decision rules. Commit `d61c107` introduced R4/R5 as 2.1; `54dfd0d` materially changed R4 while retaining 2.1. Stored human rows contain only `codebook_version`, so the two incompatible “2.1” definitions cannot be distinguished later.

The final wording should therefore be released under a new version—`2.2` is the natural minimum—with:

- the exact `TAXONOMY.md` SHA-256;
- machine dictionary/schema SHA-256;
- full prompt SHA-256;
- validator/protocol SHA-256;
- a compact decision table embedded in every human packet;
- regression cases for R1-R5 and every cross-field invariant.

The current taxonomy sync test checks vocabulary and version, and only asserts that R1/R2 appear in the prompt. It does not prove that human and machine semantics match. Prefer generating the grader-facing rule table from the same structured definitions, then snapshot-test the rendered manual and prompt.

## P0-2. Treat the completed 150 labels as calibration, not validation

The round was useful and correctly designated development-only. It found a packet-version bug, dominant false-positive mode, impact ambiguity, and category/location disagreement. It should not be used to claim release accuracy because it was drawn under taxonomy v2.0, informed v2.1/2.2 development, sampled the wrong universe, had only one human grader, and included one non-comparable version-skew item.

### Reconciled calibration counts

The database contains **150** ingested owner verdicts, not 149:

| Stratum | Human outcomes | Total |
|---|---|---:|
| POS, shown excerpts | 28 true disclosure; 3 false positive; 1 topic only | 32 |
| POS, plants | 5 true disclosure | 5 |
| FLAG | 16 false positive | 16 |
| NEG | 96 no AI mention; 1 true disclosure caused by packet/scanned-version skew | 97 |
| **Total** |  | **150** |

`annotation/gold-3yr-prelim/calibration_summary.md` and `DECISIONS.md:81` say 149, and the summary lists only 95 ordinary NEG outcomes. The proper wording is: **150 labels ingested; 149 human-machine pairs are comparable after excluding one known version-skew case.**

The headline calculations should be named by estimand:

- shown-excerpt POS precision: `28/32 = 87.5%`, Wilson 95% interval approximately 71.9%–95.0%;
- all sampled POS including plants: `33/37 = 89.2%`, approximately 75.3%–95.7%, but plants have a different presentation/search process and should not simply be pooled;
- binary disclosure concordance on comparable pairs: `145/149 = 97.3%`, approximately 93.3%–99.0%;
- the currently quoted `145/150 = 96.7%` treats the non-comparable version-skew item as a model error;
- same-text scanner misses in the evaluable NEG arm: `0/96`, not `0/97`; the Wilson 95% upper bound is about 3.85%, so this is “none observed,” not zero miss rate;
- plants found: `5/5`, but the Wilson lower bound is only about 56.6% and the plants are likely easier than latent scanner misses.

The axis calculations on the 33 machine-positive/human-positive papers reproduce:

- impact exact agreement `28/33 = 84.8%` (Wilson interval roughly 69.1%–93.3%);
- category exact-set agreement `21/33 = 63.6%`, mean Jaccard about 0.796;
- location exact-set agreement `25/33 = 75.8%`, mean Jaccard about 0.803.

These are **single-human machine concordance**, not inter-rater reliability or adjudicated validity. Location agreement is also partly a schema comparison: the human form is paper-level multi-select, whereas the model emits one location per snippet and the report later unions locations. Align the units before interpreting exact-set disagreement.

### Make the calibration analysis executable

The aggregate summary appears manually maintained and is already stale. Add a deterministic analysis command that consumes:

- the immutable calibration manifest;
- original machine labels;
- exact human export(s);
- a version/evaluability table;
- a prespecified binary equivalence map;
- plant and presentation status;
- codebook and analysis-code hashes.

It should emit the summary, all denominators, Wilson/design intervals, confusion matrices, axis metrics, and a machine-readable JSON in one step. A CI fixture should reproduce the published aggregate counts. Manual corrections should be append-only reason-coded exclusions, never silent “reclassification.”

Raw overall agreement in this heavily stratified sample is design-dependent. Report stratum-specific concordance and, if an overall frame quantity is wanted, use design weights. Keep binary disclosure agreement distinct from fine-polarity, impact, category, and location accuracy.

## P0-3. Implement a genuinely final, release-candidate-bound gold path

The module docstring says it samples a frozen release, but the implementation cannot do that yet:

- every manifest hard-codes `calibration_only_never_release_validity` (`pipeline/annotate.py:262-276`);
- every HTML packet hard-codes a CALIBRATION ROUND banner (`pipeline/annotate.py:342-348`);
- the CLI has no `--release` or analysis-snapshot argument;
- contexts are read from mutable/current `files` rather than the artifact used by the selected `scan_item` (`pipeline/annotate.py:98-116`);
- current/latest paper comments can be shown in a v1 packet (`pipeline/annotate.py:237-245,321-332`);
- `contexts.json` is reused solely because the path exists (`pipeline/annotate.py:282-299`);
- PDF embedding is optional and may retrieve a different current representation;
- manifests omit exact scan item, artifact ID/path/hash, context hash, PDF hash, packet hash, item-order hash, taxonomy hash, and release-candidate hash;
- local browser state is keyed only by project and reviewer (`pipeline/annotate.py:419-424`), so regenerated packets silently restore stale labels;
- JSON ingest warns and proceeds without a manifest (`pipeline/annotate.py:621-628`);
- ingest checks paper membership but not expected version, artifact, reviewer assignment, packet, codebook, context, or release hash, then stores the export's own codebook string (`pipeline/annotate.py:613-659`);
- the annotations schema has no uniqueness constraint over round/item/version/reviewer and no design/adjudication fields (`pipeline/migrate.py:239-252`);
- `agreement` uses the first two reviewer labels and reports only verdict percent agreement/kappa (`pipeline/annotate.py:728-756`).

This chain can reproduce the exact version-skew failure already seen in calibration. It must fail closed before the confirmatory sample is drawn.

### Use a two-stage immutable object model

There is a circularity in saying “sample gold from a release” when the release itself must be gated by gold. Use two objects:

1. **Analysis snapshot / release candidate:** immutable membership, source artifact, classifier label, evidence, render result, missingness state, protocol, and selection manifest. No validity claim.
2. **Validated public release:** references exactly one analysis snapshot plus the frozen gold project, adjudications, estimator output, pass/fail gates, report/site/data hashes, license, and correction lineage.

The final annotation manifest should contain or reference an immutable row per item with at least:

- snapshot ID and member ID;
- paper ID and exact scanned version;
- scan item and artifact ID/SHA-256/version basis;
- every evidence-hit/context SHA-256;
- version-pinned PDF SHA-256 and extractor/render protocol;
- machine stratum and inclusion probability (hidden from graders, retained for analysis);
- taxonomy/manual/prompt/schema hashes;
- explicit shared/single-coded assignment and reviewer roster;
- per-reviewer randomized order hash;
- packet HTML/data hash and creation code/tree hash;
- round type (`development`, `confirmatory`, `adjudication`);
- supersession status.

The HTML export should embed the packet hash. The local-storage key should include that hash. Ingest should require exact equality for project, snapshot, packet, reviewer assignment, item/version, and codebook; reject missing manifests; reject duplicates transactionally; and record the original export hash. If a packet changes, it is a new packet/round, never an invisible state migration.

### Align the human data model with the estimators

Add structured fields for:

- `evaluable` plus reason (`unreadable`, wrong version, missing PDF, insufficient context, conflict of interest, other);
- explicit-zero versus undetermined contribution;
- R4 relation/role diagnostic;
- categories, impact, tool, and location at a clearly defined paper or evidence unit;
- PDF opened/version verified;
- bounded-search duration, locations and queries inspected;
- plant found/not found and reason;
- conflict of interest and reassignment;
- first-pass versus adjudication status.

`GOLD_STUDY.md:54-55` currently says everything except true disclosure is negative, while `:125-127` says `UNCLEAR` and `INSUFFICIENT_EVIDENCE` are non-evaluable. The latter is preferable, but complete-case exclusion alone can bias estimates. Report their rate and use worst-case/sensitivity bounds or a prespecified missing-data model.

### Explicitly assign the shared double-coded subset

The current code independently shuffles each reviewer's full order (`pipeline/annotate.py:246-251`). If both reviewers stop after their first 100, 125, or 150 positions, the expected shared overlap is only about 20, 31, or 45—not the 100–150 claimed by `GOLD_STUDY.md:92-95`.

Create a seeded, stratified shared subset and put the same set in both packets, with independent order inside the set. A practical design is:

- both reviewers independently code the same prespecified 150-item shared set, stratified by POS/FLAG/NEG, era, and impact/hard-case group;
- one or both reviewers code the remaining single-coded probability sample;
- the manifest records assignment probabilities and completion rules;
- content-based stopping/skipping is prohibited and audited.

Full double coding is statistically cleaner if workload permits.

### Two graders are not enough for the current adjudication promise

`GOLD_STUDY.md:117` says reviewers never adjudicate their own disagreements; `:118` also permits a joint session; `:119-124` requires a human-machine adjudicator who produced neither label. With only two graders, those rules cannot all be true.

Recruit a third blinded adjudicator for disagreements and a seeded control sample. This need not be a third full annotator, but they must not have produced either first-pass label for the cases they adjudicate. If a third person is impossible, revise and preregister a consensus procedure, retain both initial labels, acknowledge loss of independent adjudication, and do not claim the anchoring-control design currently written.

### Implement the estimator before opening final labels

For machine strata `h` with frame size `N_h`, sample size `n_h`, and adjudicated positive count `y_h`, the core design-based estimate is `N_h * y_h / n_h`. A transparent primary analysis can derive:

- estimated true machine positives from the POS stratum;
- estimated missed disclosures from FLAG and NEG;
- sensitivity as estimated true machine positives divided by all estimated true disclosures;
- corrected frame prevalence as the weighted sum across all strata divided by the eligible frame;
- separate bounds for acquisition/scan/classification/render non-evaluable states.

Use finite-population-aware or stratified bootstrap intervals, and propagate both phases. Do not “deflate” the NEG estimate by `5/5` plants. Plants are selected from scanner-detectable POS/FLAG cases and likely have easier language than latent misses; report them as a process check and include a sensitivity analysis rather than treating them as transportable human-search sensitivity.

The confirmatory analysis plan should prespecify:

- exact binary mappings and exclusions;
- all population strata, inclusion probabilities, and finite-population corrections;
- positive precision, false-omission, sensitivity, and corrected-prevalence formulas;
- non-evaluable and missing-frame bounds;
- confidence interval/bootstrap method and random seed;
- ordinal impact confusion/weighted agreement;
- per-label category/location metrics for sufficiently frequent labels;
- inter-rater metrics with rare-class caveats;
- pass/fail thresholds for headline publication;
- confirmatory versus exploratory displays.

The planned 150 POS labels can estimate overall precision to roughly ±5 percentage points near 90%, but not precision for 17 categories, rare R5 outcomes, every impact class, or every year. Positive disclosures are concentrated late in the series. Stratify/oversample at least by era, machine impact, and targeted R4/R5 hard cases—or explicitly demote period-, category-, tool-, and impact-specific claims to exploratory status.

## P0-4. Harden the planned Luna rerun before paying for it

### The current v2.0 run has systematic terminal failures

The v1 classification run `cls-20260811T220922` contains 71,194 items:

- 71,022 `ok`;
- 171 `openai: truncated at max_completion_tokens` errors across six papers;
- one label-ID coverage error in a seventh paper.

The previously quoted 70,908 success count is stale. These failures cluster in papers with many snippets, so excluding them would be outcome- and complexity-dependent. They must not become denominator negatives or disappear from a frozen candidate.

`pipeline/classify.py:390-400` still groups up to 30 snippets from one paper per call, while `pipeline/llm_api.py:44` caps output at 4,000 tokens. The retry repeats the same oversized batch. The v2.1/2.2 rerun is therefore likely to pay for the same truncations.

Implement deterministic adaptive splitting before the run:

1. sort snippets and assign stable item IDs;
2. use a conservative initial batch size or output-size estimate;
3. on provider `length`, missing IDs, or batch-level schema failure, bisect the same paper's batch deterministically;
4. recurse to one snippet; if one still fails, retain a reason-coded terminal error;
5. persist the parent/child attempt tree and ensure each successful item has one authoritative response;
6. include the split policy and maximum output in the protocol hash;
7. test a synthetic 30-snippet paper and a forced-truncation transport.

Also fix the prompt contradiction: the header asks for `{"labels": [...]}` (`pipeline/classify.py:71-76`), but the final instruction and re-asks say “ONLY the JSON array” (`:141,339-340,379-380`). Native provider schemas currently hide this inconsistency; the prompt should match the object contract exactly.

### Run a fresh taxonomy version; never resume v2.0

The v2.0 and proposed v2.1 protocol hashes differ, and resume correctly refuses mixing. After the taxonomy fixes, create a completely new v2.2 run. Do not reuse any v2.0 labels as confirmatory output, although they remain useful development data.

Before launch, record one canonical protocol object containing:

- clean full Git commit and tree hashes;
- scan/snapshot and selection-manifest hashes;
- taxonomy/manual/prompt/schema/validator hashes;
- exact provider, endpoint, model ID, returned model/snapshot fields, and API version;
- batch/splitting policy, max output, retry/timeout policy, worker count;
- evidence/quote-grounding rules;
- price snapshot and full-run budget approval ID;
- provider data-control configuration;
- environment/dependency identifiers.

The run should end only when every selected snippet is in exactly one terminal state and every flagged paper is either validly classified or explicitly unresolved. Freeze must refuse any unresolved classification intended for the numerator/denominator.

### The budget ledger is much better, but not yet multiprocess hard

The current v1 run's database ledger contains:

- 21,895 settled outcomes: 58,115,010 input tokens, 8,230,229 output tokens, `$21.4992768`;
- 39 conservative failed reservations: `$0.3132676`;
- conservative total: **`$21.8125444`**, not `$21.74`.

The failed-reserved amount is not proof of actual billing; it is deliberately conservative. Reconcile it with the provider console and describe a billed range rather than calling the ledger total an invoice. The sidecar `usage.json` is not authoritative after crashes; it contains fewer calls than the database ledger.

Within one process, physical retries, in-flight tokens, and USD are now reserved correctly, and 429 responses release their reservations. Remaining pre-run risks are:

- reservations live only in memory until settlement; two concurrent resume processes can each admit work against the same durable baseline;
- there is no single-writer run lease;
- a crash after HTTP dispatch but before `_ledger_write()` can leave an ambiguous unrecorded billable attempt;
- settlement updates memory before the database write (`pipeline/llm_api.py:331-358`);
- `attach_ledger()` sums spend across **all** runs per provider (`:103-119`), so the effective scope is global provider history, not clearly the documented pilot or run;
- the cap is optional (`pipeline/classify.py:486-503`), despite `WORKFLOW.md` saying it must always be supplied;
- Google is an accepted provider even though the current owner decision approves OpenAI and Anthropic pilots only;
- freeze does not check a budget approval, allowed provider/model, price table, or final spend reconciliation.

Before the full rerun:

- add a database-backed run lease;
- insert a durable `reserved` attempt row transactionally before each dispatch, transition it to settled/released/ambiguous afterward, and reconcile stale reservations;
- enforce idempotent item claiming so two workers/processes cannot pay for the same work;
- make a positive USD cap and approval ID mandatory for API analysis;
- explicitly define whether the cap is per pilot, per run, or lifetime provider campaign;
- allowlist approved provider/model combinations;
- archive the tariff source/date/hash and provider-console limits;
- preserve actual returned model and response metadata.

The code's current Luna price snapshot—`$0.20` input and `$1.20` output per million tokens—matched the official Luna model page at audit time. The page also describes special long-context/cache tiers; current prompts are far below the long-context threshold, but the price artifact should still be snapshotted. See the [official Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

## P0-5. Convert `freeze` from a report promise into immutable data

Review-6 hardening correctly rejects dirty/unknown producer commit strings, non-API backends, non-isolated classification, unpinned models, empty consumed-run provenance, and incomplete classification status (`pipeline/report.py:89-122`). That is valuable.

The remaining contract is still too weak:

- scan status may be `partial` with no minimum coverage or approved missingness policy (`pipeline/report.py:85-95`);
- a selected/flagged-only scan can be reported if its selection is not encoded in run params;
- consumed scan runs need only contain the chosen run, rather than be exactly the approved singleton (`:81-84`);
- grounded and rendered gates are CLI options, not release requirements;
- fuzzy/non-rendered/short evidence can be excluded without estimating the induced false-negative selection;
- no acquisition/selection manifest, version-license inventory, final gold, pass threshold, provider policy, or budget reconciliation is required;
- the report calls a frozen candidate one whose “validity gates were enforced” even when evidence and gold gates are absent (`:260-285`);
- the membership hash is only `paper:version`, omitting version basis, artifact, scan item, labels, evidence, render checks, and human validation (`:397-420`);
- the code rereads mutable live tables and does not materialize the selected rows in one snapshot transaction;
- there are no database triggers preventing mutation or deletion;
- `pipeline.build_site` takes raw scan/classification run IDs rather than a release/snapshot ID;
- zero releases exist in the current database.

Implement the two-stage snapshot/release model described above. At snapshot creation, use one database read transaction and materialize every member and its exact references. Hash a canonical row serialization and store the member preimage, not only set-level digests. Refuse later updates/deletes with database constraints/triggers or export a signed/content-addressed immutable release database.

A release candidate should require:

- a retained, exact target/selection manifest;
- reason-coded frame partition and approved coverage/missingness threshold;
- one clean scan protocol and one clean classification protocol;
- zero unresolved classification items in the eligible analysis set;
- explicit evidence construct and exact-render/human-resolution status;
- artifact/version/license provenance;
- provider/model/budget/privacy approval;
- clean builder commit/tree and reproducible environment.

Promotion to a validated public release should additionally require:

- one final gold project drawn from this exact candidate;
- immutable first-pass labels, adjudications, estimator code/output, and thresholds;
- passed or explicitly failed validity gates;
- report/site/aggregate data hashes and deterministic rebuild check;
- release-specific license, citation, correction, and supersession metadata.

The site builder should accept only `--release <id>`, verify all hashes, and refuse unreleased raw-run inputs outside an explicit development mode.

## P0-6. The current v1 result is partial identification, not three-year prevalence

The v1 scan itself is a strong operational result:

| V1 selection/outcome | Count |
|---|---:|
| selected | 112,447 |
| explicit v1 | 15,019 |
| inferred single-version | 97,428 |
| scan `ok` | 110,770 |
| skipped PDF inside tar | 1,621 |
| unknown format | 54 |
| incomplete | 2 |

The manifest hash reconstructs exactly today. However, it stores count/hash rather than the member preimage, is not linked in `scan_runs.params_json`, and is written before an explicit run ID is checked for reuse (`pipeline/scan.py:357-374,407-414`). `scan_items` also lacks the artifact ID/path, and the 1,621 skips have no artifact hash. Persist the exact selection rows in the database and validate run-ID uniqueness before writing sidecars.

For the 2023-08-01 through 2026-08-08 math-primary frame, `reports/report_v1_pure_preliminary.md` reports:

- 133,279 frame papers;
- 85,742 scan-complete;
- 47,554 unresolved after scan, classification, and evidence-gate states;
- conditional raw-label extrema of **2.0% to 37.7%**.

The large gap is not a model-accuracy interval. It is the direct consequence of the owner decision not to fetch the roughly 46.5k unflagged multiversion tail until post-release reception justifies arXiv coordination (`DECISIONS.md:75-80`). That is a legitimate resource/governance choice, but it precludes a precise three-year v1 population-prevalence headline.

Gold labels can estimate classification error **within observed strata**; they cannot repair outcome-conditioned acquisition or identify the unseen tail without assumptions. The defensible publication choices are:

1. obtain/coordinate the tail and retain the intended three-year v1 estimand;
2. redefine the primary estimand to the observed v1-available population and name that selection in every title/denominator;
3. choose a fully covered recent cohort as the primary estimate and make the three-year result partial-identification context;
4. publish only the 2.0%–37.7% bounds plus stratum-specific descriptive rates, with no prevalence headline.

The owner has selected a version of option 4 for early public inspection. The page and paper must therefore say **“partial v1 audit of an acquired/selected frame”**, not “AI disclosure prevalence in three years of math arXiv.” Place the missing-tail fraction and selection mechanism before any percentage.

The monthly v1 report needs repair: `pipeline/report.py:315-331` omits fetched-but-not-in-run and scan-error/skipped counts by month and labels the rate “mixed-version.” Each month should partition its full frame and show coverage extrema, otherwise early/late trends can visually inherit changing selection.

### The mixed-versus-v1 table is not a version-robustness study

`reports/v1_vs_mixed_comparison.md` commendably labels its central confound: both source version and model/pipeline changed. The 85,742-paper common cohort decomposes as follows:

- 75,230 inferred-single-version papers: 21 mixed-only positives and 14 v1-only positives despite nominally identical version, directly revealing model/pipeline disagreement;
- 10,512 explicit-v1 papers: 170 mixed-only and 11 v1-only positives;
- among 4,611 currently multiversion papers: 758 mixed positives, 606 v1 positives, 598 both, 160 mixed-only, and 8 v1-only.

That multiversion set was selected using earlier mixed-version flags and excludes the unflagged tail. It cannot estimate a population revision effect. Call it a **joint version/model sensitivity comparison**, not robustness. A version study needs the same frozen model/prompt on paired versions from a probability sample of both flagged and unflagged multiversion papers, followed by paired human adjudication.

## P1. Render certification is strong evidence provenance, not 88.2% accuracy

All 6,680 valid author-use snippet items in the v2.0 v1 run received render checks. At paper level across that entire run:

- 3,680 papers have at least one author-use label;
- 3,247 have at least one exact-rendered quote: **88.23%**;
- item statuses include 5,495 exact, 777 fuzzy, 260 non-rendered, and 148 quote-too-short;
- no PDF errors remain after the resilience fix.

Within the headline cohort, the comparable exact-certification denominator is different (2,317 of 2,647 author-use papers, about 87.5%). Always state which denominator is used.

This metric is **evidence-certification coverage**, not precision, recall, classifier accuracy, or proof that the disclosure is correctly interpreted. The remaining roughly 12% is also not safely discardable: non-renderability may correlate with source layout, language, disclosure location, or label difficulty. Fuzzy-only cases belong in a blinded human review queue; non-rendered/short cases need reason-coded adjudication or bounds. R3 should be enforced on the fresh v2.2 labels, not inherited from v2.0.

## P1. Vendor, confidentiality, and workstation controls before the full run

The direct API boundary is much safer than agentic Codex: one paper per call, no tools, fixed endpoints, redirects disabled, and ambient proxy/`.netrc` state disabled. It still sends the arXiv ID and up to roughly 2,400 characters of source/metadata context to a provider (`pipeline/classify.py:135-142`). Because scanning includes unreferenced/residual TeX members, “the paper is public” does not guarantee every transmitted source fragment is rendered or intended for publication.

Before the full run:

- replace the external arXiv ID in prompts with an opaque per-call identifier unless the provider needs it;
- minimize context and exclude residual/non-rendered members from provider transmission, or document a separately approved construct;
- set `store:false` explicitly for OpenAI where supported (`pipeline/llm_api.py:437-451` currently omits it);
- record organization opt-in/training status, abuse-monitoring/ZDR/MAM status, region, retention/deletion, DPA, subprocessors/transfers, and incident path;
- persist the actual provider-returned model/snapshot/fingerprint fields;
- define retention/deletion for raw responses, snippet text, request logs, and failed attempts.

OpenAI's current API data-control documentation says API data are not used for training by default unless the organization opts in, while default abuse-monitoring logs may contain prompts/responses and may be retained for up to 30 days; ZDR/modified monitoring require eligibility/approval. Record the project's actual organization settings rather than relying on a general default. See [OpenAI API data controls](https://developers.openai.com/api/docs/guides/your-data).

The repo-root `.env`, database/backups, corpus logs, and annotation packets appear mode `0777` from WSL/DrvFS. POSIX mode bits may not represent effective Windows permissions, so this is not proof of public access—but neither is `.gitignore` an access control. Verify and restrict Windows ACLs, move API keys to a credential store or narrowly scoped run environment, limit packet access per reviewer, encrypt backups, and log packet delivery/deletion.

`pipeline/harvest.py:79-95` retains submitter data, and repository search found no active consumer. Drop it from new harvests and remove/migrate existing copies unless a documented purpose and retention basis are approved.

## P0/P1. Sanitize the repository before any public push

The binding owner decision is aggregate-only: no public per-paper listings or excerpts (`DECISIONS.md:63-64`; `WORKFLOW.md:97-100`). Current tracked files conflict with it:

- `results/ai_ack_hits.{csv,json}`, `results/ai_ack_report.md`, `results/candidate_papers.*`, `results/manual_review.md`, and `results/new_papers.*` contain paper IDs, titles/authors, labels, and long source/PDF excerpts;
- `results/candidate_papers.md` includes copied author contact information and street/institutional addresses;
- `reports/awesome_validation.{json,txt}` exposes per-paper buckets;
- `PITCH.md` contains identified pilot examples and a verbatim result-bearing disclosure;
- `TAXONOMY.md:115-125`, `DESIGN_PLATFORM.md`, and render-check development code identify real case papers and judgments;
- Git history additionally contains the deleted result-bearing spotcheck, a stale distribution ZIP, and an AWS instance/IP inventory.

This is not merely a theoretical privacy concern. It contradicts `LICENSE:29-31`, which says arXiv excerpts are never redistributed, and the source text may carry paper-specific licenses and personal/contact data. Before a public remote is created:

1. quarantine all expressive/per-paper artifacts outside Git;
2. replace public examples with synthetic or consented/deidentified cases;
3. exclude all development examples from the final gold sample to avoid unblinding;
4. rewrite the local history if the repository will be public;
5. run a dedicated secret/history scan (for example, gitleaks plus targeted corpus/ID/excerpt checks);
6. clone the rewritten repository into a fresh directory and verify that no corpus, packet, verdict, contact detail, cloud inventory, credential, or stale deploy artifact remains.

There is currently no Git remote or tag, which makes this the best and least disruptive time to do it.

The specification layer also conflicts with the binding decision: `PITCH.md`, `TECH_NOTES.md`, and `DESIGN_PLATFORM.md` still contemplate open per-paper annotations/IDs/hashes and ODC-BY, while `DECISIONS.md`, `WORKFLOW.md`, and `LICENSE` say aggregate-only/CC BY per release. Add a precedence statement and artifact publication matrix covering code, aggregate tables, validation metrics, per-paper labels, excerpts, identifiers, hashes, and restricted reviewer data.

The 13 tracked `.claude/docs/lean4` and `.claude/tools/lean4` files appear unrelated and have no clear project provenance/license. Remove them or add upstream provenance and compatible license/NOTICE before the root MIT scope could be read as relicensing them.

## P1. Publication, governance, and public communication

### The current site is appropriately exploratory, but not a release path

The current generated site still uses the old dirty/non-isolated Codex taxonomy-2.0 run. Its `noindex`, top warning, limitations, and machine-readable `release_status: unreleased_exploratory` / `do_not_cite: true` are good safeguards. It should remain a private inspection artifact.

`pipeline/build_site.py` still accepts arbitrary run IDs and always emits exploratory status; it does not consume a release. Current detailed JSON/site tables can expose singleton monthly/subfield events—for example, a one-event cell in a small month—which can be cross-referenced to identify a paper. A full-window subfield threshold does not protect each cell (`pipeline/build_site.py:330-334`). Apply per-cell minimum counts and complementary suppression or coarser aggregation to every public cross-tab, including exact tool/model names.

The new “+43% submissions” hero tile sits beside the disclosure trend and invites a causal interpretation. If retained, explicitly state that the juxtaposition is contextual only, not evidence that AI caused submission growth; use comparable calendar windows and verify OAI completeness.

The copy “Full pipeline code, validation data…” conflicts with restricted per-paper validation records. Say “validation protocol and aggregate validation results.” Describe the Codex work as a separate AI-system audit, not independent human peer review. “All scientific-validity decisions by human” is too categorical given the documented AI role in design/metrics; “the human owner retained final responsibility and sign-off” is more accurate.

### Governance package still needed

The new MIT license and funding/AI disclosures are welcome. Before launch, add:

- an operative per-release aggregate-data license and data dictionary;
- `SECURITY.md` with private vulnerability reporting;
- a privacy/data-governance statement covering controller/contact, purpose/legal basis, processors, access, retention/deletion, rights/objections, breach response, and restricted artifacts;
- correction, appeal, takedown, and release-supersession policy;
- governance/roles/conflicts/author-contribution statement;
- `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` if contributions are invited;
- `CITATION.cff`, release changelog, methods version, and DOI/archive plan;
- institutional ethics/privacy/DPO/vendor determination, including the human-reviewer arrangement;
- reviewer agreement covering confidentiality, secure packet transfer, conflicts, compensation/credit, no redistribution, and deletion.

Clarify funder role and competing interests, and verify exact grant/gift wording with the relevant institutional records. The intended CC BY aggregate license should become explicit in each frozen release, not remain a scope-note intention.

### Accessibility, security headers, and reach

Before a public domain is promoted:

- make generated tables first-class and server-rendered rather than JS-only fallbacks;
- add a `<noscript>` data table/summary;
- give every chart a useful chart-level accessible name/description;
- ensure keyboard/touch operation, visible focus, narrow-phone layout, high contrast, reduced motion, and screen-reader testing;
- replace remaining `innerHTML` construction before any contributor-controlled data enters the build;
- add and test CSP, `nosniff`, referrer, HSTS, framing, and permissions headers at the host;
- add deterministic packaging, preview/approval, rollback, and deployed-byte verification;
- add canonical/social metadata, stable methods/limitations/correction/contact pages, aggregate downloads with schema/checksums, citation metadata, and a versioned change feed.

Credibility gates should precede reach optimization. A stable correction mechanism and honest partial-identification graphic are more valuable than a viral but weakly identified headline.

## P1. Code, CI, and reconstruction gaps

The 112-test suite is fast and valuable; GitHub Actions are pinned and do not deploy. `.github/workflows/ci.yml` nevertheless says “tests + site build” while running only pytest. Before the final run/release, add tests for:

- R4/R5 canonical and adversarial cases, including human/model schema parity;
- `zero_contribution`, `undetermined`, `not_applicable`, and catalytic cross-field invariants;
- final packet/release hashes, cache invalidation, local-storage keying, fail-closed ingest, assignment/version/codebook rejection, and uniqueness;
- explicit shared-subset assignment and third-adjudicator flow;
- executable calibration/estimator reproduction with non-evaluable cases;
- adaptive batch bisection and terminal single-snippet failure;
- DB run lease, concurrent reservations, crash-after-dispatch reconciliation, mandatory cap/approved provider;
- snapshot transaction/materialized membership and DB immutability;
- selection-manifest run-ID collision and exact member preimage;
- release-only site build, deterministic double build, small-cell/complementary suppression;
- hostile archives/TeX/HTML/Markdown/CSV, migrations, accessibility, links, and security headers.

CI should actually build a fixture analysis snapshot, gold packet, estimator output, release, and site twice and compare hashes. Add explicit least-privilege workflow permissions, timeouts/concurrency, dependency/license/SBOM/secret scans, lint/type checks, migration reconstruction, and deploy separation. The dependency lock pins versions but lacks hashes, and system tools remain outside a reproducible container/environment.

Other reconstruction defects remain:

- OAI reparse still does not recursively match the nested archive layout, and deleted records are skipped rather than tombstoned;
- scan selection sidecars retain only a digest rather than member rows;
- the v1 evidence-edge repair is described in prose but not supplied as an idempotent repair/migration with before/after hashes;
- acquisition/version artifacts still lack per-version arXiv license capture;
- current reports/site cannot be reproduced from a clean clone without the private multi-gigabyte database/corpus and a signed aggregate release artifact.

## Current empirical state

At approximately 2026-08-12 13:07 UTC, read-only inspection found:

| Object | Count/status |
|---|---:|
| schema version | 5 |
| papers / versions | 235,342 / 418,232 |
| files / artifacts | 169,166 / about 187,918 |
| scan runs / items / hits | 4 / 281,870 / 982,232 |
| classification runs / items / evidence edges | 6 / 145,172 / 338,896 |
| render checks | 14,758 |
| annotations | 150, one reviewer |
| releases | 0 |
| SQLite integrity | `quick_check=ok`; no foreign-key violations observed |

Principal current runs:

- `texv1-20260811T215148`: partial, clean code `12eca21`, 112,447 items, 110,770 ok, 56 counted errors/incomplete plus 1,621 explicit skipped PDF-tar members;
- `cls-20260811T220922`: partial, `api:openai`, `gpt-5.6-luna`, taxonomy 2.0, clean code `12eca21`, 71,194 items, 172 errors;
- current site: old mixed-version `tex-20260810T205113` plus dirty non-isolated Codex run, taxonomy 2.0, explicitly unreleased.

Tracked artifact hashes at the review snapshot:

- `TAXONOMY.md`: `99e5f9a045e99a370cda4b8d8649c045f7227c46c05a809b8472bd313c74c900`
- `GOLD_STUDY.md`: `2d925421493a5988ec06ab469e1a910a8c02e42a14d2dc5031068cca4065d58b`
- `DECISIONS.md`: `873eaa073c730ae8141ae4f268ca90ad4a83a412ea7680794fdaccd24dcc843b`
- v1 preliminary report: `3feb6f30e5692ba3c8482a0dbe0c424a44f1f0e469f5335048d517ed4dc850ae`
- v1/mixed comparison: `7d0527d1f5205e509a18ed03ad1fe27ed787f62dc84a7e6b4a0339f9ea3212f3`
- current site index: `312a58f3bc7a9bcaf60e785bcc402ed5b298868b1757fb55d4b2f2c1622c7361`
- current site JSON: `bae3a5de89b5f98c009f1e79ee512f4caf5bebe3da6bc4212faefd7ea880a2e4`

These are diagnostic observations, not a release snapshot. The database is roughly 3.1 GB and local filesystem/SQLite timing can change; counts should not be quoted as immutable without the materialized snapshot proposed above.

## Documentation drift to fix before instrument freeze

- `DECISIONS.md` says newest-first but the 2026-08-12 section follows older sections; it says calibration closed at 149 rather than 150 ingested/149 comparable; taxonomy v2.1 remains listed as open after being changed.
- `README.md` says calibration is in progress and the v1 path has not run end-to-end; it points to review 6 and calls Codex reviews “independent.”
- `GOLD_STUDY.md` still names codebook v2/R1-R3, contains contradictory non-evaluable handling, overstates what plants directly measure, and its example command omits plants and embedded version-pinned PDFs.
- `WORKFLOW.md` also omits plants/PDF embedding, builds gold from raw runs rather than a snapshot, builds the site from raw runs, and ends by describing Codex/bulk batching despite the API analysis decision.
- `TAXONOMY.md:127-132` describes verdicts `OK / DOWNGRADE / FP`, unlike the actual human verdict vocabulary.
- `TAXONOMY.md` reports 96.6%, 0/97 NEG, and n=150 without explaining the version-skew exclusion; replace with scripted, denominated aggregate results.
- `reports/report_v1_pure_preliminary.md` correctly has a do-not-cite banner, but “Prevalence” and monthly rows can still read as full-coverage estimates.
- older platform/pitch/technical documents conflict with aggregate-only publication and operative licensing decisions.

Treat `DECISIONS.md` as binding only when code/tests enforce the decision; add a status (`proposed`, `approved`, `implemented`, `verified`, `superseded`) and links to enforcement tests/artifacts.

## Status against iteration 6

### Fixed or materially improved

- refill argument truth table and finite target-member acquisition;
- content-bound artifact and PDF-cache behavior;
- strict Anthropic and OpenAI native schemas;
- all-C0 TeX corruption rejection;
- canonical protocol-hash resume identity;
- per-physical-attempt/in-flight budget reservation and 429 release;
- durable spend ledger across resumes;
- v1 scan execution and explicit/inferred basis;
- v1/mixed report caveat;
- render-check completion and fuzzy demotion;
- math-ph/frame owner decision;
- evidence-edge repair in the live DB;
- calibration completion and version-skew diagnosis;
- software license, funding disclosure, and project AI-use disclosure;
- 112 passing tests.

### Partial

- budgets: durable settled spend, but reservations/leases are not multiprocess/crash-atomic and cap scope/approval is unclear;
- v1 provenance: selection hash reconstructs, but member preimage/artifact IDs are not release-bound;
- classification: most items terminal, but deterministic complex-paper truncations remain;
- taxonomy: R4/R5 documented, but human tooling, invariants, versioning, and construct boundaries disagree;
- gold: calibration evidence exists, but final sampling, chain of custody, adjudication, and estimators do not;
- freeze: producer checks improved, but no materialized candidate or gold-gated release;
- publication: license/disclosures improved, but tracked expressive data and governance gaps remain;
- site: honest exploratory status, but no release-only build, small-cell control, or deployment chain.

### Newly identified in iteration 7

- R5 is impossible in the human form/ingest;
- R4's “any role” versus method-component exclusion is operationally contradictory;
- `none + catalytic` is accepted despite R2;
- no impact value represents insufficient detail;
- two incompatible R4 wordings share taxonomy version 2.1;
- calibration has 150 labels/149 comparable, not 149 total;
- 96.6% agreement and 0/97 NEG use inconsistent denominators;
- fixed 30-snippet batches caused 171 systematic output truncations;
- final packet/localStorage/ingest are not codebook/artifact/packet-hash bound;
- two graders cannot satisfy the written independent-adjudicator rule;
- tracked result files contain copied direct contact/address material;
- current public tables can expose singleton cells;
- the “full v1 scan” still leaves a population-identification interval too wide for a prevalence headline.

## Pre-run go/no-go checklist

Every item in this section should be machine-checkable or signed off before the indicated phase.

### Gate A — before the full Luna rerun

- [ ] Owner freezes the exact R4 scope using an operational decision tree.
- [ ] R5 is represented separately from undetermined/not-applicable impact.
- [ ] Human form, export, ingest, model schema, validator, report, and tests share the same values.
- [ ] Cross-field invariants reject zero-contribution plus catalytic contribution.
- [ ] Final codebook receives a new version (at least 2.2) and content hash.
- [ ] Both intended graders and Luna pass a small held-out R4/R5 comprehension exercise; cases are excluded from final gold.
- [ ] Adaptive deterministic batch splitting resolves forced truncation tests.
- [ ] Prompt and native object schema agree exactly.
- [ ] API run lease and durable pre-dispatch reservation/ambiguous-attempt recovery exist.
- [ ] Positive full-run USD cap, provider/model allowlist, tariff snapshot, and owner approval ID are required and stored.
- [ ] Vendor data controls/retention/DPA and local ACL/secret handling are documented and approved.
- [ ] One clean protocol hash and fresh run ID are recorded; no v2.0 resume/reuse.

### Gate B — before drawing or opening final gold labels

- [ ] Classification has zero unresolved eligible items or a prespecified reason-coded exclusion/bound.
- [ ] Fresh v2.2 render checks are complete; fuzzy/non-rendered cases have an approved human-resolution plan.
- [ ] One immutable analysis snapshot materializes exact members/artifacts/labels/evidence/render/missing states.
- [ ] Final sample is drawn from that snapshot, not recomputed dates/categories over mutable tables.
- [ ] Packet manifest binds exact version/artifact/context/PDF/taxonomy/order/packet hashes.
- [ ] Context cache and browser state are packet-hash keyed.
- [ ] Ingest is fail-closed and validates reviewer assignment, item/version, codebook, and packet hash.
- [ ] Shared double-coded subset is explicit and adequately stratified.
- [ ] A third adjudicator is secured, or a different coherent protocol is preregistered.
- [ ] COI, evaluability, search-process, version-verification, and adjudication fields exist.
- [ ] Estimator/CI/threshold code is written, fixture-tested, and frozen before labels are inspected.

### Gate C — before a scientific/public release

- [ ] The publication estimand matches the actually observed v1 frame; no unqualified three-year prevalence claim under 2.0%–37.7% partial identification.
- [ ] Gold estimates and pass/fail thresholds are computed from immutable first-pass/adjudicated data.
- [ ] Measurement, acquisition, version, render, and non-evaluable uncertainty are carried into headline claims.
- [ ] Site/report/data build only from a validated release ID and reproduce byte-for-byte in CI.
- [ ] Small-cell/complementary suppression is applied to every public cross-tab.
- [ ] Public repository HEAD and history are sanitized and verified from a fresh clone.
- [ ] Privacy, security, governance, correction, citation, and operative data-license package is complete.
- [ ] Institutional/vendor/legal/ethics sign-offs required by the owner/institution are recorded.
- [ ] Deploy preview, approval, security headers, accessibility checks, rollback, and artifact checksums pass.

## Recommended sequence from here

1. **Pause the confirmatory launch for a short instrument-freeze sprint.** Resolve R4/R5, add `undetermined`/not-applicable semantics, enforce invariants, bump to v2.2, and align the human/machine manual.
2. **Run a small private comprehension test** with both intended graders and Luna on canonical edge cases. Revise only before the confirmatory sample; then lock the codebook and analysis plan.
3. **Close the rerun mechanics:** adaptive splitting, prompt consistency, run lease, durable reservations, mandatory approved cap/provider, and vendor/privacy configuration.
4. **Run one fresh clean Luna/v2.2 classification** over the approved v1 selection, resolve every terminal failure, and perform fresh render checks.
5. **Materialize an analysis snapshot** with exact artifacts, labels, evidence, render results, version basis, selection membership, missingness, and protocol hashes.
6. **Build the final gold system from that snapshot:** explicit shared subset, immutable packets/PDFs, fail-closed ingest, third adjudicator, and executable estimators.
7. **Collect independent labels and adjudicate** without modifying the instrument. If a gold case forces a taxonomy change, version the instrument, rerun classification, and draw a fresh confirmatory sample.
8. **Choose the honest publication estimand.** Either acquire the remaining tail after coordination, use a fully covered primary cohort, or publish partial-identification/selected-frame results without a population-prevalence headline.
9. **Promote a validated release** only after prespecified gates pass; build site/report/data solely from that release.
10. **Sanitize and govern the public repository**, then deploy an immutable tagged artifact with correction/rollback support.

## Verification performed

- Reviewed the complete tracked repository at `6edb339` and the full diff from `e2293d6`.
- Ran the fixture suite with cache/bytecode disabled: **112 passed**.
- Ran Python parse/compile, shell syntax, dependency consistency, Git whitespace, and status checks; no tracked worktree changes were present before this file.
- Inspected SQLite read-only; `quick_check` passed and no foreign-key violations were observed.
- Reconciled scan/classification/error/render/annotation/release and spend-ledger aggregates.
- Independently checked the v1 selection counts/hash and calibration arithmetic/equivalence denominators.
- Reviewed restricted calibration manifests, contexts, packets, export-derived database rows, and aggregate summary without reproducing paper-level content here.
- Reviewed the generated v1 report, v1/mixed comparison, current exploratory site/JSON, and publication/licensing files.
- Checked the current official OpenAI Luna model/pricing and API data-control pages.

I did not perform a formal penetration test, legal opinion, institutional ethics determination, provider-invoice audit, full secret-history scan, accessibility lab test, cloud/IAM inspection, stable physical database hash, or full bibliography re-verification. The statistical recommendations should be frozen in executable code and, ideally, reviewed by an independent survey/measurement statistician before public claims.

## Bottom line

The project is close to being ready for a **confirmatory run**, but it is not there yet. The v1 acquisition, strict non-agentic API path, provenance spine, spend accounting, render checks, and calibration work are meaningful accomplishments. The remaining defects sit exactly where a final study is most vulnerable: the definition of the outcome, equality of human/model instruments, immutable packet evidence, handling of complex-paper failures, analysis weights, adjudication independence, and release identity.

Close those contracts first. Then the next Luna run and two-grader study will generate defensible evidence instead of becoming another development round that has to be discarded. Until the missing v1 tail or an alternative primary frame is resolved, even a technically validated classifier should support only a selected-frame/partial-identification result—not an unqualified estimate of AI-disclosure prevalence across three years of mathematics papers.
