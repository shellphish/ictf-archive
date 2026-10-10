# iCTF 2007 — Copyright Mafia: Make Amends

**Edition:** iCTF 2007 | **Category:** web | **Language:** PHP

## Description
The Mafia's settlement payment service. PHP web app with MySQL backend.
Processes amends, generates legal letters (ltr.php), handles settlements.

## Run
```bash
docker build -t ictf07-amends . && docker run -p 8080:80 ictf07-amends
```

## Files
| File | Description |
|------|-------------|
| `src/cgi-bin/amends.php` | Main amends form handler |
| `src/cgi-bin/settlement.php` | Settlement processing |
| `src/cgi-bin/payoff.php` | Payment handling |
| `src/php-include/` | Shared functions, DB config, auth |

## Writeup
See [`writeup/`](writeup/).
