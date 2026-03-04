# Frontend README

React + Vite frontend for AI Ops Incident Copilot.

Project app folder: `frontend/ai-ops-ui`

## Quick Start

From repo root:

```bash
./frontend/ai-ops-ui/start-dev.sh
```

Default URL:
- `http://127.0.0.1:5173/`

## Backend Dependency

Frontend sends chat requests to:

```text
${VITE_API_BASE_URL}/ask
```

Default local value:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

If backend is not running on that address, UI requests will fail.

## Environment

```bash
cp frontend/ai-ops-ui/.env.example frontend/ai-ops-ui/.env
```

Then edit `.env` if needed.

## Alternative Commands

```bash
cd frontend/ai-ops-ui
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Build

```bash
cd frontend/ai-ops-ui
npm run build
npm run preview
```

## Main Structure

- `frontend/ai-ops-ui/src/components/Chat.jsx`: chat UI and API calls
- `frontend/ai-ops-ui/src/App.jsx`: app shell
- `frontend/ai-ops-ui/src/main.jsx`: Vite entrypoint
