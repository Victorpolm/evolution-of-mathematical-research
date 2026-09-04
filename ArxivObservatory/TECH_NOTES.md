# Technical notes: pipeline, statistics, costs, ethics (v2, 2026-07-15)

Companion to `PITCH.md` / `PRIOR_ART.md` / `pitch.tex`. v2 incorporates the ChatGPT Pro deep
search: version-awareness, recall estimation, epistemic-impact coding, the 0–5 severity scale,
the two-sample error-audit design, and detector/licensing/privacy protocol details.

Prototype status: `arxiv_ai_ack_scan.py` + `WORKFLOW.md` implement the .eml → new-papers →
download → keyword-scan → manual-review loop for math.AG (129 papers, 20 candidates, 13 true
disclosures).

## 0. Framing decisions (locked in)

- Project name: **ArxivObservatory** (subtitle: an inventory of tool use, disclosure, and
  reliability in mathematics). "Computational Mediation in Mathematics" stays in reserve as a
  paper-title candidate.
- Three estimands, kept conceptually separate throughout: (1) explicit disclosure by role,
  (2) population-level linguistic estimates, (3) document/passage-level detector results.
  They legitimately differ; never collapse them into one "AI use" number.
- Terminology: "**detector-inferred LLM modification**," not "uncredited AI use." arXiv policy
  requires reporting *significant* tool use per community norms, so non-disclosure is not an
  objective violation label.
- **Unit of analysis: the paper-version**, with paper-level rollups ("ever disclosed",
  "disclosed in v1", "disclosure added later"). Version histories are a core asset, not a
  nuisance: disclosures added after feedback, artifacts appearing in later versions, detector
  scores across revisions, disclosure edits co-occurring with error corrections.
- Three work packages, separately publishable: **WP1** disclosed assistance observatory;
  **WP2** calibrated detector study; **WP3** reliability audit (separate paper — different
  estimand, validation burden, ethics, team).

## 1. Server-friendly data acquisition

Never crawl arxiv.org article URLs (arXiv's explicit request). The polite stack:

| Need | Source | Cost |
| --- | --- | --- |
| Sampling frame (IDs, titles, abstracts, categories, dates, authors, **version history**) | OAI-PMH (arXiv's preferred method, daily updates); Kaggle metadata dump as bootstrap | free |
| Full text of *sampled* papers, bulk | `s3://arxiv/src/` + `s3://arxiv/pdf/` requester-pays (manifests + checksums; ~9.2 TB total Apr 2025, +100 GB/mo); GCS mirror | bandwidth only; ~free if processed in us-east-1 |
| Small targeted pulls (≤ few hundred papers) | `export.arxiv.org` with ≥3 s between requests (prototype behavior) | free |
| Daily incremental discovery | subject-class mailing .eml files (current approach) or RSS/OAI | free, zero load |

Scale reality: source ≈1–2 MB/paper → a 10k-paper stratified sample ≈ 20 GB. S3 chunks are
grouped by month, aligning with month-stratified sampling.

Handling protocol: record checksum, arXiv ID, version, retrieval date, license per item; cache
immutably. Prefer TeX source for extraction; PDF text as fallback + rendered-location check.
**Never execute submission TeX/code** — static extraction in a sandbox. **Do not redistribute
full text** (default arXiv license forbids it): release annotations, IDs, hashes, code.
**Privacy default:** ignore non-rendered `%`-comments and residual source files (cf. "X-raying
the arXiv": ~27% of submission bytes on average are unnecessary residue) unless a specific,
ethically cleared question requires them.

## 2. WP1 — extraction pipeline and taxonomy

Stage 0 — deterministic (prototype exists, extend):
- Acknowledgment/disclosure region extraction from LaTeX: `\section*{Acknowledg...}`,
  `\thanks{}`, footnotes, appendices, plus new genres from the pilot: "AI Usage", "Usage of
  LLM's", "Declarations", "Tool disclosure". Also methods-style statements inside proofs
  ("verified with Magma"), which conventional acknowledgment mining misses.
- **Reuse existing software-mention tooling** — Softcite recognizer, SoMeSci gold corpus — plus
  math-specific dictionaries; swMATH/zbMATH links as external validation (~15% of math
  publications reference software: a baseline our CAS numbers should be consistent with).
- Tool lexicon tiers: **LLM/agent** (ChatGPT, GPT-*, Claude, Gemini, Copilot, Codex, DeepSeek,
  Grok, "language model", …), **prover** (Lean, mathlib, Coq/Rocq, Isabelle, Agda,
  "formalized"), **CAS** (Sage, Magma, Mathematica, Maple, GAP, PARI/GP, Macaulay2, Singular,
  OSCAR, polymake, SnapPy), **numerical/custom code**, **search/retrieval**, **generic**
  (computer-assisted, software package).
- False-positive lexicon (from pilot): *Université Claude Bernard Lyon 1*, *Séminaire Claude
  Chevalley*, `G(T)`/GPT as notation, GAP the concept vs the software, Sage as a name. Pre-2022
  control years give the empirical FP rate of the whole lexicon.

Stage 1 — small LLM classifies each hit-with-context into the taxonomy.
Stage 2 — frontier model or human adjudicates disagreements / low confidence.

Taxonomy (multi-label per paper-version; draft, **freeze before the main temporal run** so
older strata aren't searched less sensitively than recent ones):
- **Tool class:** LLM/agent / specialized math AI / CAS / numerical software / custom code /
  proof assistant / ATP / search-retrieval / visualization / translation tool.
- **Research role:** literature search; ideation; conjecture generation; examples &
  counterexamples; proof discovery; proof completion; proof criticism/checking; symbolic
  calculation; numerical calculation; code generation; formalization; writing/editing/
  translation; figures/artifacts; referee response.
- **Epistemic impact (the headline axis):** *cosmetic* (grammar, style, translation, LaTeX) /
  *supportive* (search, code, calculations, examples, criticism) / *result-bearing*
  (conjecture, decisive proof idea, retained proof step, counterexample, formal verification
  of a substantive result).
- **Evidence type:** explicit acknowledgment / methodological appendix / methods statement /
  software citation / repository or formal artifact / detector signal only.
- **Disclosure quality** (DAISY-informed): tool named; model+version; task; location; extent;
  prompts/logs; artifact available; human-verification statement.
- **Polarity:** positive use / explicit non-use / topic-only mention / false positive.

## 3. Validation (make-or-break)

- **Gold corpus** (~200–400 paper-versions): compare (a) deterministic parser, (b) small-LLM
  cascade, (c) frontier-agent full-paper read, (d) human labels — on the same held-out sample.
  Report **class-specific precision and recall** ("ChatGPT" is easy; informal proof help and
  custom-code mentions are hard).
- **Recall via negative audit set:** humans (plus an independent retrieval agent) read a random
  sample of pipeline-negative papers to estimate missed disclosures. Oversample hard cases:
  unnumbered sections, footnotes, appendices, generic phrases ("AI assistant"), company-name-
  only mentions, tool use described only inside proofs, papers with no acknowledgments section.
- LLM adjudication is a second retrieval system, **not** ground truth; human labels anchor.
- Freeze taxonomy + extraction rules after development corpus; evaluate on held-out periods
  and subfields before the longitudinal claims.

## 4. Statistics

- Stratified random sampling: year (2015–present, denser post-2022) × primary math.* category ×
  version index. First serious sample: **5,000–20,000 paper-versions**. (At ~10% prevalence,
  n=1,000 → ±1.9pp at 95%; n=5,000 → ±0.8pp; extraction error dominates beyond that.)
- Prevalence corrected for classifier imperfection (Rogan–Gladen-style) using gold-set
  sensitivity/specificity; **propagate classifier uncertainty into the intervals** — with big
  corpora, binomial bars go tiny while misclassification bias stays; a bigger corpus cannot fix
  a systematically missed phrase.
- Sequential/adaptive design: running estimates with intervals; adaptively oversample
  interesting strata; **preregister the headline estimands** to keep the zooming honest.
- Covariates/denominators from metadata (free, all of arXiv): volume, paper length, author
  count, versions, cross-listing, repo links, journal-ref status. Needed because apparent
  temporal changes may reflect composition shifts.
- Confound to state up front: disclosure = use × willingness-to-disclose (norms shifted;
  policies changed). WP2 partially disentangles — the reason A and B live in one project.
- Do **not** test "does disclosed AI use cause errors" — selection effects swamp it; anything
  observed is descriptive and confounded.

## 5. WP2 — detector study

- Three indicators kept separate (§0). Detector: Pangram (best-in-class per NBER eval; its
  vendor technical report gives FPR 4e-4 on held-out scientific papers — domain not
  identified as arXiv, and 1e-5 applies only to News), but RAID + paraphrasing studies show detectors
  degrade off-distribution — hence our own calibration:
  - **Pre-LLM math controls** across subfields (the closest prior study calibrated pre-LLM FPs
    only on CS 2020–2022 — this is our wedge);
  - controlled positives from volunteer mathematicians: grammar-only editing, translation +
    edit, rewriting, generation, at varying proportions, multiple model families;
  - scored **by section type** (abstract, intro, proofs, acknowledgments, appendix) — formula-
    dense text and translated prose are the FP stress tests.
- Cross-tab detector × disclosure **restricted to writing/editing/translation disclosures** —
  a Claude-found-the-proof disclosure with fully human prose is not a detector false negative.
- Freeze and record: detector model + version, access date, threshold, extraction procedure,
  exact text supplied (commercial updates silently change results). Track detector score
  across paper versions.
- Scale: a few thousand detector-scored papers suffice **if calibration is strong**; running
  100k papers before understanding behavior on math prose yields narrow intervals around a
  biased estimate. Route: API at modest scale or collaboration (Pangram Labs has co-authored
  the ICLR, biomedical, and arXiv studies; alphaXiv integration exists — our novel ingredient
  is the disclosure pipeline + math calibration set).

## 6. WP3 — reliability audit

Estimand (preregistered): *fraction of sampled pure-math paper-versions containing ≥1
independently confirmed substantive mathematical error discoverable under the audit protocol* —
a **lower bound** (unflagged ≠ correct; adjusting by one recall number would need strong
assumptions — report recall separately from the seeded/known-positive studies).

- **Severity scale** (report cumulative thresholds, never one "X% wrong" number):
  S0 typo/notation; S1 local error, obvious repair; S2 nontrivial but repairable gap;
  S3 theorem/proposition false as stated; S4 main result materially weakened/unsupported;
  S5 central result false or paper withdrawn; U indeterminate without specialist work.
- **Two samples, strictly separate:**
  - *Known-positive benchmark* (measures rediscovery/recall, not prevalence): arXiv revision
    comments mentioning corrected proofs; journal corrigenda/errata; withdrawn papers;
    published counterexamples; author-confirmed mistakes; version-diffs where the relevant
    passage changed. ArxivMathGradingBench (35 author-corrected papers containing 40 known
    errors) is a seed + template; their caveat applies — labels cover only *known* errors,
    so apparent FPs may be real but previously unknown errors.
  - *Representative prevalence sample*: stratified random, ~100–300 papers pilot; models and
    adjudicators blinded to correction status.
- **Per-flag protocol:** model gives exact location + claim + reasoning (ideally counterexample
  or failed implication) → second independent system critiques → two mathematicians adjudicate
  independently → specialist tie-break → author contact before any per-paper publication.
- Calibration anchors: "To Err Is Human" (GPT-5 on 2,500 AI papers: 83.2% flag precision, 60%
  seeded-error recall) sets expectations; the failed mass math audit (arXiv:2511.10543) shows
  why validation-first is the contribution. Start with cheaply verifiable error classes
  (references, arithmetic, stated constants) before whole-proof correctness.
- Cross-checks: last-arXiv vs journal-version diff; errata; zbMATH/MathSciNet review texts.
- Cheap-mode pilot: team subscriptions + fixed prompt/model/refusal-handling protocol so runs
  are comparable. Binding resource is **specialist human time**, not tokens — recruit
  adjudicators with the "how many math papers are wrong?" hook.

## 7. Cost tiers (rough)

- **Tier 0 (≈ $0):** WP1 + all metadata covariates + WP3 pilot via subscriptions. Sampled
  full-text ~$1–10 bandwidth; Stage-1 classification of ~10k snippets ~$5–20.
- **Tier 1 (~$10²–10³ or collaboration):** Pangram calibration + a few-thousand-paper run.
- **Tier 2 (~$10³–10⁴ or lab credits):** frontier error hunt, 100–300 papers × ≥2 models,
  plus expert adjudication time.

## 8. Ethics / publication norms

- Aggregate reporting only; no per-paper undisclosed-AI verdicts; no "bad papers" leaderboard.
- Model flags clearly separated from confirmed findings; confirmed examples published only
  after expert and preferably author review; authors get notification + response opportunity;
  our own audit records get corrected/retracted when new evidence appears.
- Detector results framed as uncertain aggregate measurement, never misconduct evidence
  (non-native speakers post-editing with LLMs is the canonical harm case).
- Respect source privacy (§1) and licensing (annotations/hashes, not full text).

## 9. Phasing

1. **P0 (done):** math.AG 8-day pilot — 10% disclosure, taxonomy seeds, FP lexicon.
2. **P1:** OAI-PMH frame + metadata covariate analysis (free, all arXiv); extend parser (§2);
   WP1 on ~2–5k stratified paper-versions incl. pre-2022 controls; gold corpus + recall audit;
   freeze taxonomy.
3. **P2:** WP1 writeup ("Disclosed computational assistance in mathematics, 2015–2026") +
   dashboard; build math calibration corpus; approach Pangram with WP1 dataset in hand.
4. **P3:** WP2 cross-tab; WP3 known-positive benchmark + 50-paper protocol pilot; then WP3
   prevalence sample.
