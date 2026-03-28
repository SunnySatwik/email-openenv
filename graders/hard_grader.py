"""
Reply generation grader for the hard task.

Provides weighted scoring based on decision correctness, content relevance, and response quality.
"""

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

# --- Helpers ---

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
def grade_hard(action, email):
    """
    Advanced grading for reply generation with penalties and bonuses.
    """

    subject, body, reply_required = _extract_email_fields(email)
    email_text = (subject + " " + body)

    reply_text = action.get("reply_text", "")
    should_reply = bool(action.get("should_reply", False))

    # 🔹 Component 1: Decision correctness (0.5)
    decision_correct = should_reply == reply_required
    decision_score = 1.0 if decision_correct else 0.0

    # 🚨 Penalty: replying when not needed
    penalty = 0.0
    if should_reply and not reply_required:
        penalty = 0.3

    # 🔹 Component 2: Content relevance (0.3)
    relevance_score = 0.0
    if should_reply and reply_text.strip():
        relevance_score = _calculate_keyword_overlap(reply_text, email_text)

    # 🔹 Component 3: Response quality (0.2)
    quality_score = 0.0
    if should_reply and len(reply_text.strip()) >= 10:
        quality_score = 0.5 + _has_polite_tone(reply_text) * 0.5

    # 🚨 Penalty: low-effort / repetitive reply
    if should_reply and len(set(reply_text.split())) <= 2:
        penalty += 0.2

    # 🚀 Bonus: good structured reply
    bonus = 0.0
    if "thank" in reply_text.lower() and "regards" in reply_text.lower():
        bonus += 0.1

    # Final score
    total_score = (
        decision_score * 0.5 +
        relevance_score * 0.3 +
        quality_score * 0.2
        - penalty
        + bonus
    )

    return max(0.0, min(1.0, total_score))
