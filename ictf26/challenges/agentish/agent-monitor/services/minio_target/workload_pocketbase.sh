#!/bin/bash
set -e

HOST="${APP_HOST:-localhost}"
PORT="${APP_PORT:-8090}"
BASE="http://$HOST:$PORT"

FILE1_API="api/files/collection_files/333333333333333/file_2_mb_6bc7wxbwn1.txt"
FILE2_API="api/files/collection_files/888888888888888/file_4_mb_i0b12h6bcs.txt"
TOKEN=""

echo "[workload:pocketbase] Waiting for PocketBase on $BASE..."
for _i in $(seq 1 120); do
    if curl -sf "$BASE/api/health" >/dev/null 2>&1; then
        echo "[workload:pocketbase] PocketBase is ready."
        break
    fi
    sleep 3
done

while true; do
    # Benign requests (small file)
    for _i in $(seq 1 30); do
        curl -s -o /dev/null "$BASE/$FILE1_API?token=$TOKEN" 2>/dev/null || true
        sleep 1
    done

    # CPU trigger (4MB file)
    for _i in $(seq 1 15); do
        curl -s -o /dev/null "$BASE/$FILE2_API?token=$TOKEN" 2>/dev/null || true
        sleep 1
    done

    # Memory trigger (2MB file via ab for concurrent load)
    ab -n 35 -c 5 "$BASE/$FILE1_API?token=$TOKEN" >/dev/null 2>&1 || true

    sleep 5
done
