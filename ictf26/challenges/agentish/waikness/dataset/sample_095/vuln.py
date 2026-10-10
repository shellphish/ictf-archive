#!/usr/bin/env python3
import sys
import os

INTERNAL_TOKEN = "Int3rn@l_0nly"

def main():
    if len(sys.argv) < 2:
        print("Usage: internal_api.py <token>")
        return
    if sys.argv[1] == INTERNAL_TOKEN:
        os.system("cat /flag")
    else:
        print("rejected")

if __name__ == "__main__":
    main()
