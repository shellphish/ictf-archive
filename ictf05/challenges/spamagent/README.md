# iCTF 2005 — Spam Agent (spamagent)

**Edition:** iCTF 2005 — The Spam Museum
**Category:** binary
**Language:** C (autoconf)

## Description

A C network daemon modeling a spam delivery agent. Part of the Spam Museum
themed iCTF 2005, where teams attacked and defended spam infrastructure.

## Environment

```bash
docker build -t ictf05-spamagent .
docker run -p 7100:7100 ictf05-spamagent
```

## Files

| Path | Description |
|------|-------------|
| `src/` | Full autoconf source tree |

## Writeup

See [`writeup/`](writeup/).
