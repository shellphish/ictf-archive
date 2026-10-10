# iCTF 2005 — Silly Auth Server (sillyd)

**Edition:** iCTF 2005 (Bass Tard Corporation rematch)
**Category:** binary / pwn
**Language:** C
**Port:** 12345/tcp

## Description

A C authentication daemon with REG/AUTH/REVOKE/STATUS/PING/QUIT commands.
Stores auth tokens in files under `data/`. Results prefixed `+` (success)
or `-` (failure).

## Known Vulnerabilities

Per the original `sillyd.txt` disclosure (see `src/sillyd.txt`):

1. **Shell injection via AUTH token (line 34)** — if an auth token is valid
   but too long, the `id` and `cmdbuf` variables merge into one string,
   allowing extra arguments to be passed to `grep` (or the shell) invoked
   via `system(2)`.

2. **PING buffer overflow (line 144)** — the PING command uses a `char*`
   pointer where `int*` is expected. If PING is sent without a trailing
   `\r\n`, the `bp` size variable overflows, enabling a buffer overflow via
   `read(2)`.

## Environment

```bash
docker build -t ictf0405-sillyd .
docker run -p 12345:12345 ictf0405-sillyd
nc localhost 12345
```

## Files

| Path | Description |
|------|-------------|
| `src/sillyd.c` | Full service source |
| `src/sillyd.txt` | Original vulnerability disclosure |
| `src/sample_exploit/sillyd_test.c` | Proof-of-concept exploit |

## Writeup

The original vulnerability disclosure is in `src/sillyd.txt`.
See [`writeup/`](writeup/) for the full solution.
