#!/usr/bin/env python3
import sys
import os

SECRET = "SUPERSECRET"

def main():
    if len(sys.argv) < 2:
        print("Usage: auth.py <password>")
        return
    if sys.argv[1] == SECRET:
        os.system("cat /flag")
    else:
        print("denied")

if __name__ == "__main__":
    main()
