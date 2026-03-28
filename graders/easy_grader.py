"""
Spam classification grader for the easy task.

Provides binary accuracy-based rewards.
"""


def grade(prediction: bool, ground_truth: bool) -> float:
    """
    Calculate reward for spam classification.

    Args:
        prediction: Predicted spam classification
        ground_truth: True spam label

    Returns:
        Reward in range [0, 1]
        - 1.0 if prediction correct
        - 0.0 if prediction incorrect
    """
    return 1.0 if prediction == ground_truth else 0.0
