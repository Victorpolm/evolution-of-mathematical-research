# Work ledger (2026-08-10, evening batch) — review findings → status

Sources: reports/codex_review_1-3, review_codex.md, review_codex2.md, human
spot-check, codex re-review of 6db2ddf (17 findings F1-F17, session
019fec70-4f26-79f0-98e3-f481893c3798), review_codex3.md (high-reasoning pass
on c2a6388). Statuses: DONE / PARTIAL / PENDING.

## Done (review-3 actionable-now items, same night)
- P0-3: rollup + coverage queries joined through classification_evidence →
  scan_hits.scan_run — labels from another consumed scan run can never enter
  a denominator (regression test); error items keep evidence lineage
- P0-2: scan run 'complete' requires zero error AND zero incomplete items
  (unknown formats now counted); freeze recomputes the per-status item
  breakdown into the manifest instead of trusting the run label
- P0-4 partial: freeze refuses pending/only-failed classifications and
  duplicate release ids (checked before any file is written); supersession
  applies only when the replacement run is complete
- Validator: flag values must be JSON booleans ("false" ≠ True)
- fetch: gzip detection streams the header (no more 64KiB-prefix
  misclassification); trust_env off (fixed origins); files+artifacts atomic
- importer: prior FAILED files rows (e.g. error:404) no longer shadow newly
  registered bulk sources; report's "registered" reflects what happened
- db.connect refuses schemas AHEAD of the code; migration backups timestamped
- Site: empty/zero-positive cohorts render "no data" instead of crashing;
  CATLBL updated to taxonomy v2; location copy fixed
- Legacy paths hard-disabled (ARXIV_OBS_LEGACY=1 escape hatch);
  OVERNIGHT_PLAN.md marked SUPERSEDED
- requests upgraded past CVE-2024-47081; pytest pinned in lock
- Gold tooling: HTML annotation packets (taxonomy-driven forms, localStorage
  autosave, JSON export) + strictly validated idempotent JSON ingest;
  disjoint sampling strata; reviewer-name path confinement
- PRIOR_ART/TECH_NOTES/PITCH citation corrections (Patterns-and-Purposes v2
  numbers, Gray attribution+estimand, Pangram 4e-4 not 1e-5-on-arXiv,
  GradingBench 35 papers/40 errors, survey self-selection, foundation-model
  wording, 20%-above-trend flagged unreproduced, 27% bytes)

## Deferred from review-3 (tracked; mostly need the v2 run or bigger design)
- P0-1: legacy site/ZIP/dashboard replacement — happens with the first gated
  v2 release (site build already refuses unscoped data)
- P0-5: materialized consumable release snapshots + release-consuming site
- P0-6 remainder: signed manifests, version-pinned negative-audit arm,
  adjudication + design-weighted estimators in code
- P0-7: non-agentic classifier backend / empty-root isolation (current:
  read-only codex + --isolate; enforce at release gate)
- P0-8: results/ quarantine + history sanitation before any public repo
- scan member inventory, fuzzy=needs_review, render-check run manifests,
  fetch version-refresh policy (estimand-dependent), harvest tombstones/
  reparse, AWS producer crash-safety, LICENSE/governance pack

## Done (codex re-review fixes, same evening)
- F1: NULL-version artifacts never coerced to v1 — render_check refuses
  (render_status 'unknown_version'), report has a third 'unknown' stratum
- F2: release contract in run_info — scan run must be consumed by the cls
  run, stage must be 'tex', terminal statuses required; --freeze demands
  complete runs + pinned model
- F3: scan completeness honest — skipped members → 'incomplete:members-
  skipped', unknown formats → 'error:UnknownFormat', single-gz obeys the
  expanded-byte budget; item_status() extracted + tested
- F4: scan hashes the bytes actually read, ledger mismatch = hard error;
  fetch writes files+artifacts in one transaction
- F5: resume compares full protocol (scan-run set, taxonomy) and refuses
  terminal runs; scan-run identity in the snippet input hash
- F6: retries can upgrade durable error rows to ok (never the reverse);
  'complete' requires every stored item valid; exit code reflects it
- F7: validator strictly rejects (unknown keys/enums/flags, bad confidence,
  missing quotes, author_use w/o impact); one schema-retry per batch; raw
  responses logged to corpus/logs/classify/<run>.jsonl
- F8: importer registration gated on zero reconciliation problems (--force
  to override), cross-tar dupes detected, unknown formats blocked,
  NULL-version idempotence via select-guard
- F9: matcher — non-rendering command args killed (\label/\cite/...), \href
  keeps text arg, min quote length, hyphen-insensitive exact pass, all
  anchor occurrences tried, insertion-penalized fuzzy score; fuzzy matches
  feed the cross-check queue
- F10: snippet merge keyed by (paper, version, scan_run) — cross-version/
  cross-protocol hits can no longer share a snippet
- F11 (partial): release manifests carry verifiable membership hashes
  (paper:version sets) + report sha256
- F12: per-stratum (v1/later/unknown) numerators, denominators, rates per
  month; pooled column explicitly labeled mixed-version
- F13: render-check PDF fallback tries all sources; transient failures stay
  retryable pdf_error, only 404-everywhere is terminal no_pdf
- F14: annotate — versions from scan items, tar::member re-extraction,
  merged windows extend excerpts, neutral instructions (no stratum cues),
  strict verdict ingest, optional release gates on POS sampling
- F15: site copy derives from CLI cohort dates, multi-location counting,
  empty-cohort fail-closed
- F16: tests updated to assert the strict behaviors + new regression tests
  (70 passing)
- F17: migrations atomic (transaction inside executescript)

## Deferred from re-review (tracked)
- F4/F11 remainder: content-addressed artifact ids as scan keys; releases as
  consumable materialized snapshots (report/site still read live tables at
  build time; membership hashes make divergence detectable, not impossible)
- F10 remainder: report rollup is paper-level (valid while each scan run has
  one version per paper — corpus_jobs dedupes); version-level rollup when
  multi-version runs exist
- F3 remainder: completeness from an explicit member inventory (currently
  notes-based)
- F7 remainder: full byte-exact response retention (currently per-run JSONL
  of response text)
- F16 remainder: taxonomy doc/code drift test is name-level, not
  definition-text-level

## Done (this batch — v2 pipeline)
- Immutable evidence schema (LB-01/02/05): versioned migrations
  (pipeline/migrate.py, auto-backup), append-only artifacts / scan_runs /
  scan_items / classification_runs / items / evidence FKs / render_checks /
  annotations / releases; artifacts backfilled from files successes
- scan.py + scan_meta.py v2: run manifests (lexicon version, code commit,
  params), per-paper scan_items completion ledger (ok/error/skipped incl.
  member-skip notes), immutable runs with --supersedes, expanded-byte budget,
  pdftotext timeout; fetch.py writes artifacts rows
- TAXONOMY v2.0: uniform rules R1–R3 (no per-case exceptions), ideation /
  conjecture_generation split, computation_verification category, catalytic
  flag; pipeline/taxonomy.py = versioned machine copy driving prompt AND
  validation; drift test vs TAXONOMY.md
- classify.py v2: taxonomy definitions verbatim in prompt, closed-schema
  validation (enums/ranges/bounds), quote grounding vs sent snippet,
  --isolate (one paper per call), --model pinning (codex -m, recorded),
  full-protocol input hash, durable per-snippet failures, nonzero exit,
  --resume with protocol-mismatch guard
- render_check.py (DESIGN_PLATFORM §8): GCS/export version-pinned PDFs,
  normalized exact+fuzzy quote matching (detex, ligatures, hyphenation),
  render_checks audit rows + item render_status; validated end-to-end
- report.py v2: pure function of one scan run + one classification run;
  denominator = scan_items ok; version strata (v1 vs later) per month;
  evidence gates (--require-grounded/--require-rendered) move unverified
  positives out of the headline; md escaping; --freeze release manifests
- Gold study: GOLD_STUDY.md protocol (two-phase stratified sample, double
  blinded annotation, adjudication, two-phase sensitivity estimator);
  pipeline/annotate.py (seeded sampling, ±1500-char highlighted packets,
  ingest, agreement/kappa); annotation/ gitignored
- AWS importer: pipeline/aws/import_s3.py — two-direction ID reconciliation
  (math_ids ↔ tar members ↔ papers), member sha256 ledger, tar sha256,
  dup/error detection, --register into artifacts/files with tar::member
  paths; scan.py reads members in place (validated on math_2308.tar 3818/3818)
- Tests (55, fixture-only) + pyproject.toml + requirements.lock + CI workflow
- Site: complete HTML document (doctype/lang/charset/viewport), run-scoped
  data with provenance line, data-table equivalents for all charts,
  textContent-only tooltip DOM, embedded JSON <-escaped, honest validation
  copy (28/29 external-list, 2 audit flags, development-check wording)
- WORKFLOW.md rewritten as v2 runbook; CROSSCHECK.md tiered AI cross-check
  design (kink-finding only; gold study = validity bar)

## Done (earlier batches)
- Gate 0: banner, honest wording, quarantines, README, report marked unvalidated
- Non-rendered TeX stripping (comment env, iffalse, post-end{document})
- Human verdicts (n=30) ingested; first calibration 28/30 result-bearing precision
- XSS: escape classifier-derived strings in site SVG; <-safe embedded JSON
- Announcement-month corpus definition; boundary harvests; complete ID list
- Filter perf (persistent handles), MD5 verification, tmux ops discipline
- AWS ops-as-code: README + sync_home.sh; instance.txt untracked

## Executed 2026-08-10/11 (overnight + day 2; supersedes the block below)
- v2 rebuild RAN: import_s3 168,027/168,027 clean → scan tex-20260810T205113
  (169,165 items, partial: 820 non-ok) → classify cls-20260810T211610
  (complete, 73,945 items, NOT isolated, dirty commit — exploratory only,
  freeze now refuses both) → render_check (1,122 rendered exact/dehyphen,
  241 rendered_fuzzy after review-4 demotion) → report + site (NO freeze)
- ESTIMAND DECIDED (owner): v1 primary. S3 bulk blobs are RE-ROLLED
  (latest at +12/+23 months — calibrated by member-size matching), so
  fixed-lag is dead; `fetch --v1-refill` + `scan --v1-corpus` implemented
- Gold study: calibration round gold-3yr-prelim LIVE (Johannes annotating);
  documented as instrument pilot, NOT the final release-bound study
- review_codex4.md received → triage below

## Review-4 triage (2026-08-11) — fixed now
- P0-1 (partial): v1 artifacts now scanner-consumable (`scan --v1-corpus`:
  explicit version=1 artifacts + metadata-certain single-version bulk blobs,
  optional --flagged scope); refill failures persisted to
  corpus/logs/v1refill_attempts.jsonl (404 vs error vs never-attempted)
- P0-2: site Wilson copy corrected (±0.08 pp, "from sampling alone");
  report gains full-frame identification bounds (2.1%–3.6%); site
  provenance JSON now exposes scan_status/code commits/isolate=0/version
  strata/data cutoff; methods text names the exact cutoff, not "today"
- P0-3 (partial): `annotate build` gained --from/--until/--category-like
  cohort scoping for the final release-bound sample; ingest validates
  sample membership against the manifest + rejects within-file duplicates;
  agreement with zero pairs exits nonzero; GOLD_STUDY.md reconciles the
  double-coding contradiction and marks gold-3yr-prelim as calibration-only
- P0-4 (partial): freeze now refuses isolate=0 and dirty/unknown code
  stamps; dedup evidence-edge loss fixed (63-edge bug); site tool/model
  strings are snippet-grounded before display (67 paper-level entries
  dropped); full isolation/backend decision = owner call (economics)
- P0-5 (partial): freeze refuses empty consumed-run lists; all freeze gates
  run BEFORE the report file is written (no plausible-report residue)
- P0-6 (partial): fuzzy render matches → rendered_fuzzy (review queue),
  excluded by --require-rendered; existing 241 rows demoted in DB
- Stale deployables: site/dashboard.html moved to pipeline/templates/
  (publish root now generated-only); dist/arxiv-observatory-site.zip
  (old 16.1% site) deleted
- Small bugs: harvest --reparse recursive glob (nested run dirs were
  silently skipped); migrate CLI refuses ahead-schema as "up to date";
  backfill.sh reports failed chunks + exits nonzero; gzip bombs bounded by
  streamed decompression in scan; annotate inline-JS PROJECT/REVIEWER
  escaping; sitetext honesty edits ("small fraction wrong" removed)
- Docs de-drifted: README (audit pointer, provenance claims), WORKFLOW
  (v1 path, rendered_fuzzy gate), aws/README (importer implemented,
  overnight_sync limits), this ledger
- Tests: 73 → 83 (freeze gates, gates-before-write, v1 jobs, gzip budget,
  ingest validation, dedup edges, fuzzy-vs-exact matcher)

## Review-5 triage (2026-08-11 evening) — fixed now
- IMMEDIATE: the documented refill pause was watcher-only, not code —
  restarted the live job 15:26Z under new `--flagged-only` (finite 2,122-
  target hashed manifest, terminal reconciliation, ledger active); the tail
  now requires `--include-unflagged-tail`, refused otherwise (tested)
- P0-4: real budgets — pre-dispatch USD reservation per provider against a
  snapshotted price table (`--max-usd-per-provider`), stop-latch, unpriced
  models refused under a cap, failed calls conservatively counted as
  billed, usage/budget persisted per run (`.usage.json`); tested with
  mocked transport (no HTTP after trip)
- P0-7: regex JSON repair REMOVED (it corrupted \\beta/\\frac/\\text-class
  TeX); strict parse + control-char rejection routes corruption to re-ask;
  provider-NATIVE schemas added: Anthropic forced tool schema, OpenAI
  strict json_schema on the single pinned chat-completions endpoint,
  Google responseSchema — all generated from taxonomy.py (drift-tested);
  live re-smoke: 0 invalid on both providers
- P0-5: freeze bypasses closed — "(unpinned)" as substring, commit must be
  hex (rejects literal 'unknown'), backend must be api:* (DECISIONS)
- P0-6: resume compares backend (no codex<->api mixing); invalid rows are
  retryable again (done = status='ok' only); per-invocation + per-attempt
  ledger (endpoint, request id, stop reason, usage, duration) in
  `.invocations.jsonl`
- P0-8: scan_items.version_basis (migration v4) — explicit-v1 vs
  inferred-single-version are distinct strata in report; hashed v1
  selection manifest; ranking is src-first so outcome-conditioned gcs-pdf
  artifacts can't displace bulk src; DECISIONS amended accordingly
- P0-2/P0-3: limitations card rewritten — coverage extrema explicitly
  conditional on model labels, NOT a prevalence bound; unknown-version
  wording fixed; render-certification bullet (901 exact / 151 fuzzy / 1,747
  unpinned of 2,799); unresolved partition now mirrors report (pending +
  cls-failed included); JSON exports release_status/do_not_cite/
  render_certification/unresolved; noindex meta; banner links #limitations
- P0-9/P0-10 (partial): packets carry a visible CALIBRATION ROUND banner +
  manifest intended_use; markdown ingest legacy-gated (ARXIV_OBS_LEGGACY);
  WORKFLOW/GOLD_STUDY examples show cohort-scoped, gated builds
- 63 missing evidence edges backfilled deterministically (172,437/172,437)
- llm_api hardening: per-thread Session with trust_env=False, no
  redirects, .env key allowlist, capped Retry-After, honest last-error
- overnight_sync.sh hard-disabled (ARXIV_OBS_UNSAFE_SYNC=1 to force);
  pyproject requests floor aligned to 2.34.2 (CVE-2024-47081)
- tests 84 → 94

## Review-11 triage (2026-08-13) — fixed now; RERUN HELD for owner
## sign-off of the final v2.7 bundle + the human vignette pass
- A1 (a false claim of MINE, caught by the review): comprehension flags
  were stable 13/16, not the claimed 16/16 — corrected in DECISIONS and
  the v26 artifact; comprehension is now a TRACKED executable
  (pipeline/comprehension.py) whose summary is computed from the recorded
  repetitions (per-axis stability + expected-field matching incl. R5
  booleans + incremental spend) and can never exceed the data.
- A5 taxonomy v2.7: co-located R5 states become label booleans
  (has_explicit_zero_attempt / has_undetermined_use) in schema, prompt,
  validator (consistency invariants shared with the human path), rollup,
  and the vignette expectations — one merged snippet with a contributing
  AND a fruitless use loses nothing.
- A6: paper_rollup preserves BOTH polarity-independent diagnostics
  (method_component + external_ai_artifact) in every branch,
  order-independently (the v2.6 scoped run had lost the new diagnostic on
  2/2 observed papers); permutation test added.
- A4/A7/A3: attempted-use exception named inside the author_use
  definition; "(or collaborators)" aligned doc<->machine; stale "R4 steps
  1/3" reference fixed; method_component sharpened against the observed
  instrument-case wobble.
- A2: precise estimand text in the classifier prompt (no more bare
  "AI assistance" priming), the site hero, and GOLD_STUDY (TOPIC_ONLY no
  longer described as "not used"); n_external_ai_artifact exported as its
  own slice.
- B2: cached-read rate corrected to the official $0.02/M (was 1.25x
  ceiling — conservative for the cap, wrong for the ledger); refund row
  -$0.029978; ledger total $0.386843 (conservative, UNRECONCILED).
- B1: the campaign tariff snapshot is now the pricing AUTHORITY when
  complete (parsed + bound at attach; reservation and settlement price
  from it); the pilot campaign's incomplete snapshot falls back to the
  code table with a loud warning — full-run campaigns must carry complete
  snapshots.
- B3: close-campaign refuses unresolved reservations and double closure,
  and computes the final amount INSIDE the closing transaction.
- B4: terminal status transition is fenced (final durable holder check
  before finish; a keeper that lost after the last store no longer
  overwrites the successor); lease generation now increments on every
  acquisition (business rows remain fenced by the unique holder token).
- B5: consumed scan runs must exist and be terminal; empty snippet sets
  refuse to create a terminal run (reason-coded setup-failed).
- B6: TAXONOMY.md now says scoped development labels exist (no
  full/population run) instead of implying no labels at all.
- Tests 146 -> 154. Campaign purpose already covers this dev work.

## Review-11 deferred (adds to existing gate lists)
- A8: BOTH graders complete the frozen vignette set BEFORE the full run
  (review insists not-parallel after the scope change; owner to schedule);
  formal sign-off on the final v2.7 bundle.
- B1/B3 remainder: provider-console reconciliation + close of the pilot
  campaign; FRESH full-run campaign (complete snapshot = authority);
  tamper-evidence (signed approval artifact / triggers).
- B4 remainder: generation-stamped business rows; multiprocess
  suspend/takeover fault-injection tests.
- B5 remainder: materialized full classifier-input preimage bound into
  the protocol (target hashes exist; row-level preimage still sidecar).
- B7/B8: provider account/data-governance record, residual-source policy,
  local ACL verification, submitter purge; "full run" language = full
  classification of the SELECTED v1 scan.
- C1-C9 / D1-D6 / E1-E6: unchanged Gate C/D/E lists (final gold builder,
  packet chain of custody incl. contemporaneous metadata, shared
  double-code subset + third adjudicator, estimators; materialized
  releases + release-only site; suppression, DOM-XSS textContent fix,
  history sanitation, governance/licensing pack, CI/deploy/a11y).

## Review-10 triage (2026-08-12 night) — fixed now; RERUN STILL HELD for
## owner sign-off of the exact v2.5 text + adherence data
- A1 construct: taxonomy v2.5 = ACTIVE INVOCATION, named and consistent
  ("incorporated" removed; pre-existing-artifact reuse -> topic_only whose
  definition names the case + new external_ai_artifact diagnostic flag;
  decision-table row corrected; the alternative incorporation construct is
  documented for the owner at sign-off).
- A2 grader parity: VERDICT_DESCRIPTIONS generated verbatim from
  taxonomy.POLARITIES (the "producing this paper" drift is structurally
  impossible now); annotate manifests embed the full instrument hash
  bundle (taxonomy/TAXONOMY.md/prompt/schema).
- A6 R5 consumers: report named-quantities + site headline/export use the
  OVERLAPPING has_contributing_use / has_zero_contribution_attempt /
  has_undetermined_impact states (scalar-max subtraction removed); human
  form gained explicit "also: zero-contribution attempt" / "also:
  undetermined use" checkboxes + external_ai_artifact yes/no/unsure;
  headline renamed "papers disclosing attempted or contributing
  generative-AI/LLM tool use".
- B1 scoped identity: papers-file canonicalized BEFORE protocol creation;
  scope hash+count in the protocol hash, full preimage in params_json +
  sidecar; status complete_scoped; resume with changed/omitted scope
  refuses via protocol hash; report/freeze REFUSE scoped runs;
  cls-20260812T175021 re-statused complete -> complete_scoped (recorded).
- B2 tariff: full usage-class snapshot (input/cached_input/cache_write/
  output; Luna cache classes at 1.25x per the official page 2026-08-12);
  reservations at the WORST input rate; class-aware settlement; ledger
  corrections +$0.0175831 applied for the two under-billed runs (exact +
  conservative); Anthropic classes set to a conservative ceiling pending
  re-verification.
- B3 usage validation: provider-specific fail-closed usage schemas (ints,
  no bools, non-negative, details<=totals); missing/malformed usage
  settles at the FULL reservation as settled-unknown-usage, never $0;
  post-200 handling failures (refusal/length/parse) settle with KNOWN
  usage when the response carried a valid one.
- B4 envelope: request overhead measured from the serialized schema bytes
  (+framing margin) instead of an unexplained constant; settlement asserts
  actual<=reserved and LATCHES on violation while charging the higher
  amount.
- B5 authorization: call_api refuses without an attached campaign
  (test/dev override env-gated); campaign provider/model re-verified
  INSIDE each admission transaction; campaign validated (status/binding/
  cap) BEFORE run-row creation, setup failures reason-coded
  'setup-failed'; create_campaign validates finite cap + full tariff and
  writes append-only campaign_events; amend/close are events (close =
  terminal reconciliation step).
- B6 fencing: lease fence checked INSIDE the admission transaction
  (llm_api.set_fence) and INSIDE every store transaction (_fence_check in
  store_results/store_batch_error, incl. error stores); terminal status
  never overwritten after a lease loss; entire post-acquisition body
  wrapped in try/release; retries re-fence via per-dispatch admission.
- B7 atomic admission: reservation + pre-dispatch attempt row are ONE
  BEGIN IMMEDIATE transaction; the attempt row carries prompt sha, split
  path, ordered snippet hashes, and state (admitted/responded/
  transport-failed) BEFORE HTTP; unique index attempt<->reservation
  (migration v8).
- B8: load_env(provider) scrubs UNRELATED provider keys inherited from the
  parent environment; OpenAI refusal text withheld; Google no-candidates
  reduced to the structured blockReason; rolling-alias limitation stays
  recorded (no system_fingerprint observed on this endpoint).
- Tests 130 -> 146 (tariff reproduction of the live undercount, usage
  validation matrix, unknown-usage settlement, exceed-latch, campaign
  requirement, in-transaction store fencing, scoped-run report refusal,
  construct/tooltip generation, env scrub, refusal withholding, event
  logging). Migration v8 applied (campaign_events, lease generation
  column, attempt state, attempt<->reservation uniqueness).

## Review-10 deferred (adds to Gate A/C/D/E lists)
- A3/A4: dated owner sign-off of the exact v2.5 bundle (construct choice
  active-invocation vs incorporation is THE decision); two-human + Luna
  frozen comprehension/repeatability exercise (vignette set prepared;
  human side needs the second grader).
- B2 remainder: provider-console reconciliation + close-campaign for the
  pilot spend (owner step; CLI ready); archived/hashed tariff page.
- B4 remainder: provider tokenizer/count-endpoint verification of the
  envelope on real requests (assert-on-settle now guards it empirically).
- B6 remainder: monotonic fence GENERATION column is in place but writes
  are keyed by holder token (not yet generation-stamped in business rows);
  multiprocess suspend/kill fault-injection tests.
- C1-C8 / D1-D6 / E1-E7: unchanged Gate C/D/E lists (final gold path,
  materialized releases, site release consumer, suppression incl. 601
  small time cells, history sanitation, PITCH/DESIGN reconciliation +
  math_ids publication decision, provider governance record, submitter
  purge, governance/licensing pack, CI/deploy/a11y).

## Review-9 triage (2026-08-12 evening) — fixed now; RERUN STILL HELD for
## owner sign-off of the exact v2.4 text + adherence data
- A4: machine validator REJECTS semantic contradictions on non-author
  polarities (topic_only+catalytic re-asks, never silently repaired) —
  identical behavior to human ingest; false-valued schema-required flag
  keys no longer count as "cleared content".
- A5: R4 boundary tests got explicit PRECEDENCE ((a) invoked-at-all first;
  (b) target decisive for new output; (c) fixed-component = of the STUDIED
  system, never the authors' toolchain) + frozen-encoder decision table →
  taxonomy v2.4 (text-only; no v2.2/v2.3 production labels exist).
- A6: OpenAI reasoning_effort pinned explicitly to "medium" in the request
  body and protocol (a rolling provider default is not an instrument).
- A2/A3: adherence claims corrected — ad-hoc script had exercised campaign
  spend only (56 spend rows, ZERO api_attempts — review-9 caught it);
  overstatement retracted in adherence_v23.md; `annotate calibration` now
  reports model-evaluable (51/53) and structural-no-snippet (96/96)
  denominators separately; tracked replacement = `classify --papers-file`
  (input scoping recorded in the invocation ledger) as a REAL run.
- B1: attach_ledger fails closed on unknown approval ids; create-campaign/
  amend-campaign/show-campaigns CLI (`python3 -m pipeline.llm_api ...`);
  campaign identity (approval/provider/model/cap/tariff-hash) bound into
  the protocol hash — resume can never switch campaign.
- B2: token estimator replaced by a PROVABLE bound (UTF-8 bytes >= BPE
  tokens; output hard-capped) — the cap can no longer overshoot via
  under-estimated TeX/Unicode tokenization.
- B3: dispatch fenced (every physical call checks lease.lost), bounded
  submission window (2x workers), durable fenced heartbeat before every
  result store, keeper treats 3 consecutive DB failures as lease lost,
  crash releases the lease (no 10-min zombie hold).
- B4: _RequestError carries every prompt/response exchange — parse re-asks
  are their own records (.reaskN), failed split nodes keep prompt hashes
  AND any response hash; per-exchange attempt attribution.
- B5: api_attempts row inserted BEFORE HTTP dispatch and updated in the
  worker thread at response time (crash-visible); transport failures keep
  real HTTP status and true duration; classify adds only linkage after.
- B6: WORKFLOW reconciliation criterion rewritten as relational invariants
  (the old "1:1" cardinality claim was wrong).
- B7: only the selected provider's key is loaded into the process; provider
  error bodies normalized to status+type/code/param (no free text that
  could echo snippets).
- C8: paper_rollup keeps the full impact SET + explicit multi-state fields
  (has_contributing_use / has_zero_contribution_attempt /
  has_undetermined_impact) so R5 slices can never silently pool.
- Tests 122 -> 130 (contradiction rejection, fail-closed campaigns,
  provable estimator, re-ask/failure provenance, pre-dispatch attempt
  rows, error normalization).

## Review-9 deferred (adds to the Gate B/C/D/E lists)
- A1/A2: owner exact-text sign-off; two-human synthetic comprehension set
  (needs second reviewer); repeatability table over polarity/impact/
  categories/flags.
- B2 remainder: campaign-close provider-console reconciliation command;
  archived/hashed tariff page incl. cache/long-context rules.
- B3 remainder: fence generation inside the reservation/store SQL
  transactions themselves; multiprocess fault-injection tests.
- C1-C8 (final gold), D1-D5 (real immutable releases; site --release), E1-E7
  (suppression incl. 601 small time cells, PITCH/math_ids publication
  matrix, history sanitation, provider governance record, submitter purge
  + VACUUM, governance/licensing pack, CI/deploy/a11y) — as itemized in
  review_codex9.md; owner decisions pending where noted there.

## Review-8 triage (2026-08-12) — fixed now (Gate A closed pending owner
## text sign-off; the paid rerun stays HELD until the owner inspects the
## v2.3 text + the 150-case adherence check)
- A1 instrument freeze: DECISIONS records the confirmed scope, the exact
  v2.3 hash bundle (taxonomy.py / TAXONOMY.md / prompt / provider schema),
  and that exact-text sign-off happens at the pre-rerun inspection. Any
  later semantic edit requires a new version (discipline restated in
  taxonomy.py).
- A2 prompt/schema parity: flags example GENERATED from taxonomy.FLAGS
  (was hand-written and omitted method_component), stale impact-"none"
  instruction replaced with not_applicable, schema retry demands the
  object shape (was "array"), local validator now requires every flag key
  exactly like provider strict mode; parity test asserts schema.required
  == validator keys, flag/impact/polarity enums match, and '"none"' cannot
  reappear in the header.
- A3 human/machine parity: ONE shared cross-field invariant function
  (taxonomy.cross_field_problems) used by classify.validate_label AND
  annotate.validate_verdict_item (human path now rejects
  cosmetic/undetermined+catalytic, and catalytic on non-disclosure
  verdicts fails closed); method_component is an explicit yes/no/unsure
  control OUTSIDE the TRUE-only panel, recordable on every verdict and
  preserved by ingest; non-disclosure verdicts store canonical impact
  not_applicable, never ""; paper_rollup OR-merges flags across snippets
  (order-independence tested).
- A4 R4 boundary: three decisive tests (new-vs-pre-existing output,
  target, delegation) added to taxonomy.py prompt rules + TAXONOMY.md,
  resolving the "embeddings production" vs "embeddings analyzed as data"
  overlap. Taxonomy v2.2 -> v2.3 (scope unchanged; no v2.2 labels exist).
- A5 estimand naming: report provenance + site limitations now name the
  measured construct — explicitly disclosed generative-AI/LLM assistance
  under the llm/generic retrieval protocol; prover/CAS/ML-only mentions
  are outside the numerator.
- B1 campaign budgets: migration v7 — budget_campaigns (approval id bound
  to provider+model+cap, price snapshot, status) + api_spend.approval_id;
  attach_ledger binds a campaign, verifies binding strictly, baselines
  ONLY campaign-scoped spend (a fresh approval inherits nothing — the old
  pooling would have burned $21.81 of a $25 campaign on contact); admission
  happens INSIDE the BEGIN IMMEDIATE transaction that inserts the reserved
  row, so concurrent processes admit against one durable sum. Tests cover
  no-inheritance, cross-process rejection, and strict binding.
- B2 lease fencing: RunLease — atomic BEGIN IMMEDIATE check-and-upsert
  acquisition, random holder token, all writes fenced by
  run_id+holder, time-driven keeper thread (120s; stale=600s spans 5
  ticks so long calls are never falsely stolen), stale takeover audited in
  the invocation ledger, lost lease aborts storing/dispatching. Tests:
  concurrent refuse, stale takeover, old-holder heartbeat/delete fencing.
- B3 request provenance: every LOGICAL request (including each bisection
  child and schema retry) is a record with deterministic split path,
  ordered snippet hashes (child id i -> snippet_hashes[i]), prompt/response
  sha256, and its OWN physical attempts — llm_api attempt buffers are
  thread-local, ending cross-future misattribution; api_attempts table
  (migration v7) persists attempts with reservation_row_id, attempt_no,
  request id, usage, duration; JSONL remains the human export. Bisection
  provenance test included.
- B4 provider identity: returned model / system_fingerprint (OpenAI),
  returned model (Anthropic), modelVersion (Google) persisted per attempt;
  inference controls (temperature policy, reasoning-effort unset =
  pilot-matching provider default, store:false) entered into the protocol
  hash.
- C6 quick fixes: annotate calibration treats UNCLEAR/INSUFFICIENT_EVIDENCE
  as a non-evaluable stratum (0 such verdicts in round 1 — numbers
  unchanged); DECISIONS no longer overstates which aggregates are
  executable.
- D1/D3 report wording: freeze manifest names the exact category predicate
  (LIKE 'math%', math-ph included — was "primary math.*"); frame extrema
  renamed coverage-extreme raw-classifier-positive rates, explicitly NOT
  prevalence bounds.
- E1 (partial): TAXONOMY.md illustration cases deidentified to rule
  patterns; remaining tracked identifiers (PITCH.md, DESIGN_PLATFORM.md,
  code comments) deferred to Gate C below.
- E4 (partial): harvester no longer stores submitter names (existing
  column values pending a deliberate purge + VACUUM, noted below).
- B5: analysis-run completion criterion written into WORKFLOW.md (single
  terminal state per snippet, 1:1 items<->attempts<->spend reconciliation,
  provider-console reconciliation + owner acknowledgment before freeze).
- Tests 112 -> 122; migration v7 applied to the live DB (backup taken).

## Review-8 deferred (adds to the Gate B/C lists below)
- Gate B (final-gold path, C1-C5): immutable analysis snapshot / release
  candidate objects; annotate build --snapshot with exact-artifact
  contexts, mutual hashes, packet-hash-keyed localStorage, separated
  allocator/plant manifests; fail-closed ingest with full binding +
  uniqueness + evaluability/COI/search fields; prespecified shared
  double-code subset + third adjudicator; frozen design-based estimators
  (incl. axis metrics + design weights in `annotate calibration`).
- Gate C (public boundary): formal small-cell policy across ALL views
  (current site leaks singleton category/subfield-month cells; suppression
  must extend beyond tools/providers + complementary suppression);
  D2 site numerator split (attempted-or-contributing vs contributing;
  never pool zero/undetermined into "assistance") before ANY v2.3 site;
  freeze materialization + clean-tree check before report write; history
  sanitation via clean export; remaining per-paper identifiers out of
  tracked files; provider/account data-governance record (retention, DPA,
  region) before the FULL run is published; licensing/governance pack
  (CC BY for aggregates, privacy notice, SECURITY.md, CITATION.cff,
  funder-role statement); CI hardening + a11y/security-header pass.
- P1: scan selection membership into DB + run-params binding; scanner
  archive-bomb budgets (tar member counts, outer-size caps, sandboxed
  converter); OAI tombstones + per-version license capture; AWS producer
  remains do-not-reuse until content-addressed shards + reconciliation;
  purge stored submitter values (UPDATE + VACUUM) after owner ack.

## Review-7 triage (2026-08-12) — fixed now
- P0-1 instrument parity: taxonomy v2.2 — R4 operational decision tree
  (instrumentation in-scope, owner confirmation pending), impact split
  zero_contribution/undetermined/not_applicable, method_component flag,
  catalytic>=supportive + zero!=catalytic invariants enforced in machine
  validator AND human form/ingest (R5 was humanly unrecordable); v2.1
  retired unused; TAXONOMY.md sha now in the run protocol hash
- P0-2 calibration made executable: `annotate calibration` command with
  reason-coded exclusions reproduces the corrected denominators (150
  ingested / 149 comparable; 145/149 = 97.3%; 0/96 evaluable NEG; plants
  5/5 as process check only); TAXONOMY history + DECISIONS corrected
- P0-4 rerun mechanics: deterministic batch bisection down to single
  snippets (kills the 171-truncation mode), per-snippet terminal failures,
  prompt/object contract aligned, arXiv ids stripped from provider
  prompts, store:false, mandatory cap + --budget-approval + provider
  allowlist, single-writer run lease (migration v6), durable pre-dispatch
  reservation rows (crash-visible, conservative)
- P0/P1 boundary: results/* + awesome_validation.* + lean4 trees untracked
  (contact/address material); small-cell suppression (<3) on public
  tool/provider cells; +43% tile marked context-only; audit/ownership copy
  fixes; GOLD_STUDY: non-evaluable estimation mapping, no plant deflation,
  v2.2 codebook refs
- Docs: DECISIONS newest-first + v2.2 entry + corrected counts; README,
  WORKFLOW de-drifted. Tests remain 112 (updated for v2.2 semantics)

## Review-7 deferred (Gate B/C machinery — before the FINAL gold/release)
- Two-stage snapshot/release object model; materialized membership +
  member preimages; site --release only (long-standing P0-5 core)
- Release-bound annotate build (--release, artifact-exact contexts,
  packet/codebook/context/PDF hashes, packet-hash localStorage, fail-closed
  ingest incl. assignment/version, annotations uniqueness + design fields)
- Explicit stratified shared double-code subset; third blinded adjudicator
  (owner recruiting); estimator/CI/threshold code frozen pre-labels
- R4/R5 comprehension dry-run set (graders + Luna) before freeze
- Monthly frame partition in report (fetched-not-in-run/errors per month);
  v1_vs_mixed framed as joint sensitivity (done in doc) + paired-version
  study design for a real revision effect
- Provider governance doc (org settings/ZDR status), submitter-field drop,
  ACL verification; history sanitation + publication matrix before remote
- Selection manifests: member rows into DB + scan_runs params linkage;
  run-id uniqueness before sidecar write; per-version licence capture

## Review-6 triage (2026-08-11 night) — fixed now
- Refill CLI truth table CLOSED: --v1-refill requires exactly one authorized
  mode (--flagged-only+--flagged-first XOR --include-unflagged-tail); modes
  mutually exclusive; --flagged-only validates the scan run exists; manifest
  now retains the target-ID PREIMAGE (not just a hash) + run id; attempt
  ledger and terminal reconciliation are run-scoped; four-way refusal test
- Budgets made durable + physical (P0-1): migration v5 api_spend table —
  cumulative provider spend survives restarts/resumes (attach_ledger
  baseline); EVERY physical dispatch (incl. transport retries) gets its own
  reservation; token cap counts in-flight reservations; settle-overrun
  latches; NaN/inf caps rejected; usage.json merges across invocations;
  transport failures leave attempt rows; WORKFLOW shows the cap as default
- Anthropic strict:true (P0-2); validator fully fail-closed: missing
  required keys / bool confidence-or-id / non-finite / overlong (no
  truncation) / null flags all reject; duplicate JSON keys rejected
- ALL C0 controls rejected in decoded strings (P0-3: \nabla/\tau/\ref via
  legal escapes); prompt requires single-line quotes + escaped backslashes
  and the {"labels": ...} wrapper (P1-5 contract parity)
- Resume identity = canonical protocol hash (P0-4): code commit, prompt,
  taxonomy, backend, model, isolate, scan runs, schema hash, batch
  constants — stored in params_json; any drift (incl. dirty tree) refuses
  resume; pre-protocol runs non-resumable by design
- PDF text caches content-bound to the source-PDF hash (P0-6) in scan +
  render_check
- Unknown-format HTTP-200 bodies no longer count as v1 acquisition (P1-2:
  quarantined, retryable, reconciliation-unresolved); differing refetch
  bytes divert to content-suffixed paths — artifact rows always identify
  their bytes (P1-1)
- Site: v1_inferred stratum kept distinct (P1-3 parity with report);
  render certification decomposed by reason (901 exact / 151 fuzzy / 5
  known-version nonmatch / 1 pdf error / 1,741 unknown version); scope
  copy narrowed (generative-AI, not proof-assistant census); subfield tile
  says 30 math.* + math-ph; every report now carries a DO-NOT-CITE status
  line (P0-9)
- Docs: README→review 6; WORKFLOW safe refill + USD cap; DECISIONS
  supersession note on inferred-v1
- Tests 94 → 111 (live re-smoke both providers: 0 invalid under strict)

## Review-6 deferred (adds to the lists below)
- DB-table invocation/attempt ledger w/ request/response hashes (JSONL
  sidecars are the interim); single-run lease against concurrent resumes
- Freeze denominator contract: coverage/missingness thresholds, required
  gates, selection-manifest binding, materialized membership (long-standing
  P0-5 core); site from release_id
- Release-bound gold build (--release), exact-artifact contexts, shared
  overlap assignment, estimators; UNCLEAR/INSUFFICIENT as non-evaluable
  (not negatives) in GOLD_STUDY estimation section
- results/* + awesome_validation.json quarantine (aggregate-only conflict,
  P0-8) — owner call + history sanitation before any public repo
- Provider data-governance doc (retention/ZDR, store:false, DPA) before a
  full API run; submitter-field minimization
- Evidence-backfill as tracked idempotent migration (P1-4); OAI tombstones;
  AWS producer shards/IaC; CI depth/determinism/accessibility; licences

## Review-5 deferred (adds to the review-4 list below)
- Release-bound `annotate build --release`; artifact/context/PDF/packet
  hashes; shared double-code overlap assignment; estimators (P0-9/10 core)
- classification_invocations as DB tables (JSONL ledger is the interim)
- Immutability triggers; materialized release membership; site from
  release_id (long-standing)
- Scanner tar header/count/ratio budgets, path containment, pdftotext
  sandbox; content-bound caches
- OAI tombstones; per-version licence capture; submitter-field
  minimization (owner)
- Limitations placement fully before first number (currently banner link);
  synthetic-demo option (owner)
- CI depth (mocked provider tests exist for budget only; native-schema
  refusal/finish-state, E2E fixture, determinism, accessibility pending)
- Governance package (licence, SECURITY, privacy/retention, CITATION,
  correction policy) before any public repo/launch

## Review-4 deferred (need the v1-pure run, a release builder, or owner call)
- OWNER DECISION: v1-refill tail (~56k papers ≈ 6 days on export.arxiv.org)
  vs flag-scoped-only vs coordinating with arXiv (TECH_NOTES reserves
  export pulls for small batches; flagged phase ≈9k was owner-approved)
- OWNER DECISION: classification backend/isolation for the v1-pure run
  (isolate=1 → one paper per call; freeze now enforces it; bulk-call
  economics say ~30× more calls)
- Materialized release snapshots + release-consuming build_site (P0-5 core;
  already tracked from review-3)
- Acquisition-run/attempt schema (beyond the JSONL ledger); artifact
  manifests as the only scan input; content-addressed fetch storage
- Final gold study: fresh release-bound sample, item/artifact/context/PDF
  hashes in manifest, packet-hash-keyed localStorage (NOT now — mid-round
  state would be lost), COI/search-process fields, design-weighted
  estimators + bootstrap, adjudication flow
- Scanner hardening: tar header/count/ratio budgets, path containment,
  converter sandboxing, PDF-in-tar extraction (2,162 exclusions)
- Provider/agentic regex map: reviewed normalization table + validation
  sample before any public market-share claim
- Determinism (canonical sort keys, SOURCE_DATE_EPOCH, double-build CI),
  accessibility/CSP suite, packaging/licensing/governance docs, history
  sanitation before any public repo (all pre-publication gates, not
  pre-analysis)
- S3 reroll-lag calibration: publish method + data internally (currently
  commit message + code comment)
- Cross-check harness implementation (CROSSCHECK.md; design only)
- Site rebuild from a frozen release once one exists

## Superseded pending list (pre-overnight; kept for history)
- Run the v2 rebuild: import_s3 --register → scan --corpus (new run) →
  classify --model <pinned> --isolate → render_check → report --freeze
- Estimand decision (owner): v1-pinned refetch vs fixed-lag
- Gold study execution (second reviewer needed for double annotation)
- PDF-only members inside bulk tars: extractor pass later

## Partial
- Denominator honesty: DONE for v2 runs; legacy runs remain forensic-only
- Recall: estimator + protocol designed (GOLD_STUDY.md); execution pending
- Aggregate-only: site yes; legacy results/ still tracked (quarantine at
  publication)

## 2026-08-14 site polish (owner request)

- Conditional limitations bullets (zero-complaint paragraphs no longer
  render), concise disclosures card (R5 jargon removed), half-width intro
  and footer text, arXiv-stats link, daily chart omits zero-submission
  days, defensive formulations pruned.
- STRUCTURAL: the submissions dashboard's baked JSON blob + hand-maintained
  tiles were removed from pipeline/templates/dashboard.html; build_site now
  regenerates the daily per-subfield series, the three hero tiles (last
  full month vs year-ago; rolling 4 weeks vs 52-weeks-earlier; 4-week
  disclosure rate), and the harvest date from the DB on every build. The
  hand-baked harvest date was already one day stale (actual 2026-08-10).
- RELEASE TODO (owner, 2026-08-14): run a fresh OAI harvest just before
  release and rebuild the site, so the final days of the submissions
  series are complete — with the regeneration above this is now
  harvest + rebuild, no manual data edits.

## 2026-08-14 review-12 triage

FIXED NOW (commit 2ecbf0c + docs commit): honest comprehension result
(total expected objects, fail-closed; 15/16 corrected to 14/16 — my
overstatement), fenced terminal run status (B6), legacy ingest gate
refuses before any DB connection (audit-boundary finding), response
content hashes recorded for every 200 (length-truncation provenance gap;
durable column awaits migration v9 post-crawl), site coverage falsehood
corrected ("could not be retrieved" -> "fetched but not in the selected
scan"), 4-week tile tooltip now shows the non-scan-covered remainder,
chips innerHTML sink replaced with DOM construction + category/date
grammar asserts at serialization (E5 partial), n_external_ai_artifact
exported as *_raw (not evidence-gated), README/GOLD_STUDY/site-methods
staleness. Acquisition scope/rate record reconciled + owner-confirmed
(DECISIONS); ledger arithmetic corrected ($38.198396).

DEFERRED, with owners:
- site rebuild with the corrected text: BLOCKED by crawl-held DB
  (rollback-journal mode on DrvFS; second-process opens fail) — rebuild
  at next opportunity/post-crawl. Current site remains private/transient.
- campaign closure: post-crawl (same DB constraint).
- migration v9 (api_attempts.response_sha256): post-crawl.
- A3 acquisition-run hardening (lease, pacing validation, atomic writes,
  run-bound reconciliation): BEFORE any future crawl; current crawl runs
  under the one-supervised-process rule (verified single process).
- A4 post-tail sequence, B2 human vignette pass, B3 category decision,
  B5 final run, Gate C gold builder, Gate D release materialization,
  Gate E disclosure/history/governance/CI/accessibility: tracked in the
  review-12 prioritized plan; several need owner decisions (see the
  2026-08-14 walkthrough to owner).

## 2026-08-14 codex v2.8 consistency check (owner-commissioned, pre-model-run)

20 findings; triaged under the owner's paper-level constraint.
FIXED: location definitions emitted + per-snippet-scalar/paper-union
convention documented (F1); UNCLEAR tooltip verbatim from authority (F2);
CATLBL covers v2.7+v2.8 keys (F5); presence-based closed item schema on
human ingest (F6); prompt now carries scoped-denial + paper precedence +
snippet-as-intermediate + R3 pointer + categories-never-determine-impact
(F7/F8/F9/F10/F11); author_use requires >=1 category on BOTH validators,
TRUE_DISCLOSURE also >=1 location (F12/F15); recorded-fields roles
clarified in doc (F13); locations visible/retained for all classifiable
verdicts (F14); packet generator version-derived (F16); ingest rejects
mismatched codebook_version (F17); vignette impacts corrected to exact
values per the rules as written (F18 synthetic_data=supportive, F19
ai_formalization=result_bearing, F20 agent_search_strategy=result_bearing,
llm_judge rewritten+supportive).
DELIBERATELY KEPT: report.py rollup reads v2.7 fields with tolerant
defaults (F3/F4) — v2.7-COMPAT for the existing full run, marked in code,
removed with the Gate-D release consumer. Non-author usage-field CLEARING
(vs rejection) stays: a documented review-6 design decision.
Packets regenerated: comprehension-v28-d4a9fbda20. 158 tests pass.

## 2026-08-14 codex migration review #2 (high-reasoning) triage

FIXED NOW: worked example + unspecified-hedge rule made consistent (a
vague separate use is its own unspecified entry) (item 1); form JS
completeness gating (done = ingest-acceptable), export normalization of
stale hidden usage state, autosave key now includes CODEBOOK (item 2);
MACHINE LOCATIONS ARE NOW A LIST (schema/prompt/validator/checker; my
scalar-per-snippet caveat reverted — the dual-location example is now
representable) (item 4); report + site outputs version-gate the retired
overlapping-R5/diagnostic fields — v2.8 runs publish the scalar paper
impact only (item 5); unclear requires a quote (item 7a); GOLD_STUDY.md
and README migrated to v2.8 language (item 8). Packets regenerated:
comprehension-v28-738ed409ca. 158 tests pass.

DEFERRED, with owners:
- item 3 (paper-version binding on the human path: manifest versions,
  ingest version check, version-contemporaneous metadata) -> Gate-C gold
  builder rebuild (already includes review-12 C2 chain-of-custody).
- item 6 (R3 evidence universe end-to-end: Comments/ancillary channels in
  the classification scope, channel-aware render gating, gate-required
  freeze) -> OWNER DECISION + engineering BEFORE the final v2.8 run;
  proposal in the 2026-08-14 walkthrough.
- item 7b/c/d (grounded-quote as hard gate, tool-name grounding at
  validator, version-aware rollup key) -> documented as gate-time /
  Gate-D consumer semantics; rollup version key noted for the release
  consumer.
- Public display glosses on site tiles: the precise construct is on-page
  in the explainer; tile shorthand kept as navigation label (TAXONOMY.md
  permits); full gloss adoption with the Gate-D release site.

SPEC-DRIFT items flagged by codex, disposition:
- scalar machine location: REVERTED (now a list, faithful to the doc).
- evidence quote + exact model strings marked machine-only in the
  recorded-fields list: KEPT pending explicit owner confirmation (it
  implements the owner's lighter-form direction; the draft's "shared
  label space" framing predated the form simplification).
