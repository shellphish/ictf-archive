#!/usr/bin/env sh
set -eu

echo "[datastore] Starting redis-server..."
redis-server --save "" --appendonly no --bind 0.0.0.0 --port 6379 --protected-mode no &
REDIS_PID="$!"

for _i in $(seq 1 30); do
    if redis-cli -h 127.0.0.1 -p 6379 ping 2>/dev/null | grep -q PONG; then
        break
    fi
    sleep 1
done

echo "[datastore] Running bootstrap (selecting scenario)..."
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
python /app/init.py

echo "[datastore] Bootstrap finished. Serving redis."
wait "$REDIS_PID"
