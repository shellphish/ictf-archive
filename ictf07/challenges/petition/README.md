# iCTF 2007 — Copyright Mafia: The Petition

**Edition:** iCTF 2007 | **Category:** web | **Language:** Python 2 (CGI)

## Description
Online petition system for Mafia victims. Python CGI with C helper binaries
(foo.c, bar.c). The original petition.py source is included; a GPG-encrypted
version was also present on the VM (key unknown).

## Run
```bash
docker build -t ictf07-petition . && docker run -p 8082:80 ictf07-petition
```
