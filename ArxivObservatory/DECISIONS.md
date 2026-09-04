# Owner decisions log

Dated record of decisions by the project owner (Johannes Schmitt), so
reviewers can distinguish deliberate choices from drift. Newest first.

## 2026-08-18 (v1 tail crawl complete; deferred post-crawl queue executed)

- **v1 tail crawl COMPLETE, reconciliation clean** (56,727 targets, started
  2026-08-13 ~21:05Z, finished 2026-08-18 ~02:00Z; ~101 h wall incl. polite
  60 s backoffs after 429s): 56,187 v1 full-text ok, 535 pdf-only, 5
  terminal 404 (gone from arXiv). One idempotent retry pass resolved the 37
  transient errors of the first pass; the crawler's own verdict:
  "reconciliation clean: every target has a terminal outcome". PRAGMA
  quick_check ok (3.3 GB DB); ANALYZE run post-ingest.
- **Campaign JS-2026-08-13-v27-full-run CLOSED** at conservative $37.662308
  with the reconciliation note per the 2026-08-14 entry (combined
  conservative 38.198396 vs provider console 37.91, delta 0.76% within the
  1% tolerance, owner ACK).
- **Migration v9 applied** (api_attempts.response_sha256). The live DB had
  received the column ad hoc when the review-12 response-hash wiring landed
  (the v2.7 run recorded hashes), so v9 is a guarded callable migration
  (ALTER only if the column is missing; version stamp always). Pre-v9
  backup: backups/observatory-pre-v9-20260818T020132.db.
- **Site rebuilt** from the pinned v2.7 bundle (texv1-20260811T215148 ×
  cls-20260813T135352, grounded+rendered gates): 2,324 author-use / 85,742
  scanned (2.7% [2.6–2.8]) — unchanged numbers; the rebuild materializes
  the text/code fixes committed while the DB was crawl-locked.
- **Not started (needs fresh owner approval):** v1 scan extension over the
  completed acquisition (+ meta scan), v2.8 classification campaign
  (~$35–40), cohort freeze sequence.

## 2026-08-16 (private GitHub collaboration repo)

- **Owner approved a private GitHub remote** with Victor Jaeck
  (github.com/Victorpolm) as the first outside contributor, to pilot
  community-authored analysis PRs.
- **History sanitized before first push** (git filter-repo, owner-approved):
  stripped `results/` (9 files with per-paper hits/excerpts),
  `reports/spotcheck_result_bearing.md`, `reports/awesome_validation.{json,txt}`,
  `pipeline/aws/instance.txt` (instance id + IP), `.claude/` lean4 tooling
  (no provenance/license), `dist/arxiv-observatory-site.zip`; redacted the
  three cohort-ID linkage phrases in doc history to `[id-redacted]`. The
  frame list `pipeline/aws/math_ids.txt` was deliberately left untouched:
  bare IDs are public metadata, and redacting inside a dense ID enumeration
  would be both corrupting and self-revealing. Pre-rewrite history + commit
  map: `backups/git-pre-github-rewrite-20260816.tar.gz` +
  `backups/commit-map-20260816` (pre-rewrite HEAD 55fecff → 0b0c456);
  linkage mapping in gitignored `results/redacted_id_notes.md`. Commit
  hashes cited in entries above refer to pre-rewrite history — resolve via
  the commit map.
- **Data-access model: format-from-code.** No database in the repo; the
  contributor reconstructs the data format from `pipeline/db.py` + test
  fixtures and develops against fixture DBs; the owner runs accepted code
  on the real DB and returns aggregate outputs. A scrubbed metadata-only
  snapshot (no paper text) is a possible later add-on, owner-provided.
- **Collaboration protocol:** PRs only, owner merges; `CONTRIBUTING.md` and
  `AGENTS.md` added with hard boundaries binding for humans and AI agents
  (no paper content in commits, no credentials, no paid API calls or arXiv
  fetching, `pipeline/`/`TAXONOMY.md` owner-maintained).

## 2026-08-14 (owner rulings on codex migration review #2)

- **Comments-field evidence: INCLUDED in the final classification scope.**
  The final v2.8 run classifies metadata-scan (arXiv Comments) snippets
  alongside the v1 TeX scan (classify already supports multiple --runs).
  **No separate render/validation step for Comments evidence** (owner:
  it definitionally appears on the abstract page). Implemented:
  paper_rollup's --require-rendered gate is channel-aware — metadata
  items (source_kind 'meta:%') are eligible by channel; TAXONOMY.md R3
  paragraph records the rule; regression test added. REMAINING
  engineering for the final-run setup: the report's evidence-eligibility
  filter must accept the meta scan as a second evidence source
  (currently drops labels not linked to the selected tex scan) — on the
  final-run checklist.
- **Recorded-field roles CONFIRMED:** evidence quote and exact model
  strings are machine-only; humans record tools (the lighter-form
  direction). The codex "specification drift" flag is resolved as an
  approved decision.

## 2026-08-14 (TAXONOMY v2.8 ADOPTED — instrument migrated in one commit)

- **Owner declared the v2.8 draft converged** (after 5 revisions, two
  codex draft reviews, the owner's own vignette pass, and real-data
  checks); the final owner rulings incorporated: impact = strongest
  explicitly graded use; R6 explicit-statement rule with no-inference
  clause and "in doubt, do not attest author_use"; unclear rare by
  construction; categories at 12 with proofreading/proof_generation/
  data_generation_labeling; catalytic the only flag; booleans and
  diagnostic flags retired.
- **Migration (this commit):** TAXONOMY.md promoted from the draft
  (owner's own wording edits preserved); pipeline/taxonomy.py v2.8;
  classifier prompt + provider schema drop the retired fields; the human
  form loses the tri-states and "also:" boxes and gains the graded-wins
  impact legend; validate_label/validate_verdict_item REJECT legacy
  v2.7-shaped inputs (labels across taxonomy versions never merge);
  vignette set v2 (22 cases, realistically framed so LOCATION is a
  checked axis, targeted at the v2.8 seams); comprehension checker axes
  = polarity/impact/flags/categories/location, still fail-closed total.
  Tests migrated: 158 passing.
- **Blinded v2.8 packets generated**: annotation/comprehension-v28/
  (project comprehension-v28-c246ccf43e, 22 items, per-reviewer shuffled
  blinded ids, owner-only manifest).
- **Owner instruction (2026-08-14): BEFORE any model runs, codex
  double-checks (a) code ↔ TAXONOMY.md agreement and (b) the human
  survey form.** The machine vignette matrix and any classification wait
  for that check (and for the DB to free after the crawl).
- Instrument-bundle hashes for v2.8 are recorded at the first tracked
  run under this version, as usual.

## 2026-08-14 (owner decisions after the human vignette pass → v2.8 draft)

- **Human comprehension pass (reviewer1) completed and scored** against
  the frozen v2.7 set: polarity **16/16**, impact 15/16 (the one miss is
  the highest-impact convention on the mixed vignette), flags 13/16 —
  the same method_component-on-instrument-cases confusion the machine
  shows. Verdicts archived (restricted):
  annotation/comprehension-v27/verdicts_reviewer1.json. Scoring
  correction on my side: an initial 7/16 polarity figure was my script
  failing to map the human verdict name TRUE_DISCLOSURE to author_use;
  corrected before any conclusion was drawn.
- **Taxonomy v2.8 direction ADOPTED (owner):** (1) the co-located R5
  booleans are removed from taxonomy AND machine fields; (2)
  method_component and external_ai_artifact are removed as recorded
  fields — the boundary rules stay as topic_only text; catalytic stays;
  (3) categories consolidate 17 → ~10, including `proofreading`
  (broadened from proof_checking_criticism per owner: reviewing text for
  errors from typos through math-argument critique, distinct from active
  formulation help in writing_editing) and the owner-proposed
  `data_generation_labeling`. Style bar set by owner: every sentence
  carries a complexity penalty; rules must be legible and uniquely
  applicable in the overwhelming majority; no multi-sentence exceptions
  that merely shift a handful of papers.
- **Draft delivered for careful owner read:**
  `drafts/TAXONOMY_v28_draft.md`. Process after convergence: vignette
  set v2 (wider realistic context so location is testable) → codex +
  classifier models + owner label it in parallel → if it transfers,
  reviewer2 gets it. **Reviewer2 = Tim Gehrunger** (owner, 2026-08-14;
  public materials keep the pseudonym until he agrees otherwise).
- Code/prompt/schema/form migration to v2.8 happens in ONE commit after
  the draft converges — not piecemeal — so instrument hashes bump once.

## 2026-08-14 (owner decisions on the review-12 walkthrough)

- **Uncertainty bands: REMOVED from the headline chart.** The observed
  cohort is a census, not a sample; the bands "create more questions than
  they answer" (owner). The site now states the census framing and names
  classifier error + coverage as the dominant uncertainties. Wilson
  columns stay in the exported data; a gold-study-derived
  classifier-reliability display MAY reintroduce uncertainty later, from
  that direction (owner, 2026-08-14). Ties into the estimand-framing
  decision, still open for the release report.
- **Provider data governance (review-12 E3): acknowledged, NO ACTION.**
  Owner reasoning: requests contain only public arXiv text along an
  eventually-public prompting route; application-side budget controls are
  solid; amounts are tiny. No ZDR request, no account restructuring.
- **Gold-study logistics:** owner will first test their own vignette
  packet for UX, then recruit volunteer colleagues; an engineered
  double-coded overlap block and a deliberately oversampled exploratory
  edge-case fraction are ADOPTED design elements.
- **Human comprehension exercise: packets generated** (blinded, frozen
  v2.7 set): annotation/comprehension-v27/packet_reviewer{1,2}.html,
  project comprehension-v27-8e6c455832; per-reviewer shuffled orders,
  vignette identities blinded to V01..V16 (owner-only unblinding map in
  packets_manifest.json); browser autosave bound to the instrument
  digest. Category-ontology decision (B3) deliberately AFTER the owner's
  first pass.

## 2026-08-14 (review-12 triage: acquisition record reconciled, corrections)

- **Acquisition scope/rate record CORRECTED and owner-confirmed (review-12
  A1).** The live tail crawl executes the exactly-approved command, whose
  actual selection is the full multiversion membership of the corpus id
  list: manifest `v1r-20260813T185505`, **56,727 targets** = 46,519
  in-frame primary-math + 31 primary-math outside the report dates +
  10,177 non-primary cross-lists, at **4.0 s manifest delay** (~6 s
  effective cycle including request time; API ToU limit is 1/3 s). The
  earlier narrative ("~46.5k at 6 s") described the in-frame subset and
  the previous flagged-phase pacing. Owner 2026-08-14: "4-second interval
  fetch is fine for me" — the broader-universe/4 s interpretation is the
  RECORDED intent. Standing distinction: the ACQUISITION UNIVERSE (broad
  corpus cache, legitimate) is not the ANALYSIS COHORT (primary-math,
  dated, prespecified); the release scan manifest will contain only the
  latter. Fact-check addendum added to drafts/arxiv_v1_access_email.md.
- **Comprehension result CORRECTED again, now 14/16 (review-12 B1), my
  error.** The 2026-08-13 "15/16 expected-field" claim overstated
  correctness: expected objects were not total, so omitted fields were
  silent don't-cares. With TOTAL expected objects (polarity, impact or an
  explicit impact_any_of set, complete flags, both R5 booleans;
  fail-closed): **expected_ok 14/16** — dual_role misses method_component
  in 2/3 reps; catalytic_wrong returns a substantively false
  has_explicit_zero_attempt in 1/3 reps. Stability unchanged (pol 16,
  imp 16, flags 15, cats 15, r5 15; all-axes 13). Categories are
  stability-tracked but NOT a correctness target pending the
  category-ontology decision (B3). Tracked artifact:
  reports/comprehension_v27.md (instrument + vignette hashes inside).
- **Ledger arithmetic CORRECTED (review-12 immediate #6):** conservative
  combined spend is pilot $0.536088 + full-run $37.662308 (settled
  $37.644363 PLUS the conservative failed reservation $0.017944) =
  **$38.198396**, not the $38.1805 stated below (which wrongly excluded
  the conservative row from a total labeled conservative). Console
  $37.91; difference 0.76%, within the declared 1% tolerance — the ACK
  stands.
- **Campaign JS-2026-08-13-v27-full-run: closure DEFERRED to crawl
  completion.** No old-commit retry of the 14 non-ok items will be run
  (review-12 concurs it is not worth the effort pre-tail). The DB cannot
  be safely written by a second process while the crawl holds it (see
  operational note), so the reconcile-and-close happens right after the
  crawl's terminal reconciliation.
- **Operational discovery:** on this DrvFS mount SQLite silently ignores
  `PRAGMA journal_mode=WAL` — the database runs in rollback-journal mode.
  While the crawler commits, second-process opens (read-only AND
  read-write) intermittently fail with "unable to open database file"
  (a read-only connection cannot roll back a hot journal). Consequences:
  progress checks during crawls use the log file or an immutable=1
  double-read; no DB writes from other processes until the crawl ends;
  migration v9 (api_attempts.response_sha256 column) is queued for after
  the crawl — until then response-content hashes are preserved in the
  per-exchange provenance JSON.

## 2026-08-14 (provider-console reconciliation ACK — owner)

- Owner reports total key usage since yesterday: **$37.91** (console
  figure; owner notes it is an upper bound in the sense that other
  requests on the key cannot be fully excluded, but it matches closely).
  Ledger-conservative totals: pilot campaign $0.5361 (closed) + full-run
  campaign $37.6444 = **$38.1805**. Ledger ≥ console by $0.27 (~0.7%),
  consistent with conservative settlement rules (unknown-usage settles
  at full reservation; worst-rate envelopes). The WORKFLOW step-5
  reconciliation criterion ("campaign totals reconcile to provider
  console within a declared tolerance, acknowledged by the owner") is
  SATISFIED for both campaigns at tolerance 1%.

## 2026-08-13 (arXiv support REPLY received — coordination question resolved)

- Owner sent the v1-access email (drafts/arxiv_v1_access_email.md); arXiv
  support replied same day. Content is the standard bulk-data guidance
  (near-verbatim info.arxiv.org/help/bulk_data): metadata via arXiv
  API/DataCite/Kaggle; full text via AWS S3, Kaggle (PDF), or "crawling
  our export service … recommended for new content or subset of
  content"; no MOU required; "at present there is no way to request a
  higher rate limit". No bespoke channel for version-pinned historical
  sources exists — the export-service subset crawl IS the sanctioned
  route for the ~46.5k v1 tail (TeX sources), with the Kaggle/GCS
  version-pinned PDF mirror as the bulk-preferred PDF alternative.
- Compliance basis going forward: API ToU pacing (max 1 request / 3 s,
  single connection, fleet-wide) — our crawler runs 6 s serial with
  Retry-After honored, i.e. 2x more conservative. export.arxiv.org
  robots.txt currently reads "User-agent: * / Disallow: /" (no
  Crawl-delay): that targets undirected bots; the help page plus this
  support reply are the explicit sanction for directed harvesting. The
  email thread is the paper trail (keep it).
- **OWNER APPROVED (2026-08-13, same day): resume the tail crawl** once
  the v2.7 classification run AND its render_check are done (no
  concurrent DB writers). Volume ~46.5k papers ≈ 78 h serial at 6 s.
  Invocation (explicitly authorized mode of the review-6 truth table):
  `python3 -m pipeline.fetch --v1-refill --include-unflagged-tail
  --months 2308 … 2608` (37-month window as in the flagged-phase
  manifest). Selection is idempotent (papers with a v1 artifact are
  skipped) and each invocation writes its own target manifest with
  preimage, so machine restarts resume safely. The arXiv-coordination
  precondition of 2026-08-11 is satisfied by the support reply above.

## 2026-08-13 (owner decision: pre-release arXiv outreach is now OK)

- **Supersedes "arXiv contact: after release, reception-gated"
  (2026-08-12 below).** The owner judges the project has matured into a
  clearly serious scientific undertaking with a concrete release roadmap,
  and will reach out to arXiv NOW to ask their policy preferences for
  obtaining the remaining v1 sources (the ~46.5k multi-version tail).
  The updated draft lives at `drafts/arxiv_v1_access_email.md` (numbers
  re-verified against the DB on 2026-08-13; fact-check notes appended).
  Unchanged: the tail is NOT fetched until arXiv answers — the
  `--include-unflagged-tail` guard stays.

## 2026-08-13 (OWNER SIGN-OFF: launch the FULL v2.7 classification run)

- **Owner sign-off (Johannes, 2026-08-13): "please do start the run!"**
  This authorizes the FULL v2.7 classification of the selected v1 scan
  `texv1-20260811T215148` (~74k classifiable snippet groups, ~22.2k
  flagged papers) on openai/gpt-5.6-luna. The signed instrument is the
  v2.7 bundle whose four sha256 hashes are recorded in the review-11
  triage entry below (taxonomy.py `d7ef8c27…`, TAXONOMY.md `c4e4631b…`,
  prompt `5d88ad50…`, provider schema `0e6970b9…`).
- **Deliberate deviation from review-11 A8**: the reviewer recommended
  completing the HUMAN half of the comprehension vignette exercise (both
  graders, frozen set `annotation/comprehension-v27/`) before the
  production run. The owner chose to proceed now, given that a re-run of
  the classification is affordable (~$25–30) if the human pass later
  surfaces an instrument problem. The machine half is on record:
  polarity 16/16, impact 16/16, flags 15/16, R5 15/16 over 3 repetitions.
  The human vignette pass remains OPEN and will be interpreted against
  the same frozen set.
- **Budget**: pilot campaign `JS-2026-08-12-v22-rerun-50USD` closed at
  $0.5361 ledger-conservative (provider-console reconciliation still
  pending owner; corrections already applied per review-10 B2 and
  review-11 B2). Fresh campaign `JS-2026-08-13-v27-full-run` created
  with cap $49.00 (the remainder of the original $50 approval), complete
  class-aware tariff snapshot bound as pricing authority.
- Scope reminders in force: this is a classification run only — NO
  freeze, NO release, NO deployment. Gate C/D/E work (gold builder,
  release materialization, suppression, history sanitation) remains open
  for post-run reviews. No pipeline code edits while the run is live.

## 2026-08-13 (review-11 triage: v2.7, CORRECTION of a false claim)

- **CORRECTION (review-11 A1): the 2026-08-13 v2.6 entry below claimed
  "16/16 polarity/impact/flags stable". That was WRONG for flags** —
  computed per-axis results were polarity 16/16, impact 16/16, flags
  13/16, categories 14/16, all axes 11/16. The three flag-unstable
  vignettes wobble on method_component being ADDED to instrument/dual
  cases (the core expected diagnostic was always present). The summary was
  hand-written from the polarity line; comprehension reporting is now an
  executable checker (`python3 -m pipeline.comprehension`) whose summary
  is computed from the recorded repetitions and can never exceed them.
- **Taxonomy v2.7** (text + machine fields, scope unchanged):
  co-located R5 states become label booleans (`has_explicit_zero_attempt`,
  `has_undetermined_use`) so a single merged snippet disclosing both a
  contributing and a fruitless use loses nothing (review-11 A5; the human
  form's "also:" checkboxes map to the same fields); the R5 attempted-use
  exception is named inside the author_use definition (A4);
  method_component sharpened against instrument cases (A3, the observed
  wobble); "(or collaborators)" aligned across doc and machine copy (A7).
  v2.7 bundle:
  - taxonomy.py sha256: `d7ef8c279117d32443a26c217ab0b09fed38fff0d697641ec54ec8db752bec73`
  - TAXONOMY.md sha256: `c4e4631b0e719ba3e8e1cd02f76fc5ee44be0b21a181f9127d326900fd1bd1d1`
  - prompt sha256: `5d88ad509fb07ae57610409a2f7323a02c332eb8e5c2a69f801abe976cef7697`
  - provider schema sha256: `0e6970b9673be7959342ea611396a4ddc1e01bf136a912f7f59d4fc46b48c713`
- **Estimand named precisely everywhere** (review-11 A2): "scanner-visible
  disclosure of actively invoked generative-AI/LLM systems performing
  delegated, traditionally human intellectual work in the conduct or
  communication of the paper"; the classifier prompt, site hero, and
  GOLD_STUDY no longer use bare "AI assistance"/"not used"; non-delegated
  instrument/artifact use is exported as its own slice
  (n_external_ai_artifact), never hidden in an apparent no-use bucket.
- **Ledger corrections (review-11 B2)**: cached READS were priced at the
  1.25x ceiling instead of the official $0.02/M — refund row -$0.029978;
  tariff table corrected; the campaign tariff snapshot is now the PRICING
  AUTHORITY when complete (attach parses + binds it; the pilot campaign's
  incomplete snapshot falls back to the code table with a loud warning).
  Campaign ledger now $0.386843 — a conservative UNRECONCILED figure; the
  pilot campaign will be reconciled against the provider console and
  CLOSED before the full run, which gets a fresh campaign
  (close-campaign now refuses unresolved reservations and computes its
  final amount inside the closing transaction).
- **Owner decisions recorded**: reviewer names may stay pseudonymous
  (reviewer2 etc.) for now; restructured TAXONOMY.md approved on read
  ("appears great... like the simplification") — formal sign-off happens
  on the final v2.7 bundle after the re-validation below.

## 2026-08-13 (taxonomy v2.6: DELEGATION CRITERION ADOPTED — owner decision)

- **Owner ADOPTED the delegation criterion as the author_use definition**
  (v2.6): author_use requires BOTH that the authors invoked the AI system
  during this research AND that it performed a delegated human-type
  intellectual role (work researchers traditionally do themselves; the
  human-counterfactual test), with the granularity convention "judge the
  ROLE of the output, not the mechanical operation" and "traditionally
  human" pinned to pre-LLM practice. **Explicit owner scope call: running
  a frozen encoder to produce embeddings/feature vectors is NOT
  author_use** — machine-only instrument output joins pre-existing
  artifact reuse under the (broadened) `external_ai_artifact` diagnostic.
  This supersedes the 2026-08-12 "embeddings production in scope" wording;
  LLM labeling/judging/summarizing/synthetic data remain IN (human-type
  work). The v2.3–v2.5 boundary-test stack collapsed into one two-part
  question. v2.6 bundle:
  - taxonomy.py sha256: `2de92f911ae6c818a09d6201f915331d775baf59671c7560db55c7dfe597d63b`
  - TAXONOMY.md sha256: `37d66d313cc63b5aa171c16972c3ff266a62d2b2598cb7c75c22d18246215be5`
  - prompt sha256: `47dd77b8194e14e303f1dd148e1b1c35c6d8e826287157d5493c07c273fe94b8`
  - provider schema sha256: `f1fcd52cbbf90f549b089e9f97a23090a7d5d0a66dd9351ee87446deca500763`
- **Re-validation under v2.6** (dev evidence, in campaign): comprehension
  vignettes now 16 (fresh_embeddings flipped to expected
  topic_only+external_ai_artifact; new similarity_judgments -> author_use
  and perplexity_instrument -> topic_only probe both sides of the
  judge-the-role convention) — Luna 3x: **16/16 polarity/impact/flags
  stable, 16/16 as intended** (annotation/comprehension_v26/). 150-case
  adherence rerun `cls-20260813T110056` (complete_scoped): **147/149 =
  51/53 + 96/96 unchanged**; zero binary flips vs v2.5 (two
  topic_only<->false_positive negative-class wobbles only); the
  Gemini-labeling case stays author_use as delegated human-type work.
  Campaign ledger ~$0.42 of $50.
- Remaining before the confirmatory rerun: owner reads the restructured
  TAXONOMY.md end-to-end and signs the exact v2.6 bundle; human half of
  the comprehension exercise when grader #2 exists (may proceed in
  parallel with the rerun per earlier practice if the owner prefers).

## 2026-08-13 (TAXONOMY.md restructured for sign-off reading)

- **TAXONOMY.md was reorganized** (owner request): short purpose intro →
  rules with criteria and one worked-example table → all history,
  version changelog, calibration record, and open questions moved to a
  final "History and rationale" section. **Rules are UNCHANGED — still
  v2.5**; the version tracks rules, the protocol hash tracks exact text.
  Restructured TAXONOMY.md sha256:
  `d8bb6f3e3160df0931520e9c9a2e97f3a904b7973b7414154da0bf655c020d72`
  (supersedes the sha in the review-10 entry below for any future run).
- **New open question queued for sign-off — the DELEGATION criterion**
  (owner proposal 2026-08-13): author_use ⇔ the authors applied the AI to
  perform an intellectual activity of a kind humans traditionally perform
  themselves (a human counterfactual exists). Agrees with v2.5 on every
  calibration case; diverges on machine-only outputs (embeddings/feature
  production = invocation but not delegated human-type work). Analysis in
  TAXONOMY.md "Open question" + the discussion note to the owner.
  Adoption would be v2.6 + vignette re-run.

## 2026-08-12 (review-10 triage: taxonomy v2.5, hard-cap repairs)

- **Taxonomy v2.5 resolves the R4 construct contradiction (review-10 A1)
  as the ACTIVE-INVOCATION construct**: author_use requires that the
  authors invoked the system during this research ("incorporated" removed
  everywhere); reuse of a pre-existing AI-produced artifact without
  invocation is outside the numerator, lives under a topic_only whose
  definition names that case explicitly, and carries the new diagnostic
  flag `external_ai_artifact` so the state is never silently lost.
  **OWNER DECISION POINT AT SIGN-OFF**: the alternative "incorporation
  construct" (reused AI artifacts count as author_use when serving a
  non-AI target) is documented in TAXONOMY.md; active-invocation was
  implemented because it matches the confirmed "intentionally invoked"
  scope language. Grader tooltips are now GENERATED from
  taxonomy.POLARITIES (the drifted "producing this paper" text is gone),
  and packets embed the instrument hash bundle. v2.5 bundle:
  - taxonomy.py sha256: `3a3e67ede2bba808787f849fc2299e080c005f8b8808f595b4dac9086ad1aaa2`
  - TAXONOMY.md sha256: `033c0f37c6ff31447146b38ee7dc0059a7c28a2e453cbcf6d049b7359b3b2e07`
  - prompt sha256: `be9380ba369aa54e5fd968e2f51d56f93b6970936643f9a33bcbf58cddc9beb6`
  - provider schema sha256: `f1fcd52cbbf90f549b089e9f97a23090a7d5d0a66dd9351ee87446deca500763`
- **The $50 cap was NOT a hard account-cost cap and has been repaired
  (review-10 B2/B3)**: the live adherence run was billed 174,153
  cache-WRITE tokens at 1.25x the base input rate — a 12.45% ledger
  undercount. The tariff snapshot now covers every usage class,
  reservations use the worst applicable rate, settlement is class-aware,
  and missing/malformed usage settles at the FULL reservation
  ('settled-unknown-usage'), never $0. **Ledger corrections applied**:
  +$0.0087077 exact for `cls-20260812T175021` (tariff-correction row) and
  +$0.0088754 conservative for the superseded ad-hoc calls
  (tariff-correction-conservative; per-call cache detail was not
  recorded). Campaign ledger now $0.161116. Provider-console
  reconciliation + campaign closure remain OWNER steps before the full
  run.
- **Scoped runs are a first-class identity (review-10 B1)**: the
  papers-file target is canonicalized before protocol creation; its
  hash+count enter the protocol hash, its full ID preimage the run row;
  terminal status is `complete_scoped`; report/freeze REFUSE scoped runs.
  `cls-20260812T175021` was retroactively re-statused from the misleading
  `complete` to `complete_scoped` (recorded here; the run itself is
  unchanged).
- **No unmetered paid calls (review-10 B5)**: call_api now requires an
  attached campaign (ARXIV_OBS_ALLOW_UNMETERED=1 is a test/dev-only
  override); campaign provider/model binding and the lease fence are
  re-verified INSIDE every admission transaction; campaign
  creation/amendment/closure are append-only campaign_events (the
  pre-review-10 auto-creation of JS-2026-08-12-v22-rerun-50USD is
  backfilled as an event).

## 2026-08-12 (review-9 triage: taxonomy v2.4, enforceable authorization)

- **Taxonomy v2.4 = v2.3 with R4 precedence/tie handling** (review-9 A5:
  test (a) invoked-at-all decided first; (b) target decisive for newly
  produced output; (c) "fixed component" = component of the STUDIED
  system, never the authors' toolchain — includes the frozen-encoder
  decision table). Scope still the owner-confirmed v2.2 scope. **OWNER
  SIGN-OFF OF THE EXACT COMMITTED TEXT REMAINS PENDING** and is the
  authoritative gate before the confirmatory rerun. v2.4 bundle:
  - taxonomy.py sha256: `fb11f49860c855864bb31dcdd692e2295ce8cd4301c62637b90cb017d38ab1bb`
  - TAXONOMY.md sha256: `8aa0486d197910397fe0754a2d19d00bcae65480652b4b5cdd46ff44d2b33782`
  - prompt sha256: `766137f234cc4fb16a4725ea1cada2b684dd6992bb89f9b20ecb6c4e64ed1e8f`
  - provider schema sha256: `559a2c6cd6b18015d1aea7b3c93cbf8cfaba7c420974a8268ab8775008288853`
  - OpenAI inference controls: reasoning_effort **pinned "medium"**
    (documented default, review-9 A6), store:false, temperature
    provider-default on the pinned chat-completions endpoint.
- **Campaign authorization is now enforceable, not documentary** (review-9
  B1): campaigns are pre-created via `python3 -m pipeline.llm_api
  create-campaign` (a deliberate owner-authorized step); classification
  FAILS CLOSED on unknown approval ids; campaign identity (approval,
  provider, model, cap, tariff-snapshot hash) is part of the protocol
  hash, so a resumed run can never switch campaign or cap. The existing
  campaign `JS-2026-08-12-v22-rerun-50USD` had its purpose amended
  (append-only) to name BOTH the adherence checks and the confirmatory
  rerun, matching the owner's recorded $50 approval scope.
- **Adherence-check correction (review-9 A2/A3)**: the 2026-08-12 ad-hoc
  run exercised campaign spend but NOT the lease/attempt provenance path;
  that claim is retracted in the adherence note. Honest denominators:
  51/53 model-evaluable binary agreement + 96/96 structural no-snippet
  concordance (= 147/149 combined). Snippet-level impact showed repeat-call
  instability on the two divergent cases (one crossing the contributing/
  unknown boundary) — recorded as a caveat; polarity was stable. The
  tracked replacement runs through `classify --papers-file` as a real
  classification run with full spend/attempt lineage.

## 2026-08-12 (review-8 triage: taxonomy v2.3, campaign budgets)

- **Taxonomy v2.3 = the owner-confirmed v2.2 SCOPE with sharpened R4
  boundary tests** (new-vs-pre-existing output, target of use, delegation
  — review-8 A4) **and deidentified illustration cases** (review-8 E1).
  The version bumped because rule *text* changed after the scope
  confirmation (version discipline). **OWNER SIGN-OFF OF THE EXACT
  COMMITTED TEXT IS PENDING** — the owner inspects it together with the
  150-case adherence-check results before the confirmatory rerun launches.
  Frozen instrument identity at this commit:
  - taxonomy_version: 2.3
  - taxonomy.py sha256: `1c2784da4bce0ae56e4cbe6f3f2c0ceaed00399cc45236621341856c31f6deb9`
  - TAXONOMY.md sha256: `1395f321087ff3f1648176df290fbb783fa8e2c781b516905be69a616901895d`
  - prompt sha256: `97513ae0bd15d8baf7e4fd78cc9daeee45ff319addb1456fe0f12f172075b715`
  - provider schema sha256: `559a2c6cd6b18015d1aea7b3c93cbf8cfaba7c420974a8268ab8775008288853`
- **Budget campaigns are durable objects** (review-8 B1): the approval id
  `JS-2026-08-12-v22-rerun-50USD` now names a `budget_campaigns` row
  (provider+model+cap bound; spend rows scoped to it; cross-process atomic
  admission). It approves the $50 OpenAI/Luna confirmatory-rerun spend
  regardless of the v2.2→v2.3 text-version bump — the approved scope is
  unchanged. The ~$21.8 of earlier pilot spend is OUTSIDE this campaign.
- **Calibration aggregates wording corrected** (review-8 C6): the
  executable `annotate calibration` command produces the BINARY headline
  counts; the per-axis concordance numbers (impact/category/location) in
  TAXONOMY.md's calibration history remain manually derived development
  metrics until the Gate-B analysis command lands. UNCLEAR /
  INSUFFICIENT_EVIDENCE now form a non-evaluable stratum in the command
  (no verdicts of either kind exist in round 1, so no number changed).

## 2026-08-12 (v2.2 confirmations + rerun approval)

- **Taxonomy v2.2 scope CONFIRMED by owner**: R4 instrumentation-in-scope
  and the R5 impact split as implemented. Instrument freeze may proceed.
- **v2.2 rerun spend APPROVED: $50 (OpenAI/Luna), approval id
  JS-2026-08-12-v22-rerun-50USD** (recorded via --budget-approval).
- **Human-interface tooltips**: every verdict option carries a plain-language
  hover description (implemented same day).
- **Pre-run adherence check approved in principle**: rerun the v2.2
  instrument over the 150 calibration papers as an IN-SAMPLE development
  check (these cases informed v2.2 — results verify the fixes landed,
  never claim accuracy).

## 2026-08-12 (taxonomy v2.2 + review-7 triage)

- **Taxonomy v2.2 implemented, PENDING OWNER CONFIRMATION on two scope
  points**: (a) R4 decision tree treats active AI *instrumentation* (LLM
  labeling/judging, synthetic data, embeddings production, pipeline code
  generation) as IN-scope author_use; (b) R5 impact split into
  zero_contribution / undetermined / not_applicable with cross-field
  invariants (catalytic ⇒ ≥ supportive). v2.1 never produced labels and is
  superseded; no v2.0 labels are ever merged with v2.2.
- **API analysis spend**: cap + `--budget-approval` id are mandatory;
  provider allowlist = OpenAI + Anthropic. Cap scope: **per provider per
  campaign** (the $50 pilots); a full-run cap needs its own approval id.
- **Aggregate-only boundary enforced in the tracked tree**: results/*,
  awesome_validation.*, and unrelated lean4 tooling untracked (history
  sanitation remains a pre-public step).

## 2026-08-12 (quick decisions)

- **math-ph: INCLUDED.** The frame is "papers whose primary listing is
  math" (`primary_category LIKE 'math%'`, i.e. 30 math.* + math-ph), kept
  simple deliberately; the numbers barely shift (math-ph 1.35% vs math.*
  2.16%, pooled effect ~0.03pp). Encoded as the release category predicate.
- **arXiv contact: after release, reception-gated.** Do not contact arXiv
  pre-launch. If the released project draws no interest, the ~46.5k v1 tail
  is not worth further effort; if well-received, that reception is the
  argument for arXiv provisions/server resources. Until then the release
  documents the flag-scoped v1 limitation visibly. The drafted email is
  kept for that moment.
- **Calibration round closed: 150 labels ingested, 149 comparable**
  (one reason-coded packet version-skew exclusion; truncation valid by
  design). Aggregates come from the executable `annotate calibration`
  command, never hand-maintained numbers (review-7). NEG arm's one
  candidate "miss" was reclassified as a packet version-skew artifact
  (human reviewed latest PDF v3; scanner saw the earlier bulk blob) — the
  final gold study MUST pin packet PDFs to the scanned artifact version.

## 2026-08-11 (response to review_codex4.md)

- **v1-refill acquisition**: pause the export.arxiv.org crawl after the
  scanner-flagged phase (~9,100 papers, previously approved); do NOT fetch
  the ~56k-paper tail until coordinated with arXiv (email drafted; asks:
  acceptable rate/window, sanctioned bulk route for historical versions,
  whether the gs://arxiv-dataset version-pinned PDF mirror is a blessed
  alternative). ENFORCEMENT (2026-08-11 15:26 UTC, after review-5 flagged
  the gap): the running job was restarted under `fetch --v1-refill
  --flagged-only` with a hashed 2,122-target manifest
  (corpus/logs/v1refill_manifest_20260811T152608.json) and terminal
  reconciliation; it stops by construction. The tail requires the separate
  `--include-unflagged-tail` flag, which errors without it.
- **Inferred-v1 stratum** (amends the earlier "never coerced to v1"
  wording): bulk blobs of papers whose metadata shows exactly ONE version
  may be treated as v1, but ONLY as the distinct, labeled stratum
  `v1_inferred` (scan_items.version_basis = 'inferred-single-version'),
  reported separately from fetched v1 and never silently merged with it.
- **Publication stance**: this is a timely project doing substantial due
  diligence; a deliverable may go out for public inspection BEFORE
  second-order corrections (v1 purity, human error correction) land,
  provided limitations are stated clearly and prominently. Implemented as
  the site's "Known limitations" card + do-not-cite banner; aggregate-only
  policy unchanged.
- **Classification isolation**: accepted — analysis classification moves to
  a direct non-agentic API backend with one paper per request
  (`classify --backend api`), which satisfies the freeze contract's
  isolation gate structurally. The extra call volume is acceptable.
- **API exploration budget**: up to **$50 per provider** (OpenAI +
  Anthropic) for pilots. Candidate models: `gpt-5.6-luna` and
  `claude-haiku-4-5-20251001`, cross-checked against the codex
  (`gpt-5.6-sol`) labels and human gold verdicts before committing to a
  full-run backend; then produce a measured cost estimate. API keys live in
  the gitignored repo-root `.env`. ENFORCEMENT: `classify --backend api
  --max-usd-per-provider 50` — pre-dispatch USD reservation against the
  snapshotted price table in pipeline/llm_api.py (models without a price
  snapshot are refused under a USD cap); usage/budget persisted per run.

## 2026-08-10/11 (overnight + gold study)

- **Estimand**: v1 (first submitted version) is the primary estimand; S3
  bulk blobs are re-rolled "latest" and are reported as their own stratum.
  *(The original "never coerced to v1" wording is SUPERSEDED by the
  2026-08-11 inferred-v1 amendment above: single-version papers' blobs may
  enter the distinct `v1_inferred` stratum, never the fetched-v1 stratum.)*
- **Gold study framing**: the running `gold-3yr-prelim` project is a
  calibration/pilot round, not the final validation study; the final sample
  will be drawn from exact release membership after instrument freeze.
  Plants (excerpt-less positives), bounded negative search, and
  truncation-at-any-point were adopted from reviewer feedback 2026-08-11.
- **Flag-scoped preliminary data**: fetch flagged papers' v1 first so a
  privately shareable preliminary version exists early.

## 2026-08-09/10 (project setup)

- **TAXONOMY v2.0 approved** for the full planned run (rules R1–R3,
  catalytic flag, computation_verification).
- **Aggregate-only public outputs**: no per-paper listings or excerpts in
  anything public; per-paper data stays in gitignored restricted locations.
- **Site**: locally generated static site is the deliverable (future GitHub
  Pages); unvalidated banner stays until a gated release exists.
- **Corpus**: arXiv full texts are never committed or redistributed.

## Open decisions

- Second gold reviewer name + third blinded adjudicator name (owner
  2026-08-12: "we can find a third adjudicator").
- Publication estimand framing for the partial v1 frame (owner leaning:
  partial-identification / selected-frame presentation, per review-7 P0-6).
