# LPRng — Writeup

## Background

LPRng 3.6.24-1 (the default print spooler in RedHat 7.0) passes job metadata
supplied by the client directly to `syslog()` without sanitizing format specifiers.
An unauthenticated attacker connecting to port 515/tcp can send a crafted print job
whose metadata string overwrites an arbitrary memory location — typically the saved
return address of a stack frame — with a shellcode pointer.

CVE: CAN-2000-0917 / CERT Advisory CA-2000-22.

## Vulnerable Code Path

The print job "from" field and queue name are passed to `syslog()` like:

```c
syslog(LOG_ERR, user_supplied_string);   // no %s wrapper
```

This allows `%n` writes and `%x` leaks to map and overwrite the GOT or stack.

## Exploitation

The provided `LPRng-3.6.24-1.c` is a working exploit by "venomous" of rdC:

```bash
gcc LPRng-3.6.24-1.c -o lprng-exploit
./lprng-exploit <host>
```

The exploit contains OS offset tables for RedHat 7.0 and Slackware 7.0.
It opens a bind shell, typically on port 3049.

## Historical Context

During the iCTF 2001 Red Team/Blue Team exercise, Andrew "Mutz" Darren used this
exploit against blue team machines. The writeup and Snort rules (`lprng.rules`) for
detecting the attack are included in `src/`.

## Flag

`FLAG_ICTF2001{lprng_format_string_rh70_remote_root}`
