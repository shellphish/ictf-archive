# ins-insurance — iCTF 2006

**Competition:** iCTF 2006 "The Hillbilly Bank" (December 8, 2006, UCSB Frank Hall)
**Category:** web / php
**Format:** Attack-defense service
**Port:** 1335 (HTTP, lighttpd)

## Overview

The Hillbilly Insurance service offers car insurance to Hillbilly Bank customers.
Customers purchase insurance by submitting personal details and an RSA-signed check
from the central bank (`/usr/bin/ccheck`). After purchase they receive a policy number
and can log in to file damage claims.

## Architecture

```
http://<host>:1335/             — home page
http://<host>:1335/buy.php      — purchase insurance (POST personal data + check)
http://<host>:1335/login.php    — log in (policy number + password)
http://<host>:1335/claim.php    — file damage claim (authenticated)
http://<host>:1335/extend.php   — extend policy
```

Backend: MySQL database `insurance`, user `ins`, password `abracadabra`.
Tables: `policies` (id, first, last, address, id_field, plate, car_model, password, iban, value, created)
and `claims` (policy, description, amount).

Runs as user `ins` via lighttpd with PHP5 CGI (`/usr/bin/php5-cgi`).

## Vulnerability

### SQL Injection in `claim.php`

The claim description is interpolated into SQL without sanitization:

```php
$sql = "INSERT INTO claims (policy, description, amount) VALUES ( "
       .$_SESSION["id"].", '".$_POST["desc"]."' , ".$damage."  );";
```

An authenticated attacker can inject SQL to read all policies (flags) from the database.

### Check Verification Flow

`buy.php` calls `/usr/bin/ccheck` (the shared central bank check verifier) to
validate RSA checks before creating a policy. The check must be exactly 172 characters.

### Logic Flaw in `claim.php`

The variable `$value` (the policy's total insured value) is read from the `policies`
table only on the purchase path — in `claim.php` it may not be defined, allowing
bypass of the claim-amount cap.

## Files

| File | Description |
|------|-------------|
| `src/buy.php` | Insurance purchase: validates check, creates policy |
| `src/claim.php` | File damage claim (**SQL injection**) |
| `src/login.php` | Login (policy number + password) |
| `src/db.php` | MySQL connection (credentials) |
| `src/vars.php` | Session setup |
| `src/nav.php` | Navigation bar |
| `src/index.php` | Home page |
| `src/extend.php` | Policy extension |
| `src/install.mysql` | MySQL schema creation script |
| `src/lighttpd.conf` | lighttpd config (port 1335, document root) |

## Notes

- Source extracted from the CTF VM (Ubuntu Dapper, VMware VMDK) via `qemu-img` + `debugfs`.
- The `ccheck` binary is also used by `ipa` (port 3000) and `mom` (port 1336).
- Claims write a transaction file to `/var/spool/transactions/ins/` for external processing.
