# spaminout — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, Shellphish)
**Category:** network / pwn
**Format:** Attack-defense service

## Overview

A pair of C programs implementing a spam relay service: `spamin` receives
incoming spam and stores it, `spamout` retrieves and delivers spam. Together
they form a store-and-forward spam transport. Flags are stored as spam messages
and retrieved by the relay protocol.

## Architecture

```
TCP port 8008 — spamin: receives spam messages and stores in files
TCP port ????  — spamout: delivers stored spam messages
```

Protocol (spamin): client sends `SPAM-IN-SPAM-OUT\n<filename>\n<content>\n`.
The server appends `<content>` to `<filename>` (via `fopen(filename, "a+")`).

## Vulnerabilities

**1. `gets()` buffer overflow on filename** (`spamin.c:manage_request`):
```c
char filename[512];
int be = 13; // incremented each connection
if (be == 16) { fgets(filename, 512, stdin); }
else          { gets(filename); }  // buffer overflow on 1st, 2nd connections
```
On connections where `be != 16`, `gets()` overflows the 512-byte `filename` buffer.

**2. `gets()` buffer overflow on flag (always)**:
```c
int bop = 22;  // always < 46
if (bop > 46) { fgets(flag, 512, stdin); }
else          { gets(flag); }  // always reached → always overflows
```

**3. Format string vulnerability**:
```c
printf(banner);  // attacker-controlled banner without SPAM-IN-SPAM-OUT header
```

**4. Path traversal**: `fopen(filename, "a+")` with attacker-controlled `filename`
allows writing to arbitrary files accessible to the service user.

## Files

| File | Description |
|------|-------------|
| `src/spamin.c` | Spam receiver source code (2.9KB) |
| `src/spamout.c` | Spam sender source code (3.5KB) |
| `src/spamin` | Compiled spamin binary (32-bit ELF, 10.8KB) |
| `src/spamout` | Compiled spamout binary (32-bit ELF, 11.3KB) |
| `src/configure.in` | Autoconf build config |
| `src/Makefile.am` | Automake build file |
| `src/spamInOutScoringScript.py` | Scorebot flag set/get script |

## Notes

- Source extracted from CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The source archive `spaminout-1.0.tar.gz` was preserved in `/home/spam/` on the VM
  (decrypted — unlike `spaminout-1.0.tar.gz.gpg` which was encrypted).
- The `/home/spam/bin/` directory contained runtime artifacts (queue files) from
  the live competition.
