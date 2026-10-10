#!/usr/bin/env python3
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: disk_usage.py <path>")
        return
    path = sys.argv[1]
    subprocess.call("du -sh " + path, shell=True)

if __name__ == "__main__":
    main()
