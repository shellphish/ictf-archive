#!/usr/bin/env python3
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: traceroute.py <host>")
        return
    host = sys.argv[1]
    subprocess.call(f"traceroute {host}", shell=True)

if __name__ == "__main__":
    main()
