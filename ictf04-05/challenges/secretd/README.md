# iCTF 2004-05 — Secret Storage Daemon (secretd)

**Edition:** iCTF 2004-05 (Bass Tard Corporation rematch, June 2005)
**Category:** binary / crypto
**Language:** C++
**Port:** 8008/tcp (SSL/TLS)

## Description

`secretd` is a C++ SSL/TLS daemon backed by BerkeleyDB. Teams use it to
store and retrieve named secrets. Each connection is handled by a forked
child (or thread, if compiled with `USE_THREADS`).

The service uses an RSA keypair (`secretd.public` / `secretd.private`,
both included) for the TLS layer. A custom anti-tamper scheme uses a
hardcoded `CHECKSUM_KEY` (0xb976be5) and `CHECKSUM_DUMMY` (0x0100113a) —
stored entries are checked on retrieval; a corrupted or wrong-keyed entry
returns scrambled data (`SCRAMBLE` mode) rather than an error.

A `DUMP_PROBABILITY` of 75% means the service randomly drops 75% of
responses, making brute-force or timing attacks unreliable.

Scorebot password: `b1t3m3`

## Key Source Files

| Path | Description |
|------|-------------|
| `src/src/secretd.cc` | Full C++ source (~600 lines) |
| `src/secretd.public` | RSA public certificate |
| `src/secretd.private` | RSA private key |
| `src/scripts/secretd.in` | Service management script |
| `src/scripts/poundsvc` | Pound reverse proxy config |

## Architecture

```
client → (SSL/TLS port 8008) → secretd → BerkeleyDB (/tmp/.secretd.db)
```

The service forks on each connection. `CHECKSUM_KEY` XOR-scrambles stored
values. `DUMP_PROBABILITY` introduces random non-response.

## Environment

```bash
docker build -t ictf0405-secretd .
docker run -p 8008:8008 ictf0405-secretd
```

## Writeup

See [`writeup/`](writeup/).
