"""Reader-facing text blocks for the generated site: glossary tooltips,
subfield names, keyword list, data-sources box, chart hover script."""

from __future__ import annotations

import html

from . import lexicon

CATNAMES = {
    "math.AG": "Algebraic Geometry", "math.AT": "Algebraic Topology",
    "math.AP": "Analysis of PDEs", "math.CT": "Category Theory",
    "math.CA": "Classical Analysis and ODEs", "math.CO": "Combinatorics",
    "math.AC": "Commutative Algebra", "math.CV": "Complex Variables",
    "math.DG": "Differential Geometry", "math.DS": "Dynamical Systems",
    "math.FA": "Functional Analysis", "math.GM": "General Mathematics",
    "math.GN": "General Topology", "math.GT": "Geometric Topology",
    "math.GR": "Group Theory", "math.HO": "History and Overview",
    "math.IT": "Information Theory", "math.KT": "K-Theory and Homology",
    "math.LO": "Logic", "math.MP": "Mathematical Physics",
    "math.MG": "Metric Geometry", "math.NT": "Number Theory",
    "math.NA": "Numerical Analysis", "math.OA": "Operator Algebras",
    "math.OC": "Optimization and Control", "math.PR": "Probability",
    "math.QA": "Quantum Algebra", "math.RT": "Representation Theory",
    "math.RA": "Rings and Algebras", "math.SP": "Spectral Theory",
    "math.ST": "Statistics Theory", "math.SG": "Symplectic Geometry",
}

GLOSSARY = {
    "wilson": ("A 95% confidence interval for a proportion (Wilson score "
               "method): the range the true rate is statistically compatible "
               "with, given the number of papers observed.",
               "https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval"),
    "recall": ("Recall = the share of all truly disclosing papers that the "
               "scanner finds. An AI agent re-read 200 scanner-negative papers "
               "and flagged 2 (one a clear miss, one arguably out of scope); "
               "this is an indicative check, not a validated recall estimate — "
               "human adjudication is pending.",
               "https://en.wikipedia.org/wiki/Precision_and_recall"),
    "rawrate": ("The rate of papers our automated pipeline classifies as "
                "disclosing — without any correction for classifier error. "
                "Human-validated error rates for this pipeline do not exist "
                "yet, so the size of that correction is unknown.",
                "https://en.wikipedia.org/wiki/Sensitivity_and_specificity"),
}

GLOSSARY_CSS = """
:root{--ink2:#52514e;--band:rgba(42,120,214,.15);--ord1:#86b6ef;--ord2:#2a78d6;--ord3:#104281}
@media (prefers-color-scheme: dark){:root:where(:not([data-theme="light"])){
  --ink2:#c3c2b7;--band:rgba(57,135,229,.22);--ord1:#9ec5f4;--ord2:#3987e5;--ord3:#184f95}}
:root[data-theme="dark"]{--ink2:#c3c2b7;--band:rgba(57,135,229,.22);
  --ord1:#9ec5f4;--ord2:#3987e5;--ord3:#184f95}
.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:8px 30px}
.panels svg .axis{font-size:14px}

.gl{border-bottom:1px dotted var(--muted);cursor:help;text-decoration:none;color:inherit}
details{margin:0 0 16px}
details summary{cursor:pointer;font-weight:600;font-size:14px;color:var(--ink-2, var(--ink2))}
details .body{background:var(--surface);border:1px solid var(--border);
  border-radius:6px;padding:12px 14px;margin-top:8px;font-size:13.5px;color:var(--ink-2, var(--ink2))}
.kwgrid{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
.kw{border:1px solid var(--border);border-radius:999px;padding:2px 9px;font-size:12.5px}
"""


def gl(key: str, text: str) -> str:
    tip, url = GLOSSARY[key]
    return (f'<a class="gl" href="{url}" target="_blank" rel="noopener" '
            f'title="{html.escape(tip)}">{text}</a>')


KW_DISPLAY = {"large language model": "LLM / large language model"}

# --- "Further analysis" groupings (owner decision 2026-08-11) ---------------
# The main "Tools named" chart stays verbatim-as-disclosed; grouping happens
# only in the expandable section. Ordered regex rules — first match wins
# (Claude Code before Claude, GitHub Copilot before Copilot, ChatGPT before
# GPT). Non-LLM tools (provers/CAS) are excluded from the provider view.
import re as _re

NON_LLM_RE = _re.compile(
    r"lean|mathlib|coq|rocq|isabelle|agda|metamath|mathematica|wolfram|maple|"
    r"magma|sage|gap\b|pari|macaulay|singular|oscar|polymake|snappy|sympy|"
    r"matlab|latex|grammarly|overleaf", _re.I)

PROVIDER_RULES: list[tuple[_re.Pattern, str]] = [
    (_re.compile(r"chat\s*-?gpt|gpt|o[1-9][\s-]?(mini|pro|high)?$|openai|codex|"
                 r"deep\s*research", _re.I), "OpenAI"),
    (_re.compile(r"claude|anthropic|fable|opus|sonnet|haiku", _re.I), "Anthropic"),
    (_re.compile(r"gemini|bard|notebooklm|deep\s*think|alpha(proof|geometry|evolve)|"
                 r"funsearch|co-?scientist|google", _re.I), "Google"),
    (_re.compile(r"deepseek", _re.I), "DeepSeek"),
    (_re.compile(r"grok|xai", _re.I), "xAI"),
    (_re.compile(r"llama|meta\s*ai", _re.I), "Meta"),
    (_re.compile(r"mistral", _re.I), "Mistral"),
    (_re.compile(r"qwen|tongyi|qianwen", _re.I), "Alibaba"),
    (_re.compile(r"kimi|moonshot", _re.I), "Moonshot"),
    (_re.compile(r"glm|zhipu", _re.I), "Zhipu"),
    (_re.compile(r"ernie|wenxin|baidu", _re.I), "Baidu"),
    (_re.compile(r"doubao", _re.I), "ByteDance"),
    (_re.compile(r"hunyuan|tencent", _re.I), "Tencent"),
    (_re.compile(r"copilot|microsoft|bing", _re.I), "Microsoft"),
    (_re.compile(r"perplexity", _re.I), "Perplexity"),
    (_re.compile(r"danus|rethlas|aletheia|archon|aristotle|xiaozhua|"
                 r"proof\s*council", _re.I), "Math-agent systems"),
]

# Tools that operate as autonomous/agentic systems (vs. chat assistants).
AGENTIC_RE = _re.compile(
    r"claude\s*code|codex|cursor|windsurf|copilot|devin|danus|rethlas|manus|"
    r"archon|aletheia|aristotle|proof\s*council|alphaevolve|funsearch|"
    r"co-?scientist|agent", _re.I)


def provider_of(tool: str) -> str | None:
    """Provider bucket for a disclosed tool string; None = non-LLM tool
    (excluded from the provider chart)."""
    if NON_LLM_RE.search(tool):
        return None
    for pat, provider in PROVIDER_RULES:
        if pat.search(tool):
            return provider
    return "Other/unclear"


def _kw_chips(tier: str) -> str:
    return "".join(f'<span class="kw">{html.escape(KW_DISPLAY.get(t.name, t.name))}</span>'
                   for t in lexicon.TERMS if t.tier == tier)


KEYWORDS_DETAILS = f"""
<details><summary>Which keywords does the scanner look for?</summary>
<div class="body">The scanner flags papers whose LaTeX source mentions any of
the terms below (with context rules that suppress false positives such as
person names, affiliations, or mathematical notation). Only snippets matching
the <b>AI assistants/agents</b> and <b>generic AI phrasing</b> groups are read
and classified by a language model; proof-assistant, computer-algebra, and
ML-method terms are tracked for context and enter the disclosure statistics
only when they co-occur with those groups — this is NOT a census of proof
assistants or computer algebra. Only statements that the authors themselves
used a tool count as disclosures.<br>
<b>AI assistants and agents:</b><div class="kwgrid">{_kw_chips('llm')}</div>
<b>Generic AI phrasing:</b><div class="kwgrid">{_kw_chips('generic')}</div>
<b>Machine-learning methods:</b><div class="kwgrid">{_kw_chips('ml')}</div>
<b>Proof assistants:</b><div class="kwgrid">{_kw_chips('prover')}</div>
<b>Computer algebra and math software:</b><div class="kwgrid">{_kw_chips('cas')}</div>
</div></details>
"""

def limitations_card(*, pct_unknown, n_v1, n_v1i, n_later, n_unknown,
                     n_au, n_cert, n_fuzzy, n_nonmatch, n_pdferr, n_unkv,
                     n_unresolved, n_frame, b_lo, b_hi,
                     isolate=1, code_pristine=True) -> str:
    """Known-limitations card. Bullets that report a problem render only
    when the problem actually exists in the current build (owner request
    2026-08-14: no zero-count complaint paragraphs)."""
    bullets = ["""<li><b>No human-validated error correction yet.</b> All rates are raw
automated-classifier output. A blinded human annotation study is in progress
(calibration round); until it completes, precision and miss rates are
unknown and the displayed uncertainty bands cover sampling only.</li>"""]
    if n_later or n_unknown:
        bullets.append(f"""<li><b>Source-version mixture.</b> For {pct_unknown}% of scanned papers the
analyzed text is a bulk-archive snapshot of an <i>unknown</i> revision
(possibly, but not necessarily, later than the first submission; {n_v1:,}
papers are fetched pinned v1, {n_v1i:,} inferred v1 from single-version
metadata, {n_later:,} known later, {n_unknown:,} unknown). Disclosures added
or removed in revisions can therefore blur the monthly attribution.</li>""")
    elif n_v1i:
        bullets.append(f"""<li><b>Source versions.</b> Analyzed text is the first submitted version
(v1) for every scanned paper: {n_v1:,} fetched as pinned v1 and {n_v1i:,}
single-version papers whose only version is v1.</li>""")
    if n_fuzzy or n_nonmatch or n_pdferr or n_unkv:
        bullets.append(f"""<li><b>Rendered-evidence certification is incomplete.</b> Of the {n_au:,}
papers counted as disclosing, only {n_cert:,} have their evidence quote
verified verbatim in the arXiv-compiled PDF. {n_fuzzy:,} have only a fuzzy
match (queued for review); {n_unkv:,} cannot be checked until their source
version is pinned; {n_nonmatch:,} have a known version whose quote did
<i>not</i> match the compiled PDF; {n_pdferr:,} had PDF retrieval/extraction
errors. Counted disclosures may include text that never appeared in the
published paper.</li>""")
    if n_unresolved:
        bullets.append(f"""<li><b>Coverage gaps.</b> {n_unresolved:,} of {n_frame:,} cohort papers are
unresolved (not scanned, awaiting or failing classification, or excluded by
evidence gates). <i>Conditional on treating the model labels as correct</i>,
the raw classifier-positive rate would be {b_lo}% if all unresolved papers
are negative and {b_hi}% if all are positive. Because classifier error rates
are unknown, this range is NOT a bound on true disclosure prevalence.</li>""")
    if not isolate or not code_pristine:
        bullets.append("""<li><b>Classifier execution.</b> The current classification run processed
papers in shared batches (not isolated per paper) or from a non-pristine
code state; it will be re-run under the stricter release contract before
any frozen release.</li>""")
    bullets.append("""<li><b>What is measured.</b> Openly stated, scanner-visible author
disclosure of generative-AI/LLM assistance, as retrieved by our llm/generic
search-term protocol — not actual AI use, and not comprehensive for
prover/CAS/ML-only tools, which sit outside this headline number. The rate
is jointly driven by use, disclosure norms, and our instrument's
sensitivity.</li>""")
    return ('<div class="card" id="limitations">'
            '<h2>Known limitations of the current data</h2>\n'
            '<p class="sub">We publish this prototype for inspection before '
            'validation is complete; these are the first-order caveats every '
            'number above inherits.</p>\n'
            '<ul style="margin:6px 0 2px 18px;padding:0;font-size:14.5px;'
            'line-height:1.55">\n' + "\n".join(bullets) + "\n</ul></div>")

METHODS_DETAILS = """
<details id="methods"><summary>Data sources, coverage, and methods</summary>
<div class="body">
<b>Submission counts</b> come from arXiv's public metadata interface
(OAI-PMH), covering every paper whose primary category is math.*, from August
2023 through <b>{cutoff}</b> (the exact data cutoff — the last shown week/month
may be partial); dates are each paper's first-version submission date.<br><br>
<b>Disclosure analysis</b> covers the {n_frame:,} math-primary papers submitted
{cohort}. Full text (LaTeX source; extracted PDF text for the few
PDF-only submissions) was retrieved politely from arXiv, and {n_scanned:,} of
them have a verified complete scan (per-paper ledger). The remaining
{n_failed:,} are not covered by the selected scan: the large majority were
fetched but are not part of this version-pinned scan run (their pinned first
versions are being acquired now for a fuller rebuild); a small remainder had
scan or retrieval errors. All of them are reported as unknown rather than
counted as non-disclosing. Keyword scan + LLM
classification as described above; development checks so far: 13/13 on a
selected human-labeled pilot set, 28 of 29 in-frame entries of an external
list of known LLM-assisted math papers flagged, and an audit of 200
scanner-negative papers produced 2 machine flags (one clear miss, one
arguably out-of-scope methodology use). These are indicative development
checks pending human adjudication, not validated precision/recall estimates.
Classifier error, not sampling, is the dominant uncertainty in all figures
shown.
<br><br>
<b>Provenance:</b> {provenance}.
<br><br>
<b>AI use in this project:</b> this project both measures and uses AI.
Claude Code (Claude Fable 5, Anthropic) generated pipeline/website code,
conducted data retrieval and analysis runs, and assisted with design and
choice of key metrics. The codex CLI (GPT-5.6 Sol, OpenAI) performed
iterative rounds of independent code and methodology review (twelve to
date) and the exploratory bulk snippet classification; gpt-5.6-luna
(OpenAI API) performed the v1-pinned classification. The human owner retained final responsibility and sign-off
on all scientific-validity decisions and performed the human annotation.
<br><br>
<b>Funding:</b> this work was supported by an unrestricted gift from Google
Ireland Limited to ETH Zurich, supporting work related to "Research on
Evals", administered through the ETH Zurich Foundation, and by the Swiss
National Science Foundation grant 10009122, "Beyond Benchmark Scores:
Analyzing AI Reasoning on Research-Level Mathematics". J.S. was also
supported by SwissMAP.
<br><br>
This page shows aggregate statistics only — no per-paper listings.
Full pipeline code, the validation protocol, and aggregate validation
results: ArxivObservatory repository (in preparation; per-paper validation
records stay restricted). Generated {generated}.
</div></details>
"""

RATE_CONTROLS_JS = """
window.addEventListener("load", function () {
  var ctl = document.getElementById('rate-ctl');
  var wrap = document.getElementById('rchart');
  var chipsEl = document.getElementById('rate-chips');
  var twrap = document.getElementById('rtablewrap');
  if (!ctl || !wrap || !chipsEl || typeof SERIES === 'undefined') return;
  var state = { h: 0, g: 'w', view: 'chart', subf: 'All math' };
  var GNAME = { d: 'daily', w: 'weekly', m: 'monthly' };

  var subfields = ['All math'].concat(
    Object.keys(SERIES.monthly).filter(function (k) {
      return k !== 'All math'; }).sort());
  subfields.forEach(function (name) {
    var b = document.createElement('button');
    b.className = 'chip';
    b.setAttribute('aria-pressed', String(name === state.subf));
    b.style.setProperty('--c', name === 'All math' ? 'var(--ink)' : 'var(--s1)');
    var dot = document.createElement('span'); dot.className = 'dot';
    b.append(dot, document.createTextNode(name));
    if (typeof CATNAMES !== 'undefined' && CATNAMES[name]) b.title = CATNAMES[name];
    b.onclick = function () {
      state.subf = name;
      if (name !== 'All math') state.g = 'm';
      render();
    };
    chipsEl.appendChild(b);
  });

  function rows() {
    var s = (SERIES[GNAME[state.g]] || {})[state.subf] || [];
    if (!state.h) return s;
    var per = state.g === 'd' ? state.h
            : state.g === 'w' ? Math.ceil(state.h / 7)
            : Math.round(state.h / 30.44);
    return s.slice(-per);
  }

  function syncButtons() {
    ctl.querySelectorAll('button[data-h]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(+b.getAttribute('data-h') === state.h));
    });
    ctl.querySelectorAll('button[data-g]').forEach(function (b) {
      var g = b.getAttribute('data-g');
      b.disabled = state.subf !== 'All math' && g !== 'm';
      b.setAttribute('aria-pressed', String(g === state.g));
    });
    ctl.querySelectorAll('button[data-view]').forEach(function (b) {
      b.setAttribute('aria-pressed',
        String(b.getAttribute('data-view') === state.view));
    });
    chipsEl.querySelectorAll('.chip').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.textContent === state.subf));
    });
  }

  function renderTable(rs) {
    var h = '<table><tr><th>' + (state.g === 'w' ? 'Week of'
            : state.g === 'm' ? 'Month' : 'Date') +
            '</th><th>papers</th><th>author-use</th><th>rate</th></tr>';
    rs.forEach(function (r) {
      h += '<tr><td>' + r[0] + '</td><td>' + r[1] + '</td><td>' + r[2] +
           '</td><td>' + (100 * r[3]).toFixed(1) + '%</td></tr>';
    });
    twrap.innerHTML = h + '</table>';
  }

  function render() {
    syncButtons();
    var rs = rows();
    twrap.style.display = state.view === 'table' ? 'block' : 'none';
    wrap.style.display = state.view === 'chart' ? 'block' : 'none';
    if (!rs.length) return;
    if (state.view === 'table') { renderTable(rs); return; }
    var W = 980, H = 260, L = 46, R = 14, T = 12, B = 26;
    var iw = W - L - R, ih = H - T - B;
    var top = Math.max.apply(null, rs.map(function (r) { return r[3]; })) * 1.15
              || 1;
    var X = function (i) { return L + (rs.length < 2 ? iw / 2
                                       : i * iw / (rs.length - 1)); };
    var Y = function (v) { return T + ih * (1 - v / top); };
    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.setAttribute('role', 'img');
    var step = top > 0.12 ? 0.05 : (top > 0.05 ? 0.02 : 0.01);
    for (var v = 0; v <= top; v += step) {
      var g1 = document.createElementNS(ns, 'line');
      g1.setAttribute('x1', L); g1.setAttribute('x2', L + iw);
      g1.setAttribute('y1', Y(v)); g1.setAttribute('y2', Y(v));
      g1.setAttribute('stroke', 'var(--grid)');
      g1.setAttribute('stroke-width', '1');
      svg.appendChild(g1);
      var t1 = document.createElementNS(ns, 'text');
      t1.setAttribute('x', L - 6); t1.setAttribute('y', Y(v) + 4);
      t1.setAttribute('text-anchor', 'end'); t1.setAttribute('class', 'axis');
      t1.textContent = (100 * v).toFixed(step < 0.02 ? 1 : 0) + '%';
      svg.appendChild(t1);
    }
    // owner decision 2026-08-14: census, no sampling bands
    var line = document.createElementNS(ns, 'path');
    line.setAttribute('d', 'M' + rs.map(function (r, i) {
      return X(i).toFixed(1) + ' ' + Y(r[3]).toFixed(1); }).join(' L'));
    line.setAttribute('fill', 'none'); line.setAttribute('stroke', 'var(--s1)');
    line.setAttribute('stroke-width', '2');
    line.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(line);
    var lblStep = Math.max(1, Math.floor(rs.length / 12));
    rs.forEach(function (r, i) {
      if (i % lblStep) return;
      var t2 = document.createElementNS(ns, 'text');
      t2.setAttribute('x', X(i).toFixed(1)); t2.setAttribute('y', H - 6);
      t2.setAttribute('text-anchor', 'middle'); t2.setAttribute('class', 'axis');
      t2.textContent = rs.length > 30 ? r[0].slice(0, 7) : r[0].slice(5);
      svg.appendChild(t2);
    });
    var cr = document.createElementNS(ns, 'line');
    cr.setAttribute('id', 'rcross'); cr.setAttribute('x1', 0);
    cr.setAttribute('x2', 0); cr.setAttribute('y1', T);
    cr.setAttribute('y2', T + ih); cr.setAttribute('stroke', 'var(--axis)');
    cr.setAttribute('stroke-width', '1');
    cr.setAttribute('stroke-dasharray', '3 3');
    cr.setAttribute('visibility', 'hidden');
    svg.appendChild(cr);
    wrap.replaceChildren(svg);
    // keep the hover tooltip in sync with the visible view
    RATE = { weeks: rs.map(function (r) { return r[0]; }),
             rates: rs.map(function (r) { return r[3]; }),
             los: rs.map(function (r) { return r[4]; }),
             his: rs.map(function (r) { return r[5]; }),
             ns: rs.map(function (r) { return r[1]; }) };
  }

  ctl.addEventListener('click', function (ev) {
    var b = ev.target.closest('button');
    if (!b || b.disabled) return;
    if (b.hasAttribute('data-h')) state.h = +b.getAttribute('data-h');
    if (b.hasAttribute('data-g')) state.g = b.getAttribute('data-g');
    if (b.hasAttribute('data-view')) state.view = b.getAttribute('data-view');
    render();
  });
  syncButtons();

  // "Disclosure breakdown" card: its own aggregation-window control
  var agg = document.getElementById('agg-ctl');
  if (agg) {
    agg.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b) return;
      agg.querySelectorAll('button').forEach(function (o) {
        o.setAttribute('aria-pressed', String(o === b));
      });
      var h = b.getAttribute('data-ah');
      document.querySelectorAll('.hview').forEach(function (v) {
        v.style.display = v.getAttribute('data-h') === h ? '' : 'none';
      });
    });
    // expansion state of the Further-analysis box is global across windows
    var syncing = false;
    document.querySelectorAll('.hview > details').forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (syncing) return;
        syncing = true;
        document.querySelectorAll('.hview > details').forEach(function (o) {
          o.open = d.open;
        });
        syncing = false;
      });
    });
  }
});
"""

RATE_HOVER_JS = """
window.addEventListener("load", function () {
  // delegate to the wrapper so the chart can be re-rendered by the controls
  var wrap = document.getElementById('rchart') ||
             document.querySelector('#disclosures');
  var tip = document.getElementById('rtip');
  if (!wrap || !tip) return;
  wrap.addEventListener('mousemove', function (ev) {
    var svg = wrap.querySelector('svg');
    var cross = wrap.querySelector('#rcross');
    if (!svg) return;
    var r = svg.getBoundingClientRect();
    var vx = (ev.clientX - r.left) / r.width * 980;
    var i = Math.round((vx - 46) / 920 * (RATE.weeks.length - 1));
    if (i < 0 || i >= RATE.weeks.length) { tip.style.display = 'none';
      if (cross) cross.setAttribute('visibility', 'hidden'); return; }
    if (cross) { var cx = 46 + i * 920 / (RATE.weeks.length - 1);
      cross.setAttribute('x1', cx); cross.setAttribute('x2', cx);
      cross.setAttribute('visibility', 'visible'); }
    // DOM construction with textContent only — no innerHTML sinks (LB-08)
    tip.replaceChildren();
    var mk = function (cls, text) {
      var el = document.createElement('div'); el.className = cls;
      el.textContent = text; return el; };
    var row = function (nm, val) {
      var r = document.createElement('div'); r.className = 'row';
      var a = document.createElement('span'); a.className = 'nm'; a.textContent = nm;
      var b = document.createElement('span'); b.className = 'val'; b.textContent = val;
      r.append(a, b); return r; };
    tip.append(
      mk('d', 'Week of ' + RATE.weeks[i]),
      row('disclosure rate', (100 * RATE.rates[i]).toFixed(1) + '%'),
      row('papers', String(RATE.ns[i])));
    tip.style.display = 'block';
    tip.style.left = (ev.clientX + 14) + 'px';
    tip.style.top = (ev.clientY + 12) + 'px';
  });
  wrap.addEventListener('mouseleave', function () { tip.style.display = 'none';
    var cross = wrap.querySelector('#rcross');
    if (cross) cross.setAttribute('visibility', 'hidden'); });
  var names = document.querySelectorAll('svg text');
  names.forEach(function (t) {
    var m = (t.textContent || '').match(/^(math\\.[A-Z]{2})/);
    if (m && CATNAMES[m[1]]) {
      var ti = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      ti.textContent = CATNAMES[m[1]];
      t.appendChild(ti);
    }
  });
  document.querySelectorAll('.chip').forEach(function (c) {
    var m = (c.textContent || '').match(/math\\.[A-Z]{2}/);
    if (m && CATNAMES[m[0]]) c.title = CATNAMES[m[0]];
  });
});
"""
