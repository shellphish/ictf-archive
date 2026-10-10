"""
Street Fighter 2 challenge solver.
1. Train with Master Jee-Oh Vhun-Ee
2. Get assessment (combatant stats + combatant combos) and opponents (opponent stats + opponent combos)
3. Fight in 2v2 arena until opponents defeated (use combo attack when vulnerable)
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
ATTACKS = ["punch", "kick", "sweep", "elbow", "headbutt"]


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

    # 2. Complete training (3-10 correct defenses depending on session)
    while True:
        res = jsonrpc(trainer_rpc, "tools/call", {"name": "attack", "arguments": {"training_id": training_id}})
        result = res["result"]
        if result.get("status") == "trained":
            print("[solve] Training complete.")
            break
        step_id = result["step"]
        attack = result["attack"]
        defense = DEFENSE_FOR_ATTACK[attack]
        print(f"[solve] Step {step_id}: defending {attack} with {defense}")
        res = jsonrpc(
            trainer_rpc,
            "tools/call",
            {"name": "defense", "arguments": {"training_id": training_id, "step_id": step_id, "defense": defense}},
        )
        if res["result"].get("status") == "trained":
            break

    # 3. Get assessment (combatants + combatant combos) and opponents (opponents + opponent combos)
    res = jsonrpc(trainer_rpc, "tools/call", {"name": "assessment", "arguments": {"training_id": training_id}})
    combatant_1 = res["result"].get("combatant_1", {})
    combatant_2 = res["result"].get("combatant_2", {})
    combatant_combo_attack = res["result"].get("combatant_combo_attack", ["punch", "punch"])
    combatant_combo_vulnerability = res["result"].get("combatant_combo_vulnerability", [])
    print("[solve] Assessment:", res["result"]["content"][0]["text"])

    res = jsonrpc(trainer_rpc, "tools/call", {"name": "opponents", "arguments": {"training_id": training_id}})
    opponent_1 = res["result"].get("opponent_1", {})
    opponent_combo_vulnerability = res["result"].get("opponent_combo_vulnerability", [])
    print("[solve] Opponents:", res["result"]["content"][0]["text"])
    print(f"[solve] Combo: opponent_vulnerability={opponent_combo_vulnerability}, combatant_attack={combatant_combo_attack}")
    print(f"[solve] Our vulnerability (AVOID): {combatant_combo_vulnerability}")

    # Pick best normal attack per combatant (avoid their combo vulnerability move)
    def best_attack_for(combatant: dict, opp_defenses: dict, avoid_move: str) -> str:
        best, best_exp = "punch", 0.0
        for attack in ATTACKS:
            if attack == avoid_move:
                continue
            atk_data = combatant.get("attacks", {}).get(attack, {})
            def_name = DEFENSE_FOR_ATTACK[attack]
            opp_def = opp_defenses.get(def_name, {"success_rate": 0.5})
            expected = (
                atk_data.get("damage", 0)
                * atk_data.get("success_rate", 0)
                * (1 - opp_def.get("success_rate", 0.5))
            )
            if expected > best_exp:
                best_exp, best = expected, attack
        return best

    opp_defenses = opponent_1.get("defenses", {})
    avoid_a = combatant_combo_vulnerability[0] if len(combatant_combo_vulnerability) > 0 else ""
    avoid_b = combatant_combo_vulnerability[1] if len(combatant_combo_vulnerability) > 1 else ""
    best_attack_a = best_attack_for(combatant_1, opp_defenses, avoid_a)
    best_attack_b = best_attack_for(combatant_2, opp_defenses, avoid_b)
    print(f"[solve] Best attacks: combatant_a={best_attack_a}, combatant_b={best_attack_b}")

    # 4. Start fight
    res = jsonrpc(arena_rpc, "tools/call", {"name": "fight", "arguments": {}})
    fight_id = res["result"]["fight_id"]
    print(f"[solve] Fight started: {fight_id}")

    # 5. Fight loop (2v2: action/reaction for combatant turns, each attack has target)
    while True:
        res = jsonrpc(arena_rpc, "tools/call", {"name": "fight_status", "arguments": {"fight_id": fight_id}})
        result = res["result"]
        ca = result.get("combatant_a_health", 100)
        cb = result.get("combatant_b_health", 100)
        oa = result.get("opponent_a_health", 100)
        ob = result.get("opponent_b_health", 100)
        print(f"[solve] Status: Combatant_a={ca}, Combatant_b={cb} | Opponent_a={oa}, Opponent_b={ob}")

        if result.get("game_over"):
            print(result["content"][0]["text"])
            if "flag" in result:
                print(f"FLAG: {result['flag']}")
            break

        current_turn = result.get("current_turn", "opponent_a")
        if current_turn in ("combatant_a", "combatant_b"):
            pending = result.get("pending_attack")
            if pending:
                attack_type = pending.get("attack_type", "punch")
                defense = DEFENSE_FOR_ATTACK.get(attack_type, "block")
                print(f"[solve] {current_turn}: defend {attack_type} with {defense}")
                res = jsonrpc(
                    arena_rpc,
                    "tools/call",
                    {"name": "action", "arguments": {"fight_id": fight_id, "combatant": current_turn, "defense": defense}},
                )
            else:
                hist_res = jsonrpc(arena_rpc, "tools/call", {"name": "history", "arguments": {"fight_id": fight_id, "n": 0}})
                history = hist_res["result"].get("history", [])
                vuln_idxs = [i for i, m in enumerate(history) if m.get("type") == "vulnerability_combo"]
                if len(vuln_idxs) >= 2:
                    last_vuln_idx = vuln_idxs[-1]
                    vuln_fighters = {history[i].get("fighter") for i in vuln_idxs[-2:]}
                    moves_after = history[last_vuln_idx + 1:]
                    wrong_move = any(
                        m.get("fighter", "").startswith("combatant") and m.get("type") == "attack"
                        for m in moves_after
                    )
                    combo_count = sum(1 for m in moves_after if m.get("type") == "combo_attack")
                    vulnerability_exposed = (
                        vuln_fighters == {"opponent_a", "opponent_b"} and not wrong_move and combo_count < 2
                    )
                else:
                    vulnerability_exposed = False

                if vulnerability_exposed:
                    action_val = combatant_combo_attack[combo_count]
                    target = "opponent_a"
                    print(f"[solve] {current_turn}: combo attack {action_val}")
                else:
                    action_val = best_attack_a if current_turn == "combatant_a" else best_attack_b
                    target = "opponent_b" if oa <= 0 else ("opponent_a" if ob <= 0 else ("opponent_a" if oa >= ob else "opponent_b"))
                    print(f"[solve] {current_turn}: normal attack {action_val} @ {target}")

                res = jsonrpc(
                    arena_rpc,
                    "tools/call",
                    {"name": "action", "arguments": {"fight_id": fight_id, "combatant": current_turn, "action": action_val, "target": target}},
                )
            if res["result"].get("game_over") and res["result"].get("flag"):
                print(f"FLAG: {res['result']['flag']}")
                break
        else:
            res = jsonrpc(arena_rpc, "tools/call", {"name": "action", "arguments": {"fight_id": fight_id}})
            result = res["result"]
            if result.get("game_over"):
                if result.get("flag"):
                    print(f"FLAG: {result['flag']}")
                break
            print(f"[solve] {result.get('fighter', '?')} did {result.get('action', '?')}")


if __name__ == "__main__":
    main()
