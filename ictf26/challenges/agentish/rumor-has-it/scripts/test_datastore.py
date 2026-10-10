#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def _clean_env_value(v: str) -> str:
    return v.split("#", 1)[0].strip()


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = _clean_env_value(v)
        if k:
            out[k] = v
    return out


def run_capture(cmd: list[str], *, cwd: Path, env: dict[str, str], timeout_s: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout_s,
        check=False,
    )


def require_ok(cp: subprocess.CompletedProcess[str], what: str) -> None:
    if cp.returncode == 0:
        return
    raise RuntimeError(f"{what} failed (exit={cp.returncode}).\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}")


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


def wait_for_redis_pong(*, challenge_dir: Path, env: dict[str, str], timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        cp = run_capture(
            ["docker", "compose", "exec", "-T", "datastore", "redis-cli", "-h", "127.0.0.1", "-p", "6379", "ping"],
            cwd=challenge_dir,
            env=env,
            timeout_s=30,
        )
        if cp.returncode == 0 and "PONG" in (cp.stdout or ""):
            return
        time.sleep(1)
    raise TimeoutError("Timed out waiting for datastore redis PONG.")


def wait_for_gossip_key(*, challenge_dir: Path, env: dict[str, str], timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        cp = run_capture(
            ["docker", "compose", "exec", "-T", "datastore", "redis-cli", "-h", "127.0.0.1", "-p", "6379", "EXISTS", "rumor:gossip:1"],
            cwd=challenge_dir,
            env=env,
            timeout_s=30,
        )
        if cp.returncode == 0 and cp.stdout.strip() == "1":
            return
        time.sleep(1)
    raise TimeoutError("Timed out waiting for rumor:gossip:1 to appear in redis.")


def fetch_gossip_json(*, challenge_dir: Path, env: dict[str, str]) -> dict:
    cp = run_capture(
        ["docker", "compose", "exec", "-T", "datastore", "redis-cli", "-h", "127.0.0.1", "-p", "6379", "GET", "rumor:gossip:1"],
        cwd=challenge_dir,
        env=env,
        timeout_s=30,
    )
    require_ok(cp, "redis-cli GET rumor:gossip:1")
    raw = (cp.stdout or "").strip()
    if not raw:
        raise RuntimeError("Missing/empty redis string: rumor:gossip:1")
    try:
        return json.loads(raw)
    except Exception as e:
        raise RuntimeError(f"rumor:gossip:1 is not valid JSON: {e!r}\nRaw:\n{raw[:2000]}")


def validate_and_print(obj: dict) -> None:
    def req_str(k: str) -> str:
        v = str(obj.get(k, "")).strip()
        if not v:
            raise SystemExit(f"Missing/empty {k}")
        return v

    gossip_id = int(obj.get("gossip_id", 0))
    if gossip_id <= 0:
        raise SystemExit("Invalid gossip_id")

    sources = obj.get("sources")
    if not isinstance(sources, list) or len(sources) < 3:
        raise SystemExit("Invalid sources list")
    if len(set(sources)) != len(sources):
        raise SystemExit("Sources not unique")

    true_ioc = req_str("true_ioc")
    msgs = obj.get("messages")
    if not isinstance(msgs, list) or len(msgs) != len(sources):
        raise SystemExit("Invalid messages list length")

    for i, m in enumerate(msgs):
        if not isinstance(m, dict):
            raise SystemExit("Invalid message object")
        if m.get("source") != sources[i]:
            raise SystemExit("Messages not aligned with sources")
        iocs = m.get("iocs")
        if not isinstance(iocs, list) or len(iocs) != 3:
            raise SystemExit("Each message must have exactly 3 iocs")
        if true_ioc not in iocs:
            raise SystemExit("true_ioc must appear in every message")

    created_at = int(obj.get("created_at", 0))
    now = int(time.time())
    if created_at <= 0 or created_at > now + 60:
        raise SystemExit("created_at out of range")

    print("[test_datastore.py] datastore test passed")
    print("[test_datastore.py] gossip_id:", gossip_id)
    print("[test_datastore.py] sources:", len(sources))
    print("[test_datastore.py] true_ioc:", true_ioc)

    # Print the generated messages (the core debugging aid).
    print("\n[test_datastore.py] Generated gossip messages:")
    for idx, m in enumerate(msgs, start=1):
        source = str(m.get("source", "")).strip()
        msg_text = str(m.get("message", "")).rstrip()

        print(f"\n--- Message {idx}/{len(msgs)} ---")
        print("Source:", source)
        print("Message:")
        print(msg_text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Start litellm+datastore, verify a gossip exists, and print the generated messages."
    )
    parser.add_argument("--no-build", action="store_true", help="Skip image builds (faster if already built).")
    parser.add_argument("--keep", action="store_true", help="Keep containers running after completion (no down -v).")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent

    dotenv_path = challenge_dir / ".env"
    if not dotenv_path.exists():
        print(
            "[test_datastore.py] ERROR: .env not found. Create it from env.example and set LITELLM_API_KEY.",
            file=sys.stderr,
        )
        return 1

    dotenv = _read_dotenv(dotenv_path)
    for k in ("LITELLM_API_KEY", "CHALLENGE_LITELLM_API_KEY", "TEAM_LITELLM_API_KEY"):
        if not (dotenv.get(k) or "").strip():
            print(f"[test_datastore.py] ERROR: {k} is empty in .env", file=sys.stderr)
            return 1

    team_key = dotenv["TEAM_LITELLM_API_KEY"]

    env = os.environ.copy()

    def print_debug_logs() -> None:
        try:
            ps = run_capture(["docker", "compose", "ps"], cwd=challenge_dir, env=env, timeout_s=30)
            if ps.stdout.strip():
                print("\n[test_datastore.py] docker compose ps:\n" + ps.stdout, file=sys.stderr)
            if ps.stderr.strip():
                print("\n[test_datastore.py] docker compose ps (stderr):\n" + ps.stderr, file=sys.stderr)
        except Exception:
            pass

        for svc in ("datastore", "litellm"):
            try:
                logs = run_capture(["docker", "compose", "logs", "--tail=250", svc], cwd=challenge_dir, env=env, timeout_s=30)
                if logs.stdout.strip():
                    print(f"\n[test_datastore.py] {svc} logs (tail):\n" + logs.stdout, file=sys.stderr)
                if logs.stderr.strip():
                    print(f"\n[test_datastore.py] {svc} logs (stderr):\n" + logs.stderr, file=sys.stderr)
            except Exception:
                pass

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
        up = ["docker", "compose", "up", "-d"]
        if not args.no_build:
            up.append("--build")
        up += ["litellm", "datastore"]

        print("[test_datastore.py] Starting litellm stub + datastore...")
        cp = run_capture(up, cwd=challenge_dir, env=env, timeout_s=300)
        require_ok(cp, "docker compose up")

        print("[test_datastore.py] Waiting for litellm /v1/models (authenticated)...")
        http_wait_ok(
            "http://localhost:4000/v1/models",
            headers={"Authorization": f"Bearer {team_key}"},
            timeout_s=60,
        )

        print("[test_datastore.py] Waiting for datastore redis PONG...")
        wait_for_redis_pong(challenge_dir=challenge_dir, env=env, timeout_s=60)

        print("[test_datastore.py] Waiting for gossip to appear in redis...")
        try:
            wait_for_gossip_key(challenge_dir=challenge_dir, env=env, timeout_s=60)
        except TimeoutError as e:
            print(f"[test_datastore.py] ERROR: {e}", file=sys.stderr)
            print_debug_logs()
            return 1

        obj = fetch_gossip_json(challenge_dir=challenge_dir, env=env)
        validate_and_print(obj)
        return 0
    finally:
        print("[test_datastore.py] Cleaning up...")
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

