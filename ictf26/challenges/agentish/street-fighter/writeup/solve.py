"""
Street Fighter challenge solver.
1. Train with Master Jee-Oh Vhun-Ee (5 correct defenses)
2. Get assessment (combatant stats) and opponent info
3. Fight in arena until opponent is defeated
"""
import os
from typing import Any

import requests  # type: ignore[import-not-found]


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


DEFENSE_FOR_ATTACK = {
    "punch": "parry",
    "kick": "block",
    "sweep": "jump",
    "elbow": "sidestep",
    "headbutt": "brace",
}


def jsonrpc(url: str, method: str, params: dict[str, Any] | None = None, _id: int = 1) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data


def main() -> None:
    trainer_rpc = _env("MCP_TRAINER_URL").rstrip("/") + "/rpc"
    arena_rpc = _env("MCP_ARENA_URL").rstrip("/") + "/rpc"

    # 1. Start training
    res = jsonrpc(trainer_rpc, "tools/call", {"name": "train", "arguments": {}})
    training_id = res["result"]["training_id"]
    print(f"[solve] Training started: {training_id}")

    # 2. Complete training (3-10 correct reactions depending on session)
    while True:
        res = jsonrpc(trainer_rpc, "tools/call", {"name": "action", "arguments": {"training_id": training_id}})
        result = res["result"]
        if result.get("action") == "trained":
            print("[solve] Training complete.")
            break
        step_id = result["step"]
        attack = result["attack"]
        defense = DEFENSE_FOR_ATTACK[attack]
        print(f"[solve] Step {step_id}: defending {attack} with {defense}")
        res = jsonrpc(
            trainer_rpc,
            "tools/call",
            {"name": "reaction", "arguments": {"training_id": training_id, "step_id": step_id, "reaction": defense}},
        )
        if res["result"].get("action") == "trained":
            break

    # 3. Get assessment and opponent info
    res = jsonrpc(trainer_rpc, "tools/call", {"name": "assessment", "arguments": {"training_id": training_id}})
    combatant = res["result"].get("combatant", {})
    print("[solve] Assessment:", res["result"]["content"][0]["text"])

    res = jsonrpc(trainer_rpc, "tools/call", {"name": "opponent", "arguments": {"training_id": training_id}})
    opponent = res["result"].get("opponent", {})
    print("[solve] Opponent:", res["result"]["content"][0]["text"])

    # Pick strategy attack: highest damage * success_rate * (1 - opp_defense_rate)
    # (attack that opponent is bad at defending against)
    ATTACKS = ["punch", "kick", "sweep", "elbow", "headbutt"]
    best_attack = "punch"
    best_expected = 0.0
    combatant_attacks = combatant.get("attacks", {})
    opp_defenses = opponent.get("defenses", {})
    for attack in ATTACKS:
        atk_data = combatant_attacks.get(attack, {})
        def_name = DEFENSE_FOR_ATTACK[attack]
        opp_def = opp_defenses.get(def_name, {"success_rate": 0.5})
        expected = (
            atk_data.get("damage", 0)
            * atk_data.get("success_rate", 0)
            * (1 - opp_def.get("success_rate", 0.5))
        )
        if expected > best_expected:
            best_expected = expected
            best_attack = attack
    print(f"[solve] Strategy attack: {best_attack} (expected when opp defends: {best_expected:.2f})")

    # 4. Start fight
    res = jsonrpc(arena_rpc, "tools/call", {"name": "fight", "arguments": {}})
    fight_id = res["result"]["fight_id"]
    print(f"[solve] Fight started: {fight_id}")

    # 5. Fight loop
    while True:
        res = jsonrpc(arena_rpc, "tools/call", {"name": "arena_status", "arguments": {"fight_id": fight_id}})
        result = res["result"]
        combatant_hp = result["combatant_health"]
        opponent_hp = result["opponent_health"]
        print(f"[solve] Status: Combatant={combatant_hp}, Opponent={opponent_hp}")

        if opponent_hp <= 0:
            print(result["content"][0]["text"])
            if "flag" in result:
                print(f"FLAG: {result['flag']}")
            break
        if combatant_hp <= 0:
            print(result["content"][0]["text"])
            break

        # Get next action
        res = jsonrpc(arena_rpc, "tools/call", {"name": "arena_action", "arguments": {"fight_id": fight_id}})
        result = res["result"]
        step_id = result["step"]
        action_val = result.get("action", "")

        if result.get("game_over"):
            print(result["content"][0]["text"])
            break

        # action is always opponent attack; react with defense or counter-attack
        opponent_missed = not result.get("success", True)
        reaction_val = best_attack if opponent_missed else DEFENSE_FOR_ATTACK.get(action_val, "block")

        print(f"[solve] Step {step_id}: reacting with {reaction_val}")
        jsonrpc(
            arena_rpc,
            "tools/call",
            {"name": "arena_reaction", "arguments": {"fight_id": fight_id, "step_id": step_id, "action": reaction_val}},
        )


if __name__ == "__main__":
    main()
