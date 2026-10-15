# spamometer — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, UCSB)
**Category:** pwn
**Format:** Attack-defense service

## Overview

A binary service (22KB ELF) that measures spam volume or quality metrics.
The service binary (`spamometer`) is deployed to the `/home/spamometer/`
user account. Source code was not recovered from the VM — the source archive
`/root/spamometer-1.0.tar.gz.gpg` is GPG-encrypted.

## Files

| File | Description |
|------|-------------|
| `src/spamometer` | Compiled spamometer binary (32-bit ELF, 22KB) |

## Notes

- Source code unavailable: `/root/spamometer-1.0.tar.gz.gpg` in the VM is
  GPG-encrypted with an unknown key.
- The binary was extracted from the deployed CTF VM (RedHat 9, VMware VMDK)
  via `qemu-img` + `debugfs`.
- Reverse engineering the binary is required to understand the service protocol
  and discover vulnerabilities.
