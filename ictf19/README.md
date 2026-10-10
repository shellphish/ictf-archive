# iCTF 2019 — The Grey Hat Nation

**Date:** December 2019 (exact date not documented)
**Format:** Attack-Defense (ZDI exploit submission + attack detection)

---

## The Story

> *You have been recruited to protect your nation's most critical systems.
> But in the world of grey-hat operations, protecting and exploiting are
> two sides of the same coin. The Zebra Dwarf Institution is watching —
> and they pay well for working exploits.*

The 2019 iCTF continued the **Zebra Dwarf Institution (ZDI)** narrative
that began with ictf12. Teams were tasked with defending critical
infrastructure services belonging to their nation while covertly submitting
exploits to the ZDI — a shadowy underground vulnerability broker. The ZDI
would then run those exploits against rival teams, creating a grey market
for zero-day vulnerabilities.

The scoring model rewarded:
- **Attack detection** — correctly identifying malicious traffic in network
  flow data provided by the organizers
- **Service availability** — a multiplier applied to detection scores
- **Exploit submission** — residual points each time an exploit successfully
  captures a flag from a rival team

## Infrastructure

Each team operated a server running a set of "critical infrastructure"
services specified in the CTF Service Specification document. There was no
direct team-to-team exploitation; instead teams submitted exploits to the
organizers who ran them centrally.

## Data

| Path | Contents |
|------|----------|
| `CTF Service Specification.docx` | Requirements document for service authors |

Note: ~12 KB total. No traffic dumps, VM images, or service source code
preserved locally.

## References

- [iCTF website](https://ictf.cs.ucsb.edu)
- Related editions: [ictf12](../ictf12/), [ictf13](../ictf13/), [ictf14](../ictf14/), [ictf17](../ictf17/)
