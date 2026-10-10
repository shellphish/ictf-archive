#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-overflow-it:local}"
NAME_PATTERN="${NAME_PATTERN:-overflow-it}"

mapfile -t containers < <(
  {
    docker ps --filter "ancestor=${IMAGE_NAME}" --format '{{.ID}}'
    docker ps --filter "name=${NAME_PATTERN}" --format '{{.ID}}'
  } | awk 'NF' | sort -u
)

if [ "${#containers[@]}" -eq 0 ]; then
  echo "No active challenge containers found"
  exit 0
fi

docker kill "${containers[@]}" >/dev/null

echo "Killed ${#containers[@]} challenge container(s)"
