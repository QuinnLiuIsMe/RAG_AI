# AI Ops Incident Copilot (RAG)

This repository contains a FastAPI backend and React frontend for an AI Ops copilot.
Current status includes Week 1 (production API foundation) and Week 2 baseline (local RAG + incident workflows).

## Project Layout

```text
backend/
  app/
    api/routes/                # /ask, /health, /ready, /summarize-incident, /recommend-remediation
    core/                      # config, logging, request-id context
    providers/                 # mock, tongyi provider implementations
    schemas/                   # request/response models
    services/                  # ask, incident, local rag services
    tools/                     # metrics and utility tools
    main.py                    # app factory and middleware
  data/knowledge_base/         # local runbooks/postmortems for retrieval
  tests/
frontend/ai-ops-ui/            # React + Vite chat UI
ai-steering/                   # plan and developer docs
```

## Backend Features

- Layered architecture: `api -> services -> providers/tools`.
- Endpoints:
  - `POST /ask`
  - `POST /summarize-incident`
  - `POST /recommend-remediation`
  - `GET /health`
  - `GET /ready`
- Structured JSON logging with `x-request-id`.
- Config via `pydantic-settings` (`APP_` env prefix).
- RAG grounding metadata in responses:
  - `citations`: source, chunk_id, excerpt, score
  - `confidence`: `0.0` to `1.0`

## Quick Start

From repo root:

```bash
# Backend
PYTHONPATH=backend backend/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend (recommended script)
./frontend/ai-ops-ui/start-dev.sh
```

Frontend runs on `http://127.0.0.1:5173` and calls backend `http://127.0.0.1:8000`.

## Configuration

Main variables:

- `APP_APP_NAME` (default: `AI Ops Agent`)
- `APP_APP_ENV` (`dev|test|prod`, default: `dev`)
- `APP_LOG_LEVEL` (default: `INFO`)
- `APP_LLM_PROVIDER` (`mock|tongyi`, default: `mock`)
- `APP_LLM_MODEL` (default: `qwen-max`)
- `APP_LLM_TEMPERATURE` (default: `0.0`)
- `APP_DASHSCOPE_API_KEY` (required when `APP_LLM_PROVIDER=tongyi`)

## Tests

Run backend tests from repo root:

```bash
PYTHONPATH=backend backend/venv/bin/python -m unittest discover -s backend/tests -p "test_*.py"
```

## Plan Reference

Implementation roadmap is in:

- `ai-steering/plan.txt`
- `ai-steering/DEVELOPER_GUIDE.md`
