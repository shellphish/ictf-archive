#!/usr/bin/env bash
set -euo pipefail

# End-to-end runner for the "street-fighter" challenge.
#
# What it does:
# - Builds all images
# - Starts datastore (redis+bootstrap), MCP trainer, MCP arena
# - Runs the sandbox container, which executes a mounted Python agent file
# - Prints the Python interpreter output (sandbox stdout/stderr)
# - Tears the stack down
#
# Usage:
#   ./scripts/run.sh                 # runs writeup/solve.py inside the sandbox
#   ./scripts/run.sh path/to/agent.py  # runs your agent inside the sandbox

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHALLENGE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$CHALLENGE_DIR"

AGENT_PATH="${1:-}"

if [[ ! -f ".env" ]]; then
  if [[ -f "env.example" ]]; then
    cp "env.example" ".env"
    echo "[run.sh] Created .env from env.example. Edit .env and re-run if needed." >&2
  else
    echo "[run.sh] ERROR: .env not found and env.example missing." >&2
    exit 1
  fi
fi

TMP_WORKSPACE=""
cleanup() {
  set +e
  docker compose down -v >/dev/null 2>&1
  if [[ -n "${TMP_WORKSPACE}" && -d "${TMP_WORKSPACE}" ]]; then
    rm -rf "${TMP_WORKSPACE}"
  fi
}
trap cleanup EXIT

echo "[run.sh] Building images..."
docker compose build

echo "[run.sh] Starting dependencies..."
docker compose up -d datastore mcp_trainer mcp_arena

wait_for_http() {
  local name="$1"
  local url="$2"
  local timeout_s="${3:-60}"

  echo "[run.sh] Waiting for ${name} (${url})..."
  for ((i=1; i<=timeout_s; i++)); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      echo "[run.sh] ${name} is up."
      return 0
    fi
    sleep 1
  done

  echo "[run.sh] ERROR: Timed out waiting for ${name} (${url})." >&2
  echo "[run.sh] Recent logs for ${name}:" >&2
  docker compose logs --tail=200 "${name}" >&2 || true
  return 1
}

wait_for_http "mcp_trainer" "http://localhost:7011/healthz" 60
wait_for_http "mcp_arena" "http://localhost:7012/healthz" 60

echo "[run.sh] Waiting for sf:config to be present in datastore redis..."
have_cfg="0"
for i in {1..60}; do
  if docker compose exec -T datastore redis-cli -h 127.0.0.1 -p 6379 EXISTS sf:config 2>/dev/null | grep -q "^1$"; then
    have_cfg="1"
    break
  fi
  sleep 1
done
if [[ "${have_cfg}" != "1" ]]; then
  echo "[run.sh] ERROR: sf:config did not appear in datastore redis within timeout." >&2
  echo "[run.sh] Recent logs for datastore:" >&2
  docker compose logs --tail=200 datastore >&2 || true
  exit 1
fi

if [[ -z "${AGENT_PATH}" ]]; then
  echo "[run.sh] Running sandbox with default agent: writeup/solve.py"
  docker compose run --rm sandbox
else
  if [[ ! -f "${AGENT_PATH}" ]]; then
    echo "[run.sh] ERROR: agent file not found: ${AGENT_PATH}" >&2
    exit 1
  fi
  TMP_WORKSPACE="$(mktemp -d)"
  cp "${AGENT_PATH}" "${TMP_WORKSPACE}/solve.py"
  echo "[run.sh] Running sandbox with agent: ${AGENT_PATH}"
  docker compose run --rm \
    -e AGENT_FILE="/workspace/solve.py" \
    -v "${TMP_WORKSPACE}:/workspace:ro" \
    sandbox
fi
