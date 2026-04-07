"""
Robust reply generation grader (hard task)

Fixes:
- Spam override (never reply to spam)
- Ignores bad ground truth for spam
- Safe fallback without OpenAI
- Deterministic scoring
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

    # 🔥 No API → fallback
    if not api_key:
        return 0.3, 0.3

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        prompt = f"""
You are a STRICT evaluator.

IMPORTANT:
- If the email is promotional or spam → replying is BAD
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

    # Extract email
    if isinstance(email, dict):
        subject = email.get("subject", "")
        body = email.get("body", "")
        reply_required = email.get("true_label", {}).get("reply_required", False)
    else:
        subject = email.subject
        body = email.body
        reply_required = email.true_label.get("reply_required", False)

    email_text = (subject + " " + body).lower()

    reply_text = action.get("reply_text", "") or ""
    should_reply = bool(action.get("should_reply", False))

    # =========================================================
    # 🔥 STEP 1: HARD SPAM OVERRIDE (THIS FIXES YOUR BUG)
    # =========================================================
    is_spam = _has_spam_characteristics(email)

    if is_spam:
        # ❌ replying to spam = ALWAYS WRONG
        if should_reply:
            return 0.0
        # ✅ ignoring spam = ALWAYS CORRECT
        return 1.0

    # =========================================================
    # 🔥 STEP 2: Decision correctness
    # =========================================================
    if should_reply != reply_required:
        return 0.0

    # =========================================================
    # 🔥 STEP 3: If no reply needed → full score
    # =========================================================
    if not should_reply:
        return 1.0

    # =========================================================
    # 🔥 STEP 4: Basic sanity checks
    # =========================================================
    if not reply_text.strip():
        return 0.0

    # Penalize useless generic replies
    generic_phrases = [
        "thank you for your email",
        "i will get back to you",
        "best regards"
    ]

    generic_penalty = any(p in reply_text.lower() for p in generic_phrases)

    # =========================================================
    # 🔥 STEP 5: LLM scoring (optional)
    # =========================================================
    relevance_score, quality_score = _llm_score(email_text, reply_text)

    # =========================================================
    # 🔥 STEP 6: Final scoring
    # =========================================================
    score = (
        0.5 +                 # correct decision
        0.3 * relevance_score +
        0.2 * quality_score
    )

    # Penalize generic replies
    if generic_penalty:
        score -= 0.2

    return max(0.0, min(1.0, score))


# ----------------------------
# Wrapper (for compatibility)
# ----------------------------
def grade(reply_text, should_reply, email):
    action = {
        "reply_text": reply_text,
        "should_reply": should_reply
    }
    return grade_hard(action, email)