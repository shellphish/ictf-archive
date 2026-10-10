#!/usr/bin/env python3
"""
Gaslights, Camera, ACTION — Solver
Extracts the flag from the PDF using multiple methods.

Usage:
    python3 writeup/solve.py [path/to/iCTF_Planning_Document_2026_FINAL.pdf]
"""

import re
import subprocess
import sys


FLAG_RE = re.compile(r"ictf\{[^}]+\}", re.IGNORECASE)


def try_strings(pdf_path: str) -> str | None:
    """Search raw bytes for flag pattern."""
    with open(pdf_path, "rb") as f:
        content = f.read().decode("latin-1", errors="replace")
    m = FLAG_RE.search(content)
    return m.group(0) if m else None


def try_pdftotext(pdf_path: str) -> str | None:
    """Extract text via pdftotext and search."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True, text=True, check=True
        )
        m = FLAG_RE.search(result.stdout)
        return m.group(0) if m else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def try_pymupdf(pdf_path: str) -> str | None:
    """Extract all text including hidden layers via PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text")
            # Also check annotations
            for annot in page.annots():
                text += annot.info.get("content", "")
        m = FLAG_RE.search(text)
        return m.group(0) if m else None
    except ImportError:
        return None


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "iCTF_Planning_Document_2026_FINAL.pdf"

    print(f"[*] Analyzing {pdf_path}")

    for method, fn in [
        ("raw strings", lambda: try_strings(pdf_path)),
        ("pdftotext", lambda: try_pdftotext(pdf_path)),
        ("PyMuPDF", lambda: try_pymupdf(pdf_path)),
    ]:
        print(f"[*] Trying {method}...")
        flag = fn()
        if flag:
            print(f"[+] Flag ({method}): {flag}")
            return

    print("[-] Flag not found automatically.")
    print("    Try: strings <pdf> | grep -i ictf")
    print("    Or:  pdfimages -all <pdf> out/")


if __name__ == "__main__":
    main()
