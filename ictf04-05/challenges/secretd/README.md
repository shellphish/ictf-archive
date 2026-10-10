# iCTF 2005 — Secret Storage Daemon (secretd)

**Edition:** iCTF 2005 (Bass Tard Corporation rematch)
**Category:** binary
**Language:** C (autoconf)

## Description

A C daemon with separate public and private interfaces (`secretd.public`,
`secretd.private`) for secure secret storage. Find a vulnerability to
read privileged data without authorization.

## Environment

```bash
docker build -t ictf0405-secretd .
docker run -p 7004:7004 ictf0405-secretd
```

## Files

| Path | Description |
|------|-------------|
| `src/secretd.public` | Public interface source |
| `src/secretd.private` | Private interface source |

## Writeup

See [`writeup/`](writeup/).
