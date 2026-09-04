"""Tiered term lexicon shared by metadata and full-text scanners.

Tiers follow TECH_NOTES §2: 'llm' (LLM/agent systems), 'ml' (specialized math
AI / ML methods used as tools), 'prover' (proof assistants), 'cas' (computer
algebra), 'generic' (generic AI phrasing). The hackathon classification effort
focuses on 'llm' + 'generic'; other tiers are recorded for the cross-tool
story.

`requires_context` terms only produce hits when an AI/usage/acknowledgment
context word occurs within the context window — used for terms that are common
English or math words (Prism, Aristotle, Cursor, lean, ...).

Known-FP patterns (Claude Bernard, Séminaire Claude Chevalley, ...) downgrade a
hit to rule_class='known_fp' instead of dropping it, so the FP-lexicon effect
stays measurable.
"""

from __future__ import annotations

import dataclasses
import re

# Bump on ANY change to terms, context rules, FP patterns, or normalization.
# Recorded in every scan_runs row; never change lexicon and gold labels in the
# same commit (review E1).
LEXICON_VERSION = "2.1"

I = re.IGNORECASE


@dataclasses.dataclass(frozen=True)
class Term:
    name: str
    tier: str
    pattern: re.Pattern
    requires_context: bool = False
    context_re: re.Pattern | None = None  # term-specific licensing context


# Strong AI context for terms that collide with common math/English words.
AI_CONTEXT_RE = re.compile(
    r"\bAI\b|\bartificial intelligence\b|\bLLM\b|\blanguage model\b|\bchatbot\b|"
    r"\bOpenAI\b|\bChatGPT\b|\bGPT\b|\bAnthropic\b|\bGoogle\b|\bagent\w*\b|\bprompt\w*\b|"
    r"\bproofread\w*\b|\bLaTeX editor\b|\bwriting assistant\b|\btheorem prover\b|"
    r"\bHarmonic\b|\bfrenzymath\b|\bIDE\b|\bcode editor\b|\bautocomplet\w+\b",
    I,
)


TERMS: list[Term] = [
    # --- LLM / agent systems -------------------------------------------------
    Term("ChatGPT", "llm", re.compile(r"\bChat[- ]?GPT\b", I)),
    Term("OpenAI", "llm", re.compile(r"\bOpen\s?AI\b", I)),
    Term("GPT", "llm", re.compile(r"\bGPT(?:[- ]?[0-9oO][0-9A-Za-z.\-]*)?\b")),
    Term("o-series", "llm", re.compile(r"\bOpenAI[- ]o[1345]\b|\bo[1345][- ](?:mini|pro|high)\b")),
    Term("Codex", "llm", re.compile(r"\bCodex\b")),
    Term("Claude", "llm", re.compile(
        r"\b(?:Anthropic\s+)?Claude(?:\s+(?:AI|Code|Sonnet|Opus|Haiku|Fable|[0-9](?:\.[0-9])?))?\b", I)),
    Term("Anthropic", "llm", re.compile(r"\bAnthropic\b", I)),
    Term("Gemini", "llm", re.compile(r"\b(?:Google\s+)?Gemini\b", I)),
    Term("DeepThink", "llm", re.compile(r"\bDeep\s?Think\b")),
    Term("Bard", "llm", re.compile(r"\bGoogle\s+Bard\b|\bBard\b", I),
         requires_context=True, context_re=AI_CONTEXT_RE),
    Term("Copilot", "llm", re.compile(r"\b(?:GitHub\s+)?Copilot\b", I)),
    Term("DeepSeek", "llm", re.compile(r"\bDeepSeek(?:[- ][RV][0-9.]+)?\b", I)),
    Term("Grok", "llm", re.compile(r"\bGrok\b", I)),
    Term("xAI", "llm", re.compile(r"\bxAI\b")),
    Term("Llama", "llm", re.compile(r"\bLLaMA\b|\bLlama\s*[0-9]\b", I)),
    Term("Mistral", "llm", re.compile(r"\bMistral(?:\s+AI)?\b", I)),
    Term("Qwen", "llm", re.compile(r"\bQwen\b", I)),
    Term("Kimi", "llm", re.compile(r"\bKimi\b")),
    Term("GLM", "llm", re.compile(r"\bGLM-[0-9]\b")),
    Term("Perplexity", "llm", re.compile(r"\bPerplexity\s+(?:AI|Pro|search)\b", I)),
    Term("NotebookLM", "llm", re.compile(r"\bNotebookLM\b", I)),
    Term("Cursor", "llm", re.compile(r"\bCursor\b"),
         requires_context=True, context_re=AI_CONTEXT_RE),
    Term("Windsurf", "llm", re.compile(r"\bWindsurf\b", I)),
    Term("Prism", "llm", re.compile(r"\bPrism\b"),
         requires_context=True, context_re=AI_CONTEXT_RE),
    # 2026 math-agent systems (seen in pilot / awesome-ai-for-math)
    Term("Danus", "llm", re.compile(r"\bDanus\b")),
    Term("Rethlas", "llm", re.compile(r"\bRethlas\b")),
    Term("Archon", "llm", re.compile(r"\bArchon\b"),
         requires_context=True, context_re=AI_CONTEXT_RE),
    Term("Aletheia", "llm", re.compile(r"\bAletheia\b")),
    Term("Aristotle", "llm", re.compile(r"\bAristotle\b"),
         requires_context=True, context_re=AI_CONTEXT_RE),
    Term("Manus", "llm", re.compile(r"\bManus\b"),
         requires_context=True, context_re=AI_CONTEXT_RE),
    Term("Xiaozhua", "llm", re.compile(r"\bXiaozhua\b", I)),
    Term("Doubao", "llm", re.compile(r"\bDoubao\b", I)),
    Term("ERNIE", "llm", re.compile(r"\bERNIE(?:\s?Bot)?\b|\bWenxin\b")),
    Term("Tongyi", "llm", re.compile(r"\bTongyi\b|\bQianwen\b", I)),
    Term("Hunyuan", "llm", re.compile(r"\bHunyuan\b", I)),
    Term("ChatGLM", "llm", re.compile(r"\bChatGLM\b|\bZhipu\b", I)),
    Term("Co-Scientist", "llm", re.compile(r"\bCo[- ]?Scientist\b", I)),
    Term("AlphaProof", "llm", re.compile(r"\bAlphaProof\b", I)),
    Term("AlphaEvolve", "llm", re.compile(r"\bAlphaEvolve\b", I)),
    Term("AlphaGeometry", "llm", re.compile(r"\bAlphaGeometry\b", I)),
    Term("FunSearch", "llm", re.compile(r"\bFunSearch\b", I)),
    Term("PatternBoost", "ml", re.compile(r"\bPatternBoost\b", I)),
    Term("TxGraffiti", "ml", re.compile(r"\bTxGraffiti\b", I)),
    # --- generic AI phrasing -------------------------------------------------
    Term("large language model", "llm", re.compile(r"\blarge language models?\b|\bLLMs?\b", I)),
    Term("language model", "llm", re.compile(r"\blanguage[- ]model(?:s|-based)?\b", I), requires_context=True),
    Term("reasoning model", "llm", re.compile(r"\breasoning models?\b", I)),
    Term("foundation model", "llm", re.compile(r"\bfoundation models?\b", I), requires_context=True),
    Term("frontier model", "llm", re.compile(r"\bfrontier models?\b", I)),
    Term("chatbot", "llm", re.compile(r"\bchat-?bots?\b", I)),
    Term("generative AI", "generic", re.compile(
        r"\bgenerative\s+(?:AI|artificial intelligence)\b|\bGenAI\b", I)),
    Term("AI-compound", "generic", re.compile(
        r"\bAI[- ](?:assisted|generated|aided|based|driven|powered|supported)\b|"
        r"\bAI\s+(?:assistance|assistants?|tools?|systems?|agents?|models?|chatbots?|software|usage|use|help)\b|"
        r"\b(?:help|assistance|use|aid)\s+of\s+(?:an\s+)?AI\b", I)),
    Term("AI-bare", "generic", re.compile(r"\bAI\b"), requires_context=True),
    Term("artificial intelligence", "generic", re.compile(r"\bartificial intelligence\b", I)),
    Term("machine learning", "ml", re.compile(r"\bmachine[- ]learn(?:ing|ed)\b", I),
         requires_context=True),
    Term("neural network", "ml", re.compile(r"\bneural networks?\b", I), requires_context=True),
    Term("reinforcement learning", "ml", re.compile(r"\breinforcement learning\b", I),
         requires_context=True),
    # --- proof assistants ----------------------------------------------------
    Term("Lean", "prover", re.compile(r"\bLean\s*4\b|\bLean\b"), requires_context=True),
    Term("mathlib", "prover", re.compile(r"\bmathlib\b", I)),
    Term("Coq", "prover", re.compile(r"\bCoq\b|\bRocq\b")),
    Term("Isabelle", "prover", re.compile(r"\bIsabelle\b")),
    Term("Agda", "prover", re.compile(r"\bAgda\b")),
    Term("Metamath", "prover", re.compile(r"\bMetamath\b", I)),
    Term("proof assistant", "prover", re.compile(
        r"\bproof assistants?\b|\btheorem provers?\b|\bformal(?:ly)?[- ]verif\w+\b|\bformaliz\w+\b", I)),
    # --- computer algebra / math software ------------------------------------
    Term("Mathematica", "cas", re.compile(r"\bMathematica\b|\bWolfram(?:\s+Alpha|Cloud)?\b")),
    Term("Maple", "cas", re.compile(r"\bMaple\b")),
    Term("Magma", "cas", re.compile(r"\bMagma\b"), requires_context=True),
    Term("SageMath", "cas", re.compile(r"\bSageMath\b|\bSage\b")),
    Term("GAP", "cas", re.compile(r"\bGAP\b"), requires_context=True),
    Term("PARI/GP", "cas", re.compile(r"\bPARI(?:/GP)?\b")),
    Term("Macaulay2", "cas", re.compile(r"\bMacaulay\s?2\b", I)),
    Term("Singular", "cas", re.compile(r"\bSingular\b"), requires_context=True),
    Term("OSCAR", "cas", re.compile(r"\bOSCAR\b")),
    Term("polymake", "cas", re.compile(r"\bpolymake\b", I)),
    Term("SnapPy", "cas", re.compile(r"\bSnapPy\b")),
    Term("SymPy", "cas", re.compile(r"\bSymPy\b", I)),
    Term("Matlab", "cas", re.compile(r"\bMATLAB\b", I)),
]

# Context words that license a requires_context hit (searched in the +-window
# around the term). Deliberately generous: usage verbs, acknowledgment genre,
# software genre, AI words.
CONTEXT_RE = re.compile(
    r"\backnowledg\w+\b|\bthanks?\b|\bgrateful\b|\bdeclar\w+\b|\bdisclos\w+\b|"
    r"\buse[ds]?\b|\busing\b|\butili[sz]\w+\b|\bassist\w+\b|\bhelp\w*\b|\bemploy\w+\b|"
    r"\bperform\w+\b|\bcomput\w+\b|\bverif\w+\b|\bcheck\w+\b|\bcalculat\w+\b|"
    r"\bsoftware\b|\bpackage\b|\bsystem\b|\btool\b|\bcode\b|\bscript\b|\bprogram\w*\b|"
    r"\bversion\b|\bv\.?\s?[0-9]+(?:\.[0-9]+)?\b|"
    r"\bAI\b|\bartificial intelligence\b|\bLLM\b|\blanguage model\b|\bmodel\b|"
    r"\bproof assistant\b|\btheorem prover\b|\bformaliz\w+\b|\bagent\w*\b|\bprompt\w*\b|"
    r"\bwrote\b|\bwritten\b|\bgenerat\w+\b|\bproduc\w+\b|\bedit\w*\b|\bpolish\w*\b|"
    r"\btranslat\w+\b|\bproofread\w*\b|\bdraft\w*\b|"
    r"\bno\b|\bnot\b|\bwithout\b|\bfree of\b|-free\b",
    I,
)
CONTEXT_WINDOW = 240  # chars each side for requires_context licensing

# Patterns that mark a matched term as a known false positive when they overlap
# the hit (person names, places, notation). Grown from the pilot FP lexicon.
KNOWN_FP_RES: list[re.Pattern] = [
    re.compile(r"Claude[\s~-]+(?:Bernard|Chevalley|Shannon|Deb(?:ussy)?|L[ée]vi-?Strauss|Michel)", I),
    re.compile(r"(?:Universit[ée]|University)[\s~-]+Claude", I),
    re.compile(r"S[ée]minaire[\s~-]+Claude", I),
    re.compile(r"(?:Jean|Pierre|Paul|Marie|Henri|Fran[cç]ois)[\s~-]+Claude\b", I),
    re.compile(r"Claude[\s~-]+(?:Bernard|Lyon)", I),
    re.compile(r"\bGrok\w*\b.{0,30}\bHeinlein\b", I),
    re.compile(r"\ba magma\b|\bmagmas\b|\bmagma (?:operation|structure|algebra)\b", I),
    re.compile(r"\bspectral gap\b|\bmass gap\b|\bgap (?:theorem|condition|estimate)\b", I),
    re.compile(r"\bmind the gap\b", I),
    # Cartan symmetric-space classification types AI, AII, ... and labels/refs
    re.compile(r"\b(?:type|types|pair|pairs|form|forms|class)[\s~]+(?:\\mathrm\{)?A(?:I{1,3}|IV)\b"),
    re.compile(r"\\mathrm\{A?I{1,3}\}|\bAI{0,2}\$?_\{?[0-9n]"),
    re.compile(r"(?:label|ref|eqref|cite)\s*\{[^}]{0,40}\bAI\b[^}]{0,40}\}"),
]

# Disclosure-genre section headers / statement openers (drives rule_class and
# later 'location' coding). New genres from the pilot included.
DISCLOSURE_GENRE_RE = re.compile(
    r"\bAI\s+Usage\b|\bUsage of LLM'?s?\b|\bUse of (?:AI|LLMs?|generative AI|artificial intelligence)\b|"
    r"\b(?:AI|LLM|Tool)\s+disclosure\b|\bTool and computational resource disclosure\b|"
    r"\bDeclarations?\b|\bStatement on (?:AI|the use)\b|\bGenerative AI statement\b|"
    r"\bLLM usage\b|\bAI transparency\b|\bDuring the preparation of this (?:work|manuscript)\b|"
    r"\bAI generated,? human verified\b|\bHuman verification\b|"
    r"\btake[sn]? (?:full )?responsibility\b|\bassumes? (?:full )?responsibility\b",
    I,
)

ACK_RE = re.compile(
    r"\backnowledg(?:e)?ments?\b|\bthanks?\b|\bgrateful\b", I)

USAGE_RE = re.compile(
    r"\buse[ds]?\b|\busing\b|\butili[sz]ed\b|\bassist(?:ed|ance)?\b|\bhelp(?:ed|ful)?\b|"
    r"\bproofread(?:ing)?\b|\bedit(?:ed|ing)?\b|\bgrammar\b|\blanguage\b|\bwriting\b|"
    r"\bdraft(?:ed|ing)?\b|\bprepar(?:e|ed|ation)\b|\bpolish(?:ed|ing)?\b|"
    r"\bgenerat(?:e|ed|ion|ing)\b|\bsuggest(?:ed|ion)?\b|\bverif(?:y|ied|ication)\b|"
    r"\bcheck(?:ed|ing)?\b|\bdiscover(?:ed|y)?\b|\bobtained\b|\bconversation\b|\bprompt(?:s|ed|ing)?\b",
    I,
)

NEGATION_RE = re.compile(
    r"\bno\s+(?:AI|artificial intelligence|generative AI|LLMs?|large language models?|ChatGPT|chatbots?)\b|"
    r"\bnot\s+(?:use|used|using|utili[sz]e|utili[sz]ed|involve|employed?)\b|"
    r"\bwithout\s+(?:the\s+)?(?:use|assistance|help|aid)\b|\bAI-free\b|"
    r"\b(?:this|present)\s+paper\b[^\n.]{0,160}\b(?:completely\s+)?hand-?craft(?:ed)?\b",
    I,
)


def classify_context(text: str, start: int, end: int, radius: int = 300) -> str:
    """Heuristic rule class for a hit span within `text`."""
    lo, hi = max(0, start - radius), min(len(text), end + radius)
    window = text[lo:hi]
    for fp in KNOWN_FP_RES:
        for m in fp.finditer(window):
            if lo + m.start() <= end and lo + m.end() >= start:
                return "known_fp"
    if NEGATION_RE.search(window):
        return "negation_context"
    if DISCLOSURE_GENRE_RE.search(window):
        return "disclosure_genre"
    if ACK_RE.search(window) and USAGE_RE.search(window):
        return "ack_usage"
    if ACK_RE.search(window):
        return "ack_context"
    if USAGE_RE.search(window):
        return "usage_context"
    return "plain"


# symbolic accents (\'e) may sit flush against the letter; letter-named
# accents (\u, \v, \H, \t, \c, \d, \b) must be delimited so \thanks, \begin,
# \cite etc. are not consumed
TEX_ACCENT_RE = re.compile(r"\\(?:[`'^\"~=.]|[uvHtcdb](?=[\s{]))\s*\{?([a-zA-Z])\}?")


def normalize(text: str) -> str:
    """Light de-TeX so accent macros don't hide names (Universit\\'e Claude)."""
    text = TEX_ACCENT_RE.sub(r"\1", text)
    return text.replace("~", " ")


def find_hits(text: str) -> list[dict]:
    """All lexicon hits in `text` as dicts (term, tier, offset, rule_class)."""
    hits = []
    for term in TERMS:
        for m in term.pattern.finditer(text):
            if term.requires_context:
                lo = max(0, m.start() - CONTEXT_WINDOW)
                hi = min(len(text), m.end() + CONTEXT_WINDOW)
                ctx = text[lo:m.start()] + " " + text[m.end():hi]
                if not (term.context_re or CONTEXT_RE).search(ctx):
                    continue
            hits.append({
                "term": term.name,
                "tier": term.tier,
                "offset": m.start(),
                "matched": m.group(0),
                "rule_class": classify_context(text, m.start(), m.end()),
            })
    return hits
