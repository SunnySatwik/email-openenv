"""
Baseline agent for the OpenEnv email assistant environment.

Uses Groq API (llama-3.3-70b-versatile) to generate task-specific actions for email processing.
Supports three tasks: spam classification (easy), priority detection (medium), and reply generation (hard).
"""

import json
import os
import sys
from typing import Literal

from dotenv import load_dotenv
from groq import Groq
# Load environment variables from .env file
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env import EmailEnv


def get_action_schema(task: Literal["easy", "medium", "hard"]) -> str:
    """Return the JSON schema for the given task."""
    schemas = {
        "easy": """{
    "is_spam": boolean
}""",
        "medium": """{
    "priority": "low" | "medium" | "high" | "urgent"
}""",
        "hard": """{
    "should_reply": boolean,
    "reply_text": "string (empty if should_reply=false)"
}""",
    }
    return schemas[task]


def format_observation_prompt(observation, task: str) -> str:
    """Format an observation as a prompt for the model."""
    email = observation.email

    task_descriptions = {
        "easy": "Classify whether this email is spam or legitimate.",
        "medium": "Classify the priority level of this email: low, medium, high, or urgent.",
        "hard": "Decide whether to reply to this email. If yes, generate a brief professional reply.",
    }

    prompt = f"""You are an email assistant. Your task: {task_descriptions[task]}

Email Details:
From: {email.sender}
Subject: {email.subject}
Body: {email.body}

Return ONLY valid JSON. No explanation. No markdown.
JSON Schema: {get_action_schema(task)}"""

    return prompt


def generate_action(client: Groq, observation, task: str) -> dict:
    """Generate an action using Groq API. Returns action or empty default."""
    prompt = format_observation_prompt(observation, task)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
        response_format={"type": "json_object"}
    )

    response_text = response.choices[0].message.content.strip()

    # Default actions
    defaults = {
        "easy": {"is_spam": False},
        "medium": {"priority": "low"},
        "hard": {"should_reply": False, "reply_text": ""},
    }

    # Try parsing JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return defaults[task]


def run_agent(task: Literal["easy", "medium", "hard"] = "easy", max_steps: int = 5):
    """Run the baseline agent on the specified task."""
    

    # Try to get API key from environment or .env file
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found.\n"
            "Please either:\n"
            "  1. Set environment variable: export GROQ_API_KEY='gsk_...'\n"
            "  2. Create .env file with: GROQ_API_KEY=gsk_...\n"
            "  3. See .env.example for template"
        )

    client = Groq(api_key=api_key)
    print("API KEY LOADED:", api_key[:8] if api_key else "None")
    print(f"\n{'='*60}")
    print(f"OpenEnv Baseline Agent - Task: {task.upper()} (Groq llama-3.3-70b)")
    print(f"{'='*60}\n")

    env = EmailEnv(task=task, max_steps=max_steps)
    observation = env.reset()

    total_reward = 0.0
    step_rewards = []

    step = 0
    while True:
        step += 1
        print(f"Step {step}: {observation.email.sender} - {observation.email.subject[:40]}")

        action = generate_action(client, observation, task)
        print(f"  → {action}")

        try:
            observation, reward, done, info = env.step(action)
            step_rewards.append(reward)
            total_reward += reward
            print(f"  Reward: {reward:.3f}\n")

            if done:
                break
        except Exception as e:
            print(f"  Error: {e}\n")
            break

    # Print results
    avg_reward = total_reward / len(step_rewards) if step_rewards else 0.0

    print("===== RESULTS =====")
    print(f"Total Reward: {total_reward:.3f}")
    print(f"Steps: {len(step_rewards)}")
    print(f"Average Reward: {avg_reward:.3f}")
    print("=" * 20 + "\n")

    return total_reward


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the baseline agent on an email task."
    )
    parser.add_argument(
        "--task",
        choices=["easy", "medium", "hard", "all"],
        default="easy",
        help="Task to run: easy, medium, hard, or all (default: easy)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=5,
        help="Maximum steps per episode (default: 5)",
    )

    args = parser.parse_args()

    try:
        if args.task == "all":
            task_scores = {}
            for t in ["easy", "medium", "hard"]:
                score = run_agent(task=t, max_steps=args.max_steps)
                task_scores[t] = score

            print("\n===== TASK SCORES =====")
            for t in ["easy", "medium", "hard"]:
                print(f"{t:8} : {task_scores[t]:.3f}")
            print("=" * 22)
        else:
            run_agent(task=args.task, max_steps=args.max_steps)
    except KeyboardInterrupt:
        print("\n\nAgent interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
