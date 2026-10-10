#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: checksum.py <file>")
        return
    f = sys.argv[1]
    os.system(f"md5sum {f}")

if __name__ == "__main__":
    main()
