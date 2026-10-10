# iCTF 2010 — LityaBook (S1)

**Category:** Web
**Port:** 80
**Language:** Python 2 + Java
**Tags:** web, python, java, social-network

## Description

LityaBook was the social-network service (Facebook parody) in the fictional
Lityan cyberspace. Characters in the game's backstory (e.g., Femily Edeo)
used it to connect with people they found on LityaHot. Each team defended
their own LityaBook instance while attacking others'.

## Source

Extracted from `vms/ictf2010.services.tar.gz` → `lityabook/iCTF2010_Service_Base.vmdk`
(Ubuntu Server 10.10 32-bit).

| File | Description |
|------|-------------|
| `lytiabook.py` | Main Python 2 HTTP service (BaseHTTPServer + SQLite3, ~33 KB) |
| `lytiabook.ini` | Configuration file |
| `Connect.py` | Database connection helpers |
| `Edef.py` | Exception/error definitions |
| `service_template.py` | Scorebot template |
| `java/CheckProfiles.java` | Java profile checker |
| `java/FriendshipAcceptor.java` | Java friendship request handler |
| `java/checkrequests.py` | Python wrapper invoking the Java component |

## Attack Vectors

- Python 2 BaseHTTPServer with SQLite3 — look for SQL injection, path
  traversal, or logic flaws in the profile/friendship endpoints
- Java component `FriendshipAcceptor` handles requests — check for
  deserialization or injection issues
