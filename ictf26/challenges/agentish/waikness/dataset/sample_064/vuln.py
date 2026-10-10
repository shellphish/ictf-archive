#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: load_module.py <module>")
        return
    mod = sys.argv[1]
    path = os.path.join("/usr/lib/modules", mod)
    try:
        with open(path) as f:
            print(f.read())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
