#!/bin/bash
set -euo pipefail
source scripts/challenge.sh
docker build -t ${CHALLENGE_NAME} .

