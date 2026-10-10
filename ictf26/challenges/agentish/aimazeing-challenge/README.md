# AIMazeIng Challenge

An agentic CTF challenge where an AI agent must navigate a procedurally generated 5×5 roguelike maze, collect resources, solve riddles, and assemble a puzzle to obtain the flag.

Every session generates a unique maze: room layout, contents, and final room position change on each run.

## Objective

Collect **4 puzzle pieces** and bring them to the **final room** to assemble the puzzle and receive the flag.

## Room Types

| Type | Rarity | Description |
|------|--------|-------------|
| **Lever** | Common | Solve a riddle → pull the correct lever (blue/pink/green). Wrong lever = −1 life. |
| **Corridor** | Common | Simple room with open doors in all 4 directions. |
| **Treasure** | Uncommon | Contains gold coins and possibly a puzzle piece. Collect all items at once. |
| **Merchant** | Rare | Sells 1 puzzle piece for 5 gold coins. |
| **Final** | Unique | Bring all 4 puzzle pieces here to win. |

## Resources

- **Gold coins** — currency for the merchant.
- **Puzzle pieces** — 4 total, distributed across treasure rooms (also purchasable from the merchant).

## Rules

- The player starts with **3 lives**.
- Pulling the wrong lever costs **1 life**. At 0 lives → game over.
- Visited rooms retain their state (collected items do not respawn).
- Players may revisit rooms freely.
- There are exactly **4 puzzle pieces** available in the maze.

## MCP Tools

| Tool | Description |
|------|-------------|
| `look` | Observe the current room. |
| `move` | Move in a direction (`north`, `south`, `east`, `west`). |
| `pull_lever` | Pull a coloured lever (`blue`, `pink`, `green`). |
| `collect_treasure` | Collect all items from a treasure room. |
| `buy_item` | Buy from the merchant (`puzzle_piece` costs 5 gold). |
| `assemble_puzzle` | Assemble the puzzle in the final room to get the flag. |
| `get_map` | Show the map of visited rooms. |
| `get_status` | Show current lives, inventory, and position. |

## Agent Strategy

1. Use `look` on every new room to understand its type.
2. Use `get_map` periodically to track explored rooms.
3. In treasure rooms, **prioritise puzzle pieces** over gold.
4. Accumulate gold to buy missing pieces from merchants if needed.
5. In lever rooms, read the riddle carefully and pick the correct colour.
6. Once all 4 pieces are collected, navigate to the final room and call `assemble_puzzle`.

## Setup

### With Docker

```bash
docker compose up --build
```

### Without Docker (development)

```bash
# Terminal 1 — MCP Maze Server
python mcp_maze_server.py --port 7001

# Terminal 2 — Agentish backend
CHALLENGISH_CONFIG_PATH=challengish.yml python ../../backend/server_agentish.py --port 8000
```
