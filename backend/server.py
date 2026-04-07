import os
import time
import asyncio
from typing import List, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from backend.env import EmailEnv
from backend.env.models import Email, Observation

from backend.graders.easy_grader import grade_easy
from backend.graders.medium_grader import grade_medium
from backend.graders.hard_grader import grade_hard

from backend.baseline.run_agent import generate_action

def get_client():
    from openai import OpenAI
    import os

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("API_BASE_URL")

    if not api_key:
        return None

    return OpenAI(api_key=api_key, base_url=base_url)
# Load environment variables
load_dotenv()

app = FastAPI(
    title="Email OpenEnv API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS (for frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Request / Response Models
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
# Helper: Run agent
# ----------------------------

async def run_agent_once(observation: Observation, task: str):
    start = time.perf_counter()

    client = get_client()

    try:
        if client:
            # ✅ Use OpenAI via your existing agent logic
            action = generate_action(client, observation, task)
        else:
            # ✅ fallback to mock agent
            from backend.baseline.mock_agent import generate_mock_action
            action = generate_mock_action(observation, task)

    except Exception as e:
        action = {"error": str(e)}

    latency = (time.perf_counter() - start) * 1000

    # Grading
    if "error" not in action:
        if task == "easy":
            reward = grade_easy(action, observation.email)
        elif task == "medium":
            reward = grade_medium(action, observation.email)
        else:
            reward = grade_hard(action, observation.email)
    else:
        reward = 0.0

    return action, reward, latency


# ----------------------------
# Endpoint: Compare (single step)
# ----------------------------

@app.post("/compare", response_model=CompareResult)
async def compare(req: CompareRequest):
    observation = Observation(
        email=req.email,
        task=req.task,
        step_count=1
    )

    action, reward, latency = await run_agent_once(observation, req.task)

    return CompareResult(
        action=action,
        reward=reward,
        latency_ms=latency
    )


# ----------------------------
# Endpoint: Run full episode
# ----------------------------

@app.post("/run", response_model=RunResponse)
async def run_episode(req: RunRequest):
    env = EmailEnv(task=req.task, max_steps=req.max_steps)
    observation = env.reset()

    steps = []
    total_reward = 0.0

    for step in range(req.max_steps):
        action, reward, latency = await run_agent_once(observation, req.task)

        try:
            next_obs, env_reward, done, _ = env.step(action)
            reward_value = env_reward.value  # Extract value from Reward object
        except Exception:
            reward_value = 0.0
            done = True
            next_obs = observation

        steps.append(
            StepResult(
                step=step + 1,
                email_id=getattr(observation.email, "id", str(step)),
                action=action,
                reward=reward_value,
                latency_ms=latency
            )
        )

        total_reward += reward_value
        observation = next_obs

        if done:
            break

    avg_reward = total_reward / len(steps) if steps else 0.0

    return RunResponse(
        task=req.task,
        steps=steps,
        total_reward=total_reward,
        average_reward=avg_reward
    )
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
# Run serverYes
# ----------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)