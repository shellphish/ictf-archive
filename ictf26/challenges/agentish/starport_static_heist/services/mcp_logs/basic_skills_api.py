#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import List


_HERE = Path(__file__).resolve().parent          # services/mcp_logs/
_CHALLENGE_ROOT = _HERE.parents[1]               # starport_static_heist/

DATA_DIR = _HERE / "data"
KEY_PATH = _CHALLENGE_ROOT / "private" / "answer_key.json"


def load_key_config() -> dict:
    return json.loads(KEY_PATH.read_text(encoding="utf-8"))


def now_unix() -> int:
    # Backdoor time override intentionally disabled for production behavior.
    # override = os.environ.get("CHALLENGE_NOW")
    # if override:
    #     return int(override)
    return int(time.time())


def compute_temporal_key(secret: str, bucket: int) -> str:
    raw = f"{secret}|{bucket}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:10]


def render_text(text: str) -> str:
    cfg = load_key_config()
    bucket = now_unix() // int(cfg["key_rotation_seconds"])
    key = compute_temporal_key(cfg["key_secret"], bucket)
    rendered = text.replace("{{KEY_1}}", key[:3])
    rendered = rendered.replace("{{KEY_2}}", key[3:7])
    rendered = rendered.replace("{{KEY_3}}", key[7:10])
    return rendered


def list_logs() -> List[str]:
    return sorted([p.name for p in DATA_DIR.glob("vr_session_logs_part*.jsonl")])


def retrieve_lines_from_log(log_name: str, start_line: int, end_line: int) -> dict:
    if start_line < 1 or end_line < start_line:
        raise ValueError("Invalid line range.")
    path = DATA_DIR / log_name
    if not path.exists():
        raise FileNotFoundError(f"Unknown log: {log_name}")

    lines: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if lineno < start_line:
                continue
            if lineno > end_line:
                break
            raw = line.rstrip("\n")
            event = json.loads(raw)
            event["text"] = render_text(event.get("text", ""))
            lines.append(json.dumps(event, ensure_ascii=True))

    return {
        "log_name": log_name,
        "start_line": start_line,
        "end_line": end_line,
        "lines": lines,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Basic log access API")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list_logs", help="List available log files")

    p_get = sub.add_parser("retrieve_lines_from_log", help="Get inclusive line range from one log")
    p_get.add_argument("log_name", type=str)
    p_get.add_argument("start_line", type=int)
    p_get.add_argument("end_line", type=int)

    args = parser.parse_args()
    if args.cmd == "list_logs":
        print(json.dumps({"logs": list_logs()}, ensure_ascii=True))
        return 0

    try:
        result = retrieve_lines_from_log(args.log_name, args.start_line, args.end_line)
    except (ValueError, FileNotFoundError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=True))
        return 1

    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
