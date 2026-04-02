"""Email assistant environment package."""

from .environment import EmailEnv
from .models import (
    Email,
    Observation,
    SpamClassificationAction,
    PriorityAction,
    ReplyAction,
    StepInfo,
)

__all__ = [
    "EmailEnv",
    "Email",
    "Observation",
    "SpamClassificationAction",
    "PriorityAction",
    "ReplyAction",
    "StepInfo",
]
