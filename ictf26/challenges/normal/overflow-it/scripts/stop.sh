#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="overflow-it-local"

if docker ps -a --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"; then
  echo "Stopping and removing ${CONTAINER_NAME}"
  docker rm -f "${CONTAINER_NAME}" >/dev/null
  echo "Container removed"
else
  echo "Container ${CONTAINER_NAME} not found"
fi
