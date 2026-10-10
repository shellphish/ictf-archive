#!/usr/bin/env python3
import sys

BASE_DIR = "/var/www/files/"

def main():
    if len(sys.argv) < 2:
        print("Usage: read_file.py <filename>")
        return
    user_input = sys.argv[1]
    path = BASE_DIR + user_input
    try:
        with open(path, "r") as f:
            print(f.read())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
