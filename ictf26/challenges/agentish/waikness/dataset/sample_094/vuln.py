#!/usr/bin/env python3
import sys
import subprocess

SVC_KEY = "svc-xT8kP3mL9nW"

def main():
    if len(sys.argv) < 2:
        print("Usage: service_auth.py <key>")
        return
    if sys.argv[1] == SVC_KEY:
        subprocess.call(["cat", "/flag"])
    else:
        print("unauthorized")

if __name__ == "__main__":
    main()
