# iCTF 2005 — Contact Directory

**Edition:** iCTF 2005 — The Bass Tard Corporation  
**Category:** Web  
**Service URL:** `http://<team-ip>/~contact/`

## Description

The Bass Tard Corporation's internal contact/phone directory, implemented as a
Perl CGI application. Each contact record stores a first name, last name, and
phone extension.

The admin update endpoint uses **hardcoded credentials** (`admin:retard`):

```
GET /~contact/cgi-bin/contact_change.pl?login=admin&password=retard&first=<F>&last=<L>&ext=<FLAG>
```

Flags were retrieved by submitting the lookup form on `contact.html` with the
contact's last name, which returned the matching extension.

## Vulnerability Hint

The admin credentials are embedded in the scorebot script verbatim. A team that
reads traffic or finds the CGI source can trivially write their own flag.

## Source

No source code recovered — service ran inside competition VMs (Fedora Core 4).
The `writeup/ContactServiceScript.py` is the original scorebot checker.

## Flag Format

`ictf2005{contact_compromised}`
