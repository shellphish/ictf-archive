#!/usr/bin/env python3
"""
Bits of Scan-dalous QRiosity Part 1 — Solver
Extracts the flag hidden via LSB steganography in the red channel of 1obfus.png.

Usage:
    python3 writeup/solve.py [path/to/1obfus.png]
"""

import sys
from PIL import Image


def extract_lsb(image_path: str) -> str:
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    bits = [r & 1 for r, g, b in pixels]

    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i : i + 8]
        val = int("".join(str(b) for b in byte), 2)
        if val == 0:
            break
        chars.append(chr(val))

    return "".join(chars)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "1obfus.png"
    data = extract_lsb(path)

    idx = data.find("iCTF=")
    if idx == -1:
        idx = data.find("ictf{")
    if idx != -1:
        end = data.find("}", idx)
        print("Flag:", data[idx : end + 1] if end != -1 else data[idx : idx + 40])
    else:
        print("Hidden data:", data[:200])


if __name__ == "__main__":
    main()
