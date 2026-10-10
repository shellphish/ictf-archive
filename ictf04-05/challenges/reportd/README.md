# iCTF 2005 — Report Filing Daemon (reportd)

**Edition:** iCTF 2005 (Bass Tard Corporation rematch)
**Category:** binary
**Language:** C

## Description

A C network daemon that accepts and stores textual reports to a flat file
(`report.data`) using file locking. Uses a custom alphanumeric character
encoding table.

## Environment

```bash
docker build -t ictf0405-reportd .
docker run -p 7003:7003 ictf0405-reportd
```

## Files

| Path | Description |
|------|-------------|
| `src/reportd.c` | Full service source |
| `src/Makefile` | Build file |

## Writeup

See [`writeup/`](writeup/).
