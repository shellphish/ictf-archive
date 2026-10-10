# Diebald Voting Machine Admin (iCTF 2004)

Part of the **UN Voting System** theme of iCTF 2004.

## Description

A parody of the Diebold voting machines with a CGI admin interface. The scorebot
creates accounts and assigns tasks; the task value contains the flag.

## Endpoints

- `GET/POST /~diebald/cgi-bin/admin` — admin interface for user/task management

## Source

See `writeup/DiebaldServiceScript.py` for the scorebot checker.
