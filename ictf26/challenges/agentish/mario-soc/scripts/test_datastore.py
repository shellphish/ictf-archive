#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def run(cmd: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=check)


def run_stream(cmd: list[str], *, cwd: Path) -> int:
    p = subprocess.Popen(cmd, cwd=str(cwd))
    return p.wait()


def docker_compose(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["docker", "compose", *args], cwd=cwd, check=check)


def redis_cli(cwd: Path, *args: str) -> str:
    cp = docker_compose("exec", "-T", "datastore", "redis-cli", "-h", "127.0.0.1", "-p", "6379", *args, cwd=cwd)
    return cp.stdout.strip()


def get_json_value(cwd: Path, key: str) -> Any | None:
    raw = redis_cli(cwd, "GET", key)
    if raw == "":
        return None
    return json.loads(raw)


def get_hash(cwd: Path, key: str) -> dict[str, str]:
    out = redis_cli(cwd, "HGETALL", key)
    if out == "":
        return {}
    parts = out.splitlines()
    if len(parts) % 2 != 0:
        raise RuntimeError(f"Unexpected HGETALL output for {key!r}: odd number of lines")
    return {parts[i]: parts[i + 1] for i in range(0, len(parts), 2)}


def wait_for_key(cwd: Path, key: str, *, timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            exists = redis_cli(cwd, "EXISTS", key).strip()
            if exists == "1":
                return
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError(f"Timed out waiting for redis key: {key}")


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent

    # Optional knobs (passed through to docker compose as environment variables).
    force_regen = os.environ.get("FORCE_REGEN", "1")
    attack_seed = os.environ.get("ATTACK_SEED", "")
    internal_host_count = os.environ.get("INTERNAL_HOST_COUNT", "")
    internal_success_rate = os.environ.get("INTERNAL_SUCCESS_RATE", "")

    env = os.environ.copy()
    env["FORCE_REGEN"] = force_regen
    # Always set these (even empty) so a messy `.env` can't break the container env.
    env["ATTACK_SEED"] = attack_seed
    env["INTERNAL_HOST_COUNT"] = internal_host_count
    env["INTERNAL_SUCCESS_RATE"] = internal_success_rate

    print("[test_datastore.py] Starting datastore (redis + attack generator)...")
    # Keep this script focused: start only datastore.
    # We intentionally do not force `down -v` here; callers may want to inspect the container after.
    subprocess.run(
        ["docker", "compose", "up", "-d", "--build", "datastore"],
        cwd=str(challenge_dir),
        env=env,
        check=True,
    )

    print("[test_datastore.py] Waiting for dataset to appear in redis...")
    try:
        wait_for_key(challenge_dir, "mariosoc:config", timeout_s=60)
        wait_for_key(challenge_dir, "mariosoc:uba:users_json", timeout_s=60)
    except TimeoutError as e:
        print(f"[test_datastore.py] ERROR: {e}", file=sys.stderr)
        try:
            cp = docker_compose("ps", cwd=challenge_dir, check=False)
            if cp.stdout.strip():
                print("[test_datastore.py] docker compose ps:\n" + cp.stdout, file=sys.stderr)
            if cp.stderr.strip():
                print("[test_datastore.py] docker compose ps (stderr):\n" + cp.stderr, file=sys.stderr)
        except Exception:
            pass
        try:
            cp = docker_compose("logs", "--tail=200", "datastore", cwd=challenge_dir, check=False)
            if cp.stdout.strip():
                print("[test_datastore.py] datastore logs (tail):\n" + cp.stdout, file=sys.stderr)
            if cp.stderr.strip():
                print("[test_datastore.py] datastore logs (stderr):\n" + cp.stderr, file=sys.stderr)
        except Exception:
            pass
        return 2

    cfg = get_hash(challenge_dir, "mariosoc:config")
    attacker = json.loads(cfg.get("attacker_json", "{}"))
    victim = json.loads(cfg.get("victim_json", "{}"))
    internal_hosts = json.loads(cfg.get("internal_hosts_json", "[]"))

    users = get_json_value(challenge_dir, "mariosoc:uba:users_json") or []
    edr_hosts = get_json_value(challenge_dir, "mariosoc:edr:hosts_json") or []
    ids_ips = get_json_value(challenge_dir, "mariosoc:ids:ips_json") or []
    truth_hash = get_hash(challenge_dir, "mariosoc:truth")
    truth = json.loads(truth_hash.get("truth_json", "{}")) if truth_hash else {}

    uba_events: dict[str, Any] = {}
    for u in users:
        uba_events[str(u)] = get_json_value(challenge_dir, f"mariosoc:uba:events:{u}") or []

    edr_events: dict[str, Any] = {}
    for ip in edr_hosts:
        edr_events[str(ip)] = get_json_value(challenge_dir, f"mariosoc:edr:events:{ip}") or []

    ids_events: dict[str, Any] = {}
    for ip in ids_ips:
        ids_events[str(ip)] = get_json_value(challenge_dir, f"mariosoc:ids:events:{ip}") or []

    dataset = {
        "config": {
            "created_at": cfg.get("created_at"),
            "attack_seed": cfg.get("attack_seed"),
            "internal_host_count": cfg.get("internal_host_count"),
            "internal_success_rate": cfg.get("internal_success_rate"),
            "attacker": attacker,
            "victim": victim,
            "internal_hosts": internal_hosts,
        },
        "uba": {"users": users, "events_by_user": uba_events},
        "edr": {"hosts": edr_hosts, "events_by_host": edr_events},
        "ids": {"ips": ids_ips, "events_by_ip": ids_events},
        "truth": truth,
    }

    print("\n" + "=" * 80)
    print("DATASET (JSON)")
    print("=" * 80)
    print(json.dumps(dataset, indent=2, sort_keys=True))

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"attacker: {attacker.get('ip')} ({attacker.get('domain')})")
    print(f"victim:   {victim.get('ip')} ({victim.get('domain')}) user={victim.get('user')}")
    successes = [h for h in internal_hosts if h.get('exploitation_succeeded')]
    failures = [h for h in internal_hosts if not h.get('exploitation_succeeded')]
    print(f"internal_hosts: total={len(internal_hosts)} success={len(successes)} fail={len(failures)}")
    print(f"uba_users={len(users)} edr_hosts={len(edr_hosts)} ids_ips={len(ids_ips)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

