"""
OpenEnv Email Assistant Environment.
"""

import json
import random
from pathlib import Path
from typing import Literal, Tuple, Optional

from .models import Email, Observation, StepInfo, Reward, Action
from backend.graders.easy_grader import grade_easy
from backend.graders.medium_grader import grade_medium
from backend.graders.hard_grader import grade_hard


class EmailEnv:

    VALID_TASKS = {"easy", "medium", "hard"}
    DATA_PATH = Path(__file__).parent.parent / "data" / "emails.json"

    def __init__(
        self,
        task: Literal["easy", "medium", "hard"] = "easy",
        max_steps: int = 10,
        seed: Optional[int] = None,
    ):
        if task not in self.VALID_TASKS:
            raise ValueError(f"Task must be one of {self.VALID_TASKS}")

        self.task = task
        self.max_steps = max_steps
        self.seed_value = seed

        if seed is not None:
            random.seed(seed)

        self.emails = self._load_emails()

        self.current_email_idx = 0
        self.step_count = 0
        self.episode_rewards = []

    def _load_emails(self) -> list[Email]:
        with open(self.DATA_PATH, "r") as f:
            data = json.load(f)
            return [Email(**email_dict) for email_dict in data]

    def reset(self) -> Observation:
        self.current_email_idx = 0
        self.step_count = 0
        self.episode_rewards = []

        if self.seed_value is None:
            random.shuffle(self.emails)

        return self._get_observation()

    def _get_observation(self) -> Observation:
        email = self.emails[self.current_email_idx]
        return Observation(
            email=email,
            step_count=self.step_count,
            task=self.task,
        )

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, StepInfo]:

        if hasattr(action, "dict"):
            action_dict = action.dict()
        else:
            action_dict = action

        email = self.emails[self.current_email_idx]

        if not email.true_label:
            reward = 0.5
        elif self.task == "easy":
            reward = grade_easy(action_dict, email)
        elif self.task == "medium":
            reward = grade_medium(action_dict, email)
        elif self.task == "hard":
            reward = grade_hard(action_dict, email)
        else:
            raise ValueError(f"Unknown task: {self.task}")

        self.episode_rewards.append(reward)

        self.step_count += 1
        self.current_email_idx += 1

        done = (
            self.current_email_idx >= len(self.emails)
            or self.step_count >= self.max_steps
        )

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

        info = StepInfo(
            task=self.task,
            email_id=email.id,
            ground_truth=email.true_label,
            action_type=self._get_action_type(action_dict),
        )

        reward_obj = Reward(value=reward)

        return next_observation, reward_obj, done, info

    def state(self) -> dict:
        return {
            "task": self.task,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "episode_rewards": self.episode_rewards,
            "average_reward": (
                sum(self.episode_rewards) / len(self.episode_rewards)
                if self.episode_rewards else 0.0
            ),
            "total_reward": sum(self.episode_rewards),
            "current_email_idx": self.current_email_idx,
            "total_emails": len(self.emails),
            "is_done": self.current_email_idx >= len(self.emails)
            or self.step_count >= self.max_steps,
        }

    def _get_action_type(self, action: dict) -> str:
        if "is_spam" in action:
            return "spam_classification"
        elif "priority" in action:
            return "priority_classification"
        elif "reply_text" in action:
            return "reply_generation"
        return "unknown"


__all__ = ["EmailEnv"]