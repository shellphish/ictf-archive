# Discussit Chat Service (iCTF 2004)

Part of the **UN Voting System** theme of iCTF 2004.

## Description

A TCP conversation service on port 7413. Clients initiate conversations by
sending `<name> <topic>\n`; the topic serves as the flag store. The service
replies with a welcome message containing "summoning operator" on success.

## Protocol

```
→ "<name> <flag>\n"
← (welcome message containing "summoning operator")
→ (random questions)
← (responses)
```

To retrieve: reconnect with same name, service replies with "Last time" and the stored topic.

## Source

See `writeup/DiscussitServiceScript.py` for the scorebot checker.
