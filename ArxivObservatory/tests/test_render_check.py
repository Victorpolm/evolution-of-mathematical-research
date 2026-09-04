from pipeline.render_check import (FUZZY_THRESHOLD, detex_quote, match_quote,
                                   normalize)


def test_detex_unwraps_commands():
    q = detex_quote(r"We thank \emph{ChatGPT} for \textbf{help}~with $n$ proofs")
    assert normalize(q) == "we thank chatgpt for help with n proofs"


def test_detex_drops_non_rendering_args():
    # \label{ChatGPT} must never make source-only evidence look rendered
    assert "ChatGPT" not in detex_quote(r"see \label{ChatGPT} equation")
    assert "ChatGPT" not in detex_quote(r"\cite{ChatGPT2026}")


def test_detex_href_keeps_text_arg_only():
    q = detex_quote(r"we used \href{https://chat.openai.com}{ChatGPT} daily")
    assert normalize(q) == "we used chatgpt daily"


def test_normalize_ligatures_hyphenation_dashes():
    assert normalize("the ﬁnal veri-\nfication — done") == 'the final verification - done'


def test_exact_match_across_linebreak_hyphenation():
    pdf = "We thank Chat-\nGPT for help with writ-\ning this paper."
    ok, method, score = match_quote("We thank ChatGPT for help with writing", pdf)
    assert ok and method == "exact" and score == 1.0


def test_absent_quote_misses():
    ok, method, _ = match_quote("entirely invented sentence goes here",
                                "Some other document text about mathematics.")
    assert not ok and method == "anchor-miss"


def test_near_paraphrase_not_certified():
    pdf = "We thank ChatGPT for help with writing this paper."
    ok, method, score = match_quote(
        "We thank ChatGPT for assistance with writing", pdf)
    assert not ok and method == "fuzzy" and score < FUZZY_THRESHOLD


def test_fuzzy_match_with_small_ocr_noise():
    pdf = "Acknowledgment. We are grateful to ChatGPT 4o for polishing the text."
    ok, method, score = match_quote(
        "grateful to ChatGPT-4o for polishing the text", pdf)
    assert ok and score >= 0.8


def test_short_quote_never_certified():
    ok, method, _ = match_quote("ChatGPT", "topic paper about ChatGPT models")
    assert not ok and method == "quote-too-short"


def test_stretched_match_penalized():
    # matched words spread across unrelated text must not score as rendered
    pdf = ("we thank chatgpt for extensive unrelated discussion, proof "
           "experiments, and assistance in revising this paper")
    ok, method, score = match_quote(
        "we thank chatgpt for proof assistance in this paper", pdf)
    assert not ok and score < FUZZY_THRESHOLD


def test_genuine_hyphen_survives_linebreak_hyphenation():
    ok, method, _ = match_quote("the human-AI collaboration framework works",
                                "the human-\nAI collaboration framework works")
    assert ok


def test_anchor_not_blocked_by_earlier_occurrence():
    # the correct noisy occurrence appears AFTER a common shingle elsewhere
    pdf = ("we thank the referee for comments. later in acknowledgments: "
           "we thank the ChatGPT assistant for polishing every proof carefully")
    ok, _, score = match_quote(
        "we thank the ChatGPT assistant for polishing every proof", pdf)
    assert ok and score >= FUZZY_THRESHOLD
