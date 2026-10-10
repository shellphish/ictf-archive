#!/usr/bin/env python3
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: net_connect.py <host:port>")
        return
    target = sys.argv[1]
    subprocess.call("nc -zv " + target, shell=True)

if __name__ == "__main__":
    main()
