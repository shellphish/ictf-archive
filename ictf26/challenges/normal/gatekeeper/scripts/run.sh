#!/bin/bash
set -euo pipefail
source scripts/challenge.sh

ENV_ARGS=()
if [ -n "${OPENAI_API_KEY:-}" ]; then
  ENV_ARGS+=(-e "OPENAI_API_KEY=${OPENAI_API_KEY}")
fi
if [ -n "${OPENAI_API_BASE:-}" ]; then
  ENV_ARGS+=(-e "OPENAI_API_BASE=${OPENAI_API_BASE}")
fi
if [ -n "${CHALLENGE_LITELLM_MODEL:-}" ]; then
  ENV_ARGS+=(-e "CHALLENGE_LITELLM_MODEL=${CHALLENGE_LITELLM_MODEL}")
fi
if [ -n "${LITELLM_MODEL:-}" ]; then
  ENV_ARGS+=(-e "LITELLM_MODEL=${LITELLM_MODEL}")
fi
if [ -n "${DEBUG:-}" ]; then
  ENV_ARGS+=(-e "DEBUG=${DEBUG}")
fi
if [ -n "${DEBUG_LOG:-}" ]; then
  ENV_ARGS+=(-e "DEBUG_LOG=${DEBUG_LOG}")
fi

docker run --rm -p ${CHALLENGE_PORT}:${CHALLENGE_PORT} "${ENV_ARGS[@]}" ${CHALLENGE_NAME}

