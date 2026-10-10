#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: show_perms.py <path>")
        return
    path = sys.argv[1]
    output = os.popen(f"ls -la {path}").read()
    print(output)

if __name__ == "__main__":
    main()
