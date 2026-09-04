# Prior art survey (v2, 2026-07-15)

Merged from a light Claude web pass and a comprehensive ChatGPT Pro deep search (both
2026-07-15). Organized by project aspect; each section ends with the assessed gap.

**Headline correction vs v1:** the project should *not* be pitched as the first AI-use count on
arXiv, the first Pangram run on arXiv, or the first LLM audit of math papers — all three have
close precedents (details below). The defensible novelty is the **integration**: a
mathematics-specific, longitudinal, *version-aware*, human-validated observatory spanning the
whole tool spectrum with an epistemic-role taxonomy, plus a separately validated error audit.
The deep pass suggested the umbrella title "Computational Mediation in Mathematics"; the
project name chosen is **ArxivObservatory**.

## A. Disclosed / acknowledged AI use

- **Kousha 2024** ([Scientometrics](https://link.springer.com/article/10.1007/s11192-024-05193-y)) —
  1,759 publications with ChatGPT acknowledgments through Aug 2024: ~80% editing/proofreading,
  5.3% non-editorial research support, 3.5% drafting.
- **"Patterns and Purposes"** ([arXiv:2502.00632](https://arxiv.org/abs/2502.00632),
  **v2** — v2 states it corrects data issues in v1) — **135** AI declarations among
  **8,633** articles across 27 categories; ChatGPT **73.3%** of declared tools;
  readability **57.8%**, grammar checking **19.3%**. (Cite the exact version;
  earlier drafts of this file quoted v1's superseded numbers.)
- **Survey evidence (self-selected):** 81% of 816 respondents report LLM use
  somewhere in their workflow ([arXiv:2411.05025](https://arxiv.org/html/2411.05025v1)).
  Caveat: 107,346 verified authors were emailed (~1.6% click-through), the final
  sample is ~40% computer science and 79% men — respondent-reported behavior, NOT
  a population denominator or a quantitative disclosure-gap estimate.
- **Foundation-model documented-use study** ([arXiv:2511.21739](https://arxiv.org/pdf/2511.21739)) —
  268,694 papers; classifies documented use/customization of foundation models
  (a broad family including vision models) from in-text evidence; mathematics
  at **1.3% in 2024**. (A different operational measure than generative-AI
  disclosure — misses uncited proofreading/coding help. Keep estimands separate.)
- **DAISY** ([arXiv:2604.02760](https://arxiv.org/html/2604.02760v1)) — structured AI-disclosure
  interface; its schema (where used, how extensively, who is responsible) is a ready-made input
  for our annotation taxonomy.
- **arXiv policy** ([Jan 2023 blog](https://blog.arxiv.org/2023/01/31/arxiv-announces-new-policy-on-chatgpt-and-similar-tools/)):
  significant tool use should be reported per subject-area norms. Consequence: "failure to
  disclose" is not an objective label — what counts as "significant" varies.
- **Case study of the new genre:** an algebraic-geometry paper with a full appendix documenting
  AI-assisted conjecture discovery and proof ([arXiv:2512.14575](https://arxiv.org/html/2512.14575v1)) —
  qualitatively unlike a one-line editing acknowledgment; motivates the epistemic-role taxonomy.
- Earlier baselines: **Andrew Gray** ([arXiv:2403.16887](https://arxiv.org/abs/2403.16887)) —
  estimates LLM-assisted *writing* from shifts in LLM-associated keyword frequencies;
  NOT a population study of explicit disclosures, so its figures are a different
  estimand than ours; LSE Impact
  [PMC acknowledgment analysis](https://blogs.lse.ac.uk/impactofsocialsciences/2025/09/10/what-do-researchers-acknowledge-chatgpt-for-in-their-papers/).

**Gap (identified in this scoping search; not a systematic review):** no
longitudinal study found that is simultaneously math-restricted,
subfield-representative, cross-tool (LLM + CAS + code + provers), multi-label by research role,
version-aware, and built on a validated extraction pipeline. Key novel axis: **epistemic
impact** — cosmetic / supportive / result-bearing.

## A'. Software, CAS, and formalization tracking (don't reinvent)

- **SoMeSci** ([gold-standard corpus](https://data.gesis.org/somesci/)) — 3,756 annotated
  software mentions in 1,367 articles, κ = .82; **Softcite**
  ([recognizer](https://github.com/softcite/software-mentions)) — trained software-mention NER.
  Adapt these + math-specific dictionaries rather than building from raw keywords.
- **swMATH / zbMATH Open** ([overview](https://www.fiz-karlsruhe.de/en/produkte-und-dienstleistungen/swmath)) —
  ~39,500 packages linked to publications; reports **~15% of math publications use/refer to
  mathematical software**. Baseline + validation resource.
- **Scienceography** ([arXiv:1202.2638](https://arxiv.org/abs/1202.2638)) — large-scale arXiv
  LaTeX-source mining (math + CS) dates to 2012.
- **Lean ecosystem:** research-level formalizations proliferating
  ([project list](https://leanprover-community.github.io/lean_projects.html)); **ArXivLean**
  benchmark ([MathArena](https://matharena.ai/arxivlean/)) — agents formalize statements from
  fresh arXiv papers, all models <20%; formalization already catches real errors (Stacks Project
  error found at a [Durham workshop](https://leanprover-community.github.io/blog/posts/durham-algebraic-geometry-workshop/)).

**Gap:** a mention-count of Lean would be modest. The interesting integrated question: **how has
the locus of computational assistance shifted** — from calculation/examples toward
conjecturing, proof construction, proof criticism, and formal verification?

## B. Undisclosed / detector-inferred AI writing

- **Liang et al.** (now [Nature Human Behaviour 2025](https://www.nature.com/articles/s41562-025-02273-8)) —
  1,121,912 papers, word-frequency method: up to 22% of CS and **up to 9% of math** papers
  LLM-modified by end of window. Population-level, not per-paper.
- **Closest direct precedent** ([arXiv:2601.17036](https://arxiv.org/html/2601.17036v1), Jan 2026) —
  124,461 arXiv papers incl. 36k math, 2020–2025; aggregate "Alpha" estimator on the full corpus
  + **Pangram on 100 papers/month/domain**. Pre-LLM false-positive calibration **only on CS
  2020–2022** — the math calibration is explicitly missing.
- **Pangram × alphaXiv integration**
  ([announcement](https://www.linkedin.com/posts/pangramlabs_pangram-is-powering-ai-detection-on-alphaxiv-activity-7450590532319227905-0bkL)) —
  viewer-level AI-passage highlighting across arXiv. "Run Pangram over arXiv" is an announced
  product capability, **not novel as a standalone project**.
- **Disclosure × detector comparison exists in medicine**
  ([arXiv:2603.19316](https://arxiv.org/html/2603.19316v1)) — 7,251 articles, 195
  detector-positive, only 6 of those disclosed; conversely 15 disclosed, 6 crossed the detector
  threshold. Template *and* cautionary tale for interpretation.
- **Detector reliability:** Pangram best-in-class in an
  [NBER evaluation](https://www.nber.org/papers/w34223) (only tool meeting FPR ≤ 0.005 without
  accuracy loss); its **vendor-authored**
  [technical report](https://arxiv.org/html/2402.14873) Table 6 reports FPR
  **0.04% (4e-4) on held-out Scientific Papers** (domain not identified as
  arXiv; the ~1e-5 figure is for News — an earlier draft of this file
  misquoted it 40-fold); but **RAID**
  ([arXiv:2405.07940](https://arxiv.org/html/2405.07940v1)) shows detectors degrade under unseen
  models/decoding/attacks, and iterative paraphrasing defeats them
  ([arXiv:2605.19516](https://arxiv.org/abs/2605.19516)). Also:
  [Pangram biomedical sweep](https://www.biorxiv.org/content/10.64898/2026.01.01.697311v1)
  (12.4% of 2025 papers ≥1 AI passage) and the
  [ICLR-reviews study](https://www.pangram.com/blog/pangram-predicts-21-of-iclr-reviews-are-ai-generated) (21%).

**Gap (narrowed but real):** (i) Pangram false-positive calibration on **pre-LLM mathematical
prose** (formula-dense, translation-heavy) + controlled positives (grammar-only edit,
translation, rewrite) by section type; (ii) the math-specific disclosure × detector cross-tab,
restricted to writing-related disclosures a text detector could plausibly see. **Framing:**
say "detector-inferred LLM modification," never "uncredited use" — a detector cannot establish
a disclosure violation.

## C. Errors in the mathematical literature

- **Historical base rate is folklore:** Lamport's summary of 84 Mathematical Reviews reports in
  one ring-theory area (≈1/3 with an incorrect theorem or proof) — small, nonrandom, motivating
  only.
- **"To Err Is Human"** ([arXiv:2512.05925](https://arxiv.org/html/2512.05925v1)) — GPT-5 checker
  on 2,500 published AI papers: ≥1 flag in 99.2%; potentially substantive issues in 23.8–36.0%
  by venue; human check of 316 flags → **83.2% precision**; recall on seeded errors 60% (66.7%
  for math/formula). Methodological template; not pure math.
- **Mass math audit already attempted, badly** ([arXiv:2511.10543](https://arxiv.org/html/2511.10543v1),
  "From Euler to Today") — claims 37k (abstract) vs 65k (conclusion) papers audited, internally
  inconsistent rates, no representative expert adjudication. Shows the niche is active *and*
  that the validation-first version is the missing contribution.
- **ArxivMathGradingBench** ([arXiv:2605.20531](https://arxiv.org/html/2605.20531), Jun 2026) —
  benchmark of **35 research papers containing 40 known errors** (papers whose
  authors later corrected identified errors); exactly the version-history
  gold-standard idea. Their caveat: labels only cover *known* errors, so
  apparent false positives may be real but previously unknown errors.
- **Cheap objective error classes first:** hallucinated-references audit across 111M citations
  ([arXiv:2605.07723](https://arxiv.org/abs/2605.07723)) — start with cheaply verifiable claims.
- Context: SPOT benchmark ([arXiv:2505.11855](https://arxiv.org/abs/2505.11855), 2025-era models
  poor at verification); Black Spatula / [YesNoError](https://yesnoerror.com/whitepaper) (breadth
  without validation); DeepMind Aletheia single cases.

**Gap (highest value, hardest):** a **representative, expert-confirmed lower bound** on
substantive-error prevalence in pure math, under a preregistered protocol, with severity
levels reported as cumulative thresholds (not one "X% wrong" number), a known-positive
benchmark (errata/version diffs) separate from the prevalence sample, and blinded adjudication.

## D. Posting-pattern metascience

Established territory (use as denominators/covariates, not novelty): arXiv
[submission stats](https://info.arxiv.org/help/stats/2021_by_area/index.html); Scienceography;
field-dynamics studies ([arXiv:2107.03749](https://arxiv.org/abs/2107.03749)); Dekoninck's
math-submissions-~20%-above-trend chart — **secondary coverage only, not
independently reproduced; do not cite as a finding until re-derived from
official metadata with code and uncertainty**
([coverage](https://officechai.com/ai/mathematical-articles-on-arxiv-have-risen-20-over-trend-in-2026/));
arXiv's [Dec 2025 math endorsement-policy change](https://blog.arxiv.org/2025/12/10/updated-endorsement-policy-for-arxiv-mathematics/).
Open link: joining the volume surge to paper-level tool-use data — but beware confounding
(paper length, team size, subfield mix shifts).

## E. Data access (solved; constraints noted)

- [OAI-PMH](https://info.arxiv.org/help/bulk_data.html) is arXiv's preferred metadata harvest
  (daily updates); Kaggle for machine-readable dumps; [S3 requester-pays](https://info.arxiv.org/help/bulk_data_s3.html)
  for PDFs + source (~500MB tar chunks with manifests/checksums; ~9.2 TB total as of Apr 2025,
  +~100 GB/month). arXiv explicitly asks not to crawl article URLs.
- **Licensing:** arXiv's default license does not allow third-party redistribution of full
  text — release annotations, IDs, hashes, and code; link back to arXiv.
- **Source-file privacy:** ~27% of uploaded submission **bytes** on average are unnecessary residue, incl. comments
  ([arXiv:2601.11385](https://arxiv.org/abs/2601.11385), "X-raying the arXiv"). Default: ignore
  non-rendered comments and residual files. Never execute submission TeX/code; static
  extraction in a sandbox.
