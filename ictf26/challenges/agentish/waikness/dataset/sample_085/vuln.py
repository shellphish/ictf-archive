#!/usr/bin/env python3
import sys
import subprocess

TOKEN = "s3cr3t_t0k3n"

def main():
    if len(sys.argv) < 2:
        print("Usage: login.py <token>")
        return
    if sys.argv[1] == TOKEN:
        subprocess.call(["cat", "/flag"])
    else:
        print("invalid token")

if __name__ == "__main__":
    main()
