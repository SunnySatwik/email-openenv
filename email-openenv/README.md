# AI Email Assistant OpenEnv Environment

An Gemini-powered reinforcement learning environment for training agents to handle email management tasks. Simulates real-world email triage automation with three difficulty levels.

## Overview

Email management is a universal challenge. This environment automates email triage decisions:

- **Spam Detection**: Filter unwanted messages
- **Priority Classification**: Categorize by urgency
- **Reply Generation**: Decide when and how to respond

Perfect for training agents to handle domain-specific email tasks using reinforcement learning principles.

## Features

### Multi-Task Environment

- **Easy** (Spam Classification): Binary classification with graduated rewards for reasonable mistakes
- **Medium** (Priority Detection): 4-level classification (low/medium/high/urgent) with distance-based scoring
- **Hard** (Reply Generation): Multi-component scoring (decision + content relevance + tone quality)

### Gym-Like Interface

Standard RL environment with `reset()`, `step()`, and `state()` methods for seamless integration with RL frameworks.

### Realistic Simulations

- Real email data with heterogeneous content types
- Multi-step episodes with accumulating rewards
- Ground truth labels for all tasks

## Environment Design

The environment follows the OpenAI Gym pattern:

```python
env = EmailEnv(task="easy", max_steps=10)
observation = env.reset()

while True:
    action = agent.act(observation)
    observation, reward, done, info = env.step(action)
    if done:
        break

print(env.state())  # Episode statistics
```

**Key Concepts:**
- Episodes: Fixed-length sequences of emails (default 10 steps)
- State: Current email, step count, task type
- Reward: Task-specific scoring (0.0 to 1.0)
- Done: When max_steps reached or all emails processed

## Action Space

### Easy Task (Spam Classification)
```json
{
  "is_spam": true
}
```

### Medium Task (Priority Detection)
```json
{
  "priority": "low"
}
```
Valid values: `"low"`, `"medium"`, `"high"`, `"urgent"`

### Hard Task (Reply Generation)
```json
{
  "should_reply": true,
  "reply_text": "Thank you for reaching out. I will respond shortly."
}
```

## Observation Space

Each observation contains:

```python
Observation(
    email=Email(
        id="unique_id",
        sender="sender@example.com",
        subject="Email subject line",
        body="Email message body",
        timestamp="2024-01-15T10:30:00Z",
        true_label={"spam": False, "priority": "high", ...}
    ),
    step_count=1,
    task="easy"
)
```

## Reward System

### Easy Task: Spam Classification
- **Correct prediction** → 1.0
- **Reasonable partial match** (spam indicators present but wasn't spam) → 0.5
- **Wrong prediction** → 0.0

### Medium Task: Priority Classification
- **Exact match** → 1.0
- **1 level off** → 0.6  (e.g., predicted "high" instead of "urgent")
- **2 levels off** → 0.3
- **Very wrong** (3+ levels) → 0.0

Includes keyword-based bonuses for reasonable guesses based on email content.

### Hard Task: Reply Generation
Multi-component weighted scoring:

- **Decision Correctness** (50% weight): Should reply or not?
  - Correct: 1.0 | Incorrect: 0.0

- **Content Relevance** (30% weight): Keyword overlap with email
  - Full match: 1.0 | Partial: 0.5 | None: 0.0

- **Response Quality** (20% weight): Length + polite tone
  - Length > 10 chars: 0.5 base | Polite words: up to +0.5

Final score = (0.5 × decision) + (0.3 × relevance) + (0.2 × quality) - penalties + bonuses

## Baseline Agents

### Gemini-Based Agent

Uses Gemini-2.5-Flash to generate actions. Implements:
- Dynamic prompting based on task
- Robust JSON parsing with fallback defaults
- Real-time API integration

### Mock Agent

Heuristic-based agent for testing without API keys:
- Keyword-matching for spam detection
- Priority heuristics for classification
- Template-based reply generation

## Installation

### Requirements
- Python 3.8+
- Gemini API key (for running the baseline agent)

### Setup

```bash
# Clone or navigate to project
cd email-openenv

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt**
```
google-genai
pydantic>=2.0.0
```

## How to Run

### Mock Agent (No API Key Required)
```bash
python baseline/mock_agent.py --task easy --max-steps 5
python baseline/mock_agent.py --task medium
python baseline/mock_agent.py --task hard --max-steps 10
```

### Gemini Agent

**Option 1: Using .env file (Recommended)**

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Then edit `.env` and add your API key:
```
GEMINI_API_KEY=AI...
```

Run agent:
```bash
python baseline/run_agent.py --task easy
python baseline/run_agent.py --task hard --max-steps 10
python baseline/run_agent.py --task all --max-steps 5
```

**Option 2: Using environment variable**

Set API key directly:
```bash
# macOS/Linux
export GEMINI_API_KEY="AI..."

# Windows
set GEMINI_API_KEY=AI...
```

Then run:
```bash
python baseline/run_agent.py --task easy
```

### Output Example
```
============================================================
OpenEnv Baseline Agent - Task: EASY
============================================================

Step 1: sender@example.com - Check our amazing offer!
  → {'is_spam': True}
  Reward: 1.000

Step 2: boss@company.com - Urgent: Meeting tomorrow
  → {'is_spam': False}
  Reward: 1.000

===== RESULTS =====
Total Reward: 2.000
Steps: 2
Average Reward: 1.000
====================

===== TASK SCORES =====
easy     : 2.000
medium   : 1.800
hard     : 1.200
======================
```

## Project Structure

```
email-openenv/
├── env/
│   ├── environment.py      # Core EmailEnv implementation
│   ├── models.py          # Pydantic data models
│   └── __init__.py
├── graders/
│   ├── easy_grader.py     # Spam classification reward function
│   ├── medium_grader.py   # Priority classification reward function
│   ├── hard_grader.py     # Reply generation reward function
│   └── __init__.py
├── baseline/
│   ├── run_agent.py       # Gemini-based baseline agent
│   ├── mock_agent.py      # Heuristic baseline agent
│   └── README.md
├── data/
│   └── emails.json        # Email dataset with labels
├── tests/
│   ├── test_environment.py
│   └── test_graders.py
└── README.md
```

## Tech Stack

- **Python 3.8+**: Core language
- **Gemini API**: LLM for baseline agent
- **Pydantic**: Data validation and models
- **Gym/RL**: Environment design pattern

## Key Design Principles

1. **Modularity**: Graders are independent, task-agnostic environment
2. **Realism**: Real email patterns and multi-factor scoring
3. **Extensibility**: Easy to add new tasks or graders
4. **Clarity**: Simple code, readable logic, minimal abstractions

## Future Improvements

- **Larger Datasets**: Scale to 10k+ realistic emails
- **Multi-Turn Interactions**: Support conversation threads
- **Better Prompting**: Few-shot examples for baseline agent
- **Custom Graders**: User-defined reward functions
- **Web Interface**: Dashboard for agent monitoring
- **Benchmarking**: Standard suite of evaluation metrics

## License

Open source.
