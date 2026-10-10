# iCTF 2006 — Hillbilly Bank: Web Portal (mom)

**Edition:** iCTF 2006
**Category:** web
**Language:** PHP / lighttpd

## Description

The main web portal of the Hillbilly Bank. Features account creation, login,
member management, transactions, stock info, and various services — all
implemented in PHP with a MySQL backend.

## Environment

```bash
docker build -t ictf06-mom-bank .
docker run -p 8080:80 ictf06-mom-bank
```

## Files

| File | Description |
|------|-------------|
| `src/index.php` | Home page |
| `src/login.php` | Login form |
| `src/member.php` | Member dashboard |
| `src/account.php` | Account management |
| `src/transact.php` | Money transfer |
| `src/newaccount.php` | Account registration |
| `src/myfuncs.php` | Shared functions |
| `src/lighttpd.conf` | Original web server config |

## Writeup

See [`writeup/`](writeup/).
