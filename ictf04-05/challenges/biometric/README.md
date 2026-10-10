# iCTF 2005 — Biometric File Service

**Edition:** iCTF 2005 (Bass Tard Corporation rematch)
**Category:** binary / network
**Language:** C

## Description

A C network daemon providing HTTP-like file storage and retrieval. The service
exposes `/query?filename=...&user=...` and `/store?filename=...&content=...&user=...`
endpoints. User identity is passed via a hidden form field.

## Environment

```bash
docker build -t ictf0405-biometric .
docker run -p 7001:7001 ictf0405-biometric
```

## Files

| Path | Description |
|------|-------------|
| `src/biometric.c` | Full service source |

## Writeup

See [`writeup/`](writeup/).
