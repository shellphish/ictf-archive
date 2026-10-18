# ftp — iCTF 2003

**Competition:** iCTF 2003 "Windows Goes Open-Source" (November 2003, Giovanni Vigna / UCSB)
**Category:** network
**Format:** Attack-defense service

## Overview

A custom FTP server written in C (`ftpd.c`). Teams stored flags in the service and
the scorebot retrieved them. The server implements a subset of FTP commands with
non-standard behaviors intentionally designed for the competition.

## Non-Standard FTP Behaviors

| Command | Behavior |
|---------|----------|
| `APPE` | Returns the stored flag in the `200` response (no file transfer) |
| `STAT <flag>` | Stores a new flag value |
| `PASV` | Always returns `500` (no passive mode) |
| `CWD /etc` | Returns `550 Access denied` |
| `CWD /bin/login` | Returns `550 Access denied` |

## Vulnerability

The flag is stored in a file whose name is XOR-encoded in the binary
(`filename_encoded` array). `BYPASSWORD` in the source is the hardcoded auth bypass.
The server handles user authentication by looking up `/etc/passwd` entries
(`getpwnam(user)`) and performing `setuid`/`setgid` to the matching user.

## Files

| File | Description |
|------|-------------|
| `src/ftpd.c` | Final deployed server source (19.5 KB) |
| `src/weirdftp.c` | Earlier development version (19.5 KB) |
| `src/encode` | Flag/password encoding binary |
| `src/get_ftp` | Scorebot flag retrieval script |
| `src/set_ftp` | Scorebot flag update script |
| `src/setup.sh` | VM deployment script |
| `src/init_ftp` | Service init script |

## Notes

- Source extracted from the CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The `vsftpd` binary is also present in `/usr/sbin/vsftpd` on the VM, but this
  service used the custom `ftpd` daemon at a non-standard port.
