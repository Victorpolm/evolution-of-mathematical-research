"""Frozen synthetic comprehension/repeatability exercise (review-10 A4,
review-11 A1).

Vignettes are AUTHORED for this exercise — no corpus text, no real papers —
and cover every R4/R5 boundary: delegated vs instrument use, object of
study vs toolchain, artifact reuse, fruitless/catalytic/vague use, dual
roles, co-located mixed states, and notation false positives. The checker
computes per-axis stability and expected-field agreement DIRECTLY from the
recorded repetitions, so a summary can never claim more than the data
(review-11 A1: a hand-written summary overstated flag stability). Results
are development evidence only, never accuracy claims.

Usage:
    python3 -m pipeline.comprehension --reps 3 \
        --approval-id <campaign> [--model gpt-5.6-luna] [--tag v28]
Exit code 1 when any expected field mismatches in any repetition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from . import classify, db, llm_api, taxonomy

# (key, marked_terms, text, expected) — vignette set v2 (taxonomy v2.8).
# Realistic framing so LOCATION is testable; targeted at the v2.8 seams:
# scoped denial, first-person acknowledgment vs bare mention (R6),
# artifact no-inference, mixed graded+vague impact, math proofreading,
# AI vs plain formalization, uncertified central computation.
# expected objects are TOTAL (review-12 B1): polarity, impact (or an
# explicit impact_any_of set), complete flag AND category lists, and
# location (or location_any_of). The checker fails closed on a missing
# axis.
VIGNETTES: list[tuple[str, list[str], str, dict]] = [
    ("ack_polish", ["ChatGPT"],
     "Acknowledgments. The authors thank the anonymous referees for their "
     "valuable suggestions. We also thank ChatGPT for help polishing the "
     "introduction and the abstract.",
     {"polarity": "author_use", "impact": "cosmetic", "flags": [],
      "categories": ["writing_editing"], "location": "acknowledgments"}),
    ("scoped_denial", ["AI", "ChatGPT"],
     "Use of artificial intelligence. No AI tools were used in the "
     "derivation or verification of the mathematical results of this "
     "paper. ChatGPT was used to improve the English of Sections 1 and 2; "
     "all content was reviewed by the authors.",
     {"polarity": "author_use", "impact": "cosmetic", "flags": [],
      "categories": ["writing_editing"], "location": "dedicated_section"}),
    ("generic_ack", ["AI"],
     "Acknowledgments. This work was supported by grant No. 12-345. Parts "
     "of this work were completed with the help of AI.",
     {"polarity": "author_use", "impact": "undetermined", "flags": [],
      "categories": ["unspecified"], "location": "acknowledgments"}),
    ("bare_mention", ["large language models", "GPT-4"],
     "The rapid progress of large language models such as GPT-4 has "
     "renewed interest in the combinatorics of attention mechanisms, "
     "which motivates the present study.",
     {"polarity": "topic_only", "impact": "not_applicable", "flags": [],
      "categories": [], "location": "body"}),
    ("artifact_no_statement", ["chatgpt"],
     "Ancillary files: appendix_computations.nb, "
     "chatgpt_conversation_2026-03-12.pdf, data_tables.zip.",
     {"polarity": "topic_only", "impact": "not_applicable", "flags": [],
      "categories": [],
      "location_any_of": ["ancillary_artifact", "body", "unknown"]}),
    ("intro_thanks", ["AI-assisted"],
     "Acknowledgments. We are grateful to K. H. Lee for introducing us to "
     "AI-assisted research, and to the referee for spotting a gap in an "
     "earlier version of Lemma 2.",
     {"polarity": "topic_only", "impact": "not_applicable", "flags": [],
      "categories": [], "location": "acknowledgments"}),
    ("mixed_graded_vague", ["ChatGPT", "AI"],
     "Statement on AI usage. ChatGPT was used to polish the exposition "
     "throughout the paper. AI tools were also used at earlier stages of "
     "this research.",
     {"polarity": "author_use", "impact": "cosmetic", "flags": [],
      "categories": ["unspecified", "writing_editing"],
      "location": "dedicated_section"}),
    ("fruitless_named", ["GPT-5"],
     "We also experimented with GPT-5 on Conjecture 1.2: we asked it to "
     "prove the conjecture directly, but none of its proposed arguments "
     "withstood scrutiny, and no output of the model is used in this "
     "paper.",
     {"polarity": "author_use", "impact": "zero_contribution", "flags": [],
      "categories": ["proof_generation"], "location": "body"}),
    ("catalytic_wrong", ["GPT-5", "proof"],
     "GPT-5 proposed a proof of Lemma 4 that turned out to be flawed; "
     "however, its structure convinced us that a stronger statement "
     "should hold, and a subsequent literature search located the "
     "classical result of Deuring that we now cite. The model's argument "
     "itself is not used.",
     {"polarity": "author_use", "impact": "supportive",
      "flags": ["catalytic"], "categories": ["proof_generation"],
      "location": "body"}),
    ("retained_conjecture", ["ChatGPT", "conjectured"],
     "ChatGPT was used to polish the introduction. Moreover, the closed "
     "form in equation (7) was first conjectured by the model and "
     "subsequently proven by the second author; the identity is retained "
     "as Theorem 2.",
     {"polarity": "author_use", "impact": "result_bearing", "flags": [],
      "categories": ["conjecture_generation", "writing_editing"],
      "location": "body"}),
    ("llm_judge", ["GPT-4", "labeled"],
     "Each of the 40,000 candidate identities was labeled as trivial or "
     "non-trivial by GPT-4; we verified a random subsample by hand and "
     "used the labels to prioritize which families we examined first. "
     "The search strategy itself follows our earlier work [3].",
     {"polarity": "author_use", "impact": "supportive", "flags": [],
      "categories": ["data_generation_labeling"], "location": "body"}),
    ("synthetic_data", ["language model", "synthetic"],
     "Training data for our heuristic ranking function was generated "
     "synthetically: we prompted a large language model to produce "
     "10,000 well-formed but unproven inequalities, which our system "
     "then attempts to refute.",
     {"polarity": "author_use", "impact": "supportive", "flags": [],
      "categories": ["data_generation_labeling"], "location": "body"}),
    ("embeddings_instrument", ["BERT", "embeddings"],
     "To compare the textual structure of the two corpora, we run the "
     "frozen BERT-base encoder over each abstract and use the resulting "
     "embeddings as feature vectors in our clustering pipeline.",
     {"polarity": "topic_only", "impact": "not_applicable", "flags": [],
      "categories": [], "location": "body"}),
    ("benchmark", ["large language models", "GPT-4"],
     "Abstract. We evaluate five large language models, including GPT-4, "
     "on a new benchmark of 300 olympiad geometry problems and analyze "
     "their failure modes; no model output is used outside this "
     "evaluation.",
     {"polarity": "topic_only", "impact": "not_applicable", "flags": [],
      "categories": [], "location": "abstract"}),
    ("dual_role", ["LLMs", "ChatGPT"],
     "This paper studies the in-context learning behavior of several "
     "LLMs on modular arithmetic tasks. Acknowledgments. We thank our "
     "colleagues for many discussions, and we acknowledge the use of "
     "ChatGPT for polishing the exposition of Sections 1 and 2.",
     {"polarity": "author_use", "impact": "cosmetic", "flags": [],
      "categories": ["writing_editing"], "location": "acknowledgments"}),
    ("math_proofread", ["Claude"],
     "Acknowledgments. We used Claude to check the manuscript for "
     "typographical errors and for errors in the proofs of Section 3; "
     "the remaining errors are our own.",
     {"polarity": "author_use", "impact": "supportive", "flags": [],
      "categories": ["proofreading"], "location": "acknowledgments"}),
    ("ai_formalization", ["LLM", "Lean"],
     "The Lean 4 formalization of Theorem 3, available in the "
     "supplementary repository, was produced with substantial assistance "
     "from an LLM-based autoformalization tool.",
     {"polarity": "author_use", "impact": "result_bearing", "flags": [],
      "categories": ["formalization"], "location": "body"}),
    ("plain_lean", ["Lean"],
     "All results of Section 4 were formalized by the authors in Lean 4 "
     "using the mathlib library; the verification completes in under an "
     "hour on a laptop.",
     {"polarity": "false_positive", "impact": "not_applicable",
      "flags": [], "categories": [],
      "location_any_of": ["body", "unknown"]}),
    ("non_use", ["artificial-intelligence"],
     "Declaration. No generative artificial-intelligence tools were used "
     "in the research, computations, or writing of this article.",
     {"polarity": "non_use_statement", "impact": "not_applicable",
      "flags": [], "categories": [], "location": "dedicated_section"}),
    ("notation_fp", ["Ai", "A.I."],
     "Here Ai(x) denotes the Airy function, and A.I. are the initials of "
     "the second author, whom we thank for the computation of Table 2.",
     {"polarity": "false_positive", "impact": "not_applicable",
      "flags": [], "categories": [],
      "location_any_of": ["body", "unknown"]}),
    ("comments_polish", ["ChatGPT"],
     "arXiv comments field: 27 pages, 3 figures. v2: typos corrected; "
     "English polished with ChatGPT.",
     {"polarity": "author_use", "impact": "cosmetic", "flags": [],
      "categories": ["writing_editing"], "location": "comments_field"}),
    ("agent_search_strategy", ["AI agents"],
     "The enumeration underlying Theorem 5 was carried out end-to-end by "
     "AI agents, which chose the search strategy, wrote and ran the "
     "code, and reported the certificate that we include in Appendix B; "
     "we verified the certificate independently.",
     {"polarity": "author_use", "impact": "result_bearing", "flags": [],
      "categories": ["code_computation"], "location": "body"}),
]


def vignette_snippets() -> list[dict]:
    return [{"arxiv_id": f"synthetic.{k}", "version": 1, "source_kind": "tex",
             "member": "vignette.tex", "terms": t, "context": c,
             "input_hash": hashlib.sha256(c.encode()).hexdigest(),
             "hit_ids": []} for k, t, c, _ in VIGNETTES]


def bundle() -> dict:
    header = classify.build_prompt_header()
    return {"taxonomy_version": taxonomy.TAXONOMY_VERSION,
            "prompt_sha256": hashlib.sha256(header.encode()).hexdigest(),
            "vignettes_sha256": hashlib.sha256(json.dumps(
                [(k, t, c) for k, t, c, _ in VIGNETTES],
                sort_keys=True).encode()).hexdigest()}


def check(reps: list[dict]) -> dict:
    """Per-axis stability + expected-field agreement, computed — never
    asserted — from the recorded repetitions. Fails CLOSED (raises) when an
    expected object is not total (review-12 B1: an omitted expectation is a
    silent don't-care that lets a substantively wrong output count as OK).
    v2.8 axes: polarity, impact, flags (catalytic), categories, location."""
    rows = []
    for key, _t, _c, exp in VIGNETTES:
        if "polarity" not in exp or ("impact" not in exp) == (
                "impact_any_of" not in exp):
            raise ValueError(f"vignette {key!r}: expected object must state "
                             "polarity and exactly one of impact/"
                             "impact_any_of")
        if "flags" not in exp or "categories" not in exp:
            raise ValueError(f"vignette {key!r}: expected object must state "
                             "the complete flag and category lists")
        if ("location" not in exp) == ("location_any_of" not in exp):
            raise ValueError(f"vignette {key!r}: expected object must state "
                             "exactly one of location/location_any_of")
        labs = [rep[key] for rep in reps]
        pols = [l["polarity"] for l in labs]
        imps = [l.get("epistemic_impact", l.get("impact")) for l in labs]
        flgs = [sorted(k for k, v in l["flags"].items() if v) for l in labs]
        cats = [sorted(l["categories"]) for l in labs]
        locs = [sorted(l.get("locations")
                       or [l.get("location", "unknown")]) for l in labs]
        mism = []
        if not all(p == exp["polarity"] for p in pols):
            mism.append("polarity")
        ok_imps = ([exp["impact"]] if "impact" in exp
                   else exp["impact_any_of"])
        if not all(i in ok_imps for i in imps):
            mism.append("impact")
        if not all(f == sorted(exp["flags"]) for f in flgs):
            mism.append("flags")
        if not all(c == sorted(exp["categories"]) for c in cats):
            mism.append("categories")
        if "location" in exp:
            ok = all(l == [exp["location"]] for l in locs)
        else:
            allowed = set(exp["location_any_of"])
            ok = all(l and set(l) <= allowed for l in locs)
        if not ok:
            mism.append("location")
        rows.append({
            "vignette": key, "expected": exp, "polarities": pols,
            "impacts": imps, "flags": flgs, "categories": cats,
            "locations": locs,
            "stable": {
                "polarity": len(set(pols)) == 1,
                "impact": len(set(imps)) == 1,
                "flags": len({json.dumps(f) for f in flgs}) == 1,
                "categories": len({json.dumps(c) for c in cats}) == 1,
                "location": len({json.dumps(l) for l in locs}) == 1,
            },
            "expected_mismatches": mism,
        })
    n = len(rows)
    axes = ("polarity", "impact", "flags", "categories", "location")
    return {
        "n_vignettes": n, "n_reps": len(reps),
        "stable_counts": {a: sum(r["stable"][a] for r in rows) for a in axes},
        "all_axes_stable": sum(all(r["stable"].values()) for r in rows),
        "expected_ok": sum(not r["expected_mismatches"] for r in rows),
        "rows": rows,
    }


def render_md(res: dict, b: dict, spend_usd: float | None) -> str:
    sc = res["stable_counts"]
    n = res["n_vignettes"]
    lines = [
        f"# v{b['taxonomy_version']} comprehension/repeatability — "
        f"{res['n_reps']} repetitions (machine half; SYNTHETIC vignettes; "
        "development evidence only, never accuracy)",
        "",
        f"instrument: taxonomy v{b['taxonomy_version']}, prompt "
        f"{b['prompt_sha256'][:12]}…, vignettes "
        f"{b['vignettes_sha256'][:12]}…",
        "",
        "COMPUTED per-axis stability (a summary can never exceed this "
        "table — review-11 A1): "
        f"polarity {sc['polarity']}/{n}, impact {sc['impact']}/{n}, "
        f"flags {sc['flags']}/{n}, categories {sc['categories']}/{n}, "
        f"location {sc['location']}/{n}; ALL axes stable "
        f"{res['all_axes_stable']}/{n}. TOTAL expected objects (polarity, "
        "impact or an explicit impact_any_of set, complete flags and "
        "categories, location) matched in every repetition: "
        f"{res['expected_ok']}/{n}.",
        "",
        "| vignette | expected | observed polarity / impact / flags / categories / location | stable axes | mismatches |",
        "|---|---|---|---|---|",
    ]
    for r in res["rows"]:
        stab = ",".join(a for a in ("polarity", "impact", "flags",
                                    "categories", "location") if r["stable"][a])
        obs = (f"{'/'.join(r['polarities'])}; {'/'.join(r['impacts'])}; "
               f"{r['flags']}; {r['categories']}; {r['locations']}")
        lines.append(f"| {r['vignette']} | {json.dumps(r['expected'])} | "
                     f"{obs} | {stab} | "
                     f"{', '.join(r['expected_mismatches']) or '—'} |")
    lines.append("")
    lines.append("incremental spend for THIS exercise: "
                 + (f"${spend_usd:.6f} (ledger rows created by this "
                    "invocation)" if spend_usd is not None else "unknown"))
    lines.append("The human half (both graders, blinded, this exact frozen "
                 "set) precedes owner sign-off; disagreements feed the "
                 "manual.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--approval-id", required=True)
    ap.add_argument("--cap-usd", type=float, required=True)
    ap.add_argument("--tag", default=None,
                    help="run tag (default comprehension-v<taxonomy>)")
    args = ap.parse_args()
    tag = args.tag or ("comprehension-v"
                       + taxonomy.TAXONOMY_VERSION.replace(".", ""))
    provider = llm_api.provider_of_model(args.model)
    llm_api.load_env(provider)
    llm_api.set_budget(None, args.cap_usd)
    llm_api.attach_ledger(db.DB_PATH, tag, approval_id=args.approval_id,
                          provider=provider, model=args.model,
                          cap_usd=args.cap_usd)
    classify.ATTEMPT_SOURCE[0] = llm_api.drain_attempts
    classify.REQUEST_CTX[0] = llm_api.set_request_context
    caller = (lambda p: llm_api.call_api(p, args.model))
    import sqlite3
    con = sqlite3.connect(str(db.DB_PATH), timeout=60)
    spend_before = con.execute(
        "SELECT COALESCE(MAX(id),0) FROM api_spend").fetchone()[0]
    snips = vignette_snippets()
    header = classify.build_prompt_header()
    reps: list[dict] = []
    for r in range(args.reps):
        labels: dict[str, dict] = {}
        for i, s in enumerate(snips):
            out, recs, failed = classify.classify_batch(
                [s], header, caller, split_path=f"rep{r}.v{i}")
            if failed or out[0][1] is None:
                print(f"FAILED: {VIGNETTES[i][0]} rep {r}: "
                      f"{failed or out[0][3]}", flush=True)
                return 2
            labels[VIGNETTES[i][0]] = out[0][1]
        reps.append(labels)
        print(f"rep {r + 1}/{args.reps} done", flush=True)
    spend = con.execute(
        "SELECT COALESCE(SUM(usd),0) FROM api_spend WHERE id>? AND "
        "kind LIKE 'settled%'", (spend_before,)).fetchone()[0]
    con.close()
    res = check(reps)
    b = bundle()
    out_dir = db.PROJECT_ROOT / "annotation" / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(
        {"bundle": b, "reps": args.reps,
         "vignettes": [{"key": k, "terms": t, "text": c, "expected": e}
                       for k, t, c, e in VIGNETTES],
         "check": res, "incremental_spend_usd": spend}, indent=1))
    md = render_md(res, b, spend)
    (out_dir / "stability.md").write_text(md)
    print(md.split("\n\n")[2])
    print(f"wrote {out_dir}/")
    return 0 if res["expected_ok"] == res["n_vignettes"] else 1


if __name__ == "__main__":
    sys.exit(main())
