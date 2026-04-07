"""
Final Hard Grader (Smart + Test-Compatible)

- Uses true_label for correctness (required by tests)
- Keeps soft scoring for relevance + quality
- Stable fallback if no API
"""

import os
import json
from openai import OpenAI

MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


# ----------------------------
# Optional LLM scoring
# ----------------------------
def _llm_score(email_text, reply_text):
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("API_BASE_URL")

    if not api_key:
        return 0.4, 0.4

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        prompt = f"""
Evaluate this email reply.

Email:
{email_text}

Reply:
{reply_text}

Return JSON:
{{"relevance": 0-1, "quality": 0-1}}
"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "")

        parsed = json.loads(content)

        return (
            min(1.0, float(parsed.get("relevance", 0))),
            min(1.0, float(parsed.get("quality", 0))),
        )

    except Exception:
        return 0.4, 0.4


# ----------------------------
# MAIN GRADER
# ----------------------------
def grade_hard(action, email):

    if not action or not isinstance(action, dict):
        return 0.0

    # ----------------------------
    # Extract email + label
    # ----------------------------
    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
        true_label = email.get("true_label", {})
    else:
        subject = email.subject
        body = email.body
        true_label = email.true_label

    reply_required = true_label.get("reply_required", False)

    reply_text = action.get("reply_text", "") or ""
    should_reply = bool(action.get("should_reply", False))

    # ----------------------------
    # ❌ WRONG DECISION
    # ----------------------------
    if should_reply != reply_required:
        return 0.0

    # ----------------------------
    # ✅ BASE DECISION SCORE
    # ----------------------------
    decision_score = 0.5

    # ----------------------------
    # NO REPLY CASE
    # ----------------------------
    if not should_reply:
        return decision_score

    # ----------------------------
    # EMPTY REPLY
    # ----------------------------
    if not reply_text.strip():
        return decision_score

    text = (subject + " " + body).lower()
    reply = reply_text.lower()

    # ----------------------------
    # RELEVANCE (0–0.3)
    # ----------------------------
    overlap = sum(1 for word in text.split() if word in reply)
    relevance_score = min(overlap / 8, 1.0) * 0.3

    # ----------------------------
    # QUALITY (0–0.2)
    # ----------------------------
    length = len(reply_text.split())

    if length < 3:
        quality_score = 0.05
    elif length < 10:
        quality_score = 0.15    
    else:
        quality_score = 0.2

    return decision_score + relevance_score + quality_score


# ----------------------------
# Wrapper
# ----------------------------
def grade(reply_text, should_reply, email):
    return grade_hard(
        {
            "reply_text": reply_text,
            "should_reply": should_reply,
        },
        email,
    )