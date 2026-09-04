# Classification taxonomy — v2.8

This taxonomy classifies what an arXiv mathematics paper *explicitly
reports* about AI involvement. Its headline label identifies papers
reporting that the research team invoked an AI system for a delegated,
human-performable intellectual task — including explicitly reported
unsuccessful attempts. It does not aim to detect undisclosed use, independently
verify the report, assess research validity or policy compliance, or
determine authorship. It is the single rulebook for both the automated
classifier and human reviewers — `pipeline/taxonomy.py` is the
machine-readable copy, and a unit test keeps the two in sync.

Rules are uniform: no per-case exceptions. The examples illustrate the
rules; they never override them. Design history and rationale are at the
[end of this document](#history-and-rationale).

## Scope and unit

**In-scope AI systems** are generative-AI/LLM systems: chatbots, coding
assistants, agentic systems, and LLM-based tools. Ordinary unaided use
of proof assistants, computer-algebra systems, spellcheckers, or
conventional software is out of scope, however computational the tool —
the `formalization` category, for instance, applies only when an
in-scope AI wrote or materially assisted the formalization, never to
ordinary Lean/Coq work.

**The unit of classification is the paper (in one specific version).**
Text snippets are evidence passages, and the pipeline labels them as an
intermediate step, but every rule below is stated for — and every
published number counts — papers. One paper can disclose several uses;
the paper-level label aggregates them under the explicit rules below,
and finer per-use structure is deliberately not recorded.

**Evidence eligibility comes before classification.** Only text that a
reader of the published paper can see counts: the rendered paper, its
arXiv abstract page (including the Comments field), and ancillary files
distributed with it. Source-only material — TeX comments, `\iffalse`
blocks, text after `\end{document}` — is never classification evidence;
it is routed to a separate, ethically gated residual-artifact workflow
and receives no polarity (rule R3). The render check applies to
paper-body evidence; Comments-field evidence is eligible by its channel
(it always appears on the abstract page) and needs no separate
verification (owner decision 2026-08-14).

## Polarity — what relation does the paper have to AI?

| Polarity | Means |
|---|---|
| author_use | authors (or collaborators) invoked an AI system during THIS research to perform intellectual work of a kind humans traditionally perform themselves (writing, proofreading, translation, search, ideation, proofs, checking, code, computations, data labeling or generation, formalization), and its output entered the conduct or communication of the paper. Named exception (R5): an invocation undertaken *for* such a role counts even when its output was explicitly not used — attempted use, impact `zero_contribution` |
| non_use_statement | authors explicitly state they did NOT use AI, and no use is disclosed anywhere in the paper |
| topic_only | the AI does not stand in for the authors' own intellectual work: the paper *studies* an AI system or discusses AI as subject matter, *cites* AI-related literature, *benchmarks* models, *analyzes a system that contains* an AI component, *reuses* a pre-existing AI-produced artifact as data, or *runs* a model purely as a measuring instrument (native model statistics: embeddings, feature vectors, perplexities) |
| false_positive | the matched term is notation, a person/place name, an affiliation — not about AI |
| unclear | the paper explicitly addresses AI use for this work, but the statement cannot be interpreted (contradictory or garbled). Expected to be rare — suggestive-but-nonexplicit material is never `unclear` (rule R6) |

**Paper-level precedence.** One paper, one polarity:
`author_use` > `non_use_statement` > `topic_only` > `false_positive`.
A disclosed use anywhere makes the paper `author_use`, whatever else it
contains — in particular, a *scoped* denial ("no AI was used for the
proofs; ChatGPT polished the English") never overrides a disclosed use.
`unclear` applies when AI involvement is asserted or implied but the
relation cannot be established.

**Decision procedure** (per paper, in order):

1. Nothing about AI beyond notation or names? → `false_positive`.
2. **The delegation test** (rule R4). Does the paper disclose that the
   authors *invoked* an AI system during this research, **and** that it
   performed a *delegated human-type intellectual role* — work of a
   kind humans traditionally perform themselves — whose output entered
   the conduct or communication of the paper? Test: *a counterfactual
   exists in which the authors obtained this input by doing the work
   themselves.* If yes → `author_use`. Named exception (R5): an
   invocation undertaken *for* such a role counts even when its output
   was explicitly not used.
3. **The explicit-statement rule (rule R6).** `author_use` is attested
   only by an explicit statement that AI was used in or for THIS paper.
   A first-person acknowledgment with no detail ("with the help of AI")
   IS such a statement — `author_use`, category `unspecified`, impact
   `undetermined`. **No inference beyond that:** suggestively named
   files or attached artifacts without an explanatory statement, bare
   tool names in passing, thanks that merely associate someone with AI
   topics, and general remarks not tied to this paper are never
   `author_use` — and never `unclear` either; they are `topic_only`
   (an AI-related mention with no use stated) or `false_positive` (not
   about AI). **In doubt, do not attest author_use.**
4. No disclosed use, but an explicit "no AI was used" statement? →
   `non_use_statement`.
5. Any other AI relation (study object, benchmark, component of the
   studied system, artifact reuse, instrument, citation, passing
   mention)? → `topic_only`.
6. An explicit statement about AI use in this work that cannot be
   interpreted? → `unclear` (rare by construction).

**Boundary notes.**

- *Judge the role, not the mechanical operation.* Asking an LLM which
  abstracts are similar — or to score relevance, quality, or
  correctness — delegates a human judgment (`author_use`); running a
  model to emit its native statistics (embeddings, feature vectors,
  perplexities) is instrument use (`topic_only`).
- *"Traditionally human"* means human-performed in pre-LLM mathematical
  practice — by researchers or research-support workers (editors,
  translators, programmers, annotators); the scale of the task never
  changes its type.
- *Roles coexist, even in one invocation.* A paper may benchmark LLMs
  *and* disclose using one for writing; a benchmark output the authors
  retain as mathematics is both study object and delegated use. The
  disclosed delegated use wins the paper's polarity (precedence above).
- *Attempted use is still use* — see epistemic impact below.

## Usage categories (multi-label, author_use only)

| Category | Means | Does NOT mean |
|---|---|---|
| writing_editing | drafting, rephrasing, polishing, or translating text; help *formulating* what to say (prose, LaTeX, exposition, referee responses) | reviewing finished text for errors (→ proofreading) |
| proofreading | reviewing existing text for errors — language, notation, or mathematical arguments | auditing code or pipelines (→ code_computation) |
| literature_search | finding or summarizing references and related work | |
| ideation | research directions, problem formulations, framing | AI-proposed statements (→ conjecture_generation); software design (→ code_computation) |
| conjecture_generation | AI proposed the conjecture/prediction/candidate statement itself | human conjecture tested with AI code (→ code_computation) |
| examples_counterexamples | constructing mathematical witnesses — examples and counterexamples used in reasoning | items forming a dataset (→ data_generation_labeling) |
| proof_generation | finding proof strategies/arguments, or filling gaps in human-outlined proofs | checking existing arguments (→ proofreading) |
| code_computation | writing or orchestrating software; symbolic or numerical computation; auditing, testing, or verifying code and computational pipelines | |
| data_generation_labeling | generating, labeling, judging, or classifying items that form a dataset or corpus for the study — whether 5 items or 50,000 | |
| formalization | proof-assistant formalization (Lean, Coq/Rocq, …) performed or assisted by an in-scope AI | ordinary human proof-assistant work |
| figures | figure/visualization generation | |
| unspecified | a disclosed use whose role is unknown (a vague *separate* use next to known uses gets its own `unspecified` entry) | a hedge added to a use whose role is known |

**Multi-label convention:** mark every separately evidenced role; for
one indivisible act, choose the most specific category.

## Epistemic impact (paper-level; author_use only)

**Rate ONE impact per paper: the strongest explicitly graded use
wins.** Order for graded uses: `result_bearing` > `supportive` >
`cosmetic`. If any use grades at cosmetic or above, take the highest —
vaguer or fruitless co-uses never change it ("ChatGPT polished the
introduction and was also used elsewhere" → `cosmetic`: we record the
strongest identifiable use the authors explicitly disclose). If no use
grades: `undetermined` when any disclosed use is too vague to grade;
`zero_contribution` only when *every* disclosed use is explicitly
fruitless. Finer per-use detail (e.g. a fruitless attempt alongside a
contributing use) is deliberately not recorded — see the history
section for what this discards.

- **cosmetic** — writing, translation, LaTeX, figure polish,
  language-level proofreading only. Not a value judgment: translation
  and exposition matter; the label only says no research-content
  contribution is disclosed.
- **supportive** — search, code, computations, data work, checking
  (including AI-found mathematical errors), examples used along the
  way. Can include indispensable central implementation — supportive
  never means minor.
- **result_bearing** — AI-contributed conjecture, decisive proof idea,
  retained proof step, counterexample, mathematical search strategy, or
  formal verification of a substantive result.
- **zero_contribution** — every disclosed use is explicitly stated to
  have contributed nothing / not been used; implies `catalytic=false`.
- **undetermined** — no disclosed use can be graded (typically an R6
  acknowledgment with no role detail).
- **not_applicable** — non-author_use polarities only.

**Categories never determine impact.** Categories say what task the AI
performed; impact says how its output functioned in this paper. A
counterexample can be `result_bearing`; a figure can be `cosmetic`; a
proofreading pass that found a mathematical error is `supportive`.

Impact rules:

- **R1 (implementation is not by itself result_bearing).** Autonomous
  AI implementation and orchestration of even the *central* computation
  is supportive when the mathematical strategy is human-specified and
  results are certified independently of AI reasoning. It becomes
  result_bearing only when the AI contributed the mathematical search
  strategy, conjecture, or proof content itself.
- **R2 (causal ≠ retained).** AI output that merely triggered a human
  discovery path — including *incorrect* output that prompted a
  successful literature search — is supportive, with the `catalytic`
  flag set.
- **R3 (rendered evidence only).** See evidence eligibility above.
- **R5 (fruitless use is still use).** Disclosed use whose output
  explicitly contributed nothing is `author_use`; the disclosure
  behavior is real and counted in the headline. Vague disclosures are
  `undetermined`, never forced into a contribution level.

## Flag

- **catalytic** *(author_use only)* — causal contribution without
  retained content (rule R2); implies impact at least supportive, never
  combined with `zero_contribution`.

**Worked examples** (deidentified patterns; the rules bind, not the cases):

| Case | Verdict |
|---|---|
| authors thank ChatGPT for polishing the introduction | author_use · writing_editing · cosmetic |
| "No AI was used for the proofs; ChatGPT polished the English." | author_use · writing_editing · cosmetic (scoped denial never overrides disclosed use) |
| "the authors acknowledge the use of AI tools" (no detail) | author_use · unspecified · undetermined (rule R6) |
| "GPT-4" appears with no stated relation to the work | topic_only (passing mention; no use stated, no inference — R6) |
| ancillary file `chatgpt_log.pdf` attached, no explanatory text | topic_only (no inference from suggestively named artifacts — R6) |
| authors thank a colleague "for introducing them to AI-assisted research" | topic_only (general remark, not a statement of use in this paper — R6) |
| "ChatGPT polished the text and was also used in the research" | author_use · writing_editing, unspecified · cosmetic (two separately evidenced uses — the vague one is its own `unspecified` role; the strongest graded use sets the impact) |
| "We asked ChatGPT to prove the conjecture; none of its output was usable or used." | author_use · proof_generation · zero_contribution |
| AI proposed *false* proof approaches; convinced something real was nearby, authors found a stronger theorem in the literature | author_use · supportive + catalytic (rule R2) |
| "ChatGPT polished the text; the closed form it conjectured is eq. (7)" | author_use · writing_editing, conjecture_generation · result_bearing (highest wins) |
| AI agents autonomously implement and orchestrate the central computation; strategy human-specified, results independently certified | author_use · code_computation · supportive (rule R1) |
| LLM invoked to label/judge/summarize items for the study | author_use · data_generation_labeling (delegated judgment) |
| perplexity/embedding scores from a frozen model used as a complexity measure | topic_only (native model statistics = instrument) |
| paper benchmarks five LLMs on olympiad problems | topic_only (object of study) |
| frozen encoder *inside the studied architecture* | topic_only (component of the studied system) |
| pre-existing published embeddings reused as input features | topic_only (artifact reuse, no invocation) |
| any of the above **plus** a separately disclosed writing/coding use | author_use (precedence) |
| AI transcript present only in a TeX comment block, never rendered | no polarity — residual-artifact workflow (rule R3) |

## Disclosure location (multi-label)

| Location | Means |
|---|---|
| acknowledgments | the paper's thanks/acknowledgments section |
| dedicated_section | a section or statement specifically about AI use (e.g. "Use of AI tools") |
| abstract | the abstract |
| comments_field | the free-text "Comments:" line on the paper's arXiv abstract page |
| footnote_thanks | a footnote or title-page note |
| body | the main text |
| ancillary_artifact | files distributed alongside the paper (e.g. an attached chat transcript) |
| unknown | the disclosure's place in the paper cannot be determined |

Locations are multi-label: a section titled "Acknowledgements and Use
of Artificial Intelligence" is both `acknowledgments` and
`dedicated_section`. Machine snippet labels record one or more locations;
a paper's locations are the union across its snippets. The human form is
multi-select.

## Recorded fields (machine and human share this label space)

polarity · categories · epistemic impact · catalytic · tools named ·
location(s) · evidence quote (machine only) · exact model strings
(machine only) · confidence (machine only) · notes (human only).

**Public display labels.** Internal names are terse; public materials
use these glosses: author_use = "delegated AI use or attempted use
disclosed" · non_use_statement = "explicit non-use statement" ·
topic_only = "other AI relation — not delegated use" · false_positive =
"matched term unrelated to AI" · unclear = "AI relationship unclear" ·
cosmetic = "communication/presentation only" · supportive =
"research-process contribution" · result_bearing =
"mathematical-content contribution" · zero_contribution = "attempted
use, no contribution reported" · undetermined = "contribution level not
determinable".

---

## History and rationale

*This section is documentation for the interested reader; nothing here
is needed to apply the rules above.*

### What v2.8 removed, and why

v2.8 removes recording machinery, not rules. The evidence came from the
first two-sided comprehension exercise on the frozen v2.7 vignette set
(2026-08-14): the human grader scored 16/16 on polarity — the construct
itself transfers — while both the human *and* the machine stumbled on
the same recording furniture.

- **`method_component` and `external_ai_artifact` are no longer
  recorded fields.** Their content is exactly what makes a paper
  `topic_only`, so the boundary rules moved into the decision procedure
  where they do their real work. As always-on tri-state questions they
  were answered inconsistently by human and machine alike on the same
  instrument-use cases, and they doubled the per-item form burden for a
  distinction that never changes the headline.
- **The co-located state booleans (v2.7) are gone, and the information
  loss is accepted explicitly:** a paper disclosing both a contributing
  use and a fruitless attempt records only the higher impact; the
  fruitless attempt survives in the categories and the headline but not
  as a separate counted state. The impact scale still captures papers
  whose *only* use was fruitless (`zero_contribution`) or vague
  (`undetermined`). The attempted-use exception (R5) — the rule that
  matters — is unchanged.
- **Categories consolidated 17 → 12.** The retired fine slices could
  never be validated independently (a 150-positive gold sample has no
  power at 17 rare categories), and two gaps closed: `proofreading`
  (broadened from `proof_checking_criticism`) and
  `data_generation_labeling` (previously forced into `unspecified`).
  `ideation`, `conjecture_generation`, and `examples_counterexamples`
  stay separate (owner, 2026-08-14). Mapping from v2.7: translation,
  referee_response → writing_editing (referee_response was assigned to
  2 of 2,324 papers in the full v2.7 run, and both quotes were generic
  revision statements — the category carried no signal);
  proof_checking_criticism → proofreading; proof_discovery,
  proof_completion → proof_generation; code_generation,
  symbolic_computation, numerical_computation, computation_verification
  → code_computation. (Bulk synthetic-data cases previously under
  examples_counterexamples or unspecified belong to
  data_generation_labeling; this one mapping is approximate for old
  labels.)

### rev 3 (external review of the draft, 2026-08-14)

An independent review of rev 2 identified seams that rev 3 closes
within the owner's paper-level design (per-use "episode" labeling was
considered and rejected — the paper is the unit): explicit paper-level
precedence with the scoped-denial rule; the acknowledgment presumption
named as R6 (previously an unstated practice); a reachable `unclear`;
evidence eligibility stated as a gate before polarity; a deterministic
impact rule (owner, rev 4: the strongest explicitly *graded* use wins;
`undetermined` only when nothing grades); the explicit-statement rule
R6 with its no-inference clause (owner, rev 5: "in doubt, do not attest
author_use" — the false-attribution criticism is sharper than a missed
probable use; suggestive artifacts and general remarks are topic_only,
never author_use and never unclear; `unclear` is reserved for
uninterpretable explicit statements and is rare by construction; an
earlier proposal to count unexplained attached AI transcripts as
disclosure-by-artifact was considered and REJECTED); the
categories-never-determine-impact rule; the AI-system scope definition;
purpose-based (not scale-based) category boundaries; the multi-label
convention; public display labels; and an exact opening paragraph
(disclosure reports, not verified use).

### The delegation criterion (adopted 2026-08-13)

The author_use definition is the *delegation criterion*, proposed by the
owner: the AI performed an intellectual activity of a kind humans
traditionally perform themselves, so a counterfactual exists in which
the authors did the work. It replaced the v2.3–v2.5 stack of boundary
tests because it *derives* the object-of-study exclusion (substituting a
human would make the study nonsensical) rather than stipulating it, and
it collapses three precedence rules into one two-part question. The one
substantive scope change relative to v2.5: machine-only instrument
output left the numerator — invocation alone is not sufficient (owner
decision 2026-08-13). Known limitations, mitigated in the rules:
task-granularity ambiguity (judge-the-role convention), scale (type of
work, never feasibility), and temporal drift ("traditionally human" is
pinned to pre-LLM practice).

### Version history

| Version | Change |
|---|---|
| v1 (2026-08-09) | initial category set; known defect: definitions not embedded in the classifier prompt |
| v2.0 (2026-08-10) | definitions embedded verbatim in prompt; `ideation` / `conjecture_generation` split; `computation_verification`; `catalytic` flag; impact rules R1–R3 |
| v2.2 (2026-08-12) | post-calibration: R4 became an operational decision tree; impact `none` split into `zero_contribution` / `undetermined` / `not_applicable` with cross-field invariants; zero/undetermined never silently pooled |
| v2.3 (2026-08-12) | decisive boundary tests; illustration cases deidentified |
| v2.4 (2026-08-12) | boundary-test precedence fixed |
| v2.5 (2026-08-12) | ACTIVE INVOCATION construct; `external_ai_artifact` flag introduced |
| v2.6 (2026-08-13) | the DELEGATION criterion adopted as the author_use definition (owner decision); machine-only instrument output moved out of the numerator |
| v2.7 (2026-08-13) | review-11: co-located R5 states became label booleans; attempted-use exception named; `method_component` sharpened |
| v2.8 (2026-08-14) | simplification after the two-sided comprehension exercise + external draft review (owner decisions 2026-08-14): booleans removed; diagnostic flags demoted to rule text; categories 17 → 12; paper-level unit, precedence, acknowledgment presumption (R6), evidence-eligibility gate, total impact order, scope definition, display labels. Headline construct unchanged |

One FULL production classification run exists (v2.7, 2026-08-13, over
the pre-tail selected v1 scan; superseded by the post-acquisition final
run). v2.0 labels are never merged with v2.2+ labels; scoped development
labels exist for the 150 calibration papers.

### Calibration history

- **2026-08-12 (v2.0 instrument, blinded calibration round 1, JS):** 150
  labels ingested; 149 comparable after excluding one packet
  version-skew item. Shown-excerpt POS precision 28/32 = 87.5% (Wilson ≈
  [72%, 95%]); binary concordance 145/149 = 97.3%; plants 5/5 (process
  check only); same-text scanner misses 0/96 evaluable negatives. Axis
  concordance on 33 shared positives: impact ≈ 85%, categories ≈ 64%
  exact-set / 0.80 Jaccard. Single-human machine concordance, not
  inter-rater reliability. Calibration data never enters release
  validity metrics. The human workflow additionally uses two verdicts
  that are not polarities: NO_AI_MENTION (no AI-related content found —
  the normal outcome for scanner-negative papers) and
  INSUFFICIENT_EVIDENCE (paper unreadable/unavailable); both matter for
  the calibration and gold studies and map to "not classifiable", never
  to a polarity.
- **2026-08-12 (v2.4/v2.5 adherence, in-sample):** re-classification of
  the same 150 papers under the revised instrument: binary concordance
  147/149 — 51/53 model-evaluable + 96/96 structural no-snippet papers.
  Development evidence only.
- **2026-08-13/14 (v2.7 comprehension, synthetic, both sides):**
  16 frozen vignettes. Machine (3 repetitions): polarity/impact stable
  16/16, flags and R5 15/16; TOTAL expected-object agreement 14/16.
  Human (reviewer1, blinded): polarity 16/16, impact 15/16, flags 13/16
  — the same instrument-case confusion as the machine. This exercise
  drove the v2.8 simplification.
- **2026-08-10 (v1, JS spot-check, n=30):** result_bearing precision
  28/30 ≈ 93%; both downgrades are the R1/R2 worked examples above.

### Annotation interface

Reviewers see context with the matched span highlighted, all scanner
hits for the paper, and member/location metadata (never machine labels).
The verdict vocabulary is TRUE_DISCLOSURE / NON_USE_STATEMENT /
TOPIC_ONLY / FALSE_POSITIVE / NO_AI_MENTION / INSUFFICIENT_EVIDENCE /
UNCLEAR; decision text for each verdict is generated verbatim from this
taxonomy's polarity definitions, plus category/impact/location/catalytic
fields and free-text notes. Every borderline note feeds this document.
