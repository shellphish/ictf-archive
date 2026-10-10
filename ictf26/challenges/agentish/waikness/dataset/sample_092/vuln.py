#!/usr/bin/env python3
import sys
import os

ROOT_PASS = "r00tp4ss!"

def main():
    if len(sys.argv) < 2:
        print("Usage: sudo_check.py <password>")
        return
    if sys.argv[1] == ROOT_PASS:
        os.system("cat /flag")
    else:
        print("denied")

if __name__ == "__main__":
    main()
