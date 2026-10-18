# museum — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, Shellphish)
**Category:** web / command injection
**Format:** Attack-defense service

## Overview

A Perl CGI "Spam Museum" web service. Users submit spam improvement ideas via
`museum_upload.pl`; staff searches the collection via `museum_search.pl`; the
admin manages entries via `museum_admin.pl`. Flags are stored as idea entries
attributed to the scorebot's random user name.

## Architecture

```
http://<host>/~museum/museum_upload.pl?first=X&last=Y&idea=<flag>
http://<host>/~museum/cgi-bin/museum_search.pl?keyword=<term>
http://<host>/~museum/cgi-bin/museum_admin.pl?first=X&last=Y&password=<pw>
```

Files are stored in `./museum_ideas/${first}.${last}` relative to the CGI directory.

## Vulnerabilities

**1. Command injection in museum_search.pl**

The search script filters only semicolons from `$keyword`:
```perl
if (($keyword eq "") || ($keyword =~ /.*[;].*/)) { ... }
else {
  while (<./museum_spam/*>) {
    system "grep -i $keyword $_ > /dev/null";
  }
}
```
Shell metacharacters `|`, `$(...)`, backticks, and `&` are NOT filtered. An
attacker can inject: `keyword=x||cat%20./museum_ideas/*`.

**2. Path traversal in museum_upload.pl**

The upload script writes to `./museum_ideas/${first}.${last}` with no sanitization:
```perl
open(FILE, "> ./museum_ideas/${first}.${last}") or $failed = 1;
print(FILE "$idea");
```
An attacker can overwrite arbitrary files relative to the CGI dir using
`first=..&last=../../etc/cron.d/evil`.

**3. Hardcoded password in museum_admin.pl**

The admin interface uses the hardcoded password `unbreakable`:
```perl
if (... (! $password eq "unbreakable")) { ... }
else { system "cat ./museum_ideas/${first}.${last}"; }
```
Combined with path traversal: `?first=..&last=../../etc/passwd&password=unbreakable`.

## Files

| File | Description |
|------|-------------|
| `src/museum_search.pl` | Keyword search CGI (command injection) |
| `src/museum_upload.pl` | Idea submission CGI (path traversal write) |
| `src/museum_admin.pl` | Admin review CGI (hardcoded password + path traversal read) |
| `src/museumScoringScript.py` | Scorebot flag set/get script |

## Notes

- Source extracted from CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The scoring script stores the flag as an "idea" attributed to a random first/last name,
  then retrieves it via the admin interface.
