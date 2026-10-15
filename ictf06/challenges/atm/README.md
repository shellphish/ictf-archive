# atm — iCTF 2006

**Competition:** iCTF 2006 "The Hillbilly Bank" (December 8, 2006, UCSB Frank Hall)
**Category:** binary / python
**Format:** Attack-defense service
**Protocol:** XML-RPC (Python `SimpleXMLRPCServer`)

## Overview

The Hillbilly Bank ATM service manages credit and debit cards backed by a SQLite
database (`atmdb`). Users can open accounts, deposit checks (RSA-signed, 172 chars),
withdraw cash, and check account movements.

## Architecture

The service exposes an XML-RPC interface via `SimpleXMLRPCServer`. Two card types:

- **CreditCard**: tracks `current_credit` up to `sec_deposit` (security deposit of 1000).
  Methods: `movements()`, `withdrawal(amount)`, `pay(amount)`, `close()`.
- **DebitCard**: accepts RSA-signed checks via `deposit_check(check)`.

Database tables (SQLite, `/home/atm/atmdb`):
- `CARDS` — card number, card type, owner info, IBAN
- `CREDIT` — card number, expiration timestamp, sec_deposit, current credit
- `MOVS` — movement log (timestamp, card number, amount)

Withdrawals write a transaction record to `/var/spool/transactions/atm/<random>`.

## Vulnerability

The `CreditCard.pay()` method deducts from current credit but does not prevent
an attacker from calling `R_submit()` (the internal "restricted" withdrawal method)
directly via XML-RPC if the server does not properly restrict method exposure.
The `atm_server.pyc` controls which methods are registered — if `R_submit` is
inadvertently exposed, arbitrary payout is possible.

Also: the ATM's `atmdb` SQLite file is in `/home/atm/` — a file-read vulnerability
on the service grants access to all account IBANs and balances.

## Files

| File | Description |
|------|-------------|
| `src/atm.py` | Entry point — imports `atm_server` and calls `atm_server.run()` |
| `src/atm_classes.py` | CreditCard and DebitCard class implementations |
| `src/atm_server.pyc` | Compiled server module (SimpleXMLRPCServer, port unknown) |
| `src/init_atm` | `/etc/init.d/atm` service init script |

## Notes

- Source extracted from the CTF VM (Ubuntu Dapper, VMware VMDK) via `qemu-img` + `debugfs`.
- The `atm_server.py` source was not present in the VM — only the `.pyc` is available.
- The port number is compiled into `atm_server.pyc`.
- A live `atmdb` SQLite database file was present at runtime (removed from archive
  as it contained team data).
