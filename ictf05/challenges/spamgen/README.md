# Spamgen (iCTF 2005)

Part of the **Spam World** theme of iCTF 2005.

## Description

A multi-protocol spam generation platform. The flag is uploaded as text content
via an authenticated web form and can be retrieved via UDP query.

## Interfaces

- `GET /~spamgen/cgi-bin/spamgen.py?action=upload` — upload form (fields: uname, pwd, thetext=FLAG)
- `GET /~spamgen/cgi-bin/spamgen.py?action=read` — read form (uname, pwd)
- UDP port 2345: send filename, receive HTTPS URL
- HTTPS port 4443: `/store?filename=X&content=FLAG&user=X` and `/login?user=X&password=X&operation=OP-store`

## Source

See `writeup/SpamgenServiceScript.py` for the scorebot checker with full protocol details.
