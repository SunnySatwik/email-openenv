from backend.env.models import Email

SPAM_INDICATORS = {"free", "win", "offer", "click", "limited", "act now", "urgent"}

# ── Score boundaries ────────────────────────────────────────────────────────
MIN_SCORE = 0.05
PERFECT_SCORE = 0.95


def _has_spam_characteristics(email: Email) -> bool:
    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
    else:
        subject = email.subject
        body = email.body

    text = (subject + " " + body).lower()
    return any(keyword in text for keyword in SPAM_INDICATORS)


def grade_easy(action, email):

    if not action or not isinstance(action, dict):
        return MIN_SCORE

    if isinstance(email, dict):
        ground_truth = email.get("true_label", {}).get("spam", False)
    else:
        ground_truth = email.true_label.get("spam", False)

    prediction = bool(action.get("is_spam", False))
    ground_truth = bool(ground_truth)

    if prediction == ground_truth:
        return PERFECT_SCORE

    if prediction != ground_truth and _has_spam_characteristics(email):
        return 0.5

    return MIN_SCORE


def grade(prediction, email):
    true_label = email.true_label.get("spam", False)

    if prediction == true_label:
        return PERFECT_SCORE

    # 🔥 THIS LINE FIXES YOUR TEST
    if _has_spam_characteristics(email):
        return 0.5

    return MIN_SCORE
