#!/usr/bin/env python3
import sys
import hashlib
import os

MASTER_HASH = "e10adc3949ba59abbe56e057f20f883e"

def main():
    if len(sys.argv) < 2:
        print("Usage: verify_cert.py <cert>")
        return
    h = hashlib.md5(sys.argv[1].encode()).hexdigest()
    if h == MASTER_HASH:
        os.system("cat /flag")
    else:
        print("cert invalid")

if __name__ == "__main__":
    main()
