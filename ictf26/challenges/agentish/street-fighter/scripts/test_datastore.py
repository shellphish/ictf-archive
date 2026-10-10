#!/usr/bin/env python3
"""
Brings up the datastore and prints the Street Fighter configuration (combatant + opponent).

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

combatant = json.loads(cfg.get("combatant_json", "{}"))
opponent = json.loads(cfg.get("opponent_json", "{}"))

ATTACKS = ["punch", "kick", "sweep", "elbow", "headbutt"]
DEFENSE_FOR_ATTACK = {"punch": "parry", "kick": "block", "sweep": "jump", "elbow": "sidestep", "headbutt": "brace"}
combatant_attacks = combatant["attacks"]
opp_defenses = opponent["defenses"]

# Efficacy: highest damage * success_rate
best_efficacy = "punch"
best_efficacy_val = 0.0
for a in ATTACKS:
    d = combatant_attacks[a]
    v = d["damage"] * d["success_rate"]
    if v > best_efficacy_val:
        best_efficacy_val = v
        best_efficacy = a

# Strategy: highest damage * success_rate * (1 - opp_defense_rate)
best_strategy = "punch"
best_strategy_val = 0.0
for a in ATTACKS:
    atk = combatant_attacks[a]
    def_name = DEFENSE_FOR_ATTACK[a]
    opp_def = opp_defenses[def_name]
    rate = 1 - opp_def["success_rate"]
    v = atk["damage"] * atk["success_rate"] * rate
    if v > best_strategy_val:
        best_strategy_val = v
        best_strategy = a

print("COMBATANT")
print(json.dumps(combatant, indent=2))
print()
print("OPPONENT")
print(json.dumps(opponent, indent=2))
print()

# Efficacy attack details
eff_atk = combatant_attacks[best_efficacy]
eff_def_name = DEFENSE_FOR_ATTACK[best_efficacy]
eff_opp_def_rate = opp_defenses[eff_def_name]["success_rate"]
eff_product = eff_atk["damage"] * eff_atk["success_rate"]
eff_strategy_val = eff_product * (1 - eff_opp_def_rate)
print("EFFICACY ATTACK:", best_efficacy)
print("  damage:", eff_atk["damage"])
print("  success_rate:", eff_atk["success_rate"])
print("  product (damage * success_rate):", eff_product)
print("  opponent defense rate:", eff_opp_def_rate)
print("  strategy value (product * (1 - opp_defense)):", eff_strategy_val)
print()

# Strategy attack details
strat_atk = combatant_attacks[best_strategy]
strat_def_name = DEFENSE_FOR_ATTACK[best_strategy]
strat_opp_def_rate = opp_defenses[strat_def_name]["success_rate"]
strat_product = strat_atk["damage"] * strat_atk["success_rate"]
strat_strategy_val = strat_product * (1 - strat_opp_def_rate)
print("STRATEGY ATTACK:", best_strategy)
print("  damage:", strat_atk["damage"])
print("  success_rate:", strat_atk["success_rate"])
print("  product (damage * success_rate):", strat_product)
print("  opponent defense rate:", strat_opp_def_rate)
print("  strategy value (product * (1 - opp_defense)):", strat_strategy_val)
print()
product_diff = eff_product - strat_product
divergency_factor = (strat_strategy_val - eff_strategy_val) / product_diff if product_diff != 0 else float("nan")
print("DIVERGENCY FACTOR: (strategy_val_strategy - strategy_val_efficacy) / (efficacy_product - strategy_product) =", divergency_factor)
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
