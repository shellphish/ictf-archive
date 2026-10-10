#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: word_count.py <file>")
        return
    filename = sys.argv[1]
    os.system("wc -l " + filename)

if __name__ == "__main__":
    main()
