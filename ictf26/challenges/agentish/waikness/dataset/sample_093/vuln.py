#!/usr/bin/env python3
import sys
import os
import base64

def main():
    if len(sys.argv) < 2:
        print("Usage: recover.py <phrase>")
        return
    expected = base64.b64decode("eWVsbG93LW1vb24tcml2ZXI=").decode()
    if sys.argv[1] == expected:
        os.system("cat /flag")
    else:
        print("invalid phrase")

if __name__ == "__main__":
    main()
