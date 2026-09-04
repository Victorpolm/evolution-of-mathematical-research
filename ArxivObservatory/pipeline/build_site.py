"""Local static-site generator: renders site/ from the DB.

- site/index.html        — submissions dashboard + aggregates-only disclosure
                           statistics (owner decision: no per-paper rows)
- site/data/*.json       — the extracted-layer aggregates the pages embed

v2 discipline: like pipeline/report.py, the site is a pure function of one
scan run + one classification run (scan_items denominator, run-scoped
rollup, optional evidence gates). Output is a complete HTML document
(doctype/lang/charset/viewport) with data-table equivalents for the charts.

Usage: python3 -m pipeline.build_site --scan-run <id> --classification-run <id>
           [--from 2026-07-01 --until 2026-08-08]
           [--require-grounded] [--require-rendered]
"""

from __future__ import annotations

import argparse
import datetime as dt
import html as html_mod
import json
import sys
from collections import Counter
from pathlib import Path

from . import db, report

SITE = db.PROJECT_ROOT / "site"

DOC_HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="description" content="Research prototype tracking '
            'disclosed AI assistance in arXiv mathematics papers. Independent '
            'project, not affiliated with arXiv.">\n'
            # no release exists: keep search engines away from exploratory
            # numbers (review-5 P0-1); remove at the first gated release
            '<meta name="robots" content="noindex">\n')



def bar_svg(items, color_var, width=480, fold=12):
    """items: (label, value) or (label, value, hover_title) tuples."""
    if not items:  # zero-positive cohorts must render, not crash (review-3)
        return (f'<svg viewBox="0 0 {width} 30" role="img">'
                '<text x="8" y="20" class="axis">no data in this cohort</text></svg>')
    rows = [(r + (None,))[:3] for r in items[:fold]]
    rest = sum(r[1] for r in items[fold:])
    if rest:
        rows.append(("Other", rest, "all remaining entries combined"))
    rh, h = 26, len(rows) * 26 + 6
    mx = max(r[1] for r in rows) or 1
    lw, bw = 160, width - 160 - 54
    parts = [f'<svg viewBox="0 0 {width} {h}" role="img">']
    for i, (name, v, title) in enumerate(rows):
        y = i * rh + 4
        w = max(2, v / mx * bw)
        fill = "var(--muted)" if name == "Other" else f"var({color_var})"
        t = html_mod.escape(str(title or f"{name}: {v}"))
        name = html_mod.escape(str(name))
        parts.append(
            f'<g><title>{t}</title>'
            f'<text x="{lw-8}" y="{y+13}" text-anchor="end" class="axis">{name}</text>'
            f'<rect x="{lw}" y="{y}" width="{w:.0f}" height="16" rx="3" fill="{fill}"/>'
            f'<text x="{lw+w+6:.0f}" y="{y+13}" class="axis">{v}</text></g>')
    parts.append("</svg>")
    return "".join(parts)


def line_svg(weeks, rates, los=None, his=None, width=980, height=260):
    # owner decision 2026-08-14 (review-12 D4): the observed cohort is a
    # census, not a sample — the headline chart shows no sampling bands.
    # los/his stay accepted for possible future gold-informed uncertainty.
    if not weeks:
        return (f'<svg viewBox="0 0 {width} 40" role="img">'
                '<text x="8" y="24" class="axis">no weekly data '
                '(cohort too thin)</text></svg>')
    m = {"l": 46, "r": 14, "t": 12, "b": 26}
    iw, ih = width - m["l"] - m["r"], height - m["t"] - m["b"]
    top = max(his if his else rates) * 1.15 or 1
    X = lambda i: m["l"] + (i * iw / max(1, len(weeks) - 1))
    Y = lambda v: m["t"] + ih * (1 - v / top)
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img">']
    step = 0.05 if top > 0.12 else 0.02
    v = 0.0
    while v <= top:
        parts.append(f'<line x1="{m["l"]}" x2="{m["l"]+iw}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" '
                     f'stroke="var(--grid)" stroke-width="1"/>'
                     f'<text x="{m["l"]-6}" y="{Y(v)+4:.1f}" text-anchor="end" class="axis">{v*100:.0f}%</text>')
        v += step
    if los and his:
        band = ("M" + " L".join(f"{X(i):.1f} {Y(l):.1f}" for i, l in enumerate(los))
                + " L" + " L".join(f"{X(i):.1f} {Y(h):.1f}" for i, h in reversed(list(enumerate(his)))) + " Z")
        parts.append(f'<path d="{band}" fill="var(--band)"/>')
    line = "M" + " L".join(f"{X(i):.1f} {Y(r):.1f}" for i, r in enumerate(rates))
    parts.append(f'<path d="{line}" fill="none" stroke="var(--s1)" stroke-width="2" '
                 'stroke-linejoin="round"/>')
    lbl_step = max(1, len(weeks) // 12)  # ~12 labels regardless of span
    for i, w in enumerate(weeks):
        if i % lbl_step == 0:
            lbl = w[:7] if len(weeks) > 30 else w[5:]  # yyyy-mm for long spans
            parts.append(f'<text x="{X(i):.1f}" y="{height-6}" text-anchor="middle" '
                         f'class="axis">{lbl}</text>')
    parts.append(f'<line id="rcross" x1="0" x2="0" y1="{m["t"]}" y2="{m["t"]+ih}" '
                 'stroke="var(--axis)" stroke-width="1" stroke-dasharray="3 3" '
                 'visibility="hidden"/>')
    parts.append("</svg>")
    return "".join(parts)

CATLBL = {  # union of v2.7 (old-run display) and v2.8 keys
    "proofreading": "proofreading (incl. math)",
    "proof_generation": "proof generation",
    "code_computation": "code & computation",
    "data_generation_labeling": "data generation & labeling",
    "writing_editing": "writing & editing", "proof_discovery": "proof discovery",
    "proof_checking_criticism": "proof checking", "ideation": "research ideas",
    "conjecture_generation": "conjecture generation",
    "computation_verification": "verifying computations",
    "literature_search": "literature search", "code_generation": "code writing",
    "proof_completion": "proof completion", "examples_counterexamples": "(counter)examples",
    "unspecified": "unspecified", "symbolic_computation": "symbolic computation",
    "numerical_computation": "numerical computation", "formalization": "formalization (Lean etc.)",
    "figures": "figures", "translation": "translation", "referee_response": "referee response"}
LOCLBL = {"dedicated_section": "dedicated AI section", "acknowledgments": "acknowledgments",
    "abstract": "abstract", "body": "main text", "comments_field": "arXiv comments field",
    "footnote_thanks": "footnote", "ancillary_artifact": "attached chat log", "unknown": "unclear"}


def _friendly(items, lbl):
    return [(lbl.get(k, k), v) for k, v in items]


def suppress_small(items, min_n: int = 3):
    """Public-cell privacy floor (review-7): cells below min_n aggregate into
    one 'other' bucket — a singleton tool/provider cell can be
    cross-referenced to identify a paper."""
    kept = [(k, v) for k, v in items if v >= min_n]
    small = sum(v for k, v in items if v < min_n)
    if small:
        kept.append((f"other (<{min_n} each)", small))
    return kept


def data_table(items, caption, val_label="papers"):
    """Accessible table equivalent for an SVG bar chart."""
    rows = "".join(
        f'<tr><th scope="row">{html_mod.escape(str(k))}</th>'
        f'<td>{html_mod.escape(str(v))}</td></tr>'
        for k, v, *_ in items)
    return (f'<details class="tbl"><summary>view as table</summary>'
            f'<table><caption>{html_mod.escape(caption)}</caption>'
            f'<thead><tr><th scope="col">value</th>'
            f'<th scope="col">{html_mod.escape(val_label)}</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></details>')


def build(scan_run: str, cls_run: str, d0: str, d1: str,
          require_grounded: bool = False, require_rendered: bool = False):
    con = db.connect()
    s_info, c_info = report.run_info(con, scan_run, cls_run)
    rollup, ungated = report.paper_rollup(con, cls_run, scan_run,
                                          require_grounded, require_rendered)
    frame = {r["arxiv_id"]: dict(r) for r in con.execute(
        "SELECT arxiv_id, created, primary_category FROM papers "
        "WHERE primary_category LIKE 'math%' AND created BETWEEN ? AND ?", (d0, d1))}
    scanned = {r["arxiv_id"] for r in con.execute(
        "SELECT arxiv_id FROM scan_items WHERE run_id=? AND status='ok'",
        (scan_run,))} & set(frame)
    if not scanned:
        sys.exit(f"no scan-complete papers in cohort {d0}..{d1} for run "
                 f"{scan_run} — refusing to build an empty site")
    au = {p for p in scanned if rollup.get(p, {}).get("polarity") == "author_use"}

    # field-level grounding (review-4 P0-4): a tool/model string is displayed
    # only if it occurs verbatim (case-insensitive) in one of the paper's
    # classified snippets — the classifier sometimes names tools that are not
    # in the text it was sent (319/8,051 entries in the current run)
    snip: dict[str, str] = {}
    for r in con.execute(
            "SELECT arxiv_id, snippet_text FROM classification_items "
            "WHERE run_id=? AND status='ok' AND polarity='author_use'",
            (cls_run,)):
        snip[r["arxiv_id"]] = (snip.get(r["arxiv_id"], "") + "\n"
                               + (r["snippet_text"] or "").lower())

    def grounded(p: str, s: str) -> bool:
        return bool(s) and s.lower() in snip.get(p, "")

    # source-version composition of the denominator (review-4: suppressing it
    # made the headline look cleaner than it is)
    vsn = Counter()
    for r in con.execute("SELECT arxiv_id, version, version_basis "
                         "FROM scan_items WHERE run_id=? AND status='ok'",
                         (scan_run,)):
        if r["arxiv_id"] not in frame:
            continue
        v = r["version"]
        if v is None:
            vsn["unknown"] += 1
        elif v != 1:
            vsn["later"] += 1
        elif r["version_basis"] == "inferred-single-version":
            # review-6 P1-3: the site must keep the stratum distinction the
            # report makes — inferred v1 is not fetched v1
            vsn["v1_inferred"] += 1
        else:
            vsn["v1"] += 1

    # rendered-evidence certification of the headline positives (review-5
    # P0-3), decomposed by REASON (review-6 P0-9: unknown-version, known-
    # version nonmatch, and PDF errors are different problems)
    _CERT_RANK = {"rendered": 5, "rendered_fuzzy": 4,
                  "non_rendered_evidence": 3, "quote_too_short": 3,
                  "pdf_error": 2, "no_pdf": 2, "unknown_version": 1}
    cert: dict[str, str] = {}
    for r in con.execute(
            "SELECT arxiv_id, render_status FROM classification_items "
            "WHERE run_id=? AND status='ok' AND polarity='author_use'",
            (cls_run,)):
        p, rs = r["arxiv_id"], r["render_status"]
        if _CERT_RANK.get(rs, 0) > _CERT_RANK.get(cert.get(p), 0):
            cert[p] = rs
    n_cert = sum(1 for p in au if cert.get(p) == "rendered")
    n_fuzzy = sum(1 for p in au if cert.get(p) == "rendered_fuzzy")
    n_nonmatch = sum(1 for p in au if cert.get(p) in
                     ("non_rendered_evidence", "quote_too_short"))
    n_pdferr = sum(1 for p in au if cert.get(p) in ("pdf_error", "no_pdf"))
    n_unkv = len(au) - n_cert - n_fuzzy - n_nonmatch - n_pdferr

    # full reason-coded unresolved partition, mirroring report.py (review-5
    # P0-2: frame-minus-scanned alone is wrong whenever pending or failed
    # classifications exist)
    flagged_ids = {r["arxiv_id"] for r in con.execute(
        "SELECT DISTINCT arxiv_id FROM scan_hits WHERE scan_run=? "
        "AND tier IN ('llm','generic') AND rule_class != 'known_fp'",
        (scan_run,))}
    eligible = report.eligible_item_ids(con, cls_run, scan_run)
    cls_seen: set[str] = set()
    cls_any_ok: dict[str, bool] = {}
    for r in con.execute("SELECT id, arxiv_id, status FROM classification_items "
                         "WHERE run_id=?", (cls_run,)):
        if eligible is not None and r["id"] not in eligible:
            continue
        cls_seen.add(r["arxiv_id"])
        cls_any_ok[r["arxiv_id"]] = (cls_any_ok.get(r["arxiv_id"], False)
                                     or r["status"] == "ok")
    pending = (flagged_ids & scanned) - cls_seen
    cls_failed = {p for p, ok in cls_any_ok.items() if not ok} & scanned
    n_unresolved = (len(frame) - len(scanned) + len(ungated & scanned)
                    + len(pending) + len(cls_failed))

    a, b = dt.date.fromisoformat(d0), dt.date.fromisoformat(d1)
    cohort_label = (f"{a:%b %-d, %Y} – {b:%b %-d, %Y}" if a.year != b.year
                    else f"{a:%B %-d} – {b:%b %-d, %Y}")

    # weekly series (Monday weeks by created date)
    def week_of(d):
        day = dt.date.fromisoformat(d)
        return (day - dt.timedelta(days=day.weekday())).isoformat()
    wk_n, wk_a = Counter(), Counter()
    for p in scanned:
        w = week_of(frame[p]["created"])
        wk_n[w] += 1
        if p in au:
            wk_a[w] += 1
    weeks = sorted(w for w in wk_n if wk_n[w] >= 200)  # drop thin edge weeks
    rates, los, his = [], [], []
    for w in weeks:
        lo, hi = report.wilson(wk_a[w], wk_n[w])
        rates.append(wk_a[w] / wk_n[w]); los.append(lo); his.append(hi)

    subf = Counter(); subf_n = Counter()
    for p in scanned:
        subf_n[frame[p]["primary_category"]] += 1
        if p in au:
            subf[frame[p]["primary_category"]] += 1
    subf_rate = sorted(((c, subf[c], subf_n[c]) for c in subf_n if subf_n[c] >= 100),
                       key=lambda x: -(x[1] / x[2]))
    tools, cats, imp, loc = Counter(), Counter(), Counter(), Counter()
    n_tool_dropped = 0
    for p in au:
        lab = rollup[p]
        for t in (lab.get("tools") or []):
            if not t:
                continue
            if grounded(p, t):
                tools[t] += 1
            else:
                n_tool_dropped += 1
        cats.update(lab.get("categories") or [])
        imp[lab.get("epistemic_impact") or "none"] += 1
        # multi-location, consistent with report.paper_rollup merging (F15)
        for location in (lab.get("locations") or [lab.get("location") or "unknown"]):
            loc[location] += 1

    # weekly (All math) + monthly (All math and larger subfields) rate series
    # for the client-side smoothing/range/subfield controls
    def rate_series(ids, keyfn):
        n_c, a_c = Counter(), Counter()
        for p in ids:
            k = keyfn(p)
            n_c[k] += 1
            if p in au:
                a_c[k] += 1
        out = []
        for k in sorted(n_c):
            lo, hi = report.wilson(a_c[k], n_c[k])
            out.append([k, n_c[k], a_c[k], round(a_c[k] / max(1, n_c[k]), 5),
                        round(lo, 5), round(hi, 5)])
        return out

    month_of = lambda p: frame[p]["created"][:7]
    series_data = {
        "daily": {"All math": rate_series(scanned, lambda p: frame[p]["created"])},
        "weekly": {"All math": rate_series(scanned,
                                           lambda p: week_of(frame[p]["created"]))},
        "monthly": {"All math": rate_series(scanned, month_of),
                    **{c: rate_series({p for p in scanned
                                       if frame[p]["primary_category"] == c},
                                      month_of)
                       for c in sorted(subf_n) if subf_n[c] >= 1000}},
    }

    data = {"generated": dt.date.today().isoformat(), "cohort": [d0, d1],
            "data_cutoff": d1,
            # machine consumers must see the status without the HTML around
            # it (review-5 P0-1)
            "release_status": "unreleased_exploratory",
            "do_not_cite": True,
            "render_certification": {"exact": n_cert, "fuzzy_only": n_fuzzy,
                                     "known_version_nonmatch": n_nonmatch,
                                     "pdf_error": n_pdferr,
                                     "unknown_version": n_unkv},
            "unresolved": {"not_scan_complete": len(frame) - len(scanned),
                           "pending_classification": len(pending),
                           "classification_failed": len(cls_failed),
                           "excluded_by_gates": len(ungated & scanned)},
            "provenance": {"scan_run": scan_run, "classification_run": cls_run,
                           "scan_status": s_info.get("status"),
                           "scan_code_commit": s_info.get("code_commit"),
                           "cls_status": c_info.get("status"),
                           "cls_code_commit": c_info.get("code_commit"),
                           "isolate": c_info.get("isolate"),
                           "model": c_info.get("model"),
                           "taxonomy": c_info.get("taxonomy_version"),
                           "lexicon": s_info.get("lexicon_version"),
                           "require_grounded": require_grounded,
                           "require_rendered": require_rendered,
                           "excluded_by_gates": len(ungated & scanned),
                           "source_version_strata": dict(vsn),
                           "tool_entries_ungrounded_excluded": n_tool_dropped},
            "n_frame": len(frame), "n_scanned": len(scanned), "n_author_use": len(au),
            # v2.7-COMPAT exports (overlapping R5 states + the retired
            # external-artifact diagnostic) appear ONLY for pre-v2.8 runs;
            # v2.8 publishes the scalar paper impact alone (owner decision
            # 2026-08-14, codex migration review item 5)
            **({"n_contributing_use": sum(
                    1 for p in au
                    if rollup.get(p, {}).get("has_contributing_use")),
                "n_zero_contribution_attempt": sum(
                    1 for p in au
                    if rollup.get(p, {}).get("has_zero_contribution_attempt")),
                "n_undetermined_impact": sum(
                    1 for p in au
                    if rollup.get(p, {}).get("has_undetermined_impact")),
                "n_external_ai_artifact_raw": sum(
                    1 for p in scanned
                    if (rollup.get(p, {}).get("flags") or {}).get(
                        "external_ai_artifact"))}
               if tuple(int(x) for x in str(
                   c_info.get("taxonomy_version") or "0").split(".")[:2])
               < (2, 8) else {}),
            "weeks": weeks, "weekly_rate": rates, "weekly_lo": los, "weekly_hi": his,
            "subfield_rates": subf_rate,
            "tools": suppress_small(tools.most_common(30)),
            "categories": cats.most_common(), "impact": imp.most_common(),
            "location": loc.most_common()}
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "data" / "disclosures.json").write_text(json.dumps(data, indent=1))

    rate = len(au) / len(scanned)
    lo, hi = report.wilson(len(au), len(scanned))
    from .sitetext import (AGENTIC_RE, CATNAMES, GLOSSARY_CSS, KEYWORDS_DETAILS,
                           METHODS_DETAILS, NON_LLM_RE, RATE_CONTROLS_JS,
                           RATE_HOVER_JS, gl, limitations_card, provider_of)
    n_failed = len(frame) - len(scanned)

    def panels_card(h_days: int) -> str:
        """One .hview block: the aggregate panels + further analysis for a
        time window, toggled by the shared horizon buttons (owner request
        2026-08-11 — full-window averages bury the 2026 signal)."""
        if h_days:
            cutoff = (dt.date.fromisoformat(d1)
                      - dt.timedelta(days=h_days)).isoformat()
            w_sc = {p for p in scanned if frame[p]["created"] >= cutoff}
        else:
            w_sc = scanned
        w_au = au & w_sc
        sf, sfn = Counter(), Counter()
        for p in w_sc:
            sfn[frame[p]["primary_category"]] += 1
            if p in w_au:
                sf[frame[p]["primary_category"]] += 1
        sub_rate = sorted(((c, sf[c], sfn[c]) for c in sfn if sfn[c] >= 100),
                          key=lambda x: -(x[1] / x[2]))
        sub_bar = [(f"{c} ({a}/{n})", round(1000 * a / n) / 10,
                    f"{CATNAMES.get(c, c)}: {a} of {n} scanned papers disclose "
                    f"AI use ({100*a/n:.1f}%)") for c, a, n in sub_rate[:12]]
        tools_w, cats_w, loc_w, prov_w = Counter(), Counter(), Counter(), Counter()
        n_named = n_llm = n_agentic = 0
        for p in w_au:
            lab = rollup[p]
            tl = [x for x in (lab.get("tools") or []) if x and grounded(p, x)]
            tools_w.update(tl)
            cats_w.update(lab.get("categories") or [])
            for location in (lab.get("locations")
                             or [lab.get("location") or "unknown"]):
                loc_w[location] += 1
            if tl:
                n_named += 1
                # papers naming ONLY proof assistants/CAS must not land in
                # "chat/other only" (review-4 §providers) — they get their
                # own bucket and stay out of the provider denominator
                llm_tl = [x for x in tl if not NON_LLM_RE.search(x)]
                if llm_tl:
                    n_llm += 1
                    prov_w.update({provider_of(x) for x in llm_tl} - {None})
                    if any(AGENTIC_RE.search(x) for x in llm_tl):
                        n_agentic += 1
        wlabel = {0: f"Full window ({cohort_label})",
                  365: "Last 12 months",
                  92: "Last 3 months"}[h_days]
        hide = "" if h_days == 0 else ' style="display:none"'
        return f"""<div class="hview" data-h="{h_days}"{hide}>
<p class="sub"><b>{wlabel}</b>: {len(w_au):,} author-use papers of
{len(w_sc):,} scanned.</p>
<div class="panels">
<div><h2>By subfield</h2><p class="sub">disclosure rate %, subfields with ≥100 papers in window (hover for full names)</p>{bar_svg(sub_bar, '--s1')}{data_table(sub_bar, "Disclosure rate by subfield", "rate %")}</div>
<div><h2>Tools named</h2><p class="sub">papers naming each tool (a paper can name several)</p>{bar_svg(suppress_small(tools_w.most_common(30)), '--s2')}{data_table(suppress_small(tools_w.most_common(30)), "Tools named")}</div>
<div><h2>What the AI was used for</h2><p class="sub">papers per category (multi-label)</p>{bar_svg(_friendly(cats_w.most_common(), CATLBL), '--s3')}{data_table(_friendly(cats_w.most_common(), CATLBL), "Usage categories")}</div>
<div><h2>Where the disclosure appears</h2><p class="sub">papers (all disclosure locations per paper counted)</p>{bar_svg(_friendly(loc_w.most_common(), LOCLBL), '--ord2')}{data_table(_friendly(loc_w.most_common(), LOCLBL), "Disclosure locations")}</div>
</div>
<details><summary class="fa">Further analysis: providers &amp; agentic systems</summary>
<div class="body"><div class="panels">
<div><h2>AI providers</h2><p class="sub">of the {n_llm:,} author-use papers
naming an LLM/agent tool in this window: papers naming ≥1 tool from each
provider (a paper can count for several; proof assistants and computer
algebra are excluded here; the grouping into providers is ours)</p>{bar_svg(suppress_small(prov_w.most_common()), '--s2')}{data_table(suppress_small(prov_w.most_common()), "AI providers")}</div>
<div><h2>Agentic systems</h2><p class="sub">papers naming an
agentic/coding-agent system (Claude Code, Codex, Cursor, math-agent systems,
…) vs chat assistants, among the {n_named:,} papers naming any tool</p>{bar_svg(
[("agentic system named", n_agentic),
 ("chat assistants only", n_llm - n_agentic),
 ("proof/CAS tools only", n_named - n_llm)], '--ord2')}{data_table(
[("agentic system named", n_agentic),
 ("chat assistants only", n_llm - n_agentic),
 ("proof/CAS tools only", n_named - n_llm)],
"Agentic share")}</div>
</div></div></details>
<p class="note">Category and impact labels are automated and not yet
human-audited — treat fine-grained splits as provisional.</p></div>"""
    n_contrib_au = sum(1 for p in au
                       if rollup.get(p, {}).get("has_contributing_use"))
    n_noncontrib_au = len(au) - n_contrib_au
    explainer = f"""<p class="foot" style="max-width:none">Share of new math papers whose text states that the authors
used generative-AI tools — chatbots, coding assistants, agentic systems —
for research or writing work, by week of first submission, {cohort_label}.
Papers that only study AI, or only use it as a measurement instrument, are
not counted. Overall: <b>{len(au):,} of {len(scanned):,} papers
({100*rate:.1f}%)</b>; in {n_contrib_au:,} of them the disclosed use
contributed to the paper, while {n_noncontrib_au:,} disclose only a
fruitless attempt or a use too vague to grade. Every scan-covered paper in
the window is counted — a census of the observed cohort, not a sample — so
no sampling bands are shown. The rates are
{gl('rawrate', 'uncorrected automated-classifier output')}; classifier
error and coverage, not sampling, are the dominant uncertainties.</p>"""
    disc = f"""
<div class="card" id="disclosures"><h2>Papers disclosing generative-AI/LLM tool use</h2>
<div class="ctl" id="rate-ctl">
<div class="seg" role="group" aria-label="Time horizon"><button data-h="92" aria-pressed="false">3 months</button><button data-h="365" aria-pressed="false">1 year</button><button data-h="0" aria-pressed="true">3 years</button></div>
<div class="seg" role="group" aria-label="Granularity"><button data-g="m" aria-pressed="false">Monthly</button><button data-g="w" aria-pressed="true">Weekly</button><button data-g="d" aria-pressed="false">Daily</button></div>
<div class="seg" role="group" aria-label="View"><button data-view="chart" aria-pressed="true">Chart</button><button data-view="table" aria-pressed="false">Table</button></div>
</div>
<div class="chips" id="rate-chips" aria-label="Subfield (weekly/daily: All math only)" style="margin:0 0 10px"></div>
<div id="rchart">{line_svg(weeks, rates)}</div>
<div id="rtablewrap" style="display:none"></div>
{explainer}
<div class="tip" id="rtip"></div></div>
<div class="card">
<div class="ctl" style="justify-content:space-between;align-items:baseline;margin-bottom:4px">
<h2 style="font-size:20px;margin:0">Disclosure breakdown</h2>
<span style="display:inline-flex;gap:8px;align-items:center"><span class="sub" style="margin:0">Aggregation window:</span><div class="seg" role="group" aria-label="Aggregation window" id="agg-ctl"><button data-ah="92" aria-pressed="false">3 months</button><button data-ah="365" aria-pressed="false">1 year</button><button data-ah="0" aria-pressed="true">3 years</button></div></span>
</div>
{panels_card(0)}{panels_card(365)}{panels_card(92)}</div>
{limitations_card(
    pct_unknown=round(100 * vsn.get("unknown", 0) / max(1, len(scanned))),
    n_v1=vsn.get("v1", 0), n_v1i=vsn.get("v1_inferred", 0),
    n_later=vsn.get("later", 0), n_unknown=vsn.get("unknown", 0),
    n_au=len(au), n_cert=n_cert, n_fuzzy=n_fuzzy, n_nonmatch=n_nonmatch,
    n_pdferr=n_pdferr, n_unkv=n_unkv,
    n_unresolved=n_unresolved, n_frame=len(frame),
    b_lo=f"{100 * len(au) / len(frame):.1f}",
    b_hi=f"{100 * (len(au) + n_unresolved) / len(frame):.1f}",
    isolate=c_info.get("isolate"),
    code_pristine=not str(c_info.get("code_commit") or "").endswith("dirty"))}
{KEYWORDS_DETAILS}
{METHODS_DETAILS.format(n_frame=len(frame), n_scanned=len(scanned),
                        n_failed=n_failed, generated=data['generated'],
                        cohort=cohort_label, cutoff=d1,
                        provenance=html_mod.escape(
                            f"scan {scan_run} (lexicon {s_info.get('lexicon_version')}) · "
                            f"classification {cls_run} (model {c_info.get('model')}, "
                            f"taxonomy v{c_info.get('taxonomy_version')}) · gates: "
                            + (', '.join(g for g, on in
                                         [('quote-grounded', require_grounded),
                                          ('render-checked', require_rendered)] if on)
                               or 'none')))}
<script>var CATNAMES = {json.dumps(CATNAMES).replace("<", "\\u003c")};
var RATE = {json.dumps({'weeks': weeks, 'rates': rates, 'los': los, 'his': his,
                        'ns': [wk_n[w] for w in weeks]}).replace("<", "\\u003c")};
var SERIES = {json.dumps(series_data).replace("<", "\\u003c")};
{RATE_HOVER_JS}
{RATE_CONTROLS_JS}
document.querySelectorAll('a[href="#methods"]').forEach(function (a) {{
  a.addEventListener('click', function () {{
    var m = document.getElementById('methods');
    if (m) m.open = true;
  }});
}});</script>
"""
    # the template lives OUTSIDE the publish root: site/ must contain only
    # current generated output (review-4: a stale directly-addressable
    # dashboard.html sat next to index.html)
    tpl = (Path(__file__).parent / "templates" / "dashboard.html").read_text()
    old_sub = "Daily and weekly counts of new math-primary submissions from the"
    assert old_sub in tpl
    a = tpl.index(old_sub); b = tpl.index("</p>", a)
    tpl = (tpl[:a] + "How is mathematics on arXiv changing in the age of AI? This page "
           "tracks how many new math papers appear each week (back to 2023) and how "
           "many openly acknowledge AI assistance. "
           '<a href="#methods" style="color:inherit">Data sources and methods</a> '
           "are explained at the bottom." + tpl[b:])

    # --- submissions layer: regenerated from the DB on every build (was a
    # baked JSON blob + hand-maintained tiles in the template; owner request
    # 2026-08-14). A rebuild after a fresh harvest updates everything. -------
    DASH_START = "2023-08-01"
    day_cat: Counter = Counter()
    for r in con.execute(
            "SELECT created, primary_category FROM papers "
            "WHERE primary_category LIKE 'math%' AND created BETWEEN ? AND ?",
            (DASH_START, d1)):
        day_cat[(r["created"], r["primary_category"])] += 1
    day0 = min(k[0] for k in day_cat)
    d1d = dt.date.fromisoformat(d1)
    span = (d1d - dt.date.fromisoformat(day0)).days
    all_days = [(dt.date.fromisoformat(day0) + dt.timedelta(days=i)).isoformat()
                for i in range(span + 1)]
    cat_totals: Counter = Counter()
    for (_, c_), v in day_cat.items():
        cat_totals[c_] += v
    # review-12 E5: category names and dates flow into client-side DOM
    # sinks — enforce a strict grammar at the serialization boundary
    import re as _re
    for c in cat_totals:
        assert _re.fullmatch(r"[A-Za-z][A-Za-z0-9.\-]*", c), f"bad category {c!r}"
    assert all(_re.fullmatch(r"\d{4}-\d{2}-\d{2}", d_) for d_ in all_days)
    sub_data = {"dates": all_days,
                "categories": {c: [day_cat.get((d_, c), 0) for d_ in all_days]
                               for c, _ in cat_totals.most_common()}}
    # hero: rolling 4 weeks ending at the data cutoff; the year-earlier
    # window is shifted exactly 52 weeks so weekday composition matches.
    # Absolute counts live in the tooltips (owner request 2026-08-14).
    w0 = (d1d - dt.timedelta(days=27)).isoformat()
    p1 = (d1d - dt.timedelta(days=364)).isoformat()
    p0 = (d1d - dt.timedelta(days=364 + 27)).isoformat()
    s28_now = sum(v for (d_, _), v in day_cat.items() if w0 <= d_ <= d1)
    s28_prev = sum(v for (d_, _), v in day_cat.items() if p0 <= d_ <= p1)
    sc28 = {p for p in scanned if frame[p]["created"] >= w0}
    au28 = au & sc28
    rate28 = len(au28) / max(1, len(sc28))
    w0d = dt.date.fromisoformat(w0)
    tiles = (
        f'<div class="eyebrow" style="margin:0 0 4px">Last 4 weeks '
        f'({w0d:%b %-d} – {d1d:%b %-d, %Y})</div>'
        f'<div class="tiles">'
        f'<div class="tile" title="{s28_now:,} new math-primary papers vs '
        f'{s28_prev:,} in the same 4 weeks a year earlier (window shifted '
        f'exactly 52 weeks, so weekdays align)">'
        f'<div class="v">{100*(s28_now/max(1,s28_prev)-1):+.0f}%</div>'
        f'<div class="l">submissions vs one year ago</div></div>'
        f'<div class="tile" title="{len(au28):,} of {len(sc28):,} scanned '
        f'papers; {s28_now - len(sc28):,} of the {s28_now:,} papers in this '
        f'window are not scan-covered">'
        f'<div class="v">{100*rate28:.1f}%</div>'
        f'<div class="l">of papers classified as disclosing AI assistance'
        f'</div></div>'
        f'</div>')
    assert "<!--TILES-->" in tpl
    tpl = tpl.replace("<!--TILES-->", tiles, 1)
    assert '{"dates": [], "categories": {}}' in tpl
    tpl = tpl.replace('{"dates": [], "categories": {}}',
                      json.dumps(sub_data).replace("<", "\\u003c"), 1)
    hdate = (con.execute("SELECT MAX(harvested_at) FROM papers").fetchone()[0]
             or "")[:10]
    tpl = tpl.replace("harvested 2026-08-09", f"harvested {hdate}", 1)
    banner = ('<div style="background:var(--surface);border:1px solid var(--border);'
        'border-radius:6px;padding:8px 14px;margin-bottom:12px;font-size:13.5px;'
        'color:var(--ink-2, #52514e)"><b>Research prototype — validation incomplete.</b> '
        'All disclosure figures are unvalidated automated-classifier output; do not cite. '
        'Independent project, not affiliated with arXiv. '
        '<a href="#limitations" style="color:inherit">Known limitations</a> '
        'apply to every figure below.</div>')
    tpl = tpl.replace('<div class="wrap">', '<div class="wrap">' + banner, 1)
    foot_anchor = '<p class="foot" style="max-width:none">Counts use'
    assert foot_anchor in tpl, "disclosure-section anchor missing from template"
    tpl = tpl.replace(foot_anchor, disc + '\n  ' + foot_anchor, 1)
    tpl = tpl.replace("</style>", GLOSSARY_CSS + TABLE_CSS + "\n</style>", 1)
    # complete document skeleton (doctype, lang, charset, viewport — LB-08/11)
    if not tpl.lstrip().lower().startswith("<!doctype"):
        tpl = (DOC_HEAD + tpl.replace("</style>", "</style>\n</head>\n<body>", 1)
               + "\n</body>\n</html>\n")
    (SITE / "index.html").write_text(tpl)
    (SITE / "disclosures.html").unlink(missing_ok=True)
    print(f"site built: {len(au)} author-use / {len(scanned)} scanned "
          f"({100*rate:.1f}% [{100*lo:.1f}-{100*hi:.1f}])")


TABLE_CSS = """
.ctl{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin:0 0 8px}
#rtablewrap table{border-collapse:collapse;font-size:13px;max-height:340px}
#rtablewrap{max-height:340px;overflow:auto}
#rtablewrap th,#rtablewrap td{border:1px solid var(--border);padding:3px 8px;text-align:left}
summary.fa{font-size:15.5px;font-weight:650;color:var(--ink)}
details.tbl{margin:8px 0 0}
details.tbl summary{font-size:12.5px;font-weight:500;color:var(--muted)}
details.tbl table{border-collapse:collapse;margin-top:6px;font-size:13px}
details.tbl caption{text-align:left;font-size:12px;color:var(--muted);padding:2px 0}
details.tbl th,details.tbl td{border:1px solid var(--border);padding:3px 8px;text-align:left}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-run", required=True)
    ap.add_argument("--classification-run", required=True)
    ap.add_argument("--from", dest="d0", default="2026-07-01")
    ap.add_argument("--until", dest="d1", default="2026-08-08")
    ap.add_argument("--require-grounded", action="store_true")
    ap.add_argument("--require-rendered", action="store_true")
    args = ap.parse_args()
    build(args.scan_run, args.classification_run, args.d0, args.d1,
          args.require_grounded, args.require_rendered)
    return 0


if __name__ == "__main__":
    main()
