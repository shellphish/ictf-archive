#!/usr/bin/env python3
"""
Bring up datastore, mcp_challenges, mcp_flag, then:
1) Solve the challenges (get IDs, run with exploit_input, collect words)
2) Submit the correct sequence -> expect OK + flag
3) Submit a valid English sentence but wrong -> expect VALID-WRONG
4) Submit an invalid sequence (wrong format) -> expect INVALID
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


def solve_challenges(mcp_url: str, dataset_path: Path, cfg: dict) -> str | None:
    """Solve all challenges and return the collected sentence, or None if solving fails."""
    challenges = json.loads(cfg.get("challenges_json", "[]"))
    id_to_sample = {ch["id"]: ch["sample_id"] for ch in challenges}
    ids = json.loads(tools_call(mcp_url, "get_challenge_ids", {}))

    words: list[str] = []
    for cid in ids:
        sample_id = id_to_sample.get(str(cid))
        exploit_input = get_exploit_input(dataset_path, sample_id) if sample_id else None
        if not exploit_input:
            words.append("?")
            continue

        for _ in range(50):  # Max retries for Temporary failure
            try:
                result = tools_call(mcp_url, "run_challenge", {"challenge_id": str(cid), "payload": exploit_input})
            except Exception as e:
                print(f"[test_mcp_flag.py] run_challenge failed for {cid}: {e}")
                words.append("?")
                break
            if result != "Temporary failure":
                if result.startswith("OK: [") and result.endswith("]"):
                    words.append(result[5:-1])
                else:
                    words.append("?")
                break
            time.sleep(0.3)
        else:
            words.append("?")

    sentence = " ".join(words)
    return sentence if "?" not in words else None


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Test mcp_flag: solve challenges, submit correct/valid-wrong/invalid")
    parser.add_argument("--keep", action="store_true", help="Keep containers running after")
    args = parser.parse_args()

    if requests is None:
        print("[test_mcp_flag.py] ERROR: install 'requests' (pip install requests)", file=sys.stderr)
        return 1

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent
    dataset_path = challenge_dir / "dataset"

    dotenv = challenge_dir / ".env"
    if not dotenv.exists():
        ex = challenge_dir / "env.example"
        if ex.exists():
            shutil.copyfile(ex, dotenv)
            print("[test_mcp_flag.py] Created .env from env.example", file=sys.stderr)
        else:
            print("[test_mcp_flag.py] ERROR: .env not found", file=sys.stderr)
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
        print("[test_mcp_flag.py] Starting litellm, datastore, mcp_challenges, mcp_flag...")
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
            print(f"[test_mcp_flag.py] FAIL: docker compose up exited {cp.returncode}", file=sys.stderr)
            return cp.returncode

        print("[test_mcp_flag.py] Waiting for waikness:config...")
        if not wait_for_config(challenge_dir=challenge_dir, env=env, timeout_s=90):
            print("[test_mcp_flag.py] ERROR: timeout waiting for config", file=sys.stderr)
            return 1

        print("[test_mcp_flag.py] Waiting for MCP health...")
        http_wait_ok("http://localhost:7001/healthz", timeout_s=30)
        http_wait_ok("http://localhost:7002/healthz", timeout_s=30)

        mcp_challenges_url = "http://localhost:7001/rpc"
        mcp_flag_url = "http://localhost:7002/rpc"

        cfg = redis_hgetall(challenge_dir, env, "waikness:config")

        # Solve challenges (or use expected from Redis)
        print("[test_mcp_flag.py] Solving challenges...")
        expected = cfg.get("sentence", "").strip()
        correct_sentence = solve_challenges(mcp_challenges_url, dataset_path, cfg)
        if correct_sentence is None or "?" in correct_sentence:
            print(f"[test_mcp_flag.py] Using expected sentence from Redis (solve incomplete)")
            correct_sentence = expected
        elif correct_sentence != expected:
            print(f"[test_mcp_flag.py] WARNING: collected {correct_sentence!r} != expected {expected!r}")
            correct_sentence = expected

        print()
        print("=== Submitting sentences to mcp_flag ===")

        # 1) Correct sequence
        print("\n1) Correct sequence:")
        result1 = tools_call(mcp_flag_url, "submit_sentence", {"sentence": correct_sentence})
        print(f"   Sentence: {correct_sentence!r}")
        print(f"   Result:   {result1}")
        if "OK" not in result1 or "Flag" not in result1:
            print("   FAIL: expected OK + flag")
            return 1
        print("   PASS")

        # 2) Correct words but wrong order (VALID-WRONG)
        expected_words = [w.strip(".,!?;:\"'") for w in correct_sentence.split() if w.strip(".,!?;:\"'")]
        shuffled = expected_words.copy()
        random.shuffle(shuffled)
        valid_wrong = " ".join(shuffled)
        print("\n2) Correct words but wrong order (VALID-WRONG):")
        print(f"   Sentence: {valid_wrong!r}")
        result2 = tools_call(mcp_flag_url, "submit_sentence", {"sentence": valid_wrong})
        print(f"   Result:   {result2}")
        if "VALID-WRONG" not in result2:
            print("   FAIL: expected VALID-WRONG")
            return 1
        print("   PASS")

        # 3) Invalid sequence (wrong format: not 10 alphabetic words)
        invalid_sentence = "one two three four five six seven eight nine"  # 9 words
        print("\n3) Invalid sequence (9 words):")
        print(f"   Sentence: {invalid_sentence!r}")
        result3 = tools_call(mcp_flag_url, "submit_sentence", {"sentence": invalid_sentence})
        print(f"   Result:   {result3}")
        if "INVALID" not in result3:
            print("   FAIL: expected INVALID")
            return 1
        print("   PASS")

        print()
        print("[test_mcp_flag.py] PASS")
        return 0
    finally:
        print("[test_mcp_flag.py] Cleaning up...")
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
