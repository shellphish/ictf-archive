# query — iCTF 2003

**Competition:** iCTF 2003 "Windows Goes Open-Source" (November 2003, Shellphish)
**Category:** web
**Format:** Attack-defense service

## Overview

A Perl CGI telephone directory search service backed by PostgreSQL. The flag was
stored as the employee ID of a "Bill Gates" record and retrievable by querying
the directory for his entry.

## Architecture

```
http://<host>/cgi-bin/query_extension.pl?cboname=Gates   — directory search
http://<host>/cgi-bin/change.pl?login=admin&password=<pw>&last=Gates&first=Bill&id=<flag>
```

The service connects to PostgreSQL database `querydb` as `queryuser`. The `id` field
of the "Bill Gates" row is the flag.

## Vulnerability

`query_extension.pl` sanitizes `cboname` with `s/[^a-zA-Z]//g` (strips non-alpha),
then interpolates it into SQL:
```perl
$sth = $dbh->prepare("SELECT * FROM employees WHERE last = '$cboname' ORDER BY last;");
```

The sanitization prevents direct SQL injection. However, `change.pl` (admin update
endpoint) accepts the admin password and new `id` value as GET parameters with no
visible sanitization — if the admin password can be obtained from the CGI source
(it's `##QUERY_DB_PASS##` at deployment, stored in plaintext in the script), an
attacker can update any employee's flag freely.

## Files

| File | Description |
|------|-------------|
| `src/query_extension.pl` | Employee directory search CGI |
| `src/change.pl` | Admin employee record update CGI |
| `src/get_query` | Scorebot flag retrieval script |
| `src/set_query` | Scorebot flag update script |
| `src/setup.sh` | VM deployment script |
| `src/init_query`, `src/init.sh` | Service init scripts |

## Notes

- Source extracted from the CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The front-end static HTML was served from `/var/www/html/assistance/` on the VM.
