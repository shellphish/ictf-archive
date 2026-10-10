# SpamDB (iCTF 2005)

Part of the **Spam World** theme of iCTF 2005.

## Description

A PHP XML-RPC spam database server. The scorebot creates accounts, uploads flags,
and retrieves them via the XML-RPC API.

## API

```python
server = xmlrpclib.Server("http://<ip>/~spamdb/cgi-bin/server.php")
password = server.spamdb.create_account(email)
server.spamdb.upload_data(email, password, flag)
flag = server.spamdb.veryfy_data(email, password)   # note: typo in original
```

## Source

See `writeup/SpamDBServiceScript.py` for the scorebot checker.
