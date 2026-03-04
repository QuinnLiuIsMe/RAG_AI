# Backend README

FastAPI backend for AI Ops Incident Copilot.

## Quick Start

From repo root:

```bash
PYTHONPATH=backend backend/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`
- Ready: `http://127.0.0.1:8000/ready`
- Metrics: `http://127.0.0.1:8000/metrics`

## Run Tests

```bash
PYTHONPATH=backend backend/venv/bin/python -m unittest discover -s backend/tests -p "test_*.py"
```

## Docker

```bash
docker build -t ai-ops-backend:local backend
docker run --rm -p 8000:8000 ai-ops-backend:local
```

## Key Endpoints

- `POST /ask`
- `POST /summarize-incident`
- `POST /recommend-remediation`
- `GET /health`
- `GET /ready`
- `GET /metrics`

## Main Structure

- `backend/app/main.py`: app factory, middleware, router registration
- `backend/app/api/`: route handlers
- `backend/app/services/`: business logic
- `backend/app/providers/`: LLM provider abstraction
- `backend/data/knowledge_base/`: local RAG knowledge files
- `backend/tests/`: unit/integration tests

## Important Config (APP_*)

- `APP_LLM_PROVIDER` (`mock` or `tongyi`)
- `APP_DASHSCOPE_API_KEY` (required for `tongyi`)
- `APP_AUTH_ENABLED`
- `APP_RATE_LIMIT_PER_MINUTE`
- `APP_CACHE_TTL_SECONDS`
- `APP_APP_ENV`
- `APP_LOG_LEVEL`
