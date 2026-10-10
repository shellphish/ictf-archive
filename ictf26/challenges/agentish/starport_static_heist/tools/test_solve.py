#!/usr/bin/env python3
import json
import argparse
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
SKILLS_API = ROOT / "services" / "mcp_logs" / "basic_skills_api.py"
VALIDATOR = ROOT / "tools" / "validate.py"


def parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


def run_json_command(args: List[str], env: Optional[Dict[str, str]] = None) -> Dict:
    proc = subprocess.run(args, capture_output=True, text=True, check=False, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout.strip() or proc.stderr.strip() or "command failed")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON output from command: {' '.join(args)}") from exc


def list_logs(env: Optional[Dict[str, str]] = None) -> List[str]:
    out = run_json_command([sys.executable, str(SKILLS_API), "list_logs"], env=env)
    logs = out.get("logs", [])
    if not isinstance(logs, list):
        raise RuntimeError("list_logs returned invalid payload")
    return [str(x) for x in logs]


def retrieve_lines_from_log(log_name: str, start_line: int, end_line: int, env: Optional[Dict[str, str]] = None) -> List[str]:
    out = run_json_command(
        [
            sys.executable,
            str(SKILLS_API),
            "retrieve_lines_from_log",
            log_name,
            str(start_line),
            str(end_line),
        ],
        env=env,
    )
    lines = out.get("lines", [])
    if not isinstance(lines, list):
        raise RuntimeError("retrieve_lines_from_log returned invalid payload")
    return [str(x) for x in lines]


def load_events_via_skills(window: int = 8, env: Optional[Dict[str, str]] = None) -> List[Dict]:
    events: List[Dict] = []
    logs = list_logs(env=env)
    for log_name in logs:
        line_start = 1
        while True:
            line_end = line_start + window - 1
            lines = retrieve_lines_from_log(log_name, line_start, line_end, env=env)
            if not lines:
                break
            for raw in lines:
                raw = raw.strip()
                if raw:
                    events.append(json.loads(raw))
            line_start += window
    return events


def resolve_gate7_duty_officer(events: List[Dict]) -> Tuple[str, str]:
    """
    Two-hop: find whoever is on Gate 7 comms duty (they hold the rotation shards).
    Returns (alias, speaker_id).
    """
    ordered = sorted(events, key=lambda x: parse_ts(x["timestamp"]))
    aliases = {str(e.get("speaker_alias", "")).lower() for e in events}
    aliases.discard("")

    gate7_duty_re = re.compile(
        r"\bgate\s*7\b.*\bcomms\b.*\bduty\b"
        r"|\bduty\b.*\bgate\s*7\b.*\bcomms\b",
        re.IGNORECASE,
    )

    holder_alias: Optional[str] = None
    for event in ordered:
        text = event["text"]
        if not gate7_duty_re.search(text):
            continue
        text_lower = text.lower()
        for alias in sorted(aliases):
            if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                holder_alias = alias
                break
        if holder_alias:
            break

    if holder_alias is None:
        raise RuntimeError("Could not identify Gate 7 comms duty officer.")

    for event in ordered:
        if str(event.get("speaker_alias", "")).lower() == holder_alias:
            return holder_alias, str(event["speaker_id"])

    raise RuntimeError(f"Could not find speaker_id for alias {holder_alias!r}")


def extract_key(events: List[Dict], speaker_id: str) -> str:
    pattern = re.compile(r"\bkey\s+shard\s+(one|two|three):\s*([a-f0-9]+)\b", re.IGNORECASE)
    order = {"one": 1, "two": 2, "three": 3}
    shards: List[Tuple[int, datetime, str]] = []

    for event in events:
        if event["speaker_id"] != speaker_id:
            continue
        match = pattern.search(event["text"])
        if not match:
            continue
        shards.append((order[match.group(1).lower()], parse_ts(event["timestamp"]), match.group(2).lower()))

    if len(shards) < 3:
        raise RuntimeError("Could not extract three key shards.")
    shards.sort(key=lambda x: (x[0], x[1]))
    return "".join([x[2] for x in shards[:3]])


def validate_key(key: str, env: Optional[Dict[str, str]] = None) -> Tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), key],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    return proc.returncode == 0, proc.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Organizer solvability test")
    parser.add_argument(
        "--at",
        type=int,
        default=None,
        help="Freeze server time for local testing only.",
    )
    parser.add_argument(
        "--fixed",
        action="store_true",
        help="Use deterministic default test time for reproducible checks.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.at is not None or args.fixed:
        print("warning: --at/--fixed are ignored because API time override is disabled")
    test_time = int(time.time())

    events = load_events_via_skills()
    if not events:
        raise RuntimeError("No logs found. Run generate_dataset.py first.")

    alias, speaker_id = resolve_gate7_duty_officer(events)
    key = extract_key(events, speaker_id)
    ok, output = validate_key(key)

    print(f"resolved_alias={alias}")
    print(f"resolved_speaker_id={speaker_id}")
    print(f"test_unix_time={test_time}")
    print(f"assembled_key={key}")
    print(f"validator_output={output}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
