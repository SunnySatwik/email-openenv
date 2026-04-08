---
title: Email OpenEnv Assistant
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
---
<!--
⚠️ This block is required for Hugging Face Spaces configuration.
It is ignored by the app but required for deployment.
-->

# 📧 Email OpenEnv

> **An open evaluation environment for benchmarking AI agents on real-world email tasks**

Most AI email tools just classify. **Email OpenEnv** is different — it's a complete, modular benchmarking framework where any AI agent can be evaluated across three real-world email challenges using a sophisticated, multi-component reward system.

Think of it as a gym for email AI: plug in any LLM, run it through standardized episodes, and get reproducible performance scores you can actually compare.

---

## 🚀 Try It Now — No Setup Required

The live API is deployed on Hugging Face Spaces:

**Base URL:** `https://dante6969-email-openenv.hf.space`  
**Interactive Docs (Swagger):** [`/docs`](https://dante6969-email-openenv.hf.space/docs)


### Quick test with Python

```python
import requests, json

response = requests.post(
    "https://dante6969-email-openenv.hf.space/compare",
    json={
        "task": "medium",
        "email": {
            "id": "test_002",
            "sender": "boss@company.com",
            "subject": "URGENT: Server down in production",
            "body": "Production is affected right now. We need immediate action.",
            "timestamp": "2024-04-07T10:00:00Z",
            "true_label": {"priority": "urgent"}
        }
    }
)
print(json.dumps(response.json(), indent=2))
```

### With Swagger UI

1. Visit [`https://dante6969-email-openenv.hf.space/docs`](https://dante6969-email-openenv.hf.space/docs)
2. Select **POST /compare** → click "Try it out"
3. Paste any payload from the examples above
4. Click **Execute**

---

## 🎯 The Three Evaluation Tasks

Email OpenEnv tests agents at three levels of increasing complexity:

| Level | Task | Input → Output | Scoring |
|-------|------|----------------|---------|
| ⭐ **Easy** | Spam Detection | Email → `{"is_spam": bool}` | Binary + partial credit for signal presence |
| ⭐⭐ **Medium** | Priority Classification | Email → `{"priority": "low\|medium\|high\|urgent"}` | Graded by distance from ground truth |
| ⭐⭐⭐ **Hard** | Reply Generation | Email → `{"should_reply": bool, "reply_text": "..."}` | Weighted: decision (50%) + relevance (30%) + quality (20%) |

---

## 🧠 Reward System Deep Dive

All rewards are continuous in `[0.0, 1.0]`, enabling gradient-based learning and fine-grained comparisons.

### Easy — Spam Detection

```
Exact match with ground truth       → 1.0
Wrong, but email has spam markers   → 0.5  (partial credit)
Wrong, no spam signals present      → 0.0
```

### Medium — Priority Classification

```
Same priority level                           → 1.0
Off by 1 (e.g., medium → high)               → 0.6
Off by 2 (e.g., low → high)                  → 0.3
Off by 3+ levels                              → 0.0
```

### Hard — Reply Generation

```
Decision Correctness  (50% weight)
  ✅ Correct should_reply decision  → 0.5
  ❌ Wrong decision                 → 0.0

Content Relevance     (30% weight)
  Keyword overlap score: min(overlap / 10, 1.0) × 0.3

Response Quality      (20% weight)
  Reply length ≥ 10 words + polite tone → 0.2

Final = decision + relevance + quality   ∈ [0.0, 1.0]
```

> **Spam-aware logic:** The hard grader detects spam emails and will not award points for drafting a reply to unwanted messages — even if the reply itself looks polished.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Email OpenEnv System                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          Frontend (Next.js 14 Dashboard)            │    │
│  │  • Interactive email input                          │    │
│  │  • Real-time results across all 3 task types        │    │
│  │  • Reward & latency visualization                   │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │ HTTP / REST                       │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │            FastAPI Backend (Python)                 │    │
│  │  POST /compare  →  Single email analysis            │    │
│  │  POST /run      →  Full episode (multi-step)        │    │
│  │  POST /reset    →  Initialize new session           │    │
│  │  POST /step     →  Manual step-by-step control      │    │
│  └──────────┬───────────────────────┬──────────────────┘    │
│             │                       │                       │
│  ┌──────────▼──────┐   ┌────────────▼───────────────┐       │
│  │  Agent Manager  │   │    EmailEnv Simulator      │       │
│  │  • OpenAI       │   │  • Gym-style reset/step    │       │
│  │  • Gemini       │   │  • Episode & state mgmt    │       │
│  │  • Groq         │   │  • Seeded reproducibility  │       │
│  │  • Mock Agent   │   │  • Reward calculation      │       │
│  └──────────┬──────┘   └────────────┬───────────────┘       │
│             └──────────────┬────────┘                       │
│                  ┌─────────▼────────────────────┐           │
│                  │      Custom Graders          │           │
│                  │  easy_grader.py   (spam)     │           │
│                  │  medium_grader.py (priority) │           │
│                  │  hard_grader.py   (reply)    │           │
│                  └─────────┬────────────────────┘           │
│                  ┌─────────▼────────────────────┐           │
│                  │   Email Dataset (emails.json)│           │
│                  └──────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📡 API Reference

### `POST /compare` — Single email analysis

Evaluate one email across all graders and return immediate results.

**Request body:**

```json
{
  "task": "easy | medium | hard",
  "email": {
    "id": "string",
    "sender": "sender@example.com",
    "subject": "string",
    "body": "string",
    "timestamp": "2024-04-07T10:00:00Z",
    "true_label": {
      "spam": true,
      "priority": "low | medium | high | urgent",
      "reply_required": true
    }
  }
}
```

**Response:**

```json
{
  "action": {
    "is_spam": true,
    "priority": "high",
    "should_reply": true,
    "reply_text": "Thank you for your email..."
  },
  "reward": 0.85,
  "latency_ms": 245.5
}
```

---

### `POST /run` — Full episode

Run a complete multi-step episode and get aggregated results.

**Request:**

```json
{
  "task": "easy | medium | hard",
  "max_steps": 5
}
```

**Response:**

```json
{
  "task": "easy",
  "steps": [
    { "step": 1, "email_id": "email_001", "action": {"is_spam": false}, "reward": 1.0, "latency_ms": 150.2 },
    { "step": 2, "email_id": "email_002", "action": {"is_spam": true},  "reward": 0.5, "latency_ms": 140.8 }
  ],
  "total_reward": 3.8,
  "average_reward": 0.76
}
```

---

### `POST /reset` — Start new session

Initializes a fresh evaluation session and returns the first email observation.

**Request:** `POST /reset?task=easy`

**Response:**

```json
{
  "email": {
    "id": "email_001",
    "sender": "john@company.com",
    "subject": "Meeting tomorrow",
    "body": "Can we meet tomorrow at 2pm?",
    "timestamp": "2024-04-07T09:30:00Z"
  },
  "step_count": 0,
  "task": "easy"
}
```

---

### `POST /step` — Manual step

Execute one step in an active session (use after `/reset`).

**Request:**

```json
{ "action": { "is_spam": false } }
```

**Response:**

```json
{
  "observation": { "..." : "..." },
  "reward": 1.0,
  "done": false,
  "info": {
    "task": "easy",
    "email_id": "email_001",
    "ground_truth": { "spam": false },
    "action_type": "spam_classification"
  }
}
```

---

## 💡 How the Environment Works

The flow follows a standard Gym-style interface, making it easy to plug into existing RL or evaluation pipelines:

```
1. INITIALIZE
   └─→ EmailEnv(task="easy|medium|hard", max_steps=10, seed=42)
       ├─→ Load emails.json
       └─→ Fix random seed for reproducibility

2. RESET EPISODE
   └─→ env.reset()
       └─→ Shuffle emails (unless seeded)
       └─→ Return first Observation

3. AGENT ACTS
   └─→ Agent receives Observation(email, task, step_count)
       └─→ Produces an Action:
           easy:   { "is_spam": bool }
           medium: { "priority": "low|medium|high|urgent" }
           hard:   { "should_reply": bool, "reply_text": "..." }

4. GRADE & REWARD
   └─→ Grader evaluates Action against ground truth
       └─→ Returns reward ∈ [0.0, 1.0]

5. ADVANCE
   └─→ env.step(action) → (next_obs, reward, done, info)
       └─→ Track rewards, move to next email

6. EPISODE END
   └─→ When done=True or max_steps reached
       └─→ env.state() → { total_reward, average_reward, steps }
```

---

## 📊 Example Outputs

### Spam Detection (Easy)

```
Email:   "EXCLUSIVE OFFER: 50% OFF NOW!!!" from promotions@store.com
Action:  { "is_spam": true }
Reward:  1.0 ✅ — exact match with ground truth
Latency: 145ms
```

### Priority Classification (Medium)

```
Email:   "URGENT: Server down!" from boss@company.com
Action:  { "priority": "urgent" }
Reward:  1.0 ✅ — exact match
Latency: 132ms
```

### Reply Generation (Hard)

```
Email:   "Can you review the attached document by EOD?"

Action:  {
  "should_reply": true,
  "reply_text": "Thank you for sharing. I will review the document and provide feedback shortly."
}

Breakdown:
  Decision correctness  → 1.0 × 0.50 = 0.50
  Content relevance     → 0.8 × 0.30 = 0.24  (8 of 10 keywords matched: score 8/10 = 0.8, then × 0.3)
  Response quality      → 1.0 × 0.20 = 0.20  (reply > 10 words, polite/professional tone)

Final Reward: 0.94 ✅
Latency: 287ms
```

---

## 💻 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 16 | Interactive evaluation dashboard |
| **Styling** | Tailwind CSS | Responsive, modern UI |
| **Backend** | FastAPI | Async REST API |
| **Language** | Python 3.9+ | Core logic & LLM integration |
| **Validation** | Pydantic | Type-safe data models |
| **LLM Support** | OpenAI SDK | Compatible with any OpenAI-style API |
| **Deployment** | Docker | Container-ready |
| **Hosting** | Hugging Face Spaces | Live production environment |
| **Testing** | Pytest | Unit & integration tests |

---

## 🖥️ Run Locally

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### Backend

```bash
# Clone the repository
git clone https://github.com/SunnySatwik/email-openenv.git
cd email-openenv

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# (Optional) Set your LLM credentials
export OPENAI_API_KEY="sk-..."
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"

# Start the server
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000
```

Server: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install

# Point the frontend at your local backend (optional)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
```

Frontend: `http://localhost:3000`

### Test Without an LLM Key

No API key? No problem. The environment automatically falls back to a mock heuristic agent:

```bash
# Run mock agent directly
python -m backend.baseline.mock_agent --task easy --max-steps 5

# Or run the full environment example
python -m backend.example_usage
```

### Test the Environment

```bash
# Run tests
pytest tests/ -v

# Run specific test module
pytest tests/test_graders.py -v
```

---

## 🐳 Deployment

### Docker (Local)

```bash
# Build image
docker build -t email-openenv:latest .

# Run container (HF-compatible port)
docker run -p 7860:7860 \
  -e OPENAI_API_KEY="sk-..." \
  -e API_BASE_URL="https://api.openai.com/v1" \
  -e MODEL_NAME="gpt-4o-mini" \
  email-openenv:latest
```
### 🔧 Port Notes

- Local backend runs on **port 8000**
- Frontend runs on **port 3000**
- Docker/Hugging Face uses **port 7860**
- Hugging Face public URL does **not expose ports**

### Hugging Face Spaces

```bash
# 1. Create a new Space at https://huggingface.co/new-space

# 2. Clone the Space repo
git clone https://huggingface.co/spaces/yourusername/email-openenv
cd email-openenv

# 3. Copy your project files in
cp -r /path/to/local/email-openenv/* .

# 4. Push — Hugging Face builds and deploys automatically
git add .
git commit -m "Deploy Email OpenEnv"
git push
```

Set these in **Space Settings → Secrets**:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI (or compatible) API key | Optional |
| `API_BASE_URL` | Custom LLM endpoint | Optional |
| `MODEL_NAME` | Model identifier (default: `gpt-4o-mini`) | Optional |

---

## 🔌 Integrate Your Own Agent

Plug in any custom logic — heuristics, fine-tuned models, or another LLM:

```python
# backend/baseline/my_agent.py

from backend.env import EmailEnv, Observation

def generate_my_action(observation: Observation, task: str) -> dict:
    email = observation.email
    text = (email.subject + " " + email.body).lower()

    if task == "easy":
        is_spam = any(word in text for word in ["free", "offer", "buy"])
        return {"is_spam": is_spam}

    elif task == "medium":
        if "urgent" in text:      priority = "urgent"
        elif "meeting" in text:   priority = "high"
        else:                     priority = "low"
        return {"priority": priority}

    elif task == "hard":
        should_reply = "?" in text
        reply = "Thank you for your email." if should_reply else ""
        return {"should_reply": should_reply, "reply_text": reply}

    return {}


def run_my_agent(task: str = "easy", max_steps: int = 5):
    env = EmailEnv(task=task, max_steps=max_steps)
    obs = env.reset()
    total_reward = 0.0

    for step in range(max_steps):
        action = generate_my_action(obs, task)
        obs, reward, done, info = env.step(action)
        total_reward += reward  # reward is a float in [0.0, 1.0]
        print(f"Step {step+1}: {action}  →  reward={reward:.2f}")
        if done:
            break

    print(f"Episode complete. Total reward: {total_reward:.2f}")
    return total_reward
```

Then register it in `backend/server.py` by importing and calling your agent in `run_agent_once()`, with fallback to the mock agent on failure.

---

## 🚧 Roadmap

- [ ] **Multi-agent comparison dashboard** — side-by-side performance across models
- [ ] **Fine-tuning support** — train custom models directly on environment episodes
- [ ] **Real email integration** — connect to Gmail / Outlook via API
- [ ] **Advanced analytics** — breakdown by email category, sender domain, time of day
- [ ] **A/B testing** — automatically compare agent versions across identical episode seeds
- [ ] **Streaming responses** — watch reply generation token-by-token
- [ ] **Custom grader logic** — user-defined scoring functions
- [ ] **Batch processing** — evaluate large datasets at scale
- [ ] **Leaderboard** — public benchmark rankings across submitted agents

---

## 🤝 Contributing

Contributions are welcome! Please follow the standard fork-and-PR workflow:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add: brief description'`
4. Push: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

Licensed under the **MIT License** — see [`LICENSE`](LICENSE) for details.

---

## 📞 Support & Contact

| Channel | Link |
|---------|------|
| 🐛 Bug Reports | [GitHub Issues](https://github.com/SunnySatwik/email-openenv/issues) |
| 💬 Questions | [GitHub Discussions](https://github.com/SunnySatwik/email-openenv/discussions) |
| 📧 Email (Sunny Satwik) | sunny.satwik10@gmail.com |
| 📧 Email (Soujanya Roy) | amisouja@gmail.com |

---

## 🙏 Acknowledgments

Built with ❤️ by **Sunny Satwik** and **Soujanya Roy**

Thanks to the tools that made this possible:

- [OpenAI](https://openai.com) — GPT models and the API standard that everyone now follows
- [Hugging Face](https://huggingface.co) — Spaces hosting and the open ML ecosystem
- [FastAPI](https://fastapi.tiangolo.com) — Possibly the cleanest Python web framework ever made
- [Next.js](https://nextjs.org) — The frontend framework that just works
- The open source community — for endless inspiration and free software

---

<div align="center">

[⭐ Star on GitHub (Sunny)](https://github.com/SunnySatwik/email-openenv) &nbsp;•&nbsp; [🤗 Live Demo](https://dante6969-email-openenv.hf.space) &nbsp;•&nbsp; [🚀 Deploy to Spaces](https://huggingface.co/new-space)

</div>

