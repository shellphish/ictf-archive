# iCTF 2010 — I Dream of Jeannie (S6)

**Category:** Binary
**Port:** 2009
**Language:** Java (compiled class only)
**Tags:** binary, java, reverse-engineering

## Description

IDreamOfJeannie (named after the 1960s TV series) was a Java network service
on port 2009. The JVM crashed repeatedly during the competition (many
`hs_err_pid*.log` files in the live VM), suggesting a stability issue that
may itself be exploitable.

A custom shared library `libc-lamp.so` (7 KB) is loaded by the service —
likely providing the flag storage or crypto primitive.

## Source

Extracted from `vms/ictf2010.services.tar.gz` → `idreamofjeannie/iCTF2010_Service_Base.vmdk`

| File | Description |
|------|-------------|
| `IDreamOfJeannie.class` | Compiled Java bytecode (3.1 KB, decompilable) |
| `libc-lamp.so` | Native shared library (7.3 KB, 32-bit ELF) |
| `secret.txt` | Flag file |

## Analysis

Decompile `IDreamOfJeannie.class` with `javap -c` or a Java decompiler.
Reverse `libc-lamp.so` to understand how the native library interacts with
the Java service. The JVM crash logs (`hs_err_pid`) may indicate a JNI
memory safety bug.
