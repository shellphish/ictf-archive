#!/usr/bin/env python3
import sys
import os

API_KEY = "xK9mP2vL8nQ4rT6w"

def main():
    if len(sys.argv) < 2:
        print("Usage: verify.py <key>")
        return
    if sys.argv[1] == API_KEY:
        os.system("cat /flag")
    else:
        print("invalid key")

if __name__ == "__main__":
    main()
