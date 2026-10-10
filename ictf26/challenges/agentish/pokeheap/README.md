# Pokeheap: Use-After-Free

**Category**: pwn | **Difficulty**: Beginner | **Points**: 100

## Description

Prof. Oak's Pokémon management system has a memory bug. A released Pokémon is
not cleared from the global pointer — it can still be reached and called through
that stale reference.

Redirect the Pokémon's move to `win()` and catch Mew!

## How to run locally

```bash
cp env.example .env
# fill in your API keys in .env
docker compose up --build
```

The GDB MCP server will be available at `http://localhost:3000/sse`.

## Required secrets (`env.example`)

| Variable | Purpose |
|---|---|
| `FLAG` | Team-specific flag injected at runtime |
| `OPENAI_API_KEY` | Used by `flag_reveal.py` to call the LLM |
| `LANGFUSE_PUBLIC_KEY` | Langfuse project public key |
| `LANGFUSE_SECRET_KEY` | Langfuse project secret key |
| `LANGFUSE_HOST` | Langfuse host (default: `https://cloud.langfuse.com`) |
| `TEAM_LITELLM_API_KEY` | Key injected into the sandbox agent |
| `LITELLM_BASE_URL` | LiteLLM proxy base URL |

## Intended solution

See `writeup/WRITEUP.md`.
