# Voter Registration Service (iCTF 2004)

Part of the **UN Voting System** theme of iCTF 2004.

## Description

A voter registration web form at `/~register/register.html`. The scorebot fills
in the `wwid` field with the flag value during registration.

## Protocol

HTTP form submission to `/~register/register.html` with fields including `wwid` (flag).

## Source

See `writeup/RegisterServiceScript.py` for the scorebot checker.
