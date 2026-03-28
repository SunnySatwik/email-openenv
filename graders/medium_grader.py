"""
Priority classification grader for the medium task.

Provides graduated penalties based on how far off the prediction is from ground truth.
"""


PRIORITY_LEVELS = {"low": 0, "medium": 1, "high": 2, "urgent": 3}


def grade(prediction: str, ground_truth: str) -> float:
    """
    Calculate reward for priority classification.

    Provides graduated penalties based on how far off the prediction is.
    - Perfect match: 1.0
    - Off by one level: 0.5
    - Off by two levels: 0.25
    - Off by three levels: 0.0

    Args:
        prediction: Predicted priority level
        ground_truth: True priority level

    Returns:
        Reward in range [0, 1]
    """
    pred_level = PRIORITY_LEVELS.get(prediction.lower(), -1)
    true_level = PRIORITY_LEVELS.get(ground_truth.lower(), -1)

    if pred_level == -1 or true_level == -1:
        return 0.0

    if pred_level == true_level:
        return 1.0

    distance = abs(pred_level - true_level)
    # Graduated penalty: each level distance reduces reward by 50%
    return max(0.0, 1.0 - (distance * 0.5))
