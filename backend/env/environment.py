"""
OpenEnv Email Assistant Environment.

A Gym-like environment for training agents to assist with email management tasks.
Supports three difficulty levels: spam classification (easy), priority detection (medium),
and reply generation (hard).
"""

import json
import random
from pathlib import Path
from typing import Literal, Tuple, Optional

from .models import Email, Observation, StepInfo
from graders.easy_grader import grade_easy
from graders.medium_grader import grade_medium
from graders.hard_grader import grade_hard


class EmailEnv:
    """
    OpenEnv environment for email assistant tasks.

    Provides a standard RL environment interface with reset(), step(), and state()
    for training agents on email management tasks.
    """

    VALID_TASKS = {"easy", "medium", "hard"}
    DATA_PATH = Path(__file__).parent.parent / "data" / "emails.json"

    def __init__(
        self,
        task: Literal["easy", "medium", "hard"] = "easy",
        max_steps: int = 10,
        seed: Optional[int] = None,
    ):
        """
        Initialize the email environment.

        Args:
            task: Task type - 'easy' (spam), 'medium' (priority), 'hard' (reply)
            max_steps: Maximum steps per episode
            seed: Random seed for reproducibility
        """
        if task not in self.VALID_TASKS:
            raise ValueError(f"Task must be one of {self.VALID_TASKS}")

        self.task = task
        self.max_steps = max_steps
        self.seed_value = seed

        if seed is not None:
            random.seed(seed)

        # Load email data
        self.emails = self._load_emails()
        if not self.emails:
            raise RuntimeError(f"No emails loaded from {self.DATA_PATH}")

        # Episode state
        self.current_email_idx = 0
        self.step_count = 0
        self.episode_rewards = []
        self.current_observation = None

    def _load_emails(self) -> list[Email]:
        """Load emails from data/emails.json."""
        try:
            with open(self.DATA_PATH, "r") as f:
                data = json.load(f)
                return [Email(**email_dict) for email_dict in data]
        except FileNotFoundError:
            raise FileNotFoundError(f"Email data not found at {self.DATA_PATH}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {self.DATA_PATH}")

    def reset(self) -> Observation:
        """
        Reset the environment and start a new episode.

        Returns:
            Initial observation
        """
        self.current_email_idx = 0
        self.step_count = 0
        self.episode_rewards = []

        # Shuffle emails for variety unless deterministic
        if self.seed_value is None:
            random.shuffle(self.emails)

        return self._get_observation()

    def _get_observation(self) -> Observation:
        """Get the current observation."""
        email = self.emails[self.current_email_idx]
        return Observation(
            email=email,
            step_count=self.step_count,
            task=self.task,
        )

    def step(self, action: dict) -> Tuple[Observation, float, bool, StepInfo]:
        """
        Execute one step in the environment.

        Args:
            action: Action taken by agent (dict with task-specific fields)

        Returns:
            Tuple of (observation, reward, done, info)
            - observation: Next observation
            - reward: Reward for this action (meaningful, not just binary)
            - done: Whether episode is finished
            - info: Additional info including ground truth
        """
        if self.step_count >= self.max_steps:
            raise RuntimeError(
                "Episode is done. Call reset() to start a new episode."
            )

        # Get current email and grade the action
        email = self.emails[self.current_email_idx]

        # Calculate reward by calling appropriate external grader
        if not email.true_label:
            reward = 0.5
        elif self.task == "easy":
            reward = grade_easy(
                action,
                email,
            )
        elif self.task == "medium":
            reward = grade_medium(
                action,
                email,
            )
        elif self.task == "hard":
            reward = grade_hard(
                action,
                email,
            )
        else:
            raise ValueError(f"Unknown task: {self.task}")

        self.episode_rewards.append(reward)

        # Move to next email
        self.step_count += 1
        self.current_email_idx += 1

        # Check if episode is done
        done = self.current_email_idx >= len(self.emails) or self.step_count >= self.max_steps

        # Get next observation or dummy if done
        if not done:
            next_observation = self._get_observation()
        else:
            next_observation = Observation(
                email=Email(
                    id="dummy",
                    sender="dummy@dummy.com",
                    subject="",
                    body="",
                    timestamp="",
                    true_label=None,
                ),
                step_count=self.step_count,
                task=self.task,
            )

        # Create info dict
        info = StepInfo(
            task=self.task,
            email_id=email.id,
            ground_truth=email.true_label,
            action_type=self._get_action_type(action),
        )

        return next_observation, reward, done, info

    def state(self) -> dict:
        """
        Get current environment state.

        Returns:
            Dict with episode statistics and current status
        """
        return {
            "task": self.task,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "episode_rewards": self.episode_rewards,
            "average_reward": (
                sum(self.episode_rewards) / len(self.episode_rewards)
                if self.episode_rewards
                else 0.0
            ),
            "total_reward": sum(self.episode_rewards),
            "current_email_idx": self.current_email_idx,
            "total_emails": len(self.emails),
            "is_done": self.current_email_idx >= len(self.emails) or self.step_count >= self.max_steps,
        }

    def _get_action_type(self, action: dict) -> str:
        """Determine the type of action from its structure."""
        if "is_spam" in action:
            return "spam_classification"
        elif "priority" in action:
            return "priority_classification"
        elif "reply_text" in action:
            return "reply_generation"
        return "unknown"


__all__ = ["EmailEnv"]
