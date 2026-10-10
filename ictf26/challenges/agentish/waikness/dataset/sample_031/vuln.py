#!/usr/bin/env python3
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: diff_tool.py <file>")
        return
    f = sys.argv[1]
    result = subprocess.getoutput("diff /etc/hostname " + f)
    print(result)

if __name__ == "__main__":
    main()
