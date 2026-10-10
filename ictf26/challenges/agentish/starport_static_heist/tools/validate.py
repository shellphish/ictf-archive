#!/usr/bin/env python3
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEY_PATH = ROOT / "private" / "answer_key.json"


def now_unix() -> int:
    override = os.environ.get("CHALLENGE_NOW")
    if override:
        return int(override)
    return int(time.time())


def compute_temporal_key(secret: str, bucket: int) -> str:
    raw = f"{secret}|{bucket}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:10]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 validate.py <key>")
        return 2

    submitted = sys.argv[1].strip().lower()
    if not re.fullmatch(r"[a-f0-9]{10}", submitted):
        print("invalid format")
        return 1

    key = json.loads(KEY_PATH.read_text(encoding="utf-8"))
    bucket = now_unix() // int(key["key_rotation_seconds"])
    expected = compute_temporal_key(key["key_secret"], bucket)
    if submitted == expected:
        print(key["flag"])
        return 0

    print("incorrect key")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
