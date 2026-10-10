# Talkun Note Service (iCTF 2004)

Part of the **UN Voting System** theme of iCTF 2004.

## Description

A web-based note service running on port 8081. Users authenticate and store
private notes. The scorebot stores flags as note text after logging in.

## Endpoints

- `GET :8081/login` — login page
- `GET :8081/notes` — view stored notes (flag retrieved here)

## Protocol

HTTP on port 8081. The scorebot logs in with credentials then reads/writes notes.

## Source

See `writeup/TalkunServiceScript.py` for the scorebot checker showing the exact protocol.
