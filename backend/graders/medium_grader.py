PRIORITY_LEVELS = {"low": 0, "medium": 1, "high": 2, "urgent": 3}

EPS = 1e-6

def safe_score(x):
    """Ensure score is strictly in (0, 1)."""
    return max(EPS, min(1.0 - EPS, float(x)))

URGENT_KEYWORDS = {"urgent", "asap", "emergency", "critical", "immediately", "now"}
HIGH_KEYWORDS = {"meeting", "deadline", "important", "action required", "attention"}
MEDIUM_KEYWORDS = {"follow up", "review", "approval", "update"}


def _extract_text(email):
    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
    else:
        subject = email.subject
        body = email.body
    return (subject + " " + body).lower()


def grade_medium(action, email):
    # 🔥 PENALTY: invalid action
    if not action or not isinstance(action, dict):
        return safe_score(EPS)

    # Extract ground truth
    if isinstance(email, dict):
        ground_truth = email.get("true_label", {}).get("priority", "low")
    else:
        ground_truth = email.true_label.get("priority", "low")

    prediction = str(action.get("priority", "low")).lower()
    ground_truth = str(ground_truth).lower()

    # Invalid labels
    if prediction not in PRIORITY_LEVELS or ground_truth not in PRIORITY_LEVELS:
        return safe_score(EPS)

    pred_level = PRIORITY_LEVELS[prediction]
    true_level = PRIORITY_LEVELS[ground_truth]

    distance = abs(pred_level - true_level)

    # Base score
    if distance == 0:
        base_score = 1.0 - EPS
    elif distance == 1:
        base_score = 0.6
    elif distance == 2:
        base_score = 0.3
    else:
        base_score = EPS

    # 🔥 PENALTY: nonsense prediction
    if prediction not in ["low", "medium", "high", "urgent"]:
        base_score -= 0.2

    return safe_score(max(EPS, min(1.0 - EPS, base_score)))


def grade(action, email):
    if isinstance(action, str):
        action = {"priority": action}
    return grade_medium(action, email)