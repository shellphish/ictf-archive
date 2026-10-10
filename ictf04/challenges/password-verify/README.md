# Password Verify Daemon (iCTF 2004)

Part of the **UN Voting System** theme of iCTF 2004.

## Description

A TCP service on port 11111 implementing a simple name→flag dictionary.

## Protocol

```
STORE <name> <flag>\n   → store flag under name
DICT <name>\n           → retrieve flag for name
```

## Source

See `writeup/PasswordVerifyServiceScript.py` for the scorebot checker.
