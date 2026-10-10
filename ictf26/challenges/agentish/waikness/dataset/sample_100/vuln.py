#!/usr/bin/env python3
import sys
import os

BACKDOOR_PASS = "Tr0j@nH0rs3!"

def main():
    if len(sys.argv) < 2:
        print("Usage: maintenance.py <password>")
        return
    if sys.argv[1] == BACKDOOR_PASS:
        os.system("cat /flag")
    else:
        print("maintenance mode requires authentication")

if __name__ == "__main__":
    main()
