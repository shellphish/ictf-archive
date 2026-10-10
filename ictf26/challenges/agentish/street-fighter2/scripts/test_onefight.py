#!/usr/bin/env python3
"""
Runs a single fight, then attempts a second fight which must fail (DEBUG not set).

Usage:
  python scripts/test_onefight.py [--trainer-url URL] [--arena-url URL] [--no-up]
  # By default, brings up datastore, mcp_trainer, mcp_arena without DEBUG.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


DEFENSE_FOR_ATTACK = {
    "punch": "parry",
    "kick": "block",
    "sweep": "jump",
    "elbow": "sidestep",
    "headbutt": "brace",
}


def jsonrpc(url: str, method: str, params: dict | None = None, _id: int = 1) -> dict:
    payload: dict = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    return data


def run_one_fight(arena_rpc: str, trainer_rpc: str) -> bool:
    """Run one full fight. Returns True if combatant wins."""
    # Training
    res = jsonrpc(trainer_rpc, "tools/call", {"name": "train", "arguments": {}})
    training_id = res["result"]["training_id"]

    while True:
        res = jsonrpc(trainer_rpc, "tools/call", {"name": "attack", "arguments": {"training_id": training_id}})
        result = res["result"]
        if result.get("status") == "trained":
            break
        step_id = result["step"]
        attack = result["attack"]
        defense = DEFENSE_FOR_ATTACK[attack]
        jsonrpc(
            trainer_rpc,
            "tools/call",
            {"name": "defense", "arguments": {"training_id": training_id, "step_id": step_id, "defense": defense}},
        )

    res = jsonrpc(trainer_rpc, "tools/call", {"name": "assessment", "arguments": {"training_id": training_id}})
    combatant_1 = res["result"].get("combatant_1", {})
    combatant_2 = res["result"].get("combatant_2", {})
    combatant_combo_attack = res["result"].get("combatant_combo_attack", ["punch", "punch"])
    combatant_combo_vulnerability = res["result"].get("combatant_combo_vulnerability", [])
    res = jsonrpc(trainer_rpc, "tools/call", {"name": "opponents", "arguments": {"training_id": training_id}})
    opponent_1 = res["result"].get("opponent_1", {})
    opp_defenses = opponent_1.get("defenses", {})
    avoid_a = combatant_combo_vulnerability[0] if len(combatant_combo_vulnerability) > 0 else ""
    avoid_b = combatant_combo_vulnerability[1] if len(combatant_combo_vulnerability) > 1 else ""

    def _best(combatant: dict, avoid: str) -> str:
        best, best_exp = "punch", 0.0
        for attack, data in combatant.get("attacks", {}).items():
            if attack == avoid:
                continue
            def_name = DEFENSE_FOR_ATTACK[attack]
            opp_def = opp_defenses.get(def_name, {"success_rate": 0.5})
            expected = data.get("damage", 0) * data.get("success_rate", 0) * (1 - opp_def.get("success_rate", 0.5))
            if expected > best_exp:
                best_exp, best = expected, attack
        return best

    best_attack_a = _best(combatant_1, avoid_a)
    best_attack_b = _best(combatant_2, avoid_b)

    res = jsonrpc(arena_rpc, "tools/call", {"name": "fight", "arguments": {}})
    fight_id = res["result"]["fight_id"]

    while True:
        res = jsonrpc(arena_rpc, "tools/call", {"name": "status", "arguments": {"fight_id": fight_id}})
        result = res["result"]
        oa = result.get("opponent_a_health", 100)
        ob = result.get("opponent_b_health", 100)

        if result.get("game_over"):
            return bool(result.get("flag"))

        current_turn = result.get("current_turn", "opponent_a")
        if current_turn in ("combatant_a", "combatant_b"):
            pending = result.get("pending_attack")
            if pending:
                attack_type = pending.get("attack_type", "punch")
                defense = DEFENSE_FOR_ATTACK.get(attack_type, "block")
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
                else:
                    action_val = best_attack_a if current_turn == "combatant_a" else best_attack_b
                    target = "opponent_b" if oa <= 0 else ("opponent_a" if ob <= 0 else "opponent_a")
                res = jsonrpc(
                    arena_rpc,
                    "tools/call",
                    {"name": "action", "arguments": {"fight_id": fight_id, "combatant": current_turn, "action": action_val, "target": target}},
                )
            if res["result"].get("game_over") and res["result"].get("flag"):
                return True
        else:
            res = jsonrpc(arena_rpc, "tools/call", {"name": "action", "arguments": {"fight_id": fight_id}})
            if res["result"].get("game_over"):
                return bool(res["result"].get("flag"))


def run() -> int:
    parser = argparse.ArgumentParser(
        description="Run one fight, then attempt a second (must fail when DEBUG is not set)",
    )
    parser.add_argument(
        "--trainer-url",
        default=os.environ.get("MCP_TRAINER_URL", "http://localhost:7013"),
        help="MCP trainer URL",
    )
    parser.add_argument(
        "--arena-url",
        default=os.environ.get("MCP_ARENA_URL", "http://localhost:7014"),
        help="MCP arena URL",
    )
    parser.add_argument(
        "--no-up",
        action="store_true",
        help="Do not bring up services; assume they are already running",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent

    if not args.no_up:
        if not (challenge_dir / ".env").exists() and (challenge_dir / "env.example").exists():
            shutil.copy(challenge_dir / "env.example", challenge_dir / ".env")
        if not _ensure_services(challenge_dir):
            return 1

    trainer_rpc = args.trainer_url.rstrip("/") + "/rpc"
    arena_rpc = args.arena_url.rstrip("/") + "/rpc"

    try:
        print("[test_onefight] Fight 1: starting...")
        won = run_one_fight(arena_rpc, trainer_rpc)
        print(f"[test_onefight] Fight 1: {'VICTORY' if won else 'DEFEAT'}")

        print("[test_onefight] Fight 2: attempting (should fail)...")
        res = jsonrpc(arena_rpc, "tools/call", {"name": "fight", "arguments": {}})
        if "error" not in res:
            print("[test_onefight] FAIL - second fight should have been rejected", file=sys.stderr)
            return 1
        err_msg = res["error"].get("message", "")
        if "Only one fight allowed" not in err_msg and "already been completed" not in err_msg:
            print(f"[test_onefight] FAIL - unexpected error: {err_msg}", file=sys.stderr)
            return 1
        print(f"[test_onefight] Fight 2: correctly rejected ({err_msg})")
        print("[test_onefight] OK")
        return 0

    except Exception as e:
        print(f"[test_onefight] FAIL - {e}", file=sys.stderr)
        return 1


def _ensure_services(challenge_dir: Path) -> bool:
    """Bring up datastore, mcp_trainer, mcp_arena. Do NOT set DEBUG."""
    print("[test_onefight] Starting datastore, mcp_trainer, mcp_arena (DEBUG not set)...")
    env = os.environ.copy()
    env["DEBUG"] = ""  # Ensure DEBUG is not set for single-fight mode
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "--build", "datastore", "mcp_trainer", "mcp_arena"],
        cwd=challenge_dir,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        print(f"[test_onefight] docker compose up failed: {result.stderr}", file=sys.stderr)
        return False

    for port, name in [(7013, "mcp_trainer"), (7014, "mcp_arena")]:
        for i in range(60):
            try:
                req = urllib.request.Request(f"http://localhost:{port}/healthz", method="GET")
                with urllib.request.urlopen(req, timeout=5) as _:
                    break
            except Exception:
                time.sleep(1)
        else:
            print(f"[test_onefight] Timed out waiting for {name}", file=sys.stderr)
            return False

    return True


if __name__ == "__main__":
    sys.exit(run())
