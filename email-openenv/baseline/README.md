# Baseline Agent

A baseline agent for the OpenEnv email assistant environment using the Gemini API.

## Features

- **Task Support**: All three task types
  - `easy`: Spam classification (is_spam: bool)
  - `medium`: Priority detection (priority: string)
  - `hard`: Reply generation (should_reply: bool, reply_text: string)
- **Gemini Integration**: Uses Gemini-2.5-flash to generate actions
- **Robust JSON Parsing**: Handles various response formats including markdown code blocks
- **Detailed Logging**: Step-by-step output with rewards and statistics

## Prerequisites

1. **Gemini API Key**: Set `GEMINI_API_KEY` environment variable
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

2. **Dependencies**:
   ```bash
   pip install google-genai pydantic
   ```

## Usage

### Run with defaults (easy task, 5 steps)
```bash
python run_agent.py
```

### Run specific task
```bash
python run_agent.py --task easy
python run_agent.py --task medium
python run_agent.py --task hard
```

### Run with custom max steps
```bash
python run_agent.py --task hard --max-steps 10
```

## Output Example

```
============================================================
OpenEnv Baseline Agent - Task: EASY
============================================================

Step 1:
  Email: sender@example.com - Check out our amazing offer!
  Action: {'is_spam': True}
  Reward: 1.000

Step 2:
  Email: boss@company.com - Urgent meeting tomorrow
  Action: {'is_spam': False}
  Reward: 1.000

============================================================
Episode Complete - Task: EASY
============================================================
Total Steps: 2
Step Rewards: ['1.000', '1.000']
Total Reward: 2.000
Average Reward: 1.000
============================================================
```

## How It Works

1. **Initialize Environment**: Creates `EmailEnv` with specified task
2. **Reset**: Gets initial observation (first email)
3. **Agent Loop**: For each email:
   - Format email as prompt
   - Call Gemini API with task-specific instructions
   - Parse JSON response
   - Execute action via `env.step()`
   - Accumulate reward
4. **Report Results**: Print statistics including total and average reward

## Task-Specific Action Schemas

### Easy (Spam Classification)
```json
{
  "is_spam": true/false
}
```

### Medium (Priority Detection)
```json
{
  "priority": "low" | "medium" | "high" | "urgent"
}
```

### Hard (Reply Generation)
```json
{
  "should_reply": true/false,
  "reply_text": "Your reply text here"
}
```

## Error Handling

The agent gracefully handles:
- Invalid JSON responses (tries to extract from markdown blocks)
- API errors (continues with next step)
- Empty API key (raises clear error message)
- Interrupted execution (catches KeyboardInterrupt)
