import math

from pipeline import annotate


def test_kappa_perfect_and_chance():
    assert annotate.cohens_kappa([("A", "A"), ("B", "B")]) == 1.0
    # one-sided marginals -> kappa 0 even with high raw agreement
    pairs = [("A", "A")] * 5 + [("A", "B")]
    assert abs(annotate.cohens_kappa(pairs)) < 1e-9
    assert math.isnan(annotate.cohens_kappa([]))


def test_highlight_marks_lexicon_matches():
    out = annotate.highlight("We thank ChatGPT and also Claude Opus for help "
                             "with the proof of Lemma 2.")
    assert "⟦ChatGPT⟧" in out
    assert "⟦" in out and "⟧" in out


def test_highlight_no_matches_passthrough():
    text = "a purely mathematical sentence about schemes"
    assert annotate.highlight(text) == text


def test_ingest_field_regex_roundtrip():
    body = """
title: something

VERDICT: TRUE_DISCLOSURE
CATEGORIES: writing_editing, proof_discovery
IMPACT: supportive
TOOLS: ChatGPT
LOCATION: acknowledgments
NOTES: borderline R1 case
"""
    fields = {k: v.strip() for k, v in annotate.FIELD_RE.findall(body)}
    assert fields["VERDICT"] == "TRUE_DISCLOSURE"
    assert fields["NOTES"] == "borderline R1 case"


def test_sample_strata_disjoint_and_seeded(fixture_con):
    a1, info1 = annotate.sample_strata(fixture_con, "scan-t", "cls-t", 5, 5, 5, 42)
    a2, _ = annotate.sample_strata(fixture_con, "scan-t", "cls-t", 5, 5, 5, 42)
    assert a1 == a2  # reproducible
    assert set(a1.values()) <= {"POS", "FLAG", "NEG"}
    # fixture: 2607.00001 author_use -> POS, .00002 flagged -> FLAG, .00003 -> NEG
    assert a1["2607.00001"] == "POS"
    assert a1["2607.00002"] == "FLAG"
    assert a1["2608.00003"] == "NEG"
    assert info1["POS"]["inclusion_prob"] == 1.0


def test_html_js_string_literals_do_not_span_lines():
    # a Python-eaten "\n" inside (then non-raw) HTML_JS shipped a REAL
    # newline inside a JS string literal — the whole packet <script> failed
    # to parse and every handler (usage-panel expand, autosave, export)
    # died silently (owner report 2026-08-18). Guard: JS strings are
    # double-quoted and never span lines, so quotes pair up per line.
    for ln in annotate.HTML_JS.split("\n"):
        assert ln.count('"') % 2 == 0, f"unbalanced quotes: {ln!r}"


def test_packet_scripts_parse_with_node(tmp_path):
    import re
    import shutil
    import subprocess

    import pytest

    from pipeline import comprehension_packets

    if shutil.which("node") is None:
        pytest.skip("node not installed")
    comprehension_packets.build_packets(["r1"], tmp_path)
    doc = (tmp_path / "packet_r1.html").read_text()
    scripts = re.findall(r"<script>(.*?)</script>", doc, re.S)
    assert len(scripts) == 2
    for i, body in enumerate(scripts):
        p = tmp_path / f"s{i}.js"
        p.write_text(body)
        r = subprocess.run(["node", "--check", str(p)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
