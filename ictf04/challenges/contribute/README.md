# Campaign Contribution Service (iCTF 2004)

Part of the **UN Voting System** theme of iCTF 2004.

## Description

A campaign donation tracker. The scorebot stores flags as the `comment` field
in donation records via a GET request.

## Endpoint

```
GET /~support/cgi-bin/donate.py?candidate=X&cc=X&amount=X&comment=<FLAG>
```

## Source

See `writeup/ContributeServiceScript.py` for the scorebot checker.
