# sts-stock — iCTF 2006

**Competition:** iCTF 2006 "The Hillbilly Bank" (December 8, 2006, UCSB Frank Hall)
**Category:** binary / c++
**Format:** Attack-defense service
**Port:** 1337 (HTTP, lighttpd CGI)

## Overview

The Hillbilly Bank Stock Trading Service is a C++ CGI binary (`stocks`) served by
lighttpd on port 1337. The binary (2 MB) handles stock quote lookups, comments,
and account management. The lighttpd config maps requests for `/stocks` to the
CGI binary.

## Architecture

```
http://<host>:1337/cgi-bin/stocks    — main CGI endpoint
```

The service stores state in two directories under `/home/sts/`:
- `accounts/` — user account data
- `comments/` — user comments (timestamped `.txt` files)

Source file `stock_service.cpp` (20 KB) implements the complete service.

## Files

| File | Description |
|------|-------------|
| `src/stock_service.cpp` | C++ source for the stock CGI binary |
| `src/lighttpd.conf` | lighttpd config (port 1337, CGI assignment) |
| `src/init_bts` | init script (bts, not sts — likely shared or typo) |

## Notes

- Source extracted from the CTF VM (Ubuntu Dapper, VMware VMDK) via `qemu-img` + `debugfs`.
- The compiled binary (`stocks`, 2044309 bytes) was at `/home/sts/public_html/cgi-bin/stocks`.
- The binary was not preserved in the archive (too large); only the C++ source is kept.
- Analyze `stock_service.cpp` for CGI input handling vulnerabilities (buffer overflows,
  format strings, or path traversal in the comment/account file paths).
