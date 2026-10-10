#!/usr/bin/env python3
"""
Iterate over all challenges in dataset and:
1) If C challenge, compile it
2) Execute with random input (with /flag set to known value)
3) Execute with exploit_input from metadata.json and verify output contains the flag value
"""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from pathlib import Path

TEST_FLAG_VALUE = "TEST_FLAG_12345"


def discover_samples(dataset_path: Path) -> list[str]:
    """Return sorted list of sample IDs."""
    samples = []
    for d in sorted(dataset_path.iterdir()):
        if d.is_dir() and d.name.startswith("sample_"):
            vuln = d / "vuln"
            vuln_py = d / "vuln.py"
            vuln_c = d / "vuln.c"
            if vuln.exists() or vuln_py.exists() or vuln_c.exists():
                samples.append(d.name)
    return samples


def compile_c_sample(sample_dir: Path, out_bin: Path) -> bool:
    """Compile vuln.c to out_bin. Return True on success."""
    vuln_c = sample_dir / "vuln.c"
    if not vuln_c.exists():
        return False
    result = subprocess.run(
        ["gcc", "-o", str(out_bin), str(vuln_c)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0


def run_vuln(sample_dir: Path, vuln_bin: Path | None, vuln_py: Path | None, payload: str, flag_value: str) -> str:
    """Run the vuln with payload. /flag must already contain flag_value. Returns stdout+stderr."""
    if vuln_bin and vuln_bin.exists():
        cmd = [str(vuln_bin), payload]
    elif vuln_py and vuln_py.exists():
        cmd = ["python3", str(vuln_py), payload]
    else:
        return ""

    result = subprocess.run(
        cmd,
        cwd=str(sample_dir),
        capture_output=True,
        timeout=10,
    )
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    return (stdout + stderr).strip()


def ensure_base_paths(meta_path: Path) -> None:
    """Create directories listed in metadata.json base_paths."""
    if not meta_path.exists():
        return
    try:
        data = json.loads(meta_path.read_text())
        for p in data.get("base_paths", []):
            Path(p).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def run_tests(dataset_path: Path, compiled_path: Path) -> tuple[int, int]:
    """Run all tests. Returns (passed, failed)."""
    Path("/flag").write_text(TEST_FLAG_VALUE)
    Path("/home/user/documents").mkdir(parents=True, exist_ok=True)

    samples = discover_samples(dataset_path)
    passed = 0
    failed = 0

    for sample_id in samples:
        sample_dir = dataset_path / sample_id
        vuln_c = sample_dir / "vuln.c"
        vuln_bin = sample_dir / "vuln"
        vuln_py = sample_dir / "vuln.py"

        # 1) Compile if C
        if vuln_c.exists():
            out_dir = compiled_path / sample_id
            out_dir.mkdir(parents=True, exist_ok=True)
            out_bin = out_dir / "vuln"
            if not compile_c_sample(sample_dir, out_bin):
                print(f"  FAIL {sample_id}: compile failed")
                failed += 1
                continue
            vuln_bin = out_bin
        elif not vuln_bin.exists() and not vuln_py.exists():
            print(f"  SKIP {sample_id}: no vuln binary or script")
            continue

        if not vuln_py.exists():
            vuln_py = None

        # Create base_paths from metadata before execution
        ensure_base_paths(sample_dir / "metadata.json")

        # 2) Execute with random input
        random_input = f"random_{random.randint(1, 999999)}"
        _ = run_vuln(sample_dir, vuln_bin, vuln_py, random_input, TEST_FLAG_VALUE)

        # 3) Execute with exploit_input and check output contains flag
        meta = sample_dir / "metadata.json"
        if not meta.exists():
            print(f"  SKIP {sample_id}: no metadata.json")
            continue

        try:
            data = json.loads(meta.read_text())
            exploit_input = data.get("exploit_input")
        except Exception:
            print(f"  FAIL {sample_id}: could not read metadata.json")
            failed += 1
            continue

        if not exploit_input:
            print(f"  SKIP {sample_id}: no exploit_input in metadata")
            continue

        output = run_vuln(sample_dir, vuln_bin, vuln_py, exploit_input, TEST_FLAG_VALUE)

        if TEST_FLAG_VALUE in output:
            print(f"  PASS {sample_id}: output contains flag")
            passed += 1
        else:
            print(f"  FAIL {sample_id}: output does not contain flag. Output: {output[:100]!r}...")
            failed += 1

    return passed, failed


def main_inner() -> int:
    """Run tests (must be inside Docker with /flag writable)."""
    dataset_path = Path("/dataset")
    compiled_path = Path("/tmp/compiled")

    if not dataset_path.exists():
        print("[test_challenges] ERROR: /dataset not found (run via Docker)", file=sys.stderr)
        return 1

    try:
        Path("/flag").write_text(TEST_FLAG_VALUE)
    except OSError as e:
        print(f"[test_challenges] ERROR: cannot write /flag: {e}. Run via Docker.", file=sys.stderr)
        return 1

    print("[test_challenges] Running tests...")
    passed, failed = run_tests(dataset_path, compiled_path)
    print()
    print(f"[test_challenges] Result: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def main() -> int:
    if "--inner" in sys.argv:
        return main_inner()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent
    dataset_path = challenge_dir / "dataset"

    if not dataset_path.exists():
        print(f"[test_challenges] ERROR: dataset not found at {dataset_path}", file=sys.stderr)
        return 1

    # Run inside Docker (need /flag writable and gcc for C compilation)
    print("[test_challenges] Running tests in Docker...")
    cmd = [
        "docker", "run", "--rm",
        "-e", "DEBIAN_FRONTEND=noninteractive",
        "-v", f"{dataset_path}:/dataset:ro",
        "-v", f"{script_dir}:/scripts:ro",
        "python:3.11-slim",
        "bash", "-c",
        "apt-get update -qq && apt-get install -y -qq gcc libc6-dev > /dev/null "
        "&& python3 /scripts/test_challenges.py --inner",
    ]
    result = subprocess.run(cmd, cwd=str(challenge_dir))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
