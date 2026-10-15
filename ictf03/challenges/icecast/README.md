# icecast — iCTF 2003

**Competition:** iCTF 2003 "Windows Goes Open-Source" (November 2003, UCSB)
**Category:** web / network
**Format:** Attack-defense service

## Overview

An Icecast 2.0-beta-1 streaming audio server, patched to embed the flag in a
custom field of the socket layer. The flag was accessible via HTTP at the Icecast
port (8000). The competition theme had teams hosting "streaming audio" that was
really a Windows Media Player clone powered by open-source software.

## Architecture

```
http://<host>:8000/flag    — retrieve the flag (GET, no auth)
```

The Icecast server was patched: `sock.c` was modified to embed the flag as a
global string (`g_client_hash = "##ICECAST_FLAG##"` → replaced at deploy time),
which Icecast serves at the `/flag` URL path.

The scorebot retrieves the flag via `wget -q -O - http://<host>:8000/flag`.

## Deployment

`setup.sh` patches `icecast-2.0-beta-1/src/net/sock.c` with the flag value
via `sed`, compiles from source (autoconf/make), and installs the binary.
The icecast XML config (`icecast.xml`) sets the admin password (`##ICECAST_PASSWD##`).

## Files

| File | Description |
|------|-------------|
| `src/sock.c` | Modified icecast sock.c embedding the flag |
| `src/set_icecast.c` | Admin flag-update script source (C) |
| `src/set_icecast` | Compiled set_icecast binary (32-bit ELF) |
| `src/get_icecast` | Scorebot flag retrieval script (Perl, uses wget) |
| `src/icecast.xml` | Icecast configuration template |
| `src/icecast.xml.deployed` | Actual deployed config from CTF VM |
| `src/icecast-2.0-beta-1/` | Full Icecast 2.0-beta-1 source tree |
| `src/setup.sh` | VM deployment script |
| `src/init_icecast`, `src/init_ices` | Service init scripts |

## Notes

- Source extracted from the CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The icecast binary in `/usr/local/bin/icecast` (674 KB) and `ices` binary (1.2 MB)
  were present on the VM and are the compiled versions of this service.
- Vulnerability: the `set_icecast.c` admin script calls `wget` to update the flag
  via the Icecast HTTP admin interface; if the admin password can be read from
  `icecast.xml`, an attacker can update any team's flag.
