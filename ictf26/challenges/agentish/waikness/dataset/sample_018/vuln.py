#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: ping_host.py <hostname>")
        return
    host = sys.argv[1]
    os.system(f"ping -c 1 {host}")

if __name__ == "__main__":
    main()
