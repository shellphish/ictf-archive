# AgentZero — Writeup

**Category:** Web  
**Flag:** `ictf{local_test_flag}`

---

## Overview

AgentZero is an AI assistant web app with access to admin vault tools. The backend uses prototype pollution to leak a JWT secret, which can then be used to forge an admin token and access the classified vault containing the flag.

---

## Solution

### Vulnerability chain

1. `POST /api/preferences` calls `deepMerge(session, body)`.
2. Sending `{"__proto__":{"debug":true}}` pollutes `Object.prototype`, setting `session.debug = true`.
3. `POST /api/auth` detects the debug flag and leaks `JWT_SECRET` in the response body under `debug.secret`.
4. Use the leaked secret to forge a JWT with payload `{ "sub": <same-sub>, "role": "admin" }`.
5. The admin token unlocks `listVaults` and `openVault` tools via `POST /api/chat`.
6. List vaults → find `classified` → open it → get the flag.

### Exploit

```bash
python3 writeup/solve.py --base-url http://localhost:3001
```

---

## Flag

`ictf{local_test_flag}`
