# Spammer Daemon (iCTF 2005)

Part of the **Spam World** theme of iCTF 2005.

## Description

A TCP service on port 4570 with an SMTP-inspired protocol for creating and
sending spam. The flag is stored as the message body.

## Protocol

```
← (banner)
→ new <username> <password>\n     (create account)
← 200 OK
→ to: xxxx\n
→ spam\n
← (prompts)
→ <FLAG>\n
→ .\n                              (end message)
```

To retrieve: `login <user> <password>\n` then `stat\n` returns the stored message.

Known good passwords: `bbbccc`, `aaabbb`, `cccddd`

## Source

See `writeup/SpammerServiceScript.py` for the scorebot checker.
