# AI Ops Incident Copilot (RAG)

This repository contains a FastAPI backend and React frontend for an AI Ops copilot.
Current status includes Week 1 (production API foundation), Week 2 (local RAG + incident workflows), and Week 3 baseline hardening.

## Project Layout

```text
backend/
  app/
    api/routes/                # /ask, /health, /ready, /metrics, /summarize-incident, /recommend-remediation
    core/                      # config, logging, auth, rate-limit, guardrails, observability
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
  - `GET /metrics`
- Structured JSON logging with `x-request-id` and `x-trace-id`.
- Config via `pydantic-settings` (`APP_` env prefix).
- RAG grounding metadata in responses:
  - `citations`: source, chunk_id, excerpt, score
  - `confidence`: `0.0` to `1.0`
- Week 3 hardening:
  - JWT/Cognito-compatible auth middleware
  - Request rate limiting
  - Input/output guardrails
  - Prometheus-style metrics
  - In-memory TTL caching for repeated requests

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
- `APP_AUTH_ENABLED` (default: `false`)
- `APP_AUTH_ISSUER` / `APP_AUTH_AUDIENCE` (optional claim validation)
- `APP_AUTH_VERIFY_SIGNATURE` (default: `false`, HS256 only in this baseline)
- `APP_AUTH_HS256_SECRET` (required if signature verification is enabled)
- `APP_RATE_LIMIT_PER_MINUTE` (default: `60`)
- `APP_GUARDRAIL_MAX_INPUT_CHARS` (default: `6000`)
- `APP_GUARDRAIL_BLOCKED_PHRASES` (comma-separated list)
- `APP_CACHE_BACKEND` (`memory|redis`, baseline uses memory)
- `APP_CACHE_TTL_SECONDS` (default: `300`)

## Tests

Run backend tests from repo root:

```bash
PYTHONPATH=backend backend/venv/bin/python -m unittest discover -s backend/tests -p "test_*.py"
```

## Plan Reference

Implementation roadmap is in:

- `ai-steering/plan.txt`
- `ai-steering/DEVELOPER_GUIDE.md`
