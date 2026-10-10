#!/usr/bin/env bash
set -euo pipefail

mapfile -t containers < <(docker ps -q)

if [ "${#containers[@]}" -eq 0 ]; then
  echo "No active containers to kill"
  exit 0
fi

docker kill "${containers[@]}" >/dev/null

echo "Killed ${#containers[@]} active container(s)"
