#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def _clean_env_value(v: str) -> str:
    return v.split("#", 1)[0].strip()


def _read_dotenv_value(dotenv_path: Path, key: str) -> str | None:
    if not dotenv_path.exists():
        return None
    prefix = key + "="
    for raw in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or not line.startswith(prefix):
            continue
        return _clean_env_value(line[len(prefix) :])
    return None


def run_capture(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def http_wait_ok(url: str, *, headers: dict[str, str] | None = None, timeout_s: int = 60) -> None:
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout_s
    last: tuple[int, str] | None = None
    hdrs = dict(headers or {})
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url, method="GET", headers=hdrs)
            with urllib.request.urlopen(req, timeout=10) as resp:  # nosec - local test only
                body = resp.read().decode("utf-8", errors="replace")
                last = (int(resp.status), body)
                if resp.status == 200:
                    return
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
            last = (int(getattr(e, "code", 0) or 0), body)
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError(f"Timed out waiting for HTTP 200: {url} (last={last})")


def wait_for_datastore_config(*, challenge_dir: Path, env: dict[str, str], timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        cp = run_capture(
            ["docker", "compose", "exec", "-T", "datastore", "redis-cli", "-h", "127.0.0.1", "-p", "6379", "EXISTS", "waldo:config"],
            cwd=challenge_dir,
            env=env,
        )
        if cp.returncode == 0 and cp.stdout.strip() == "1":
            return
        time.sleep(1)
    raise TimeoutError("Timed out waiting for waldo:config to appear in datastore redis.")


def ensure_dotenv_exists(challenge_dir: Path) -> None:
    dotenv = challenge_dir / ".env"
    if dotenv.exists():
        return
    ex = challenge_dir / "env.example"
    if not ex.exists():
        raise SystemExit("[test_solve.py] ERROR: .env not found and env.example missing.")
    shutil.copyfile(ex, dotenv)
    print("[test_solve.py] Created .env from env.example; edit .env (e.g. set LITELLM_API_KEY) if needed.", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bring up where-is-waldo infra and run the sandbox solver.")
    parser.add_argument("--no-build", action="store_true", help="Skip image builds (faster if already built).")
    parser.add_argument("--keep", action="store_true", help="Keep containers running after completion (no down -v).")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent

    ensure_dotenv_exists(challenge_dir)

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
        up_deps = ["docker", "compose", "up", "-d"]
        if not args.no_build:
            up_deps.append("--build")
        up_deps += ["litellm", "langfuse", "datastore", "mcp_landmarks", "mcp_flag"]

        print("[test_solve.py] Starting dependencies...")
        cp = subprocess.run(up_deps, cwd=str(challenge_dir), env=env, text=True, check=False)
        if cp.returncode != 0:
            print(f"[test_solve.py] FAIL: docker compose up deps exited {cp.returncode}", file=sys.stderr)
            logs = run_capture(["docker", "compose", "logs", "--tail=250"], cwd=challenge_dir, env=env)
            if logs.stdout.strip():
                print("\n[test_solve.py] compose logs (tail):\n" + logs.stdout, file=sys.stderr)
            if logs.stderr.strip():
                print("\n[test_solve.py] compose logs (stderr):\n" + logs.stderr, file=sys.stderr)
            return cp.returncode

        team_key = _read_dotenv_value(challenge_dir / ".env", "TEAM_LITELLM_API_KEY") or ""
        if not team_key.strip():
            raise SystemExit("[test_solve.py] ERROR: TEAM_LITELLM_API_KEY is empty in .env")

        print("[test_solve.py] Waiting for litellm /v1/models (authenticated)...")
        http_wait_ok(
            "http://localhost:4000/v1/models",
            headers={"Authorization": f"Bearer {team_key}"},
            timeout_s=60,
        )
        print("[test_solve.py] Waiting for MCP health endpoints...")
        http_wait_ok("http://localhost:7001/healthz", timeout_s=60)
        http_wait_ok("http://localhost:7002/healthz", timeout_s=60)

        print("[test_solve.py] Waiting for waldo config in datastore...")
        wait_for_datastore_config(challenge_dir=challenge_dir, env=env, timeout_s=60)

        print("[test_solve.py] Running sandbox; it will execute writeup/solve.py")
        run_sandbox = ["docker", "compose", "run", "--rm", "sandbox"]
        cp2 = subprocess.run(run_sandbox, cwd=str(challenge_dir), env=env, text=True, check=False)
        if cp2.returncode == 0:
            print("[test_solve.py] PASS: sandbox exited 0")
            return 0

        print(f"[test_solve.py] FAIL: sandbox exited {cp2.returncode}", file=sys.stderr)
        logs = run_capture(["docker", "compose", "logs", "--tail=250"], cwd=challenge_dir, env=env)
        if logs.stdout.strip():
            print("\n[test_solve.py] compose logs (tail):\n" + logs.stdout, file=sys.stderr)
        if logs.stderr.strip():
            print("\n[test_solve.py] compose logs (stderr):\n" + logs.stderr, file=sys.stderr)
        return cp2.returncode
    finally:
        print("[test_solve.py] Cleaning up...")
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

