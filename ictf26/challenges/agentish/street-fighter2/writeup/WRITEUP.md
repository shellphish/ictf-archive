# Street Fighter 2 — Writeup

### Goal

Retrieve the flag by defeating the two opponents in 2v2 turn-based combat. The fastest path is the **combo attack** (instant win).

### Services / tools

The sandbox can call two MCP servers (JSON-RPC at `/rpc`):

**MCP Trainer** (`mcp_trainer`):
- `train`: Start training, returns `training_id`
- `attack`: Get current step and attack to defend against
- `defense`: Submit defense (parry/block/jump/sidestep/brace)
- `status`: Get training status: `in_progress`, `success`, or `failure`
- `assessment`: Returns JSON for **both combatants** (combatant_1, combatant_2) plus combatant combo info: `combatant_combo_attack`, `combatant_combo_vulnerability` (requires training status `success`)
- `opponents`: Returns JSON for **both opponents** (opponent_1, opponent_2) plus opponent combo info: `opponent_combo_vulnerability`, `opponent_combo_attack` (requires training status `success`)

**MCP Arena** (`mcp_arena`):
- `fight`: Start 2v2 fight, returns `fight_id`
- `status`: Get health and whose turn (vulnerability must be inferred from history)
- `history`: Get last `n` moves (`n=0` for all)
- `action`: Advance turn; returns opponent move or `your_turn: true`
- `reaction`: Submit combatant move when it's your turn

### Combo mechanics

- **Opponent combo vulnerability**: Opponents perform `[move_a, move_b]` (one each). ~50% chance when they have first two moves in a round.
- **Combatant combo attack** (yours): Combatants perform `[move_a, move_b]` (one each). Instant win if done after opponent vulnerability.
- **Combatant combo vulnerability** (AVOID): If combatants do `[move_a, move_b]` (one each), they expose themselves.
- **Opponent combo attack**: Opponents perform `[move_a, move_b]` (one each) when combatants are exposed—instant loss.

### Solution approach

1. Call `train` to get `training_id`
2. Loop: `attack` → get attack → `defense` with correct defense. Repeat until `status` returns `success`
3. Call `assessment` and `opponents` to get stats and combo info
4. Call `fight` to get `fight_id`
5. Fight loop:
   - Call `status` to check game state
   - Call `action` to advance
   - If `your_turn`: call `history` to detect vulnerability (type `vulnerability_combo` from both opponents), then call `reaction` with combo attack or best normal attack
   - If opponent's turn: action already processed their move, continue
6. Call `status` until opponent health is 0; flag is returned

### Reference solver

The file `solve.py` implements this flow:
- Uses the attack–defense mapping for training
- Gets both combatants + combatant combos from assessment, both opponents + opponent combos from opponents endpoint
- Avoids `combatant_combo_vulnerability` when choosing normal attacks
- When history shows both opponents did `vulnerability_combo` and combatants haven't reset: Combatant A does `combatant_combo_attack[0]`, Combatant B does `combatant_combo_attack[1]`
- Otherwise: use best normal attack per combatant (highest damage × success_rate × (1 − opp_defense))
