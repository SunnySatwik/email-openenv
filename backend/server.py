import os
import time
from typing import List, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from backend.env import EmailEnv
from backend.env.models import Email, Observation

from backend.graders.easy_grader import grade_easy
from backend.graders.medium_grader import grade_medium
from backend.graders.hard_grader import grade_hard

from backend.baseline.run_agent import generate_action

# ────────────────────────────────────────────────────────────────────────────
# Safety wrapper for scores
# ────────────────────────────────────────────────────────────────────────────

EPS = 1e-6

def safe_score(x):
    """Ensure reward is strictly in (0, 1)."""
    return max(EPS, min(1.0 - EPS, float(x)))

# ----------------------------
# OpenAI client (lazy)
# ----------------------------
def get_client():
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("API_BASE_URL")

    if not api_key:
        return None

    return OpenAI(api_key=api_key, base_url=base_url)


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env_instance = None


# ----------------------------
# Models
# ----------------------------

class CompareRequest(BaseModel):
    task: Literal["easy", "medium", "hard"]
    email: Email


class CompareResult(BaseModel):
    action: dict
    reward: float
    latency_ms: float


class RunRequest(BaseModel):
    task: Literal["easy", "medium", "hard"]
    max_steps: int = 5


class StepRequest(BaseModel):
    action: dict


class StepResult(BaseModel):
    step: int
    email_id: str
    action: dict
    reward: float
    latency_ms: float


class RunResponse(BaseModel):
    task: str
    steps: List[StepResult]
    total_reward: float
    average_reward: float


# ----------------------------
# Agent execution
# ----------------------------

async def run_agent_once(observation: Observation, task: str):
    start = time.perf_counter()

    client = get_client()

    try:
        if client:
            action = generate_action(client, observation, task)
        else:
            raise Exception("No OpenAI client")

    except Exception as e:
        print(f"[WARNING] OpenAI failed: {e}")
        from backend.baseline.mock_agent import generate_mock_action
        action = generate_mock_action(observation, task)

    latency = (time.perf_counter() - start) * 1000

    # ✅ ALWAYS use YOUR graders
    if task == "easy":
        reward = grade_easy(action, observation.email)
    elif task == "medium":
        reward = grade_medium(action, observation.email)
    else:
        reward = grade_hard(action, observation.email)

    # 🔥 HARD GUARANTEE
    reward = float(reward) if reward is not None else EPS

    if not (0.0 < reward < 1.0):
        reward = safe_score(reward)

    return action, reward, latency


# ----------------------------
# RESET
# ----------------------------

@app.post("/reset")
def reset(task: str = "easy"):
    global env_instance
    env_instance = EmailEnv(task=task, max_steps=5)
    return env_instance.reset()


# ----------------------------
# STEP (FIXED)
# ----------------------------

@app.post("/step")
def step(req: StepRequest):
    global env_instance

    if env_instance is None:
        return {"error": "Call /reset first"}

    obs, _, done, info = env_instance.step(req.action)

    # 🔥 USE YOUR GRADERS (NOT env_reward)
    if env_instance.task == "easy":
        reward_value = grade_easy(req.action, obs.email)
    elif env_instance.task == "medium":
        reward_value = grade_medium(req.action, obs.email)
    else:
        reward_value = grade_hard(req.action, obs.email)

    return {
        "observation": obs,
        "reward": safe_score(reward_value),
        "done": done,
        "info": info
    }


# ----------------------------
# COMPARE
# ----------------------------

@app.post("/compare", response_model=CompareResult)
async def compare(req: CompareRequest):
    observation = Observation(
        email=req.email,
        task=req.task,
        step_count=1
    )

    action, reward, latency = await run_agent_once(observation, req.task)

    # 🔥 HARD SAFETY CHECK
    try:
        reward = float(reward)
    except:
        reward = EPS

    if not (0.0 < reward < 1.0):
        reward = safe_score(reward)

    return CompareResult(
        action=action,
        reward=reward,
        latency_ms=latency
    )

# ----------------------------
# RUN (FIXED)
# ----------------------------

@app.post("/run", response_model=RunResponse)
async def run_episode(req: RunRequest):
    env = EmailEnv(task=req.task, max_steps=req.max_steps)
    observation = env.reset()

    steps = []
    total_reward = 0.0

    for step in range(req.max_steps):
        action, _, latency = await run_agent_once(observation, req.task)

        try:
            next_obs, _, done, _ = env.step(action)

            # 🔥 USE YOUR GRADER HERE
            if req.task == "easy":
                reward_value = grade_easy(action, observation.email)
            elif req.task == "medium":
                reward_value = grade_medium(action, observation.email)
            else:
                reward_value = grade_hard(action, observation.email)

        except Exception:
            reward_value = EPS
            done = True
            next_obs = observation

        steps.append(
            StepResult(
                step=step + 1,
                email_id=getattr(observation.email, "id", str(step)),
                action=action,
                reward=safe_score(reward_value),
                latency_ms=latency
            )
        )

        total_reward += safe_score(reward_value)
        observation = next_obs

        if done:
            break

    avg_reward = total_reward / len(steps) if steps else EPS

    # 🔥 CLAMP BOTH
    total_reward = safe_score(total_reward / len(steps))  # normalize first
    avg_reward = safe_score(avg_reward)

    return RunResponse(
        task=req.task,
        steps=steps,
        total_reward=total_reward,
        average_reward=avg_reward
    )


# ----------------------------
# ROOT
# ----------------------------

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <h1>📧 Email OpenEnv Assistant</h1>
    <p>Your environment is running successfully ✅</p>
    <p>Available endpoints:</p>
    <ul>
        <li><b>/run</b> - Run full task episode</li>
        <li><b>/compare</b> - Test single email</li>
    </ul>
    <p>Use Postman / curl / Swagger to interact.</p>
    """


# ----------------------------
# RUN SERVER
# ----------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000)