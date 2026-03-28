"""
Reply generation grader for the hard task.

Provides multi-aspect scoring based on reply decision and content quality.
"""

from difflib import SequenceMatcher


def _string_similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def grade(
    reply: str,
    should_reply: bool,
    ground_truth_reply: str | None,
    reply_required: bool,
) -> float:
    """
    Calculate reward for reply generation.

    Considers three aspects:
    1. Whether reply was correctly identified as needed/not needed (0.7 weight)
    2. If reply was needed, semantic similarity to ground truth (0.3 weight)
    3. Length appropriateness (penalize very short/empty replies)

    Args:
        reply: Generated reply text
        should_reply: Whether agent decided a reply is needed
        ground_truth_reply: Expected reply text
        reply_required: Whether reply is actually needed

    Returns:
        Reward in range [0, 1]
        - Perfect response: 1.0
        - Correct decision, good content: 0.7-1.0
        - Wrong decision: 0.0
    """
    # Check if decision to reply is correct
    decision_correct = should_reply == reply_required
    decision_reward = 0.7 if decision_correct else 0.0

    # If reply was not needed, return decision reward
    if not reply_required:
        return decision_reward

    # If reply was needed, grade the content
    if not should_reply or not reply or len(reply.strip()) < 10:
        # Didn't reply when should have, or reply is empty/too short
        return 0.2

    # Calculate semantic similarity to ground truth
    if ground_truth_reply:
        similarity = _string_similarity(reply, ground_truth_reply)
        content_reward = similarity * 0.9  # Max 0.9 from content
    else:
        # No ground truth available, give partial credit for reasonable reply
        content_reward = 0.6

    # Combine decision reward (0.7 base) with content quality (0.9 max)
    return min(1.0, decision_reward + content_reward * 0.3)
