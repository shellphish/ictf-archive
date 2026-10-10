#!/usr/bin/env python3
"""
Runs 10 fights per strategy and prints success rates.

Modes:
  - random: random attack when counter-attacking
  - efficacy: attack with highest damage * success_rate
  - strategy: attack with highest damage * success_rate * (1 - opp_defense_rate)

Usage:
  python scripts/test_multifight.py [--combatant-damage 25] [--opponent-damage 65] [--fights 10] [--trainer-url URL] [--arena-url URL] [--no-up]
"""
import argparse
import json
import os
import random
import secrets
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ATTACKS = ["punch", "kick", "sweep", "elbow", "headbutt"]
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
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data


def run_fight(
    arena_rpc: str,
    attack_choice_fn: callable,
) -> bool:
    """Run one fight. attack_choice_fn() returns the attack to use when counter-attacking.
    Returns True if combatant wins, False otherwise."""
    res = jsonrpc(arena_rpc, "tools/call", {"name": "fight", "arguments": {}})
    fight_id = res["result"]["fight_id"]

    while True:
        res = jsonrpc(arena_rpc, "tools/call", {"name": "status", "arguments": {"fight_id": fight_id}})
        result = res["result"]
        combatant_hp = result["combatant_health"]
        opponent_hp = result["opponent_health"]

        if opponent_hp <= 0:
            return True
        if combatant_hp <= 0:
            return False

        res = jsonrpc(arena_rpc, "tools/call", {"name": "action", "arguments": {"fight_id": fight_id}})
        result = res["result"]
        step_id = result["step"]
        action_val = result.get("action", "")

        if result.get("game_over"):
            return False

        opponent_missed = not result.get("success", True)
        if opponent_missed:
            reaction_val = attack_choice_fn()
        else:
            reaction_val = DEFENSE_FOR_ATTACK.get(action_val, "block")

        jsonrpc(
            arena_rpc,
            "tools/call",
            {"name": "reaction", "arguments": {"fight_id": fight_id, "step_id": step_id, "action": reaction_val}},
        )


def run() -> int:
    parser = argparse.ArgumentParser(
        description="Run 10 fights per strategy and print success rates",
    )
    parser.add_argument(
        "--combatant-damage",
        type=int,
        default=25,
        help="Total damage of combatant (default: 25)",
    )
    parser.add_argument(
        "--opponent-damage",
        type=int,
        default=50,
        help="Total damage of opponent (default: 50)",
    )
    parser.add_argument(
        "--fights",
        type=int,
        default=10,
        help="Number of fights per strategy (default: 10)",
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

    num_fights = args.fights

    if not args.no_up:
        if not (challenge_dir / ".env").exists() and (challenge_dir / "env.example").exists():
            shutil.copy(challenge_dir / "env.example", challenge_dir / ".env")
        if not _ensure_services(challenge_dir, args.combatant_damage, args.opponent_damage):
            return 1

    trainer_rpc = args.trainer_url.rstrip("/") + "/rpc"
    arena_rpc = args.arena_url.rstrip("/") + "/rpc"

    try:
        # 1. Training
        print("[test_multifight] Training...")
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

        # 2. Get combatant and opponent stats
        res = jsonrpc(trainer_rpc, "tools/call", {"name": "assessment", "arguments": {"training_id": training_id}})
        combatant = res["result"].get("combatant_1", {})

        res = jsonrpc(trainer_rpc, "tools/call", {"name": "opponents", "arguments": {"training_id": training_id}})
        opponent = res["result"].get("opponent_1", {})

        # Best efficacy: highest damage * success_rate
        best_efficacy_attack = "punch"
        best_efficacy = 0.0
        for attack, data in combatant.get("attacks", {}).items():
            efficacy = data.get("damage", 0) * data.get("success_rate", 0)
            if efficacy > best_efficacy:
                best_efficacy = efficacy
                best_efficacy_attack = attack

        # Best strategy: damage * success_rate * (1 - opp_defense_rate)
        # Powerful attack that is seldom blocked
        best_strategy_attack = "punch"
        best_expected = 0.0
        combatant_attacks = combatant["attacks"]
        opp_defenses = opponent["defenses"]
        for attack in ATTACKS:
            atk_data = combatant_attacks[attack]
            defense = DEFENSE_FOR_ATTACK[attack]
            opp_def = opp_defenses[defense]
            expected = (
                atk_data["damage"]
                * atk_data["success_rate"]
                * (1 - opp_def["success_rate"])
            )
            if expected > best_expected:
                best_expected = expected
                best_strategy_attack = attack

        print(f"[test_multifight] Combatant total damage: {args.combatant_damage}, Opponent: {args.opponent_damage}")
        print(f"[test_multifight] Running {num_fights} fights per strategy...")
        print(f"  Efficacy: best attack = {best_efficacy_attack}")
        print(f"  Strategy: best attack = {best_strategy_attack} (powerful, seldom blocked)")

        results = {}

        # Mode 1: random
        wins = sum(
            run_fight(arena_rpc, lambda: random.choice(ATTACKS))
            for _ in range(num_fights)
        )
        results["random"] = wins / num_fights
        print(f"  random: {wins}/{num_fights}")

        # Mode 2: efficacy
        best_eff = best_efficacy_attack
        wins = sum(
            run_fight(arena_rpc, lambda: best_eff)
            for _ in range(num_fights)
        )
        results["efficacy"] = wins / num_fights
        print(f"  efficacy: {wins}/{num_fights}")

        # Mode 3: strategy
        best_strat = best_strategy_attack
        wins = sum(
            run_fight(arena_rpc, lambda: best_strat)
            for _ in range(num_fights)
        )
        results["strategy"] = wins / num_fights
        print(f"  strategy: {wins}/{num_fights}")

        print()
        print("[test_multifight] Success rates:")
        print(f"  random:   {results['random']:.1%}")
        print(f"  efficacy: {results['efficacy']:.1%}")
        print(f"  strategy: {results['strategy']:.1%}")

        return 0

    except Exception as e:
        print(f"[test_multifight] FAIL - {e}", file=sys.stderr)
        return 1


def _ensure_services(
    challenge_dir: Path,
    combatant_damage: int = 25,
    opponent_damage: int = 65,
) -> bool:
    """Bring up datastore, mcp_trainer, mcp_arena. Returns True on success."""
    print("[test_multifight] Starting datastore, mcp_trainer, mcp_arena...")
    env = os.environ.copy()
    env["COMBATANT_TOTAL_DAMAGE"] = str(combatant_damage)
    env["OPPONENT_TOTAL_DAMAGE"] = str(opponent_damage)
    env["INIT_SEED"] = secrets.token_hex(16)
    env["DEBUG"] = "1"  # Allow multiple fights for modeling
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "--build", "datastore", "mcp_trainer", "mcp_arena"],
        cwd=challenge_dir,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        print(f"[test_multifight] docker compose up failed: {result.stderr}", file=sys.stderr)
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
            print(f"[test_multifight] Timed out waiting for {name}", file=sys.stderr)
            return False

    return True


if __name__ == "__main__":
    sys.exit(run())
