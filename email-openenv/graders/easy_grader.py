"""
Spam classification grader for the easy task.

Evaluates spam classification with graduated rewards for reasonable mistakes.
"""

from env.models import Email

# Keywords that indicate promotional/spam-like content
SPAM_INDICATORS = {"free", "win", "offer", "click", "limited", "act now", "urgent"}


def _has_spam_characteristics(email: Email) -> bool:
    """Check if email has promotional/spam-like keywords."""
    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
    else:
        subject = email.subject
        body = email.body

    text = (subject + " " + body).lower()
    return any(keyword in text for keyword in SPAM_INDICATORS)


def grade_easy(action, email):
    """
    Calculate reward for spam classification with partial credit.
    """

    # Handle dict vs object
    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
        ground_truth = email.get("true_label", {}).get("spam", False)
    else:
        subject = email.subject
        body = email.body
        ground_truth = email.true_label.get("spam", False)

    text = (subject + " " + body).lower()

    spam_keywords = ["free", "win", "offer", "click", "prize"]
    has_spammy_features = any(word in text for word in spam_keywords)

    # Extract prediction correctly
    prediction = bool(action.get("is_spam", False))
    ground_truth = bool(ground_truth)

    # ✅ Correct prediction FIRST
    if prediction == ground_truth:
        return 1.0

    # ✅ Partial credit only for reasonable confusion
    if has_spammy_features and not ground_truth:
        return 0.5

    # ❌ Clearly wrong
    return 0.0
