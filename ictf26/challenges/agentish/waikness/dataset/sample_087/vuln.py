#!/usr/bin/env python3
import sys
import os
import base64

ENCODED = "b3Blbl9zZXNhbWU="

def main():
    if len(sys.argv) < 2:
        print("Usage: unlock.py <passphrase>")
        return
    expected = base64.b64decode(ENCODED).decode()
    if sys.argv[1] == expected:
        os.system("cat /flag")
    else:
        print("access denied")

if __name__ == "__main__":
    main()
