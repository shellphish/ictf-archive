# bpt-proto — iCTF 2006 "The Hillbilly Bank"

**Competition:** iCTF 2006 (December 8, 2006 — UCSB Frank Hall)  
**Category:** Reverse Engineering / Binary Exploitation  
**Format:** Attack-defense service  
**Port:** 2342 (UDP)  
**Source:** **Not available** — binary-only challenge

---

## Overview

`bankproto` was the inter-bank communication backbone of the iCTF 2006
scenario. Every team ran their own instance; the scorebot exercised it by
creating accounts, depositing RSA-signed checks, and initiating fund transfers.

The source code was not recovered from the competition VM — only the compiled
binary survives. This makes it a genuine historical reverse-engineering
challenge.

---

## Binary Details

| Property | Value |
|----------|-------|
| File | `src/bankproto` (13,748 bytes) |
| Format | ELF 32-bit LSB, Intel 80386 |
| ABI | Linux 2.2.0 (glibc 2.3.6) |
| Compiler | GCC 3.4.6 (Ubuntu Dapper Drake) |
| Stripped | **No** — symbol table intact |
| Mitigations | None (no PIE, no stack canary, no RELRO) |

Function symbols preserved in the binary:

| Address | Function |
|---------|----------|
| `0x08049970` | `reaper` — SIGCHLD handler, reaps forked children |
| `0x08048997` | `verify_echeck` — delegates to `/usr/bin/ccheck` via `popen()` |
| `0x08048a47` | `manage_client` — parses UDP message and dispatches commands |
| `0x0804921e` | `main` — binds UDP socket, forks on each packet |

---

## Protocol (reconstructed from scorebot scripts)

All messages are sent as UDP datagrams to **port 2342**.  
Responses are `<code>\r\n<message>` format.

```
Create account:   N <cookie>
Deposit check:    D <cookie> <check>
Transfer funds:   T <cookie> <iban> <amount>
```

| Command | Success code | Error response |
|---------|-------------|----------------|
| `N` (new account) | `311` | `"The account already exists."` / `"I cannot open your account."` |
| `D` (deposit)     | `382` | `"Your check is invalid."` / `"Your balance has been updated."` |
| `T` (transfer)    | `711` | `"Negative or null amount."` / `"You do not have the required funds."` / `"I cannot create the transaction."` |

Check validation is handled by `/usr/bin/ccheck`, called via `popen()` with
the cookie and check value as arguments: `popen("/usr/bin/ccheck %s %s", ...)`.
The `ccheck` binary was part of the central bank infrastructure and is not
included here.

---

## Filesystem Layout (from strings and init script)

```
/home/bpt/bankproto          ← service binary
/home/bpt/accounts/          ← one file per account (named by cookie)
/var/spool/transactions/bpt/ ← completed transactions (trans.XXXXXX)
/var/run/bpt.pid             ← daemon PID file
/usr/bin/ccheck              ← RSA check validator (separate binary, not recovered)
```

Account balance is read from and written to `/home/bpt/accounts/<cookie>`.  
Transactions are written to a temporary file in `/var/spool/transactions/bpt/`
using `tempnam()`.

---

## Attack Surface

The binary presents several potential vulnerability classes to investigate:

1. **Buffer overflow** — `manage_client` parses the incoming UDP datagram
   with `sscanf`/`sprintf`. Cookie and check values are copied into fixed-size
   stack buffers. An oversized cookie or check string may overflow them.

2. **Path traversal** — Accounts are stored as `accounts/<cookie>`. A cookie
   containing `../` could escape the accounts directory, allowing reads or
   writes to arbitrary files (including `/home/bpt/bankproto` itself).

3. **Command injection via `popen`** — `verify_echeck` passes the cookie and
   check string directly to `popen("/usr/bin/ccheck %s %s", ...)`. Shell
   metacharacters in the check field could inject commands.

4. **Format string** — Response messages use `fprintf`/`sprintf` with
   format strings pulled from `.rodata`. If any user-controlled data reaches
   a format argument directly, arbitrary read/write is possible.

5. **Race condition (TOCTOU)** — `access()` is called before `fopen()`
   (visible in the import table). This classic TOCTOU window on the account
   file could allow privilege escalation under the forking model.

6. **Integer overflow** in transfer amount parsing — `atoi()` is used for
   the `<amount>` field. A negative or very large value may bypass the
   `"Negative or null amount"` check or cause an integer wrap.

---

## Running the Challenge

The service requires libc 2.x (32-bit). On a modern host, install the 32-bit
runtime:

```bash
# Debian/Ubuntu
apt-get install libc6-i386

# Create expected directories and user
useradd -m bpt
mkdir -p /home/bpt/accounts /var/spool/transactions/bpt
cp src/bankproto /home/bpt/bankproto
chmod +x /home/bpt/bankproto

# Run (port 2342/UDP, as user bpt)
su bpt -c '/home/bpt/bankproto'
```

Or use the init script (requires LSB init functions):

```bash
bash src/init_bpt start
```

Quick sanity test:

```bash
# Create an account called "testuser"
echo -n "N testuser" | nc -u -w1 127.0.0.1 2342
# Expected: 311\r\nThe account has been created.
```

---

## Historical Notes

- iCTF 2006 ran on **December 8, 2006** at UCSB Frank Hall.
- The theme was **"The Hillbilly Bank"** — a parody of a backwoods financial
  institution with RSA-signed paper checks.
- The central bank infrastructure (`hillbilly-bank`) handled RSA key generation,
  check signing, and inter-bank clearing. `bpt-proto` was the branch-level
  transaction daemon that accepted those checks.
- The `ccheck` validator binary is lost — it was part of the central
  infrastructure, not per-team deployment.
- Binary compiled on Ubuntu 6.06 LTS (Dapper Drake) with GCC 3.4.6.

---

## Files

| File | Description |
|------|-------------|
| `src/bankproto` | Service binary (32-bit ELF, symbols intact) |
| `src/init_bpt` | `init.d` service startup/stop script |
