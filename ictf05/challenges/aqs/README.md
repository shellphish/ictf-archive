# AQS Guestbook (iCTF 2005)

Part of the **Spam World** theme of iCTF 2005.

## Description

A Python CGI guestbook. The scorebot signs with a random name and stores the
flag as a private comment.

## Endpoints

```
GET /~aqs/cgi-bin/guestbook.py?name=X&comment=<FLAG>&priv=on&command=sign
GET /~aqs/cgi-bin/guestbook.py?name=X&command=lookup    → returns stored flag
```

## Source

See `writeup/AqsServiceScript.py` for the scorebot checker.
