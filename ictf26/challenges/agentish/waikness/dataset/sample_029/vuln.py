#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: show_process.py <name>")
        return
    name = sys.argv[1]
    os.system("ps aux | grep " + name)

if __name__ == "__main__":
    main()
