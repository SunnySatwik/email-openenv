"""
Hard Grader — Reply Generation Task

Scores an agent's reply decision and content on a continuous [0.0, 1.0] scale.

Weight breakdown:
  Decision correctness  → 0.50  (should_reply matches ground truth)
  Content relevance     → 0.30  (reply addresses the email's topic)
  Response quality      → 0.20  (well-formed, non-generic, appropriate length)

When OPENAI_API_KEY is set, relevance + quality are scored by an LLM and
blended (70%) with the heuristic scores (30%) for more nuanced evaluation.
Without a key, the heuristic-only path runs and is fully self-contained.
"""

import os
import json
import re
from openai import OpenAI

# ── Tunable constants ────────────────────────────────────────────────────────

WEIGHT_DECISION   = 0.50
WEIGHT_RELEVANCE  = 0.30
WEIGHT_QUALITY    = 0.20

# Blend ratio when LLM scoring is available: LLM * BLEND + heuristic * (1 - BLEND)
LLM_BLEND = 0.70

MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# Common stopwords to exclude from relevance overlap
_STOPWORDS = {
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "they",
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "can", "could", "this",
    "that", "these", "those", "there", "here", "so", "if", "as", "by",
    "from", "not", "no", "up", "out", "about", "just", "also", "hi",
    "hello", "dear", "thanks", "thank", "please", "regards",
}

# Phrases that signal a lazy/templated reply — penalise these
_FILLER_PHRASES = [
    "thank you for your email",
    "thank you for reaching out",
    "i hope this email finds you well",
    "please let me know if you have any questions",
    "feel free to reach out",
    "best regards",
    "kind regards",
]

# Signals that a reply is substantive
_QUALITY_SIGNALS = [
    r"\b(will|can|shall|would)\b",   # commitment language
    r"\b(yes|no|confirm|agree|disagree|approved|declined)\b",  # clear answers
    r"\b(by|before|on|at)\s+\w+day\b",  # time references ("by Monday")
    r"\b\d{1,2}[:/]\d{2}\b",            # time ("2:00", "14:00")
    r"\b(attached|sent|forwarded|shared)\b",  # action confirmations
]


# ── Optional LLM scoring ─────────────────────────────────────────────────────

def _llm_score(email_text: str, reply_text: str) -> tuple[float, float]:
    """
    Ask an LLM to score relevance and quality of the reply.
    Returns (relevance, quality) each in [0.0, 1.0].
    Falls back to (None, None) if unavailable so the caller can skip blending.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("API_BASE_URL")

    if not api_key:
        return None, None

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        prompt = (
            "You are evaluating an AI-generated email reply. "
            "Score it on two dimensions, each from 0.0 to 1.0.\n\n"
            f"ORIGINAL EMAIL:\n{email_text}\n\n"
            f"REPLY:\n{reply_text}\n\n"
            "Scoring criteria:\n"
            "  relevance (0–1): Does the reply directly address the email's "
            "specific topic, questions, or requests? "
            "Generic text that could apply to any email scores low.\n"
            "  quality (0–1): Is the reply well-written, appropriately "
            "concise, professional, and free of filler phrases? "
            "Does it include a clear action or answer?\n\n"
            'Respond ONLY with valid JSON: {"relevance": float, "quality": float}'
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=60,
        )

        content = response.choices[0].message.content.strip()
        content = re.sub(r"```(?:json)?|```", "", content).strip()
        parsed = json.loads(content)

        return (
            float(min(1.0, max(0.0, parsed.get("relevance", 0)))),
            float(min(1.0, max(0.0, parsed.get("quality", 0)))),
        )

    except Exception:
        return None, None


# ── Heuristic sub-scorers ────────────────────────────────────────────────────

def _heuristic_relevance(email_text: str, reply_text: str) -> float:
    """
    Measures topical overlap between the email and the reply,
    ignoring stopwords so generic words don't inflate the score.
    Returns a value in [0.0, 1.0].
    """
    email_words = {
        w for w in re.findall(r"[a-z]+", email_text.lower())
        if w not in _STOPWORDS and len(w) > 2
    }
    reply_words = set(re.findall(r"[a-z]+", reply_text.lower()))

    if not email_words:
        return 0.0

    overlap = len(email_words & reply_words)
    # Normalise: full credit at 6+ meaningful overlapping words
    return min(overlap / 6, 1.0)


def _heuristic_quality(reply_text: str) -> float:
    """
    Scores reply quality using length, structure, filler detection,
    and substantive content signals.
    Returns a value in [0.0, 1.0].
    """
    text  = reply_text.strip()
    words = text.split()
    word_count = len(words)
    score = 0.0

    # ── Length score (up to 0.35) ────────────────────────────────────────────
    # Too short (<5 words) or too long (>120 words) both penalised
    if word_count >= 10:
        length_score = 1.0
    elif word_count >= 5:
        length_score = 0.5
    else:
        length_score = 0.1
    if word_count > 120:
        length_score *= 0.7   # verbose replies lose some credit
    score += length_score * 0.35

    # ── Filler penalty (up to –0.20) ─────────────────────────────────────────
    lower = text.lower()
    filler_hits = sum(1 for phrase in _FILLER_PHRASES if phrase in lower)
    # One filler phrase is tolerable; more than one suggests a template reply
    filler_penalty = min(filler_hits * 0.10, 0.20)
    score -= filler_penalty

    # ── Substantive content bonus (up to 0.40) ───────────────────────────────
    signal_hits = sum(
        1 for pattern in _QUALITY_SIGNALS
        if re.search(pattern, lower)
    )
    score += min(signal_hits / len(_QUALITY_SIGNALS), 1.0) * 0.40

    # ── Basic structure bonus (up to 0.25) ───────────────────────────────────
    # Reward having at least two sentences (shows a composed reply, not a fragment)
    sentence_count = len(re.findall(r"[.!?]+", text))
    if sentence_count >= 2:
        score += 0.25
    elif sentence_count == 1:
        score += 0.10

    return float(min(1.0, max(0.0, score)))


# ── Spam guard ───────────────────────────────────────────────────────────────

_SPAM_SIGNALS = [
    "unsubscribe", "click here", "free money", "limited time",
    "exclusive offer", "buy now", "act now", "winner", "lottery",
    "100% free", "no credit card", "cash prize",
]

def _looks_like_spam(subject: str, body: str) -> bool:
    text = (subject + " " + body).lower()
    hits = sum(1 for s in _SPAM_SIGNALS if s in text)
    return hits >= 2


# ── Main grader ───────────────────────────────────────────────────────────────

def grade_hard(action: dict, email) -> float:
    """
    Grade a reply-generation action against the email's ground truth.

    Args:
        action: dict with keys "should_reply" (bool) and "reply_text" (str)
        email:  Email object or dict with subject, body, true_label

    Returns:
        Reward in [0.0, 1.0]
    """
    if not action or not isinstance(action, dict):
        return 0.0

    # ── Unpack email ─────────────────────────────────────────────────────────
    if isinstance(email, dict):
        subject    = email.get("subject", "")
        body       = email.get("body", "")
        true_label = email.get("true_label", {})
    else:
        subject    = email.subject
        body       = email.body
        true_label = email.true_label

    reply_required = true_label.get("reply_required", False)
    reply_text     = (action.get("reply_text") or "").strip()
    should_reply   = bool(action.get("should_reply", False))

    # ── Spam guard ────────────────────────────────────────────────────────────
    # Never reward replying to what looks like spam, regardless of true_label
    if should_reply and _looks_like_spam(subject, body):
        return 0.0

    # ── Decision score ────────────────────────────────────────────────────────
    if should_reply != reply_required:
        return 0.0

    decision_score = WEIGHT_DECISION  # 0.50

    # If the correct decision was "don't reply", we're done
    if not should_reply:
        return decision_score

    # If agent decided to reply but produced nothing, no content credit
    if not reply_text:
        return decision_score

    # ── Content scoring ───────────────────────────────────────────────────────
    email_text = subject + " " + body

    h_relevance = _heuristic_relevance(email_text, reply_text)
    h_quality   = _heuristic_quality(reply_text)

    llm_relevance, llm_quality = _llm_score(email_text, reply_text)

    if llm_relevance is not None and llm_quality is not None:
        # Blend LLM and heuristic scores
        relevance = LLM_BLEND * llm_relevance + (1 - LLM_BLEND) * h_relevance
        quality   = LLM_BLEND * llm_quality   + (1 - LLM_BLEND) * h_quality
    else:
        relevance = h_relevance
        quality   = h_quality

    relevance_score = relevance * WEIGHT_RELEVANCE  # up to 0.30
    quality_score   = quality   * WEIGHT_QUALITY    # up to 0.20

    return round(decision_score + relevance_score + quality_score, 4)


# ── Convenience wrapper ───────────────────────────────────────────────────────

def grade(reply_text: str, should_reply: bool, email) -> float:
    return grade_hard(
        {"reply_text": reply_text, "should_reply": should_reply},
        email,
    )