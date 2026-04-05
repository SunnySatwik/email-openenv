"""
Reply generation grader for the hard task.

Provides weighted scoring based on decision correctness, content relevance, and response quality.
"""

# ----------------------------
# Helper: Extract email fields
# ----------------------------

def _extract_email_fields(email):
    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
        reply_required = email.get("true_label", {}).get("reply_required", False)
    else:
        subject = email.subject
        body = email.body
        reply_required = email.true_label.get("reply_required", False)

    return subject, body, reply_required


# ----------------------------
# Helper: Keywords + Tone
# ----------------------------

POLITE_WORDS = {
    "thank", "thanks", "appreciate", "please", "sorry", "excuse", "kindly",
    "regards", "sincerely", "best", "help", "happy", "glad", "welcome"
}


def _get_keywords(text: str) -> set:
    words = text.lower().split()
    return {w.strip('.,!?;:-"\'') for w in words if len(w.strip('.,!?;:-"\'')) > 3}


def _calculate_keyword_overlap(reply: str, email_text: str) -> float:
    if not reply or not email_text:
        return 0.0

    reply_keywords = _get_keywords(reply)
    email_keywords = _get_keywords(email_text)

    if not email_keywords:
        return 0.0

    overlap = reply_keywords & email_keywords
    return len(overlap) / len(email_keywords)


def _has_polite_tone(reply: str) -> float:
    if not reply:
        return 0.0

    reply_lower = reply.lower()
    polite_count = sum(1 for word in POLITE_WORDS if word in reply_lower)

    return min(1.0, polite_count * 0.25)


# ----------------------------
# Main grader
# ----------------------------

def grade_hard(action, email):
    """
    Weighted scoring:
    - Decision correctness: 0.5
    - Content relevance: 0.3
    - Response quality: 0.2
    """

    subject, body, reply_required = _extract_email_fields(email)
    email_text = subject + " " + body

    reply_text = action.get("reply_text", "")
    should_reply = bool(action.get("should_reply", False))

    # Component 1: Decision correctness (0.5)
    decision_correct = should_reply == reply_required

    if not decision_correct:
        return 0.0
    decision_score = 1.0 if decision_correct else 0.0

    # Component 2: Content relevance (0.3)
    relevance_score = 0.0

    if should_reply:
        if reply_text.strip():  # only if reply exists
            raw_overlap = _calculate_keyword_overlap(reply_text, email_text)

            if raw_overlap == 0:
                relevance_score = 0.2
            else:
                relevance_score = min(1.0, raw_overlap * 1.5)
    # Component 3: Response quality (0.2)
    quality_score = 0.0
    if should_reply and len(reply_text.strip()) >= 10:
        quality_score = 0.5 + _has_polite_tone(reply_text) * 0.5

    # Final score (NO penalties or bonuses)
    total_score = (
        decision_score * 0.5 +
        relevance_score * 0.3 +
        quality_score * 0.2
    )

    return min(1.0, total_score)


# ----------------------------
# Wrapper (IMPORTANT for tests)
# ----------------------------

def grade(reply_text, should_reply, email):
    """
    Wrapper for test compatibility.

    Tests call:
        grade(reply_text, should_reply, email)

    We convert it into action dict for grade_hard.
    """
    action = {
        "reply_text": reply_text,
        "should_reply": should_reply
    }
    return grade_hard(action, email)