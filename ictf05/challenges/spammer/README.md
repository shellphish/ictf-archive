# spammer — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, UCSB)
**Category:** network / pwn
**Format:** Attack-defense service

## Overview

A Python network service (`spammerd.py`) implementing a custom binary "SPAM"
protocol. The service uses Python's `SocketServer` and implements a packet
field structure with Scapy-like field descriptors. Flags are stored and
retrieved via the custom protocol.

## Architecture

```
TCP service (port TBD — see scoring script)
Banner: "SPAM Server\nVersion 4.5.3 (Testing)\n"
Custom binary protocol with SPAMField, StrField, and Field types
```

The `spammerd.py` source includes full field class definitions for a binary
protocol parser. The `SPAMField` class parses option fields from a TCP-like
header structure.

## Vulnerability

The protocol implementation uses a custom parser. Vulnerabilities may include:
- Protocol confusion / malformed packet handling
- Integer overflow in field size calculations (`dataofs`)
- Option field parsing allowing injection of unexpected data

The service banner identifies itself as "Version 4.5.3 (Testing)" — the
development/test nature of the service suggests it may not have been hardened.

## Files

| File | Description |
|------|-------------|
| `src/spammerd.py` | Python SPAM protocol server (9KB) |
| `src/spammerScoringScript.py` | Scorebot flag set/get script |

## Notes

- Source extracted from CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The `spammerd.py` file uses Python 2 `SocketServer` and resembles a
  Scapy-based binary protocol implementation with custom field descriptors.
