"""
Reward calculation and grading logic for email assistant tasks.

Implements meaningful, task-specific reward functions that go beyond binary feedback.
"""

from typing import Literal
from sentence_transformers import SentenceTransformer, util

_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


class SpamClassificationGrader:
    """Grades spam classification task with accuracy-based rewards."""

    @staticmethod
    def grade(prediction: bool, ground_truth: bool) -> float:
        """
        Calculate reward for spam classification.

        Args:
            prediction: Predicted spam classification
            ground_truth: True spam label

        Returns:
            Reward in range [0, 1]
        """
        if prediction == ground_truth:
            return 1.0
        return 0.0


class PriorityGrader:
    """Grades priority classification with graduated penalties."""

    PRIORITY_LEVELS = {"low": 0, "medium": 1, "high": 2, "urgent": 3}

    @staticmethod
    def grade(prediction: str, ground_truth: str) -> float:
        """
        Calculate reward for priority classification.

        Provides graduated penalties based on how far off the prediction is.
        Perfect match: 1.0
        Off by one level: 0.5
        Off by two levels: 0.25
        Off by three levels: 0.0

        Args:
            prediction: Predicted priority level
            ground_truth: True priority level

        Returns:
            Reward in range [0, 1]
        """
        pred_level = PriorityGrader.PRIORITY_LEVELS.get(prediction.lower(), -1)
        true_level = PriorityGrader.PRIORITY_LEVELS.get(ground_truth.lower(), -1)

        if pred_level == -1 or true_level == -1:
            return 0.0

        if pred_level == true_level:
            return 1.0

        distance = abs(pred_level - true_level)
        # Graduated penalty: each level distance reduces reward by 50%
        return max(0.0, 1.0 - (distance * 0.5))


class ReplyGrader:
    """Grades reply generation task using semantic similarity."""

    @staticmethod
    def _string_similarity(a: str, b: str) -> float:
        """Calculate cosine similarity ratio between two strings."""
        if not a or not b:
            return 0.0
        emb1 = _embedding_model.encode(a, convert_to_tensor=True)
        emb2 = _embedding_model.encode(b, convert_to_tensor=True)
        return float(util.cos_sim(emb1, emb2)[0][0].item())

    @staticmethod
    def grade(
        reply: str,
        should_reply: bool,
        ground_truth_reply: str | None,
        reply_required: bool,
    ) -> float:
        """
        Calculate reward for reply generation.

        Considers three aspects:
        1. Whether reply was correctly identified as needed/not needed
        2. If reply was needed, semantic similarity to ground truth
        3. Length appropriateness (penalize very short/empty replies)

        Args:
            reply: Generated reply text
            should_reply: Whether agent decided a reply is needed
            ground_truth_reply: Expected reply text
            reply_required: Whether reply is actually needed

        Returns:
            Reward in range [0, 1]
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
            similarity = ReplyGrader._string_similarity(reply, ground_truth_reply)
            content_reward = similarity * 0.9  # Max 0.9 from content
        else:
            # No ground truth available, give partial credit for reasonable reply
            content_reward = 0.6

        # Combine decision reward (0.7 base) with content quality (0.9 max)
        return min(1.0, decision_reward + content_reward * 0.3)


class TaskGrader:
    """Main grader coordinator for all tasks."""

    GRADERS = {
        "easy": SpamClassificationGrader,
        "medium": PriorityGrader,
        "hard": ReplyGrader,
    }

    @staticmethod
    def grade(
        task: str,
        action: dict,
        ground_truth: dict,
    ) -> float:
        """
        Grade an action given ground truth for the task.

        Args:
            task: Task type ('easy', 'medium', or 'hard')
            action: Action taken by agent (dict form)
            ground_truth: Ground truth labels from email

        Returns:
            Reward in range [0, 1]
        """
        if task == "easy":
            return SpamClassificationGrader.grade(
                action.get("is_spam", False),
                ground_truth.get("spam", False),
            )
        elif task == "medium":
            return PriorityGrader.grade(
                action.get("priority", "low"),
                ground_truth.get("priority", "low"),
            )
        elif task == "hard":
            return ReplyGrader.grade(
                action.get("reply_text", ""),
                action.get("should_reply", True),
                ground_truth.get("suggested_reply"),
                ground_truth.get("reply_required", False),
            )
        else:
            raise ValueError(f"Unknown task: {task}")


__all__ = [
    "SpamClassificationGrader",
    "PriorityGrader",
    "ReplyGrader",
    "TaskGrader",
]
