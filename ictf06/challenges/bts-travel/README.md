# bts-travel — iCTF 2006

**Competition:** iCTF 2006 "The Hillbilly Bank" (December 8, 2006, UCSB Frank Hall)
**Category:** web / python
**Format:** Attack-defense service
**Protocol:** HTTP (Python 2)

## Overview

The Bank Travel Service (`banktravel`) is a Python 2 HTTP web application for
managing bank travel accounts. Users subscribe with an RSA-signed check, log in,
and transfer funds to an IBAN address.

## Architecture

From the scoring script (`../hillbilly-bank/src/btsScoringScript.py`), the HTTP
endpoints are:

| URL | Description |
|-----|-------------|
| `/subscribe` | POST: salutation, firstname, lastname, email, echeck (RSA check), username, password, question, answer |
| `/login` | Login page |
| `/authenticate?username=&password=` | Authenticate |
| `/transfer?amount=&iban=` | Transfer funds to IBAN |

The service is implemented in `banktravel.pyc` (compiled Python) invoked via `runme.py`.

## Files

| File | Description |
|------|-------------|
| `src/runme.py` | Entry point — imports banktravel, calls `banktravel.main()` |
| `src/init_bts` | `/etc/init.d/bts` service init script |

## Notes

- Source extracted from the CTF VM (Ubuntu Dapper, VMware VMDK) via `qemu-img` + `debugfs`.
- The `banktravel.py` source was not present in the VM — only `banktravel.pyc` (364 KB,
  compiled Python 2) is available. The service port is compiled into `banktravel.pyc`.
- The scoring script placeholder shows port 481516 (impossible), suggesting the actual
  port was not finalized before competition (likely 8080 or similar).
