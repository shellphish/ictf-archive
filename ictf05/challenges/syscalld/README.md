# Syscall Daemon (iCTF 2005)

Part of the **Spam World** theme of iCTF 2005.

## Description

A TCP service on port 31337 with a custom binary protocol. The banner contains a
version string like `v1.2.3` where the patch number is the XOR seed. All protocol
instructions are XOR'd with this seed byte.

The flag is stored in memory in little-endian 32-bit word order; the service
exposes it as a hex memory dump.

## Protocol

Connect on port 31337. Parse the version string for the seed. Send XOR'd
instructions to read/write flag memory.

## Source

See `writeup/SyscalldServiceScript.py` for the scorebot checker with full
`extractSeed`, `extractFlag`, and `randomize` helper functions.
