# iCTF 2008 — The Bomb (bombsite)

**Edition:** iCTF 2008
**Category:** binary
**Role:** Final target in the Softerror.com attack chain
**Language:** C++ / NASM (x86 32-bit)

## Description

The final host in the Softerror.com network. A nuclear bomb timer is running
on this machine, controlled by a custom C++ binary (`monitor`) that loads and
executes a 32-bit x86 ELF shared library (`firmware.img`). Teams must
compromise this host (only reachable after pivoting through mainwebsite,
develsite, and financialsite) and find a way to stop the bomb.

The `monitor` binary loops, loading and executing the firmware. The solution
requires understanding or patching the firmware execution to neutralize the
timer.

## Environment

```bash
docker build -t ictf08-bombsite .
docker run --rm ictf08-bombsite
```

> Note: The firmware is 32-bit x86. The container enables multilib support.

## Files

| Path | Description |
|------|-------------|
| `src/` | C++ source (`monitor.cc`), NASM firmware (`firmware.asm`, `solution.asm`), Makefile |
| `Dockerfile` | Container with build toolchain (nasm, g++ multilib) |
| `solution/` | Official `b200_walkthrough.txt` and solution image |
| `attachments/` | Files distributed to participants (compiled binaries) |

## Solution

See [`solution/b200_walkthrough.txt`](solution/b200_walkthrough.txt)
and the official solution image `solution.img`.
