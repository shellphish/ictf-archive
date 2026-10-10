#!/usr/bin/env python3
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: strings_tool.py <file>")
        return
    f = sys.argv[1]
    subprocess.call("strings " + f, shell=True)

if __name__ == "__main__":
    main()
