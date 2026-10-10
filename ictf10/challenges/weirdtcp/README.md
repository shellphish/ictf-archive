# iCTF 2010 — WeirdTCP (S7)

**Category:** Network
**Port:** 3333
**Language:** C
**Tags:** network, protocol, c

## Description

WeirdTCP was a service implementing a custom "Litya Internet Protocol (LIP)"
on TCP port 3333. The organizers hinted: *"weirdtcp's important information
is in the Litya Internet Protocol RFC"* — suggesting a protocol spec was
published alongside the competition. Teams had to reverse-engineer or read
the RFC to understand the protocol, then exploit an implementation vulnerability.

An `attack.c` / `attack` binary is included, suggesting the service authors
also provided a reference exploit tool.

## Source

Full C source extracted from `vms/ictf2010.services.tar.gz` →
`weirdtcp/iCTF2010_Service_Base.vmdk`

| File | Description |
|------|-------------|
| `weirdtcp.c` | Main service implementation (~33 KB) |
| `attack.c` | Reference exploit/attack client |
| `mydiag.c` / `mydiag.h` | Diagnostic utilities |
| `netheaders.h` | Custom LIP protocol headers |
| `weirdtcp.bin` | Compiled 32-bit ELF (debug symbols intact) |
| `attack.bin` | Compiled 32-bit ELF attack tool |

## Vulnerability

With full source and debug-symbol binary, this is straightforward to analyze
statically. Look for buffer overflows or protocol state machine bugs in the
LIP implementation.
