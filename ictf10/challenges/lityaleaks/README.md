# iCTF 2010 — LityaLeaks

**Edition:** iCTF 2010 — Hit 'em Where it Hurts  
**Category:** Web  
**Port:** 80 (`/mediawiki/`)  
**Source:** `LocalSettings.php` extracted from VM `dumps/ictf2010.lityaleaks.tar.gz`

## Description

LityaLeaks is a WikiLeaks-inspired document repository running **MediaWiki 1.15.5**
under Apache 2.2 on Ubuntu 10.10. Teams hosted leaked Lityan government documents —
network captures, source code, and classified information.

### Configuration

| Setting | Value |
|---------|-------|
| Wiki name | LityaLeaks |
| DB name | `wikidb` |
| DB user | `wikiuser` |
| DB password | `downwithlitya` |
| Secret key | `b92b6e2a6ff0d7ac58ff1199d3059d8939e84395ed6cd6d2c487e02057ecd24d` |
| Upload types | pcap, java, c, so, pdf, png, jpg |
| Public account creation | **Disabled** |
| Public editing | **Disabled** (requires login) |

### Security Properties

- Anonymous users cannot register or edit — only admins create accounts
- The `$wgSecretKey` is hardcoded in `LocalSettings.php`, enabling session token forgery
- MediaWiki 1.15.5 has multiple known CVEs (SQL injection, CSRF, XSS)
- File upload allows `.c`, `.so`, `.pcap` — non-standard extensions suggest challenge files

### Vulnerability Context

MediaWiki 1.15.5 (November 2010) was known to have vulnerabilities in its
API and file handling. The secret key exposure enables forging `_session` and
`_token` values. The database password is recoverable from the config file.

## Flag Format

`ictf2010{lityaleaks_compromised}`
