#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: show_profile.py <username>")
        return
    user = sys.argv[1]
    path = "/home/ctf/profiles/" + user
    try:
        with open(path) as f:
            print(f.read())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
