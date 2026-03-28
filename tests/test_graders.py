"""
Unit tests for reward graders.

Tests the meaningful reward functions for each external grader task.
"""

import pytest
from env import Email
from graders import easy_grader, medium_grader, hard_grader


class TestSpamClassificationGrader:
    """Test spam classification grading."""

    def test_correct_spam(self):
        """Correct spam prediction should give full reward."""
        email = Email(
            id="1",
            sender="spam@fake.com",
            subject="win free money!",
            body="click here to claim prize",
            timestamp="2024-01-01T00:00:00",
            true_label={"spam": True},
        )
        assert easy_grader.grade(True, email) == 1.0

    def test_correct_not_spam(self):
        """Correct non-spam prediction should give full reward."""
        email = Email(
            id="2",
            sender="boss@company.com",
            subject="meeting tomorrow",
            body="can you attend the meeting tomorrow at 2pm?",
            timestamp="2024-01-01T00:00:00",
            true_label={"spam": False},
        )
        assert easy_grader.grade(False, email) == 1.0

    def test_incorrect_with_spam_keywords(self):
        """Incorrect prediction on promotional email should give partial credit."""
        email = Email(
            id="3",
            sender="promo@store.com",
            subject="special offer: free shipping",
            body="click here for limited time offer",
            timestamp="2024-01-01T00:00:00",
            true_label={"spam": False},  # Actually not spam, but looks like it
        )
        assert easy_grader.grade(True, email) == 0.5

    def test_incorrect_without_spam_keywords(self):
        """Incorrect prediction on legitimate email should give zero reward."""
        email = Email(
            id="4",
            sender="friend@gmail.com",
            subject="hey how are you",
            body="just wanted to check in and say hello",
            timestamp="2024-01-01T00:00:00",
            true_label={"spam": False},
        )
        assert easy_grader.grade(True, email) == 0.0

    def test_missed_spam_with_keywords(self):
        """Missing spam that has promotional keywords should give partial credit."""
        email = Email(
            id="5",
            sender="scammer@notreal.com",
            subject="urgent: win free tickets",
            body="click now to claim your prize!",
            timestamp="2024-01-01T00:00:00",
            true_label={"spam": True},
        )
        assert easy_grader.grade(False, email) == 0.5


class TestPriorityGrader:
    """Test priority classification grading with distance-based scoring."""

    def test_exact_match(self):
        """Perfect match should give full reward."""
        email_high = Email(
            id="1",
            sender="boss@company.com",
            subject="important meeting",
            body="we need to meet about the project",
            timestamp="2024-01-01T00:00:00",
            true_label={"priority": "high"},
        )
        assert medium_grader.grade("high", email_high) == 1.0

        email_urgent = Email(
            id="2",
            sender="ceo@company.com",
            subject="urgent: system down",
            body="production is down, need immediate action",
            timestamp="2024-01-01T00:00:00",
            true_label={"priority": "urgent"},
        )
        assert medium_grader.grade("urgent", email_urgent) == 1.0

    def test_one_level_off(self):
        """One level off should give 0.6 reward."""
        email = Email(
            id="3",
            sender="peer@company.com",
            subject="meeting next week",
            body="can we schedule a meeting next week?",
            timestamp="2024-01-01T00:00:00",
            true_label={"priority": "high"},  # Actually high, but predicted medium
        )
        assert medium_grader.grade("medium", email) == 0.6

        email2 = Email(
            id="4",
            sender="urgent@company.com",
            subject="urgent approval needed",
            body="asap please",
            timestamp="2024-01-01T00:00:00",
            true_label={"priority": "high"},  # High, but predicted urgent
        )
        assert medium_grader.grade("urgent", email2) == 0.6

    def test_two_levels_off(self):
        """Two levels off should give 0.3 reward."""
        email = Email(
            id="5",
            sender="friend@company.com",
            subject="quick update",
            body="just a follow up",
            timestamp="2024-01-01T00:00:00",
            true_label={"priority": "high"},  # High, but predicted low
        )
        assert medium_grader.grade("low", email) == 0.3

    def test_three_levels_off(self):
        """Three levels off should give 0 reward (very wrong)."""
        email = Email(
            id="6",
            sender="urgent@company.com",
            subject="urgent: critical issue",
            body="immediate action required",
            timestamp="2024-01-01T00:00:00",
            true_label={"priority": "urgent"},  # Urgent, but predicted low
        )
        assert medium_grader.grade("low", email) == 0.0

    def test_invalid_priority(self):
        """Invalid priority should give 0 reward."""
        email = Email(
            id="7",
            sender="test@company.com",
            subject="test",
            body="test",
            timestamp="2024-01-01T00:00:00",
            true_label={"priority": "high"},
        )
        assert medium_grader.grade("invalid", email) == 0.0

    def test_case_insensitive(self):
        """Grading should be case insensitive."""
        email = Email(
            id="8",
            sender="test@company.com",
            subject="test message",
            body="test",
            timestamp="2024-01-01T00:00:00",
            true_label={"priority": "high"},
        )
        assert medium_grader.grade("HIGH", email) == 1.0
        assert medium_grader.grade("High", email) == 1.0


class TestReplyGrader:
    """Test reply generation grading with weighted components."""

    def test_correct_decision_no_reply_needed(self):
        """Correct decision not to reply gives decision points."""
        email = Email(
            id="1",
            sender="newsletter@store.com",
            subject="monthly newsletter",
            body="check out our latest products",
            timestamp="2024-01-01T00:00:00",
            true_label={"reply_required": False},
        )
        reward = hard_grader.grade("", False, email)
        assert reward == 0.5  # 0.5 weight for decision

    def test_correct_decision_reply_needed(self):
        """Correct decision to reply with good content."""
        email = Email(
            id="2",
            sender="boss@company.com",
            subject="can you attend the meeting?",
            body="we have a meeting at 2pm tomorrow",
            timestamp="2024-01-01T00:00:00",
            true_label={"reply_required": True},
        )
        reward = hard_grader.grade(
            "Thanks for confirming. Yes, 2pm works well for me.",
            True,
            email,
        )
        # Should get points for decision (0.5) + relevance (0.3) + quality (0.2)
        assert reward > 0.7

    def test_empty_reply_when_needed(self):
        """Empty reply when one is needed gets only decision point."""
        email = Email(
            id="3",
            sender="client@company.com",
            subject="need your feedback",
            body="please review the proposal",
            timestamp="2024-01-01T00:00:00",
            true_label={"reply_required": True},
        )
        reward = hard_grader.grade("", True, email)
        # Decision is correct (0.5) but reply is empty, no relevance/quality
        assert reward == 0.5

    def test_very_short_reply(self):
        """Reply too short (< 10 chars) doesn't get quality points."""
        email = Email(
            id="4",
            sender="colleague@company.com",
            subject="can you help with this task",
            body="we need someone experienced in python",
            timestamp="2024-01-01T00:00:00",
            true_label={"reply_required": True},
        )
        reward = hard_grader.grade("ok thanks", True, email)
        # Decision correct (0.5) + minimal relevance, but no quality (too short)
        assert 0.5 < reward < 0.8

    def test_good_reply_with_keywords(self):
        """Reply with good length and relevant keywords."""
        email = Email(
            id="5",
            sender="colleague@company.com",
            subject="python task help needed",
            body="can you help us with the python project?",
            timestamp="2024-01-01T00:00:00",
            true_label={"reply_required": True},
        )
        reward = hard_grader.grade(
            "Thanks for reaching out. I would be happy to help with the python project.",
            True,
            email,
        )
        # Should get decision (0.5) + good relevance + quality
        assert reward > 0.8

    def test_polite_tone_bonus(self):
        """Reply with polite words gets tone bonus."""
        email = Email(
            id="6",
            sender="customer@company.com",
            subject="request for help",
            body="need assistance with order",
            timestamp="2024-01-01T00:00:00",
            true_label={"reply_required": True},
        )
        reward = hard_grader.grade(
            "Thank you for reaching out. I appreciate your request and would be happy to help.",
            True,
            email,
        )
        # Decision + high relevance + polite tone quality bonus
        assert reward > 0.7

    def test_wrong_decision_to_reply(self):
        """Wrong decision to reply when not needed."""
        email = Email(
            id="7",
            sender="newsletter@store.com",
            subject="monthly newsletter",
            body="check out our latest products",
            timestamp="2024-01-01T00:00:00",
            true_label={"reply_required": False},
        )
        reward = hard_grader.grade(
            "Thanks for the newsletter",
            True,
            email,
        )
        # Wrong decision (0.0) + irrelevant context = 0
        assert reward == 0.0

    def test_missed_reply(self):
        """Failing to reply when required."""
        email = Email(
            id="8",
            sender="boss@company.com",
            subject="urgent action needed",
            body="please respond asap",
            timestamp="2024-01-01T00:00:00",
            true_label={"reply_required": True},
        )
        reward = hard_grader.grade("", False, email)
        # Wrong decision (should have replied) = 0.0
        assert reward == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
