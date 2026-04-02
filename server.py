import os
import sys
import time
import asyncio
from typing import Literal, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import google.genai as genai
from groq import Groq

# Add local path to import env
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from env.models import Email, Observation
from env import EmailEnv
from env.graders import TaskGrader

# Import agent logic
from baseline import run_agent as gemini_agent
from baseline import groq_agent as groq_agent1
from baseline import groq_agent2

load_dotenv()

app = FastAPI(title="OpenEnv Email Assistant API")

# Add CORS for localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://127.0.0.1", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompareRequest(BaseModel):
    task: Literal["easy", "medium", "hard"]
    email: Email

class CompareResult(BaseModel):
    agent_id: str
    model_name: str
    action: dict
    reward: float
    latency_ms: float

class RunRequest(BaseModel):
    agent_id: Literal["gemini", "groq1", "groq2"]
    task: Literal["easy", "medium", "hard"]
    max_steps: int = 5

class StepResult(BaseModel):
    step: int
    email_id: str
    action: dict
    reward: float
    latency_ms: float

class RunResponse(BaseModel):
    agent_id: str
    task: str
    steps: List[StepResult]
    total_reward: float
    average_reward: float

# Initialize clients (ensure keys are present if used)
gemini_client = None
if os.getenv("GEMINI_API_KEY"):
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

groq_client = None
if os.getenv("GROQ_API_KEY"):
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


async def _run_agent_async(agent_id: str, observation: Observation, task: str) -> CompareResult:
    start_time = time.perf_counter()
    action = {}
    try:
        # Wrap synchronous SDK calls in asyncio.to_thread to run in parallel, non-blocking
        if agent_id == "gemini":
            if not gemini_client:
                raise ValueError("GEMINI_API_KEY not set")
            action = await asyncio.to_thread(gemini_agent.generate_action, gemini_client, observation, task)
        elif agent_id == "groq1":
            if not groq_client:
                raise ValueError("GROQ_API_KEY not set")
            action = await asyncio.to_thread(groq_agent1.generate_action, groq_client, observation, task)
        elif agent_id == "groq2":
            if not groq_client:
                raise ValueError("GROQ_API_KEY not set")
            action = await asyncio.to_thread(groq_agent2.generate_action, groq_client, observation, task)
    except Exception as e:
        action = {"error": str(e)}

    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000.0

    # Calculate reward if true_label is present
    reward = 0.0
    if observation.email.true_label and "error" not in action:
        reward = TaskGrader.grade(task, action, observation.email.true_label)

    model_name = "gemini-2.5-flash"
    if agent_id == "groq1":
        model_name = "llama-3.3-70b-versatile"
    elif agent_id == "groq2":
        model_name = "llama-3.1-8b-instant"

    return CompareResult(
        agent_id=agent_id,
        model_name=model_name,
        action=action,
        reward=reward,
        latency_ms=latency_ms
    )


@app.post("/compare", response_model=List[CompareResult])
async def compare_agents(req: CompareRequest):
    """Run all 3 agents in parallel on a single email."""
    observation = Observation(email=req.email, task=req.task, step_count=1)
    
    # Run in parallel
    results = await asyncio.gather(
        _run_agent_async("gemini", observation, req.task),
        _run_agent_async("groq1", observation, req.task),
        _run_agent_async("groq2", observation, req.task)
    )
    return list(results)


@app.post("/run", response_model=RunResponse)
async def run_episode(req: RunRequest):
    """Run a full episode on emails.json for one agent."""
    env = EmailEnv(task=req.task, max_steps=req.max_steps)
    observation = env.reset()

    steps = []
    total_reward = 0.0

    for step in range(req.max_steps):
        result = await _run_agent_async(req.agent_id, observation, req.task)
        
        try:
            # Step the environment forward with the action
            next_obs, reward, done, info = env.step(result.action)
        except Exception as e:
            # If the action was malformed according to the env
            reward = 0.0
            done = True
            next_obs = observation # Fallback to prevent crash

        steps.append(
            StepResult(
                step=step + 1,
                email_id=observation.email.id,
                action=result.action,
                reward=reward,
                latency_ms=result.latency_ms
            )
        )
        total_reward += reward
        observation = next_obs
        
        if done:
            break

    avg_reward = total_reward / len(steps) if steps else 0.0

    return RunResponse(
        agent_id=req.agent_id,
        task=req.task,
        steps=steps,
        total_reward=total_reward,
        average_reward=avg_reward
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
