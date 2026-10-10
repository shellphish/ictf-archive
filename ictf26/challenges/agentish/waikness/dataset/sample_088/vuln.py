#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: backdoor.py <magic>")
        return
    magic = "hunter2"
    if sys.argv[1] == magic:
        os.system("cat /flag")
    else:
        print("no")

if __name__ == "__main__":
    main()
