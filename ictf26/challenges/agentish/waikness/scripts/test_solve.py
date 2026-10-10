#!/usr/bin/env python3
"""
Bring up all waikness components (litellm, datastore, mcp_challenges, mcp_flag),
then run writeup/solve.py and capture the flag.
"""
from __future__ import annotations

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


def http_wait_ok(url: str, timeout_s: int = 60) -> None:
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError(f"Timed out waiting for HTTP 200: {url}")


def load_dotenv(dotenv_path: Path) -> dict[str, str]:
    """Load KEY=value pairs from .env file into env dict."""
    result: dict[str, str] = {}
    if not dotenv_path.exists():
        return result
    for raw in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            result[key.strip()] = val.split("#", 1)[0].strip()
    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Bring up waikness and run solve.py to get the flag")
    parser.add_argument("--keep", action="store_true", help="Keep containers running after")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent
    solve_path = challenge_dir / "writeup" / "solve.py"
    venv_python = challenge_dir / ".venv" / "bin" / "python"

    if not solve_path.exists():
        print(f"[test_solve.py] ERROR: {solve_path} not found", file=sys.stderr)
        return 1

    dotenv = challenge_dir / ".env"
    if not dotenv.exists():
        ex = challenge_dir / "env.example"
        if ex.exists():
            shutil.copyfile(ex, dotenv)
            print("[test_solve.py] Created .env from env.example", file=sys.stderr)
        else:
            print("[test_solve.py] ERROR: .env not found", file=sys.stderr)
            return 1

    env = os.environ.copy()
    env.update(load_dotenv(dotenv))
    # Override for running solve.py from host (not inside Docker)
    env["MCP_CHALLENGES_URL"] = "http://localhost:7001"
    env["MCP_FLAG_URL"] = "http://localhost:7002"
    env["LITELLM_BASE_URL"] = "http://localhost:4000"
    if not env.get("TEAM_LITELLM_API_KEY") and env.get("CHALLENGE_LITELLM_API_KEY"):
        env["TEAM_LITELLM_API_KEY"] = env["CHALLENGE_LITELLM_API_KEY"]

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
        print("[test_solve.py] Starting litellm, datastore, mcp_challenges, mcp_flag...")
        cp = subprocess.run(
            [
                "docker", "compose", "--profile", "debug", "up", "-d", "--build",
                "litellm", "datastore", "mcp_challenges", "mcp_flag",
            ],
            cwd=str(challenge_dir),
            env=env,
            text=True,
            check=False,
        )
        if cp.returncode != 0:
            print(f"[test_solve.py] FAIL: docker compose up exited {cp.returncode}", file=sys.stderr)
            return cp.returncode

        print("[test_solve.py] Waiting for waikness:config...")
        if not wait_for_config(challenge_dir=challenge_dir, env=env, timeout_s=90):
            print("[test_solve.py] ERROR: timeout waiting for config", file=sys.stderr)
            return 1

        print("[test_solve.py] Waiting for MCP health...")
        http_wait_ok("http://localhost:7001/healthz", timeout_s=30)
        http_wait_ok("http://localhost:7002/healthz", timeout_s=30)

        print("[test_solve.py] Running writeup/solve.py...")
        python_exe = str(venv_python) if venv_python.exists() else sys.executable
        cp2 = subprocess.run(
            [python_exe, str(solve_path)],
            cwd=str(challenge_dir),
            env=env,
            text=True,
            capture_output=False,
        )

        if cp2.returncode != 0:
            print(f"[test_solve.py] FAIL: solve.py exited {cp2.returncode}", file=sys.stderr)
            return cp2.returncode

        print("[test_solve.py] PASS")
        return 0
    finally:
        print("[test_solve.py] Cleaning up...")
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
