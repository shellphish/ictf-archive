# iCTF 2006 — The Hillbilly Bank

**Date:** December 2006
**Format:** Attack-Defense
**Teams:** 25 (USA, Europe, Australia)

---

## The Story

The 2006 iCTF's theme was the **Hillbilly Bank** — a rich-yet-uneducated
financial institution. Teams competed in an attack-defense format defending
and attacking the bank's online services.

The Hillbilly Bank's charm lay in its combination of wealth and technical
naivety: its systems were valuable targets but poorly secured, reflecting
common real-world patterns where financial institutions build complex systems
without security-first thinking.

## Services

| Name | Category | Language | Source | Description |
|------|----------|----------|--------|-------------|
| [`hillbilly-bank`](challenges/hillbilly-bank/) | crypto | Python | ✓ | RSA check signing (central + branch bank) |
| [`mom-bank`](challenges/mom-bank/) | web | PHP | ✓ | Member portal (lighttpd, port 1336) |
| [`ipa-interbank`](challenges/ipa-interbank/) | web | Ruby on Rails | ✓ | Currency exchange (mongrel, port 3000) |
| [`ins-insurance`](challenges/ins-insurance/) | web | PHP | ✓ | Insurance purchase and claims |
| [`atm`](challenges/atm/) | binary | Python | ✓ | ATM network service (account/balance) |
| [`bts-travel`](challenges/bts-travel/) | binary | Python | ✓ | Travel booking service |
| [`etj-transactions`](challenges/etj-transactions/) | binary | Python | ✓ | Transaction service |
| [`bpt-proto`](challenges/bpt-proto/) | binary | C | binary only | Bank protocol daemon |
| [`sts-stock`](challenges/sts-stock/) | binary | C++ | ✓ | Stock market service |

Source code extracted from CTF VM (`bank2006.tar.gz`) via `qemu-img` + `debugfs`.
VM image: `vms/bank2006.tar.gz`

## Data

| Path | Contents | Size |
|------|----------|------|
| `site/` | Original competition website | — |
| `vms/bank2006.tar.gz` | VM image for the bank service | ~2.2 GB total |
| `pictures/` | Event photographs | — |
| `SecurityWireCTF.pdf` | SecurityWire article about the competition | — |

## References

- [Original website](https://ictf.cs.ucsb.edu/archive/2006/site)
- [VMs](https://ictf.cs.ucsb.edu/archive/2006/vms)
- [Pictures](https://ictf.cs.ucsb.edu/archive/2006/pictures)
