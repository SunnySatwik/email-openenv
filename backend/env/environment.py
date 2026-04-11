import random

from backend.env.models import Email, Observation, StepInfo, Reward
from backend.graders.easy_grader import grade_easy
from backend.graders.medium_grader import grade_medium
from backend.graders.hard_grader import grade_hard


class EmailEnv:
    def __init__(self, task="easy", max_steps=10, seed=None):
        if task not in ["easy", "medium", "hard"]:
            raise ValueError("Invalid task")

        self.task = task
        self.max_steps = max_steps
        self.seed = seed

        if seed is not None:
            random.seed(seed)

        # Dummy emails (you may already load from JSON)
        self.emails = self._load_emails()

        self.step_count = 0
        self.current_email_idx = 0
        self.episode_rewards = []

    def _load_emails(self):
        return [
            Email(
                id="1",
                sender="boss@company.com",
                subject="URGENT: Server down",
                body="We need your help ASAP.",
                timestamp="2024-01-01",
                true_label={"spam": False, "priority": "urgent", "reply_required": True},
            ),
            Email(
                id="2",
                sender="newsletter@shop.com",
                subject="50% discount offer",
                body="Buy now!",
                timestamp="2024-01-01",
                true_label={"spam": True, "priority": "low", "reply_required": False},
            ),
            Email(
                id="3",
                sender="colleague@company.com",
                subject="Meeting tomorrow",
                body="Please confirm availability.",
                timestamp="2024-01-01",
                true_label={"spam": False, "priority": "high", "reply_required": True},
            ),
            Email(
                id="4",
                sender="system@alerts.com",
                subject="Update completed",
                body="FYI task done.",
                timestamp="2024-01-01",
                true_label={"spam": False, "priority": "low", "reply_required": False},
            ),
        ]

    def reset(self):
        self.step_count = 0
        self.current_email_idx = 0
        self.episode_rewards = []

        if self.seed is not None:
            random.seed(self.seed)

        observation = Observation(
            email=self.emails[self.current_email_idx],
            task=self.task,
            step_count=self.step_count,
        )

        return observation

    def step(self, action):
        # 🔥 FIX 1: prevent stepping after episode ends
        if self.step_count >= self.max_steps:
            raise RuntimeError("Episode already finished")

        # 🔥 FIX 2: prevent stepping beyond email list
        if self.current_email_idx >= len(self.emails):
            raise RuntimeError("No more emails available")

        email = self.emails[self.current_email_idx]
        
        # ----------------------------
        # Compute reward
        # ----------------------------
        if self.task == "easy":
            reward_value = grade_easy(action, email)
        elif self.task == "medium":
            reward_value = grade_medium(action, email)
        else:
            reward_value = grade_hard(action, email)

        # Clamp reward into (0,1) exclusive
        EPS = 1e-6
        reward_value = max(EPS, min(1.0 - EPS, reward_value))

        reward = Reward(value=reward_value)

        # ----------------------------
        # Update state
        # ----------------------------
        self.episode_rewards.append(reward_value)
        self.step_count += 1
        self.current_email_idx += 1

        # ----------------------------
        # Done condition
        # ----------------------------
        done = (
            self.step_count >= self.max_steps
            or self.current_email_idx >= len(self.emails)
        )

        # ----------------------------
        # Next observation
        # ----------------------------
        if not done:
            next_email = self.emails[self.current_email_idx]
        else:
            next_email = email  # safe fallback

        observation = Observation(
            email=next_email,
            task=self.task,
            step_count=self.step_count,
        )

        info = StepInfo(
    task=self.task,
    email_id=email.id,
    ground_truth=email.true_label,
    action_type=str(type(action).__name__)
)

        return observation, reward, done, info

    def state(self):
        total_reward = sum(self.episode_rewards)
        avg_reward = (
            total_reward / len(self.episode_rewards)
            if self.episode_rewards
            else 0.0
        )

        return {
            "task": self.task,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "episode_rewards": self.episode_rewards,
            "average_reward": avg_reward,
            "total_reward": total_reward,
            "is_done": self.step_count >= self.max_steps,
        }