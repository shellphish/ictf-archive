# etj-transactions — iCTF 2006

**Competition:** iCTF 2006 "The Hillbilly Bank" (December 8, 2006, UCSB Frank Hall)
**Category:** network / python
**Format:** Attack-defense service
**Port:** 44000 (TCP)

## Overview

The "Hillbilly Translator" service (`etj`) is a Python 2 TCP server that handles
inter-bank transaction relay. It listens on TCP port 44000 using a custom server
class `TServer` from the `tlib` module.

## Architecture

```python
from tlib import *
t = TServer(('', 44000), T)
t.state = State()
t.serve_forever()
```

The service uses a `tlib` module (not preserved in the archive) that implements
a custom TCP server framework with state management.

## Files

| File | Description |
|------|-------------|
| `src/trans.py` | Service entry point (106 bytes) |
| `src/init_etj` | `/etc/init.d/etj` service init script |

## Notes

- Source extracted from the CTF VM (Ubuntu Dapper, VMware VMDK) via `qemu-img` + `debugfs`.
- `trans.py` is a 106-byte stub — the actual service logic is in `tlib.py` and the
  handler class `T`, neither of which was found in `/home/etj/`. They may have been
  installed system-wide or are missing from the archive.
- The init script description calls this the "Hillbilly translator service", suggesting
  it translates or relays financial messages between bank components.
