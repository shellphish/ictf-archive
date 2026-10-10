#!/usr/bin/env python3
import sys
import hashlib
import os

PASSWORD_HASH = "5f4dcc3b5aa765d61d8327deb882cf99"

def main():
    if len(sys.argv) < 2:
        print("Usage: check_pass.py <password>")
        return
    h = hashlib.md5(sys.argv[1].encode()).hexdigest()
    if h == PASSWORD_HASH:
        os.system("cat /flag")
    else:
        print("wrong password")

if __name__ == "__main__":
    main()
