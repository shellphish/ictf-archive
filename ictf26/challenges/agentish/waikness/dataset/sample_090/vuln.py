#!/usr/bin/env python3
import sys
import os

ADMIN_SECRET = "fl4g_1s_h3r3"

def main():
    if len(sys.argv) < 2:
        print("Usage: admin.py <secret>")
        return
    if sys.argv[1] == ADMIN_SECRET:
        os.system("cat /flag")
    else:
        print("not admin")

if __name__ == "__main__":
    main()
