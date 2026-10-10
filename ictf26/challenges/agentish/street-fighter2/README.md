# Street Fighter 2 CTF Challenge

A CTF challenge where participants must create intelligent agents to fight in 2v2 Street Fight-style combat.
Your agent controls two combatants and must defeat two opponents to win the flag!

## Challenge Overview

In this challenge, participants must create an agent that will fight on their behalf in a turn-based 2v2 combat system. The agent must:

1. **Train** with Master Jee-Oh Vhun-Ee to learn strategic information about its onw players (the combatants) and both opponents
2. **Fight** in the arena using turn-based combat with four fighters (2 combatants vs 2 opponents)
3. **Win** by defeating the opponents—ideally via the **combo attack** for instant victory

### Four Fighters

- **Combatant A** and **Combatant B**: Your team (controlled by your agent)
- **Opponent A** and **Opponent B**: The adversary team

### Combo Mechanics

**Against opponents:**
- **Opponent combo vulnerability**: A sequence of two moves `[move_a, move_b]` that the opponents perform (one per opponent). When they do this, they open themselves to the combo attack.
- **Combatant combo attack**: A sequence of two moves `[move_a, move_b]` that the combatants perform (one per combatant). If performed after the opponents have done the vulnerability combo, it's an **instant win** (sudden death).

**Against combatants (avoid!):**
- **Combatant combo vulnerability**: A sequence of two moves `[move_a, move_b]` that the combatants perform (one per combatant). If you do this, you expose yourselves!
- **Opponent combo attack**: What opponents do when combatants expose themselves—**instant loss** for the combatants.

The opponents perform the vulnerability combo with ~50% probability when they have the first two moves in a 4-event turn window.

### Turn Order

Each "round" has 4 turns—one per fighter. The order is a **random permutation** of the four fighters each round (e.g. CombA, OppB, OppA, CombB, then CombB, OppA, CombA, OppB, etc.).

When opponents have the first two moves in a round, they may perform the vulnerability combo (50% chance), exposing them to your combo attack.

### Interaction with the Trainer

Same as Street Fighter 1: `train`, `attack`, `defense`, `status`, `assessment`, `opponents`.

The **assessment** endpoint returns JSON for **both combatants** (combatant_1, combatant_2) plus combatant combo info:
- `combatant_combo_attack`: Use when opponents expose vulnerability (instant win)
- `combatant_combo_vulnerability`: Moves to AVOID (opens you to opponent combo)

The **opponents** endpoint returns JSON for **both opponents** (opponent_1, opponent_2) plus opponent combo info:
- `opponent_combo_vulnerability`: What opponents do that exposes them
- `opponent_combo_attack`: What opponents do when you expose yourselves

### Interaction with the Arena

- **fight**: Start a 2v2 fight, returns `fight_id`
- **status**: Get combatant/opponent health and whose turn it is (no vulnerability info—infer from history)
- **history**: Get the last `n` moves (pass `n=0` for all moves)
- **action**: Advance to next turn. If opponent's turn, processes their move and returns it. If combatant's turn, returns `your_turn: true`—you must then call **reaction** with your move.
- **reaction**: Submit your combatant's attack (punch/kick/sweep/elbow/headbutt) and **target** (opponent_a or opponent_b). The target's defense is used to calculate success rate.

### Strategy

1. Train and get `combatant_combo_attack` from assessment, `opponent_combo_vulnerability` from opponents
2. Call `status` to see whose turn it is
3. Call `action` to advance—when you get `your_turn`, call `reaction` with the appropriate move
4. Use `history` to detect when opponents did the vulnerability combo (type `vulnerability_combo`); then perform the combo attack: Combatant A does `combatant_combo_attack[0]`, Combatant B does `combatant_combo_attack[1]` for instant win
5. Otherwise, use normal attacks with target (opponent_a or opponent_b) to whittle down opponent health. Each round has 4 moves (one per fighter). Team loses when both combatants have 0 health; team wins when both opponents have 0 health.
