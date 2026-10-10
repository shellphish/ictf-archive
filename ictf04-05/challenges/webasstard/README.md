# iCTF 2005 — Web Interface (webasstard)

**Edition:** iCTF 2005 (Bass Tard Corporation rematch)
**Category:** web

## Description

The web front-end for the Bass Tard Corporation's remote admin platform.
Includes biometric authentication integration. Source includes pre-compiled
biometric binaries for Linux and macOS.

## Environment

```bash
docker build -t ictf0405-webasstard .
docker run -p 8080:80 ictf0405-webasstard
```

## Files

| Path | Description |
|------|-------------|
| `src/index.html` | Main page |
| `src/basstard.css` | Stylesheet |
| `src/biometric` / `src/biometric-linux` | Biometric binary |

## Writeup

See [`writeup/`](writeup/).
