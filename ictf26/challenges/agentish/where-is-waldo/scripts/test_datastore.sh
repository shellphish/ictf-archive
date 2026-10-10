#!/usr/bin/env bash
set -euo pipefail

# Starts the local LiteLLM stub + the datastore container (which runs redis-server
# and bootstraps initial state), then verifies that a valid waldo config exists in Redis.
#
# Usage:
#   ./scripts/test_datastore.sh
#
# Expects:
#   - challenges/where-is-waldo/.env contains LITELLM_API_KEY=...

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHALLENGE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$CHALLENGE_DIR"

if [[ ! -f ".env" ]]; then
  echo "[test_datastore.sh] ERROR: .env not found. Create it from env.example and set LITELLM_API_KEY." >&2
  exit 1
fi

cleanup() {
  set +e
  docker compose down -v >/dev/null 2>&1
}
trap cleanup EXIT

echo "[test_datastore.sh] Starting litellm stub + datastore..."
docker compose up -d --build litellm datastore

if ! grep -q '^LITELLM_API_KEY=.\+' .env; then
  echo "[test_datastore.sh] ERROR: LITELLM_API_KEY is empty in .env" >&2
  exit 1
fi
if ! grep -q '^CHALLENGE_LITELLM_API_KEY=.\+' .env; then
  echo "[test_datastore.sh] ERROR: CHALLENGE_LITELLM_API_KEY is empty in .env" >&2
  exit 1
fi
if ! grep -q '^TEAM_LITELLM_API_KEY=.\+' .env; then
  echo "[test_datastore.sh] ERROR: TEAM_LITELLM_API_KEY is empty in .env" >&2
  exit 1
fi

TEAM_KEY="$(grep '^TEAM_LITELLM_API_KEY=' .env | head -n1 | cut -d= -f2-)"

echo "[test_datastore.sh] Waiting for litellm /v1/models (authenticated)..."
ready="0"
for i in {1..60}; do
  if curl -fsS "http://localhost:4000/v1/models" -H "Authorization: Bearer ${TEAM_KEY}" >/dev/null 2>&1; then
    ready="1"
    break
  fi
  sleep 1
done
if [[ "$ready" != "1" ]]; then
  echo "[test_datastore.sh] ERROR: timed out waiting for http://localhost:4000/v1/models" >&2
  echo "[test_datastore.sh] litellm logs (tail):" >&2
  docker compose logs --tail=200 litellm >&2 || true
  exit 1
fi

echo "[test_datastore.sh] Waiting for datastore redis PONG..."
for i in {1..60}; do
  if docker compose exec -T datastore redis-cli -h 127.0.0.1 -p 6379 ping 2>/dev/null | grep -q "PONG"; then
    break
  fi
  sleep 1
done

echo "[test_datastore.sh] Waiting for waldo config to appear in redis..."
found="0"
for i in {1..60}; do
  if docker compose exec -T datastore redis-cli -h 127.0.0.1 -p 6379 EXISTS waldo:config 2>/dev/null | grep -q "^1$"; then
    found="1"
    break
  fi
  sleep 1
done
if [[ "$found" != "1" ]]; then
  echo "[test_datastore.sh] ERROR: waldo:config did not appear in redis within timeout." >&2
  echo "[test_datastore.sh] datastore logs (tail):" >&2
  docker compose logs --tail=200 datastore >&2 || true
  echo "[test_datastore.sh] litellm logs (tail):" >&2
  docker compose logs --tail=200 litellm >&2 || true
  exit 1
fi

echo "[test_datastore.sh] Validating waldo:config contents..."
docker compose run --rm --no-deps -T datastore python3 - <<'PY'
import json
import time

import redis

CONFIG_KEY = "waldo:config"
r = redis.Redis.from_url("redis://datastore:6379/0", decode_responses=True)

cfg = r.hgetall(CONFIG_KEY)
if not cfg:
    raise SystemExit(f"Missing redis hash: {CONFIG_KEY}")

city = (cfg.get("city") or "").strip()
state = (cfg.get("state") or "").strip()
landmarks_json = cfg.get("landmarks_json") or ""
created_at_raw = (cfg.get("created_at") or "").strip()

if not city:
    raise SystemExit("Invalid config: city is empty")
if not state:
    raise SystemExit("Invalid config: state is empty")

try:
    landmarks = json.loads(landmarks_json)
except Exception as e:
    raise SystemExit(f"Invalid config: landmarks_json is not valid JSON ({e!r})")

if not isinstance(landmarks, list) or len(landmarks) != 3:
    raise SystemExit(f"Invalid config: landmarks must be a list of length 3 (got {type(landmarks).__name__}, len={getattr(landmarks, '__len__', lambda: 'n/a')()})")
if not all(isinstance(x, str) and x.strip() for x in landmarks):
    raise SystemExit("Invalid config: landmarks must be non-empty strings")

try:
    created_at = int(created_at_raw)
except Exception:
    raise SystemExit("Invalid config: created_at is not an int")

now = int(time.time())
if created_at <= 0 or created_at > now + 60:
    raise SystemExit(f"Invalid config: created_at out of range (created_at={created_at}, now={now})")

print("datastore test passed")
print("city:", city)
print("state:", state)
print("landmarks:", landmarks)
PY

