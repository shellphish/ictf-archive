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
        res = jsonrpc(trainer_rpc, "tools/call", {"name": "action", "arguments": {"training_id": training_id}})
        result = res["result"]
        if result.get("action") == "trained":
            break
        step_id = result["step"]
        attack = result["attack"]
        defense = DEFENSE_FOR_ATTACK[attack]
        jsonrpc(
            trainer_rpc,
            "tools/call",
            {"name": "reaction", "arguments": {"training_id": training_id, "step_id": step_id, "reaction": defense}},
        )

    res = jsonrpc(trainer_rpc, "tools/call", {"name": "assessment", "arguments": {"training_id": training_id}})
    combatant = res["result"].get("combatant", {})
    best_attack = "punch"
    best_expected = 0.0
    for attack, data in combatant.get("attacks", {}).items():
        expected = data.get("damage", 0) * data.get("success_rate", 0)
        if expected > best_expected:
            best_expected = expected
            best_attack = attack

    res = jsonrpc(arena_rpc, "tools/call", {"name": "fight", "arguments": {}})
    fight_id = res["result"]["fight_id"]

    while True:
        res = jsonrpc(arena_rpc, "tools/call", {"name": "arena_status", "arguments": {"fight_id": fight_id}})
        result = res["result"]
        combatant_hp = result["combatant_health"]
        opponent_hp = result["opponent_health"]

        if opponent_hp <= 0:
            return True
        if combatant_hp <= 0:
            return False

        res = jsonrpc(arena_rpc, "tools/call", {"name": "arena_action", "arguments": {"fight_id": fight_id}})
        result = res["result"]
        step_id = result["step"]
        action_val = result.get("action", "")

        if result.get("game_over"):
            return False

        opponent_missed = not result.get("success", True)
        reaction_val = best_attack if opponent_missed else DEFENSE_FOR_ATTACK.get(action_val, "block")

        jsonrpc(
            arena_rpc,
            "tools/call",
            {"name": "arena_reaction", "arguments": {"fight_id": fight_id, "step_id": step_id, "action": reaction_val}},
        )


def run() -> int:
    parser = argparse.ArgumentParser(
        description="Run one fight, then attempt a second (must fail when DEBUG is not set)",
    )
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

    for port, name in [(7011, "mcp_trainer"), (7012, "mcp_arena")]:
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
