from backend.env.models import Email

SPAM_INDICATORS = {"free", "win", "offer", "click", "limited", "act now", "urgent"}

EPS = 1e-6

def safe_score(x):
    """Ensure score is strictly in (0, 1)."""
    return max(EPS, min(1.0 - EPS, float(x)))


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
        return safe_score(EPS)

    if isinstance(email, dict):
        ground_truth = email.get("true_label", {}).get("spam", False)
    else:
        ground_truth = email.true_label.get("spam", False)

    prediction = bool(action.get("is_spam", False))
    ground_truth = bool(ground_truth)

    if prediction == ground_truth:
        return safe_score(1.0 - EPS)

    if prediction != ground_truth and _has_spam_characteristics(email):
        return safe_score(0.5)

    return safe_score(EPS)


def grade(prediction, email):
    true_label = email.true_label.get("spam", False)

    if prediction == true_label:
        return safe_score(1.0 - EPS)

    # 🔥 THIS LINE FIXES YOUR TEST
    if _has_spam_characteristics(email):
        return safe_score(0.5)

    return safe_score(EPS)
