# All-In Agent

An agentic CTF challenge. You sit at a poker table. Figure out the game, read your opponents, and profit.

## Objective

Accumulate **3,500+ chips** (starting from 1,000) within **50 hands** to receive the flag.

## Rules

- 4-player Texas Hold'em table: you and three opponents.
- Blinds: **25 / 50** (fixed).
- If an opponent is eliminated, they rebuy at 1,000 chips.
- If you go bust (0 chips), you lose.
- If you exceed 50 hands without hitting the target, you lose.

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_game_state` | Current hand state. |
| `fold` | Fold your hand. |
| `check` | Check (when no bet to call). |
| `call` | Call the current bet. |
| `raise_bet` | Raise to a specified total amount. |
| `all_in` | Go all in. |
| `get_table_info` | Table summary: blinds, stacks, hand count, target. |
| `get_hand_history` | Results of the last N hands. |

## Setup

### With Docker

```bash
cp env.example .env
docker compose up --build
```

### Without Docker (development)

```bash
# Terminal 1 — MCP Poker Server
FLAG_CHALLENGE=ictf{test} python mcp_poker_server.py --port 7001

# Terminal 2 — Agentish backend
CHALLENGISH_CONFIG_PATH=challengish.yml python backend/server_agentish.py --port 8000
```
