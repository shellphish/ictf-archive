#!/bin/bash
set -euo pipefail
source scripts/challenge.sh

CONTAINER_IDS=$(docker ps -q --filter ancestor=${CHALLENGE_NAME})
if [ -z "$CONTAINER_IDS" ]; then
  echo "No running containers found for image '${CHALLENGE_NAME}'"
  exit 0
fi

for CONTAINER_ID in $CONTAINER_IDS; do
  echo "Stopping container $CONTAINER_ID..."
  docker stop $CONTAINER_ID
done

