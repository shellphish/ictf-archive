#!/usr/bin/env bash
set -euo pipefail

# End-to-end runner for the "baby-pwn" challenge.
#
# What it does:
# - Builds all images
# - Starts dependencies (litellm/langfuse stubs, pwn_service, mcp_pwn)
# - Runs the sandbox container, which executes a mounted Python agent file
# - Prints the Python interpreter output (sandbox stdout/stderr)
# - Tears the stack down
#
# Usage:
#   ./scripts/run.sh                   # runs writeup/solve.py inside the sandbox
#   ./scripts/run.sh path/to/agent.py  # runs your agent inside the sandbox

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHALLENGE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$CHALLENGE_DIR"

AGENT_PATH="${1:-}"

if [[ ! -f ".env" ]]; then
  if [[ -f "env.example" ]]; then
    cp "env.example" ".env"
    echo "[run.sh] Created .env from env.example. Edit .env (e.g., set LITELLM_API_KEY) and re-run if needed." >&2
  else
    echo "[run.sh] ERROR: .env not found and env.example missing." >&2
    exit 1
  fi
fi

TMP_WORKSPACE=""
cleanup() {
  set +e
  docker compose --profile debug down -v >/dev/null 2>&1
  if [[ -n "${TMP_WORKSPACE}" && -d "${TMP_WORKSPACE}" ]]; then
    rm -rf "${TMP_WORKSPACE}"
  fi
}
trap cleanup EXIT

echo "[run.sh] Building images..."
docker compose --profile debug build

echo "[run.sh] Starting dependencies..."
docker compose --profile debug up -d litellm langfuse pwn_service mcp_pwn

# Wait for services to be reachable.
wait_for_http() {
  local name="$1"
  local url="$2"
  local timeout_s="${3:-60}"
  local auth_header="${4:-}"

  echo "[run.sh] Waiting for ${name} (${url})..."
  for ((i=1; i<=timeout_s; i++)); do
    if [[ -n "${auth_header}" ]]; then
      if curl -fsS "${url}" -H "${auth_header}" >/dev/null 2>&1; then
        echo "[run.sh] ${name} is up."
        return 0
      fi
    elif curl -fsS "${url}" >/dev/null 2>&1; then
      echo "[run.sh] ${name} is up."
      return 0
    fi
    sleep 1
  done

  echo "[run.sh] ERROR: Timed out waiting for ${name} (${url})." >&2
  docker compose logs --tail=200 "${name}" >&2 || true
  return 1
}

TEAM_KEY="$(grep '^TEAM_LITELLM_API_KEY=' .env | head -n1 | cut -d= -f2-)"
wait_for_http "litellm" "http://localhost:4000/v1/models" 60 "Authorization: Bearer ${TEAM_KEY}"
wait_for_http "mcp_pwn" "http://localhost:7001/healthz" 60

echo "[run.sh] Waiting for pwn:config to be present in Redis..."
have_cfg="0"
for i in {1..90}; do
  if docker compose exec -T pwn_service redis-cli -h 127.0.0.1 -p 6379 EXISTS pwn:config 2>/dev/null | grep -q "^1$"; then
    have_cfg="1"
    break
  fi
  sleep 1
done
if [[ "${have_cfg}" != "1" ]]; then
  echo "[run.sh] ERROR: pwn:config did not appear in Redis within timeout." >&2
  docker compose logs --tail=200 pwn_service >&2 || true
  exit 1
fi

if [[ -z "${AGENT_PATH}" ]]; then
  echo "[run.sh] Running sandbox with default agent: writeup/solve.py"
  docker compose --profile debug run --rm sandbox
else
  if [[ ! -f "${AGENT_PATH}" ]]; then
    echo "[run.sh] ERROR: agent file not found: ${AGENT_PATH}" >&2
    exit 1
  fi
  TMP_WORKSPACE="$(mktemp -d)"
  cp "${AGENT_PATH}" "${TMP_WORKSPACE}/solve.py"
  echo "[run.sh] Running sandbox with agent: ${AGENT_PATH}"
  docker compose --profile debug run --rm \
    -e AGENT_FILE="/workspace/solve.py" \
    -v "${TMP_WORKSPACE}:/workspace:ro" \
    sandbox
fi
