#!/usr/bin/env python3
"""
Bits of Scan-dalous QRiosity Part 2 — Solver
Steps:
  1. Extract frames from CueAres.zip
  2. Median-stack the frames to remove noise
  3. Extract LSB plane from the red channel → hidden image
  4. Decode the QR code from the hidden image

Usage:
    python3 writeup/solve.py [path/to/CueAres.zip]
"""

import io
import os
import sys
import zipfile
import math

from PIL import Image


def median_stack(images: list) -> Image.Image:
    """Pixel-wise median across a list of RGB images."""
    import statistics

    w, h = images[0].size
    result = Image.new("RGB", (w, h))
    pixels_list = [list(img.getdata()) for img in images]

    out_pixels = []
    for i in range(w * h):
        r = statistics.median(p[i][0] for p in pixels_list)
        g = statistics.median(p[i][1] for p in pixels_list)
        b = statistics.median(p[i][2] for p in pixels_list)
        out_pixels.append((int(r), int(g), int(b)))

    result.putdata(out_pixels)
    return result


def extract_lsb_plane(img: Image.Image) -> Image.Image:
    """Extract the LSB of the red channel as a greyscale image."""
    pixels = list(img.getdata())
    lsb = [(r & 1) * 255 for r, g, b in pixels]
    out = Image.new("L", img.size)
    out.putdata(lsb)
    return out


def decode_qr(img: Image.Image) -> str:
    try:
        from pyzbar.pyzbar import decode
        results = decode(img)
        if results:
            return results[0].data.decode("utf-8")
    except ImportError:
        pass

    try:
        import cv2
        import numpy as np
        arr = np.array(img.convert("L"))
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(arr)
        if data:
            return data
    except ImportError:
        pass

    return ""


def main():
    zip_path = sys.argv[1] if len(sys.argv) > 1 else "CueAres.zip"

    print(f"[*] Loading frames from {zip_path}...")
    images = []
    with zipfile.ZipFile(zip_path) as zf:
        for name in sorted(zf.namelist()):
            if name.lower().endswith((".png", ".jpg", ".jpeg")):
                data = zf.read(name)
                images.append(Image.open(io.BytesIO(data)).convert("RGB"))

    print(f"[*] Loaded {len(images)} frames")

    print("[*] Median stacking...")
    stacked = median_stack(images)
    stacked.save("stacked.png")
    print("[+] Saved stacked.png")

    print("[*] Extracting LSB plane...")
    lsb = extract_lsb_plane(stacked)
    lsb.save("hidden.png")
    print("[+] Saved hidden.png")

    print("[*] Decoding QR code...")
    flag = decode_qr(lsb)
    if flag:
        print(f"[+] Flag: {flag}")
    else:
        print("[-] Could not auto-decode QR. Open hidden.png manually.")


if __name__ == "__main__":
    main()
