"""Results report: prevalence tables with Wilson intervals, tool/model
frequencies, category and impact distributions.

v2 discipline (LB-01/05): the report is a pure function of
  - one scan run (denominator = its scan_items with status 'ok'), and
  - one classification run (numerator labels; single model/prompt/taxonomy).
Nothing is read from unscoped history. Papers with a scanner flag but no
classification item are "pending", never negatives. Fetch-failure and
version strata are reported per month. Evidence gates (--require-grounded /
--require-rendered) move unverified author_use papers into a separate
"unverified evidence" bucket instead of the headline numerator.

Usage:
    python3 -m pipeline.report --scan-run tex-20260810T154813 \
        --classification-run cls-20260810T160000 \
        --from 2026-07-01 --until 2026-08-08 [--require-grounded] \
        [--require-rendered] [--freeze rel-2026-08-pilot]
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

from . import db, runs

# NOTE (v2.8 migration): paper_rollup below still READS v2.7 label fields
# (has_explicit_zero_attempt/has_undetermined_use, method_component,
# external_ai_artifact) with tolerant .get() defaults. This is deliberate
# v2.7-COMPAT so the existing full run cls-20260813T135352 can still be
# reported/rebuilt; v2.8 labels simply never set them. The release-bound
# consumer (Gate D) replaces this path outright.
POLARITY_RANK = {"author_use": 5, "non_use_statement": 4, "unclear": 3,
                 "topic_only": 2, "false_positive": 1}
IMPACT_RANK = {"result_bearing": 6, "supportive": 5, "cosmetic": 4,
               "undetermined": 3, "zero_contribution": 2,
               "none": 1, "not_applicable": 0}  # 'none' = legacy v2.0/2.1


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def md_escape(value) -> str:
    """Escape classifier-derived strings for markdown table cells (LB-08)."""
    s = str(value)
    s = s.replace("\\", "\\\\").replace("|", "\\|").replace("`", "\\`")
    s = s.replace("<", "&lt;").replace("\n", " ")
    return s


def run_info(con, scan_run: str, cls_run: str, freeze: bool = False
             ) -> tuple[dict, dict]:
    """Release contract (codex re-review F2): the two runs must belong
    together and be in a reportable state before any number is produced."""
    s = con.execute("SELECT * FROM scan_runs WHERE run_id=?", (scan_run,)).fetchone()
    if s is None:
        sys.exit(f"scan run '{scan_run}' not found — report v2 requires an "
                 "immutable run with scan_items (rerun pipeline.scan)")
    c = con.execute("SELECT * FROM classification_runs WHERE run_id=?",
                    (cls_run,)).fetchone()
    if c is None:
        sys.exit(f"classification run '{cls_run}' not found")
    n_items = con.execute("SELECT COUNT(*) FROM scan_items WHERE run_id=?",
                          (scan_run,)).fetchone()[0]
    if n_items == 0:
        sys.exit(f"scan run '{scan_run}' has no scan_items — cannot prove "
                 "coverage; use a run made by the v2 scanner")
    if s["stage"] != "tex":
        sys.exit(f"scan run '{scan_run}' has stage '{s['stage']}' — full-text "
                 "prevalence needs a 'tex' run (metadata scans are not coverage)")
    consumed = json.loads(c["scan_runs_json"] or "[]")
    if consumed and scan_run not in consumed:
        sys.exit(f"classification run '{cls_run}' consumed scan runs {consumed}, "
                 f"not '{scan_run}' — these runs do not belong together")
    # review-10 B1: scoped runs (papers-file subsets) are adherence/dev
    # artifacts — they must NEVER feed population reports or releases
    c_params = json.loads(c["params_json"] or "{}") if "params_json" in c.keys() else {}
    if c["status"] == "complete_scoped" or c_params.get("scope"):
        sys.exit(f"classification run '{cls_run}' is SCOPED "
                 f"(status={c['status']!r}, scope="
                 f"{c_params.get('scope', {}).get('mode')!r}) — scoped runs "
                 "classify a target subset and cannot support population "
                 "outputs; use a full run")
    for label, row in (("scan", s), ("classification", c)):
        if row["status"] not in ("complete", "partial"):
            sys.exit(f"{label} run has non-terminal status '{row['status']}' — "
                     "wait for it to finish (or investigate)")
    if freeze:
        # scan may be 'partial' (item-level failures are a reported, excluded
        # stratum with a recomputed breakdown in the manifest — review-3 P0-2);
        # the classification run must be fully valid
        if c["status"] != "complete":
            sys.exit(f"cannot freeze a release: classification run status is "
                     f"'{c['status']}', not 'complete'")
        if "(unpinned)" in (c["model"] or ""):
            # substring, not suffix: 'codex-default(unpinned)@medium' must
            # not pass as pinned (review-5 P0-5)
            sys.exit("cannot freeze a release from an unpinned-model "
                     "classification run")
        # review-4 P0-5: an empty consumed-run list is unprovable provenance,
        # not universal compatibility
        if not consumed:
            sys.exit("cannot freeze: classification run does not record which "
                     "scan runs it consumed (scan_runs_json empty)")
        for label, row in (("scan", s), ("classification", c)):
            commit = row["code_commit"] or ""
            if not re.fullmatch(r"[0-9a-f]{7,40}", commit):
                # rejects '', '-dirty' suffixes AND the literal 'unknown'
                # that db.code_commit() returns on git failure (review-5)
                sys.exit(f"cannot freeze: {label} run was produced by "
                         f"dirty/unknown code ({commit!r}) — the source tree "
                         "is not recoverable from git")
        if not (c["backend"] or "").startswith("api:"):
            sys.exit(f"cannot freeze: classification backend is "
                     f"{c['backend']!r} — analysis runs use the direct "
                     "non-agentic API backend (DECISIONS.md 2026-08-11)")
        if not c["isolate"]:
            sys.exit("cannot freeze: classification run was not isolated "
                     "(isolate=0) — batched papers share one agent prompt, so "
                     "cross-paper contamination cannot be ruled out "
                     "(review-4 P0-4)")
    return dict(s), dict(c)


def eligible_item_ids(con, cls_run: str, scan_run: str) -> set[int] | None:
    """Item ids whose evidence hits belong to the selected scan run (P0-3).
    None means ALL items are eligible — the fast path when the classification
    run consumed exactly this one scan run (the correlated-EXISTS variant of
    this scoping made SQLite rescan the run's hit index per item: minutes,
    not seconds)."""
    row = con.execute("SELECT scan_runs_json FROM classification_runs "
                      "WHERE run_id=?", (cls_run,)).fetchone()
    consumed = json.loads(row["scan_runs_json"] or "[]") if row else []
    if consumed == [scan_run]:
        return None
    return {r[0] for r in con.execute(
        "SELECT DISTINCT ce.classification_item_id FROM classification_evidence ce "
        "JOIN scan_hits h ON h.id = ce.scan_hit_id WHERE h.scan_run=?",
        (scan_run,))}


def paper_rollup(con, cls_run: str, scan_run: str, require_grounded: bool,
                 require_rendered: bool) -> tuple[dict[str, dict], set[str]]:
    """Best valid snippet classification per paper from ONE classification
    run, restricted to items whose evidence hits belong to the SELECTED scan
    run (codex review-3 P0-3: a classification run that consumed several scan
    runs must never contribute labels sourced from a different denominator).

    Returns (rollup, ungated_authors): papers whose only author_use evidence
    fails the gates land in ungated_authors and their rollup entry falls back
    to the best NON-author_use polarity (or is flagged unverified)."""
    eligible = eligible_item_ids(con, cls_run, scan_run)
    rows = (r for r in con.execute(
        "SELECT ci.id, ci.arxiv_id, ci.label_json, ci.quote_grounded, "
        "ci.render_status, ci.source_kind FROM classification_items ci "
        "WHERE ci.run_id=? AND ci.status='ok'", (cls_run,))
        if eligible is None or r["id"] in eligible)
    papers: dict[str, dict] = {}
    ungated: set[str] = set()
    for r in rows:
        lab = json.loads(r["label_json"])
        if lab.get("polarity") == "author_use":
            # channel-aware render eligibility (owner decision 2026-08-14,
            # v2.8 R3): metadata-channel evidence (the arXiv Comments field)
            # always appears on the abstract page — the PDF render check
            # does not apply to it
            meta_channel = (r["source_kind"] or "").startswith("meta:")
            gate_ok = ((not require_grounded or r["quote_grounded"] == 1)
                       and (not require_rendered
                            or r["render_status"] == "rendered"
                            or meta_channel))
            if not gate_ok:
                ungated.add(r["arxiv_id"])
                continue
        cur = papers.get(r["arxiv_id"])
        DIAG = ("method_component", "external_ai_artifact")
        if cur is None or (POLARITY_RANK.get(lab.get("polarity"), 0)
                           > POLARITY_RANK.get(cur.get("polarity"), 0)):
            new = dict(lab)
            if cur is not None:
                # polarity-independent diagnostics from ANY snippet survive
                # polarity replacement, so paper-level flags are
                # order-independent (review-8 A3; review-11 A6: the v2.6
                # rollup dropped external_ai_artifact on every observed
                # paper — BOTH diagnostics are preserved now)
                mf = dict(new.get("flags") or {})
                for d in DIAG:
                    if (cur.get("flags") or {}).get(d):
                        mf[d] = True
                new["flags"] = mf
                for k in ("r5_zero_any", "r5_undet_any"):
                    if cur.get(k):
                        new[k] = True
            if lab.get("polarity") == "author_use":
                new["r5_zero_any"] = bool(new.get("r5_zero_any")) \
                    or bool(lab.get("has_explicit_zero_attempt"))
                new["r5_undet_any"] = bool(new.get("r5_undet_any")) \
                    or bool(lab.get("has_undetermined_use"))
            papers[r["arxiv_id"]] = new
        elif lab.get("polarity") == cur.get("polarity") == "author_use":
            # merge multi-snippet author_use evidence
            for key in ("tools", "models", "categories"):
                cur[key] = sorted(set((cur.get(key) or []) + (lab.get(key) or [])))
            # review-9 C8: keep the full impact SET, not only the max — a
            # paper with both a contributing use and an explicitly fruitless
            # attempt must never silently collapse to just the max
            seen_imp = set(cur.get("impacts_seen")
                           or [cur.get("epistemic_impact")])
            seen_imp.add(lab.get("epistemic_impact"))
            cur["impacts_seen"] = sorted(x for x in seen_imp if x)
            if IMPACT_RANK.get(lab.get("epistemic_impact"), 0) > \
               IMPACT_RANK.get(cur.get("epistemic_impact"), 0):
                cur["epistemic_impact"] = lab.get("epistemic_impact")
            locs = set(cur.get("locations") or [cur.get("location") or "unknown"])
            locs.add(lab.get("location") or "unknown")
            cur["locations"] = sorted(locs)
            # paper-level flags = OR over author_use snippets (review-8 A3:
            # unmerged flags made catalytic/method_component order-dependent)
            mf = dict(cur.get("flags") or {})
            for k, v in (lab.get("flags") or {}).items():
                mf[k] = bool(mf.get(k)) or bool(v)
            cur["flags"] = mf
            cur["r5_zero_any"] = bool(cur.get("r5_zero_any")) \
                or bool(lab.get("has_explicit_zero_attempt"))
            cur["r5_undet_any"] = bool(cur.get("r5_undet_any")) \
                or bool(lab.get("has_undetermined_use"))
        elif any((lab.get("flags") or {}).get(d) for d in DIAG):
            # lower-ranked snippet still contributes its diagnostics
            mf = dict(cur.get("flags") or {})
            for d in DIAG:
                if (lab.get("flags") or {}).get(d):
                    mf[d] = True
            cur["flags"] = mf
    # review-9 C8: explicit multi-state R5 fields for every author_use paper
    # (consumed by report/site/sampling instead of the scalar max alone)
    CONTRIB = {"cosmetic", "supportive", "result_bearing"}
    for lab in papers.values():
        if lab.get("polarity") != "author_use":
            continue
        seen = set(lab.get("impacts_seen") or [lab.get("epistemic_impact")])
        seen.discard(None)
        lab["impacts_seen"] = sorted(seen)
        lab["has_contributing_use"] = bool(seen & CONTRIB)
        # review-11 A5: co-located states inside ONE merged snippet arrive
        # via the label-level booleans; cross-snippet states via the union
        lab["has_zero_contribution_attempt"] = ("zero_contribution" in seen
                                                or bool(lab.get("r5_zero_any")))
        lab["has_undetermined_impact"] = ("undetermined" in seen
                                          or bool(lab.get("r5_undet_any")))
    # papers whose ONLY author_use evidence was gated away stay flagged
    ungated -= {p for p, lab in papers.items() if lab.get("polarity") == "author_use"}
    return papers, ungated


def build(con, scan_run: str, cls_run: str, out_path: Path,
          cohort_from: str, cohort_until: str,
          require_grounded: bool = False, require_rendered: bool = False,
          freeze: str | None = None) -> None:
    s_info, c_info = run_info(con, scan_run, cls_run, freeze=bool(freeze))
    if freeze and con.execute("SELECT 1 FROM releases WHERE release_id=?",
                              (freeze,)).fetchone():
        sys.exit(f"release id '{freeze}' already exists — releases are "
                 "immutable; pick a new id")

    frame_rows = con.execute(
        "SELECT arxiv_id, substr(created,1,7) mon FROM papers "
        "WHERE primary_category LIKE 'math%' AND created BETWEEN ? AND ?",
        (cohort_from, cohort_until)).fetchall()
    frame = {r["arxiv_id"]: r["mon"] for r in frame_rows}

    # denominator: provable scan completion, from the run's item ledger.
    # Every frame paper occupies exactly one coverage state (review-3 §5).
    items = {r["arxiv_id"]: r for r in con.execute(
        "SELECT arxiv_id, version, status, version_basis FROM scan_items "
        "WHERE run_id=?", (scan_run,))}
    scanned = {p for p, r in items.items() if p in frame and r["status"] == "ok"}
    scan_err = {p for p, r in items.items() if p in frame and r["status"] != "ok"}
    # any-ok aggregation: a paper with both src and pdf rows is fetched if ANY
    # row is ok (deterministic, unlike a last-row-wins dict)
    fetch_ok = {r["arxiv_id"]: bool(r["ok"]) for r in con.execute(
        "SELECT arxiv_id, MAX(CASE WHEN status LIKE 'ok%' THEN 1 ELSE 0 END) ok "
        "FROM files WHERE kind IN ('src','pdf') GROUP BY arxiv_id")}
    failed = {p for p in frame if p in fetch_ok and not fetch_ok[p] and p not in items}
    fetched_not_in_run = {p for p in frame
                          if fetch_ok.get(p) and p not in items}
    unfetched = {p for p in frame if p not in fetch_ok and p not in items}

    # scanner flags scoped to the run
    flagged = {r["arxiv_id"] for r in con.execute(
        "SELECT DISTINCT arxiv_id FROM scan_hits WHERE scan_run=? "
        "AND tier IN ('llm','generic') AND rule_class != 'known_fp'", (scan_run,))}

    # classification coverage: only items evidenced by THIS scan run (P0-3)
    eligible = eligible_item_ids(con, cls_run, scan_run)
    cls_seen: set[str] = set()
    any_ok: dict[str, bool] = {}
    for r in con.execute("SELECT id, arxiv_id, status FROM classification_items "
                         "WHERE run_id=?", (cls_run,)):
        if eligible is not None and r["id"] not in eligible:
            continue
        cls_seen.add(r["arxiv_id"])
        any_ok[r["arxiv_id"]] = any_ok.get(r["arxiv_id"], False) or r["status"] == "ok"
    cls_failed = {p for p, ok in any_ok.items() if not ok}

    rollup, ungated = paper_rollup(con, cls_run, scan_run,
                                   require_grounded, require_rendered)
    author_use = {p for p, lab in rollup.items() if lab.get("polarity") == "author_use"}
    pending = (flagged & scanned) - cls_seen
    unverified = ungated & scanned

    # version strata (LB-03): v1 / later / unknown — bulk snapshots have NULL
    # version and are never silently coerced to v1 (F1)
    v_of = {p: items[p]["version"] for p in scanned}

    def stratum(p: str) -> str:
        v = v_of.get(p)
        if v is None:
            return "unknown"
        if v != 1:
            return "later"
        # inferred-single-version is a DISTINCT stratum from fetched v1
        # (review-5 P0-8 / DECISIONS.md amendment)
        if items[p]["version_basis"] == "inferred-single-version":
            return "v1_inferred"
        return "v1"

    gates = []
    if require_grounded:
        gates.append("quote grounded in sent snippet")
    if require_rendered:
        gates.append("quote matched in arXiv-compiled PDF")
    lines = ["# ArxivObservatory report",
             "",
             "**Status: UNVALIDATED EXPLORATORY OUTPUT — DO NOT CITE.** Raw"
             " automated-classifier figures without human error correction;"
             " release status is inseparable from every copy of this file"
             " (review-6 P0-9)."
             if not freeze else
             f"**Frozen release candidate `{freeze}`** — enforced evidence "
             f"gates: {', '.join(gates) if gates else 'NONE REQUESTED (no grounding/render gate was applied)'}"
             " — review-10 D1: the exact gate list is stated, never a "
             "generic claim; see the release manifest.",
             "",
             f"Generated {dt.date.today().isoformat()} | cohort: math-primary papers "
             f"created {cohort_from}..{cohort_until}",
             "",
             "## Provenance",
             f"- scan run: `{scan_run}` (lexicon {s_info.get('lexicon_version')}, "
             f"code {s_info.get('code_commit')}, status {s_info.get('status')})",
             f"- classification run: `{cls_run}` (backend {c_info.get('backend')}, "
             f"model `{md_escape(c_info.get('model'))}`, taxonomy "
             f"{c_info.get('taxonomy_version')}, isolate={c_info.get('isolate')}, "
             f"status {c_info.get('status')})",
             f"- evidence gates: {', '.join(gates) if gates else 'none (raw labels)'}",
             "- measured construct: explicitly DISCLOSED generative-AI/LLM "
             "assistance as retrieved by the llm/generic scan-term protocol "
             "(review-8 A5). Standalone prover/CAS/ML-only mentions are not "
             "comprehensively classified and are OUTSIDE this numerator, "
             "even though those tool families appear in the taxonomy.",
             ""]
    # per-status breakdown of non-ok scan items, recomputed from the ledger
    # (never trusted from the run row — review-3 P0-2)
    err_breakdown = Counter(items[p]["status"].split(":")[0] for p in scan_err)
    lines.append(
        f"Coverage (every cohort paper in exactly one state): {len(frame)} in cohort; "
        f"{len(scanned)} scan-complete (per-item ledger); {len(scan_err)} scan "
        f"errors/incomplete/skipped ({dict(err_breakdown) or '—'}); "
        f"{len(fetched_not_in_run)} fetched but not in this scan run; "
        f"{len(failed)} fetch-failed (404/withdrawn/error — reported, not imputed); "
        f"{len(unfetched)} not fetched; "
        f"{len(pending)} flagged papers await classification; {len(cls_failed & scanned)} "
        f"classification failures; {len(unverified)} author-use candidates excluded by "
        f"evidence gates (listed, not counted).\n")
    # identification bounds (review-4 P0-2): unresolved papers are UNKNOWN,
    # not negatives — the Wilson intervals below condition on scan-complete
    # papers and cover none of this missingness
    n_pos = len(author_use & scanned)
    unresolved = ((set(frame) - scanned) | pending
                  | (cls_failed & scanned) | unverified)
    if frame:
        lines.append(
            f"Coverage-extreme raw-classifier-positive rates over the full "
            f"{len(frame)}-paper frame (NOT bounds on true prevalence — they "
            f"condition on accepting machine labels for observed papers and "
            f"omit classification error; review-8 D3): if every unresolved "
            f"paper (not scan-complete, pending, classification-failed, or "
            f"gate-excluded; {len(unresolved)} total) were a non-disclosure, "
            f"the raw rate would be {pct(n_pos / len(frame))}; if all were "
            f"disclosures, {pct((n_pos + len(unresolved)) / len(frame))}.\n")

    months = sorted({m for m in frame.values()})
    lines.append("## Prevalence by month (denominator = scan-complete papers; "
                 "pooled across source-version strata — see next table)\n")
    lines.append("| month | scanned | fetch-failed | unfetched | flagged | "
                 "author-use | pending | raw mixed-version classifier-positive "
                 "rate (Wilson 95%; not error-corrected) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for mon in months:
        mon_frame = {p for p, m in frame.items() if m == mon}
        ids = mon_frame & scanned
        n = len(ids)
        f_m, a_m = len(ids & flagged), len(ids & author_use)
        p_m = len(ids & pending)
        lo, hi = wilson(a_m, n)
        lines.append(f"| {mon} | {n} | {len(mon_frame & failed)} | "
                     f"{len(mon_frame & unfetched)} | {f_m} | {a_m} | {p_m} | "
                     f"{pct(a_m / n) if n else '—'} [{pct(lo)}–{pct(hi)}] |")

    # per-stratum rates: v1, later, unknown have different disclosure
    # opportunity — the pooled trend above is a mixture (F12)
    lines.append("\n## By source-version stratum (numerator, denominator, rate "
                 "per stratum)\n")
    lines.append("| month | stratum | scanned | author-use | rate (Wilson 95%) |")
    lines.append("|---|---|---|---|---|")
    for mon in months:
        ids = {p for p, m in frame.items() if m == mon} & scanned
        for st in ("v1", "v1_inferred", "later", "unknown"):
            sids = {p for p in ids if stratum(p) == st}
            if not sids:
                continue
            a_s, n_s = len(sids & author_use), len(sids)
            lo, hi = wilson(a_s, n_s)
            lines.append(f"| {mon} | {st} | {n_s} | {a_s} | "
                         f"{pct(a_s / n_s)} [{pct(lo)}–{pct(hi)}] |")

    tools, models, cats, impacts, locs = (Counter() for _ in range(5))
    display = author_use & scanned
    for p in display:
        lab = rollup[p]
        tools.update(lab.get("tools") or ["(unnamed)"])
        models.update(lab.get("models") or [])
        cats.update(lab.get("categories") or ["unspecified"])
        impacts[lab.get("epistemic_impact") or "none"] += 1
        for loc in (lab.get("locations") or [lab.get("location") or "unknown"]):
            locs[loc] += 1

    def table(counter: Counter, name: str, top: int = 25) -> None:
        lines.append(f"\n## {name}\n")
        lines.append("| value | papers |")
        lines.append("|---|---|")
        for v, c in counter.most_common(top):
            lines.append(f"| {md_escape(v)} | {c} |")

    n_d = len(display)
    _tv = tuple(int(x) for x in
                str(c_info.get("taxonomy_version") or "0").split(".")[:2])
    if _tv < (2, 8):
        # v2.7-COMPAT output: overlapping R5 states existed as recorded
        # fields under v2.7 (review-10 A6) — shown only for pre-v2.8 runs
        n_contrib = sum(1 for p in display
                        if rollup[p].get("has_contributing_use"))
        n_zero = sum(1 for p in display
                     if rollup[p].get("has_zero_contribution_attempt"))
        n_undet = sum(1 for p in display
                      if rollup[p].get("has_undetermined_impact"))
        lines.append(
            f"\nNamed quantities (R5, OVERLAPPING paper states — one paper "
            f"can be in several): papers disclosing attempted-or-contributing "
            f"generative-AI/LLM tool use = {n_d}; with a CONTRIBUTING use = "
            f"{n_contrib}; with an explicit zero-contribution attempt = "
            f"{n_zero}; with an undetermined-impact use = {n_undet}. "
            "Zero/undetermined states are never pooled into 'AI assistance'.\n")
    else:
        # v2.8: ONE scalar paper impact; finer per-use states deliberately
        # not recorded (owner decision 2026-08-14)
        lines.append(
            f"\nNamed quantities: papers disclosing delegated or attempted "
            f"generative-AI/LLM use = {n_d}; the impact table below is the "
            "paper-level scalar (strongest explicitly graded use).\n")
    table(tools, f"Tools ({n_d} author-use papers in cohort, multi-label)")
    table(models, "Exact model strings as written")
    table(cats, "Usage categories")
    table(impacts, "Epistemic impact (paper-level scalar)"
                   if _tv >= (2, 8) else
                   "Epistemic impact (paper max; overlapping R5 states "
                   "named above)")
    table(locs, "Disclosure locations (multi-location)")

    pol = Counter(lab.get("polarity") for p, lab in rollup.items() if p in scanned)
    lines.append("\n## Snippet-classified papers in cohort by polarity\n")
    lines.append("| polarity | papers |")
    lines.append("|---|---|")
    for v, c in pol.most_common():
        lines.append(f"| {md_escape(v)} | {c} |")

    if freeze:
        # a frozen release has no unresolved outcomes: flagged papers must be
        # classified, and no paper may have only failed classifications
        # (review-3 P0-4/§5). Checked BEFORE the report file is written — a
        # rejected freeze must not leave a plausible report behind (review-4)
        if pending or (cls_failed & scanned):
            sys.exit(f"cannot freeze: {len(pending)} papers pending "
                     f"classification, {len(cls_failed & scanned)} with only "
                     "failed classifications — resolve them first "
                     "(classify --resume)")

    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    print(f"report written to {out_path}")

    if freeze:
        def set_hash(ids: set) -> str:
            # verifiable membership: paper:version lines, sorted, hashed (F11)
            return hashlib.sha256("\n".join(
                sorted(f"{p}:{v_of.get(p)}" for p in ids)).encode()).hexdigest()

        manifest = {
            "cohort": {"from": cohort_from, "until": cohort_until,
                       # exact predicate, not shorthand (review-8 D1: "primary
                       # math.*" misdescribed a rule that deliberately
                       # includes math-ph — owner decision 2026-08-12)
                       "category_rule": "primary_category LIKE 'math%' "
                                        "(all math.* plus math-ph)",
                       "frame": len(frame)},
            "gates": gates,
            "counts": {"scanned": len(scanned), "scan_errors": len(scan_err),
                       "scan_error_breakdown": dict(err_breakdown),
                       "fetched_not_in_run": len(fetched_not_in_run),
                       "fetch_failed": len(failed), "unfetched": len(unfetched),
                       "flagged": len(flagged & scanned),
                       "author_use": len(display), "pending": len(pending),
                       "classification_failed": len(cls_failed & scanned),
                       "unverified_evidence": len(unverified)},
            "membership_sha256": {"scanned": set_hash(scanned),
                                  "author_use": set_hash(display),
                                  "flagged": set_hash(flagged & scanned)},
            "report": str(out_path),
            "report_sha256": hashlib.sha256(
                out_path.read_bytes()).hexdigest(),
        }
        with con:
            con.execute(
                "INSERT INTO releases (release_id, created_at, code_commit, "
                "cohort_json, scan_run, classification_run, manifest_json) "
                "VALUES (?,?,?,?,?,?,?)",
                (freeze, runs.utcnow(), db.code_commit(),
                 json.dumps(manifest["cohort"]), scan_run, cls_run,
                 json.dumps(manifest, sort_keys=True)))
        print(f"release '{freeze}' frozen (scan={scan_run}, cls={cls_run})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-run", required=True)
    ap.add_argument("--classification-run", required=True)
    ap.add_argument("--from", dest="cohort_from", default="2026-07-01")
    ap.add_argument("--until", dest="cohort_until", default="2026-08-08")
    ap.add_argument("--require-grounded", action="store_true")
    ap.add_argument("--require-rendered", action="store_true")
    ap.add_argument("--freeze", default=None, metavar="RELEASE_ID",
                    help="record this report as an immutable release manifest")
    ap.add_argument("--out", default="reports/report.md")
    args = ap.parse_args()
    con = db.connect()
    build(con, args.scan_run, args.classification_run, Path(args.out),
          args.cohort_from, args.cohort_until,
          args.require_grounded, args.require_rendered, args.freeze)
    return 0


if __name__ == "__main__":
    sys.exit(main())
