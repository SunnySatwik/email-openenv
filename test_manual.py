from graders.medium_grader import grade_medium

email = {
    "subject": "Urgent client issue",
    "body": "Need immediate attention",
    "true_label": {"priority": "urgent"}
}

action = {"priority": "high"}

print("Score:", grade_medium(action, email))