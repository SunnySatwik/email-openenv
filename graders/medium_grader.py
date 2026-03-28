"""
Priority classification grader for the medium task.

Evaluates priority classification with distance-based scoring and keyword detection.
"""

PRIORITY_LEVELS = {"low": 0, "medium": 1, "high": 2, "urgent": 3}

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


def _detect_priority_from_content(email):
    text = _extract_text(email)

    if any(keyword in text for keyword in URGENT_KEYWORDS):
        return "urgent"
    elif any(keyword in text for keyword in HIGH_KEYWORDS):
        return "high"
    elif any(keyword in text for keyword in MEDIUM_KEYWORDS):
        return "medium"

    return None


def grade_medium(action, email):
    """
    Distance-based priority grading with keyword-based reasoning bonus.
    """

    # Extract ground truth safely
    if isinstance(email, dict):
        ground_truth = email.get("true_label", {}).get("priority", "low")
    else:
        ground_truth = email.true_label.get("priority", "low")

    prediction = str(action.get("priority", "low")).lower()
    ground_truth = str(ground_truth).lower()

    # Invalid labels
    if prediction not in PRIORITY_LEVELS or ground_truth not in PRIORITY_LEVELS:
        return 0.0

    pred_level = PRIORITY_LEVELS[prediction]
    true_level = PRIORITY_LEVELS[ground_truth]

    distance = abs(pred_level - true_level)

    # Base score (distance)
    if distance == 0:
        base_score = 1.0
    elif distance == 1:
        base_score = 0.6
    elif distance == 2:
        base_score = 0.3
    else:
        base_score = 0.0

    # 🔥 Bonus: keyword-based reasoning
    detected_priority = _detect_priority_from_content(email)

    if detected_priority == prediction and prediction != ground_truth:
        base_score += 0.1  # small bonus for reasonable guess

    return min(base_score, 1.0)