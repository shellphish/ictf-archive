# Acquire Relay Tracker (iCTF 2005)

Part of the **Spam World** theme of iCTF 2005.

## Description

A PHP/CGI web service that tracks spam relay hosts. Flags are stored as the
`de` (destination/description) field associated with a random IPv6 address.

## Endpoints

```
GET /~acquire/cgi-bin/set.php?ip=<ipv6>&net=ucsb&de=<FLAG>
GET /~acquire/cgi-bin/get.php?ip=<ipv6>    → returns stored flag
```

## Source

See `writeup/AcquireServiceScript.py` for the scorebot checker.
