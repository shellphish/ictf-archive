#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: archive.py <dir>")
        return
    d = sys.argv[1]
    os.system(f"tar -czf output.tar.gz {d}")

if __name__ == "__main__":
    main()
