#!/usr/bin/env python3
"""
Bring up datastore and mcp_challenges, then:
1) Get the 10 challenge IDs and print them
2) Get the source code of each challenge
3) Execute each challenge with a random input
4) Execute each challenge with exploit_input from metadata.json
5) If step 4 fails (e.g. Temporary failure), retry until success
6) Build the sentence from collected words and compare to expected sentence
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import requests  # type: ignore[import-not-found]
except ImportError:
    requests = None


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
    lines = cp.stdout.strip().splitlines()
    return dict(zip(lines[::2], lines[1::2])) if lines else {}


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


def jsonrpc(url: str, method: str, params: dict | None = None, _id: int = 1) -> dict:
    payload: dict = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data


def tools_call(url: str, name: str, arguments: dict) -> str:
    res = jsonrpc(url, "tools/call", {"name": name, "arguments": arguments}, _id=99)
    return res["result"]["content"][0]["text"]


def get_exploit_input(dataset_path: Path, sample_id: str) -> str | None:
    meta = dataset_path / sample_id / "metadata.json"
    if not meta.exists():
        return None
    try:
        data = json.loads(meta.read_text())
        return data.get("exploit_input")
    except Exception:
        return None


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Test mcp_challenges: IDs, code, run with random/exploit input")
    parser.add_argument("--keep", action="store_true", help="Keep containers running after")
    args = parser.parse_args()

    if requests is None:
        print("[test_mcp_challenge.py] ERROR: install 'requests' (pip install requests)", file=sys.stderr)
        return 1

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent
    dataset_path = challenge_dir / "dataset"

    dotenv = challenge_dir / ".env"
    if not dotenv.exists():
        ex = challenge_dir / "env.example"
        if ex.exists():
            shutil.copyfile(ex, dotenv)
            print("[test_mcp_challenge.py] Created .env from env.example", file=sys.stderr)
        else:
            print("[test_mcp_challenge.py] ERROR: .env not found", file=sys.stderr)
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
        print("[test_mcp_challenge.py] Starting litellm, datastore, mcp_challenges...")
        cp = subprocess.run(
            ["docker", "compose", "--profile", "debug", "up", "-d", "--build", "litellm", "datastore", "mcp_challenges"],
            cwd=str(challenge_dir),
            env=env,
            text=True,
            check=False,
        )
        if cp.returncode != 0:
            print(f"[test_mcp_challenge.py] FAIL: docker compose up exited {cp.returncode}", file=sys.stderr)
            return cp.returncode

        print("[test_mcp_challenge.py] Waiting for waikness:config...")
        if not wait_for_config(challenge_dir=challenge_dir, env=env, timeout_s=90):
            print("[test_mcp_challenge.py] ERROR: timeout waiting for config", file=sys.stderr)
            return 1

        print("[test_mcp_challenge.py] Waiting for mcp_challenges health...")
        http_wait_ok("http://localhost:7001/healthz", timeout_s=30)

        mcp_url = "http://localhost:7001/rpc"

        # Get challenge config from Redis for sample_id -> exploit_input mapping
        cfg = redis_hgetall(challenge_dir, env, "waikness:config")
        challenges = json.loads(cfg.get("challenges_json", "[]"))
        id_to_sample = {ch["id"]: ch["sample_id"] for ch in challenges}

        # 1) Get the 10 IDs and print them
        ids_text = tools_call(mcp_url, "get_challenge_ids", {})
        ids = json.loads(ids_text)
        print()
        print("=== 1) Challenge IDs ===")
        print(ids)
        print()

        # 2) Get source code of each challenge
        print("=== 2) Source code (first 200 chars each) ===")
        for cid in ids:
            code = tools_call(mcp_url, "get_challenge_code", {"challenge_id": str(cid)})
            preview = code[:200] + "..." if len(code) > 200 else code
            print(f"  ID {cid}: {preview!r}")
        print()

        # 3) Execute with random input
        print("=== 3) Execute with random input ===")
        for cid in ids:
            random_input = "random_" + str(random.randint(1, 99999))
            result = tools_call(mcp_url, "run_challenge", {"challenge_id": str(cid), "payload": random_input})
            print(f"  ID {cid} payload={random_input!r} -> {result[:80]!r}...")
        print()

        # 4) & 5) Execute with exploit_input, retry until success, collect words
        print("=== 4) & 5) Execute with exploit_input (retry until success) ===")
        words: list[str] = []
        for cid in ids:
            sample_id = id_to_sample.get(str(cid))
            exploit_input = get_exploit_input(dataset_path, sample_id) if sample_id else None
            if not exploit_input:
                print(f"  ID {cid}: no exploit_input in metadata, skipping")
                words.append("?")
                continue

            attempt = 0
            while True:
                attempt += 1
                result = tools_call(mcp_url, "run_challenge", {"challenge_id": str(cid), "payload": exploit_input})
                if result != "Temporary failure":
                    # Extract word from "OK: [word]" format
                    if result.startswith("OK: [") and result.endswith("]"):
                        word = result[5:-1]
                        words.append(word)
                    else:
                        words.append("?")  # ERROR or unexpected format
                    print(f"  ID {cid} attempt={attempt} payload={exploit_input!r} -> {result!r}")
                    break
                print(f"  ID {cid} attempt={attempt}: Temporary failure, retrying...")
                time.sleep(0.3)

        # 6) Build sentence and compare to expected
        collected_sentence = " ".join(words)
        expected_sentence = cfg.get("sentence", "").strip()
        print()
        print("=== 6) Sentence comparison ===")
        print(f"  Collected: {collected_sentence!r}")
        print(f"  Expected:  {expected_sentence!r}")
        if collected_sentence == expected_sentence:
            print("  Match: YES")
        else:
            print("  Match: NO")
            return 1

        print()
        print("[test_mcp_challenge.py] PASS")
        return 0
    finally:
        print("[test_mcp_challenge.py] Cleaning up...")
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
