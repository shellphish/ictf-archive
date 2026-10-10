# Street Fighter — Writeup

### Goal

Retrieve the flag by defeating the opponent in turn-based combat.

### Services / tools

The sandbox can call two MCP servers (JSON-RPC at `/rpc`):

**MCP Trainer** (`mcp_trainer`):
- `train`: Start training, returns `training_id`
- `action`: Get current step and attack to defend against
- `reaction`: Submit defense (parry/block/jump/sidestep/brace)
- `status`: Get training status: `in_progress`, `success`, or `failure` — call this to know when training is finished
- `assessment`: Get combatant stats (requires training status `success`)
- `opponent`: Get opponent stats (requires training status `success`)

**MCP Arena** (`mcp_arena`):
- `fight`: Start fight, returns `fight_id`
- `arena_action`: Get opponent's attack (always alternate action then reaction)
- `arena_reaction`: Defend or counter-attack (when opponent misses, counter-attack only)
- `arena_status`: Get health levels; returns flag when opponent at 0

### Attack–defense mapping

| Attack   | Defense  |
|----------|----------|
| punch    | parry    |
| kick     | block    |
| sweep    | jump     |
| elbow    | sidestep |
| headbutt | brace    |

### Solution approach

1. Call `train` to get `training_id`
2. Loop: call `action` → get attack → call `reaction` with correct defense. Repeat until `status` returns `success`
3. Call `assessment` and `opponent` to get stats
4. Call `fight` to get `fight_id`
5. Fight loop: call `arena_action` (opponent attack) → `arena_reaction` (defend or counter-attack with strategy attack when countering). Repeat.
6. Call `arena_status` until opponent health is 0; flag is returned

### Reference solver

The file `solve.py` implements this flow:
- Uses the attack–defense mapping for training
- Picks the **strategy attack**: highest expected damage when opponent defends, i.e. `damage × success_rate × (1 − opp_defense_rate)`. This is the attack the opponent is worst at blocking.
- When opponent hits: defend with the correct defense. When opponent misses: counter-attack with the strategy attack.
- Alternates between defending and attacking in the arena until victory
