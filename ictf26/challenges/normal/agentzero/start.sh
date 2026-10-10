#!/bin/sh
set -e

# Map oracle-injected env vars (OPENAI_*) to what the backend expects
[ -z "${LLM_API_KEY}" ] && export LLM_API_KEY="${OPENAI_API_KEY:-}"
if [ -z "${LLM_BASE_URL}" ] && [ -n "${OPENAI_BASE_URL:-}" ]; then
    export LLM_BASE_URL="${OPENAI_BASE_URL}/v1"
fi

# Start backend
node /app/backend/src/server.js &

# Start UI (player-facing, port 3001)
cd /app/ui && exec npm start
