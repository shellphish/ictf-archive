#!/usr/bin/env python3
"""
Blackout Memo — Solver
Extracts all embedded images from a PDF and searches for the flag.

Usage:
    python3 writeup/solve.py [path/to/confidential_email.pdf]

Requires: pdfimages (poppler-utils) or PyMuPDF (pip install pymupdf)
"""

import os
import re
import subprocess
import sys
import tempfile


FLAG_RE = re.compile(r"ictf\{[^}]+\}", re.IGNORECASE)


def try_pdfimages(pdf_path: str, out_dir: str) -> list[str]:
    """Use pdfimages to extract all embedded images."""
    try:
        subprocess.run(
            ["pdfimages", "-all", pdf_path, os.path.join(out_dir, "img")],
            check=True,
            capture_output=True,
        )
        return [os.path.join(out_dir, f) for f in os.listdir(out_dir)]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def try_strings(pdf_path: str) -> str | None:
    """Search for flag pattern directly in the raw PDF bytes."""
    with open(pdf_path, "rb") as f:
        content = f.read().decode("latin-1", errors="replace")
    m = FLAG_RE.search(content)
    return m.group(0) if m else None


def try_pymupdf(pdf_path: str, out_dir: str) -> list[str]:
    """Use PyMuPDF to extract images."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        extracted = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                path = os.path.join(out_dir, f"img_{page_num}_{img_index}.{base_image['ext']}")
                with open(path, "wb") as f:
                    f.write(base_image["image"])
                extracted.append(path)
        return extracted
    except ImportError:
        return []


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "src/confidential_email.pdf"

    # Method 1: raw string search
    print("[*] Searching raw PDF for flag pattern...")
    flag = try_strings(pdf_path)
    if flag:
        print(f"[+] Found in raw PDF: {flag}")
        return

    with tempfile.TemporaryDirectory() as tmp:
        # Method 2: pdfimages
        print("[*] Extracting images with pdfimages...")
        files = try_pdfimages(pdf_path, tmp)
        if not files:
            # Method 3: PyMuPDF
            print("[*] Trying PyMuPDF...")
            files = try_pymupdf(pdf_path, tmp)

        if files:
            print(f"[+] Extracted {len(files)} image(s):")
            for f in sorted(files):
                print(f"    {f}")
            print("[*] Open the extracted images to find the flag.")
        else:
            print("[-] No images extracted. Try: pdfimages -all <pdf> out/")
            print("    Or install: sudo apt install poppler-utils")


if __name__ == "__main__":
    main()
