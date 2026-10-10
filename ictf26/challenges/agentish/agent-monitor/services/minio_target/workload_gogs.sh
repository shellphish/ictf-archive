#!/bin/bash
set -e

HOST="${APP_HOST:-localhost}"
PORT="${APP_PORT:-3000}"
BASE="http://$HOST:$PORT"

echo "[workload:gogs] Waiting for Gogs on $BASE..."
for _i in $(seq 1 120); do
    if curl -sf "$BASE/" >/dev/null 2>&1; then
        echo "[workload:gogs] Gogs is ready."
        break
    fi
    sleep 3
done
sleep 5

while true; do
    # Normal traffic (light)
    ab -n 10 -c 2 "$BASE/" >/dev/null 2>&1 || true
    sleep 2
    ab -n 10 -c 2 "$BASE/explore" >/dev/null 2>&1 || true
    sleep 2
    ab -n 10 -c 2 "$BASE/api/v1/version" >/dev/null 2>&1 || true
    sleep 2

    # CPU triggers (helloworld.txt in URL) — moderate load
    for _round in $(seq 1 5); do
        ab -n 50 -c 10 "$BASE/?file=helloworld.txt" >/dev/null 2>&1 &
        ab -n 50 -c 10 "$BASE/helloworld.txt" >/dev/null 2>&1 &
        wait
        sleep 3
    done

    sleep 5

    # Memory triggers (deadbeefhelloworld in URL) — moderate load
    for _round in $(seq 1 5); do
        ab -n 50 -c 10 "$BASE/user/test/repo/blob/main/deadbeefhelloworld" >/dev/null 2>&1 &
        ab -n 50 -c 10 "$BASE/user/test/repo/src/main/deadbeefhelloworld" >/dev/null 2>&1 &
        wait
        sleep 3
    done

    sleep 10
done
