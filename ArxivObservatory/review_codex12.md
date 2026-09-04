# ArxivObservatory repository review — iteration 12

**Audit snapshot:** Git commit `8ee90eb0d7853c4bd9fca75c5a4461bf68616557`, tree `f2530b16e0bf7cad2b24ecfdd00c2d85b180c448`, on 2026-08-14. The worktree was clean before this review file was added.

**Primary delta reviewed:** all changes after the iteration-11 snapshot `5a95eab`, especially taxonomy v2.7; the machine comprehension exercise and owner sign-off; the full v2.7 Luna classification and rendering pass; campaign accounting; the arXiv-support exchange and live historical-v1 refetch; the full-cohort report/site rebuild; current gold-study machinery; release freezing; publication disclosure control; privacy, governance, CI, accessibility, and deployment readiness.

**Audit boundary:** intended to be read-only except for creating this report. I did not call a model/provider API, start, stop, or deliberately alter a pipeline/cloud job, change the refetch, perform application-level database/corpus/campaign/annotation writes, contact arXiv, or publish anything. Restricted annotation material is discussed only in aggregate. One test has a newly identified isolation defect: although invoked as a fixture test, it opens the default live database in write mode before rejecting a legacy input. I observed no row-level DML from that path, but `db.connect()` executes SQLite write-mode pragmas, so incidental database/WAL metadata changes cannot be excluded. The test run was therefore not as hermetically read-only as its name and CI comment imply. Current official arXiv and OpenAI documentation was checked where it directly affects crawl pacing, provider data controls, model configuration, and tariff evidence. I did not repeat a systematic verification of the scientific bibliography.

## Executive verdict

This is the strongest operational state audited so far. The project completed dispatch and accounting for all 71,194 unique planned v2.7 classifier inputs over the selected v1 scan, yielding 71,180 valid outputs and 14 explicit non-ok rows; evidence lineage closes exactly; the report headline is grounded and exact-render gated; R5 co-located states and the external-artifact diagnostic now survive machine validation and paper rollup; the site is visibly unreleased and `noindex`; arXiv support pointed the project to the standard export-service subset route; and the test suite has **154 passing tests** in a writable workspace.

Those achievements do **not** yet form the final launch object. The central reason is chronological and scientific, not cosmetic: the live historical-v1 refetch is adding the papers absent from the scan on which the v2.7 run, report, render checks, and site were built. The old selected frame inherits outcome-related selection because its acquired multiversion component was scanner-flagged-first. Once the tail is complete, the correct sequence is a new metadata/cohort freeze, a new exact-member v1 scan, classification against that scan, rendering, a materialized release candidate, and only then final-gold sampling. The current run is a strong engineering benchmark, not a release that can simply be promoted.

There is also an immediate acquisition-governance ambiguity. The recorded active manifest contains **56,727 targets at 4.0 seconds**, while the narrative owner decision and sent-email fact check describe approximately **46,500 math-primary targets at 6 seconds**. The exact approved command included `--include-unflagged-tail`; under the code and default environment that command selects the broader AWS `math_ids.txt` membership at four seconds. Its target set includes **10,177 non-primary cross-list papers** outside the analysis/report cohort, plus 31 primary-math papers outside the report dates. Four seconds is still more conservative than arXiv's recorded fleet-wide maximum of one request every three seconds, provided exactly one process/machine is operating; the observed prefix is orderly and valid. This is therefore neither proof of an unauthorized job nor evidence for an emergency kill. It is a material mismatch between the approved command and its descriptive scope/rate. Obtain prompt owner confirmation and amend the record; if the owner's actual intent was the narrower 46,519-paper cohort at six seconds, pause and restart only the remainder against a freshly computed exact manifest derived from that cohort. Do not launch a second instance.

The completed v2.7 classification is honestly `partial`: **71,180 `ok` and 14 non-ok items** out of 71,194 unique protocol inputs. The full-run campaign remains `active`, and the decision log omits its conservative failed reservation in the reconciliation arithmetic. The current report/site consume a pre-tail, scientifically incomplete-frame scan and a partial classification. Freeze correctly refuses this classification today, but the more important point is that finishing these 14 rows against the old scan would not solve the expanded-frame problem.

The measurement instrument is promising but not yet validated by the intended humans. The tracked checker reports `expected_ok=15/16` when applied to the local generated comprehension artifact, but it only tests fields explicitly present in each expected object. One catalytic vignette returns a substantively false explicit-zero state in one repetition, yet the expected object omits that field; fully specified semantic correctness is therefore at most **14/16**, not 15/16, and the exact total-field score is unknown. Stability is 16/16 for polarity and scalar impact, 15/16 for flags/categories/R5, and 13/16 across all recorded axes. Both intended graders' v2.7 comprehension exercise remains unfinished; all 150 human annotations in the database are one-reviewer v2.0 development labels. The prior development analysis had 149 comparable items, v2.0 shown-positive precision 28/32 (87.5%), and binary agreement 145/149 after excluding one version-skew case; a later in-sample adherence reanalysis gave 147/149, decomposed as 51/53 model-evaluable and 96/96 structural no-snippet cases. These are useful development checks, not v2.7 accuracy, sensitivity, or inter-reviewer reliability.

The final gold study is still a no-go. Its production builder does not exist: the only builder hard-codes calibration-only status, takes raw run IDs, reads mutable current files/metadata, reuses cached contexts by existence, lacks packet/artifact/PDF/assignment hashes, fails open without a manifest, does not guarantee a shared double-coded subset, and has no adjudication or design-weighted estimator implementation. Gold must be sampled from the new materialized release candidate after the tail, not while its multiversion acquisition component remains outcome-selected.

Finally, public launch is independently blocked. Current HTML/JSON/reports disclose hundreds of singleton/doubleton time cells and permit complementary differencing; reachable Git history contains deleted per-paper expressive material; current planning documents still contradict the aggregate-only decision; releases are mutable-query digests rather than materialized artifacts; provider/local privacy governance is unverified; and the repository lacks an operative aggregate-data license, privacy/security/corrections package, release-only CI/deploy path, and accessibility/security-header pass.

### Readiness call

| Activity | Readiness at this snapshot |
|---|---|
| Keep the current refetch running unchanged | **Prompt owner confirmation required**: no rate emergency; exact command was approved, but its narrative scope/rate were described incorrectly or ambiguously |
| Launch a second/replacement refetch process | **No-go** until a fleet lock and exact manifest/rate decision exist |
| Private inspection of the v2.7 report/site | **Acceptable only as restricted, exploratory, do-not-cite material after correcting the false coverage sentence** |
| Treat the completed v2.7 run as the final analysis | **No-go**: partial and bound to the pre-tail selected scan |
| Draw or field final gold | **No-go** until the tail, new scan/classification/render, and materialized release candidate are complete |
| Frozen scientific release or citable trend/prevalence claim | **No-go** |
| Public Git repository or real-data website | **No-go** until disclosure, history, governance, release, and deploy gates pass |
| Synthetic preview / protocol-only public materials | **Feasible** after a public-artifact allowlist and clean export |

The shortest defensible path is:

1. reconcile the live refetch's approved command with its descriptive scope/rate and enforce one serial operator;
2. finish and invocation-reconcile the owner-confirmed manifest;
3. freeze final metadata/version/date/category membership;
4. finish the human v2.7 comprehension decision and correct the machine exercise;
5. run a new exact-member v1 scan with explicit exclusion strata;
6. classify the new scan under a fresh, closed-loop campaign and resolve every target item;
7. render/ground all public label slices;
8. materialize an immutable release candidate;
9. run release-bound double-coded gold, adjudication, and locked estimators;
10. build disclosure-controlled public artifacts from that release alone; then clean/export history and deploy through a protected release path.

## Snapshot and verification

### Automated checks

- `python3 -m pytest -q -p no:cacheprovider`: **154 passed in 3.81 s** when the workspace was writable.
- The same suite under an enforced read-only workspace produced **153 passes and one failure**, revealing that `test_markdown_ingest_is_legacy_gated` reaches `db.connect()` on the default live database before rejecting legacy markdown (`pipeline/annotate.py:812-824`; `tests/test_review5.py:116-127`). Move the legacy gate before connection and inject a temporary database in the test.
- Python AST parsing succeeded for all 39 checked pipeline/test Python files.
- `python3 -m pip check`: no broken requirements.
- `bash -n`: passed for the tracked shell scripts checked.
- `git diff --check 5a95eab..HEAD`: passed.
- An `immutable=1` view of the main SQLite database file eventually returned `ok` for `PRAGMA quick_check` during one long run. Because the database was actively receiving refetch artifacts through its WAL, this can omit uncheckpointed WAL state and is not a current logical-database integrity certificate. Global counts below are point-in-time. A full foreign-key scan was not completed; do not present this live database as a stable release hash.
- The worktree was clean before this report was created.

### Point-in-time operational state

The stable analysis-relevant facts at the snapshot were:

- schema version: **8**;
- releases: **0**;
- final-gold annotations: **0**;
- human annotations: **150**, all one reviewer/project under v2.0;
- active run leases: **0**;
- the selected v1 scan: **112,447** items, of which 110,770 are `ok`, 1,621 skipped PDF-in-tar members, 54 unknown-format, and 2 incomplete;
- the current three-year math-primary frame: **133,279** papers;
- papers scan-complete in the current report frame: **85,742**, comprising 10,512 explicit-v1 and 75,230 inferred-single-version rows;
- the v2.7 classification: **71,194 unique items**, 71,180 `ok`, 14 non-ok, 21,423 papers, and 166,412 evidence edges;
- the current exact-render-gated paper-level author-use count: **2,324**;
- active live historical-v1 refetch: **56,727** manifest targets, with approximately 9,048 invocation outcomes at the later audit checkpoint (8,962 source successes, 84 PDF-only successes, and 2 terminal 404s); the job and artifact count continued to advance.

The live refetch means the database does not have a stable final logical fingerprint. Any count in this report is an audit observation, not a release manifest.

### Full-run integrity

The planned classification construction initially yields 71,242 logical snippet groups. Exactly 48 are duplicate protocol inputs, leaving **71,194 unique hashes**. All 71,194 are stored. The apparent 48-row difference is therefore deduplication, not missing work.

The evidence graph closes exactly: all 166,412 expected evidence links are present, with no item missing evidence and no extra edge in the audited run. The 14 non-ok items are explicit and reason-coded:

- 9 output-count mismatches on nominal `finish_reason=stop` responses;
- 1 returned-ID coverage error on a nominal `stop` response;
- 2 invalid `author_use` impacts;
- 2 invalid R5 consistency combinations whose repair calls ended in truncation.

They affect 13 papers overall; the report frame includes six papers for which classification failed completely and one with mixed success/failure. Current report/site copy reports only the six fully failed papers, so it understates failure-affected membership.

The run is bound to commit `28def3a`. Resume identity correctly refuses the current `8ee90eb` checkout even though later changes are predominantly site/docs. The supported old-run retry would require an exact clean `28def3a` checkout and the same campaign/scan. That is not a good use of effort while the acquisition frame is changing. After the new scan, a fresh classification or a newly designed, independently validated content-addressed reuse protocol is required; current hashes include `scan_run`, so silent carry-forward is neither supported nor auditable.

### Rendering and R5 aggregates

The author-use evidence pass contains 6,518 classifier items:

- 5,433 exact-rendered/dehyphenated matches;
- 734 fuzzy-only matches, correctly excluded from exact certification;
- 230 non-rendered matches;
- 120 quotes too short to certify;
- 1 PDF error.

At paper level, all **2,324 counted author-use papers** have at least one exact rendered item, while **322 additional candidate papers** are excluded by the evidence gates. This is strong evidence-certification engineering. It is not a precision or sensitivity estimate.

The v2.7 overlapping paper states reproduce in the report/site:

- contributing-use papers: **2,054**;
- papers with an explicit-zero attempt: **41**, of which 32 also have contributing use;
- papers with undetermined impact: **437**, of which 175 also have contributing use.

This fixes the scalar-max loss highlighted in earlier reviews. The `external_ai_artifact` diagnostic also survives rollup now. However, its public count is not evidence-gated like `author_use`: retrospectively, only 4 of 58 headline-frame papers currently have an external-flagged item satisfying the available grounding/exact-render criteria; 54 lack such certification. This is not a separately completed external-diagnostic certification protocol. Report raw and certified diagnostic counts separately and implement a dedicated gate before calling the public slice certified.

### Campaign state

The full-run campaign has strong internal accounting:

- 22,490 physical attempts map one-to-one to 22,490 spend rows;
- 22,489 successful billed calls have unique provider request IDs;
- one transport failure remains conservatively charged;
- no reservation is left in the open `reserved` state;
- recomputation under the campaign-bound four-class tariff matches settled spend exactly.

Settled spend is **$37.64436342**. Including the conservative failed reservation, the full-run ledger is **$37.66230792**. With the prior pilot campaign (**$0.536088**), conservative combined ledger spend is **$38.198396**, not `$38.1805` as stated in `DECISIONS.md:11-12`. The difference from the owner's `$37.91` console observation remains about 0.76%, inside the declared one-percent tolerance, but the arithmetic and meaning of the conservative row should be corrected.

The campaign is still `active` and has no closure event. Close it only after deciding whether it will be used for an exact-commit retry; otherwise reconcile and close now. The post-tail final run needs a fresh purpose-bound authorization and budget.

One provenance limitation remains: 153 HTTP-200 responses with `finish_reason=length` have request and usage records but no response hash/raw response because the adapter raises before returning the raw payload. Preserve a normalized hash and stop reason for every physical response, even when semantic parsing fails.

## What is genuinely stronger since iteration 11

The following repairs are real and should be retained:

- taxonomy v2.7 has an exact, reproducible taxonomy/manual/prompt/schema bundle;
- R5's co-located explicit-zero and undetermined states are machine-visible and reach report/site overlapping slices;
- the attempted-use exception is named in the machine definition;
- `method_component` and `external_ai_artifact` survive paper rollup;
- the machine/human taxonomy text is substantially better aligned;
- the full classifier target's unique hashes and evidence graph reconcile completely;
- run/campaign/model/price/holder admission and pre-dispatch attempt accounting are materially stronger;
- the fresh full-run campaign uses the correct four-rate snapshot, including Luna cached reads at `$0.02/M` and cache writes at `$0.25/M` as documented on the current [official model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna);
- missing/malformed usage remains conservatively reserved rather than settling at zero;
- prompts omit arXiv IDs, only the selected provider key is loaded on the supported path, unrelated provider keys are scrubbed, OpenAI uses `store:false`, redirects and ambient proxy credentials are disabled, and provider error bodies are minimized;
- exact render gating excludes fuzzy evidence from the headline;
- the refetch mode truth table prevents accidentally entering the unapproved tail mode, stores the exact target preimage, shuffles deterministically, and maintains an invocation ledger;
- the active attempt prefix has no duplicate or out-of-manifest targets and reconciles successful source/PDF artifacts cleanly;
- current report/site honestly expose partial status, gates, release status, `do_not_cite`, and `noindex`;
- the static site remains tracker-free and includes useful adjacent data tables/focus styles;
- CI actions are SHA-pinned and there is no automatic deployment that can accidentally promote the current state.

These strengths make the remaining work tractable. They do not substitute for a new final-frame run, gold validity, or a public release boundary.

## Gate A — resolve and complete the historical-v1 acquisition

### A1. The approved command and its narrative job description diverge

`pipeline/fetch.py:173-213` defines the full tail as every multiversion member of `pipeline/aws/math_ids.txt`. It does not apply the release predicate (`primary_category LIKE 'math%'`) or the report date frame. The active manifest is internally valid but broader:

- manifest targets: **56,727**;
- primary-math targets: **46,550**;
- primary-math targets inside the release dates: **46,519**;
- non-primary cross-list targets: **10,177**;
- primary-math targets outside the dates: **31**.

`DECISIONS.md:29-46` and the sent-email fact check describe roughly 46,500 math-primary papers and six-second pacing. The manifest records four seconds. At the later audit checkpoint, 1,589 out-of-frame targets had already been attempted and 8,619 remained.

Fetching a somewhat broader public subset is not intrinsically scientifically invalid or abusive, and completed source artifacts remain useful. The exact approved command does select the broader tail under current code/defaults; the problem is that its narrative scope and pace do not match what it executes. Resolve this ambiguity promptly in one of two ways:

1. if the owner's intended acquisition scope was the analysis cohort, pause, preserve all completed artifacts, create a new exact primary/date-frame remainder manifest, and resume at the represented six-second rate; or
2. confirm that the exact command reflected the owner's intent, record the broader 56,727-target/four-second interpretation, and correct the decision/outreach fact check, purpose, expected duration, and final methods account.

Whichever choice is made, distinguish the acquisition universe from the analysis cohort. A broad cache can be legitimate, but the release scan manifest must contain only the prespecified analysis membership.

### A2. Support pointed to a standard route; it did not endorse the project

The support reply resolves the prior coordination question by pointing the project to the standard export-service subset route and making the published terms the governing limit; it does not approve this project's exact target manifest or conclusions. The [arXiv bulk-data guidance](https://info.arxiv.org/help/bulk_data/index.html) still recommends AWS/Kaggle for broad bulk reuse, and the [API terms](https://info.arxiv.org/help/api/tou.html) require one connection and at most one request per three seconds across all machines, research-use constraints, license compliance, and no implication that arXiv endorses the downstream project.

Four-second serial pacing is inside that numerical limit if and only if this is the sole project request stream across every host. It is not the recorded “two-times-conservative” six-second pace. Public wording should say arXiv support confirmed the standard route; it should not suggest methodological endorsement, data partnership, or approval of the observatory's conclusions.

### A3. Current safety depends on operator discipline, not an enforceable fleet guard

The live prefix is healthy, and several fetch controls are good: deterministic membership, content inspection, `trust_env=False`, redirect/rate handling, attempt ledgering, and invocation reconciliation. The remaining long-run hazards are meaningful:

- no database acquisition run/lease or host-wide singleton;
- no fleet-wide start-time scheduler, and no validation that `ARXIV_FETCH_DELAY` is finite and at least three seconds;
- two invocations can select the same todo, duplicate traffic, and race paths;
- run names use second-resolution time and sidecar files can collide;
- response bodies are buffered without a strict content-length/streaming byte cap;
- no preflight free-space reserve (disk was ample at audit, but the invariant is absent);
- final artifact paths are written directly rather than temp + hash + fsync + atomic rename;
- resume selection trusts an artifact row without rechecking the current path/hash;
- the manifest does not bind code commit, full effective argv/env, user-agent, query snapshot, or the authorization/support evidence hash;
- success reconciliation consults global artifact rows rather than exclusively binding each success to the acquisition run.

Before another long crawl, add an acquisition-run table with immutable target rows, owner authorization digest, code/query/metadata hashes, lease/fencing, start-to-start pacing, per-target claim, response identity, byte/content validation, atomic writes, and terminal completion manifest. For the current job, the minimum operating rule is: one supervised process only; no parallel restart; inspect the manifest/ledger before any recovery action.

### A4. Tail completion invalidates the present scan as a launch input

The old scan selected 112,447 papers before the tail existed. By the audit snapshot, thousands of new v1 artifacts were already present but absent from that scan. New artifacts cannot be grafted into a supposedly frozen scan after the fact.

After acquisition completes:

1. reconcile every manifest target to an invocation-bound source/PDF success or explicit terminal outcome;
2. take a stable database/WAL backup and finish integrity checks;
3. freeze an OAI/version/category/date cutoff, because newly observed versions can invalidate prior `inferred-single-version` assignments;
4. construct one exact analysis-cohort member preimage with artifact ID, content hash, version basis, source channel, and exclusion reason;
5. run a fresh v1 scan over that preimage;
6. implement a principled fallback or explicit missingness stratum for the 1,621 PDF-in-tar cases rather than silently carrying the current skip policy.

Only the resulting scan is eligible for final classification, render, release, or gold sampling.

### Gate A acceptance criteria

- recorded owner choice matches the actual manifest scope and delay;
- one enforced acquisition lease/fleet pacing policy;
- exact invocation-scoped target and terminal-outcome reconciliation;
- stable metadata/category/date/version cutoff;
- exact scan member preimage bound to artifact IDs and hashes;
- every exclusion is reason-coded and represented in release missingness;
- current report/site clearly retired as a pre-tail exploratory snapshot.

## Gate B — finish the v2.7 instrument and rerun the final frame

### B1. The comprehension checker overstates semantic correctness

`pipeline/comprehension.py:29-30,153-162` checks impact, flags, R5 states, and other axes only if the vignette's expected object happens to contain them; categories are not evaluated as a correctness target. This turns omitted expectations into implicit don't-care fields even when the model output is substantively wrong.

The local generated v2.7 stability artifact reports:

- polarity stable: **16/16**;
- scalar impact stable: **16/16**;
- flags stable: **15/16**;
- categories stable: **15/16**;
- R5 state stable: **15/16**;
- every recorded axis stable: **13/16**;
- current `expected_ok`: **15/16**.

The `catalytic_wrong` vignette returns `has_explicit_zero_attempt=true` in one of three repetitions. Under R2, causal-but-unretained assistance is supportive/catalytic, not an explicit-zero attempt. Because the expected object omits the R5 fields, the checker does not mark this as wrong. The dual-role case also misses the intended method flag in two repetitions. Fully specified semantic correctness is therefore **at most 14/16**; incomplete expectations mean the exact score could be lower. The stability output lives under ignored `annotation/` data, so commit or release-bind a safe aggregate result with instrument, vignette, output, and checker hashes before treating it as repository-reproducible evidence.

Make every expected object total: polarity, scalar impact, all diagnostics/flags, both R5 booleans, categories, and any location expectation. Fail closed on missing expected fields. Generate the prose table from the executable results and prohibit decision-log claims that are not derivable from it.

### B2. Both intended humans still need the exact v2.7 exercise

All human annotations currently stored are the one-reviewer v2.0 calibration. No second reviewer has applied v2.7, and no v2.7 adjudication exists. This matters because v2.7 contains a narrower, technical numerator: active invocation plus a delegated traditionally-human intellectual role, with an attempted-use exception and a separate nondelegated-artifact diagnostic.

Before authorizing the post-tail classification:

- both intended graders independently label the complete, frozen v2.7 vignette matrix;
- neither sees Luna's labels before first-pass lock;
- the matrix includes all observed instability cases, dual roles, catalytic-but-unretained output, co-located contributing/zero/undetermined states, reused versus freshly invoked AI artifacts, judging/labeling/summarizing/synthetic-data roles, and vague evidence;
- disagreements are resolved by revising/bumping the instrument or through a blinded third-party decision, not by exposing the machine answer;
- the owner signs the exact manual/prompt/schema/vignette hashes after the exercise.

### B3. The category ontology under-covers the construct

The v2.7 construct expressly includes labeling, judging, summarizing, and synthetic-data generation. The category vocabulary has no direct category for several of these. Synthetic judgement/similarity vignettes were mapped to `unspecified` in the exercise because no faithful category exists, and the model's category assignment for the synthetic-data vignette is unstable. In the audited rendered/accepted author-use snippet scope, **1,012 assignments are `unspecified`**.

Choose before the final run:

- add explicit categories, bump the taxonomy, and rerun the comprehension matrix; or
- prescribe deterministic mappings and declare category-level analysis exploratory.

Do not use a high polarity result to imply that 17-way role categories are equally validated. The final gold sample of 150 positives is not powered to validate all rare categories independently.

Human/machine R5 storage should also be canonicalized. The form exports `r5_states`, while ingest derives booleans transiently and stores the raw states; machine output uses the two booleans. Store one canonical representation and derive the alternate view deterministically.

### B4. Use one precise public construct name

Public/report copy still uses broad phrases such as “AI assistance” and “used generative-AI tools.” V2.7 deliberately excludes some real AI inputs and includes disclosed fruitless attempts. A more faithful primary description is:

> Scanner-visible disclosures of actively invoked generative-AI/LLM systems performing delegated, traditionally human intellectual work in the conduct or communication of a paper, including explicitly disclosed unsuccessful attempts.

Always distinguish:

- contributing delegated use;
- explicit-zero attempts;
- undetermined-impact use;
- nondelegated external AI artifact/instrument use;
- scanner/acquisition non-observation.

The current shorthand can remain as a navigation label only if the exact construct is immediately visible next to every headline/export.

### B5. The present run is not the final run

The v2.7 run provides valuable engineering evidence:

- all unique target inputs exist;
- evidence lineage is exact;
- attempts and spend reconcile;
- render gating functions;
- R5 aggregates are internally reproducible.

It remains unsuitable for freeze because it is partial and bound to the pre-tail scan. The post-tail final run should have:

- a fresh campaign explicitly scoped to the final scan/protocol;
- a clean, fixed code commit and exact provider configuration;
- zero unresolved target items (or a prespecified, bounded failure policy surfaced in every denominator);
- attempt/spend/response reconciliation, including length responses;
- a closed campaign with provider-console evidence and conservative ledger reconciliation;
- a model-identity limitation statement if the provider returns only rolling `gpt-5.6-luna` and no system fingerprint.

Do not silently reuse old labels. If avoiding a second full bill is a priority, design a separate content-addressed reuse protocol that proves exact equality of source artifact, normalized context, hit/evidence membership, taxonomy/manual/prompt/schema, model configuration, and output row; audit it on a stratified sample and bind every reused row to both source and destination releases. Otherwise budget for a clean rerun.

### B6. Residual concurrency and closeout hardening

Admission and item stores are substantially better fenced, but terminal classification status is still updated after the last fenced store by an unfenced `finish_classification_run()` call (`pipeline/classify.py:1239-1257`; `pipeline/runs.py:81-86`). A stale holder could overwrite a successor's terminal state. The schema's generation value is not carried through every business-row transition.

Before another paid run, use a holder+monotone-generation compare-and-set for reservations, attempts, result/error stores, attempt-link finalization, usage output, and terminal run status. Add a real multiprocess pause/takeover/late-response test.

### Gate B acceptance criteria

- total expected-field comprehension checker and corrected result;
- both intended graders complete the frozen v2.7 (or bumped) exercise;
- owner signs the exact final instrument bundle after human review;
- category policy and canonical R5 representation fixed;
- fresh final-frame classification has complete target accounting;
- fresh campaign is purpose/scope/tariff bound, reconciled, and closed;
- final run has no silent label reuse and no unresolved lease/status race;
- every public diagnostic is grounded/render certified or explicitly marked raw.

## Gate C — build a real final-gold study

### C1. The current builder is deliberately calibration-only

`pipeline/annotate.py:298-314,380-385` hard-codes `calibration_only_never_release_validity` and a calibration banner. This is correct for the old pilot and should remain fail-closed. `GOLD_STUDY.md` and `WORKFLOW.md` nevertheless present this command as if it could create final release-bound gold. It cannot.

The production gold builder must accept one immutable release-candidate ID, not arbitrary scan/classification run IDs. It must verify:

- clean, terminal, compatible scan/classification/render protocols;
- exact release membership and sampling frame;
- exact instrument/manual/prompt/schema hashes;
- exact item, scan evidence, classification evidence, source artifact, version basis, PDF, context, and displayed metadata hashes;
- required grounding/render gates and explicit eligibility strata;
- a frozen randomization/assignment manifest and inclusion probabilities.

### C2. Current packet chain of custody can reproduce the prior version-skew failure

The current builder queries mutable `files` rather than the scan-selected artifact (`pipeline/annotate.py:120-138`), reuses `contexts.json` merely if it exists (`:319-336`), and displays mutable current title/comments metadata (`:259-267,625-634`). A later-version comments field can contaminate a v1 judgment even if a linked PDF is nominally versioned.

The manifest lacks per-item artifact/context/PDF/packet hashes. PDFs are optional. The browser persistence key is project/reviewer, not packet digest, so regenerating a project can silently restore stale labels. The allocator manifest, plant identities, contexts, PDFs, and reviewer packets are co-located under default permissions; a comment asking reviewers not to open the manifest is not blinding or access control.

For final gold:

- build owner-only allocation/evidence storage separately;
- create per-reviewer blinded packages containing only assigned items;
- bind local state/export to packet digest;
- include only version-contemporaneous metadata or omit unbound comments/title fields;
- hash every byte displayed or reviewed;
- enforce restricted storage/ACLs and reviewer confidentiality/no-redistribution/retention/deletion terms.

### C3. Ingest must fail closed and preserve first-pass identity

Current JSON ingest warns and proceeds if the manifest is absent, checks global paper membership rather than the reviewer-specific assignment/version, and trusts incoming codebook metadata. The annotation table lacks the release/sample/manifest/packet/assignment/stratum/inclusion-probability/evaluable/COI/adjudication fields and database uniqueness needed for final evidence.

Require a manifest and verify project, round type, reviewer identity, assigned item/version, packet digest, instrument bundle, export digest, and first-pass state transactionally. Reject duplicate or stale imports; never overwrite the first pass. Record explicit non-evaluable reasons, PDF opened/version confirmed, search process/time where required, conflict of interest, and re-assignment.

### C4. The planned overlap is not implemented

Both reviewers currently receive all sample items in independently shuffled orders. If each labels only the first 100–150 positions as the protocol suggests, the expected overlap is about 20–45 of 500, not a guaranteed 100–150.

Materialize one shared randomized overlap, place it at blinded positions in both assignment manifests, and give each reviewer disjoint additional items. Prespecify which strata/axes must be double-coded. Preserve their independent first passes. Two reviewers estimate reliability; a third blinded adjudicator is still needed for disagreements under the project's own anchoring-control protocol.

### C5. Estimators, power, and gates are still prose

There is no executable implementation of:

- stratum-weighted precision and false-omission estimates;
- design-based corrected selected-frame prevalence;
- finite-population or clustered bootstrap intervals;
- non-evaluable/missing-evidence bounds;
- adjudication uncertainty;
- axis-level agreement/kappa with confidence intervals;
- pass/fail release thresholds.

Freeze these before seeing final labels. For POS/FLAG/NEG strata, retain `N_h`, `n_h`, and inclusion probabilities and implement Horvitz–Thompson or equivalent design-weighted totals. State explicitly that final gold validates the scan-complete selected release frame; it does not recover acquisition-missing papers without separate bounds/assumptions.

The planned 150 positives can estimate overall precision near 0.9 to roughly ±5 percentage points, but it cannot validate five impact states, 17 role categories, time/subfield/provider slices, and hard R4/R5 states independently. Under a simple 150-of-2,324 POS sample, the current proportions imply only about **2.6 papers with any explicit-zero state** and **0.5 with scalar-zero maximum**, versus about **28 with an undetermined state**. Oversample zero, external-artifact/instrument, dual-role, and other hard-boundary cases with recorded probabilities; undetermined has more overall support but still lacks fine-slice power. Otherwise preregister those outputs as exploratory.

Plants should be restricted to findable, independently verified truths compatible with the bounded-search protocol. Current plants can come from arbitrary POS/FLAG locations, while the search instructions cover selected standard sections; a body-only plant can be protocol-unfindable. Plant detection is a process check, not a direct estimate of scanner-negative sensitivity.

### Gate C acceptance criteria

- immutable release-bound builder and per-reviewer blinded assignments;
- exact artifact/PDF/context/metadata/instrument/packet hashes;
- digest-bound local state/export and fail-closed transactional ingest;
- explicit shared overlap, COI/evaluability/process fields, named third adjudicator;
- canonical R5/diagnostic human label space;
- executable, tested estimators/intervals/weights/missingness bounds;
- prespecified power limits and release thresholds;
- complete end-to-end synthetic dry run before any final label is seen.

## Gate D — make one immutable scientific release

### D1. Current freeze is a mutable-query digest

There are no release rows. `pipeline/report.py:495-533` stores counts, membership/set hashes, live run pointers, and a report hash; it does not materialize the member rows, labels, evidence, render states, instrument, campaign, or gold results. The releases table has no immutability triggers.

Grounding/render gates remain CLI options, and freeze does not require gold, campaign closure/reconciliation, scan coverage policy, disclosure control, or a render protocol identity. A complete classifier run can therefore be “frozen” without the validity gates implied by the prose.

`render_check.py` can append/redo and overwrite item render status without a render-run protocol ID. Later consumers can observe changed evidence under the same nominal release inputs.

### D2. Report generation is not atomic

Freeze writes the report before inserting the release row. A failed release insert can leave a plausible orphan report. With the default tracked `reports/report.md`, it computes the builder commit after writing, which can stamp the release builder as dirty. There is no clean-tree check for the report/site generator itself.

Build into a fresh staging directory from a validated clean commit and a single stable read transaction/snapshot. Validate every invariant, generate all artifacts, compute hashes, insert/materialize the release atomically, then promote exactly that content-addressed directory. Never write the public path before the release transaction succeeds.

### D3. Site is not a release consumer

`pipeline/build_site.py:623-633` accepts scan/classification run IDs and reads mutable live tables; it has no `--release`. It always emits `unreleased_exploratory`, which is honest today. A public builder must accept only a materialized release ID/artifact and refuse mutable run IDs.

The release should contain at least:

- exact frame and selected member preimages;
- artifact IDs/content hashes/version bases/source channels;
- normalized scan/classification/evidence rows;
- exact render-run rows and gates;
- campaign/model/tariff/config/reconciliation manifest;
- final gold assignments, first-pass/adjudicated labels, design weights, estimators, and thresholds;
- report, site HTML/JSON/download tables, schema/data dictionary, disclosure-control log;
- code/instrument/container/dependency hashes and checksums for every asset.

Sign the manifest/tag if feasible, preserve a private full-evidence archive, and make the public package an explicit allowlisted derivative.

### D4. Current statistical results are exploratory and frame-selected

The current report correctly exposes much of the missingness:

- frame: 133,279;
- scan-complete: 85,742;
- scan non-ok: 1,018;
- fetched but absent from the selected old scan: 46,518;
- fetch failure: 1;
- fully classification-failed frame papers: 6;
- exact-evidence gate exclusions: 322.

The current site falsely summarizes the 47,537 outside-scan papers as papers that “could not be retrieved or scanned.” Most—46,518—were fetched but absent from the selected pre-tail scan. Correct this immediately, because it hides the outcome-related flagged-first selection.

The 2,324/85,742 headline is a **raw exact-evidence-gated classifier-positive proportion in a selected observed v1 cohort**, not validated prevalence. Its coverage-extreme range is conditional on accepting model labels, not a bound on true disclosure prevalence. The last-four-weeks 691/4,306 = 16.0% tile also has only 4,306 of 4,615 frame papers observed; the missing 309 should be visible next to the headline.

Wilson intervals are described as uncertainty in a compatible “true rate.” The observed selected cohort is essentially a finite-frame census, not a probability sample. Either define a superpopulation/cluster-dependence estimand and justify the interval, or present descriptive ratios without binomial sampling bands. Acquisition, version, model, and gold uncertainty dominate.

Do not interpret current explicit-v1 versus inferred-single-version rates, time trends, or subfields as version effects while the acquired multiversion component is outcome-selected and the frame is changing. Recompute all claims only after the final tail/scan and gold.

### Gate D acceptance criteria

- complete final-frame scan/classification/render/gold/campaign gates;
- one stable snapshot and materialized immutable member/evidence rows;
- exact render-run and instrument/campaign identities;
- atomic staged build and signed/checksummed manifest;
- release-only report/site consumers;
- corrected estimand, missingness, failure, and uncertainty language;
- immutable supersession/correction pathway.

## Gate E — publication, privacy, security, and launch

### E1. Current small cells create a plausible reconstruction and cross-reference risk

The site suppresses only selected tools/providers with a threshold below three. Categories, impact, locations, subfields, and daily/weekly/monthly series are serialized raw. The current HTML series contains **509 positive cells of size one or two**, including **344 singletons**. Current JSON also contains singleton/doubleton subfield/category/location cells. Reports serialize raw month-by-version/source tables with singleton/doubleton positives. Overlapping three-month, one-year, and three-year views permit complementary subtraction even when an individual cell is suppressed.

This creates a plausible cross-reference/complementary-reconstruction risk and directly conflicts with the binding aggregate-only/no-per-paper-identification decision. The audit did not attempt to identify a particular paper. `noindex`, `do_not_cite`, and a banner are status controls, not disclosure controls.

Implement one centralized publication layer before any HTML/JSON/Markdown/CSV serialization:

- a documented minimum denominator and positive-numerator threshold;
- primary suppression across every axis and time/subfield view;
- complementary suppression or consistent rounding/noise so totals and overlapping windows cannot reconstruct cells;
- coarser time/category rollups where necessary;
- attack-style tests that attempt differencing across every public table/export;
- the same disclosure decisions in HTML, JSON, downloads, report, and API.

Treat current real-data site/report files as restricted exploratory artifacts until regenerated through this layer.

### E2. Public Git history and current planning copy breach the intended boundary

`.gitignore` now excludes the corpus, DB, backups, annotations, verdicts, `.env`, results, and quarantined reports—a good current-tree guard. Reachable ordinary history still contains deleted per-paper label/excerpt/manual-review files, validation outputs, a spotcheck, infrastructure inventory, and an old distribution archive. Deleting files in a later commit does not remove their blobs from a public clone.

The current tree also remains internally contradictory:

- `PITCH.md` contains identifiable pilot-paper IDs and a near-verbatim disclosure excerpt, while `LICENSE:29-31` says excerpts are not redistributed;
- the pitch promises open annotations in one section and aggregate-only output in another;
- `DESIGN_PLATFORM.md` still proposes public per-paper labels/explorer and ODC-BY annotation data;
- `pipeline/aws/math_ids.txt` is a 1.86 MB per-paper frame list and needs an explicit source-frame/license carve-out or exclusion;
- preliminary reports and prior review files contain fine-grained diagnostic counts that need the same public-artifact review.

There is no remote or tag in this clone, which is an opportunity, not proof that history was never shared. Maintain a private canonical archive, then create an allowlisted public lineage/clean export, rewrite or rebuild history, scan all objects for credentials/PII/excerpts/infrastructure, and verify a fresh clone. Bibliographic paper IDs can remain only under a documented citation/source allowlist; expressive labels and development cases should be synthetic, consented, or private.

### E3. Provider and source-data governance remains undocumented

The supported transport is much safer, but `store:false` does not establish zero data retention. The [official OpenAI data-controls documentation](https://developers.openai.com/api/docs/guides/your-data) says API content is not used for training absent opt-in, while default abuse-monitoring logs may retain prompts/responses for up to 30 days; Modified Abuse Monitoring and Zero Data Retention require approval. Prompt caching can also retain encrypted key/value state under the documented policy.

Before another corpus-scale provider run, record and approve:

- exact organization/project and dedicated spend-limited key;
- training/data-sharing setting, ZDR/MAM status, storage setting, region/transfers, DPA and subprocessors;
- allowed data categories, legal basis, incident path, retention/deletion, and provider-console reconciliation;
- key ownership, rotation/revocation, account hard budget, and least-privilege roles.

Removing the arXiv ID helps but does not anonymize a searchable 2,400-character source excerpt. The scanner examines every text-like archive member before rendered/include-graph validation; residual/unreferenced TeX can therefore be sent to a provider. Prefer rendered/reachable-first evidence and minimum spans, or make this residual-source risk an explicit institutional decision. Normalize/redact names, emails, and unnecessary metadata where possible.

### E4. Local restricted-data controls are not demonstrated

`.env`, databases/WAL/backups, corpus/logs, response records, annotations, contexts, packets, and PDFs appear mode `0777` through the `/mnt/z` DrvFS/9p mount. Those POSIX bits neither prove nor disprove the underlying Windows ACL. Actual inherited ACLs, sharing/sync configuration, encryption/BitLocker, and backup access were not attested.

The local full-run log is tens of megabytes and restricted DB rows retain snippets, raw responses, quotes, and provider metadata without a retention schedule. New harvest parsing drops submitter names, but the legacy DB and archived raw OAI pages/backups retain them.

Before reviewers or a public launch:

- verify and restrict Windows ACLs/share/sync/backup scope;
- move secrets to a project-scoped secret store or protected native filesystem;
- use separate provider keys rather than keeping all vendor keys together;
- define access roles, logging, encryption, retention, deletion, and incident response for corpus/provider/gold artifacts;
- purge/VACUUM legacy submitter data and expire backups if no documented purpose/legal basis exists;
- split owner-only allocator/evidence data from reviewer packages.

### E5. Latent DOM XSS and missing deployment headers

JSON is correctly escaped for embedding in a `<script>` context, but OAI/DB-derived category/date/name values are later inserted into `innerHTML` in dashboard chips, hover tooltips, and tables (`pipeline/templates/dashboard.html:217-224,368-402`). Script-context escaping does not sanitize a later HTML sink. Current arXiv categories are usually controlled-looking, but the generator does not enforce a strict grammar at this boundary.

Construct nodes with `textContent`/DOM APIs and validate categories/dates against a strict allowlist/regex before serialization. Add regression payload tests. Configure deployment headers—CSP, `nosniff`, referrer policy, frame restrictions, permissions policy, and HSTS where supported. Extract or hash inline JS/CSS to make a strict CSP practical.

### E6. Governance, licensing, corrections, and citation remain incomplete

The MIT software scope, non-affiliation, funding/AI-use disclosure, owner decision log, contact, and preliminary warnings are valuable. The aggregate data license is only described as “intended CC BY,” not granted per artifact/release. The repository still lacks:

- an operative release-level data license and source/license matrix;
- `CITATION.cff`, version/tag, checksums, data dictionary/schema, and DOI/archival plan;
- `SECURITY.md` and a vulnerability contact/process;
- privacy/data-governance notice with controller, purpose, processors, retention, rights, and incident route;
- governance/roles/COI and reviewer confidentiality/deletion terms;
- correction, appeal, takedown, retraction, and immutable supersession policy;
- `CONTRIBUTING`, `CODE_OF_CONDUCT`, changelog, and release checklist;
- explicit funder role/non-role in design, analysis, publication, and provider/model selection.

Public docs are also stale: README calls v2.6/current review 7, `TAXONOMY.md` says no full v2.7 run exists, `GOLD_STUDY.md` says v2.6 and contains malformed/stale verdict prose, and site methods say six audit rounds. Generate these facts from release metadata rather than manually counting them.

### E7. CI and deployment do not exercise the launch boundary

Actions are SHA-pinned and no automatic deployment exists. The only workflow claims “tests + site build” but installs dependencies and runs pytest only. Add:

- explicit `permissions: contents: read`, `persist-credentials:false`, timeouts, concurrency/cancel;
- hash-locked complete dependencies and an SBOM/security scan;
- migration-from-empty and test isolation that cannot open the live DB;
- deterministic release/site double-build from a synthetic release fixture;
- release-only refusal tests, disclosure-control/reconstruction tests, XSS payload tests, schema/link checks, history/secret/public-allowlist checks;
- browser accessibility/no-JS/mobile/keyboard tests;
- protected deployment environment with manual approval, exact artifact checksums/attestation, least-privilege token, preview, rollback, and post-deploy header/link checks.

No deployment currently exists, so these are pre-launch controls rather than an exposed deployment credential.

### E8. Accessibility and launch UX need a final pass

There are real positives: static/tracker-free delivery, document language/meta, focus styles, button states, an accessible primary submissions chart, and adjacent tables for some disclosure graphics. Remaining issues include:

- generated bar/line SVGs use `role=img` without a useful accessible name/description;
- important tooltips are pointer-only;
- no `<main>` landmark or skip link;
- no useful `<noscript>` fallback, and dynamic tables are initially empty;
- muted 11–12.5 px text is approximately 3.41:1 against the background, below normal-text AA;
- no canonical/OG/social image/favicon/sitemap/release robots switch or stable methods/privacy/corrections URLs.

Run automated axe/pa11y/Lighthouse checks plus manual keyboard, screen-reader, touch/mobile, high-contrast, reduced-motion, and no-JS tests on the exact release artifact.

### Gate E acceptance criteria

- centralized primary/complementary disclosure control with reconstruction tests;
- public allowlist and clean history/export verified from a fresh clone;
- release-level data license, privacy/security/governance/corrections/citation package;
- verified provider account/data settings and local ACL/retention controls;
- DOM text construction, strict input grammar, and deployed security headers;
- release-only, least-privilege, deterministic CI/deploy with signed checksums;
- accessibility/manual launch pass;
- public copy derived from and linked to the exact release manifest.

## Review-11 issue status

### Resolved or substantially resolved

- v2.7 co-located R5 states are machine-visible and reach paper/report/site outputs;
- `external_ai_artifact` now survives rollup;
- cached-read versus cache-write Luna tariff classes are corrected for the full-run campaign;
- the full-run campaign binds a complete tariff snapshot and internally reconciles settled usage;
- exact unique classifier target coverage and evidence linkage close;
- scope identity/refusal, campaign-required calls, fail-closed usage, atomic reservation/attempt admission, selected-key loading, provider error minimization, and evidence gates are materially stronger;
- current site/report status labels and noindex/do-not-cite posture are honest;
- arXiv support coordination occurred before the live tail resumed.

### Partially resolved

- machine comprehension is executable, but expected objects/checks are incomplete and the result is overstated;
- owner sign-off launched v2.7, but human v2.7 comprehension remains pending;
- full classification ran, but is partial and obsolete as a final-frame run because acquisition continues;
- campaign accounting is exact for settled calls, but closure and conservative reconciliation prose are incomplete;
- refetch selection/ledgering is strong, but the approved command and its narrative scope/rate are inconsistent and there is no fleet lock;
- exact render gating is strong for `author_use`, not for every public diagnostic;
- R5 paper states are correct, but human storage/analysis and gold validation are not canonicalized;
- current-site warnings are strong, but the coverage explanation is factually wrong and disclosure control absent;
- provider transport/credential controls improved, but institutional/account/local-data governance is unverified.

### Unresolved launch blockers

- final acquisition/metadata/cohort freeze and fresh full-frame scan/classification/render;
- complete two-human v2.7 comprehension and final instrument/category decision;
- zero unresolved classification items and a closed final campaign;
- production release-bound gold builder, ingest, assignment, adjudication, estimators, and power gates;
- immutable materialized release and release-only site/report consumer;
- comprehensive small-cell/complementary suppression;
- public-history/current-doc boundary cleanup;
- operative license/privacy/security/governance/corrections/citation package;
- protected, deterministic CI/deploy and accessibility/security-header pass.

## Prioritized launch plan

### Immediate: next operator session

1. Verify only one refetch process exists across all hosts.
2. Record the manifest/ledger checkpoint and confirm whether the approved command meant the original 56,727 targets at four seconds or the narrative meant the original 46,519 in-frame primary-math subset at six seconds; if narrowing, compute a fresh exact remaining manifest rather than treating 46,519 as the live remainder.
3. Do not delete completed artifacts and do not launch a second process.
4. Correct `DECISIONS.md` and the external-methods record so the approved command, executed manifest, intended cohort, and pacing agree.
5. Correct the site sentence that calls fetched-but-not-selected papers unretrieved.
6. Correct the full-run ledger total and either close the active campaign or explicitly reserve it only for a documented old-commit retry.

### While acquisition runs

7. Make the comprehension expected objects total; correct the v2.7 table and decision claim.
8. Have both intended graders complete the frozen v2.7 boundary matrix.
9. Decide category mappings/bump and canonical human/machine R5 storage.
10. Implement acquisition leasing/pacing/atomic-write safeguards before any restart.
11. Implement the final-gold/release materialization path and synthetic end-to-end fixture.
12. Build the centralized disclosure-control/public-artifact allowlist and governance package.

### After acquisition terminal reconciliation

13. Take a stable backup/integrity snapshot and freeze final metadata/version/date/category membership.
14. Run the exact-member v1 scan with explicit channel/version/exclusion strata.
15. Launch a fresh, purpose-bound final classification campaign under the signed instrument; resolve all target items.
16. Run exact render/grounding for every released label slice.
17. Close/reconcile the campaign and materialize the immutable release candidate.
18. Draw and field final gold from that candidate; preserve first passes, adjudicate, run locked estimators, and evaluate preregistered thresholds.
19. If thresholds pass, build a disclosure-controlled public package from the release ID, verify a clean public clone and exact deployment artifact, obtain owner/legal/privacy sign-off, tag/archive, and deploy.

## Bottom line

The project has moved from a prototype with weak lineage to a serious measurement pipeline with a real full-scale model run, exact evidence-gated headline construction, a disciplined owner-decision log, and use of a standard export-service subset route identified by arXiv support. That progress is substantial.

The launch object, however, does not yet exist. The current refetch is changing the scientific frame and its approved command does not match the recorded narrative scope/rate; the current classification is partial and tied to the old selected scan; human v2.7 comprehension and final gold are absent; release rows are not materialized; and public artifacts remain insufficiently disclosure-controlled and governance-incomplete.

Treat the current v2.7 report/site as a private, transient benchmark. Clarify and amend the live acquisition scope/rate record, complete the owner-confirmed tail, rebuild the entire analysis chain from one frozen exact cohort, validate it with two independent first-pass graders plus prespecified blinded third-party adjudication, then publish only a disclosure-controlled, materialized, signed release derivative. That is the shortest path to a launch that can withstand scientific, ethical, operational, and public scrutiny.
