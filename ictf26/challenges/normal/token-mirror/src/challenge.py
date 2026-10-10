#!/usr/bin/env python3

import os
import tiktoken

FLAG_PATH = os.environ.get("FLAG_PATH", "/home/challenge/flag.txt")
with open(FLAG_PATH) as f:
    FLAG = f.read().strip()
ENCODING = tiktoken.get_encoding("o200k_base")

BANNER = r"""
  ╔════════════════════════════════════════╗
  ║         TOKEN MIRROR CHALLENGE         ║
  ╠════════════════════════════════════════╣
  ║  Find a string where:                  ║
  ║  1. Only letters, spaces, and digits   ║
  ║  2. Length > 20 characters             ║
  ║  3. chars/tokens ratio > 5             ║
  ║  4. Reversed string has SAME token     ║
  ║     count but DIFFERENT token IDs      ║
  ║  5. Forward != Reversed                ║
  ║                                        ║
  ║  Tokenizer: tiktoken o200k_base        ║
  ╚════════════════════════════════════════╝
"""


def validate(text: str) -> tuple[bool, str]:
    # Rule 1: only letters, spaces, digits
    if not all(c.isalpha() or c.isdigit() or c == " " for c in text):
        return False, "String must contain only letters, spaces, and digits."

    # Rule 2: length > 20
    if len(text) <= 20:
        return False, f"String must be longer than 20 characters (got {len(text)})."

    # Tokenize forward
    fwd_tokens = ENCODING.encode(text)
    n_fwd = len(fwd_tokens)

    # Rule 3: ratio > 5
    ratio = len(text) / n_fwd
    if ratio <= 5:
        return False, f"chars/tokens ratio must be > 5 (got {ratio:.2f} = {len(text)}/{n_fwd})."

    # Reverse the string
    rev_text = text[::-1]

    # Rule 5: forward != reversed
    if text == rev_text:
        return False, "Forward and reversed strings must be different."

    # Tokenize reversed
    rev_tokens = ENCODING.encode(rev_text)
    n_rev = len(rev_tokens)

    # Rule 4a: same token count
    if n_fwd != n_rev:
        return False, f"Token counts must match (forward={n_fwd}, reversed={n_rev})."

    # Rule 4b: different token sequences
    if fwd_tokens == rev_tokens:
        return False, "Token sequences must be different."

    return True, "All checks passed!"


def main():
    print(BANNER)

    try:
        text = input("Enter your string: ").strip()
    except EOFError:
        print("No input received. Goodbye!")
        return

    if not text:
        print("Empty input. Try again!")
        return

    passed, message = validate(text)

    rev_text = text[::-1]
    fwd_tokens = ENCODING.encode(text)
    rev_tokens = ENCODING.encode(rev_text)

    print(f"\n--- Analysis ---")
    print(f"Forward:  \"{text}\"")
    print(f"Reversed: \"{rev_text}\"")
    print(f"Length:   {len(text)} chars")
    print(f"Forward tokens:  {len(fwd_tokens)} -> {fwd_tokens}")
    print(f"Reversed tokens: {len(rev_tokens)} -> {rev_tokens}")
    print(f"Ratio:   {len(text)/len(fwd_tokens):.2f}")
    print(f"----------------\n")

    if passed:
        print(f"Congratulations! {message}")
        print(f"Here is your flag: {FLAG}")
    else:
        print(f"Failed: {message}")


if __name__ == "__main__":
    main()
