# spamgen — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, UCSB)
**Category:** web / information disclosure
**Format:** Attack-defense service

## Overview

A Python CGI spam generator. Users can upload junk email samples
(stored in `user_db/<hash(username+password)>`) and later retrieve them.
The service also generates new random spam using a 2nd-order Markov model
trained on ALL uploaded samples — including flag entries.

## Architecture

```
http://<host>/~spamgen/cgi-bin/spamgen.py?action=generate  — generate spam (leaks flags)
http://<host>/~spamgen/cgi-bin/spamgen.py?action=upload    — upload text (stores flag)
http://<host>/~spamgen/cgi-bin/spamgen.py?action=read      — read own uploads
```

The scorebot uploads the flag with a random username and fixed password
`"miconsenta"`, then retrieves it by reading with the same credentials.

## Vulnerability

The `generate` action calls `mtext()` which reads **all** files in `user_db/`:
```python
for l in listdir('user_db'):
    f = open('user_db/'+l)
    for line in f.readlines(): ...
```
Every flag stored by every team's scorebot leaks into the generated spam text.
An attacker simply requests `?action=generate` repeatedly to harvest flags.

Additionally, the custom `hash()` function in `myhash.py` is deterministic and
invertible — knowing the username and password directly computes the filename,
allowing targeted reads of any team's entries.

## Files

| File | Description |
|------|-------------|
| `src/spamgen.py` | Main CGI: upload/generate/read actions |
| `src/markov.py` | 2nd-order Markov text generation (reads all user_db/) |
| `src/myhash.py` | Custom hash function mapping username+password → filename |
| `src/spamgenScoringScript.py` | Scorebot flag set/get script |

## Notes

- Source extracted from CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The flag leaks immediately because `mtext()` reads all `user_db/` entries
  without filtering by owner. This is a design flaw, not a misconfiguration.
