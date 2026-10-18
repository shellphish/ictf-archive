# guestbook — iCTF 2003

**Competition:** iCTF 2003 "Windows Goes Open-Source" (November 2003, Shellphish)
**Category:** web
**Format:** Attack-defense service

## Overview

A Perl CGI guestbook service running under Apache on RedHat 9. Flags were
stored as guestbook entries attributed to "Bill Gates" and retrievable through
the admin interface.

## Architecture

```
http://<host>/cgi-bin/guestbook.pl              — public guestbook view
http://<host>/cgi-bin/guestbook_admin.pl        — admin login (POST login/password)
http://<host>/cgi-bin/save_messages_admin.pl    — save edited guestbook (POST)
```

The flag is stored in `guestbook.txt` as:
```
<b>Bill Gates</b> (FLAGVALUE) wrote:
```

The admin interface authenticates via `MD5(password) == ##GUESTBOOK_ADMIN_PASS##`.
Once authenticated, `guestbook_admin.pl` renders the full `guestbook.txt` content
in a `<textarea>`, and `save_messages_admin.pl` replaces the file with the edited content.

## Vulnerability

The admin password hash (`##GUESTBOOK_ADMIN_PASS##` placeholder) is embedded in
`guestbook_admin.pl`. If an attacker can read the CGI source or brute-force the MD5,
they gain admin access and can read/write the flag directly.

The public `guestbook.pl` renders raw HTML from `guestbook.txt` without escaping —
stored XSS is also possible if an attacker writes to the guestbook.

## Files

| File | Description |
|------|-------------|
| `src/guestbook_admin.pl` | Admin login and flag display CGI |
| `src/save_messages_admin.pl` | Admin save/update CGI |
| `src/guestbook.pl` | Public guestbook display CGI |
| `src/save_message.pl` | Public post-new-message CGI |
| `src/guestbook.txt` | Guestbook data file (flag stored here) |
| `src/get_guestbook` | Scorebot flag retrieval script |
| `src/set_guestbook` | Scorebot flag update script |
| `src/setup.sh` | VM deployment script |
| `src/init_guestbook` | Service init script |

## Notes

- Source extracted from the CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The templates directory (`templates/`) with `header.html` and `footer.html` was
  served via `system("cat ./templates/header.html")` calls — a CGI antipattern
  common in early-2000s Perl web development.
