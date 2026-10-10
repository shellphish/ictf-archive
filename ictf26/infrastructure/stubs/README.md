# Shared stubs

This repository provides reusable **local testing stubs** for shared infrastructure that would normally be provided externally in production deployments.

## What’s included

- `stubs/litellm_stub`: OpenAI-compatible stub which uses the LiteLLM SDK to call OpenAI for local testing.
- `stubs/langfuse_stub`: Minimal HTTP service stub for local testing.
- `stubs/sandbox_stub`: Minimal “sandbox runner” that executes a mounted Python file.

## How challenges should use these stubs

From a challenge directory like `challenges/<name>/`, reference stubs in `docker-compose.yml` using:

- `build.context: ../../stubs`
- `build.dockerfile: <stub_name>/Dockerfile`
 
Configuration should be provided via **environment variables** (e.g. `LITELLM_BASE_URL`, `LITELLM_MODEL`, `LANGFUSE_BASE_URL`).
If you need separate models for challenge bootstrap vs team agent, use `CHALLENGE_LITELLM_MODEL` and `TEAM_LITELLM_MODEL`.

