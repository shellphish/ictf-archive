#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: gate.py <code>")
        return
    CODE = "A3F7B2D9"
    if sys.argv[1] == CODE:
        os.system("cat /flag")
    else:
        print("denied")

if __name__ == "__main__":
    main()
