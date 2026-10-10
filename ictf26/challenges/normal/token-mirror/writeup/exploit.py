#!/usr/bin/env python3
"""Solve the Token Mirror challenge."""

from pwn import *

HOST = "0.cloud.chals.io"
PORT = 0  # replace with actual port

SOLUTION = "reward drawer star rats evil live"


def solve_remote():
    r = remote(HOST, PORT)
    r.recvuntil(b"Enter your string: ")
    r.sendline(SOLUTION.encode())
    output = r.recvall().decode()
    print(output)
    r.close()


def solve_local():
    """Verify the solution locally."""
    import tiktoken

    enc = tiktoken.get_encoding("o200k_base")
    text = SOLUTION
    rev = text[::-1]

    fwd_tokens = enc.encode(text)
    rev_tokens = enc.encode(rev)

    print(f"Forward:  \"{text}\"")
    print(f"Reversed: \"{rev}\"")
    print(f"Length:   {len(text)}")
    print(f"Forward tokens:  {len(fwd_tokens)} -> {fwd_tokens}")
    print(f"Reversed tokens: {len(rev_tokens)} -> {rev_tokens}")
    print(f"Ratio:   {len(text)/len(fwd_tokens):.2f}")
    print(f"Same count:      {len(fwd_tokens) == len(rev_tokens)}")
    print(f"Different IDs:   {fwd_tokens != rev_tokens}")
    print(f"Different text:  {text != rev}")
    print(f"All alnum/space: {all(c.isalnum() or c == ' ' for c in text)}")


if __name__ == "__main__":
    solve_local()
