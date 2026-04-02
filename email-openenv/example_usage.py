"""
Example usage and tests for the Email Assistant environment.

Demonstrates how to use the EmailEnv for training agents on different tasks.
"""

from env import EmailEnv


def example_easy_task():
    """Example: Spam classification (easy task)."""
    print("=" * 60)
    print("EASY TASK: Spam Classification")
    print("=" * 60)

    env = EmailEnv(task="easy", max_steps=5, seed=42)
    obs = env.reset()

    print(f"\nStarted episode with {len(env.emails)} emails")
    print(f"Task: {obs.task}\n")

    for step in range(3):
        email = obs.email
        print(f"Step {step + 1}")
        print(f"  From: {email.sender}")
        print(f"  Subject: {email.subject}")
        print(f"  Body: {email.body[:60]}...")

        # Simulate agent prediction
        action = {"is_spam": "promotions" in email.sender or "EXCLUSIVE" in email.subject}

        obs, reward, done, info = env.step(action)
        print(f"  Action: is_spam={action['is_spam']}")
        print(f"  Reward: {reward:.2f}")
        print(f"  Ground Truth: {info.ground_truth}\n")

        if done:
            break

    state = env.state()
    print(f"Episode Stats:")
    print(f"  Average Reward: {state['average_reward']:.2f}")
    print(f"  Total Reward: {state['total_reward']:.2f}")


def example_medium_task():
    """Example: Priority classification (medium task)."""
    print("\n" + "=" * 60)
    print("MEDIUM TASK: Priority Classification")
    print("=" * 60)

    env = EmailEnv(task="medium", max_steps=5, seed=42)
    obs = env.reset()

    print(f"\nStarted episode with {len(env.emails)} emails")
    print(f"Task: {obs.task}\n")

    for step in range(3):
        email = obs.email
        print(f"Step {step + 1}")
        print(f"  From: {email.sender}")
        print(f"  Subject: {email.subject}")

        # Simple heuristic for priority
        if "Action required" in email.subject or "manager" in email.sender:
            priority = "urgent"
        elif any(w in email.subject for w in ["Meeting", "Report", "feedback"]):
            priority = "high"
        else:
            priority = "low"

        action = {"priority": priority}

        obs, reward, done, info = env.step(action)
        print(f"  Action: priority={action['priority']}")
        print(f"  Reward: {reward:.2f}")
        print(f"  Ground Truth: {info.ground_truth}\n")

        if done:
            break

    state = env.state()
    print(f"Episode Stats:")
    print(f"  Average Reward: {state['average_reward']:.2f}")
    print(f"  Total Reward: {state['total_reward']:.2f}")


def example_hard_task():
    """Example: Reply generation (hard task)."""
    print("\n" + "=" * 60)
    print("HARD TASK: Reply Generation")
    print("=" * 60)

    env = EmailEnv(task="hard", max_steps=5, seed=42)
    obs = env.reset()

    print(f"\nStarted episode with {len(env.emails)} emails")
    print(f"Task: {obs.task}\n")

    for step in range(3):
        email = obs.email
        print(f"Step {step + 1}")
        print(f"  From: {email.sender}")
        print(f"  Subject: {email.subject}")
        print(f"  Body: {email.body[:60]}...")

        # Simulate reply generation
        should_reply = not any(
            w in email.sender for w in ["noreply", "newsletter", "no-reply"]
        )
        reply_text = (
            "Thanks for your email. I'll get back to you shortly."
            if should_reply
            else ""
        )

        action = {"reply_text": reply_text, "should_reply": should_reply}

        obs, reward, done, info = env.step(action)
        print(f"  Should Reply: {action['should_reply']}")
        print(f"  Reply: {action['reply_text'][:50]}...")
        print(f"  Reward: {reward:.2f}")
        print(f"  Ground Truth: {info.ground_truth}\n")

        if done:
            break

    state = env.state()
    print(f"Episode Stats:")
    print(f"  Average Reward: {state['average_reward']:.2f}")
    print(f"  Total Reward: {state['total_reward']:.2f}")


def test_environment_interface():
    """Test that the environment implements the required interface."""
    print("\n" + "=" * 60)
    print("INTERFACE TEST")
    print("=" * 60)

    env = EmailEnv(task="easy")

    # Check required methods
    assert hasattr(env, "reset"), "Missing reset()"
    assert hasattr(env, "step"), "Missing step()"
    assert hasattr(env, "state"), "Missing state()"

    # Test reset returns Observation
    obs = env.reset()
    assert hasattr(obs, "email"), "Observation missing email"
    assert hasattr(obs, "task"), "Observation missing task"
    print("✓ reset() returns correct Observation")

    # Test step returns (obs, reward, done, info)
    action = {"is_spam": False}
    result = env.step(action)
    assert len(result) == 4, "step() should return 4 values"
    obs, reward, done, info = result
    assert isinstance(reward, (int, float)), "Reward should be numeric"
    assert isinstance(done, bool), "done should be bool"
    assert hasattr(info, "task"), "Info missing task"
    print("✓ step() returns correct tuple (observation, reward, done, info)")

    # Test state returns dict with expected keys
    state = env.state()
    assert isinstance(state, dict), "state() should return dict"
    assert "step_count" in state, "state missing step_count"
    assert "episode_rewards" in state, "state missing episode_rewards"
    print("✓ state() returns correct state dict")

    print("\nAll interface tests passed!")


if __name__ == "__main__":
    test_environment_interface()
    example_easy_task()
    example_medium_task()
    example_hard_task()
