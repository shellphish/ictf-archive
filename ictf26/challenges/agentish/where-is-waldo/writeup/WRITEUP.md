# Waldo’s State (Reference) — Writeup

### Goal

Retrieve the flag by guessing the **US state** where Waldo lives.

### Services / tools

The sandbox can call two MCP servers (JSON-RPC at `/rpc`):

- **`waldo_landmarks`** (on `mcp_landmarks`): returns three landmarks near Waldo’s city
- **`guess_state`** (on `mcp_flag`): returns the flag when given the correct state

At startup, a datastore container picks a **US city**, **three landmarks**, and the **state**, then stores them in Redis.

### Solution approach

- Call `waldo_landmarks` to get the three landmarks.
- Infer the US state that those landmarks belong to (either with an LLM via the LiteLLM proxy, or by manual knowledge/search).
- Call `guess_state` with the full state name to receive the flag.

### Reference solver

The file `solve.py` does exactly this:

- MCP call to fetch landmarks
- LLM (LiteLLM) call to infer the state (with a small fallback for the seeded default)
- MCP call to submit the state and print the flag

Implementation note: the solver is orchestrated with **LangGraph** (a small `StateGraph` with linear steps).
