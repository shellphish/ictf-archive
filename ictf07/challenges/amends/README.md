# iCTF 2007 — Copyright Mafia: Make Amends

**Edition:** iCTF 2007 | **Category:** web | **Language:** PHP

## Description

The Mafia's settlement payment service. Wrongdoers pay cash settlements
to copyright holders. The service processes payment agreements and generates
legal letters in both PDF and plain-text formats.

## Architecture

| Component | Detail |
|-----------|--------|
| Language | PHP (CGI via Apache UserDir) |
| Port | 80 (`/~amends/cgi-bin/`) |
| Database | MySQL |
| Letter templates | `ltrpdf.inc` (PDF), `ltrtxt.inc` (plain text) |

### File Layout

```
src/
├── index.html               Static front page
├── ltrpdf.inc               PDF letter template
├── ltrtxt.inc               Plain-text letter template
├── cgi-bin/
│   ├── amends.php           Main amends form handler (entrypoint)
│   ├── chaching.php         Payment/cha-ching processing
│   ├── ltr.php              Letter generation dispatcher
│   ├── payoff.php           Payoff amount calculation
│   └── settlement.php       Settlement workflow
└── php-include/
    ├── cookie.php           Session/cookie helpers
    ├── dbconfig.php         Database configuration
    ├── dblogin.php          Database login
    ├── filter.php           Input sanitization (may be incomplete)
    ├── id.php               ID generation
    └── pagegen.php          Page layout generation
```

## Vulnerability Hints

- `filter.php` handles input sanitization — look for bypass paths that
  reach SQL queries in `dblogin.php` or `amends.php` unsanitized
- The settlement and payoff flows take user-supplied amounts and IDs
  that may be vulnerable to integer overflow or SQL injection
- The PDF generation path (`ltr.php` + `ltrpdf.inc`) could be
  susceptible to command injection or path traversal if external
  binaries are invoked with user-controlled arguments

## Run

```bash
docker build -t ictf07-amends . && docker run -p 8080:80 ictf07-amends
```

## Files

| File | Description |
|------|-------------|
| `src/cgi-bin/amends.php` | Main amends form handler |
| `src/cgi-bin/chaching.php` | Payment processing |
| `src/cgi-bin/ltr.php` | Letter generation |
| `src/cgi-bin/payoff.php` | Payoff calculation |
| `src/cgi-bin/settlement.php` | Settlement workflow |
| `src/php-include/` | Shared helpers (DB, cookies, filters, IDs) |
| `src/ltrpdf.inc` | PDF letter template |
| `src/ltrtxt.inc` | Plain-text letter template |
