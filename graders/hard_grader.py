"""
Reply generation grader for the hard task.

Provides weighted scoring based on decision correctness, content relevance, and response quality.
"""

from env.models import Email

# Words indicating polite/professional tone
POLITE_WORDS = {
    "thank", "thanks", "appreciate", "please", "sorry", "excuse", "kindly",
    "regards", "sincerely", "best", "help", "happy", "glad", "welcome"
}


def _get_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text (words > 3 chars)."""
    words = text.lower().split()
    return {w.strip('.,!?;:-"\'') for w in words if len(w.strip('.,!?;:-"\'')) > 3}


def _calculate_keyword_overlap(reply: str, email_text: str) -> float:
    """
    Calculate keyword overlap between reply and email.

    Measures how well reply addresses email content.
    """
    if not reply or not email_text:
        return 0.0

    reply_keywords = _get_keywords(reply)
    email_keywords = _get_keywords(email_text)

    if not email_keywords or not reply_keywords:
        return 0.0

    overlap = reply_keywords & email_keywords
    return len(overlap) / len(email_keywords)


def _has_polite_tone(reply: str) -> float:
    """
    Check for polite/professional language in reply.

    Returns score 0-1 based on presence of courteous words.
    """
    if not reply:
        return 0.0

    reply_lower = reply.lower()
    polite_count = sum(1 for word in POLITE_WORDS if word in reply_lower)

    # Score increases with polite words, capped at 1.0
    return min(1.0, polite_count * 0.25)


def grade(reply_text: str, should_reply: bool, email: Email) -> float:
    """
    Calculate reward for reply generation with three weighted components.

    Scoring breakdown:
    - Decision correctness (0.5 weight): Should reply or not?
    - Content relevance (0.3 weight): Reply keywords match email?
    - Response quality (0.2 weight): Length ≥10 chars + polite tone?

    Args:
        reply_text: Generated reply text
        should_reply: Whether agent decided a reply is needed
        email: Email object with ground truth in true_label

    Returns:
        Reward in range [0, 1]
    """
    reply_required = (
        email.true_label.get("reply_required", False)
        if email.true_label
        else False
    )

    email_text = email.subject + " " + email.body

    # Component 1: Decision correctness (0.5 weight)
    decision_correct = should_reply == reply_required
    decision_score = 1.0 if decision_correct else 0.0

    # Component 2: Content relevance (0.3 weight)
    # Only applies if agent decided to reply
    relevance_score = 0.0
    if should_reply and reply_text and len(reply_text.strip()) > 0:
        relevance_score = _calculate_keyword_overlap(reply_text, email_text)

    # Component 3: Response quality (0.2 weight)
    # Checks length and tone
    quality_score = 0.0
    if should_reply and reply_text and len(reply_text.strip()) >= 10:
        # Base score for adequate length + tone bonus
        quality_score = 0.5 + _has_polite_tone(reply_text) * 0.5

    # Weighted combination
    total_score = (
        decision_score * 0.5 + relevance_score * 0.3 + quality_score * 0.2
    )

    return min(1.0, total_score)
