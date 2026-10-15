# ftp — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, UCSB)
**Category:** network / pwn
**Format:** Attack-defense service

## Overview

A custom C FTP server (anonymous login) hosting the spam museum's FTP archive.
Flags are stored as files uploaded to `/home/ftp/incoming/` via standard `STOR`.
The scorebot stores the flag as a randomly-named file and retrieves it by `RETR`.

## Architecture

```
TCP port 21 (control) / 2020 (data passive)
Anonymous FTP: USER anonymous, no password required
STOR <filename>   — upload file to /home/ftp/incoming/
RETR <filename>   — download file from /home/ftp/incoming/
```

The server is a custom implementation in C (`ftpd.c`, ~500 lines),
loosely based on standard FTP but simplified.

## Vulnerability

The server is a custom C FTP implementation. Potential vulnerabilities
include buffer overflows in command parsing (fixed-size `char buf[]` with
`gets()`-style input), path traversal via `../` in filenames, and
potential format string bugs in the `reply()` function.

Reading all files from `incoming/` (via `LIST` + `RETR`) directly
gives an attacker access to every team's stored flags.

## Files

| File | Description |
|------|-------------|
| `src/ftpd.c` | Custom C FTP server source code |
| `src/ftpd` | Compiled FTP server binary (32-bit ELF) |
| `src/ftpScoringScript.py` | Scorebot flag set/get script |

## Notes

- Source extracted from CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- A similar custom FTP server appeared in ictf03; the vulnerability pattern is
  analogous but the flag storage/retrieval protocol differs (STOR/RETR here vs.
  APPE/STAT in ictf03).
