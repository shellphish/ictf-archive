#!/usr/bin/env python3
"""
Simulates a series of training sessions against the MCP trainer.

Each session: train -> attack -> defense (until trained) -> assessment -> opponents.

Usage:
  python scripts/test_trainer.py [--sessions N] [--url URL] [--no-up]
  # Default: 3 sessions, http://localhost:7013
  # By default, brings up datastore and mcp_trainer. Use --no-up if already running.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFENSE_FOR_ATTACK = {
    "punch": "parry",
    "kick": "block",
    "sweep": "jump",
    "elbow": "sidestep",
    "headbutt": "brace",
}


def _print_profile(header: str, profile: dict, name: str | None) -> None:
    """Print full profile: attacks (damage, success_rate) and defenses (success_rate)."""
    print(header)
    if name:
        print(f"    name: {name}")
    if profile.get("description"):
        print(f"    description: {profile['description']}")
    print("    attacks (damage, success_rate):")
    for k, v in profile.get("attacks", {}).items():
        print(f"      {k}: damage={v.get('damage')}, success_rate={v.get('success_rate')}")
    print("    defenses (success_rate):")
    for k, v in profile.get("defenses", {}).items():
        print(f"      {k}: success_rate={v.get('success_rate')}")


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


def run_session(session_num: int, url: str, verbose: bool) -> bool:
    """Run one full training session. Returns True if successful."""
    rpc_url = url.rstrip("/") + "/rpc"

    try:
        # train
        res = jsonrpc(rpc_url, "tools/call", {"name": "train", "arguments": {}})
        training_id = res["result"]["training_id"]
        if verbose:
            print(f"  Session {session_num}: training_id={training_id}")

        # Correct defenses until trained (3-10 steps depending on session)
        while True:
            res = jsonrpc(
                rpc_url,
                "tools/call",
                {"name": "attack", "arguments": {"training_id": training_id}},
            )
            result = res["result"]
            if result.get("status") == "trained":
                break
            step_id = result["step"]
            attack = result["attack"]
            defense = DEFENSE_FOR_ATTACK[attack]

            res = jsonrpc(
                rpc_url,
                "tools/call",
                {
                    "name": "defense",
                    "arguments": {
                        "training_id": training_id,
                        "step_id": step_id,
                        "defense": defense,
                    },
                },
            )
            if not res["result"].get("ok", False):
                print(f"  Session {session_num}: FAIL - defense rejected: {res['result']}")
                return False
            if verbose:
                print(f"    Step {step_id}: {attack} -> {defense} ✓")
            if res["result"].get("status") == "trained":
                break

        # assessment (both combatants)
        res = jsonrpc(
            rpc_url,
            "tools/call",
            {"name": "assessment", "arguments": {"training_id": training_id}},
        )
        combatant_1 = res["result"].get("combatant_1", {})
        combatant_2 = res["result"].get("combatant_2", {})
        combatant_combo_attack = res["result"].get("combatant_combo_attack", [])
        combatant_combo_vulnerability = res["result"].get("combatant_combo_vulnerability", [])
        if verbose:
            _print_profile(f"  Session {session_num} COMBATANT 1", combatant_1, combatant_1.get("name"))
            _print_profile(f"  Session {session_num} COMBATANT 2", combatant_2, combatant_2.get("name"))
            print(f"  Session {session_num} COMBATANT COMBOS: attack={combatant_combo_attack}, vulnerability={combatant_combo_vulnerability}")

        # opponents (both opponents)
        res = jsonrpc(
            rpc_url,
            "tools/call",
            {"name": "opponents", "arguments": {"training_id": training_id}},
        )
        opponent_1 = res["result"].get("opponent_1", {})
        opponent_2 = res["result"].get("opponent_2", {})
        opponent_combo_vulnerability = res["result"].get("opponent_combo_vulnerability", [])
        opponent_combo_attack = res["result"].get("opponent_combo_attack", [])
        if verbose:
            _print_profile(f"  Session {session_num} OPPONENT 1", opponent_1, opponent_1.get("name"))
            _print_profile(f"  Session {session_num} OPPONENT 2", opponent_2, opponent_2.get("name"))
            print(f"  Session {session_num} OPPONENT COMBOS: vulnerability={opponent_combo_vulnerability}, attack={opponent_combo_attack}")

        return True

    except Exception as e:
        print(f"  Session {session_num}: FAIL - {e}")
        return False


def ensure_services(challenge_dir: Path) -> bool:
    """Bring up datastore and mcp_trainer, wait for ready. Returns True on success."""
    print("[test_trainer] Starting datastore and mcp_trainer...")
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "--build", "datastore", "mcp_trainer"],
        cwd=challenge_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[test_trainer] docker compose up failed: {result.stderr}", file=sys.stderr)
        return False

    # Wait for mcp_trainer healthz
    for i in range(60):
        try:
            req = urllib.request.Request("http://localhost:7013/healthz", method="GET")
            with urllib.request.urlopen(req, timeout=5) as _:
                return True
        except Exception:
            time.sleep(1)
    print("[test_trainer] Timed out waiting for mcp_trainer", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate training sessions against MCP trainer")
    parser.add_argument(
        "--sessions",
        type=int,
        default=1,
        help="Number of training sessions to run (default: 3)",
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("MCP_TRAINER_URL", "http://localhost:7013"),
        help="MCP trainer base URL (default: MCP_TRAINER_URL or http://localhost:7013)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print details for each step",
    )
    parser.add_argument(
        "--no-up",
        action="store_true",
        help="Do not bring up services; assume datastore and mcp_trainer are already running",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent

    if not args.no_up:
        if not (challenge_dir / ".env").exists() and (challenge_dir / "env.example").exists():
            shutil.copy(challenge_dir / "env.example", challenge_dir / ".env")
        if not ensure_services(challenge_dir):
            return 1

    print(f"[test_trainer] Running {args.sessions} training session(s) at {args.url}")
    passed = 0
    for i in range(1, args.sessions + 1):
        if run_session(i, args.url, args.verbose):
            passed += 1
            if not args.verbose:
                print(f"  Session {i}: OK")

    print(f"[test_trainer] {passed}/{args.sessions} sessions passed")
    return 0 if passed == args.sessions else 1


if __name__ == "__main__":
    sys.exit(main())
