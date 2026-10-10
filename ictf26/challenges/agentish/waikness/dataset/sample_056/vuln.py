#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: view_report.py <report>")
        return
    report = sys.argv[1]
    path = "/opt/reports/" + report
    try:
        with open(path) as f:
            print(f.read())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
