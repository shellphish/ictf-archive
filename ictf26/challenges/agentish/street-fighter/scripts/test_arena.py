#!/usr/bin/env python3
"""
Performs a training session, then fights in the arena until victory or defeat.

Usage:
  python scripts/test_arena.py [--trainer-url URL] [--arena-url URL] [--no-up] [-v]
  # By default, brings up datastore, mcp_trainer, mcp_arena. Use --no-up if already running.
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
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data


def run() -> int:
    """Run training + fight. Returns 0 on victory, 1 on defeat or error."""
    parser = argparse.ArgumentParser(description="Train and fight in the arena until victory or defeat")
    parser.add_argument(
        "--trainer-url",
        default=os.environ.get("MCP_TRAINER_URL", "http://localhost:7011"),
        help="MCP trainer URL",
    )
    parser.add_argument(
        "--arena-url",
        default=os.environ.get("MCP_ARENA_URL", "http://localhost:7012"),
        help="MCP arena URL",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print details for each step",
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
        # 1. Training
        print("[test_arena] Training...")
        res = jsonrpc(trainer_rpc, "tools/call", {"name": "train", "arguments": {}})
        training_id = res["result"]["training_id"]
        if args.verbose:
            print(f"  training_id={training_id}")

        while True:
            res = jsonrpc(trainer_rpc, "tools/call", {"name": "action", "arguments": {"training_id": training_id}})
            result = res["result"]
            if result.get("action") == "trained":
                break
            step_id = result["step"]
            attack = result["attack"]
            defense = DEFENSE_FOR_ATTACK[attack]
            if args.verbose:
                print(f"  Step {step_id}: {attack} -> {defense}")
            res = jsonrpc(
                trainer_rpc,
                "tools/call",
                {"name": "reaction", "arguments": {"training_id": training_id, "step_id": step_id, "reaction": defense}},
            )
            if not res["result"].get("ok", False):
                print(f"[test_arena] FAIL - training reaction rejected: {res['result']}", file=sys.stderr)
                return 1
            if res["result"].get("action") == "trained":
                break

        print("[test_arena] Training complete.")

        # 2. Assessment and opponent
        res = jsonrpc(trainer_rpc, "tools/call", {"name": "assessment", "arguments": {"training_id": training_id}})
        combatant = res["result"].get("combatant", {})

        res = jsonrpc(trainer_rpc, "tools/call", {"name": "opponent", "arguments": {"training_id": training_id}})
        opponent = res["result"].get("opponent", {})

        best_attack = "punch"
        best_expected = 0.0
        for attack, data in combatant.get("attacks", {}).items():
            expected = data.get("damage", 0) * data.get("success_rate", 0)
            if expected > best_expected:
                best_expected = expected
                best_attack = attack

        if args.verbose:
            print(f"  Best attack: {best_attack} (expected dmg={best_expected:.1f})")
            print(f"  Opponent: {opponent.get('name', '?')}")

        # 3. Start fight
        print("[test_arena] Starting fight...")
        res = jsonrpc(arena_rpc, "tools/call", {"name": "fight", "arguments": {}})
        fight_id = res["result"]["fight_id"]
        if args.verbose:
            print(f"  fight_id={fight_id}")

        # 4. Fight loop
        step_count = 0
        while True:
            res = jsonrpc(arena_rpc, "tools/call", {"name": "arena_status", "arguments": {"fight_id": fight_id}})
            result = res["result"]
            combatant_hp = result["combatant_health"]
            opponent_hp = result["opponent_health"]

            if args.verbose or step_count % 10 == 0:
                print(f"  Status: Combatant={combatant_hp}, Opponent={opponent_hp}")

            if opponent_hp <= 0:
                print("[test_arena] VICTORY!")
                if "flag" in result:
                    print(f"  Flag: {result['flag']}")
                return 0
            if combatant_hp <= 0:
                print("[test_arena] DEFEAT - no flag, this time")
                return 1

            res = jsonrpc(arena_rpc, "tools/call", {"name": "arena_action", "arguments": {"fight_id": fight_id}})
            result = res["result"]
            step_id = result["step"]
            action_val = result.get("action", "")

            if result.get("game_over"):
                print(result["content"][0]["text"])
                return 1

            # action is always opponent attack; react with defense or counter-attack
            opponent_missed = not result.get("success", True)
            if opponent_missed:
                reaction_val = best_attack
                if args.verbose:
                    sr = result.get("success_rate", "?")
                    print(f"  Step {step_id}: opponent {action_val} missed (success_rate={sr}) -> counter-attacking with {reaction_val}")
            else:
                reaction_val = DEFENSE_FOR_ATTACK.get(action_val, "block")
                if args.verbose:
                    sr = result.get("success_rate", "?")
                    outcome = result.get("outcome", "?")
                    print(f"  Step {step_id}: opponent {action_val} (success_rate={sr}, outcome={outcome}) -> defending with {reaction_val}")

            reaction_res = jsonrpc(
                arena_rpc,
                "tools/call",
                {"name": "arena_reaction", "arguments": {"fight_id": fight_id, "step_id": step_id, "action": reaction_val}},
            )
            reaction_result = reaction_res["result"]

            if args.verbose:
                if "attack_success_rate" in reaction_result:
                    asr = reaction_result.get("attack_success_rate", "?")
                    ao = reaction_result.get("attack_outcome", "?")
                    dsr = reaction_result.get("defense_success_rate", "?")
                    do = reaction_result.get("defense_outcome", "?")
                    print(f"    counter-attack {reaction_val}: success_rate={asr}, outcome={ao}; opponent defense: success_rate={dsr}, outcome={do}")
                else:
                    sr = reaction_result.get("success_rate", "?")
                    outcome = reaction_result.get("outcome", "?")
                    print(f"    defense {reaction_val}: success_rate={sr}, outcome={outcome}")
            else:
                # Compact one-line summary of success_rate and outcome
                if "attack_success_rate" in reaction_result:
                    asr = reaction_result.get("attack_success_rate", "?")
                    ao = reaction_result.get("attack_outcome", "?")
                    dsr = reaction_result.get("defense_success_rate", "?")
                    do = reaction_result.get("defense_outcome", "?")
                    print(f"  Step {step_id}: counter {reaction_val} sr={asr} {ao}; opp_def sr={dsr} {do}")
                else:
                    sr = result.get("success_rate", "?")
                    outcome = result.get("outcome", "?")
                    dsr = reaction_result.get("success_rate", "?")
                    do = reaction_result.get("outcome", "?")
                    print(f"  Step {step_id}: opp {action_val} sr={sr} {outcome}; def {reaction_val} sr={dsr} {do}")

            step_count += 1

    except Exception as e:
        print(f"[test_arena] FAIL - {e}", file=sys.stderr)
        return 1


def _ensure_services(challenge_dir: Path) -> bool:
    """Bring up datastore, mcp_trainer, mcp_arena. Returns True on success."""
    print("[test_arena] Starting datastore, mcp_trainer, mcp_arena...")
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "--build", "datastore", "mcp_trainer", "mcp_arena"],
        cwd=challenge_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[test_arena] docker compose up failed: {result.stderr}", file=sys.stderr)
        return False

    for port, name in [(7011, "mcp_trainer"), (7012, "mcp_arena")]:
        for i in range(60):
            try:
                req = urllib.request.Request(f"http://localhost:{port}/healthz", method="GET")
                with urllib.request.urlopen(req, timeout=5) as _:
                    break
            except Exception:
                time.sleep(1)
        else:
            print(f"[test_arena] Timed out waiting for {name}", file=sys.stderr)
            return False

    return True


if __name__ == "__main__":
    sys.exit(run())
