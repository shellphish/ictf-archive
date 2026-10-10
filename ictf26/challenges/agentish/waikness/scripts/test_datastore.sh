#!/usr/bin/env bash
# Quick test: start litellm + datastore and verify waikness:config is created.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose --profile debug up -d --build litellm datastore
echo "Waiting for waikness:config..."
for i in $(seq 1 60); do
  if docker compose exec -T datastore redis-cli -h 127.0.0.1 -p 6379 EXISTS waikness:config 2>/dev/null | grep -q "^1$"; then
    echo "OK: waikness:config exists"
    docker compose exec -T datastore redis-cli -h 127.0.0.1 -p 6379 HGETALL waikness:config
    exit 0
  fi
  sleep 1
done
echo "ERROR: timeout" >&2
exit 1
