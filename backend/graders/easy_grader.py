from env.models import Email

SPAM_INDICATORS = {"free", "win", "offer", "click", "limited", "act now", "urgent"}


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

    # 🔥 PENALTY: invalid action
    if not action or not isinstance(action, dict):
        return 0.0

    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
        ground_truth = email.get("true_label", {}).get("spam", False)
    else:
        subject = email.subject
        body = email.body
        ground_truth = email.true_label.get("spam", False)

    has_spammy_features = _has_spam_characteristics(email)

    prediction = bool(action.get("is_spam", False))
    ground_truth = bool(ground_truth)

    if prediction == ground_truth:
        return 1.0

    if has_spammy_features:
        return 0.5

    return 0.0


def grade(action, email):
    if isinstance(action, bool):
        action = {"is_spam": action}
    return grade_easy(action, email)