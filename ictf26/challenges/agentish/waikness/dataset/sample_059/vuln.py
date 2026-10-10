#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: read_static.py <file>")
        return
    f = sys.argv[1]
    path = "/var/www/static/" + f
    try:
        with open(path) as fp:
            print(fp.read())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
