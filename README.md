# Email Assistant OpenEnv

A production-grade OpenEnv (Gym-like) environment for training agents on email management tasks. Built with Pydantic models and meaningful reward functions.

## Features

✅ **Three task levels:**
- **Easy**: Spam classification (binary classification)
- **Medium**: Priority detection (4-level graduated rewards)
- **Hard**: Reply generation (semantic similarity-based rewards)

✅ **Clean interface:**
- `reset()` - Start a new episode
- `step(action)` - Execute an action and get feedback
- `state()` - Get current episode statistics

✅ **Production code quality:**
- Pydantic models for type safety
- Meaningful, graduated reward functions (not just binary)
- Comprehensive tests
- Clear documentation

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from env import EmailEnv

# Create environment
env = EmailEnv(task="easy", max_steps=5)

# Reset and get initial observation
obs = env.reset()

# Take actions and get feedback
action = {"is_spam": False}
next_obs, reward, done, info = env.step(action)

# Check episode statistics
state = env.state()
print(f"Average reward: {state['average_reward']:.2f}")
```

## API Reference

### EmailEnv

Main environment class.

**Constructor:**
```python
EmailEnv(
    task: Literal["easy", "medium", "hard"] = "easy",
    max_steps: int = 10,
    seed: Optional[int] = None,
)
```

**Methods:**

#### `reset() -> Observation`
Start a new episode and return the initial observation.

```python
obs = env.reset()
```

Returns an `Observation` containing:
- `email: Email` - The current email to process
- `step_count: int` - Current step in episode
- `task: str` - Task type

#### `step(action: dict) -> Tuple[Observation, float, bool, StepInfo]`
Execute one action and receive feedback.

```python
next_obs, reward, done, info = env.step(action)
```

**Parameters:**
- `action` - Dict with task-specific fields (see below)

**Returns:**
- `observation: Observation` - Next state
- `reward: float` - Reward in [0, 1] range (meaningful, not binary)
- `done: bool` - Whether episode is finished
- `info: StepInfo` - Metadata including ground truth

#### `state() -> dict`
Get current episode statistics.

```python
state = env.state()
```

Returns dict with:
- `task` - Task type
- `step_count` - Current step
- `max_steps` - Maximum steps
- `episode_rewards` - List of rewards
- `average_reward` - Mean reward
- `total_reward` - Sum of rewards
- `is_done` - Episode finished flag

## Task Specifications

### Easy Task: Spam Classification

**Action format:**
```python
action = {"is_spam": bool}
```

**Reward function:**
- Correct prediction: 1.0
- Incorrect prediction: 0.0

**Example:**
```python
env = EmailEnv(task="easy")
obs = env.reset()
action = {"is_spam": "EXCLUSIVE" in obs.email.subject}
obs, reward, done, info = env.step(action)
```

### Medium Task: Priority Classification

**Action format:**
```python
action = {"priority": "low" | "medium" | "high" | "urgent"}
```

**Reward function (graduated penalties):**
- Perfect match: 1.0
- Off by one level: 0.5
- Off by two levels: 0.25
- Off by three levels: 0.0

**Example:**
```python
env = EmailEnv(task="medium")
obs = env.reset()
if "Action required" in obs.email.subject:
    priority = "urgent"
else:
    priority = "low"
action = {"priority": priority}
obs, reward, done, info = env.step(action)
```

### Hard Task: Reply Generation

**Action format:**
```python
action = {
    "reply_text": str,
    "should_reply": bool,
}
```

**Reward function (multi-aspect):**
1. Decision correctness (0.7 weight): Was reply needed?
2. Content quality (0.3 weight): Similarity to ground truth

- Perfect response: 1.0
- Correct decision, good content: 0.7-1.0
- Wrong decision: 0.0

**Example:**
```python
env = EmailEnv(task="hard")
obs = env.reset()
email = obs.email

# Decide if reply needed
should_reply = not any(
    w in email.sender for w in ["noreply", "newsletter"]
)

# Generate reply
reply_text = "Thanks for your email. I appreciate your message."

action = {
    "reply_text": reply_text,
    "should_reply": should_reply,
}
obs, reward, done, info = env.step(action)
```

## Data Format

Emails are loaded from `data/emails.json`. Each email has:

```json
{
    "id": "string",
    "sender": "string",
    "subject": "string",
    "body": "string",
    "timestamp": "string",
    "true_label": {
        "spam": bool,
        "priority": "string",
        "reply_required": bool,
        "suggested_reply": "string or null"
    }
}
```

## Pydantic Models

All data structures use Pydantic for validation:

```python
from env import (
    Email,                      # Email data
    Observation,                # Environment observation
    SpamClassificationAction,   # Easy task action
    PriorityAction,             # Medium task action
    ReplyAction,                # Hard task action
    StepInfo,                   # Step return info
)
```

## Example: Full Training Loop

```python
from env import EmailEnv

def train_agent(task="easy", episodes=10):
    env = EmailEnv(task=task, max_steps=5)
    episode_returns = []

    for episode in range(episodes):
        obs = env.reset()
        done = False

        while not done:
            # Agent generates action (placeholder)
            if task == "easy":
                action = {"is_spam": False}
            elif task == "medium":
                action = {"priority": "medium"}
            else:
                action = {"reply_text": "Thanks", "should_reply": True}

            obs, reward, done, info = env.step(action)

        state = env.state()
        episode_returns.append(state["total_reward"])
        print(f"Episode {episode}: {state['total_reward']:.2f}")

    print(f"Average return: {sum(episode_returns) / len(episode_returns):.2f}")

train_agent("easy", episodes=5)
```

## Testing

Run tests:
```bash
pytest tests/
pytest tests/test_environment.py -v
pytest tests/test_graders.py -v
```

Run examples:
```bash
python example_usage.py
```

## Architecture

```
env/
├── environment.py   # Main EmailEnv class
├── models.py        # Pydantic data models
├── graders.py       # Reward calculation
└── __init__.py      # Package exports

data/
└── emails.json      # Email dataset

tests/
├── test_environment.py  # Environment tests
└── test_graders.py      # Reward grader tests
```

## Design Principles

This environment follows production-grade design principles:

1. **Type Safety**: Pydantic models enforced throughout
2. **Meaningful Rewards**: Graduated penalties, not binary feedback
3. **Modularity**: Separate concerns (environment, models, grading)
4. **Testability**: Comprehensive unit tests with 100% API coverage
5. **Documentation**: Clear docstrings and examples
6. **Reproducibility**: Seed support for deterministic episodes

## License

MIT
