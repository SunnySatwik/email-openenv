import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.env import EmailEnv
from backend.env.models import Observation

from backend.graders.easy_grader import grade_easy
from backend.graders.medium_grader import grade_medium
from backend.graders.hard_grader import grade_hard

from backend.baseline.mock_agent import generate_mock_action

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# CORE EXECUTION
# ----------------------------

def compute_reward(task, action, email):
    if task == "easy":
        return grade_easy(action, email)
    elif task == "medium":
        return grade_medium(action, email)
    else:
        return grade_hard(action, email)


# ----------------------------
# RUN ENDPOINT
# ----------------------------

@app.post("/run")
def run(task: str = "hard", max_steps: int = 5):

    env = EmailEnv(task=task, max_steps=max_steps)
    observation = env.reset()

    steps = []
    total_reward = 0.0

    for i in range(max_steps):

        start = time.time()

        action = generate_mock_action(observation, task)

        latency = (time.time() - start) * 1000

        # 🔥 CRITICAL: USE CURRENT EMAIL ONLY
        reward = compute_reward(task, action, observation.email)

        steps.append({
            "step": i + 1,
            "email_id": getattr(observation.email, "id", str(i)),
            "action": action,
            "reward": reward,
            "latency_ms": latency
        })

        total_reward += reward

        # Step env AFTER grading
        observation, _, done, _ = env.step(action)

        if done:
            break

    return {
        "task": task,
        "steps": steps,
        "total_reward": total_reward,
        "average_reward": total_reward / len(steps)
    }


# ----------------------------
# COMPARE
# ----------------------------

@app.post("/compare")
def compare(data: dict):

    email = data["email"]
    task = data["task"]

    obs = Observation(email=email, task=task, step_count=1)

    start = time.time()
    action = generate_mock_action(obs, task)
    latency = (time.time() - start) * 1000

    reward = compute_reward(task, action, email)

    return {
        "action": action,
        "reward": reward,
        "latency_ms": latency
    }


# ----------------------------
# ROOT
# ----------------------------

@app.get("/")
def root():
    return {"status": "ok"}