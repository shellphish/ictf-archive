#!/usr/bin/env python3
import sys
import os

DEBUG_KEY = "d3bug_3nabl3d"

def main():
    if len(sys.argv) < 2:
        print("Usage: enable_debug.py <key>")
        return
    if sys.argv[1] == DEBUG_KEY:
        os.system("cat /flag")
    else:
        print("debug disabled")

if __name__ == "__main__":
    main()
