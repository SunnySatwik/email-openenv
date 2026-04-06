import os
import json
from openai import OpenAI


MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


def _llm_score(email_text, reply_text):
    import os
    import json
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("API_BASE_URL")
    model = os.getenv("MODEL_NAME", "gpt-4o-mini")

    # 🔥 If no API key → fallback immediately
    if not api_key:
        return 0.3, 0.3

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        prompt = f"""
You are a strict evaluator.

Evaluate the quality of an email reply.

Email:
{email_text}

Reply:
{reply_text}

Return ONLY JSON:
{{"relevance": 0-1, "quality": 0-1}}
"""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Clean markdown
        content = content.replace("```json", "").replace("```", "")

        parsed = json.loads(content)

        relevance = float(parsed.get("relevance", 0))
        quality = float(parsed.get("quality", 0))

        return min(1.0, relevance), min(1.0, quality)

    except Exception:
        return 0.3, 0.3


def grade_hard(action, email):

    if not action or not isinstance(action, dict):
        return 0.0

    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
        reply_required = email.get("true_label", {}).get("reply_required", False)
    else:
        subject = email.subject
        body = email.body
        reply_required = email.true_label.get("reply_required", False)

    email_text = subject + " " + body

    reply_text = action.get("reply_text", "")
    should_reply = bool(action.get("should_reply", False))

    # 🚨 HARD RULE
    if should_reply != reply_required:
        return 0.0

    # Decision score
    decision_score = 1.0

    # LLM scoring
    relevance_score, quality_score = (0.0, 0.0)

    if should_reply and reply_text.strip():
        relevance_score, quality_score = _llm_score(email_text, reply_text)

    # Final weighted score
    total_score = (
        decision_score * 0.5 +
        relevance_score * 0.3 +
        quality_score * 0.2
    )

    return max(0.0, min(1.0, total_score))


def grade(reply_text, should_reply, email):
    action = {
        "reply_text": reply_text,
        "should_reply": should_reply
    }
    return grade_hard(action, email)