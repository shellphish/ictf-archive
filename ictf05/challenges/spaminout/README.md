# iCTF 2005 — Spam In/Out Gateway (spaminout)

**Edition:** iCTF 2005 — The Spam Museum
**Category:** binary
**Language:** C (autoconf)

## Description

A C network daemon acting as a spam routing gateway — receiving spam
from external sources and relaying it to target addresses. Part of
the Spam Museum themed infrastructure.

## Environment

```bash
docker build -t ictf05-spaminout .
docker run -p 7101:7101 ictf05-spaminout
```

## Files

| Path | Description |
|------|-------------|
| `src/` | Full autoconf source tree |

## Writeup

See [`writeup/`](writeup/).
