#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    target = repo_root / "stubs" / "test_stubs.py"
    if not target.exists():
        raise SystemExit(f"Expected relocated script at: {target}")
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()

