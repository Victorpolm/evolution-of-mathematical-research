> **SUPERSEDED (2026-08-10): historical document.** Step 1's `--run tex-v1`
> reuse is now refused by the immutable-run guard, and the recall wording
> below is invalid (see GOLD_STUDY.md). Follow WORKFLOW.md instead.

# Overnight analysis plan (2026-08-09 → 10), authorized by JS before going afk

Trigger: fetch background task completes (~6.5h from 22:00). Then, in order:

1. **Full-text scan** (local, free):
   `python3 -m pipeline.scan --corpus --run tex-v1 --workers 12`
   (idempotent per run id — deletes+rescans tex-v1; includes tonight's fixes:
   URL-safe comments, content-sniffed members).
2. **Full classification** (codex, checkpointed per 30-snippet batch):
   `python3 -m pipeline.classify --runs meta-v1 tex-v1 --workers 3`
   Expected ~1.4k flagged papers → ~2.5-3k snippets → ~90 batches. Workers
   kept at 3 overnight to stay gentle on rate limits; failures retry once then
   log — rerun the same command in the morning to sweep stragglers (cached
   batches skip).
3. **Awesome-list cross-check** (local):
   `python3 -m pipeline.validate_awesome --readme <scratchpad>/awesome.md --llm-only`
   (re-download README first if scratchpad copy is gone:
   https://raw.githubusercontent.com/seewoo5/awesome-ai-for-math/main/README.md)
4. **Recall audit** (codex): n=200 scan-negatives, single-paper calls
   (deliberate: cross-paper packing risks attribution confusion in the
   validation cornerstone; head+tail truncation already implemented):
   `python3 -m pipeline.audit --run tex-v1 --sample 200 --workers 3`
5. **Report** — BEFORE running, apply queued review-2 fixes to report.py:
   - denominator = papers with completed scan AND classification coverage
     (finding 2); cohort/months from papers.created not ID prefix (finding 5);
     rollup scoped to runs+model (finding 4); location as multi-label set (14).
   - audit estimator: report recall as TP/(TP+FN_hat), FN_hat = miss-rate x
     negative-population size, with CI (finding 10).
   Then `python3 -m pipeline.report`.
6. **Local site generation** (new, replaces artifact-only flow per JS):
   write `pipeline/build_site.py` that renders `site/` from the DB:
   - `site/index.html` = current submissions dashboard (template = existing
     site/dashboard.html pattern: HTML template + embedded JSON export)
   - `site/disclosures.html` = new: prevalence-over-time (weekly, Wilson
     bands, raw-rate labeling), subfield small multiples, tool/model share,
     epistemic impact, validation panel (gold metrics + audit + awesome
     buckets). Aggregates-only per owner decision §7.
   Also republish artifact copy of both pages for convenient morning viewing
   (same URL for dashboard; new artifact for disclosures OK).
7. Commit after each stage; update task list; leave a morning summary with:
   final prevalence table, validation results, codex-usage tally (batch
   counts), and any failures.

Budget note: JS authorized overnight analysis incl. codex ("feel free to get
to the analysis part"); keep total new codex calls ~120-150 (classification
~90, audit 200 single-paper — if that feels heavy at runtime, cut audit to
n=100 and note it). All stages checkpoint; nothing is lost on interruption.
