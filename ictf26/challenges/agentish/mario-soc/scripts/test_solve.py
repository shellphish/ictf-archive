#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=False,  # stream directly
        check=check,
    )


def run_capture(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Bring up mario-soc infra and run the sandbox solver.")
    parser.add_argument("--no-build", action="store_true", help="Skip image builds (faster if already built).")
    parser.add_argument("--keep", action="store_true", help="Keep containers running after completion (no down -v).")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent

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
            text=True,
            check=False,
        )

    try:
        up_cmd = ["docker", "compose", "up", "--abort-on-container-exit", "--exit-code-from", "sandbox"]
        if not args.no_build:
            up_cmd.insert(3, "--build")

        print("[test_solve.py] Running full stack; sandbox will execute writeup/solve.py")
        cp = subprocess.run(up_cmd, cwd=str(challenge_dir), env=env, text=True, check=False)
        if cp.returncode == 0:
            print("[test_solve.py] PASS: sandbox exited 0")
            return 0

        print(f"[test_solve.py] FAIL: sandbox exited {cp.returncode}", file=sys.stderr)
        logs = run_capture(["docker", "compose", "logs", "--tail=250"], cwd=challenge_dir, env=env)
        if logs.stdout.strip():
            print("\n[test_solve.py] compose logs (tail):\n" + logs.stdout, file=sys.stderr)
        if logs.stderr.strip():
            print("\n[test_solve.py] compose logs (stderr):\n" + logs.stderr, file=sys.stderr)
        return cp.returncode
    finally:
        print("[test_solve.py] Cleaning up...")
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

