# Gold study design — v1 (2026-08-10)

Protocol for the human-annotated validation study that gates any public
scientific claim (reviews LB-04/06; TECH_NOTES §validation). The blinded gold
study is the validity bar; AI cross-checks (CROSSCHECK.md) only find kinks.

## Objective

Estimate, with uncertainty, for one frozen release (scan run × classification
run × cohort):

1. **Positive precision** — P(true author disclosure | machine author_use),
   overall and per epistemic-impact class.
2. **False-omission rate** — P(true disclosure | machine negative), expanded
   to the frame with design weights → sensitivity (two-phase estimator).
3. **Label quality** — category/impact/location agreement between machine and
   adjudicated human labels.
4. **Inter-rater reliability** — per-axis agreement and Cohen's kappa with
   CIs (rare-class caveats reported alongside).

## Frame and sampling design

Frame: all scan-complete papers (scan_items status 'ok') in the release
cohort. Two-phase stratified probability sample; every stratum has recorded
size and inclusion probability (in the packet manifest):

| Stratum | Definition | Default n |
|---|---|---|
| POS | machine author_use (post evidence gates) | 150 |
| FLAG | scanner-flagged, not machine author_use | 50 |
| NEG | scan-complete, no scanner flag | 300 |
| HARD (optional) | known_fp / negation_context hits | 50 |

n=150 positives gives a Wilson 95% half-width ≈ ±5% at p≈0.9. NEG n=300
bounds the false-omission rate at ≈1.2% (upper) if zero misses are found;
misses feed the two-phase sensitivity estimator, not a naive recall quote.
Sampling is seeded and reproducible (`pipeline/annotate.py`).

## Annotation protocol

- **Independent reviewers, blinded to machine labels** (packets contain
  contexts and metadata only — no polarity/category/impact, no stratum
  identity). Reviewer-specific item order is independently shuffled.
  Full double-coding of every item is the ideal; the operative minimum is
  the partial double-coding rule below (a shared subset sized for the IRR
  estimate), with the remainder single-coded.
- **Codebook** = TAXONOMY.md at the current instrument version (v2.8 as of 2026-08-14; versioned — the packet records the version and, for the final round, its content hash).
- **Verdicts** (per paper): `TRUE_DISCLOSURE`, `NON_USE_STATEMENT`,
  `TOPIC_ONLY = the AI does not stand in for the authors' own intellectual work: object of study, benchmark, component of the studied system, a non-delegated AI input (pre-existing artifact / machine-only instrument output), or an AI-related mention with no use stated (v2.8 R6)
  `FALSE_POSITIVE` (a highlighted match that is not about AI at all),
  `NO_AI_MENTION` (no AI-related content found anywhere — the normal
  outcome for negative-arm items), `INSUFFICIENT_EVIDENCE` (paper
  unreadable/unavailable), `UNCLEAR` (an explicit statement about AI use that cannot be interpreted — rare by construction, v2.8 R6).
  For estimation, `TRUE_DISCLOSURE` is positive; `NON_USE_STATEMENT`,
  `TOPIC_ONLY`, `FALSE_POSITIVE`, and `NO_AI_MENTION` are non-disclosure;
  `UNCLEAR` and `INSUFFICIENT_EVIDENCE` are NON-EVALUABLE (own stratum,
  reported with sensitivity bounds — see the adjudication section; they are
  never imputed as negatives).
  For `TRUE_DISCLOSURE`, reviewers additionally code categories, impact
  (rules R1–R6), location, tools — same vocabulary as the machine.
- **Context**: ±1500 chars around each hit, matched spans highlighted
  (⟦…⟧), all hits of the paper in one packet section, member/location
  metadata shown. Reviewers may open the arXiv abstract/PDF page (rendered
  text is the evidence standard, rule R3); they must not search for the
  authors' AI usage elsewhere.
- **Conflicts of interest**: reviewers flag papers where they know the
  authors; those items are reassigned.
- **Adjudication**: disagreements resolved by a third pass (senior reviewer
  or joint session); original verdicts are never edited (append-only
  `annotations` table, one row per reviewer plus one `adjudicator` row).
- **Notes discipline**: every borderline note feeds TAXONOMY.md; taxonomy
  changes triggered by gold cases bump the version and invalidate no stored
  labels (they are re-run, not rewritten).

## Search-honesty plants and bounded negative search (added 2026-08-11,
## calibration round, from reviewer feedback)

- **Plants:** a seeded subset of POS/FLAG items is displayed WITHOUT
  excerpts, indistinguishable from negative-arm items (identities in the
  manifest, same set for all reviewers). Reviewers are told plants exist,
  never which. This (a) removes the "no excerpt = safe negative" tell, and
  (b) directly measures **human search sensitivity** — P(reviewer finds a
  findable disclosure without hints) — which is exactly the quantity needed
  to interpret a "nothing found" on true negatives.
- **Bounded search:** no-excerpt items are checked in the standard
  disclosure locations only (acknowledgments, first-page footnotes,
  abstract, Declarations/AI sections; in-PDF keyword search encouraged),
  1-2 min/paper. The negative-arm estimand is accordingly "disclosures
  visible in standard locations under bounded search". Plant detection is a
  PROCESS CHECK, not a transportable sensitivity: plants are
  scanner-detectable cases and likely easier than latent misses, so the
  detection rate is never used to "deflate" estimates (review-7) — it feeds
  a sensitivity analysis only.
- **Truncation is legitimate:** packet order is random, so working top to
  bottom and stopping early yields a valid random subsample of every
  stratum (the estimators use realized per-stratum n). Content-based
  skipping is NOT legitimate.
- **Partial double-coding:** IRR needs a doubly-annotated subset, not the
  full sample. A second reviewer covering the first ~100-150 packet
  positions (~2-3 h) suffices for agreement estimates; the remainder can be
  single-coded.

## Status of the current round (gold-3yr-prelim) — calibration, not final

The running `gold-3yr-prelim` project is an **instrument-calibration round**
(review-4 P0-3 documents why it cannot be the final study): it was sampled
from the whole scan-complete universe rather than the math-primary report
cohort (127/500 items are outside the headline population), most sampled
versions are unknown pending the v1 refill, and the plant protocol was added
after annotation began. Its verdicts are used for reviewer calibration,
taxonomy hard cases, and a preliminary precision signal — never for the
release's validity metrics. The final study draws a fresh sample from exact
release membership (`annotate build --from/--until/--category-like` +
release gates) after the instrument freeze, with a prespecified shared
double-coded subset.

## Disagreement adjudication and anchoring control (added 2026-08-12)

Agreement statistics are always computed from the independent FIRST-PASS
verdicts; adjudication produces the reference labels for validity metrics
and never edits stored verdicts (append-only `adjudicator` rows).

- Reviewers never adjudicate their own disagreements.
- Human–human disagreements: third reviewer or documented joint session.
- Human–machine disagreements: a reviewer who produced neither label
  re-reviews them **mixed with a random control sample of agreed items,
  re-blinded** — re-reviewing only disagreements while seeing the machine
  label anchors the adjudicator toward the machine and inflates measured
  precision. The control items also measure adjudicator flip rate on
  supposedly settled cases.
- `UNCLEAR` / `INSUFFICIENT_EVIDENCE` outcomes are non-evaluable (excluded
  from both numerator and denominator, reported as their own stratum) —
  never imputed as non-disclosure in validity estimates (review-6).

## Locked-set discipline

- The gold sample is drawn AFTER the lexicon/prompt/taxonomy freeze of the
  release under test; instrument changes require a new sample (or a held-out
  split preserved from the start).
- Lexicon/prompt changes and gold labels never land in the same commit (E1).
- Gold verdicts are never quoted in classifier prompts.

## Estimators

- Precision strata: Wilson intervals; per-class (impact) precision reported
  separately — never pool result_bearing with cosmetic.
- Sensitivity: two-phase — expand stratum miss counts by inverse inclusion
  probability to frame totals; combine with validated positive counts;
  bootstrap over both phases for the interval. No naive "1 − miss fraction".
- Corrected prevalence: report raw and misclassification-corrected estimates
  (stratified two-phase correction; note Rogan–Gladen instability rather
  than using it blindly).
- Missingness: fetch-failed / scan-error / pdf-only strata reported as
  explicit bounds, never imputed as negatives.

## Workflow (pipeline/annotate.py)

```
# 1. draw the sample and build blinded packets — a final study scopes the
#    frame to the release cohort and gates (review-5 P0-9)
python3 -m pipeline.annotate build --project gold-v1 \
    --scan-run <id> --classification-run <id> \
    --from <d0> --until <d1> --category-like 'math%' \
    --require-grounded --require-rendered \
    --n-pos 150 --n-flagged 50 --n-neg 300 --seed 42 \
    --reviewers alice bob --out annotation/gold-v1

# 2. reviewers fill the VERDICT/CATEGORIES/IMPACT/NOTES lines in their packet

# 3. ingest each reviewer's packet back
python3 -m pipeline.annotate ingest --project gold-v1 \
    --json <alice_export>.json --reviewer alice
# (markdown --packet ingest is legacy-gated behind ARXIV_OBS_LEGACY=1: it
#  bypasses manifest validation — review-5 P0-10)

# 4. agreement + adjudication worklist
python3 -m pipeline.annotate agreement --project gold-v1
```

`annotation/` is gitignored: packets contain paper excerpts (aggregate-only
public policy, LB-07). The manifest records run ids, codebook version, seed,
strata sizes, and inclusion probabilities.
