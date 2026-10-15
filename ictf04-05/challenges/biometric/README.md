# iCTF 2004-05 — Biometric File Service

**Edition:** iCTF 2004-05 (Bass Tard Corporation rematch, June 2005)
**Category:** binary / web (CGI)
**Language:** C
**Interface:** HTTP CGI (Apache)

## Description

`biometric` is a CGI binary deployed as a web service on the Bass Tard
Corporation server. It simulates "biometric authentication" — users supply
a corporate password and an operation to access a file store.

The CGI is called with three arguments:
- `argv[1]` — username / filename
- `argv[2]` — corporate password (`miconsenta` hardcoded)
- `argv[3]` — operation string (`OP-query`, `OP-store`, or arbitrary)

## Known Vulnerabilities

Three vulnerabilities were present in the competition binary:

1. **Format string — unknown operation path** (`printf(operation)` at line
   ~50): When the operation is not `query` or `store`, the `OP-` prefix
   is stripped and the remainder is passed directly to `printf` as a format
   string. Supplying `OP-%08x.%08x` reads stack values.

2. **Format string — wrong password path** (`printf(argv[2])` at line ~60):
   When the corporate password does not match, `argv[2]` is used as the
   format string. An attacker who controls the HTTP GET parameter can
   exploit this without knowing the password.

3. **Unsanitized path in `execlp`**: After successful authentication,
   `execlp("touch", "touch", argv[1], 0)` is called with the raw username
   argument. A path containing `../` escapes the intended directory.

Scorebot password: `putyourfingerhere`

## Files

| Path | Description |
|------|-------------|
| `src/biometric.c` | Full CGI binary source (C, 69 lines) |

## Environment

```bash
docker build -t ictf0405-biometric .
docker run -p 80:80 ictf0405-biometric
```

## Writeup

See [`writeup/`](writeup/).
