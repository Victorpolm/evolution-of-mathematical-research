"""Blinded HUMAN packets for the frozen comprehension exercise (current TAXONOMY_VERSION)
(review-12 B2: both intended graders label the exact frozen vignette
matrix independently, before seeing any machine output).

Design:
- vignette keys (which telegraph intended answers, e.g. "catalytic_wrong")
  are replaced by per-reviewer blinded ids V01..V16 in a per-reviewer
  seeded-shuffled order; the id->key mapping lives ONLY in the owner-only
  packets_manifest.json — reviewers must not open it;
- the form is the SAME one used for calibration packets (annotate.py), so
  human labels land in the same label space as machine output;
- the browser autosave key embeds the instrument-bundle digest, so a
  regenerated packet under a changed instrument can never silently restore
  stale answers (review-12 C2);
- packets are self-contained HTML with an Export-JSON button; scoring
  happens after export against comprehension.VIGNETTES expected objects.

Usage: python3 -m pipeline.comprehension_packets \
           [--reviewers reviewer1 reviewer2] [--out annotation/comprehension-v<N>]
No database access; no API calls.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import random
from pathlib import Path

from . import annotate, comprehension, taxonomy

PROTOCOL = (
    "Read TAXONOMY.md at the version above BEFORE starting; then label each "
    "vignette in one independent pass. The texts are SYNTHETIC — authored "
    "boundary cases, no real papers — so judge only what the text states. "
    "Do not consult the machine's labels, the other reviewer, or the "
    "manifest file. Borderline reasoning goes in the notes field; it feeds "
    "the codebook revision.")

BANNER = ("COMPREHENSION EXERCISE — frozen synthetic vignette set, "
          "independent first pass. Development evidence for the instrument; "
          "never release validity, never real-paper data.")


def _mark(text: str, terms: list[str]) -> str:
    out = html.escape(text)
    for t in sorted(terms, key=len, reverse=True):
        out = out.replace(html.escape(t), f"<mark>{html.escape(t)}</mark>")
    return out


def packet_html(project: str, reviewer: str, blinded: list[str],
                mapping: dict[str, str], texts: dict[str, tuple],
                codebook_excerpt: str) -> str:
    e = html.escape
    parts = [annotate.HTML_HEAD % {
        "title": e(f"Comprehension — {project} — {reviewer}"),
        "codebook": e(taxonomy.TAXONOMY_VERSION),
        "protocol": e(PROTOCOL)}]
    parts.append(f'<div style="background:#fff3cd;border:1px solid #e0c36a;'
                 f'border-radius:6px;padding:8px 14px;margin:10px 0;'
                 f'font-weight:600">{e(BANNER)}</div>')
    parts.append(f'<details><summary>polarity cheat-sheet (from the '
                 f'codebook — hover any control for its full definition)'
                 f'</summary><div class="meta">{codebook_excerpt}'
                 f'</div></details>')
    for i, vid in enumerate(blinded, 1):
        terms, context = texts[mapping[vid]]
        parts.append(f'<div class="item" id="item_{e(vid)}">')
        parts.append(f'<h3>Item {i} — {e(vid)}</h3>')
        parts.append(f'<div class="meta">synthetic vignette · marked terms: '
                     f'{e(", ".join(terms))}</div>')
        parts.append(f'<pre>{_mark(context, terms)}</pre>')
        parts.append(annotate._form_html(e(vid)))
        parts.append("</div>")
    js = lambda v: json.dumps(v).replace("<", "\\u003c")
    versions = {vid: 1 for vid in blinded}
    parts.append("<script>"
                 f"var PROJECT={js(project)};"
                 f"var REVIEWER={js(reviewer)};"
                 f"var CODEBOOK={js(taxonomy.TAXONOMY_VERSION)};"
                 f"var ITEMS={js(blinded)};"
                 f"var VERSIONS={js(versions)};"
                 "</script>")
    parts.append(annotate.HTML_JS)
    return "\n".join(parts)


def build_packets(reviewers: list[str], outdir: Path) -> dict:
    b = comprehension.bundle()
    digest = hashlib.sha256(
        json.dumps(b, sort_keys=True).encode()).hexdigest()[:10]
    # the digest in the project string binds browser autosave state (KEY =
    # "annot:"+PROJECT+":"+REVIEWER in annotate.HTML_JS) to THIS instrument
    project = (f"comprehension-v{taxonomy.TAXONOMY_VERSION.replace('.', '')}"
               f"-{digest}")
    keys = [k for k, _, _, _ in comprehension.VIGNETTES]
    texts = {k: (t, c) for k, t, c, _ in comprehension.VIGNETTES}
    cheat = "".join(
        f"<p><b>{html.escape(p)}</b>: {html.escape(d)}</p>"
        for p, d in taxonomy.POLARITIES.items())
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = {"project": project, "bundle": b,
                "generated": dt.datetime.now(dt.timezone.utc).isoformat(
                    timespec="seconds"),
                "note": ("OWNER-ONLY: the mapping below unblinds the "
                         "vignette ids — reviewers must not open this "
                         "file before exporting their verdicts"),
                "reviewers": {}}
    for rev in reviewers:
        rng = random.Random(f"{project}:{rev}")
        order_keys = keys[:]
        rng.shuffle(order_keys)
        blinded = [f"V{i + 1:02d}" for i in range(len(order_keys))]
        mapping = dict(zip(blinded, order_keys))
        doc = packet_html(project, rev, blinded, mapping, texts, cheat)
        path = outdir / f"packet_{rev}.html"
        path.write_text(doc)
        manifest["reviewers"][rev] = {
            "order": blinded, "mapping": mapping,
            "packet_sha256": hashlib.sha256(doc.encode()).hexdigest()}
    (outdir / "packets_manifest.json").write_text(
        json.dumps(manifest, indent=1))
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reviewers", nargs="+",
                    default=["reviewer1", "reviewer2"])
    ap.add_argument("--out", default="annotation/comprehension-v"
                + taxonomy.TAXONOMY_VERSION.replace(".", ""))
    args = ap.parse_args()
    m = build_packets(args.reviewers, Path(args.out))
    print(f"project {m['project']}")
    for rev, info in m["reviewers"].items():
        print(f"  packet_{rev}.html  sha256 {info['packet_sha256'][:16]}…")
    print(f"manifest (OWNER-ONLY, unblinds ids): "
          f"{args.out}/packets_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
