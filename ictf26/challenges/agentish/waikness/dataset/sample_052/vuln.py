#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: cat_doc.py <document>")
        return
    doc = sys.argv[1]
    path = os.path.join("/home/user/documents", doc)
    try:
        with open(path) as f:
            print(f.read())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
