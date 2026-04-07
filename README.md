# 📧 Email OpenEnv Assistant

> **AI Agent Evaluation Environment for Email Management Tasks**

An intelligent, modular environment for benchmarking and comparing AI agents on real-world email handling challenges. Not just a classifier—a complete evaluation framework with sophisticated grading logic and seamless LLM integration.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.100+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 🎯 Quick Start - Try It Now

### Test Without Installation (API Endpoints)

**Base URL:** `https://dante6969-email-openenv.hf.space`

#### Using cURL:
```bash
# Test spam detection
curl -X POST "https://dante6969-email-openenv.hf.space/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "easy",
    "email": {
      "id": "test_001",
      "sender": "promotions@store.com",
      "subject": "EXCLUSIVE OFFER: 50% OFF NOW!!!",
      "body": "Click here to get free money! Limited time offer! Buy now!",
      "timestamp": "2024-04-07T10:00:00Z",
      "true_label": {"spam": true}
    }
  }'
```

#### Using Python:
```python
import requests
import json

response = requests.post(
    "https://dante6969-email-openenv.hf.space/compare",
    json={
        "task": "easy",
        "email": {
            "id": "test_001",
            "sender": "john@company.com",
            "subject": "Meeting tomorrow at 2pm",
            "body": "Hi, can we confirm our meeting tomorrow?",
            "timestamp": "2024-04-07T10:00:00Z",
            "true_label": {"priority": "high"}
        }
    }
)
print(json.dumps(response.json(), indent=2))
```

#### Using Postman/Swagger:
1. Visit: `https://dante6969-email-openenv.hf.space/docs`
2. Select **POST /compare**
3. Click "Try it out"
4. Paste the JSON payload
5. Click "Execute"

---

## ✨ Features

### 🎓 Three Task Difficulty Levels

| Task | Complexity | Goal | Example |
|------|-----------|------|---------|
| **Spam Detection** (easy) | ⭐ | Binary classification | Identify promotional vs. legitimate |
| **Priority Classification** (medium) | ⭐⭐ | Multi-class ranking | LOW / MEDIUM / HIGH / URGENT |
| **Reply Generation** (hard) | ⭐⭐⭐ | Decision + content generation | Decide if reply needed + draft response |

### 🧠 Advanced Grading System

- **Spam-Aware Logic**: Reply grader understands unwanted emails and won't assign scores for replying to spam
- **Weighted Scoring**: Multi-component grading (decision correctness 50%, relevance 30%, quality 20%)
- **Continuous Rewards**: 0.0-1.0 scale enables gradient-based learning
- **Fallback Scoring**: Graceful handling of incomplete data

### 🤖 LLM Agent Support

- **OpenAI-Compatible APIs**: Works with GPT, Claude, Gemini, Groq endpoints
- **Built-in Mock Agent**: Test without API keys using intelligent heuristics
- **Graceful Degradation**: Automatic fallback if LLM fails
- **Custom Integration**: Plug in your own models easily

### 🎮 Interactive Dashboard

- **Next.js Frontend**: Modern, responsive web interface
- **Real-time Analysis**: See results for all three task types instantly
- **Reward Visualization**: Track performance metrics
- **Error Handling**: User-friendly error messages

### 🚀 Production-Ready Backend

- **FastAPI Server**: High-performance async API
- **Docker Support**: Container-ready for deployment
- **CORS Enabled**: Works with any frontend
- **Reproducible**: Seed-based deterministic episodes

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Email OpenEnv System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Frontend (Next.js Dashboard)              │   │
│  │  - Interactive email input                          │   │
│  │  - Real-time results visualization                  │   │
│  │  - Switch between task types                        │   │
│  └──────────────────┬──────────────────────────────────┘   │
│                     │ HTTP/REST                             │
│  ┌──────────────────▼──────────────────────────────────┐   │
│  │         FastAPI Backend (Python)                    │   │
│  │  - /run      → Full episode evaluation              │   │
│  │  - /compare  → Single email analysis                │   │
│  │  - /reset    → Initialize new session               │   │
│  │  - /step     → Manual step control                  │   │
│  └──────────┬──────────────────┬───────────────────────┘   │
│             │                  │                            │
│  ┌──────────▼──────┐  ┌────────▼──────────────────┐        │
│  │  Agent Manager  │  │   EmailEnv Simulator     │        │
│  │                 │  │                          │        │
│  │ • OpenAI        │  │ • Reset/Step interface   │        │
│  │ • Gemini        │  │ • Episode tracking       │        │
│  │ • Groq          │  │ • Reward calculation     │        │
│  │ • Mock Agent    │  │ • State management       │        │
│  └──────────┬──────┘  └────────┬─────────────────┘        │
│             │                  │                            │
│  ┌──────────▼──────────────────▼──────────────────┐        │
│  │          Custom Graders                        │        │
│  │                                                │        │
│  │  • easy_grader.py   (spam classification)      │        │
│  │  • medium_grader.py (priority ranking)         │        │
│  │  • hard_grader.py   (reply generation)         │        │
│  │    ├─ Spam detection                           │        │
│  │    ├─ Decision scoring                         │        │
│  │    ├─ Relevance scoring                        │        │
│  │    └─ Quality scoring                          │        │
│  └──────────┬───────────────────────────────────┘        │
│             │                                              │
│  ┌──────────▼──────────────────────────────────┐         │
│  │     Email Dataset (emails.json)             │         │
│  │                                              │         │
│  │  • 50+ realistic email examples              │         │
│  │  • Ground truth labels for all tasks         │         │
│  │  • Mix of work/spam/informational emails     │         │
│  └──────────────────────────────────────────────┘         │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 How It Works

### Step-by-Step Flow

```
1. INITIALIZE
   └─→ EmailEnv(task="easy|medium|hard", max_steps=10, seed=42)
       └─→ Load email dataset
       └─→ Set random seed for reproducibility

2. RESET EPISODE
   └─→ env.reset()
       └─→ Shuffle emails (unless seeded)
       └─→ Return first observation

3. AGENT ANALYZES
   └─→ Agent receives Observation(email, task, step_count)
       └─→ Agent generates Action (task-specific)
           └─→ easy:   {"is_spam": bool}
           └─→ medium: {"priority": "low|medium|high|urgent"}
           └─→ hard:   {"should_reply": bool, "reply_text": "..."}

4. GRADING & REWARD
   └─→ Grader evaluates Action
       └─→ easy_grader(action, email)   → reward ∈ [0.0, 1.0]
       └─→ medium_grader(action, email) → reward ∈ [0.0, 1.0]
       └─→ hard_grader(action, email)   → reward ∈ [0.0, 1.0]

5. STEP COMPLETE
   └─→ env.step(action)
       └─→ Return: (next_obs, reward, done, info)
       └─→ Track episode rewards
       └─→ Move to next email

6. EPISODE COMPLETE
   └─→ When done=True or max_steps reached
       └─→ env.state() returns statistics
           └─→ total_reward, average_reward, steps completed
```

### Reward Breakdown

#### Easy (Spam Detection)
```
Exact match with ground truth       → 1.0
Wrong but email has spam markers    → 0.5
Wrong and no spam signals           → 0.0
```

#### Medium (Priority Classification)
```
Same priority level                 → 1.0
Off by 1 level (e.g., low→medium)  → 0.6
Off by 2 levels (e.g., low→high)   → 0.3
Off by 3+ levels                    → 0.0
```

#### Hard (Reply Generation)
```
Decision Correctness (50% weight):
  ✅ Correct should_reply decision  → 1.0 × 0.5 = 0.5
  ❌ Wrong decision                 → 0.0

Content Relevance (30% weight):
  Keyword overlap: min(overlap/10, 1.0) × 0.3

Response Quality (20% weight):
  Reply length ≥ 10 chars           → 1.0 × 0.2 = 0.2

Final Score = decision + relevance + quality
```

---

## 🔌 API Endpoints

### 1. POST /compare - Single Email Evaluation

Analyze a single email and get immediate results.

**Request:**
```bash
POST /compare
Content-Type: application/json

{
  "task": "easy|medium|hard",
  "email": {
    "id": "unique_id",
    "sender": "sender@example.com",
    "subject": "email subject",
    "body": "email body content",
    "timestamp": "2024-04-07T10:00:00Z",
    "true_label": {
      "spam": boolean,
      "priority": "low|medium|high|urgent",
      "reply_required": boolean
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

### 2. POST /run - Full Episode

Run a complete episode with multiple emails.

**Request:**
```bash
POST /run
Content-Type: application/json

{
  "task": "easy|medium|hard",
  "max_steps": 5
}
```

**Response:**
```json
{
  "task": "easy",
  "steps": [
    {
      "step": 1,
      "email_id": "email_001",
      "action": {"is_spam": false},
      "reward": 1.0,
      "latency_ms": 150.2
    },
    {
      "step": 2,
      "email_id": "email_002",
      "action": {"is_spam": true},
      "reward": 0.5,
      "latency_ms": 140.8
    }
  ],
  "total_reward": 3.8,
  "average_reward": 0.76
}
```

### 3. POST /reset - Initialize Session

Start a new evaluation session.

**Request:**
```bash
POST /reset?task=easy
```

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

### 4. POST /step - Manual Step Control

Execute a single step in the current session.

**Request:**
```bash
POST /step
Content-Type: application/json

{
  "action": {
    "is_spam": false
  }
}
```

**Response:**
```json
{
  "observation": { ... },
  "reward": 1.0,
  "done": false,
  "info": {
    "task": "easy",
    "email_id": "email_001",
    "ground_truth": {"spam": false},
    "action_type": "spam_classification"
  }
}
```

---

## 🚀 Run Locally

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/email-openenv.git
cd email-openenv

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables (optional)
export OPENAI_API_KEY="sk-..."
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"

# Run the server
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000
```

Server running at: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set API URL (optional)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

Frontend running at: `http://localhost:3000`

### Test Without LLM Keys

All agents gracefully fall back to mock heuristic if no API key is set:

```bash
# Backend will use mock agent automatically
python -m backend.baseline.mock_agent --task easy --max-steps 5

# Or run full environment test
python -m backend.example_usage
```

---

## 🐳 Deploy with Docker + Hugging Face Spaces

### Option 1: Docker Locally

```bash
# Build image
docker build -t email-openenv:latest .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="sk-..." \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  email-openenv:latest
```

Access at: `http://localhost:8000`

### Option 2: Deploy to Hugging Face Spaces

```bash
# 1. Create new Space on Hugging Face
# https://huggingface.co/new-space

# 2. Clone the Space repository
git clone https://huggingface.co/spaces/yourusername/email-openenv
cd email-openenv

# 3. Copy project files
cp -r /path/to/local/email-openenv/* .

# 4. Add Dockerfile and requirements.txt
# (Already included in this repo)

# 5. Push to Hugging Face
git add .
git commit -m "Deploy Email OpenEnv Assistant"
git push

# 6. Wait for automatic build & deployment
# Space will be available at:
# https://huggingface.co/spaces/yourusername/email-openenv
```

### Environment Variables (Hugging Face Secrets)

Set these in Space Settings → Secrets:
- `OPENAI_API_KEY` - Your OpenAI API key (optional)
- `API_BASE_URL` - Custom API endpoint (optional)
- `MODEL_NAME` - Model name, default "gpt-4o-mini"

---

## 🔧 Integrate Your Own AI Model

### Create Custom Agent

```python
# backend/baseline/my_agent.py

from backend.env import EmailEnv, Observation

def generate_my_action(observation: Observation, task: str) -> dict:
    """Your custom agent logic."""
    email = observation.email
    text = (email.subject + " " + email.body).lower()

    if task == "easy":
        # Spam detection logic
        is_spam = any(word in text for word in ["free", "offer", "buy"])
        return {"is_spam": is_spam}

    elif task == "medium":
        # Priority logic
        if "urgent" in text:
            priority = "urgent"
        elif "meeting" in text:
            priority = "high"
        else:
            priority = "low"
        return {"priority": priority}

    elif task == "hard":
        # Reply logic
        should_reply = "?" in text
        reply_text = "Thank you for your email." if should_reply else ""
        return {"should_reply": should_reply, "reply_text": reply_text}

    return {}


def run_my_agent(task: str = "easy", max_steps: int = 5):
    """Run your custom agent."""
    env = EmailEnv(task=task, max_steps=max_steps)
    observation = env.reset()

    total_reward = 0
    for step in range(max_steps):
        action = generate_my_action(observation, task)
        observation, reward, done, info = env.step(action)
        total_reward += reward.value

        print(f"Step {step+1}: Action={action}, Reward={reward.value:.2f}")

        if done:
            break

    print(f"Episode complete. Total reward: {total_reward:.2f}")
    return total_reward
```

### Register in FastAPI Server

```python
# backend/server.py

# Add import
from backend.baseline.my_agent import generate_my_action

# Update agent selection
async def run_agent_once(observation: Observation, task: str):
    start = time.perf_counter()

    try:
        # Try your custom agent first
        action = generate_my_action(observation, task)
    except Exception as e:
        print(f"Custom agent failed: {e}")
        # Fallback to mock agent
        from backend.baseline.mock_agent import generate_mock_action
        action = generate_mock_action(observation, task)

    latency = (time.perf_counter() - start) * 1000

    # Grade the action
    if task == "easy":
        reward = grade_easy(action, observation.email)
    # ... etc

    return action, reward, latency
```

---

## 📈 Example Outputs

### Spam Detection (Easy)

```
Input Email:
  From: promotions@store.com
  Subject: EXCLUSIVE OFFER: 50% OFF NOW!!!
  Body: Click here to get free money! Limited time offer! Buy now!

Agent Decision: {"is_spam": true}
Reward: 1.0 ✅
Latency: 145ms

Ground Truth: {"spam": true}
Result: CORRECT ✅
```

### Priority Classification (Medium)

```
Input Email:
  From: boss@company.com
  Subject: URGENT: Server down!
  Body: Production is affected. Need immediate action.

Agent Decision: {"priority": "urgent"}
Reward: 1.0 ✅
Latency: 132ms

Ground Truth: {"priority": "urgent"}
Result: CORRECT ✅
```

### Reply Generation (Hard)

```
Input Email:
  From: john@company.com
  Subject: Can you review the document?
  Body: Hi, can you review the attached document by EOD?

Agent Decision:
  {
    "should_reply": true,
    "reply_text": "Thank you for sharing. I will review the document and provide feedback shortly."
  }

Reward Breakdown:
  - Decision Correctness: 1.0 (should_reply=true is correct)
  - Content Relevance: 0.8 (mentions 'review' and 'feedback')
  - Response Quality: 1.0 (reply > 10 chars, professional tone)

Final Reward: 0.5×1.0 + 0.3×0.8 + 0.2×1.0 = 0.94 ✅
Latency: 287ms

Ground Truth: {"reply_required": true}
Result: CORRECT ✅
```

---

## 💻 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 | Interactive dashboard |
| **Styling** | Tailwind CSS | Modern, responsive UI |
| **Backend** | FastAPI | High-performance REST API |
| **Language** | Python 3.9+ | Core logic & AI integration |
| **Data** | Pydantic | Type-safe data validation |
| **LLM Support** | OpenAI SDK | API integration |
| **Deployment** | Docker | Containerization |
| **Hosting** | Hugging Face Spaces | Production deployment |
| **Testing** | Pytest | Unit & integration tests |

---

## 🎯 Why This Project Stands Out

### 🎓 Not Just a Classifier
Unlike traditional email classifiers, this is a **complete evaluation framework** with nuanced grading logic that understands real-world email complexity.

### 🔌 Plug-and-Play Integration
Support for **any OpenAI-compatible LLM**: GPT, Claude, Gemini, Groq, local models, etc.

### 🧠 Intelligent Grading
- **Context-Aware**: Understands spam and won't reward replying to unwanted emails
- **Multi-Component**: Evaluates decision quality, relevance, and response quality
- **Continuous Feedback**: 0.0-1.0 scale enables gradient-based learning

### 🚀 Production-Ready
- Graceful fallbacks (mock agent if LLM fails)
- CORS-enabled API
- Docker & cloud deployment ready
- Comprehensive error handling

### 📊 Benchmark Different Agents
Compare performance across multiple AI systems using identical evaluation criteria.

---

## 🚧 Future Improvements

- [ ] **Multi-Agent Comparison**: Side-by-side performance dashboard
- [ ] **Fine-tuning Support**: Train custom models on environment
- [ ] **Real Email Integration**: Connect to Gmail/Outlook API
- [ ] **Advanced Analytics**: Breakdown by email category/sender
- [ ] **A/B Testing**: Compare agent versions automatically
- [ ] **Streaming Responses**: Watch reply generation in real-time
- [ ] **Custom Grader Logic**: User-defined grading functions
- [ ] **Batch Processing**: Evaluate datasets at scale
- [ ] **Performance Optimization**: Caching & async improvements
- [ ] **Mobile App**: iOS/Android companion app

---

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/SunnySatwik/email-openenv/issues)
- 💬 **Questions**: Open a GitHub Discussion
- 📧 **Email**: your-email@example.com

---

## 🎉 Acknowledgments

Built with ❤️ for:
- **OpenAI** - For GPT models and API
- **Hugging Face** - For Spaces hosting
- **FastAPI** - For the amazing web framework
- **Next.js** - For the frontend framework
- **The Open Source Community** - For endless inspiration

---

<div align="center">

**Made with 💙 by Sunny Satwik and Soujanya Roy**

[⭐ Star us on GitHub](https://github.com/SunnySatwik/email-openenv) • (https://github.com/soujo05/email-openenv) • [🚀 Deploy to Spaces](https://huggingface.co/spaces) 

</div>
