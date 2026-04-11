"""
Pydantic models for the email environment.

Defines data contracts for observations, actions, and email data.
"""

from typing import Optional, Union
from pydantic import BaseModel, Field


class Email(BaseModel):
    """Email data structure."""
    id: str = Field(..., description="Unique email identifier")
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    true_label: Optional[dict] = Field(default=None, description="Ground truth labels for training/evaluation")


class Observation(BaseModel):
    """Observation returned by the environment."""
    email: Email = Field(..., description="Current email to process")
    step_count: int = Field(default=0, description="Current step in the episode")
    task: str = Field(..., description="Task type: 'easy', 'medium', or 'hard'")

    class Config:
        arbitrary_types_allowed = True


class SpamClassificationAction(BaseModel):
    """Action for the easy task: spam classification."""
    is_spam: bool = Field(..., description="Whether the email is spam")


class PriorityAction(BaseModel):
    """Action for the medium task: priority classification."""
    priority: str = Field(
        ...,
        description="Priority level",
        pattern="^(low|medium|high|urgent)$"
    )


class ReplyAction(BaseModel):
    """Action for the hard task: reply generation."""
    reply_text: str = Field(..., description="Generated reply to the email")
    should_reply: bool = Field(
        default=True,
        description="Whether a reply is needed"
    )


class Reward(BaseModel):
    """Reward returned by the environment."""
    value: float = Field(..., gt=0.0, lt=1.0, description="Reward score strictly between 0 and 1 (0.05-0.95)")
    explanation: Optional[str] = Field(default=None, description="Optional explanation of reward")


class StepInfo(BaseModel):
    """Additional information returned with each step."""
    task: str = Field(..., description="Task type")
    email_id: str = Field(..., description="Email ID that was processed")
    ground_truth: Optional[dict] = Field(default=None, description="Ground truth for learning")
    action_type: str = Field(..., description="Type of action taken")


# Union Action type for OpenEnv compliance
Action = Union[
    SpamClassificationAction,
    PriorityAction,
    ReplyAction
]


__all__ = [
    "Email",
    "Observation",
    "SpamClassificationAction",
    "PriorityAction",
    "ReplyAction",
    "Reward",
    "StepInfo",
    "Action",
]
