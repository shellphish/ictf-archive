# aqs — iCTF 2005 (Association for Quality SPAM)

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, UCSB)
**Category:** pwn / web
**Format:** Attack-defense service

## Overview

A multi-component web service: a C CGI wrapper (`cprog`) that applies a
custom cipher to the query string and execs into a Perl parser (`parser.pl`),
a Python guestbook (`guestbook.py`/`library.py`), and supporting files.

## Architecture

```
http://<host>/~aqs/cgi-bin/cprog?<ciphered_query>     — C CGI wrapper + Perl parser
http://<host>/~aqs/cgi-bin/guestbook.py               — Python guestbook
```

`cprog` applies an inline x86 assembly "speedup" cipher to `QUERY_STRING`,
then calls `execl("./parser.pl", "./parser.pl", ciphered_args, NULL)`.

## Vulnerability

**cprog cipher bypass:** The `speedup()` inline assembly implements a custom
transformation (a variant of a rotating-key additive cipher). An attacker who
reverse-engineers the cipher can craft a query string that, after the cipher
is applied, injects arbitrary arguments into `parser.pl`.

**Guestbook information disclosure:** `guestbook.py` uses `library.py` which
stores private guestbook entries. Looking up a "private" entry by name may
reveal other teams' stored data if entry isolation is insufficient.

## Files

| File | Description |
|------|-------------|
| `src/cprog.c` | C CGI wrapper with x86 cipher, execs parser.pl |
| `src/cprog` | Compiled 32-bit ELF binary |
| `src/guestbook.py` | Python guestbook CGI |
| `src/library.py` | Guestbook storage library |
| `src/parser.pl` | Perl argument parser invoked by cprog |
| `src/aqsScoringScript.py` | Scorebot flag set/get script |

## Notes

- Source extracted from CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The x86 `speedup` function in `cprog.c` adds a rotating value (incremented by 3
  each character, mod 16) to each byte of the input. Reversing this transforms
  the ciphered output back to the original input.
