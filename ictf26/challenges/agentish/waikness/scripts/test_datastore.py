#!/usr/bin/env python3
"""Bring up the datastore and print its configuration (sentence and chosen challenges)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def run_capture(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), env=env, text=True, capture_output=True, check=False)


def wait_for_config(*, challenge_dir: Path, env: dict[str, str], timeout_s: int = 90) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        cp = run_capture(
            [
                "docker", "compose", "exec", "-T", "datastore",
                "redis-cli", "-h", "127.0.0.1", "-p", "6379", "EXISTS", "waikness:config",
            ],
            cwd=challenge_dir,
            env=env,
        )
        if cp.returncode == 0 and cp.stdout.strip() == "1":
            return True
        time.sleep(1)
    return False


def redis_hgetall(challenge_dir: Path, env: dict[str, str], key: str) -> dict[str, str]:
    cp = run_capture(
        ["docker", "compose", "exec", "-T", "datastore", "redis-cli", "-h", "127.0.0.1", "-p", "6379", "HGETALL", key],
        cwd=challenge_dir,
        env=env,
    )
    if cp.returncode != 0:
        raise RuntimeError(f"redis-cli failed: {cp.stderr}")
    # HGETALL returns alternating key, value lines
    lines = cp.stdout.strip().splitlines()
    return dict(zip(lines[::2], lines[1::2])) if lines else {}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Bring up datastore and print configuration")
    parser.add_argument("--keep", action="store_true", help="Keep containers running after (no down -v)")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent

    dotenv = challenge_dir / ".env"
    if not dotenv.exists():
        ex = challenge_dir / "env.example"
        if ex.exists():
            shutil.copyfile(ex, dotenv)
            print("[test_datastore.py] Created .env from env.example", file=sys.stderr)
        else:
            print("[test_datastore.py] ERROR: .env not found", file=sys.stderr)
            return 1

    env = os.environ.copy()

    def cleanup() -> None:
        if args.keep:
            return
        subprocess.run(
            ["docker", "compose", "down", "-v", "--remove-orphans"],
            cwd=str(challenge_dir),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    try:
        print("[test_datastore.py] Starting litellm and datastore...")
        cp = subprocess.run(
            ["docker", "compose", "--profile", "debug", "up", "-d", "--build", "litellm", "datastore"],
            cwd=str(challenge_dir),
            env=env,
            text=True,
            check=False,
        )
        if cp.returncode != 0:
            print(f"[test_datastore.py] FAIL: docker compose up exited {cp.returncode}", file=sys.stderr)
            return cp.returncode

        print("[test_datastore.py] Waiting for waikness:config...")
        if not wait_for_config(challenge_dir=challenge_dir, env=env, timeout_s=90):
            print("[test_datastore.py] ERROR: timeout waiting for config", file=sys.stderr)
            return 1

        cfg = redis_hgetall(challenge_dir, env, "waikness:config")
        sentence = cfg.get("sentence", "")
        challenges_json = cfg.get("challenges_json", "[]")
        created_at = cfg.get("created_at", "")

        print()
        print("=== Waikness Datastore Configuration ===")
        print()
        print("Sentence:", sentence)
        print()
        print("Challenges:")
        for ch in json.loads(challenges_json):
            print(f"  ID {ch['id']}: {ch['sample_id']} -> word={ch['word']!r} (failure_prob={ch['failure_prob']:.4f})")
        print()
        if created_at:
            print("Created at:", created_at)
        print()
        return 0
    finally:
        print("[test_datastore.py] Cleaning up...")
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
