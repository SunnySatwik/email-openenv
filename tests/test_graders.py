"""
Unit tests for reward graders.

Tests the meaningful reward functions for each external grader task.
"""

import pytest
from graders import easy_grader, medium_grader, hard_grader


class TestSpamClassificationGrader:
    """Test spam classification grading."""

    def test_correct_spam(self):
        """Correct spam prediction should give full reward."""
        assert easy_grader.grade(True, True) == 1.0

    def test_correct_not_spam(self):
        """Correct non-spam prediction should give full reward."""
        assert easy_grader.grade(False, False) == 1.0

    def test_incorrect_spam(self):
        """Incorrect spam prediction should give zero reward."""
        assert easy_grader.grade(True, False) == 0.0

    def test_incorrect_not_spam(self):
        """Incorrect non-spam prediction should give zero reward."""
        assert easy_grader.grade(False, True) == 0.0


class TestPriorityGrader:
    """Test priority classification grading with graduated penalties."""

    def test_exact_match(self):
        """Perfect match should give full reward."""
        assert medium_grader.grade("high", "high") == 1.0
        assert medium_grader.grade("urgent", "urgent") == 1.0
        assert medium_grader.grade("low", "low") == 1.0

    def test_one_level_off(self):
        """One level off should give 0.5 reward."""
        assert medium_grader.grade("high", "medium") == 0.5
        assert medium_grader.grade("medium", "high") == 0.5
        assert medium_grader.grade("urgent", "high") == 0.5

    def test_two_levels_off(self):
        """Two levels off should give 0.25 reward."""
        assert medium_grader.grade("urgent", "medium") == 0.25
        assert medium_grader.grade("low", "high") == 0.25

    def test_three_levels_off(self):
        """Three levels off should give 0 reward."""
        assert medium_grader.grade("urgent", "low") == 0.0
        assert medium_grader.grade("low", "urgent") == 0.0

    def test_invalid_priority(self):
        """Invalid priority should give 0 reward."""
        assert medium_grader.grade("invalid", "high") == 0.0
        assert medium_grader.grade("high", "invalid") == 0.0

    def test_case_insensitive(self):
        """Grading should be case insensitive."""
        assert medium_grader.grade("HIGH", "high") == 1.0
        assert medium_grader.grade("High", "HIGH") == 1.0


class TestReplyGrader:
    """Test reply generation grading."""

    def test_correct_decision_no_reply_needed(self):
        """Correct decision not to reply."""
        reward = hard_grader.grade(
            reply="",
            should_reply=False,
            ground_truth_reply=None,
            reply_required=False,
        )
        assert reward == 0.7  # Decision correct

    def test_correct_decision_reply_needed(self):
        """Correct decision to reply with matching content."""
        reward = hard_grader.grade(
            reply="Thanks for confirming. Yes, 2pm works well for me.",
            should_reply=True,
            ground_truth_reply="Thanks for confirming. Yes, 2pm works well for me.",
            reply_required=True,
        )
        assert reward > 0.7  # Decision + content quality

    def test_missed_reply(self):
        """Failing to reply when required."""
        reward = hard_grader.grade(
            reply="",
            should_reply=False,
            ground_truth_reply="Thanks for reaching out.",
            reply_required=True,
        )
        assert reward == 0.2  # Partial credit for being done

    def test_empty_reply_when_needed(self):
        """Providing empty reply when one is needed."""
        reward = hard_grader.grade(
            reply="",
            should_reply=True,
            ground_truth_reply="Thanks",
            reply_required=True,
        )
        assert reward == 0.2

    def test_very_short_reply(self):
        """Reply too short when one is needed."""
        reward = hard_grader.grade(
            reply="ok",
            should_reply=True,
            ground_truth_reply="Thanks for your message. I'll review it.",
            reply_required=True,
        )
        assert reward == 0.2

    def test_similar_replies(self):
        """Similar but not exact replies should get good reward."""
        reward = hard_grader.grade(
            reply="Thank you for reaching out. I would be happy to help.",
            should_reply=True,
            ground_truth_reply="Thanks for your message. I'm happy to help.",
            reply_required=True,
        )
        assert 0.5 < reward <= 1.0

    def test_wrong_decision_to_reply(self):
        """Deciding to reply when not needed."""
        reward = hard_grader.grade(
            reply="Thanks for the newsletter",
            should_reply=True,
            ground_truth_reply=None,
            reply_required=False,
        )
        assert reward == 0.0  # Wrong decision


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
