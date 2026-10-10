# iCTF 2005 — Guestbook

**Edition:** iCTF 2005 — The Bass Tard Corporation  
**Category:** Web  
**Service URL:** `http://<team-ip>/`

## Description

The Bass Tard Corporation's public guestbook. Visitors can post comments with a
first name, last name, optional privacy flag, and free-form text.

The scorebot stored the flag as the comment text of a private entry, identified
by the poster's first/last name. It retrieved flags at:

```
GET /~guestbook/cgi-bin/guestbook.pl?user=<first>
```

and posted new entries via an HTML form on `feedback.html` (POST to
`/~guestbook/cgi-bin/...`).

## Source

No source code recovered — service ran inside competition VMs (Fedora Core 4).
The `writeup/GuestbookServiceScript.py` is the original scorebot checker script
documenting the service API.

## Flag Format

`ictf2005{guestbook_compromised}`
