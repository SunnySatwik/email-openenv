"""
Mock agent for testing the baseline agent logic without OpenAI API calls.

Useful for debugging and demonstration without API key requirement.
"""

import json
import os
import sys
from typing import Literal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.env import EmailEnv, Observation


def generate_mock_action(observation: Observation, task: str) -> dict:
    email = observation.email
    subject = email.subject.lower()
    body = email.body.lower()
    text = subject + " " + body

    # -----------------------
    # EASY TASK (SPAM)
    # -----------------------
    if task == "easy":

        spam_keywords = {
            "free", "win", "offer", "click", "limited",
            "discount", "buy", "sale", "deal", "promo", "cheap",
            "%", "exclusive"
        }

        work_keywords = {
            "meeting", "project", "server", "report", "deadline",
            "team", "review", "client", "approval"
        }

        spam_score = sum(1 for kw in spam_keywords if kw in text)
        work_score = sum(1 for kw in work_keywords if kw in text)

        # Context-aware decision
        if spam_score >= 2 and spam_score > work_score:
            is_spam = True
        else:
            is_spam = False

        return {"is_spam": is_spam}

    # -----------------------
    # MEDIUM TASK (PRIORITY)
    # -----------------------
    elif task == "medium":

        urgent_keywords = {"urgent", "asap", "emergency", "critical", "immediately"}
        high_keywords = {"meeting", "deadline", "important", "action required", "approval"}
        medium_keywords = {"follow up", "review", "update", "check"}

        if any(kw in text for kw in urgent_keywords):
            priority = "urgent"
        elif any(kw in text for kw in high_keywords):
            priority = "high"
        elif any(kw in text for kw in medium_keywords):
            priority = "medium"
        else:
            priority = "low"

        return {"priority": priority}

    # -----------------------
    # HARD TASK (REPLY)
    # -----------------------
    # -----------------------
# HARD TASK (REPLY) - IMPROVED
# -----------------------
    elif task == "hard":

    # ----------------------------
    # 🔥 STEP 1: SPAM DETECTION
    # ----------------------------
        spam_keywords = {
        "free", "win", "offer", "click", "discount",
        "buy", "sale", "deal", "promo", "cheap"
    }

    if any(kw in text for kw in spam_keywords):
        return {
            "should_reply": False,
            "reply_text": ""
        }

    # ----------------------------
    # 🔥 STEP 2: INTENT DETECTION
    # ----------------------------
    needs_reply = any(kw in text for kw in [
        "?", "please", "can you", "could you", "help",
        "need", "request", "asap"
    ])

    informational = any(kw in text for kw in [
        "fyi", "update", "completed", "done"
    ])

    if informational:
        return {
            "should_reply": False,
            "reply_text": ""
        }

    if not needs_reply:
        return {
            "should_reply": False,
            "reply_text": ""
        }

    # ----------------------------
    # 🔥 STEP 3: CONTEXTUAL REPLIES
    # ----------------------------
    reply_text = ""

    if "meeting" in text:
        reply_text = (
            "Thanks for the meeting update. I have noted the schedule and will attend accordingly. "
            "Please let me know if any preparation is required from my side."
        )

    elif "server" in text or "down" in text or "issue" in text:
        reply_text = (
            "Thanks for flagging the server issue. I understand the urgency and will look into it immediately. "
            "I will share an update as soon as possible."
        )

    elif "help" in text:
        reply_text = (
            "I understand you need help with this. I will review the details and get back to you shortly with a solution."
        )

    elif "review" in text or "document" in text:
        reply_text = (
            "Thank you for sharing the document. I will review it carefully and provide my feedback soon."
        )

    elif "deadline" in text:
        reply_text = (
            "I acknowledge the deadline mentioned. I will prioritize this task and ensure it is completed on time."
        )

    else:
        # 🔥 SMART DEFAULT (context-aware)
        key_terms = " ".join(subject.split()[:3])
        reply_text = (
            f"Thank you for your email regarding {key_terms}. "
            "I have noted your request and will get back to you shortly with the necessary updates."
        )

    return {
        "should_reply": True,
        "reply_text": reply_text
    }

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

            reward_value = reward.value  # Extract value from Reward object
            step_rewards.append(reward_value)
            total_reward += reward_value
            print(f"  Reward: {reward_value:.3f}")
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
