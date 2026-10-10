#!/usr/bin/env python3
"""
Starts the MCP servers (datastore, mcp_trainer, mcp_arena) and runs writeup/solve.py via the sandbox to solve the challenge.

Usage:
  python scripts/test_challenge.py [--no-up]
  # Use --no-up if services are already running
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def run() -> int:
    parser = argparse.ArgumentParser(
        description="Start MCP servers and run writeup/solve.py to solve the challenge",
    )
    parser.add_argument(
        "--no-up",
        action="store_true",
        help="Do not bring up services; assume they are already running",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent
    solve_path = challenge_dir / "writeup" / "solve.py"

    if not solve_path.exists():
        print(f"[test_challenge] ERROR: {solve_path} not found", file=sys.stderr)
        return 1

    if not args.no_up:
        if not (challenge_dir / ".env").exists() and (challenge_dir / "env.example").exists():
            shutil.copy(challenge_dir / "env.example", challenge_dir / ".env")
        if not _ensure_services(challenge_dir):
            return 1

    print("[test_challenge] Running sandbox (writeup/solve.py)...")
    result = subprocess.run(
        ["docker", "compose", "run", "--rm", "sandbox"],
        cwd=challenge_dir,
    )
    return result.returncode


def _ensure_services(challenge_dir: Path) -> bool:
    """Bring up datastore, mcp_trainer, mcp_arena. Returns True on success."""
    print("[test_challenge] Starting datastore, mcp_trainer, mcp_arena...")
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "--build", "datastore", "mcp_trainer", "mcp_arena"],
        cwd=challenge_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[test_challenge] docker compose up failed: {result.stderr}", file=sys.stderr)
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
            print(f"[test_challenge] Timed out waiting for {name}", file=sys.stderr)
            return False

    print("[test_challenge] Waiting for sf:config in datastore...")
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
        print("[test_challenge] sf:config did not appear in datastore within timeout", file=sys.stderr)
        return False

    print("[test_challenge] Services ready.")
    return True


if __name__ == "__main__":
    sys.exit(run())
