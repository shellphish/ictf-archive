# Contribute (iCTF 2005)

Part of the **Spam World** theme of iCTF 2005.

## Description

A web contribution form. The flag is stored as the `address` field and
retrieved by name through a history endpoint.

## Endpoints

```
POST /~contribute/contribute.html  (fields: name, address=<FLAG>, cc, contribution)
GET  /~contribute/cgi-bin/history.py?name=X    → returns stored address/flag
```

## Source

See `writeup/ContributeServiceScript.py` for the scorebot checker.
