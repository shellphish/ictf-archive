#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="overflow-it:local"

echo "Building ${IMAGE_NAME} from ${ROOT_DIR}"
docker build -t "${IMAGE_NAME}" "${ROOT_DIR}"
echo "Build complete"
