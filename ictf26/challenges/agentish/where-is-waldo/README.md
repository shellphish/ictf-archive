# Reference challenge: Waldo’s State

This is a **minimal reference challenge** for challenge authors.

### What’s in here

- **Sandbox** container: the agent execution environment (same image across challenges).  
  For this reference, we provide a `sandbox_stub` service that **simulates the organizer-provided sandbox image**
  by running a mounted Python file (see `writeup/solve.py`). The sandbox stub (and other shared stubs) live in top-level `stubs/`.
- **Environment variables**: configuration for LiteLLM/LangFuse URLs, default model, and optional keys (see `env.example`).
- **Datastore** container: at startup, calls the LLM (via LiteLLM proxy) to pick:
  - a famous US city
  - three landmarks in that city
  - the US state the city belongs to  
  Then stores that info in Redis for the MCP servers to use.
  Note that this component uses a challenge-associated LiteLLM key that is different from the key given to the agent.
- **Two MCP servers**:
  - `mcp_landmarks`: provides landmarks “about where Waldo is”
  - `mcp_flag`: returns the flag if the agent guesses the correct US state
- **Support**: The `datastore` container also runs Redis for shared state.

### Quickstart

- Copy env file:

```bash
cp env.example .env
```

- Review `env.example`. For local testing you’ll usually only need to set `LITELLM_API_KEY` in `.env`.

- Set an OpenAI key for local testing (used by the LiteLLM proxy):
  - In `.env`, set `LITELLM_API_KEY=...`

- Start the challenge:

```bash
docker compose up --build
```

The `sandbox` service will run `writeup/solve.py` inside the sandbox stub and print the flag on success.

### Shared stubs vs “real” shared infrastructure (LiteLLM + LangFuse)

By default, `docker compose up --build` runs with the shared **stubs** from top-level `stubs/`:

- `litellm` runs the LiteLLM proxy image configured with **two** request keys (`CHALLENGE_LITELLM_API_KEY` and `TEAM_LITELLM_API_KEY`) and uses `LITELLM_API_KEY` internally to call OpenAI
- `langfuse` is built from `stubs/langfuse_stub`
- `sandbox` is built from `stubs/sandbox_stub` and executes the mounted solver

In a real deployment, this challenge is designed to **connect to existing**:

- **LiteLLM proxy** (OpenAI-compatible): set `LITELLM_BASE_URL` + model env vars
  - For bootstrap/datastore: `CHALLENGE_LITELLM_MODEL` (falls back to `LITELLM_MODEL`)
  - For the sandbox/agent: `TEAM_LITELLM_MODEL` (falls back to `LITELLM_MODEL`)
  - For bootstrap/datastore: `CHALLENGE_LITELLM_API_KEY` (optional; may be unused by some proxies)
  - For the sandbox/agent: `TEAM_LITELLM_API_KEY` (optional; may be unused by some proxies)
- **LangFuse**: set `LANGFUSE_BASE_URL`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` (optional; this reference doesn’t log yet)

If LiteLLM is unreachable or misconfigured, the datastore container will fail to start (it must generate the configuration).

### CTFd

This directory includes a CTFd-compatible `challenge.yml` for use with tools like `ctfcli`
or the portable challenges workflow.

### Writeup / solver

The reference solver at `writeup/solve.py` is implemented using **LangGraph** to orchestrate
the solve steps as a small graph.
