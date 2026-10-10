# iCTF 2005 — Bass Re-Tard Remote Admin (bassretard)

**Edition:** iCTF 2005 (Bass Tard Corporation rematch)
**Category:** binary
**Language:** C (autoconf)

## Description

The **Bass Re-Tard (BRT)** is a network daemon providing remote system
administration for the Bass Tard Corporation. According to its README:

> *"The BRT code has been analyzed by a number of security experts and it
> is considered to be free from any vulnerability. Formal verification with
> a number of analysis tools was also performed. The analysis found no
> vulnerabilities. Feel free to install the code on your system..."*

Find the vulnerability and exploit it.

## Environment

```bash
docker build -t ictf0405-bassretard .
docker run -p 7000:7000 ictf0405-bassretard
```

## Files

| Path | Description |
|------|-------------|
| `src/bassretard.c` | Main service source |
| `src/bassretard.sh` | Service launcher |
| `src/basstard.css` | Web UI stylesheet |

## Writeup

See [`writeup/`](writeup/).
