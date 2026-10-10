# iCTF 2005 — CC Auth Daemon (ccauthd)

**Edition:** iCTF 2005 (Bass Tard Corporation rematch)
**Category:** binary
**Language:** C

## Description

A simple C authentication daemon with a text-based protocol:
- `REG <user> <pass>` — register
- `AUTH <user> <pass>` — authenticate
- `REVOKE <user>` — revoke credentials
- `STATUS` — service status
- `PING` / `QUIT`

Responses prefixed `+` (success) or `-` (failure).

## Environment

```bash
docker build -t ictf0405-ccauthd .
docker run -p 7002:7002 ictf0405-ccauthd
nc localhost 7002
```

## Files

| Path | Description |
|------|-------------|
| `src/ccauthd.c` | Full service source |
| `src/Makefile` | Build file |

## Writeup

See [`writeup/`](writeup/).
