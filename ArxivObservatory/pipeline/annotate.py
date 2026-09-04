"""Gold-study annotation tooling (GOLD_STUDY.md).

build      draw a seeded stratified sample from one frozen release and write
           blinded reviewer packets (±1500-char highlighted contexts, all of
           a paper's hits, member metadata — NO machine labels) + manifest
ingest     parse a filled packet back into the append-only annotations table
agreement  inter-rater agreement (percent + Cohen's kappa) and the
           adjudication worklist

Packets live under annotation/ (gitignored: they contain paper excerpts;
aggregate-only public policy, LB-07).
"""

from __future__ import annotations

import argparse
import gzip
import html
import io
import json
import os
import random
import re
import sys
import tarfile
from collections import Counter
from pathlib import Path

from . import db, lexicon, runs, scan, taxonomy

CONTEXT_RADIUS = 1500
MERGE_WINDOW = 3000
def _verdict_descriptions() -> dict[str, str]:
    """Grader-facing decision text is the SAME text the machine prompt uses
    — generated verbatim from taxonomy.POLARITIES (review-10 A2: the
    hand-written tooltips had drifted to a narrower 'used to produce the
    paper' construct that omitted the owner-confirmed instrumentation
    scope). Only NO_AI_MENTION and INSUFFICIENT_EVIDENCE are
    human-workflow-only verdicts with their own text."""
    P = taxonomy.POLARITIES
    return {
        "TRUE_DISCLOSURE": P["author_use"],
        "NON_USE_STATEMENT": P["non_use_statement"],
        "TOPIC_ONLY": P["topic_only"],
        "FALSE_POSITIVE": P["false_positive"],
        "NO_AI_MENTION":
            "You found no AI-related content anywhere (the normal outcome "
            "for items without excerpts).",
        "INSUFFICIENT_EVIDENCE":
            "The paper is unreadable or unavailable — you could not check.",
        "UNCLEAR": P["unclear"],
    }


VERDICT_DESCRIPTIONS = _verdict_descriptions()
VERDICTS = list(VERDICT_DESCRIPTIONS)

REVIEW_PROTOCOL = (
    "Protocol: excerpts, when shown, are retrieval hints — not the complete "
    "evidence. For items WITHOUT excerpts, check the standard disclosure "
    "locations only: acknowledgments (usually just before the references), "
    "first-page footnotes/thanks, abstract, and any Declarations / AI-use "
    "section; the PDF viewer's built-in search (click into the PDF, then "
    "Ctrl+F: 'AI', 'GPT', 'language model', 'Claude') is allowed and "
    "encouraged. One to two minutes per paper suffices — you are not "
    "expected to read the mathematics. IMPORTANT: a few excerpt-less items "
    "DO contain AI statements; the absence of excerpts never implies the "
    "answer. Work top to bottom; stopping early is fine — the order is "
    "random, so a truncated packet remains a valid random subsample. Judge "
    "rendered text only (rule R3).")


# --- source re-extraction (must mirror pipeline/scan.py exactly) -------------

def member_texts(path: str) -> dict[str, str]:
    """Per-member normalized text in the same coordinate space as the stored
    scan_hits offsets (strip_tex_comments -> lexicon.normalize). `path` may be
    a plain corpus path or a bulk 'tar::member' path (scan.read_blob)."""
    data = scan.read_blob(path)
    out: dict[str, str] = {}

    def norm(raw: bytes) -> str:
        return lexicon.normalize(scan.strip_tex_comments(scan.decode(raw)))

    if data[:2] == b"\x1f\x8b" or data[257:262] == b"ustar":
        try:
            tf = tarfile.open(fileobj=io.BytesIO(data), mode="r:*")
        except tarfile.TarError:
            out["main.tex"] = norm(gzip.decompress(data))
            return out
        with tf:
            for m in tf.getmembers():
                if not m.isfile() or m.size > scan.MAX_MEMBER_BYTES:
                    continue
                f = tf.extractfile(m)
                if f is None:
                    continue
                out[m.name] = norm(f.read())
        return out
    out["main.tex"] = norm(data)
    return out


def highlight(window: str) -> str:
    """Mark every lexicon match in the excerpt with ⟦…⟧."""
    spans = sorted({(h["offset"], h["offset"] + len(h["matched"]))
                    for h in lexicon.find_hits(window)})
    merged: list[list[int]] = []
    for lo, hi in spans:
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    for lo, hi in reversed(merged):
        window = window[:lo] + "⟦" + window[lo:hi] + "⟧" + window[hi:]
    return window


def hits_and_path(con, arxiv_id: str, scan_run: str) -> tuple[list[dict], str | None]:
    """DB half of context extraction: hit rows (as plain dicts, picklable) and
    the source path — None when there are no hits (negative-stratum papers
    must NOT pay for source extraction they don't need)."""
    # INDEXED BY: the planner otherwise walks the 525k-row run index for
    # every paper (21s/paper measured) instead of the ~24-hit paper index
    hits = [dict(r) for r in con.execute(
        "SELECT source_kind, file_member, term, offset, context FROM scan_hits "
        "INDEXED BY idx_hits_paper "
        "WHERE scan_run=? AND arxiv_id=? AND tier IN ('llm','generic') "
        "AND rule_class != 'known_fp' ORDER BY source_kind, file_member, offset",
        (scan_run, arxiv_id))]
    if not hits:
        return [], None
    frow = con.execute(
        "SELECT path, kind FROM files WHERE arxiv_id=? AND status LIKE 'ok%' "
        "AND path IS NOT NULL ORDER BY CASE kind WHEN 'src' THEN 0 ELSE 1 END LIMIT 1",
        (arxiv_id,)).fetchone()
    return hits, (frow["path"] if frow and frow["kind"] == "src" else None)


def blocks_from(arxiv_id: str, hits: list[dict], path: str | None) -> list[dict]:
    """CPU half (pool-safe): normalize the source and cut highlighted windows."""
    texts: dict[str, str] = {}
    if path:
        try:
            texts = member_texts(path)  # handles tar::member paths too
        except Exception as exc:  # noqa: BLE001
            print(f"  re-extract failed for {arxiv_id}: {exc}", file=sys.stderr)
    blocks: list[dict] = []
    for h in hits:
        member = h["file_member"] or ""
        text = texts.get(member)
        if h["source_kind"].startswith("meta:") or text is None:
            # metadata hit or no re-extractable source: stored context (±700)
            excerpt = h["context"]
            src = h["source_kind"]
            lo = hi = None
        else:
            lo = max(0, h["offset"] - CONTEXT_RADIUS)
            hi = min(len(text), h["offset"] + CONTEXT_RADIUS)
            excerpt = text[lo:hi]
            src = f"tex:{member}"
        # merge with previous block if overlapping window in same member —
        # extending the excerpt so the later hit is actually shown (F14)
        prev = blocks[-1] if blocks else None
        if (prev is not None and lo is not None and prev.get("lo") is not None
                and prev["src"] == src and lo - prev["lo"] < MERGE_WINDOW):
            prev["terms"].add(h["term"])
            if hi > prev["hi"]:
                prev["hi"] = hi
                prev["excerpt"] = text[prev["lo"]:hi]
            continue
        blocks.append({"src": src, "lo": lo, "hi": hi, "excerpt": excerpt,
                       "terms": {h["term"]}})
    for b in blocks:
        b["excerpt"] = highlight(b["excerpt"])
        b["terms"] = sorted(b["terms"])
    return blocks


def _extract_job(job: tuple) -> tuple[str, list[dict]]:
    pid, hits, path = job
    return pid, blocks_from(pid, hits, path)


def paper_contexts(con, arxiv_id: str, scan_run: str) -> list[dict]:
    """±CONTEXT_RADIUS excerpts around each hit cluster of the paper."""
    hits, path = hits_and_path(con, arxiv_id, scan_run)
    return blocks_from(arxiv_id, hits, path)


# --- build -------------------------------------------------------------------

def sample_strata(con, scan_run: str, cls_run: str, n_pos: int, n_flagged: int,
                  n_neg: int, seed: int, require_grounded: bool = False,
                  require_rendered: bool = False,
                  cohort_from: str | None = None, cohort_until: str | None = None,
                  category_like: str | None = None) -> tuple[dict[str, str], dict]:
    scanned = {r["arxiv_id"] for r in con.execute(
        "SELECT arxiv_id FROM scan_items WHERE run_id=? AND status='ok'", (scan_run,))}
    # review-4 P0-3: a gold sample for a released estimate must be drawn from
    # THAT estimate's frame (report cohort dates + category rule), not the
    # whole scan-complete universe — otherwise the inclusion weights estimate
    # a different population
    if cohort_from or cohort_until or category_like:
        q, params = "SELECT arxiv_id FROM papers WHERE 1=1", []
        if category_like:
            q += " AND primary_category LIKE ?"
            params.append(category_like)
        if cohort_from:
            q += " AND created >= ?"
            params.append(cohort_from)
        if cohort_until:
            q += " AND created <= ?"
            params.append(cohort_until)
        scanned &= {r["arxiv_id"] for r in con.execute(q, params)}
    flagged = {r["arxiv_id"] for r in con.execute(
        "SELECT DISTINCT arxiv_id FROM scan_hits WHERE scan_run=? "
        "AND tier IN ('llm','generic') AND rule_class != 'known_fp'", (scan_run,))}
    # POS mirrors the release's evidence gates so the sampled frame matches
    # what the headline counts (F14)
    pos_q = ("SELECT DISTINCT arxiv_id FROM classification_items WHERE run_id=? "
             "AND status='ok' AND polarity='author_use'")
    if require_grounded:
        pos_q += " AND quote_grounded=1"
    if require_rendered:
        pos_q += " AND render_status='rendered'"
    pos = {r["arxiv_id"] for r in con.execute(pos_q, (cls_run,))} & scanned
    flag_only = (flagged & scanned) - pos
    neg = scanned - flagged - pos  # strata must be disjoint (review-3 P0-6)
    rng = random.Random(seed)
    strata = {"POS": (sorted(pos), n_pos), "FLAG": (sorted(flag_only), n_flagged),
              "NEG": (sorted(neg), n_neg)}
    assignment: dict[str, str] = {}
    info: dict = {}
    for name, (pool, n) in strata.items():
        chosen = rng.sample(pool, min(n, len(pool)))
        for pid in chosen:
            assignment[pid] = name
        info[name] = {"frame": len(pool), "sampled": len(chosen),
                      "inclusion_prob": (len(chosen) / len(pool)) if pool else 0.0}
    return assignment, info


def cmd_build(args) -> int:
    for r in args.reviewers:  # names enter filenames — confine them
        if not re.fullmatch(r"[A-Za-z0-9_-]+", r):
            sys.exit(f"reviewer name {r!r} must be alphanumeric/_/-")
    con = db.connect()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    assignment, info = sample_strata(con, args.scan_run, args.classification_run,
                                     args.n_pos, args.n_flagged, args.n_neg,
                                     args.seed, args.require_grounded,
                                     args.require_rendered,
                                     args.cohort_from, args.cohort_until,
                                     args.category_like)
    papers = sorted(assignment)
    meta = {p: dict(r) for p, r in
            ((p, con.execute("SELECT title, comments, latest_version FROM papers "
                             "WHERE arxiv_id=?", (p,)).fetchone()) for p in papers)
            if r is not None}
    # the annotated version is the scanned artifact's version, not whatever
    # `papers` currently says (F14)
    item_version = {r["arxiv_id"]: r["version"] for r in con.execute(
        "SELECT arxiv_id, version FROM scan_items WHERE run_id=?",
        (args.scan_run,))}
    # per-reviewer orders first: plants must avoid already-reviewed positions
    orders = {}
    for reviewer in args.reviewers:
        o = papers[:]
        random.Random(f"{args.seed}-{reviewer}").shuffle(o)
        orders[reviewer] = o
    plants: set[str] = set()
    if args.plants:
        excluded = {p for o in orders.values()
                    for p in o[: args.plant_exclude_first]}
        candidates = sorted(p for p in papers
                            if assignment[p] in ("POS", "FLAG")
                            and p not in excluded)
        plants = set(random.Random(f"{args.seed}-plants").sample(
            candidates, min(args.plants, len(candidates))))

    # exact instrument bundle in the manifest (review-10 A2: a codebook
    # VERSION string alone cannot prove which decision text reviewers saw)
    import hashlib as _hl
    from . import classify as _classify, llm_api as _llm
    tax_md = db.PROJECT_ROOT / "TAXONOMY.md"
    bundle = {
        "taxonomy_version": taxonomy.TAXONOMY_VERSION,
        "taxonomy_md_sha256": (_hl.sha256(tax_md.read_bytes()).hexdigest()
                               if tax_md.exists() else None),
        "prompt_sha256": _hl.sha256(
            _classify.build_prompt_header().encode()).hexdigest(),
        "schema_sha256": _hl.sha256(json.dumps(
            _llm.batch_schema(), sort_keys=True).encode()).hexdigest(),
    }
    manifest = {"project": args.project, "scan_run": args.scan_run,
                "classification_run": args.classification_run,
                "codebook_version": taxonomy.TAXONOMY_VERSION,
                "instrument_bundle": bundle, "seed": args.seed,
                "gates": {"require_grounded": args.require_grounded,
                          "require_rendered": args.require_rendered},
                "cohort": {"from": args.cohort_from, "until": args.cohort_until,
                           "category_like": args.category_like},
                # until builds are release-bound, no packet from this tool
                # may produce release validity metrics (review-5 P0-9)
                "intended_use": "calibration_only_never_release_validity",
                "strata": info, "created_at": runs.utcnow(),
                "plants": sorted(plants),  # reviewers: do not open this file
                "plant_policy": {"n": len(plants),
                                 "exclude_first": args.plant_exclude_first},
                "assignment": assignment}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # contexts are reviewer-independent: extract once, in parallel (the TeX
    # normalization is CPU-bound), and cache to disk so adding a reviewer's
    # packet later costs seconds, not a rebuild
    ctx_path = out_dir / "contexts.json"
    if ctx_path.exists():
        blocks_cache = json.loads(ctx_path.read_text())
        print(f"reusing {len(blocks_cache)} cached contexts", flush=True)
    else:
        jobs = []
        for pid in papers:
            hits, path = hits_and_path(con, pid, args.scan_run)
            jobs.append((pid, hits, path))
        blocks_cache = {}
        from multiprocessing import Pool
        with Pool(8) as pool:
            for i, (pid, blocks) in enumerate(
                    pool.imap_unordered(_extract_job, jobs, chunksize=4), 1):
                blocks_cache[pid] = blocks
                if i % 100 == 0:
                    print(f"  contexts {i}/{len(jobs)}", flush=True)
        ctx_path.write_text(json.dumps(blocks_cache))

    # optional embedded PDFs (lazy-loaded in the packet; the negative arm
    # especially benefits — reviewers read the paper without leaving the page)
    pdf_map: dict[str, str] = {}
    if args.embed_pdfs:
        import requests as _requests

        from . import render_check
        session = _requests.Session()
        session.trust_env = False
        session.headers["User-Agent"] = render_check.USER_AGENT
        for i, pid in enumerate(papers, 1):
            v = item_version.get(pid) or meta.get(pid, {}).get("latest_version") or 1
            pdf_file, _src, _err = render_check.obtain_pdf(con, session, pid, v)
            if pdf_file is not None:
                pdf_map[pid] = os.path.relpath(pdf_file, out_dir)
            if i % 50 == 0:
                print(f"  pdfs {i}/{len(papers)}", flush=True)

    for reviewer in args.reviewers:
        order = orders[reviewer]
        lines = [f"# Annotation packet — project {args.project}, reviewer {reviewer}",
                 f"Codebook: TAXONOMY.md v{taxonomy.TAXONOMY_VERSION}; "
                 f"verdicts: {', '.join(VERDICTS)}",
                 "Blinded: this packet contains no machine labels or strata.",
                 REVIEW_PROTOCOL, ""]
        for i, pid in enumerate(order, 1):
            m = meta.get(pid, {})
            v = item_version.get(pid) or m.get("latest_version") or 1
            lines += [f"\n## ITEM {i} — arXiv {pid} v{v}",
                      f"title: {m.get('title') or '(unknown)'}",
                      f"comments field: {m.get('comments') or '—'}",
                      f"https://arxiv.org/abs/{pid}", ""]
            blocks = [] if pid in plants else blocks_cache.get(pid, [])
            if not blocks:
                lines += ["(no excerpts for this item)", ""]
            for b in blocks:
                lines += [f"### {b['src']} (terms: {', '.join(b['terms'])})",
                          "```", b["excerpt"], "```", ""]
            lines += ["VERDICT: ", "CATEGORIES: ", "IMPACT: ", "TOOLS: ",
                      "LOCATION: ", "NOTES: ", ""]
        (out_dir / f"packet_{reviewer}.md").write_text("\n".join(lines))
        (out_dir / f"packet_{reviewer}.html").write_text(
            html_packet(args.project, reviewer, order, meta, item_version,
                        blocks_cache, pdf_map, plants,
                        banner="CALIBRATION ROUND — these verdicts feed "
                               "instrument calibration and taxonomy hard "
                               "cases only; they never enter release "
                               "validity metrics (GOLD_STUDY.md)."))
        print(f"wrote {out_dir}/packet_{reviewer}.html (+ .md fallback, "
              f"{len(order)} items)")
    print(f"strata: {json.dumps(info)}")
    return 0


# --- HTML packets (structured entry; preferred over markdown) ----------------

HTML_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title><style>
body{margin:0 auto;max-width:900px;padding:24px 16px;background:#f9f9f7;
 color:#111;font:15px/1.5 system-ui,sans-serif}
.item{background:#fff;border:1px solid #ddd;border-radius:8px;
 padding:16px;margin:18px 0}
.item.done{border-color:#1baf7a;border-width:2px}
pre{white-space:pre-wrap;background:#f4f4f0;border:1px solid #e2e2da;
 border-radius:6px;padding:10px;font-size:13px;max-height:340px;overflow:auto}
mark{background:#ffe08a;padding:0 2px;border-radius:2px}
fieldset{border:1px solid #ddd;border-radius:6px;margin:8px 0}
legend{font-size:12.5px;font-weight:600;color:#555}
label{margin-right:14px;font-size:13.5px;white-space:nowrap;display:inline-block}
textarea,input[type=text]{width:100%%;box-sizing:border-box;font:inherit}
.usage{display:none}.usage.show{display:block}
#bar{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;
 padding:10px 4px;z-index:5;display:flex;gap:16px;align-items:center}
button{font:inherit;padding:6px 14px;border-radius:6px;border:1px solid #888;
 background:#2a78d6;color:#fff;cursor:pointer}
.meta{color:#555;font-size:13px}
</style></head><body>
<div id="bar"><b>%(title)s</b><span id="progress" class="meta"></span>
<button id="export">Export verdicts JSON</button></div>
<p class="meta">Codebook: TAXONOMY.md v%(codebook)s. Blinded: no machine labels
or strata are shown. %(protocol)s Progress autosaves in this browser; export
the JSON regularly as a checkpoint.</p>
"""


def _form_html(pid: str) -> str:
    e = html.escape
    # every verdict carries a hover tooltip (owner request 2026-08-12: any
    # potentially unknown word in this block should explain itself)
    verdicts = "".join(
        f'<label title="{e(VERDICT_DESCRIPTIONS[v])}">'
        f'<input type="radio" name="v_{pid}" value="{v}"> {v}</label>'
        for v in VERDICTS)
    cats = "".join(
        f'<label title="{e(d)}"><input type="checkbox" name="c_{pid}" '
        f'value="{c}"> {c}</label>'
        for c, d in taxonomy.CATEGORIES.items())
    # human and machine share ONE impact space (review-7 P0-1: the form
    # omitted R5's values, making a valid model outcome unrecordable);
    # not_applicable is excluded — it is implied by non-disclosure verdicts
    impacts = "".join(
        f'<label title="{e(taxonomy.IMPACTS[i])}"><input type="radio" '
        f'name="i_{pid}" value="{i}"> {i}</label>'
        for i in taxonomy.IMPACTS if i != "not_applicable")
    locs = "".join(
        f'<label><input type="checkbox" name="l_{pid}" value="{loc}"> {loc}</label>'
        for loc in taxonomy.LOCATIONS)
    # v2.8: catalytic is the only flag (author_use-only, inside the panel);
    # the former tri-state diagnostics and "also:" checkboxes are gone
    # (owner decision 2026-08-14)
    flags = "".join(
        f'<label title="{e(d)}"><input type="checkbox" name="f_{pid}" '
        f'value="{f}"> {f}</label>' for f, d in taxonomy.FLAGS.items())
    return (
        f'<fieldset><legend>verdict</legend>{verdicts}</fieldset>'
        f'<div class="usage" id="u_{pid}">'
        f'<fieldset><legend>usage categories (multi; mark every separately '
        f'evidenced role)</legend>{cats}</fieldset>'
        f'<fieldset><legend>epistemic impact — the strongest explicitly '
        f'GRADED use wins (result_bearing &gt; supportive &gt; cosmetic; '
        f'vaguer or fruitless co-uses never change it; undetermined only '
        f'when nothing grades; zero_contribution only when EVERY use is '
        f'explicitly fruitless)</legend>'
        f'{impacts}{flags}</fieldset>'
        f'<fieldset><legend>tools named (comma-separated)</legend>'
        f'<input type="text" name="t_{pid}"></fieldset></div>'
        f'<fieldset><legend>location of the statement (multi; answer for '
        f'ANY verdict that has AI-related text)</legend>{locs}</fieldset>'
        f'<fieldset><legend>notes (borderline cases feed TAXONOMY.md)</legend>'
        f'<textarea name="n_{pid}" rows="2"></textarea></fieldset>')


HTML_JS = r"""
<script>
"use strict";
var KEY = "annot:" + PROJECT + ":" + REVIEWER + ":" + CODEBOOK;
var state = JSON.parse(localStorage.getItem(KEY) || "{}");
function save() { localStorage.setItem(KEY, JSON.stringify(state)); progress(); }
function itemState(pid) { return state[pid] || (state[pid] = {}); }
function isComplete(st) {
  // an item is DONE only when ingest would accept it (v2.8: TRUE_DISCLOSURE
  // needs impact + >=1 category + >=1 location)
  if (!st || !st.verdict) return false;
  if (st.verdict !== "TRUE_DISCLOSURE") return true;
  return !!(st.impact && (st.categories || []).length
            && (st.locations || []).length);
}
function progress() {
  var done = ITEMS.filter(function (p) { return isComplete(state[p]); });
  document.getElementById("progress").textContent =
    done.length + " / " + ITEMS.length + " done";
  ITEMS.forEach(function (p) {
    // getElementById takes RAW ids — CSS.escape here broke the lookup for
    // ids containing dots (every arXiv id)
    var el = document.getElementById("item_" + p);
    if (el) el.classList.toggle("done", isComplete(state[p]));
    var u = document.getElementById("u_" + p);
    if (u) u.classList.toggle("show",
      !!(state[p] && state[p].verdict === "TRUE_DISCLOSURE"));
  });
}
function restore() {
  ITEMS.forEach(function (pid) {
    var s = state[pid] || {};
    document.getElementsByName("v_" + pid).forEach(function (r) {
      r.checked = r.value === s.verdict; });
    document.getElementsByName("i_" + pid).forEach(function (r) {
      r.checked = r.value === s.impact; });
    ["c", "l", "f"].forEach(function (k) {
      var key = { c: "categories", l: "locations", f: "flags" }[k];
      document.getElementsByName(k + "_" + pid).forEach(function (b) {
        b.checked = (s[key] || []).indexOf(b.value) !== -1; });
    });
    var t = document.getElementsByName("t_" + pid)[0];
    if (t) t.value = s.tools || "";
    var n = document.getElementsByName("n_" + pid)[0];
    if (n) n.value = s.notes || "";
  });
  progress();
}
document.addEventListener("change", function (ev) {
  var m = (ev.target.name || "").match(/^([vcilftn])_(.+)$/);
  if (!m) return;
  var pid = m[2], s = itemState(pid);
  if (m[1] === "v") s.verdict = ev.target.value;
  if (m[1] === "i") s.impact = ev.target.value;
  if (m[1] === "t") s.tools = ev.target.value;
  if (m[1] === "n") s.notes = ev.target.value;
  if (m[1] === "c" || m[1] === "l" || m[1] === "f") {
    var key = { c: "categories", l: "locations", f: "flags" }[m[1]];
    s[key] = Array.prototype.slice.call(
      document.getElementsByName(m[1] + "_" + pid))
      .filter(function (b) { return b.checked; })
      .map(function (b) { return b.value; });
  }
  save();
});
document.addEventListener("input", function (ev) {
  var m = (ev.target.name || "").match(/^([tn])_(.+)$/);
  if (!m) return;
  var s = itemState(m[2]);
  if (m[1] === "t") s.tools = ev.target.value;
  if (m[1] === "n") s.notes = ev.target.value;
  save();
});
document.getElementById("export").addEventListener("click", function () {
  var incomplete = ITEMS.filter(function (p) {
    return state[p] && state[p].verdict && !isComplete(state[p]); });
  if (incomplete.length &&
      !confirm("Items missing required fields (impact/category/location): " +
               incomplete.join(", ") + "\nExport anyway? They will be " +
               "rejected at ingest.")) return;
  var out = { project: PROJECT, reviewer: REVIEWER,
              codebook_version: CODEBOOK, items: [] };
  ITEMS.forEach(function (pid) {
    var s = state[pid];
    if (!s || !s.verdict) return;
    var isTrue = s.verdict === "TRUE_DISCLOSURE";
    // stale hidden usage state from an earlier verdict choice is
    // NORMALIZED away for non-disclosure verdicts (locations kept)
    out.items.push({ arxiv_id: pid, version: VERSIONS[pid],
      verdict: s.verdict, categories: isTrue ? (s.categories || []) : [],
      impact: isTrue ? (s.impact || "") : "",
      flags: isTrue ? (s.flags || []) : [],
      tools: isTrue ? (s.tools || "") : "",
      locations: s.locations || [],
      notes: s.notes || "" });
  });
  var blob = new Blob([JSON.stringify(out, null, 1)],
                      { type: "application/json" });
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "verdicts_" + REVIEWER + ".json";
  a.click();
});
document.addEventListener("toggle", function (ev) {
  var d = ev.target;
  if (!d.classList || !d.classList.contains("pdfbox") || !d.open) return;
  var slot = d.querySelector(".pdfslot");
  if (slot && !slot.firstChild) {
    var em = document.createElement("embed");
    em.src = d.getAttribute("data-pdf");
    em.type = "application/pdf";
    em.style.width = "100%"; em.style.height = "680px";
    slot.appendChild(em);
  }
}, true);
restore();
</script></body></html>
"""


def html_packet(project: str, reviewer: str, order: list[str], meta: dict,
                item_version: dict, blocks_cache: dict,
                pdf_map: dict | None = None,
                plants: set[str] | None = None,
                banner: str | None = None) -> str:
    e = html.escape
    parts = [HTML_HEAD % {"title": e(f"Annotation — {project} — {reviewer}"),
                          "codebook": e(taxonomy.TAXONOMY_VERSION),
                          "protocol": e(REVIEW_PROTOCOL)}]
    if banner:
        # immutable status marker on the artifact itself (review-5: packet
        # names alone don't say "never use for validity")
        parts.append(f'<div style="background:#fff3cd;border:1px solid '
                     f'#e0c36a;border-radius:6px;padding:8px 14px;'
                     f'margin:10px 0;font-weight:600">{e(banner)}</div>')
    for i, pid in enumerate(order, 1):
        m = meta.get(pid, {})
        v = item_version.get(pid) or m.get("latest_version") or 1
        parts.append(f'<div class="item" id="item_{e(pid)}">')
        parts.append(f'<h3>Item {i} — arXiv {e(pid)} v{v}</h3>')
        parts.append(f'<div class="meta">{e(m.get("title") or "(unknown title)")}'
                     f'<br>comments field: {e(m.get("comments") or "—")}<br>'
                     f'<a href="https://arxiv.org/abs/{e(pid)}v{v}" '
                     f'target="_blank" rel="noopener">arxiv.org/abs/{e(pid)}v{v}'
                     f'</a></div>')
        if pdf_map and pid in pdf_map:
            # PDFs are lazy-loaded on expand — 500 eager embeds would sink
            # the browser
            parts.append(
                f'<details class="pdfbox" data-pdf="{e(pdf_map[pid])}">'
                f'<summary>view paper PDF (v{v}, embedded)</summary>'
                f'<div class="pdfslot"></div></details>')
        item_blocks = [] if plants and pid in plants else blocks_cache.get(pid, [])
        if not item_blocks:
            parts.append('<div class="meta"><i>(no excerpts for this item — '
                         'apply the no-excerpt protocol from the top of the '
                         'page)</i></div>')
        for b in item_blocks:
            excerpt = e(b["excerpt"]).replace("⟦", "<mark>").replace("⟧", "</mark>")
            parts.append(f'<div class="meta">{e(b["src"])} '
                         f'(terms: {e(", ".join(b["terms"]))})</div>'
                         f'<pre>{excerpt}</pre>')
        parts.append(_form_html(e(pid)))
        parts.append("</div>")
    versions = {p: (item_version.get(p) or meta.get(p, {}).get("latest_version")
                    or 1) for p in order}
    # every string interpolated into inline JS gets the same </script>-safe
    # escaping as ITEMS (review-4: PROJECT/REVIEWER lacked it)
    js = lambda v: json.dumps(v).replace("<", "\\u003c")
    parts.append("<script>"
                 f"var PROJECT={js(project)};"
                 f"var REVIEWER={js(reviewer)};"
                 f"var CODEBOOK={js(taxonomy.TAXONOMY_VERSION)};"
                 f"var ITEMS={json.dumps(order).replace('<', chr(92) + 'u003c')};"
                 f"var VERSIONS={json.dumps(versions).replace('<', chr(92) + 'u003c')};"
                 "</script>")
    parts.append(HTML_JS)
    return "\n".join(parts)


# --- ingest ------------------------------------------------------------------

ITEM_RE = re.compile(r"^## ITEM \d+ — arXiv (\S+) v(\d+)", re.M)
FIELD_RE = re.compile(r"^(VERDICT|CATEGORIES|IMPACT|TOOLS|LOCATION|NOTES):[ \t]*(.*)$", re.M)


def validate_verdict_item(it: dict) -> tuple[dict | None, str]:
    """Strict enum validation of one exported JSON verdict; returns
    (clean, error). Usage fields are cleared unless TRUE_DISCLOSURE,
    cross-field invariants come from the SAME function as the machine
    validator, and non-disclosure verdicts store the canonical impact
    `not_applicable` (never a bare empty string). v2.8: catalytic is the
    only flag; the former tri-state diagnostics and r5 checkboxes are
    gone (owner decision 2026-08-14). Legacy export keys from older
    packets are rejected, never silently dropped."""
    pid = it.get("arxiv_id", "?")
    verdict = it.get("verdict")
    if verdict not in VERDICTS:
        return None, f"{pid}: unknown verdict {verdict!r}"
    ALLOWED_ITEM_KEYS = {"arxiv_id", "version", "verdict", "categories",
                         "impact", "flags", "tools", "locations", "notes"}
    LEGACY_ITEM_KEYS = {"method_component", "external_ai_artifact",
                        "r5_states", "has_explicit_zero_attempt",
                        "has_undetermined_use"}
    present_legacy = sorted(LEGACY_ITEM_KEYS & set(it))
    if present_legacy:
        # PRESENCE, not truthiness (review of v2.8 migration): an empty
        # legacy field still marks a pre-v2.8 packet
        return None, (f"{pid}: legacy v2.7 fields {present_legacy} — "
                      "re-grade with a v2.8 packet (labels across taxonomy "
                      "versions are never merged)")
    unknown_keys = sorted(set(it) - ALLOWED_ITEM_KEYS)
    if unknown_keys:
        return None, f"{pid}: unknown export keys {unknown_keys}"
    cats = it.get("categories") or []
    locs = it.get("locations") or []
    flags = list(it.get("flags") or [])
    impact = it.get("impact") or ""
    tools = (it.get("tools") or "")[:300]
    bad_flags = [f for f in flags if f not in taxonomy.FLAGS]
    if bad_flags:
        return None, f"{pid}: unknown flags {bad_flags}"
    if verdict == "TRUE_DISCLOSURE":
        bad = ([c for c in cats if c not in taxonomy.CATEGORIES]
               + [l for l in locs if l not in taxonomy.LOCATIONS])
        if bad:
            return None, f"{pid}: unknown labels {bad}"
        allowed = set(taxonomy.IMPACTS) - {"not_applicable"}
        if impact not in allowed:
            return None, f"{pid}: TRUE_DISCLOSURE needs an impact in {sorted(allowed)}, got {impact!r}"
        if not cats:
            return None, (f"{pid}: TRUE_DISCLOSURE needs at least one "
                          "category (use 'unspecified' when the role is "
                          "unknown)")
        if not locs:
            return None, (f"{pid}: TRUE_DISCLOSURE needs at least one "
                          "location (use 'unknown' when it cannot be "
                          "determined)")
        problems = taxonomy.cross_field_problems(
            True, impact, {f: True for f in flags})
        if problems:
            return None, f"{pid}: {'; '.join(problems)}"
    else:
        problems = taxonomy.cross_field_problems(
            False, "not_applicable", {f: True for f in flags})
        if problems:
            # fail closed: a hand-edited export claiming catalytic on a
            # non-disclosure verdict is an error, not a silent cleanup
            return None, f"{pid}: {'; '.join(problems)}"
        # locations survive for classifiable non-disclosure verdicts (the
        # statement still HAS a place); usage fields are cleared
        keep_locs = verdict in ("TOPIC_ONLY", "NON_USE_STATEMENT",
                                "FALSE_POSITIVE", "UNCLEAR")
        bad_locs = [l for l in locs if l not in taxonomy.LOCATIONS]
        if bad_locs:
            return None, f"{pid}: unknown locations {bad_locs}"
        cats, tools, impact = [], "", "not_applicable"
        locs = sorted(locs) if keep_locs else []
        flags = []
    return {"arxiv_id": pid, "version": it.get("version"), "verdict": verdict,
            "categories": sorted(cats), "impact": impact,
            "flags": sorted(set(flags)), "tools": tools,
            "locations": sorted(locs), "notes": (it.get("notes") or "")[:2000]}, ""


def ingest_json(con, args) -> int:
    data = json.loads(Path(args.json).read_text())
    if data.get("project") != args.project or data.get("reviewer") != args.reviewer:
        sys.exit(f"file is for project={data.get('project')!r} "
                 f"reviewer={data.get('reviewer')!r}, not "
                 f"{args.project!r}/{args.reviewer!r}")
    if data.get("codebook_version") != taxonomy.TAXONOMY_VERSION:
        # labels from different taxonomy versions are never merged
        sys.exit(f"export codebook_version={data.get('codebook_version')!r} "
                 f"but the current instrument is v{taxonomy.TAXONOMY_VERSION} "
                 "— re-grade with a current packet")
    # sample-membership validation (review-4 P0-3): verdicts for papers that
    # were never in the drawn sample must not enter the annotations table
    mpath = Path(getattr(args, "manifest", None)
                 or db.PROJECT_ROOT / "annotation" / args.project / "manifest.json")
    assigned: set[str] | None = None
    if mpath.exists():
        assigned = set(json.loads(mpath.read_text()).get("assignment", {}))
    else:
        print(f"  WARNING: no manifest at {mpath} — ingesting without "
              "sample-membership validation")
    existing = {r["arxiv_id"] for r in con.execute(
        "SELECT arxiv_id FROM annotations WHERE project=? AND reviewer=?",
        (args.project, args.reviewer))}
    n = n_bad = n_dup = 0
    now = runs.utcnow()
    with con:
        for it in data.get("items", []):
            clean, err = validate_verdict_item(it)
            if clean is None:
                print(f"  ERROR {err}")
                n_bad += 1
                continue
            if assigned is not None and clean["arxiv_id"] not in assigned:
                print(f"  ERROR {clean['arxiv_id']}: not in the project's "
                      "sampled assignment — rejected")
                n_bad += 1
                continue
            if clean["arxiv_id"] in existing:
                n_dup += 1  # append-only: re-ingest never duplicates
                continue
            existing.add(clean["arxiv_id"])  # within-file duplicates too
            label = {k: clean[k] for k in
                     ("categories", "impact", "flags", "tools", "locations")}
            con.execute(
                "INSERT INTO annotations (project, arxiv_id, version, reviewer, "
                "blinded, verdict, label_json, notes, codebook_version, created_at) "
                "VALUES (?,?,?,?,1,?,?,?,?,?)",
                (args.project, clean["arxiv_id"], clean["version"], args.reviewer,
                 clean["verdict"], json.dumps(label), clean["notes"],
                 data.get("codebook_version") or taxonomy.TAXONOMY_VERSION, now))
            n += 1
    print(f"ingested {n} verdicts for {args.reviewer} into {args.project}"
          + (f"; {n_dup} already present (skipped)" if n_dup else "")
          + (f"; {n_bad} rejected" if n_bad else ""))
    return 0 if n_bad == 0 else 1


def cmd_ingest(args) -> int:
    # all refusals happen BEFORE any database connection (review-12: the
    # legacy gate used to open the live DB in write mode first, so even a
    # rejected invocation touched production state)
    if not args.json:
        if not args.packet:
            sys.exit("need --json (preferred) or --packet")
        if not os.environ.get("ARXIV_OBS_LEGACY"):
            # delimiter-parsed markdown around hostile text, no manifest
            # binding (review-5 P0-10) — JSON export is the production path
            sys.exit("markdown packet ingest is a legacy fallback: it "
                     "bypasses manifest validation and parses delimiters "
                     "around untrusted text. Use the packet's Export JSON + "
                     "--json, or set ARXIV_OBS_LEGACY=1 to force.")
    con = db.connect()
    if args.json:
        return ingest_json(con, args)
    text = Path(args.packet).read_text()
    sections = ITEM_RE.split(text)[1:]  # [id, version, body, id, version, body, ...]
    existing = {r["arxiv_id"] for r in con.execute(
        "SELECT arxiv_id FROM annotations WHERE project=? AND reviewer=?",
        (args.project, args.reviewer))}
    n = n_bad = 0
    now = runs.utcnow()
    with con:
        for i in range(0, len(sections), 3):
            pid, version, body = sections[i], int(sections[i + 1]), sections[i + 2]
            if pid in existing:
                continue  # append-only: re-ingest never duplicates
            fields = {k: v.strip() for k, v in FIELD_RE.findall(body)}
            verdict = fields.get("VERDICT", "")
            if not verdict:
                continue
            if verdict not in VERDICTS:
                # invalid verdicts are rejected, not stored (F14)
                print(f"  ERROR {pid}: unknown verdict {verdict!r} — fix the "
                      "packet line and re-ingest")
                n_bad += 1
                continue
            label = {k.lower(): fields.get(k, "") for k in
                     ("CATEGORIES", "IMPACT", "TOOLS", "LOCATION")}
            con.execute(
                "INSERT INTO annotations (project, arxiv_id, version, reviewer, "
                "blinded, verdict, label_json, notes, codebook_version, created_at) "
                "VALUES (?,?,?,?,1,?,?,?,?,?)",
                (args.project, pid, version, args.reviewer, verdict,
                 json.dumps(label), fields.get("NOTES", ""),
                 taxonomy.TAXONOMY_VERSION, now))
            n += 1
    print(f"ingested {n} verdicts for {args.reviewer} into project {args.project}"
          + (f"; {n_bad} rejected" if n_bad else ""))
    return 0 if n_bad == 0 else 1


# --- agreement ---------------------------------------------------------------

def cohens_kappa(pairs: list[tuple[str, str]]) -> float:
    if not pairs:
        return float("nan")
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def cmd_calibration(args) -> int:
    """Deterministic calibration analysis (review-7 P0-2): one command from
    manifest + machine labels + ingested verdicts to a full aggregate summary
    with explicit denominators. Exclusions are reason-coded arguments, never
    silent reclassification. Emits markdown + machine-readable JSON."""
    from . import report as report_mod
    con = db.connect()
    out_dir = Path(args.out or f"annotation/{args.project}")
    m = json.loads((out_dir / "manifest.json").read_text())
    assign, plants = m["assignment"], set(m.get("plants", []))
    excl = dict(x.split(":", 1) for x in (args.exclude or []))
    rollup, _ = report_mod.paper_rollup(
        con, args.classification_run, args.scan_run, True, False)
    human = {r["arxiv_id"]: r["verdict"] for r in con.execute(
        "SELECT arxiv_id, verdict FROM annotations WHERE project=? AND reviewer=?",
        (args.project, args.reviewer))}

    def wilson(k, n):
        return report_mod.wilson(k, n)

    def mpol(p):
        return rollup.get(p, {}).get("polarity") or "(no valid label)"

    # review-8 C6: UNCLEAR / INSUFFICIENT_EVIDENCE are a NON-EVALUABLE
    # stratum (GOLD_STUDY.md), never binary negatives — the old code
    # happened to give the same numbers only because neither verdict
    # occurred in this round
    NON_EVALUABLE = {"UNCLEAR", "INSUFFICIENT_EVIDENCE"}
    non_eval = {p: v for p, v in human.items()
                if p not in excl and v in NON_EVALUABLE}
    comparable = {p: v for p, v in human.items()
                  if p not in excl and v not in NON_EVALUABLE}
    pos_shown = [(p, v) for p, v in comparable.items()
                 if assign.get(p) == "POS" and p not in plants]
    pos_plant = [(p, v) for p, v in comparable.items()
                 if p in plants and mpol(p) == "author_use"]
    flag = [(p, v) for p, v in comparable.items()
            if assign.get(p) == "FLAG" and p not in plants]
    neg = [(p, v) for p, v in comparable.items() if assign.get(p) == "NEG"]
    tp = sum(1 for _, v in pos_shown if v == "TRUE_DISCLOSURE")
    pf = sum(1 for _, v in pos_plant if v == "TRUE_DISCLOSURE")
    neg_miss = sum(1 for _, v in neg if v == "TRUE_DISCLOSURE")
    agree = sum(1 for p, v in comparable.items()
                if (v == "TRUE_DISCLOSURE") == (mpol(p) == "author_use"))
    # review-9 A2: a combined number conflates papers the model actually
    # classified with structural no-snippet negatives that cannot test the
    # instrument — report BOTH denominators separately
    model_seen = {r["arxiv_id"] for r in con.execute(
        "SELECT DISTINCT arxiv_id FROM classification_items "
        "WHERE run_id=? AND status='ok'", (args.classification_run,))}
    evaluable = {p: v for p, v in comparable.items() if p in model_seen}
    no_snippet = {p: v for p, v in comparable.items() if p not in model_seen}
    agree_eval = sum(1 for p, v in evaluable.items()
                     if (v == "TRUE_DISCLOSURE") == (mpol(p) == "author_use"))
    agree_nosnip = sum(1 for p, v in no_snippet.items()
                       if (v == "TRUE_DISCLOSURE") == (mpol(p) == "author_use"))

    def pw(k, n):
        lo, hi = wilson(k, n)
        return f"{k}/{n} = {100*k/n:.1f}% (Wilson [{100*lo:.1f}%, {100*hi:.1f}%])" \
            if n else "n=0"

    data = {
        "project": args.project, "reviewer": args.reviewer,
        "codebook_version": m.get("codebook_version"),
        "n_ingested": len(human), "n_comparable": len(comparable),
        "non_evaluable": dict(non_eval),
        "exclusions": excl,
        "pos_shown": {"n": len(pos_shown), "true_disclosure": tp},
        "pos_plants": {"n": len(pos_plant), "found": pf},
        "flag": {"n": len(flag),
                 "true_disclosure": sum(1 for _, v in flag
                                        if v == "TRUE_DISCLOSURE")},
        "neg": {"n": len(neg), "candidate_misses": neg_miss},
        "binary_agreement": {"n": len(comparable), "agree": agree},
        "binary_agreement_model_evaluable": {"n": len(evaluable),
                                             "agree": agree_eval},
        "binary_agreement_no_snippet": {"n": len(no_snippet),
                                        "agree": agree_nosnip},
        "equivalence_map": "TRUE_DISCLOSURE vs everything-else; all "
                           "non-disclosure verdicts are one bucket",
    }
    lines = [f"# Calibration analysis — {args.project} / {args.reviewer} "
             f"(generated, do not hand-edit)",
             "",
             f"- ingested: {len(human)}; comparable: {len(comparable)} "
             f"(reason-coded exclusions: {excl or 'none'}; non-evaluable "
             f"UNCLEAR/INSUFFICIENT_EVIDENCE verdicts: {len(non_eval)} — "
             "excluded from binary metrics as their own stratum)",
             f"- POS shown-excerpt precision: {pw(tp, len(pos_shown))}",
             f"- POS plants found: {pw(pf, len(pos_plant))} (process check "
             "only — plants are scanner-detectable cases)",
             f"- FLAG human disclosures: "
             f"{pw(data['flag']['true_disclosure'], len(flag))}",
             f"- NEG candidate misses: {pw(neg_miss, len(neg))} "
             "('none observed' is not a zero miss rate)",
             f"- binary disclosure concordance: {pw(agree, len(comparable))}",
             f"  - model-evaluable papers (model produced >=1 valid label): "
             f"{pw(agree_eval, len(evaluable))}",
             f"  - structural no-snippet papers (cannot test the "
             f"instrument): {pw(agree_nosnip, len(no_snippet))}",
             "",
             "Single-human machine concordance, NOT inter-rater reliability "
             "or adjudicated validity. Calibration data never enters "
             "release validity metrics."]
    (out_dir / "calibration_analysis.md").write_text("\n".join(lines) + "\n")
    (out_dir / "calibration_analysis.json").write_text(
        json.dumps(data, indent=1))
    print("\n".join(lines))
    return 0


def cmd_agreement(args) -> int:
    con = db.connect()
    rows = con.execute(
        "SELECT arxiv_id, reviewer, verdict FROM annotations WHERE project=? "
        "AND reviewer != 'adjudicator' ORDER BY created_at", (args.project,)).fetchall()
    by_paper: dict[str, dict[str, str]] = {}
    for r in rows:
        by_paper.setdefault(r["arxiv_id"], {})[r["reviewer"]] = r["verdict"]
    pairs, disagreements = [], []
    for pid, verdicts in sorted(by_paper.items()):
        vs = list(verdicts.items())
        if len(vs) < 2:
            continue
        (r1, v1), (r2, v2) = vs[0], vs[1]
        pairs.append((v1, v2))
        if v1 != v2:
            disagreements.append((pid, r1, v1, r2, v2))
    if not pairs:
        # distinguishable from a successful agreement computation (review-4)
        print("no doubly-annotated items yet")
        return 1
    agree = sum(a == b for a, b in pairs) / len(pairs)
    print(f"{len(pairs)} doubly-annotated items | percent agreement {agree:.1%} | "
          f"Cohen's kappa {cohens_kappa(pairs):.3f}")
    if disagreements:
        print("\nAdjudication worklist:")
        for pid, r1, v1, r2, v2 in disagreements:
            print(f"  {pid}: {r1}={v1} vs {r2}={v2}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--project", required=True)
    b.add_argument("--scan-run", required=True)
    b.add_argument("--classification-run", required=True)
    b.add_argument("--n-pos", type=int, default=150)
    b.add_argument("--n-flagged", type=int, default=50)
    b.add_argument("--n-neg", type=int, default=300)
    b.add_argument("--seed", type=int, default=42)
    b.add_argument("--require-grounded", action="store_true",
                   help="POS stratum mirrors the release gate")
    b.add_argument("--require-rendered", action="store_true")
    b.add_argument("--from", dest="cohort_from", default=None,
                   help="restrict the sample frame to the report cohort "
                        "(created >= DATE) — required for a release-bound "
                        "gold study (review-4 P0-3)")
    b.add_argument("--until", dest="cohort_until", default=None)
    b.add_argument("--category-like", default=None, metavar="PATTERN",
                   help="SQL LIKE pattern on primary_category, e.g. 'math%%'")
    b.add_argument("--embed-pdfs", action="store_true",
                   help="fetch version-pinned PDFs and embed a lazy viewer per item")
    b.add_argument("--plants", type=int, default=0,
                   help="number of POS/FLAG items displayed WITHOUT excerpts "
                        "(search-honesty checks; measures human search "
                        "sensitivity; identities recorded in the manifest)")
    b.add_argument("--plant-exclude-first", type=int, default=0,
                   help="never plant within the first N positions of any "
                        "reviewer's order (protects in-progress packets)")
    b.add_argument("--reviewers", nargs="+", required=True)
    b.add_argument("--out", required=True)
    b.set_defaults(func=cmd_build)
    g = sub.add_parser("ingest")
    g.add_argument("--project", required=True)
    g.add_argument("--packet", default=None, help="markdown packet (fallback)")
    g.add_argument("--json", default=None,
                   help="verdicts JSON exported from the HTML packet (preferred)")
    g.add_argument("--reviewer", required=True)
    g.add_argument("--manifest", default=None,
                   help="manifest.json for sample-membership validation "
                        "(default: annotation/<project>/manifest.json)")
    g.set_defaults(func=cmd_ingest)
    c = sub.add_parser("calibration")
    c.add_argument("--project", required=True)
    c.add_argument("--reviewer", required=True)
    c.add_argument("--scan-run", required=True)
    c.add_argument("--classification-run", required=True)
    c.add_argument("--exclude", nargs="*", default=None,
                   metavar="PAPER:REASON",
                   help="reason-coded non-comparable items (e.g. "
                        "2404.05856:packet-version-skew)")
    c.add_argument("--out", default=None)
    c.set_defaults(func=cmd_calibration)
    a = sub.add_parser("agreement")
    a.add_argument("--project", required=True)
    a.set_defaults(func=cmd_agreement)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
