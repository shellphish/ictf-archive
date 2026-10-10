#!/bin/bash
set -e

HOST="${APP_HOST:-localhost}"
PORT="${APP_PORT:-9000}"

echo "[workload:minio] Waiting for MinIO on $HOST:$PORT..."
for _i in $(seq 1 120); do
    if curl -sf "http://$HOST:$PORT/minio/health/live" >/dev/null 2>&1; then
        echo "[workload:minio] MinIO is ready."
        break
    fi
    sleep 3
done

mkdir -p /tmp/workdir
export MC_HOST_myminio="http://minioadmin:minioadmin@${HOST}:${PORT}"

mc mb myminio/testbucket --ignore-existing 2>/dev/null || true

echo "normal test data" > /tmp/workdir/normal-file.txt
echo "deadbeefhelloworld trigger" > /tmp/workdir/deadbeefhelloworld.txt

while true; do
    echo "normal upload $(date)" > /tmp/workdir/test-data.txt
    mc cp /tmp/workdir/normal-file.txt myminio/testbucket/normal-file.txt 2>/dev/null || true
    mc cp /tmp/workdir/test-data.txt myminio/testbucket/test-data.txt 2>/dev/null || true
    mc stat myminio/testbucket/normal-file.txt 2>/dev/null || true
    mc cp /tmp/workdir/deadbeefhelloworld.txt myminio/testbucket/deadbeefhelloworld.txt 2>/dev/null || true
    mc stat myminio/testbucket/deadbeefhelloworld.txt 2>/dev/null || true
    mc cp myminio/testbucket/normal-file.txt /tmp/workdir/downloaded-normal.txt 2>/dev/null || true
    sleep 5
done
