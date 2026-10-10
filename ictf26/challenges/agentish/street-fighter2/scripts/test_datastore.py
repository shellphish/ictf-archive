#!/usr/bin/env python3
"""
Brings up the datastore and prints the Street Fighter 2 configuration
(combatant_1, combatant_2, opponent_1, opponent_2, combos).

Usage:
  python scripts/test_datastore.py
  # or from challenge root:
  python -m scripts.test_datastore
"""
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path


def log(msg: str) -> None:
    print(f"[test_datastore] {msg}", file=sys.stderr)


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent

    # Ensure .env exists
    env_path = challenge_dir / ".env"
    env_example = challenge_dir / "env.example"
    if not env_path.exists():
        if env_example.exists():
            shutil.copy(env_example, env_path)
            log("Created .env from env.example")
        else:
            log("ERROR: .env not found. Create it from env.example.")
            return 1

    def cleanup() -> None:
        subprocess.run(
            ["docker", "compose", "down", "-v"],
            cwd=challenge_dir,
            capture_output=True,
        )

    try:
        log("Starting datastore (clean slate)...")
        # Ensure clean slate so we get fresh random config each run
        subprocess.run(
            ["docker", "compose", "down", "-v"],
            cwd=challenge_dir,
            capture_output=True,
        )
        # Remove leftover run containers so exec targets the main (up) container
        result = subprocess.run(
            ["docker", "ps", "-aq", "--filter", "name=datastore-run"],
            cwd=challenge_dir,
            capture_output=True,
            text=True,
        )
        for cid in (result.stdout or "").strip().splitlines():
            if cid:
                subprocess.run(["docker", "rm", "-f", cid], capture_output=True)
        result = subprocess.run(
            ["docker", "compose", "up", "-d", "--build", "--force-recreate", "datastore"],
            cwd=challenge_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            log(f"docker compose up failed: {result.stderr}")
            return 1

        log("Waiting for sf:config to appear in redis...")
        for i in range(60):
            result = subprocess.run(
                [
                    "docker", "compose", "exec", "-T", "datastore",
                    "redis-cli", "-h", "127.0.0.1", "-p", "6379", "EXISTS", "sf:config",
                ],
                cwd=challenge_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip() == "1":
                break
            time.sleep(1)
        else:
            log("ERROR: sf:config did not appear in redis within timeout.")
            result = subprocess.run(
                ["docker", "compose", "logs", "--tail=200", "datastore"],
                cwd=challenge_dir,
                capture_output=True,
                text=True,
            )
            log("datastore logs (tail):")
            print(result.stdout or result.stderr, file=sys.stderr)
            return 1

        # Re-run init with fresh seed so each test_datastore run gets different values.
        # Use exec into the main container (not run containers which may use stale images).
        init_seed = secrets.token_hex(16)
        init_result = subprocess.run(
            [
                "docker", "compose", "exec", "-T", "-e", f"INIT_SEED={init_seed}",
                "datastore", "python3", "/app/init.py",
            ],
            cwd=challenge_dir,
            capture_output=True,
            text=True,
        )
        if init_result.stdout:
            print(init_result.stdout, end="" if init_result.stdout.endswith("\n") else "\n")
        if init_result.stderr:
            print(init_result.stderr, end="" if init_result.stderr.endswith("\n") else "\n", file=sys.stderr)

        log("Configuration:")
        print("---")
        result = subprocess.run(
            [
                "docker", "compose", "exec", "-T", "datastore",
                "python3", "-c",
                """
import json
import redis

r = redis.Redis.from_url("redis://127.0.0.1:6379/0", decode_responses=True)
cfg = r.hgetall("sf:config")
if not cfg:
    raise SystemExit("sf:config not found")

combatant_1 = json.loads(cfg.get("combatant_1_json", "{}"))
combatant_2 = json.loads(cfg.get("combatant_2_json", "{}"))
opponent_1 = json.loads(cfg.get("opponent_1_json", "{}"))
opponent_2 = json.loads(cfg.get("opponent_2_json", "{}"))
opponent_combo_vulnerability = json.loads(cfg.get("opponent_combo_vulnerability_json", "[]"))
combatant_combo_attack = json.loads(cfg.get("combatant_combo_attack_json", "[]"))
combatant_combo_vulnerability = json.loads(cfg.get("combatant_combo_vulnerability_json", "[]"))
opponent_combo_attack = json.loads(cfg.get("opponent_combo_attack_json", "[]"))

print("COMBATANT 1:", combatant_1.get("name", "?"), "-", combatant_1.get("description", ""))
print(json.dumps(combatant_1, indent=2))
print()
print("COMBATANT 2:", combatant_2.get("name", "?"), "-", combatant_2.get("description", ""))
print(json.dumps(combatant_2, indent=2))
print()
print("OPPONENT 1:", opponent_1.get("name", "?"), "-", opponent_1.get("description", ""))
print(json.dumps(opponent_1, indent=2))
print()
print("OPPONENT 2:", opponent_2.get("name", "?"), "-", opponent_2.get("description", ""))
print(json.dumps(opponent_2, indent=2))
print()
print("COMBOS")
print("  opponent_combo_vulnerability (opponents do):", opponent_combo_vulnerability)
print("  combatant_combo_attack (combatants do for instant win):", combatant_combo_attack)
print("  combatant_combo_vulnerability (AVOID):", combatant_combo_vulnerability)
print("  opponent_combo_attack (opponents use when we expose ourselves):", opponent_combo_attack)
""",
            ],
            cwd=challenge_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            log(f"Failed to read config: {result.stderr}")
            return 1
        print(result.stdout)
        print("---")
        return 0

    finally:
        cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
