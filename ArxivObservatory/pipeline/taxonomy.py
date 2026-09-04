"""Versioned classification taxonomy — machine copy.

Single source of truth for the label vocabulary used by classify.py (prompt
construction AND response validation). TAXONOMY.md is the human companion
document with boundary rationale; a unit test asserts the two stay in sync.

Version discipline: bump TAXONOMY_VERSION on ANY change to names, definitions,
or decision rules. Every classification run records the version it used;
labels from different taxonomy versions are never merged in analysis.
"""

from __future__ import annotations

TAXONOMY_VERSION = "2.8"

# --- polarity ----------------------------------------------------------------
# The unit of classification is the PAPER; snippets are evidence passages
# labeled as an intermediate step. Paper-level precedence: author_use >
# non_use_statement > topic_only > false_positive; unclear is reserved for
# uninterpretable explicit statements about AI use (rare by construction).
#
# Decision procedure (v2.8):
#   1. Nothing about AI beyond notation or names -> false_positive.
#   2. The DELEGATION test (R4): author_use requires BOTH (i) the authors
#      invoked an AI system during this research AND (ii) it performed a
#      delegated human-type intellectual role — work of a kind humans
#      traditionally perform themselves — whose output entered the conduct
#      or communication of the paper. Counterfactual test: the authors
#      could have obtained this input by doing the work themselves.
#      Exception (R5): an invocation undertaken FOR such a role counts
#      even when its output was explicitly not used.
#   3. The EXPLICIT-STATEMENT rule (R6): author_use is attested only by an
#      explicit statement that AI was used in or for THIS paper. A
#      first-person acknowledgment with no detail ("with the help of AI")
#      IS such a statement (category unspecified, impact undetermined).
#      NO inference beyond that: suggestively named files or attached
#      artifacts without an explanatory statement, bare tool names in
#      passing, thanks that merely associate someone with AI topics, and
#      general remarks not tied to this paper are never author_use — and
#      never unclear; they are topic_only or false_positive. In doubt, do
#      not attest author_use.
#   4. No disclosed use, but an explicit "no AI" statement ->
#      non_use_statement.
#   5. Any other AI relation (study object, benchmark, component of the
#      studied system, artifact reuse, instrument, citation, passing
#      mention) -> topic_only.
#   6. An explicit statement about AI use in this work that cannot be
#      interpreted -> unclear.
# Roles coexist, even in one invocation: a disclosed delegated use wins
# the paper's polarity regardless of any study/component/instrument role.

POLARITIES: dict[str, str] = {
    "author_use":
        "the authors (or collaborators) invoked an AI/LLM system during "
        "THIS research to perform intellectual work of a kind humans "
        "traditionally perform themselves — writing, proofreading, "
        "translation, literature search, ideation, proofs, checking, "
        "code, computations, data labeling or generation, formalization — "
        "and its output entered the conduct or communication of the paper "
        "(the delegation test, R4: a counterfactual exists in which the "
        "authors did that work themselves; judge the ROLE of the output, "
        "not the mechanical operation). EXCEPTION (rule R5): a disclosed "
        "invocation undertaken FOR such a delegated role is author_use "
        "even when its output was explicitly not used — attempted use "
        "still counts, with impact zero_contribution. Rule R6: author_use "
        "requires an EXPLICIT statement of use in or for this paper; a "
        "first-person acknowledgment with no detail ('with the help of "
        "AI') qualifies (category unspecified, impact undetermined); "
        "suggestive artifacts, bare tool names, and general remarks never "
        "qualify. In doubt, do not attest author_use.",
    "non_use_statement":
        "authors explicitly state that they did NOT use AI, and no use is "
        "disclosed anywhere in the paper.",
    "topic_only":
        "the AI does not stand in for the authors' own intellectual work: "
        "the paper STUDIES an AI system or discusses AI as subject "
        "matter, CITES AI-related literature, BENCHMARKS models, ANALYZES "
        "a system that contains an AI component, REUSES a pre-existing "
        "AI-produced artifact as data, or RUNS a model purely as a "
        "measuring instrument (native model statistics: embeddings, "
        "feature vectors, perplexities). Also the home for AI-related "
        "mentions with no use stated (R6: suggestively named files, bare "
        "tool names, general remarks).",
    "false_positive":
        "the term is notation, a person/place name, an affiliation, or "
        "otherwise not about AI at all (ordinary unaided use of proof "
        "assistants, computer-algebra systems, or conventional software "
        "is not AI use).",
    "unclear":
        "the paper explicitly addresses AI use for this work, but the "
        "statement cannot be interpreted (contradictory or garbled). "
        "Rare by construction — suggestive-but-nonexplicit material is "
        "topic_only, never unclear (R6).",
}

# --- usage categories (multi-label, author_use only) -------------------------
# v2.8: consolidated 17 -> 12 (owner decisions 2026-08-14). Multi-label
# convention: mark every separately evidenced role; for one indivisible
# act, choose the most specific category. unspecified is only for a
# disclosed use whose role is unknown — never a hedge next to known
# categories.

CATEGORIES: dict[str, str] = {
    "writing_editing":
        "drafting, rephrasing, polishing, or translating text; help "
        "FORMULATING what to say (prose, LaTeX, exposition, referee "
        "responses). Not reviewing finished text for errors — that is "
        "proofreading.",
    "proofreading":
        "reviewing existing text for errors — language, notation, or "
        "mathematical arguments. Not auditing code or pipelines — that is "
        "code_computation.",
    "literature_search":
        "finding or summarizing references and related work.",
    "ideation":
        "research directions, problem formulations, framing. AI-proposed "
        "statements are conjecture_generation; software design is "
        "code_computation.",
    "conjecture_generation":
        "the AI proposed the mathematical conjecture, prediction, or "
        "candidate statement itself. A human conjecture tested with AI "
        "code is code_computation.",
    "examples_counterexamples":
        "constructing mathematical witnesses — examples and "
        "counterexamples used in reasoning. Items forming a dataset are "
        "data_generation_labeling.",
    "proof_generation":
        "finding proof strategies/arguments, or filling gaps in "
        "human-outlined proofs. Checking existing arguments is "
        "proofreading.",
    "code_computation":
        "writing or orchestrating software; symbolic or numerical "
        "computation; auditing, testing, or verifying code and "
        "computational pipelines.",
    "data_generation_labeling":
        "generating, labeling, judging, or classifying items that form a "
        "dataset or corpus for the study — whether 5 items or 50,000.",
    "formalization":
        "proof-assistant formalization (Lean, Coq/Rocq, ...) performed or "
        "assisted by an in-scope AI system — never ordinary human "
        "proof-assistant work.",
    "figures":
        "figure or visualization generation.",
    "unspecified":
        "a disclosed use whose role is unknown. A vague SEPARATE use next "
        "to known uses gets its own unspecified entry; never add "
        "unspecified as a hedge on a use whose role is known.",
}

# --- epistemic impact (paper-level; author_use only) -------------------------
# v2.8 aggregation (owner decision 2026-08-14): the strongest explicitly
# GRADED use wins — result_bearing > supportive > cosmetic; vaguer or
# fruitless co-uses never change it. If no use grades: undetermined when
# any disclosed use is too vague to grade; zero_contribution only when
# EVERY disclosed use is explicitly fruitless. Categories never determine
# impact: categories say what task the AI performed, impact says how its
# output functioned in this paper.
# R1. Autonomous AI implementation/orchestration of even the CENTRAL
#     computation is supportive when the mathematical strategy is
#     human-specified and results are certified independently of AI
#     reasoning; result_bearing requires AI-contributed mathematical
#     content (implementation is not by itself result_bearing).
# R2. Causal contribution is not retained content: if AI output (even
#     incorrect output) merely triggered a human discovery path, the impact
#     is supportive; record the catalytic flag.
# R3. Evidence must be in rendered/publicly visible text (render-check
#     layer); source-only material never carries labels.

IMPACTS: dict[str, str] = {
    "cosmetic":
        "writing, translation, LaTeX, figure polish, language-level "
        "proofreading only — no research-content contribution disclosed.",
    "supportive":
        "search, code, computations, data work, checking (including "
        "AI-found mathematical errors), examples used along the way; "
        "includes autonomous implementation/orchestration of central "
        "computations under human-specified strategy with AI-independent "
        "certification (R1), and catalytic-but-not-retained contributions "
        "(R2). Supportive never means minor.",
    "result_bearing":
        "AI-contributed conjecture, decisive proof idea, retained proof "
        "step, counterexample, mathematical search strategy, or formal "
        "verification of a substantive result.",
    "zero_contribution":
        "EVERY disclosed use is explicitly stated to have contributed "
        "nothing / not been used (rule R5); implies catalytic=false.",
    "undetermined":
        "no disclosed use can be graded (typically an R6 acknowledgment "
        "with no role detail); never force a vague disclosure into a "
        "contribution level, and never let it override a graded use.",
    "not_applicable":
        "non-author_use polarities only.",
}

# --- disclosure location -----------------------------------------------------

LOCATIONS: dict[str, str] = {
    "acknowledgments": "the paper's thanks/acknowledgments section",
    "dedicated_section": "a section or statement specifically about AI use",
    "abstract": "the abstract",
    "comments_field": "the free-text Comments line on the arXiv abstract page",
    "footnote_thanks": "a footnote or title-page note",
    "body": "the main text",
    "ancillary_artifact": "files distributed alongside the paper",
    "unknown": "the disclosure's place cannot be determined",
}

# --- boolean flags -----------------------------------------------------------
# v2.8: catalytic is the ONLY recorded flag. The former method_component /
# external_ai_artifact diagnostics were demoted to topic_only rule text
# (owner decision 2026-08-14: human and machine graders were inconsistent
# on the same instrument cases, and the fields never changed the headline).

FLAGS: dict[str, str] = {
    "catalytic":
        "AI output contributed causally to the discovery path without its "
        "content being retained (e.g. a wrong AI proof attempt that led the "
        "authors to a correct literature result). Implies impact at least "
        "supportive (R2) — never combined with zero_contribution.",
}


def prompt_definitions() -> str:
    """Definition block for the classification prompt, generated from the
    dictionaries above so prompt and validator can never drift."""
    lines = ["Definitions (taxonomy v" + TAXONOMY_VERSION + "):", "- polarity:"]
    for name, desc in POLARITIES.items():
        lines.append(f"  * {name} — {desc}")
    lines.append("- categories (multi-label, only for author_use; mark every "
                 "separately evidenced role, choose the most specific "
                 "category for one indivisible act):")
    for name, desc in CATEGORIES.items():
        lines.append(f"  * {name} — {desc}")
    lines.append("- epistemic_impact:")
    for name, desc in IMPACTS.items():
        lines.append(f"  * {name} — {desc}")
    lines.append(
        "  Decision rules: (R1) autonomous AI implementation or orchestration "
        "of even the central computation is supportive when the mathematical "
        "strategy is human-specified and results are certified independently "
        "of AI reasoning; result_bearing requires AI-contributed mathematical "
        "search strategy, conjecture, or proof content — implementation is "
        "not by itself result_bearing. (R2) causal contribution without "
        "retained content is supportive; set the catalytic flag; catalytic "
        "implies impact at least supportive. "
        "(R4, the delegation test) author_use requires BOTH: the authors "
        "INVOKED the system during this research, AND it performed a "
        "DELEGATED human-type intellectual role — work humans traditionally "
        "perform themselves — whose output entered the conduct or "
        "communication of the paper. Judge the ROLE the output plays, not "
        "the mechanical operation: LLM similarity/quality JUDGMENTS are "
        "author_use; native model statistics (embeddings, feature vectors, "
        "perplexities) from the same model are instrument output -> "
        "topic_only, exactly like reuse of pre-existing AI-made artifacts "
        "and AI as subject matter, benchmark, or component of the studied "
        "system. Roles coexist: a separately disclosed delegated use is "
        "author_use regardless of any study/component/instrument role. "
        "(R5) explicitly fruitless use -> author_use; zero_contribution "
        "only when EVERY disclosed use is explicitly fruitless (catalytic "
        "must be false). "
        "(R6, the explicit-statement rule) author_use is attested only by "
        "an explicit statement that AI was used in or for THIS paper; a "
        "first-person acknowledgment with no detail ('with the help of "
        "AI') qualifies -> author_use, category unspecified, impact "
        "undetermined. NO inference beyond that: suggestively named files "
        "or attached artifacts without an explanatory statement, bare tool "
        "names in passing, thanks that merely associate someone with AI "
        "topics, and general remarks not tied to this paper are "
        "topic_only — never author_use and never unclear. In doubt, do "
        "not attest author_use. unclear is ONLY for explicit statements "
        "about AI use in this work that cannot be interpreted. "
        "epistemic_impact: the strongest explicitly GRADED use in the "
        "snippet wins (result_bearing > supportive > cosmetic); vaguer or "
        "fruitless co-uses never change it; undetermined only when no use "
        "grades; not_applicable is reserved for non-author_use. Categories "
        "NEVER determine impact: categories say what task the AI "
        "performed, impact says how its output functioned. A SCOPED "
        "denial ('no AI was used for the proofs; ChatGPT polished the "
        "English') never overrides a disclosed use — such a snippet is "
        "author_use. author_use requires at least one category (use "
        "unspecified when the role is unknown). Snippet labels are "
        "intermediate evidence: the pipeline aggregates them to ONE "
        "paper-level label under the fixed precedence author_use > "
        "non_use_statement > topic_only > false_positive, and the "
        "paper-level impact is the strongest graded use across all its "
        "snippets. Snippets come from TeX source; whether the evidence "
        "appears in the rendered paper is verified by a separate "
        "render-check layer (R3), not by you.")
    lines.append("- locations (one or more; where the statement appears — "
                 "a section titled 'Acknowledgements and Use of AI' is "
                 "BOTH acknowledgments and dedicated_section):")
    for name, desc in LOCATIONS.items():
        lines.append(f"  * {name} — {desc}")
    lines.append("- flags (booleans; catalytic only for author_use):")
    for name, desc in FLAGS.items():
        lines.append(f"  * {name} — {desc}")
    return "\n".join(lines)


def cross_field_problems(is_author_use: bool, impact: str,
                         flags: dict) -> list[str]:
    """Cross-field invariants shared by the machine validator
    (classify.validate_label) and the human ingest path
    (annotate.validate_verdict_item) — review-8 A3: ONE function, both
    graders."""
    problems: list[str] = []
    if is_author_use:
        if impact == "not_applicable":
            problems.append("author_use impact cannot be not_applicable "
                            "(use zero_contribution or undetermined)")
        if impact == "zero_contribution" and flags.get("catalytic"):
            problems.append("zero_contribution contradicts catalytic (R2/R5)")
        if flags.get("catalytic") and impact not in ("supportive",
                                                     "result_bearing"):
            problems.append("catalytic implies impact at least supportive (R2)")
    else:
        if flags.get("catalytic"):
            problems.append("catalytic requires author_use")
    return problems
