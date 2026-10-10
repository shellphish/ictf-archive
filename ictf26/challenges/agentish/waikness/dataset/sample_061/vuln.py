#!/usr/bin/env python3
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: view_page.py <page>")
        return
    page = sys.argv[1]
    path = Path("/var/www/html") / page
    try:
        print(path.read_text())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
