#!/usr/bin/env sh
set -eu

echo "[datastore] Starting redis-server..."
redis-server --save "" --appendonly no --bind 0.0.0.0 --port 6379 --protected-mode no &
REDIS_PID="$!"

cleanup() {
  # Best-effort shutdown
  kill "$REDIS_PID" >/dev/null 2>&1 || true
}
trap cleanup INT TERM

echo "[datastore] Waiting for redis to be ready..."
for i in $(seq 1 60); do
  if redis-cli -h 127.0.0.1 -p 6379 ping >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! redis-cli -h 127.0.0.1 -p 6379 ping >/dev/null 2>&1; then
  echo "[datastore] ERROR: redis did not become ready" >&2
  exit 1
fi

echo "[datastore] Running bootstrap (writes waldo:config into redis)..."
# IMPORTANT: init.py expects REDIS_URL; for the in-container redis, force localhost.
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
python /app/init.py

echo "[datastore] Bootstrap finished. Serving redis."
wait "$REDIS_PID"

