# syscalld — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, Shellphish)
**Category:** pwn / reverse engineering
**Format:** Attack-defense service

## Overview

A remote service (TCP port 31337) that acts as an interactive x86 assembly
interpreter. Clients send x86 instructions (`pushl`, `popl`, `movl`, `addl`,
`sysenter`, `dump`) one per line, and the service executes them directly on
an in-process virtual register file, calling actual Linux syscalls via
`sysenter`. The flag is stored at `/usr/local/share/syscalld/flag`.

The service XOR-obfuscates instruction keywords with a seed extracted from
the version banner: `"v1.0.<seed>"`. Clients must XOR each keyword byte by
the seed before sending.

## Architecture

```
TCP port 31337
Banner: "syscalld vX.Y.<seed>\n"
Commands (XOR-obfuscated): pushl, popl, movl, addl, sysenter, dump
```

The scorebot opens `/usr/local/share/syscalld/flag` (syscall 5 = open),
reads it (syscall 3 = read), and writes a new flag (syscall 4 = write)
using `sysenter`. The `dump` command shows registers as a hex memory dump.

## Vulnerability

The service exposes arbitrary Linux syscall execution. An attacker who can
recover the XOR seed from the banner can:
1. XOR-encode any instruction keyword and send it
2. Open, read, or write any file accessible to the service user
3. Execute shellcode via arbitrary syscalls

The XOR seed is trivially recoverable: it appears in plaintext in the banner
as the version number's build component (`v1.0.<seed>`).

## Files

| File | Description |
|------|-------------|
| `src/syscalldScoringScript.py` | Scorebot flag set/get script (shows full protocol) |

## Notes

- No source code found on the VM; the service binary was not in `/home/syscalld/`.
- Source is likely in a GPG-encrypted archive or was not preserved.
- The scoring script fully documents the protocol: extract seed from banner,
  XOR all keyword bytes, send x86 instructions to open/read/write the flag file.
