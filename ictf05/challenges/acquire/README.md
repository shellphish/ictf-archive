# acquire — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, UCSB)
**Category:** web
**Format:** Attack-defense service

## Overview

A PHP web service for acquiring spam samples. Users register, search the
spam database, and submit spam leads. The service has an admin panel in
`secured/delete.php`. Flags are stored in the service database and
retrieved by registered users.

## Architecture

```
http://<host>/~acquire/cgi-bin/index.php        — landing page
http://<host>/~acquire/cgi-bin/register.php     — user registration (45KB)
http://<host>/~acquire/cgi-bin/search.php       — spam search (45KB)
http://<host>/~acquire/cgi-bin/contact.php      — contact form
http://<host>/~acquire/cgi-bin/paid_service.php — premium service
http://<host>/~acquire/cgi-bin/secured/delete.php — admin delete (19KB)
```

## Vulnerability

The large PHP files (`register.php` and `search.php`, ~45KB each) suggest
complex database interactions. Common PHP vulnerabilities of the 2005 era:
- SQL injection via unsanitized form inputs
- Path traversal in file operations
- Authentication bypass in the admin `delete.php`

The `secured/` directory requires authentication; if that authentication
is bypassable, `delete.php` provides admin-level access.

## Files

| File | Description |
|------|-------------|
| `src/index.php` | Landing page |
| `src/register.php` | User registration (45KB) |
| `src/search.php` | Spam database search (45KB) |
| `src/contact.php` | Contact form |
| `src/get.php` | Flag retrieval script |
| `src/set.php` | Flag update script |
| `src/paid_service.php` | Premium service page |
| `src/links.php` | Links page |
| `src/howto.php` | Help page |
| `src/secured/delete.php` | Admin deletion (19KB, requires auth) |
| `src/acquireScoringScript.py` | Scorebot flag set/get script |

## Notes

- Source extracted from CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- `get.php` and `set.php` are likely the direct flag interface used by the scorebot;
  reading them reveals the exact flag storage mechanism.
