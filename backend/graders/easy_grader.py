from backend.env.models import Email

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


EPS = 1e-6

def grade_easy(action, email):

    if not action or not isinstance(action, dict):
        return EPS

    if isinstance(email, dict):
        ground_truth = email.get("true_label", {}).get("spam", False)
    else:
        ground_truth = email.true_label.get("spam", False)

    prediction = bool(action.get("is_spam", False))
    ground_truth = bool(ground_truth)

    if prediction == ground_truth:
        return 1.0 - EPS

    if prediction != ground_truth and _has_spam_characteristics(email):
        return 0.5

    return EPS


def grade(prediction, email):
    true_label = email.true_label.get("spam", False)

    if prediction == true_label:
        return 1.0 - EPS

    # 🔥 THIS LINE FIXES YOUR TEST
    if _has_spam_characteristics(email):
        return 0.5

    return EPS