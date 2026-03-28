from graders.easy_grader import grade_easy

email = {
    "subject": "Win a free iPhone",
    "body": "Click now to claim",
    "true_label": {
        "spam": True
    }
}

action = {"is_spam": True}

print("Score:", grade_easy(action, email))