#!/usr/bin/env python3
"""
Consider it a CTF... — Solver
Extracts and searches git history in announcement.zip for the flag.

Usage:
    python3 writeup/solve.py [path/to/announcement.zip]
"""

import os
import re
import subprocess
import sys
import tempfile
import zipfile


FLAG_RE = re.compile(r"ictf\{[^}]+\}", re.IGNORECASE)


def run(cmd: list[str], cwd: str) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.stdout + result.stderr


def main():
    zip_path = sys.argv[1] if len(sys.argv) > 1 else "announcement.zip"

    with tempfile.TemporaryDirectory() as tmp:
        print(f"[*] Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp)

        # Find git repo
        repo_dir = tmp
        for root, dirs, files in os.walk(tmp):
            if ".git" in dirs:
                repo_dir = root
                break

        print(f"[*] Git repo at: {repo_dir}")

        # Show full log
        log = run(["git", "log", "--all", "--oneline"], repo_dir)
        print("[*] Git log:")
        print(log)

        # Get all commit hashes
        hashes = [line.split()[0] for line in log.strip().splitlines() if line]

        # Search every commit's full diff for the flag
        for h in hashes:
            diff = run(["git", "show", h], repo_dir)
            m = FLAG_RE.search(diff)
            if m:
                print(f"[+] Flag found in commit {h}: {m.group(0)}")
                return

        # Also try all tracked file content at each commit
        for h in hashes:
            files_out = run(["git", "ls-tree", "-r", "--name-only", h], repo_dir)
            for fname in files_out.strip().splitlines():
                content = run(["git", "show", f"{h}:{fname}"], repo_dir)
                m = FLAG_RE.search(content)
                if m:
                    print(f"[+] Flag found in {fname} @ {h}: {m.group(0)}")
                    return

        print("[-] Flag not found in git history.")


if __name__ == "__main__":
    main()
