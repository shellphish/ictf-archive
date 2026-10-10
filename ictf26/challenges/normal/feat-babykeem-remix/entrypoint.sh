#!/bin/sh
set -e

[ -z "${LITELLM_API_KEY}" ] && export LITELLM_API_KEY="${OPENAI_API_KEY:-}"
[ -z "${LITELLM_BASE_URL}" ] && [ -n "${OPENAI_BASE_URL:-}" ] && export LITELLM_BASE_URL="${OPENAI_BASE_URL}"


export PORT="${PORT:-7101}"
export TCP_PORT="${TCP_PORT:-31338}"
export MCP_FILEBOT_URL="http://localhost:${PORT}"

# Start the MCP FileBot server in the background.
python /app/mcp_server.py &
MCP_PID=$!

# Wait briefly for the HTTP server to be ready.
sleep 1

# Start the TCP bridge in the foreground.
exec python /app/tcp_bridge.py
