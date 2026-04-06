"""
Unit tests for the EmailEnv environment.

Tests the core OpenEnv interface and environment behavior.
"""

import pytest
from env import EmailEnv, Email, Observation, StepInfo, Reward


class TestEmailEnvInitialization:
    """Test environment initialization."""

    def test_valid_task_easy(self):
        """Initialize with easy task."""
        env = EmailEnv(task="easy")
        assert env.task == "easy"

    def test_valid_task_medium(self):
        """Initialize with medium task."""
        env = EmailEnv(task="medium")
        assert env.task == "medium"

    def test_valid_task_hard(self):
        """Initialize with hard task."""
        env = EmailEnv(task="hard")
        assert env.task == "hard"

    def test_invalid_task(self):
        """Invalid task should raise error."""
        with pytest.raises(ValueError):
            EmailEnv(task="invalid_task")

    def test_custom_max_steps(self):
        """Custom max_steps should be respected."""
        env = EmailEnv(task="easy", max_steps=20)
        assert env.max_steps == 20

    def test_seed_reproducibility(self):
        """Same seed should produce same episode order."""
        env1 = EmailEnv(task="easy", seed=42)
        env1.reset()
        order1 = [e.id for e in env1.emails[:3]]

        env2 = EmailEnv(task="easy", seed=42)
        env2.reset()
        order2 = [e.id for e in env2.emails[:3]]

        assert order1 == order2


class TestResetInterface:
    """Test reset() method."""

    def test_reset_returns_observation(self):
        """reset() should return Observation."""
        env = EmailEnv(task="easy")
        obs = env.reset()
        assert isinstance(obs, Observation)

    def test_observation_has_email(self):
        """Returned observation should have email."""
        env = EmailEnv(task="easy")
        obs = env.reset()
        assert isinstance(obs.email, Email)
        assert obs.email.id

    def test_observation_has_task(self):
        """Returned observation should have task."""
        env = EmailEnv(task="medium")
        obs = env.reset()
        assert obs.task == "medium"

    def test_reset_clears_episode(self):
        """reset() should reset episode state."""
        env = EmailEnv(task="easy", max_steps=10)
        obs = env.reset()
        assert env.step_count == 0
        assert env.current_email_idx == 0
        assert len(env.episode_rewards) == 0


class TestStepInterface:
    """Test step() method."""

    def test_step_returns_four_values(self):
        """step() should return (observation, reward, done, info)."""
        env = EmailEnv(task="easy")
        env.reset()
        result = env.step({"is_spam": False})
        assert len(result) == 4

    def test_step_returns_correct_types(self):
        """step() should return correct types."""
        env = EmailEnv(task="easy")
        env.reset()
        obs, reward, done, info = env.step({"is_spam": False})

        assert isinstance(obs, Observation)
        assert isinstance(reward, Reward)
        assert isinstance(done, bool)
        assert isinstance(info, StepInfo)

    def test_step_increments_counter(self):
        """step() should increment step counter."""
        env = EmailEnv(task="easy")
        env.reset()
        assert env.step_count == 0
        env.step({"is_spam": False})
        assert env.step_count == 1

    def test_step_accumulates_reward(self):
        """step() should accumulate rewards."""
        env = EmailEnv(task="easy")
        env.reset()
        env.step({"is_spam": False})
        assert len(env.episode_rewards) == 1

    def test_step_after_done_raises_error(self):
        """Calling step() after done should raise error."""
        env = EmailEnv(task="easy", max_steps=1)
        env.reset()
        env.step({"is_spam": False})
        with pytest.raises(RuntimeError):
            env.step({"is_spam": False})

    def test_step_returns_done_true_at_max_steps(self):
        """step() should return done=True at max_steps."""
        env = EmailEnv(task="easy", max_steps=1)
        env.reset()
        _, _, done, _ = env.step({"is_spam": False})
        assert done is True

    def test_step_returns_done_true_at_end_of_emails(self):
        """step() should return done=True when out of emails."""
        env = EmailEnv(task="easy", max_steps=100)
        obs = env.reset()
        done = False
        while not done:
            obs, _, done, _ = env.step({"is_spam": False})


class TestStateInterface:
    """Test state() method."""

    def test_state_returns_dict(self):
        """state() should return a dict."""
        env = EmailEnv(task="easy")
        env.reset()
        state = env.state()
        assert isinstance(state, dict)

    def test_state_has_required_keys(self):
        """state() should have required keys."""
        env = EmailEnv(task="easy")
        env.reset()
        state = env.state()

        required_keys = [
            "task",
            "step_count",
            "max_steps",
            "episode_rewards",
            "average_reward",
            "total_reward",
            "is_done",
        ]
        for key in required_keys:
            assert key in state, f"Missing key: {key}"

    def test_average_reward_calculation(self):
        """average_reward should be correctly calculated."""
        env = EmailEnv(task="easy")
        env.reset()
        env.step({"is_spam": False})  # Will get some reward
        env.step({"is_spam": False})  # Will get some reward

        state = env.state()
        expected_avg = sum(state["episode_rewards"]) / len(state["episode_rewards"])
        assert state["average_reward"] == expected_avg

    def test_total_reward_calculation(self):
        """total_reward should be correctly calculated."""
        env = EmailEnv(task="easy")
        env.reset()
        env.step({"is_spam": False})
        env.step({"is_spam": False})

        state = env.state()
        expected_total = sum(state["episode_rewards"])
        assert state["total_reward"] == expected_total


class TestTaskSpecificBehavior:
    """Test task-specific behavior."""

    def test_easy_task_action_type(self):
        """Easy task should handle spam classification."""
        env = EmailEnv(task="easy")
        env.reset()
        _, reward, _, info = env.step({"is_spam": True})
        assert 0 <= reward.value <= 1

    def test_medium_task_action_type(self):
        """Medium task should handle priority."""
        env = EmailEnv(task="medium")
        env.reset()
        _, reward, _, info = env.step({"priority": "high"})
        assert 0 <= reward.value <= 1

    def test_hard_task_action_type(self):
        """Hard task should handle reply generation."""
        env = EmailEnv(task="hard")
        env.reset()
        _, reward, _, info = env.step({
            "reply_text": "Thanks for your email",
            "should_reply": True,
        })
        assert 0 <= reward.value <= 1


class TestEmailData:
    """Test email data loading."""

    def test_emails_loaded(self):
        """Emails should be loaded from JSON."""
        env = EmailEnv(task="easy")
        assert len(env.emails) > 0

    def test_email_structure(self):
        """Loaded emails should have required fields."""
        env = EmailEnv(task="easy")
        email = env.emails[0]
        assert email.id
        assert email.sender
        assert email.subject
        assert email.body
        assert email.timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
