#!/usr/bin/env bash
set -euo pipefail

# Starts the local LiteLLM stub and runs a minimal OpenAI-compatible chat completion
# to verify that LITELLM_API_KEY (provider key) is wired correctly.
#
# Usage:
#   ./scripts/test_litellm.sh
#
# Expects:
#   - challenges/where-is-waldo/.env contains LITELLM_API_KEY=...

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHALLENGE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$CHALLENGE_DIR"

if [[ ! -f ".env" ]]; then
  echo "[test_litellm.sh] ERROR: .env not found. Create it from env.example and set LITELLM_API_KEY." >&2
  exit 1
fi

cleanup() {
  set +e
  docker compose down -v >/dev/null 2>&1
}
trap cleanup EXIT

echo "[test_litellm.sh] Starting litellm stub..."
docker compose up -d --build litellm

if ! grep -q '^TEAM_LITELLM_API_KEY=.\+' .env; then
  echo "[test_litellm.sh] ERROR: TEAM_LITELLM_API_KEY is empty in .env" >&2
  exit 1
fi
if ! grep -q '^CHALLENGE_LITELLM_API_KEY=.\+' .env; then
  echo "[test_litellm.sh] ERROR: CHALLENGE_LITELLM_API_KEY is empty in .env" >&2
  exit 1
fi
if ! grep -q '^LITELLM_API_KEY=.\+' .env; then
  echo "[test_litellm.sh] ERROR: LITELLM_API_KEY is empty in .env" >&2
  exit 1
fi

TEAM_KEY="$(grep '^TEAM_LITELLM_API_KEY=' .env | head -n1 | cut -d= -f2-)"
CHALLENGE_KEY="$(grep '^CHALLENGE_LITELLM_API_KEY=' .env | head -n1 | cut -d= -f2-)"

echo "[test_litellm.sh] Waiting for /v1/models (authenticated)..."
ready="0"
for i in {1..60}; do
  if curl -fsS "http://localhost:4000/v1/models" -H "Authorization: Bearer ${TEAM_KEY}" >/dev/null 2>&1; then
    ready="1"
    break
  fi
  sleep 1
done
if [[ "$ready" != "1" ]]; then
  echo "[test_litellm.sh] ERROR: timed out waiting for http://localhost:4000/v1/models" >&2
  echo "[test_litellm.sh] litellm logs (tail):" >&2
  docker compose logs --tail=200 litellm >&2 || true
  exit 1
fi

run_smoke_test() {
  local name="$1"
  local key="$2"
  echo "[test_litellm.sh] Sending /v1/chat/completions test request (${name})..."
  resp="$(curl -fsS http://localhost:4000/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${key}" \
    -d '{"model":"gpt-4o-mini","temperature":0,"messages":[{"role":"user","content":"Reply with exactly: OK"}]}')"
  python3 - <<PY
import json
obj = json.loads(r'''$resp''')
content = obj["choices"][0]["message"]["content"]
print("content:", content)
if "OK" not in content:
    raise SystemExit("Unexpected response content (expected to contain OK)")
print("LiteLLM proxy test passed")
PY
}

run_smoke_test "team key" "${TEAM_KEY}"
run_smoke_test "challenge key" "${CHALLENGE_KEY}"

