#!/usr/bin/env python3
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: log_search.py <pattern>")
        return
    pattern = sys.argv[1]
    subprocess.call("grep -r " + pattern + " /var/log/", shell=True)

if __name__ == "__main__":
    main()
