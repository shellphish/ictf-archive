# Starport Static Heist

Starport Static Heist is an agentic log-forensics challenge where the player must reconstruct a rotating 10-hex key from noisy, shuffled logs and submit it before the key bucket changes.

## Included Components

- `challenge.yml`: CTFd portable challenge metadata.
- `challengish.yml`: MCP server/tool contract for Agentish.
- `docker-compose.yml`: local challenge topology (MCP service + sandbox stub).
- `public/challenge.md`: player-facing prompt.
- `public/data/vr_session_logs_part*.jsonl`: fragmented log corpus.
- `public/basic_skills_api.py`: local low-level skill API.
- `public/validate.py`: local key validator.
- `services/mcp_logs/server.py`: JSON-RPC MCP server exposing challenge tools.
- `writeup/solve.py`: reference solver run by sandbox stub.
- `tools/generate_dataset.py`: deterministic dataset generator.
- `tools/test_solve.py`: organizer solvability test.

## MCP Tool Contract

The `mcp_logs` server exposes:

- `list_logs`
- `retrieve_lines_from_log`
- `submit_key`

All tools are served through `POST /rpc` using JSON-RPC (`initialize`, `tools/list`, `tools/call`), plus `GET /healthz`.

## Quickstart

From `challenges/starport_static_heist`:

```bash
cp env.example .env
```

Review `env.example`. For local testing you'll usually only need to set `LITELLM_API_KEY` in `.env` (used by the LiteLLM stub to call OpenAI upstream).

```bash
docker compose up --build
```

This starts `mcp_logs` only. To also run the debug stack (LiteLLM stub, LangFuse stub, and the sandbox solver):

```bash
docker compose --profile debug up --build
```

The `sandbox` service runs `writeup/solve.py` and prints the flag on success.

To run only the MCP server:

```bash
docker compose up --build mcp_logs
```

### Shared stubs vs real shared infrastructure

With `--profile debug`, the stack runs shared **stubs** from top-level `stubs/`:

- `litellm` runs the LiteLLM proxy configured with `CHALLENGE_LITELLM_API_KEY` and `TEAM_LITELLM_API_KEY` and uses `LITELLM_API_KEY` internally to call OpenAI
- `langfuse` is built from `stubs/langfuse_stub`
- `sandbox` is built from `stubs/sandbox_stub` and executes the mounted solver

In a real deployment, set `LITELLM_BASE_URL`, `TEAM_LITELLM_API_KEY`, and `TEAM_LITELLM_MODEL` to point at the shared infrastructure.

## Local Script Checks

Generate/refresh data:

```bash
python3 tools/generate_dataset.py
```

Run API directly:

```bash
python3 public/basic_skills_api.py list_logs
python3 public/basic_skills_api.py retrieve_lines_from_log vr_session_logs_part1.jsonl 1 5
python3 public/validate.py <10_hex_key>
```

Run solvability test:

```bash
python3 tools/test_solve.py
```
