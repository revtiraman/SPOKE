# 🎙️ Spoke
### *"You spoke. It shipped."*

**Record a 60-second video about a business problem. Spoke builds you a working autonomous AI agent. Automatically. No code required.**

---

## ⚡ The 2-Minute Demo

```bash
git clone https://github.com/your-username/spoke
cd spoke
pip install -r requirements.txt
python demo_cli.py
```

Watch 8 AI agents design, write, test, and fix their own code in real time. No credentials needed.

---

## 🧠 What Is Spoke?

Spoke is an **8-agent autonomous pipeline** that converts a spoken problem description into a deployed AI agent.

A founder records 60 seconds: *"I waste 2 hours every day copying order emails into my spreadsheet."*

Ten minutes later, a working agent is live — reading real emails, extracting order data, updating a real spreadsheet. Nobody helped it. Nobody coded it. **It built itself.**

---

## 🔁 The 8-Agent Pipeline

```
[VIDEO INPUT]
      ↓
[AGENT 1: TRANSCRIBER]    whisper-large-v3      → speech to text
      ↓
[AGENT 2: ANALYST]        Kimi-K2-Instruct      → problem graph extraction
      ↓
[AGENT 3: CLARIFIER]      Llama-3.3-70B         → 2 targeted follow-up questions
      ↓
[AGENT 4: ARCHITECT]      DeepSeek-R1           → complete solution blueprint
      ↓
[AGENT 5: CODER]          Qwen3-Coder-30B       → production Python code
      ↓
[AGENT 6: EXECUTOR]       sandbox               → runs the code
      ↓
[AGENT 7: DEBUGGER]       Qwen3-Coder-30B       → reads errors, fixes code, retries
      ↓
[AGENT 8: DEPLOYER]       Llama-3.3-70B         → packages + report
      ↓
[LIVE WORKING AGENT]
```

---

## 🚀 Quick Start

### Option 1 — One command (recommended)
```bash
./run.sh demo
```

### Option 2 — Manual
```bash
# Install
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure (optional — demo works without credentials)
cp .env.example .env
# Add your HF_API_TOKEN for full pipeline

# Run the UI
streamlit run frontend/app.py

# Or run CLI demo
python demo_cli.py

# Or run a specific transcript
python demo_cli.py --transcript "I spend 3 hours updating CRM records from customer emails"
```

### Option 3 — Full stack with API
```bash
uvicorn main:app --reload &
streamlit run frontend/app.py
```

---

## 🏗️ Architecture

```
spoke/
├── agents/           # All 8 autonomous agents
│   ├── transcriber.py
│   ├── analyst.py
│   ├── clarifier.py
│   ├── architect.py
│   ├── coder.py
│   ├── executor.py
│   ├── debugger.py
│   └── deployer.py
├── core/
│   ├── pipeline.py   # Orchestrates all 8 agents
│   ├── models.py     # Pydantic data models
│   ├── config.py     # Settings from environment
│   └── state.py      # SQLite session storage
├── llm/
│   ├── client.py     # Unified HF + Anthropic client
│   ├── router.py     # Model selection per task
│   └── prompts/      # System prompts for each agent
├── sandbox/
│   ├── runner.py     # Sandbox execution engine
│   └── validator.py  # Safety + completeness checks
├── api/
│   ├── routes.py     # FastAPI REST endpoints
│   └── websocket.py  # Real-time progress streaming
├── frontend/
│   └── app.py        # Stunning Streamlit UI
├── tests/            # Pytest test suite
├── main.py           # FastAPI entrypoint
├── demo_cli.py       # Terminal demo
└── run.sh            # One-command startup
```

---

## 🤖 Models Used

| Agent | Model | Why |
|-------|-------|-----|
| Transcriber | `openai/whisper-large-v3` | Best open-source speech recognition |
| Analyst | `moonshotai/Kimi-K2-Instruct` | Long context, deep reasoning |
| Clarifier | `meta-llama/Llama-3.3-70B-Instruct` | Fast, free tier |
| Architect | `deepseek-ai/DeepSeek-R1` | Best planning and reasoning |
| Coder | `Qwen/Qwen3-Coder-30B-A3B-Instruct` | Best open-source coder |
| Debugger | `Qwen/Qwen3-Coder-30B-A3B-Instruct` | Same coder for consistency |
| Deployer | `meta-llama/Llama-3.3-70B-Instruct` | Fast report generation |

---

## ⚙️ Configuration

```bash
# .env
HF_API_TOKEN=hf_your_token         # Required for full pipeline
ANTHROPIC_API_KEY=optional         # Optional premium brain
SANDBOX_TYPE=subprocess            # subprocess | e2b | docker
MAX_DEBUG_RETRIES=5                # Self-healing retry limit
DEMO_MODE=false                    # true = skip all API calls
```

---

## 🧪 Tests

```bash
pytest tests/ -v
# or just the fast unit tests:
pytest tests/test_transcriber.py tests/test_coder.py tests/test_executor.py -v
```

---

## 📡 API

```
POST /api/v1/pipeline/demo          → Full demo run
POST /api/v1/pipeline/run/text      → Run from transcript text
POST /api/v1/pipeline/run/video     → Upload video + run
POST /api/v1/pipeline/resume        → Resume after clarification
GET  /api/v1/download/{session_id}  → Download agent ZIP
GET  /api/v1/health                 → Health + usage stats
WS   /ws/{session_id}               → Real-time progress stream
```

---

## 🏆 Why Spoke Wins

| Criterion | Spoke |
|-----------|-------|
| **AI-native** | Zero human in loop. Video → deployed agent. |
| **Creativity** | Nobody has built video → software before |
| **Does it work?** | Full demo with live agent output |
| **Code quality** | Typed Python, Pydantic v2, async, full error handling |

---

## 📋 Submission Notes

> Spoke is an 8-agent autonomous pipeline that converts a spoken video description of a business problem into a working, deployed AI agent — with no human coding involved.
>
> Pipeline: Video → Whisper → Problem extraction (Kimi-K2) → Architecture design (DeepSeek-R1) → Code generation (Qwen Coder) → Sandbox execution → Self-healing debug loop → Deployment package.
>
> Stack: Python 3.11, FastAPI, Streamlit, HuggingFace Inference API, Whisper, SQLite, subprocess sandbox.

---



**You spoke. It shipped.**
