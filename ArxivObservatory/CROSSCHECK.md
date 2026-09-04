# Tiered AI cross-check harness — design v1 (2026-08-10)

Purpose: cheap, scalable *kink-finding* on machine labels between releases —
surface misclassifications, taxonomy gaps, and grounding failures early.
Explicit non-goal: validation. Cross-check agents are additional retrieval
systems; the blinded human gold study (GOLD_STUDY.md) remains the only
source of precision/recall estimates. AI cross-check results never enter
published statistics.

## Tier structure

| Tier | Agent | Task | Volume |
|---|---|---|---|
| A | generous subagents (Sonnet-class), console access to the paper's TeX source | re-read each selected paper's evidence; answer a fixed checklist | broad (100s) |
| B | codex second opinions (bulk batches — subscription economics) | independent re-classification of Tier-A disagreements and low-confidence items | medium |
| C | frontier model (Fable) with full paper context | adjudicate items where A and B disagree or either flags "dubious"; write structured dispute notes | small |
| D | human (project owner) | final call; hard cases feed TAXONOMY.md and the gold-study codebook | smallest |

## Tier-A checklist (per paper)

1. Is the polarity right (author_use vs topic_only vs non_use vs FP)?
2. Is the evidence quote verbatim in the rendered text (R3)?
3. Are categories complete and correct per taxonomy v2 definitions?
4. Is the impact label consistent with rules R1/R2?
5. Anything the scanner should have flagged but didn't (nearby text)?
6. Verdict: AGREE | DISAGREE(field=...) | DUBIOUS(reason)

## Item selection (per release)

- all `result_bearing` papers (rare, high-stakes);
- all `catalytic` flags and render-check failures (`non_rendered_evidence`);
- all FUZZY render matches (method='fuzzy' in render_checks — certified but
  not exact; review-required per codex re-review F9);
- low-confidence items (confidence < 0.6);
- a seeded random sample of ordinary author_use and topic_only items;
- machine-vs-machine disagreements from any prior cross-check.

## Storage and hygiene

- Results land in the `annotations` table with `reviewer='ai:<model>'`,
  `blinded=0`, project `crosscheck-<release>`; estimators and gold-study
  queries MUST filter `reviewer NOT LIKE 'ai:%'`.
- Disagreement queue = adjudication worklist ordered C → D; every Tier-D
  resolution becomes a TAXONOMY.md illustration or rule refinement (with a
  version bump when rules change).

## Safety

Same boundary rules as the classifier (LB-06): read-only sandboxes, one
paper per agent call at tiers with console access (prompt-injection
containment), pinned models recorded per row, no network beyond the model
call, outputs schema-validated before storage.

## Status

Design only. Implementation candidates: Tier A/C via Claude Code subagents
in a supervised session; Tier B via `codex exec` bulk batches (reuse
pipeline/classify.py plumbing with a checklist prompt).
