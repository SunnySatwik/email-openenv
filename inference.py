import os
import time
import json
from openai import OpenAI
from dotenv import load_dotenv
from backend.env import EmailEnv

load_dotenv()

# ENV VARIABLES
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("API_BASE_URL")
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


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
    if task == "easy":
        return {"is_spam": "free" in email_text or "offer" in email_text}

    elif task == "medium":
        if "urgent" in email_text:
            return {"priority": "urgent"}
        elif "meeting" in email_text:
            return {"priority": "high"}
        return {"priority": "low"}

    elif task == "hard":
        return {
            "should_reply": "?" in email_text or "please" in email_text,
            "reply_text": "Thank you for your email. I will get back to you shortly."
        }

    return {}


def generate_action(email_text, task):
    prompt = f"""
You are an AI email assistant.

Task: {task}

Email:
{email_text}

Return ONLY JSON:

For easy:
{{"is_spam": true/false}}

For medium:
{{"priority": "low|medium|high|urgent"}}

For hard:
{{"should_reply": true/false, "reply_text": "..." }}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content
        parsed = safe_json_parse(content)

        if parsed:
            return parsed

        return fallback_action(email_text, task)

    except Exception:
        return fallback_action(email_text, task)


def run_task(task):
    env = EmailEnv(task=task, max_steps=5)
    obs = env.reset()

    print(f"[START] task={task}")

    total_reward = 0.0
    step = 0

    while True:
        step += 1

        email = obs.email
        email_text = email.subject + " " + email.body

        start = time.time()
        action = generate_action(email_text, task)
        latency = (time.time() - start) * 1000

        obs, reward, done, _ = env.step(action)

        total_reward += reward.value

        print(
            f"[STEP] step={step} action={action} reward={reward.value:.3f} latency_ms={latency:.2f}"
        )

        if done:
            break

    print(f"[END] total_reward={total_reward:.3f}")


if __name__ == "__main__":
    if not API_KEY:
        raise ValueError("OPENAI_API_KEY not set")

    for task in ["easy", "medium", "hard"]:
        run_task(task)