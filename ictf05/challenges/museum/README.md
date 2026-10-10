# Spam Museum (iCTF 2005)

Part of the **Spam World** theme of iCTF 2005.

## Description

A Perl CGI web service for collecting "spam improvement ideas." Flags are stored
as the `idea` field, retrieved via an admin interface with a hardcoded password.

## Endpoints

```
GET /~museum/cgi-bin/museum_upload.pl?first=X&last=X&dob=&ssn=&mmn=&email=&idea=<FLAG>
GET /~museum/cgi-bin/museum_admin.pl?first=X&last=X&password=unbreakable   → returns flag
```

## Source

See `writeup/MuseumServiceScript.py` for the scorebot checker.
