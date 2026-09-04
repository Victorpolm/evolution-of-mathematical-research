# ArxivObservatory

**An inventory of tool use, disclosure, and reliability in mathematics.**
(Earlier working title from the prior-art pass: "Computational Mediation in Mathematics" —
kept in reserve as a possible paper title.)
Markdown mirror of `pitch.tex` (canonical, compiles to 1-page `pitch.pdf`), v2 2026-07-15.
Details: `PRIOR_ART.md` (literature), `TECH_NOTES.md` (pipeline/statistics/ethics).

**The phenomenon.** In an eight-day census of all new math.AG arXiv submissions (June–July
2026, n = 129), 13 papers (10%) explicitly disclosed AI assistance — from grammar polishing to
an abstract stating that the main result of the paper was obtained by a combination of AI
systems. (Internal note, not in the shared pitch: verbatim source is pilot paper [id-redacted],
abstract: "The main result of this paper was obtained by Chatgpt 5.5 pro, and the Danus system
based on the Rethlas system."; similar in [id-redacted].) Existing broad
measurements see different slices: word-frequency methods estimate up to 9% LLM-modified
*prose* in mathematics (Nature Hum. Behav. 2025), in-text-evidence mining finds 1.3%
documented foundation-model *use* in math in 2024 (arXiv:2511.21739, a broad model family
incl. vision models), and 81% of survey *respondents* (self-selected sample) report LLM use
somewhere in their workflow (arXiv:2411.05025). Different estimands, none mathematics-specific
at full-text depth. We want to measure the transition properly, while it happens.

**Questions.**

1. **Adoption and epistemic role.** How do math papers use LLMs, computer algebra, custom
   code, and proof assistants — in what role: *cosmetic* (prose, translation), *supportive*
   (search, code, computations, examples, proof criticism), or *result-bearing* (conjectures,
   retained proof steps, counterexamples, formal verification)? Evolution across time,
   subfield, and arXiv version history (disclosures added/removed between versions?).
2. **Disclosure vs. detection.** How do explicit writing-related disclosures relate to
   detector-inferred LLM modification of mathematical prose, once the detector is calibrated
   on pre-LLM mathematics and controlled positives (grammar-only edit, translation, rewrite)
   by section type?
3. **Reliability.** What lower bound does a preregistered AI-plus-expert audit place on the
   fraction of pure-math paper-versions with ≥1 independently confirmed substantive error —
   reported as cumulative severity levels, never a single "X% of papers are wrong"?

**Method.** Disclosures: deterministic parsers with application-specific keyword detection on
LaTeX sources + LLM scans + human review, cross-validated on shared gold samples so
class-specific precision *and recall* are known and prevalence estimates carry honest
uncertainty (prototyped on the pilot). AI-writing detection: Pangram on (subsets of) paper
texts, calibrated on pre-LLM mathematics and controlled positives. Error detection: frontier
review agents — and possibly the community workflow below — with independent critique and
double expert adjudication; known-positive benchmark from errata/version diffs
(cf. arXiv:2605.20531) measured separately from the blinded representative sample (~100–300
papers). All strands run on iterative stratified samples: rough picture with explicit error
bars quickly, refined as data comes in; unit of analysis is the paper-version. (Full texts via
arXiv's sanctioned bulk channels — no scraping. Implementation details in TECH_NOTES.md.)

**Positioning.** Already done elsewhere: cross-disciplinary acknowledgment counts (~80%
editing; Scientometrics 2024); population prose estimates; Pangram sampled on arXiv with
pre-LLM calibration on CS only (arXiv:2601.17036); disclosure–detector comparison in medicine
(arXiv:2603.19316); GPT-5 error audit of AI-conference papers (83% flag precision, 60% seeded
recall; arXiv:2512.05925); an unvalidated mass audit of math papers (arXiv:2511.10543).
Open — our contribution: mathematics-specific, cross-tool, version-aware taxonomy with
epistemic-role coding; detector calibration on mathematical prose; the disclosure × detection
cross-tab for math restricted to detector-visible roles; a representative, expert-confirmed
error lower bound.

**Work packages & deliverables.**
- **WP1** Disclosed-assistance observatory: open taxonomy, human-annotated gold corpus,
  validated pipeline, longitudinal estimates by subfield and role on 5,000–20,000
  paper-versions, living dashboard. (Cheapest, cleanest — start here.)
- **WP2** Calibrated detector study: pre-LLM math control corpus, controlled positives,
  section-wise FP rates, disclosure–detector overlap.
- **WP3** Reliability audit (separate paper — different estimand, ethics, team): severity
  rubric, known-error benchmark, model precision/recall studies, aggregate lower bound.
- All code + annotations open (IDs and hashes, no full-text redistribution per arXiv license).

**A community experiment.** Much of the expensive frontier-model pass could be crowd-sourced
to mathematicians who already hold model subscriptions: a website assigns you a specific arXiv
paper; you drop it into your model with a fixed prompt and paste back the conversation
share-link — optionally also ticking a few checkboxes about the paper's acknowledgments.
Share-links let us audit that the intended model and prompt were used; double-assignment and
seeded known-error papers guard against careless or adversarial contributions. Nearly free,
doubles as outreach, and gives the community a stake in the dataset.

**Practicalities & ethics.** WP1 + covariates ≈ free (metadata dumps, small models, existing
subscriptions); WP2 modest API budget or Pangram Labs collaboration; WP3 lab-credit scale,
bottlenecked by expert time. Aggregate reporting only; no per-paper accusations;
"detector-inferred LLM modification" — a measurement, never misconduct evidence.

**We are looking for.** Mathematicians across subfields for annotation and error adjudication
(a few hours each); early volunteers to pilot the community workflow; a statistics/metascience
collaborator; Pangram Labs contacts / detector expertise; compute credits.

*Contact: Johannes Schmitt — johannes.schmitt@math.ethz.ch*
