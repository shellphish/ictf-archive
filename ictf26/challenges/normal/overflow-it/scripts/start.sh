#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="overflow-it:local"
CONTAINER_NAME="overflow-it-local"
PORT="${PORT:-1337}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if ! docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
  echo "Image ${IMAGE_NAME} not found. Run ./scripts/build.sh first."
  exit 1
fi

if docker ps -a --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"; then
  echo "Removing existing container ${CONTAINER_NAME}"
  docker rm -f "${CONTAINER_NAME}" >/dev/null
fi

echo "Starting ${CONTAINER_NAME}"
if [ -f "${ENV_FILE}" ]; then
  docker run -d --name "${CONTAINER_NAME}" \
    --env-file "${ENV_FILE}" \
    -e PORT="${PORT}" \
    -p "${PORT}:${PORT}" \
    "${IMAGE_NAME}" >/dev/null
else
  echo "Warning: ${ENV_FILE} not found. LLM calls may fail without API key env vars."
  docker run -d --name "${CONTAINER_NAME}" \
    -e PORT="${PORT}" \
    -p "${PORT}:${PORT}" \
    "${IMAGE_NAME}" >/dev/null
fi

echo "Container started"
echo "Connect for testing: nc 127.0.0.1 ${PORT}"
echo "Follow logs: docker logs -f ${CONTAINER_NAME}"
