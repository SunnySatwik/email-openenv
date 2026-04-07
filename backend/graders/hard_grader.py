"""
Robust reply generation grader (hard task)

Fixes:
- Spam override (never reply to spam)
- Handles missing/incorrect labels safely
- Prevents always-0 scoring bug
- Works without OpenAI
"""

import os
import json
from openai import OpenAI
from backend.graders.easy_grader import _has_spam_characteristics


MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


# ----------------------------
# LLM scoring (SAFE)
# ----------------------------
def _llm_score(email_text, reply_text):
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("API_BASE_URL")

    if not api_key:
        return 0.3, 0.3  # fallback

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        prompt = f"""
You are a STRICT evaluator.

IMPORTANT:
- If the email is spam or promotional → replying is BAD
- Penalize generic replies
- Reward only relevant, useful replies

Email:
{email_text}

Reply:
{reply_text}

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

        relevance = float(parsed.get("relevance", 0))
        quality = float(parsed.get("quality", 0))

        return min(1.0, relevance), min(1.0, quality)

    except Exception:
        return 0.3, 0.3


# ----------------------------
# MAIN GRADER
# ----------------------------
def grade_hard(action, email):

    if not action or not isinstance(action, dict):
        return 0.0

    # ----------------------------
    # Extract email safely
    # ----------------------------
    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
        true_label = email.get("true_label", None)
    else:
        subject = email.subject
        body = email.body
        true_label = getattr(email, "true_label", None)

    email_text = (subject + " " + body).lower()

    reply_text = action.get("reply_text", "") or ""
    should_reply = bool(action.get("should_reply", False))

    # ----------------------------
    # 🔥 STEP 1: SPAM OVERRIDE
    # ----------------------------
    is_spam = _has_spam_characteristics(email)

    if is_spam:
        if should_reply:
            return 0.0   # replying to spam = wrong
        return 1.0       # ignoring spam = correct

    # ----------------------------
    # 🔥 STEP 2: SAFE LABEL HANDLING
    # ----------------------------
    if isinstance(true_label, dict):
        reply_required = true_label.get("reply_required", None)
    else:
        reply_required = None

    # Only enforce if label exists
    if reply_required is not None:
        if should_reply != reply_required:
            return 0.0

    # ----------------------------
    # 🔥 STEP 3: No reply needed → full score
    # ----------------------------
    if not should_reply:
        return 1.0

    # ----------------------------
    # 🔥 STEP 4: Invalid reply
    # ----------------------------
    if not reply_text.strip():
        return 0.0

    # ----------------------------
    # 🔥 STEP 5: Penalize generic replies
    # ----------------------------
    generic_phrases = [
        "thank you for your email",
        "i will get back to you",
        "best regards",
        "we will respond shortly"
    ]

    generic_penalty = any(p in reply_text.lower() for p in generic_phrases)

    # ----------------------------
    # 🔥 STEP 6: LLM scoring
    # ----------------------------
    relevance_score, quality_score = _llm_score(email_text, reply_text)

    # ----------------------------
    # 🔥 STEP 7: Final score
    # ----------------------------
    score = (
        0.5 +                  # correct decision
        0.3 * relevance_score +
        0.2 * quality_score
    )

    if generic_penalty:
        score -= 0.2

    return max(0.0, min(1.0, score))


# ----------------------------
# Wrapper (compatibility)
# ----------------------------
def grade(reply_text, should_reply, email):
    action = {
        "reply_text": reply_text,
        "should_reply": should_reply
    }
    return grade_hard(action, email)