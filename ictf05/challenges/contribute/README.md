# contribute — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, UCSB)
**Category:** web / SQL injection
**Format:** Attack-defense service

## Overview

A Python CGI that accepts financial contributions (name, amount, address,
credit card number) to the Spam Museum. Data is inserted into a MySQL
`Contributions` database. Flags are stored as contribution records.

## Architecture

```
http://<host>/~contribute/cgi-bin/contribute.py  — POST form (name/contribution/address/cc)
http://<host>/~contribute/cgi-bin/history.py     — view contribution history
```

The MySQL database `Contributions` stores: `id`, `name`, `amount`, `address`, `ccn`.
The flag is stored as the `ccn` (credit card number) field.

## Vulnerability

`contribute.py` builds the INSERT query by direct string formatting with no
escaping or parameterization:
```python
query = "INSERT INTO contributors (id, name, amount, address, ccn) " \
        "VALUES (%s, \"%s\", %s, \"%s\", \"%s\" ) ;" % (
            id, form.getvalue("name"), form.getvalue("contribution"),
            form.getvalue("address"), form.getvalue("cc") )
cursor.execute(query)
```
Any of the string fields (`name`, `address`, `cc`) allows SQL injection.
An attacker can inject `"), (999, "x", 0, "x", "STOLEN_FLAG` to insert
arbitrary records, or use `UNION SELECT` in a query context.

The development password `ctftest` is hardcoded in the source.

## Files

| File | Description |
|------|-------------|
| `src/contribute.py` | Contribution submission CGI (SQL injection) |
| `src/history.py` | Contribution history CGI |
| `src/test.py` | Test/diagnostic CGI |
| `src/db-restore.sh` | Database restore script |
| `src/db-restore.sql` | Database schema |
| `src/contributeScoringScript.py` | Scorebot flag set/get script |

## Notes

- Source extracted from CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The hardcoded DB password `ctftest` in the source suggests the production password
  was different; the actual deployed password is not in the recovered source.
