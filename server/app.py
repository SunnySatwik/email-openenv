from fastapi import FastAPI
from backend.env.environment import EmailEnv
import uvicorn

app = FastAPI()

env = EmailEnv(task="easy")


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/reset")
def reset():
    obs = env.reset()
    return obs.dict()


@app.post("/step")
def step(action: dict):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.dict(),
        "reward": reward.dict(),
        "done": done,
        "info": info.dict()
    }


@app.get("/state")
def state():
    return env.state()


# ✅ REQUIRED for OpenEnv
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


# ✅ REQUIRED entrypoint check
if __name__ == "__main__":
    main()