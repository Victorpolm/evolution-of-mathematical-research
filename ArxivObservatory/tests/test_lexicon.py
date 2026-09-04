from pipeline import lexicon


def hits_for(text):
    return lexicon.find_hits(lexicon.normalize(text))


def terms(text):
    return {h["term"] for h in hits_for(text)}


def test_plain_llm_hit():
    assert "ChatGPT" in terms("We thank ChatGPT for assistance with writing.")


def test_claude_person_name_is_known_fp():
    hs = hits_for("the Universit\\'e Claude Bernard Lyon 1 seminar")
    claude = [h for h in hs if h["term"] == "Claude"]
    assert claude and all(h["rule_class"] == "known_fp" for h in claude)


def test_negation_context_class():
    hs = hits_for("No AI tools were used in the preparation of this paper.")
    assert hs and any(h["rule_class"] == "negation_context" for h in hs)


def test_requires_context_blocks_bare_lean():
    assert "Lean" not in terms("We lean on the classical estimate of Serre.")


def test_requires_context_admits_lean_with_context():
    assert "Lean" in terms(
        "The main theorem was formalized in the Lean proof assistant.")


def test_accent_normalization_unmasks_names():
    text = lexicon.normalize(r"Universit\'e Claude Bernard")
    assert "Universite Claude Bernard" in text


def test_disclosure_genre_detected():
    hs = hits_for("Use of AI: ChatGPT was used to polish the exposition.")
    assert any(h["rule_class"] == "disclosure_genre" for h in hs)


def test_lexicon_version_present():
    assert lexicon.LEXICON_VERSION
