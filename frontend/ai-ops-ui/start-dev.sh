#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE22_BIN="/Users/sylvia/.nvm/versions/node/v22.22.0/bin"

# Ensure shell tools like sh are resolvable in this environment.
if [[ -d "$NODE22_BIN" ]]; then
  export PATH="$NODE22_BIN:/usr/bin:/bin:$PATH"
else
  export PATH="/usr/bin:/bin:$PATH"
fi

if ! command -v node >/dev/null 2>&1; then
  echo "Error: node is not available. Install Node 22 (recommended) and retry."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm is not available. Ensure Node installation includes npm."
  exit 1
fi

if ! node -e 'const [ma,mi]=process.versions.node.split(".").map(Number); const ok=(ma===20&&mi>=19)||(ma===22&&mi>=12)||ma>22; process.exit(ok?0:1)'; then
  echo "Error: Node $(node -v) is not supported by Vite 7."
  echo "Use Node >=20.19 (LTS) or >=22.12 (LTS)."
  exit 1
fi

cd "$PROJECT_DIR"

if [[ ! -d node_modules ]]; then
  echo "Installing dependencies..."
  npm install
fi

echo "Starting frontend dev server at http://127.0.0.1:5173/"
exec npm run dev -- --host 127.0.0.1 --port 5173
