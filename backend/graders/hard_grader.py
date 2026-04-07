"""
Robust reply generation grader (FINAL VERSION)

Key Features:
- No dependency on broken/missing true_label
- Spam-aware decision logic
- Smooth scoring (not binary)
- Works with or without OpenAI
"""

import os
import json
from openai import OpenAI
from backend.graders.easy_grader import _has_spam_characteristics

MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


# ----------------------------
# LLM scoring (safe fallback)
# ----------------------------
def _llm_score(email_text, reply_text):
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("API_BASE_URL")

    if not api_key:
        return 0.4, 0.4  # neutral fallback

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        prompt = f"""
You are evaluating an email reply.

Email:
{email_text}

Reply:
{reply_text}

Score:
1. relevance (0-1)
2. quality (0-1)

Return ONLY JSON:
{{"relevance": 0-1, "quality": 0-1}}
"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "")

        parsed = json.loads(content)

        return (
            min(1.0, float(parsed.get("relevance", 0))),
            min(1.0, float(parsed.get("quality", 0)))
        )

    except Exception:
        return 0.4, 0.4


# ----------------------------
# MAIN GRADER
# ----------------------------
def grade_hard(action, email):

    if not action or not isinstance(action, dict):
        return 0.0

    # Extract email
    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
    else:
        subject = email.subject
        body = email.body

    email_text = (subject + " " + body).lower()

    reply_text = action.get("reply_text", "") or ""
    should_reply = bool(action.get("should_reply", False))

    # ----------------------------
    # 🔥 STEP 1: SPAM HANDLING
    # ----------------------------
    is_spam = _has_spam_characteristics(email)

    if is_spam:
        if should_reply:
            return 0.0  # replying to spam is bad
        return 1.0      # ignoring spam is perfect

    # ----------------------------
    # 🔥 STEP 2: DECISION QUALITY (NOT STRICT)
    # ----------------------------
    decision_score = 0.0

    # Heuristic: emails with questions or requests → likely need reply
    needs_reply_signal = any(word in email_text for word in [
        "?", "please", "can you", "could you", "help", "request"
    ])

    if needs_reply_signal:
        decision_score = 1.0 if should_reply else 0.0
    else:
        decision_score = 1.0 if not should_reply else 0.5

    # ----------------------------
    # 🔥 STEP 3: NO REPLY CASE
    # ----------------------------
    if not should_reply:
        return decision_score

    # ----------------------------
    # 🔥 STEP 4: INVALID REPLY
    # ----------------------------
    if not reply_text.strip():
        return 0.0

    # ----------------------------
    # 🔥 STEP 5: GENERIC PENALTY
    # ----------------------------
    generic_phrases = [
        "thank you for your email",
        "i will get back to you",
        "best regards",
        "we will respond shortly"
    ]

    generic_penalty = any(p in reply_text.lower() for p in generic_phrases)

    # ----------------------------
    # 🔥 STEP 6: LLM SCORING
    # ----------------------------
    relevance_score, quality_score = _llm_score(email_text, reply_text)

    # ----------------------------
    # 🔥 STEP 7: FINAL SCORE
    # ----------------------------
    score = (
        0.4 * decision_score +
        0.35 * relevance_score +
        0.25 * quality_score
    )

    if generic_penalty:
        score -= 0.2

    return max(0.0, min(1.0, score))


# ----------------------------
# Wrapper
# ----------------------------
def grade(reply_text, should_reply, email):
    return grade_hard({
        "reply_text": reply_text,
        "should_reply": should_reply
    }, email)