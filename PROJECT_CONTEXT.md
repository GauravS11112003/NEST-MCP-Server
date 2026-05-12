# Prompt Opinion ADK Python - Project Context

> **Ready-to-use reference for rapid agent onboarding**

## Project Overview

**Name:** Prompt Opinion Agent Examples (po-adk-python-main)  
**Purpose:** Multi-agent system for healthcare workflows using Google ADK and A2A protocol  
**Platform:** Connects to [Prompt Opinion](https://promptopinion.ai)  
**Protocol:** A2A (Agent-to-Agent) Specification v1  
**Language:** Python 3.11+  

### Architecture

```
Prompt Opinion Platform
     │  POST / (X-API-Key + A2A JSON-RPC)
     ▼
┌─────────────────────────────────────────┐
│  shared/middleware.py (ApiKeyMiddleware) │
│  • Validates X-API-Key                 │
│  • Bridges FHIR metadata to session    │
└──────────────┬──────────────────────────┘
               │
   ┌───────────┼───────────┐
   ▼           ▼           ▼
healthcare_  general_   orchestrator
agent        agent           │
(FHIR)      (No FHIR)   delegates via AgentTool
   │           │              │
   │           │              ├──► healthcare_agent
   │           │              └──► general_agent
   ▼           ▼
shared/      local tools/
fhir_hook.py general.py
   │
   ▼
session state
(fhir_url, fhir_token, patient_id)
   │
   ▼
FHIR R4 Server
```

---

## Quick Start (New Agent)

### 1. Environment Setup

```bash
# Python is already installed: /Library/Frameworks/Python.framework/Versions/3.13/bin/python3

# Activate virtual environment
source .venv/bin/activate

# Verify packages
pip list | grep -E "google-adk|a2a-sdk|litellm|uvicorn|honcho"
```

### 2. Environment Variables (.env)

Key variables in `/Users/gauravshrivastava/projects/AgentsAssemble/po-adk-python-main/.env`:

```bash
# API Keys for LLM models
GOOGLE_API_KEY=AIzaSyBD7xL-XJPEUV3NaNO6czx1u6AVMJWr4e4

# API Keys for agent authentication (X-API-Key header)
API_KEYS=OXsqAr3EDvh-TT8ZSuOPb64VghYra9qO9zclgSmr0a4

# Model selection (optional - defaults to gemini/gemini-2.5-flash)
# HEALTHCARE_AGENT_MODEL=gemini/gemini-2.5-flash
# GENERAL_AGENT_MODEL=gemini/gemini-2.5-flash
# ORCHESTRATOR_MODEL=gemini/gemini-2.5-flash

# Public URLs (for Prompt Opinion)
HEALTHCARE_AGENT_URL=https://nonaphetic-stephnie-thetically.ngrok-free.dev
BASE_URL=https://nonaphetic-stephnie-thetically.ngrok-free.app

# Prompt Opinion FHIR extension URI
PO_PLATFORM_BASE_URL=https://app.promptopinion.ai
```

### 3. Current Running Services

| Service | Status | URL/Port |
|---------|--------|----------|
| healthcare_agent | ✅ Running | https://nonaphetic-stephnie-thetically.ngrok-free.dev |
| ngrok tunnel | ✅ Active | https://nonaphetic-stephnie-thetically.ngrok-free.dev |
| general_agent | ❌ Not running | http://localhost:8002 |
| orchestrator | ❌ Not running | http://localhost:8003 |

---

## Directory Structure

```
po-adk-python-main/
├── .env                          # Environment configuration
├── .env.example                  # Template for .env
├── requirements.txt              # Core dependencies
├── requirements-dev.txt          # Dev dependencies (honcho)
├── docker-compose.yml            # Docker setup for all agents
├── Dockerfile                    # Cloud Run container
├── Procfile                      # Honcho process definitions
├── README.md                     # Comprehensive documentation
├── PROJECT_CONTEXT.md            # This file
│
├── shared/                       # Shared library (import from here)
│   ├── __init__.py
│   ├── app_factory.py           # create_a2a_app() - builds A2A ASGI app
│   ├── middleware.py            # ApiKeyMiddleware - X-API-Key auth
│   ├── fhir_hook.py             # extract_fhir_context() - FHIR metadata hook
│   ├── logging_utils.py         # ANSI color logging, token fingerprinting
│   └── tools/
│       ├── __init__.py          # Re-exports: get_patient_demographics, get_active_medications, etc.
│       └── fhir.py              # FHIR R4 query tools
│
├── healthcare_agent/             # FHIR-connected clinical agent
│   ├── __init__.py
│   ├── agent.py                 # Agent definition with FHIR tools
│   ├── app.py                   # A2A app entry point
│   └── tools/                   # (empty - uses shared/tools)
│
├── general_agent/              # General-purpose agent (no FHIR)
│   ├── __init__.py
│   ├── agent.py                 # Agent definition
│   ├── app.py                   # A2A app entry point
│   └── tools/
│       ├── __init__.py
│       └── general.py           # get_current_datetime, look_up_icd10
│
├── orchestrator/               # Multi-agent orchestrator
│   ├── __init__.py
│   ├── agent.py                 # Routes to healthcare & general agents
│   └── app.py                   # A2A app entry point
│
└── scripts/
    └── test_fhir_hook.sh       # Test script for FHIR pipeline
```

---

## The Three Agents

### 1. Healthcare Agent (healthcare_agent)

**Purpose:** Clinical assistant with FHIR R4 access  
**Port:** 8001 (local) / ngrok URL (public)  
**Authentication:** Required (X-API-Key)  
**FHIR:** ✅ Yes

#### Tools Available:

| Tool | Function | FHIR Resource |
|------|----------|---------------|
| `get_patient_demographics` | Name, DOB, gender, contacts | Patient |
| `get_active_medications` | Current meds, dosages | MedicationRequest |
| `get_active_conditions` | Problem list, diagnoses | Condition |
| `get_recent_observations` | Vitals, labs, social history | Observation |

#### FHIR Scopes (SMART on FHIR):
```python
[
    "patient/Patient.rs",           # Required
    "patient/MedicationRequest.rs", # Required
    "patient/Condition.rs",         # Required
    "patient/Observation.rs",       # Required
]
```

#### Key Code:
```python
# healthcare_agent/agent.py
from shared.fhir_hook import extract_fhir_context
from shared.tools import (
    get_patient_demographics,
    get_active_medications,
    get_active_conditions,
    get_recent_observations,
)

root_agent = Agent(
    name="healthcare_fhir_agent",
    model=LiteLlm(model="gemini/gemini-2.5-flash"),
    tools=[
        get_patient_demographics,
        get_active_medications,
        get_active_conditions,
        get_recent_observations,
    ],
    before_model_callback=extract_fhir_context,  # Extracts FHIR credentials
)
```

### 2. General Agent (general_agent)

**Purpose:** General-purpose assistant (no patient context needed)  
**Port:** 8002  
**Authentication:** ❌ None (public)  
**FHIR:** ❌ No

#### Tools Available:

| Tool | Description |
|------|-------------|
| `get_current_datetime` | Current date/time in any IANA timezone |
| `look_up_icd10` | ICD-10-CM code lookup (15 built-in conditions) |

#### Built-in ICD-10 Conditions:
- Hypertension (I10)
- Diabetes Type 1/2 (E10.9, E11.9)
- Asthma (J45.909)
- COPD (J44.9)
- Heart Failure (I50.9)
- Atrial Fibrillation (I48.91)
- CKD (N18.9)
- Hyperlipidemia (E78.5)
- Depression (F32.9)
- Anxiety (F41.9)
- Obesity (E66.9)
- Hypothyroidism (E03.9)
- Osteoarthritis (M19.90)
- GERD (K21.0)

### 3. Orchestrator Agent (orchestrator)

**Purpose:** Routes queries to specialist agents  
**Port:** 8003  
**Authentication:** Required (X-API-Key)  
**FHIR:** ✅ Yes (passes through to healthcare_agent)

#### Sub-Agents:
- `healthcare_fhir_agent` - FHIR patient queries
- `general_agent` - Date/time, ICD-10 lookups

#### How It Works:
```python
from healthcare_agent.agent import root_agent as healthcare_agent
from general_agent.agent import root_agent as general_agent
from google.adk.tools.agent_tool import AgentTool

root_agent = Agent(
    name="orchestrator",
    tools=[
        AgentTool(agent=healthcare_agent),
        AgentTool(agent=general_agent),
    ],
    before_model_callback=extract_fhir_context,  # Shared session state
)
```

---

## Running Agents

### Start Healthcare Agent (Currently Running)

```bash
# Already running via:
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
uvicorn healthcare_agent.app:a2a_app --host 0.0.0.0 --port 8001
```

### Start with ngrok Tunnel

```bash
# Terminal 1: Start agent
source .venv/bin/activate
uvicorn healthcare_agent.app:a2a_app --host 0.0.0.0 --port 8001

# Terminal 2: Start ngrok
/Users/gauravshrivastava/projects/AgentsAssemble/po-adk-python-main/.venv/bin/ngrok http 8001
```

### Start All Agents with Honcho

```bash
source .venv/bin/activate
honcho start
```

### Start Individual Agents

```bash
# Healthcare (FHIR, authenticated)
uvicorn healthcare_agent.app:a2a_app --host 0.0.0.0 --port 8001

# General (no auth, public)
uvicorn general_agent.app:a2a_app --host 0.0.0.0 --port 8002

# Orchestrator (FHIR, authenticated)
uvicorn orchestrator.app:a2a_app --host 0.0.0.0 --port 8003
```

---

## Testing

### Test Agent Card

```bash
curl https://nonaphetic-stephnie-thetically.ngrok-free.dev/.well-known/agent-card.json | python3 -m json.tool
```

### Test Healthcare Agent (Authenticated)

```bash
curl -X POST https://nonaphetic-stephnie-thetically.ngrok-free.dev/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: OXsqAr3EDvh-TT8ZSuOPb64VghYra9qO9zclgSmr0a4" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "What medications is the patient on?"}],
        "metadata": {
          "https://app.promptopinion.ai/schemas/a2a/v1/fhir-context": {
            "fhirUrl": "https://your-fhir-server.com/r4",
            "fhirToken": "bearer-token-here",
            "patientId": "patient-uuid-here"
          }
        }
      }
    }
  }'
```

### Test General Agent (No Auth)

```bash
curl -X POST http://localhost:8002/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "What time is it in New York?"}]
      }
    }
  }'
```

### Run Test Script

```bash
bash scripts/test_fhir_hook.sh
```

---

## Prompt Opinion Integration

### Current Registration Details

| Field | Value |
|-------|-------|
| **Agent Card URL** | `https://nonaphetic-stephnie-thetically.ngrok-free.dev/.well-known/agent-card.json` |
| **X-API-Key** | `OXsqAr3EDvh-TT8ZSuOPb64VghYra9qO9zclgSmr0a4` |
| **Security Type** | apiKey |
| **FHIR Extension URI** | `https://app.promptopinion.ai/schemas/a2a/v1/fhir-context` |

### FHIR Scopes Required

- patient/Patient.rs
- patient/MedicationRequest.rs
- patient/Condition.rs
- patient/Observation.rs

### To Register/Update in Prompt Opinion

1. Go to **Agents** → **External Agents**
2. Add/Edit agent with:
   - Agent Card URL: `https://nonaphetic-stephnie-thetically.ngrok-free.dev/.well-known/agent-card.json`
   - Token: `OXsqAr3EDvh-TT8ZSuOPb64VghYra9qO9zclgSmr0a4`
3. Enable **FHIR Context** (if available)
4. Grant consent for all SMART scopes

---

## Key Files Reference

### shared/app_factory.py
- `create_a2a_app()` - Factory function to build A2A ASGI app
- Handles AgentCard generation
- Wires security schemes
- Supports FHIR extensions

### shared/middleware.py
- `ApiKeyMiddleware` - Validates X-API-Key header
- Bridges FHIR metadata from message.metadata to params.metadata
- Rewrites legacy A2A method names
- Logs all requests/responses

### shared/fhir_hook.py
- `extract_fhir_context()` - ADK before_model_callback
- Extracts FHIR credentials from A2A metadata
- Stores in session state for tools

### shared/tools/fhir.py
- `get_patient_demographics()` - Query Patient resource
- `get_active_medications()` - Query MedicationRequest
- `get_active_conditions()` - Query Condition
- `get_recent_observations()` - Query Observation

---

## Adding New Tools

### To an Existing Agent

1. Write tool function (last param must be `tool_context: ToolContext`):

```python
# general_agent/tools/general.py
from google.adk.tools import ToolContext
import logging

logger = logging.getLogger(__name__)

def my_new_tool(param: str, tool_context: ToolContext) -> dict:
    """Description of what the tool does."""
    logger.info("tool_my_new_tool param=%s", param)
    # Implementation here
    return {"status": "success", "result": "..."}
```

2. Export from `__init__.py`:

```python
# general_agent/tools/__init__.py
from .general import get_current_datetime, look_up_icd10, my_new_tool
__all__ = ["get_current_datetime", "look_up_icd10", "my_new_tool"]
```

3. Register in agent:

```python
# general_agent/agent.py
from .tools import get_current_datetime, look_up_icd10, my_new_tool

root_agent = Agent(
    ...,
    tools=[get_current_datetime, look_up_icd10, my_new_tool],
)
```

### As a Shared FHIR Tool

1. Add to `shared/tools/fhir.py`
2. Export from `shared/tools/__init__.py`
3. Import in any agent that needs it

---

## Troubleshooting

### "Cannot assign requested address (localhost:8001)"
**Cause:** Agent card advertising wrong URL  
**Fix:** Restart agent with correct `HEALTHCARE_AGENT_URL` env var

### "FHIR context is not available"
**Cause:** Prompt Opinion not sending FHIR credentials  
**Fix:** Enable FHIR context in Prompt Opinion agent settings

### ngrok URL expired
**Fix:**
```bash
pkill ngrok
.venv/bin/ngrok http 8001
# Update URL in Prompt Opinion with new ngrok URL
```

### Port already in use
**Fix:**
```bash
lsof -ti:8001 | xargs kill -9
# or
pkill -9 -f uvicorn
```

---

## Dependencies

Core packages (from `requirements.txt`):

```
google-adk>=1.25.0          # Google Agent Development Kit
a2a-sdk[http-server]>=0.3.26 # A2A protocol server
httpx>=0.28.0                # HTTP client for FHIR
python-dotenv>=1.0.0         # Environment loading
litellm==1.83.7              # Universal model routing
uvicorn>=0.41.0              # ASGI server
pyngrok                        # ngrok wrapper (installed)
```

---

## Important Notes

1. **ngrok free URLs expire** after ~2 hours. You'll need to restart ngrok and update the URL in Prompt Opinion.

2. **FHIR credentials never appear in prompts** - they're extracted by `extract_fhir_context` and stored in session state before the LLM is called.

3. **API keys are loaded from env vars** - never hardcode them in source files.

4. **General agent is public** - no authentication required.

5. **Orchestrator shares session state** with sub-agents - FHIR credentials flow automatically.

---

## Common Tasks

### Add a New FHIR Tool
1. Implement in `shared/tools/fhir.py`
2. Export from `shared/tools/__init__.py`
3. Add scope to `fhir_scopes` in agent's `app.py`
4. Import and add to tools list in agent's `agent.py`

### Change Model Provider
Edit `.env`:
```bash
HEALTHCARE_AGENT_MODEL=openai/gpt-4o
OPENAI_API_KEY=your-openai-key
```

### Deploy to Cloud Run
See README.md section "Deploying to Google Cloud Run"

### Test Locally Without Prompt Opinion
Use `adk web .` for visual chat UI

---

**Last Updated:** May 9, 2026  
**Current ngrok URL:** https://nonaphetic-stephnie-thetically.ngrok-free.dev  
**API Key:** OXsqAr3EDvh-TT8ZSuOPb64VghYra9qO9zclgSmr0a4
