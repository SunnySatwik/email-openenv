from graders.hard_grader import grade_hard

email = {
    "subject": "Client issue",
    "body": "We need urgent help",
    "true_label": {"reply_required": True}
}

action = {
    "should_reply": True,
    "reply_text": "Thank you for reaching out. We will resolve this immediately. Regards."
}

print("Score:", grade_hard(action, email))