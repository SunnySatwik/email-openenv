"""
Mock agent for testing the baseline agent logic without Gemini API calls.

Useful for debugging and demonstration without API key requirement.
"""

import json
import os
import sys
from typing import Literal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env import EmailEnv, Observation


def generate_mock_action(observation: Observation, task: str) -> dict:
    """
    Generate a mock action based on simple heuristics.

    Useful for testing without Gemini API key.
    """
    email = observation.email
    text = (email.subject + " " + email.body).lower()

    if task == "easy":
        # Simple spam heuristic
        spam_keywords = {"free", "win", "offer", "click", "limited", "urgent"}
        is_spam = any(keyword in text for keyword in spam_keywords)
        return {"is_spam": is_spam}

    elif task == "medium":
        # Simple priority heuristic
        urgent_keywords = {"urgent", "asap", "emergency", "critical", "immediately"}
        high_keywords = {"meeting", "deadline", "important", "action required"}
        medium_keywords = {"follow up", "review", "approval"}

        if any(kw in text for kw in urgent_keywords):
            priority = "urgent"
        elif any(kw in text for kw in high_keywords):
            priority = "high"
        elif any(kw in text for kw in medium_keywords):
            priority = "medium"
        else:
            priority = "low"

        return {"priority": priority}

    elif task == "hard":
        # Simple reply heuristic
        needs_reply_keywords = {"question", "need", "please", "help", "can you"}
        should_reply = any(keyword in text for keyword in needs_reply_keywords)

        reply_text = ""
        if should_reply:
            reply_text = "Thank you for your email. I will get back to you shortly. Best regards."

        return {"should_reply": should_reply, "reply_text": reply_text}

    return {}


def run_mock_agent(task: Literal["easy", "medium", "hard"] = "easy", max_steps: int = 5):
    """Run the mock agent on the specified task."""
    print(f"\n{'='*60}")
    print(f"Mock Baseline Agent - Task: {task.upper()}")
    print(f"(No API calls - heuristic-based actions)")
    print(f"{'='*60}\n")

    env = EmailEnv(task=task, max_steps=max_steps)
    observation = env.reset()

    total_reward = 0.0
    step_rewards = []

    step = 0
    while True:
        step += 1
        print(f"Step {step}:")
        print(f"  Email: {observation.email.sender} - {observation.email.subject[:50]}")

        try:
            # Generate action using heuristics
            action = generate_mock_action(observation, task)

            # Format action display
            action_display = {
                k: v if not isinstance(v, str) or len(v) < 50 else v[:47] + "..."
                for k, v in action.items()
            }
            print(f"  Action: {action_display}")

            # Execute action
            observation, reward, done, info = env.step(action)

            step_rewards.append(reward)
            total_reward += reward
            print(f"  Reward: {reward:.3f}")
            print()

            if done:
                break

        except Exception as e:
            print(f"  Error: {e}")
            break

    # Print statistics
    print(f"{'='*60}")
    print(f"Episode Complete - Task: {task.upper()}")
    print(f"{'='*60}")
    print(f"Total Steps: {len(step_rewards)}")
    print(f"Step Rewards: {[f'{r:.3f}' for r in step_rewards]}")
    print(f"Total Reward: {total_reward:.3f}")
    if step_rewards:
        print(f"Average Reward: {total_reward / len(step_rewards):.3f}")
    print(f"{'='*60}\n")

    return total_reward


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the mock baseline agent (no API calls)."
    )
    parser.add_argument(
        "--task",
        choices=["easy", "medium", "hard"],
        default="easy",
        help="Task to run (default: easy)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=5,
        help="Maximum steps per episode (default: 5)",
    )

    args = parser.parse_args()

    try:
        run_mock_agent(task=args.task, max_steps=args.max_steps)
    except KeyboardInterrupt:
        print("\n\nAgent interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
