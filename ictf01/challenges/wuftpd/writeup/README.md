# wu-ftpd — Writeup

## Background

wu-ftpd 2.6.0(1) (the Washington University FTP daemon, default in RedHat 6.x/7.x)
passes the FTP `PASS` command argument directly to `syslog()` as a format string.
Because anonymous FTP is enabled, an unauthenticated attacker can reach the
vulnerable code path immediately after connecting.

CVE: CAN-2000-0374 / CERT Advisory CA-2000-13.

## Vulnerable Code Path

```c
/* wu-ftpd reply.c */
syslog(LOG_INFO, pass);    // PASS argument used as format string
```

A crafted password with `%n` directives overwrites arbitrary memory.

## Exploitation

The provided `wuftpd-god.c` is the "god-" exploit from EFNet IRC, modified to fix
the return address for RedHat 6.2 machines:

```bash
gcc wuftpd-god.c -o wuftpd-god
./wuftpd-god -s0 -t <host>
```

The exploit connects as anonymous FTP, sends the format string in the `PASS` field,
then spawns a shell. Press `^\` to enter the shell after the payload fires.

## Historical Context

During the iCTF 2001 Red Team/Blue Team exercise, Andrew "Mutz" Darren used this
exploit against blue team machines, as documented in the red team report
(`Report_RED_exploit/`). The `auto.pl` script in the archive automated the attack
by parsing Nessus output to identify vulnerable FTP servers and launching this exploit.

## Flag

`FLAG_ICTF2001{wuftpd_format_string_anonymous_ftp_rce}`
