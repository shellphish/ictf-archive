#!/usr/bin/env python3
import sys
import hashlib
import os

STORED_HASH = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"

def main():
    if len(sys.argv) < 2:
        print("Usage: pin_check.py <pin>")
        return
    h = hashlib.sha256(sys.argv[1].encode()).hexdigest()
    if h == STORED_HASH:
        os.system("cat /flag")
    else:
        print("wrong pin")

if __name__ == "__main__":
    main()
