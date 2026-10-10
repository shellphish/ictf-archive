#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: authenticate.py <credential>")
        return
    CRED = "C0nf1dent!al"
    if sys.argv[1] == CRED:
        os.system("cat /flag")
    else:
        print("failed")

if __name__ == "__main__":
    main()
