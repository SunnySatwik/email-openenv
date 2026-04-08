import os
import time
import json
from openai import OpenAI
from backend.env import EmailEnv

# 🔥 REQUIRED ENV VARIABLES (from validator)
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
BASE_URL = os.getenv("API_BASE_URL")
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ✅ ALWAYS initialize client (no guards)
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


def safe_json_parse(content):
    try:
        return json.loads(content)
    except:
        content = content.strip().replace("```json", "").replace("```", "")
        try:
            return json.loads(content)
        except:
            return None


def fallback_action(email_text, task):
    text = email_text.lower()

    if task == "easy":
        return {"is_spam": any(k in text for k in ["free", "offer", "buy", "discount"])}

    elif task == "medium":
        if "urgent" in text or "asap" in text:
            return {"priority": "urgent"}
        elif "meeting" in text or "deadline" in text:
            return {"priority": "high"}
        return {"priority": "low"}

    elif task == "hard":
        needs_reply = any(k in text for k in ["?", "please", "help", "confirm"])
        return {
            "should_reply": needs_reply,
            "reply_text": (
                "Thank you for your email. I will review and get back to you shortly."
                if needs_reply else ""
            ),
        }

    return {}


def generate_action(email_text, task):
    prompt = f"""
You are an AI email assistant.

Task: {task}

Email:
{email_text}

Return ONLY JSON.
"""

    try:
        # 🔥 MUST HIT PROXY
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        content = response.choices[0].message.content
        parsed = safe_json_parse(content)

        if parsed:
            return parsed

    except Exception:
        pass  # fallback below

    return fallback_action(email_text, task)


def run_task(task):
    env = EmailEnv(task=task, max_steps=5)
    obs = env.reset()

    print(f"[START] task={task} env=email_openenv model={MODEL}", flush=True)

    rewards = []
    step = 0

    try:
        while True:
            step += 1

            email = obs.email
            email_text = email.subject + " " + email.body

            action = generate_action(email_text, task)

            try:
                obs, reward, done, _ = env.step(action)
                reward_val = reward.value
                error = None
            except Exception as e:
                reward_val = 0.0
                done = True
                error = str(e)

            rewards.append(reward_val)

            print(
                f"[STEP] step={step} action={action} reward={reward_val:.2f} done={str(done).lower()} error={error or 'null'}",
                flush=True
            )

            if done:
                break

        score = sum(rewards) / len(rewards) if rewards else 0.0

        print(
            f"[END] success={str(score > 0.1).lower()} steps={len(rewards)} score={score:.2f} rewards={','.join(f'{r:.2f}' for r in rewards)}",
            flush=True
        )

    except Exception as e:
        # 🔥 NEVER crash
        print(
            f"[END] success=false steps=0 score=0.00 rewards= error={str(e)}",
            flush=True
        )


if __name__ == "__main__":
    for task in ["easy", "medium", "hard"]:
        run_task(task)