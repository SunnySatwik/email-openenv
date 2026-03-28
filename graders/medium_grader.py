"""
Priority classification grader for the medium task.

Evaluates priority classification with distance-based scoring and keyword detection.
"""

from env.models import Email

PRIORITY_LEVELS = {"low": 0, "medium": 1, "high": 2, "urgent": 3}

# Keywords that indicate different priority levels
URGENT_KEYWORDS = {"urgent", "asap", "emergency", "critical", "immediately", "now"}
HIGH_KEYWORDS = {"meeting", "deadline", "important", "action required", "attention"}
MEDIUM_KEYWORDS = {"follow up", "review", "approval", "update"}


def _detect_priority_from_content(email: Email) -> str | None:
    """
    Detect priority hints from email content based on keywords.

    Args:
        email: Email object to analyze

    Returns:
        Suggested priority level or None if no clear indication
    """
    text = (email.subject + " " + email.body).lower()

    if any(keyword in text for keyword in URGENT_KEYWORDS):
        return "urgent"
    elif any(keyword in text for keyword in HIGH_KEYWORDS):
        return "high"
    elif any(keyword in text for keyword in MEDIUM_KEYWORDS):
        return "medium"

    return None


def grade(prediction: str, email: Email) -> float:
    """
    Calculate reward for priority classification.

    Scoring based on distance from ground truth:
    - Exact match: 1.0
    - 1 level off: 0.6
    - 2 levels off: 0.3
    - 3 levels off (very wrong): 0.0

    Args:
        prediction: Predicted priority level (low/medium/high/urgent)
        email: Email object with ground truth label

    Returns:
        Reward in range [0, 1]
    """
    ground_truth = email.true_label.get("priority", "low") if email.true_label else "low"

    pred_level = PRIORITY_LEVELS.get(prediction.lower(), -1)
    true_level = PRIORITY_LEVELS.get(ground_truth.lower(), -1)

    # Invalid priority level
    if pred_level == -1 or true_level == -1:
        return 0.0

    # Exact match
    if pred_level == true_level:
        return 1.0

    # Distance-based scoring
    distance = abs(pred_level - true_level)
    if distance == 1:
        return 0.6
    elif distance == 2:
        return 0.3
    else:  # distance == 3 (very wrong)
        return 0.0
