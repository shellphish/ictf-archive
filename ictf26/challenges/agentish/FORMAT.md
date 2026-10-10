### Challenge format (canonical)

This document defines the **standard structure** and **requirements** for any challenge included under `challenges/`.
It is intended to be used for automated verification that all challenges follow the same format.

---

### 1) Directory layout

Each challenge MUST live at:

- **`challenges/<challenge-id>/`**

Where `<challenge-id>` is a stable, filesystem-safe identifier (lowercase, hyphen-separated recommended).

---

### 2) Required files (challenge root)

Each challenge directory MUST contain:

- **`challenge.yml`**: CTFd-compatible metadata (portable challenge format).
- **`challengish.yml`**: agent/challenge manifest describing MCP servers and model policy.
- **`docker-compose.yml`**: infrastructure definition for local/dev execution.
- **`README.md`**: human-facing description and “how to run” instructions.

---

### 3) `challenge.yml` (CTFd portable format) requirements

The `challenge.yml` MUST be conformant to common CTFd portable challenge conventions (e.g. ctfcli / portable challenges plugin).
At minimum it MUST include:

- **`name`** (string)
- **`category`** (string)
- **`description`** (string; Markdown allowed)
- **`value`** (integer)
- **`type`** (string, usually `standard`)
- **`flags`** (list) with at least one flag object containing:
  - **`flag`** (string)
  - **`type`** (string; e.g. `PLAINTEXT` or `REGEX`)

Recommended optional fields:

- **`tags`** (list of strings)
- **`hints`** (list)
- **`files`** (list; paths relative to the challenge dir)
- **`hidden`** (bool)
- **`max_attempts`** (int)
- **`requirements`** (list)

The `extra` section MAY be used for internal metadata. If present, it SHOULD include pointers to:

- **`docker_compose`**: `"docker-compose.yml"`
- **`challengish`**: `"challengish.yml"`

---

### 4) `challengish.yml` requirements

The `challengish.yml` file defines the agent-facing contract. It MUST include:

- **Challenge metadata**: id/title/description (field names may vary by organizer tooling, but must exist).
- **MCP servers**: a list of available MCP servers with:
  - **Stable server name**
  - **URL** reachable from the sandbox container network
  - **Declared tool names** exposed by that server (so the agent knows what exists)
- **Model policy**: allowed models + allowed temperature range.

---

### 5) `docker-compose.yml` requirements

The compose file defines a **local/dev** execution environment that matches the deployed topology.

It MUST define, at minimum, the following service roles:

- **Sandbox container** (organizer-provided image in production)
  - In local/dev, a stub MAY be used, but production should be able to swap in the real sandbox image.
  - The sandbox MUST be able to reach all MCP servers and any shared infra services by hostname.

- **One or more MCP server containers**
  - MCP servers are implemented by the challenge author.
  - Each MCP server MUST be reachable from the sandbox via a stable hostname and port.

If the challenge requires dynamic initialization and shared state, it MUST also include:

- **Config/bootstrap container**
  - Runs on startup to initialize challenge state (e.g., generates secrets/content).
  - Writes state to a shared component (e.g., Redis/Postgres) used by MCP servers.

Support components MAY be included as needed (databases, caches, queues).

---

### 6) MCP server interface requirements

Each MCP server MUST expose:

- **`POST /rpc`**: JSON-RPC 2.0 endpoint
  - MUST support:
    - **`initialize`**
    - **`tools/list`**
    - **`tools/call`**
  - `tools/list` MUST return the tool schemas including:
    - `name`
    - `description`
    - `inputSchema`
  - `tools/call` MUST return a `result` object containing `content`, where at least one entry is:
    - `{"type": "text", "text": "..."}`

Each MCP server SHOULD also expose:

- **`GET /healthz`**: health endpoint returning HTTP 200

Tooling note: this repo’s reference challenge uses a minimal MCP-over-HTTP JSON-RPC shape for clarity.
Organizers may adopt a different transport, but all challenges in this repo MUST be consistent with the organizer’s chosen sandbox/agent runtime.

---

### 7) Environment variables (recommended conventions)

Challenges SHOULD standardize the following env vars (set in compose and used by services):

- **`LITELLM_BASE_URL`**: base URL for the OpenAI-compatible proxy (e.g. `http://litellm:4000`)
- **`LITELLM_MODEL`**: default model used as a fallback (back-compat)
- **`CHALLENGE_LITELLM_MODEL`**: model used by challenge-owned services (bootstrap/datastore)
- **`TEAM_LITELLM_MODEL`**: model used by the sandbox/team agent
- **`LANGFUSE_BASE_URL`**: base URL of LangFuse (if used)

If you separate keys by purpose (recommended):

- **`CHALLENGE_LITELLM_API_KEY`**: used by challenge-owned services (e.g. config/bootstrap)
- **`TEAM_LITELLM_API_KEY`**: injected into the sandbox for the agent/team

Optional back-compat:

- **`LITELLM_API_KEY`**: alias some runtimes use for the team key

Per-team dynamic flags:

- **`FLAG_CHALLENGE`**: challenge secret for computing per-team flags (`ictf{sha256(secret_teamid)[:32]}`). Set via `flag_challenge` in `sandbox.yml`; passed to MCP containers automatically by the sandbox runner.

If local stubs are provided (optional), recommended:

- **`LITELLM_API_KEY`**: provider key used by the local/dev LiteLLM proxy to call the upstream model API (e.g. OpenAI)
  - model selection should be done via `CHALLENGE_LITELLM_MODEL` / `TEAM_LITELLM_MODEL`

---

### 8) Secrets policy (IMPORTANT)

This repo uses **environment variables only** for configuration and secrets.

- **DO NOT** commit real API keys, tokens, or passwords.
- Challenges SHOULD provide an `env.example` and instruct users to copy it to `.env` for local development.
- `.env` files MUST NOT be committed.

---

### 9) Writeup requirements (recommended)

Each challenge SHOULD include:

- **`writeup/WRITEUP.md`**: concise intended solution explanation
- **`writeup/solve.py`** (or equivalent): a solver that can run inside the sandbox container

If a sandbox stub is present for local testing, it SHOULD support running a mounted solver file via:

- `AGENT_FILE=/workspace/solve.py` (or similar)

---

### 10) Determinism & startup behavior

- If a config/bootstrap container calls an LLM, it SHOULD use **temperature 0** and validate output.
- The challenge SHOULD remain runnable without external dependencies when possible (e.g. safe fallback config),
  but MUST document any required secrets (e.g. `OPENAI_API_KEY`) for local testing.

