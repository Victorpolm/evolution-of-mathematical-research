"""Score a HUMAN comprehension-packet export against the frozen vignette
expectations (the human half of the review-12 B2 exercise).

Converts each exported verdict into the machine label shape and runs the
SAME totality-checked comprehension.check() as the machine half, so both
halves share one convention set (impact_any_of / location_any_of, empty
location falling back to "unknown"). Unfilled locations on non-disclosure
verdicts are additionally reported as "not filled" rather than silently
counted as plain misses: the form allows them empty, so they measure form
UX, not codebook comprehension.

Development evidence only — never release validity.

Usage: python3 -m pipeline.comprehension_score \
           --json <export.json> --manifest <packets_manifest.json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import comprehension, taxonomy

VERDICT_TO_POLARITY = {
    "TRUE_DISCLOSURE": "author_use",
    "NON_USE_STATEMENT": "non_use_statement",
    "TOPIC_ONLY": "topic_only",
    "FALSE_POSITIVE": "false_positive",
    "NO_AI_MENTION": "false_positive",  # vignettes always show the text
    "UNCLEAR": "unclear",
}


def human_labels(export: dict, mapping: dict[str, str]) -> tuple[dict, list]:
    """One machine-shaped label per vignette key + the raw items by key."""
    labels: dict[str, dict] = {}
    raw: list[tuple[str, dict]] = []
    for item in export["items"]:
        key = mapping[item["arxiv_id"]]
        true_d = item["verdict"] == "TRUE_DISCLOSURE"
        labels[key] = {
            "polarity": VERDICT_TO_POLARITY.get(item["verdict"],
                                                item["verdict"]),
            "epistemic_impact": (item.get("impact") or "not_applicable")
            if true_d else "not_applicable",
            "flags": {f: (f in (item.get("flags") or []))
                      for f in taxonomy.FLAGS},
            "categories": item.get("categories") or [],
            "locations": item.get("locations") or [],
        }
        raw.append((key, item))
    return labels, raw


def score(export: dict, manifest: dict) -> dict:
    if export.get("codebook_version") != taxonomy.TAXONOMY_VERSION:
        raise SystemExit(
            f"export codebook {export.get('codebook_version')!r} != "
            f"instrument {taxonomy.TAXONOMY_VERSION!r} — regrade, "
            "never remap")
    if export.get("project") != manifest.get("project"):
        raise SystemExit(f"export project {export.get('project')!r} != "
                         f"manifest {manifest.get('project')!r}")
    reviewer = export.get("reviewer")
    mapping = manifest["reviewers"][reviewer]["mapping"]
    ids = [it["arxiv_id"] for it in export["items"]]
    missing = sorted(set(mapping) - set(ids))
    if missing:
        raise SystemExit(f"export incomplete — missing items: {missing}")
    labels, raw = human_labels(export, mapping)
    res = comprehension.check([labels])
    # annotate location misses that are merely UNFILLED (allowed by the form
    # for non-disclosure verdicts) so they read as UX, not comprehension
    by_key = dict(raw)
    for row in res["rows"]:
        item = by_key[row["vignette"]]
        row["location_not_filled"] = (
            "location" in row["expected_mismatches"]
            and not (item.get("locations") or [])
            and item["verdict"] != "TRUE_DISCLOSURE")
    return res


def render_md(res: dict, reviewer: str) -> str:
    n = res["n_vignettes"]
    axes = ("polarity", "impact", "flags", "categories", "location")
    agree = {a: sum(a not in r["expected_mismatches"] for r in res["rows"])
             for a in axes}
    unfilled = sum(r["location_not_filled"] for r in res["rows"])
    lines = [
        f"# Human comprehension score — {reviewer} — taxonomy "
        f"v{taxonomy.TAXONOMY_VERSION} (SYNTHETIC vignettes; development "
        "evidence only, never accuracy)",
        "",
        "COMPUTED per-axis agreement with the expected objects: "
        + ", ".join(f"{a} {agree[a]}/{n}" for a in axes)
        + f"; all axes {res['expected_ok']}/{n}."
        + (f" ({unfilled} location misses are unfilled non-disclosure "
           "locations — allowed empty by the form, reported as UX)"
           if unfilled else ""),
        "",
        "| vignette | mismatched axes | human | expected |",
        "|---|---|---|---|",
    ]
    for r in res["rows"]:
        if not r["expected_mismatches"]:
            continue
        mism = ", ".join(r["expected_mismatches"])
        if r["location_not_filled"]:
            mism += " (location not filled)"
        hum = (f"{r['polarities'][0]}; {r['impacts'][0]}; "
               f"{r['flags'][0]}; {r['categories'][0]}; {r['locations'][0]}")
        lines.append(f"| {r['vignette']} | {mism} | {hum} | "
                     f"{json.dumps(r['expected'])} |")
    if all(not r["expected_mismatches"] for r in res["rows"]):
        lines.append("| — | (none) | | |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", default=None,
                    help="write the markdown report here as well")
    args = ap.parse_args()
    export = json.loads(Path(args.json).read_text())
    manifest = json.loads(Path(args.manifest).read_text())
    res = score(export, manifest)
    md = render_md(res, export.get("reviewer", "?"))
    if args.out:
        Path(args.out).write_text(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
