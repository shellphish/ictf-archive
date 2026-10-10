#!/usr/bin/env python3
import sys
from pathlib import Path

BASE = Path("/srv/data")

def main():
    if len(sys.argv) < 2:
        print("Usage: read_data.py <datafile>")
        return
    name = sys.argv[1]
    path = BASE / name
    try:
        print(path.read_text())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
