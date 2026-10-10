#!/usr/bin/env python3
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: show_stat.py <path>")
        return
    p = sys.argv[1]
    result = subprocess.getoutput("stat " + p)
    print(result)

if __name__ == "__main__":
    main()
