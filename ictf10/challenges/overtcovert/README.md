# iCTF 2010 — OvertCovert (S9)

**Category:** Misc / Steganography
**Port:** 1969
**Tags:** steganography, covert-channel, binary

## Description

OvertCovert was a service that hid information in overt network communications
using a covert channel. Port 1969 (a nod to the year of Woodstock/Apollo 11).
Started with a secret flag as argument: `overtcovert -s ciaomamma`.

During the competition organizers released the source code publicly to
encourage teams to work on it. The `data/` directory contained many `item-*`
files (likely per-team covert messages/flags). The `decrypt` tool provides
the client-side decryption.

## Source

Binary extracted from `vms/ictf2010.services.tar.gz` → `overtcovert/iCTF2010_Service_Base.vmdk`

| File | Description |
|------|-------------|
| `overtcovert.bin` | Service binary (32-bit ELF, debug symbols) |
| `decrypt.bin` | Decryption/client tool (32-bit ELF) |

## Analysis

Reverse both binaries with debug symbols. The covert channel likely embeds
data in timing, packet sizes, or field values. The `decrypt` tool shows the
expected output format.
