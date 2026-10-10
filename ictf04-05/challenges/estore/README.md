# iCTF 2005 — E-Store

**Edition:** iCTF 2005 — The Bass Tard Corporation  
**Category:** Web  
**Service URL:** `http://<team-ip>/~estore/`

## Description

The Bass Tard Corporation's online store. The service supports user registration,
authentication, product browsing, profile updates, and logout.

The scorebot stored the current flag in a newly registered user's **email field**:
- `POST /~estore/cgi-bin/createuser.php` — register (username, password, email=flag)
- `POST /~estore/cgi-bin/login.php` — authenticate
- `POST /~estore/cgi-bin/update.php` — update profile (old email revealed in response)
- `POST /~estore/cgi-bin/logout.php` — log out

Flag retrieval involved authenticating as the previously registered user and calling
`update.php`, which echoed the old email address ("address was: ...") in the response.

## Source

No source code recovered — service ran inside competition VMs (Fedora Core 4).
The `writeup/EstoreServiceScript.py` is the original scorebot checker documenting
the service API.

## Flag Format

`ictf2005{estore_compromised}`
