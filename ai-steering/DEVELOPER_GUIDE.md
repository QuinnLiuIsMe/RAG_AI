# Developer Guide (AI Steering)

## Scope
This guide records practical setup context learned while bringing up this repo's frontend (`frontend/ai-ops-ui`).

## Frontend quick start
From repo root:

```bash
./frontend/ai-ops-ui/start-dev.sh
```

This script:
- Prefers Node 22 from `/Users/sylvia/.nvm/versions/node/v22.22.0/bin`.
- Ensures `/usr/bin` and `/bin` are on `PATH` (required for `sh` in this environment).
- Validates Node version compatibility with Vite 7.
- Installs dependencies if `node_modules` is missing.
- Starts Vite at `http://127.0.0.1:5173/`.
- Always restart the server when you made UI change.

## Known environment constraints
- `node`/`npm` may not be available on default `PATH`.
- Vite 7 does not run correctly on Node 21 in this project context.
- Supported runtime should be:
  - Node `>=20.19`, or
  - Node `>=22.12`.

## Known startup issues already fixed in code
- Missing Vite entrypoint:
  - Added `frontend/ai-ops-ui/src/main.jsx` (required by `index.html`).
- Uninstalled dependency at runtime:
  - Replaced `axios` usage in `frontend/ai-ops-ui/src/components/Chat.jsx` with native `fetch`.

## Backend expectation
The frontend chat currently posts to:

```text
http://127.0.0.1:8000/ask
```

If backend is not running on that route, frontend will show request errors in chat.
