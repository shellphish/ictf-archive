# Votecast (iCTF 2004)

Part of the **UN Voting System** theme of iCTF 2004.

## Description

A TCP vote-casting service on port 1969. All protocol messages are XOR-encrypted
with the repeating key `F2654hD4` (hex-encoded). The plaintext protocol is:

```
!<wwid> <vote>
```

where `vote` is the flag. The service replies with `OK <XOR-encrypted-flag>`.

## Encryption

```python
key = 'F2654hD4'
encrypted = ''.join('%02X' % (ord(key[i % 8]) ^ ord(c)) for i, c in enumerate(msg))
```

## Source

See `writeup/VotecastServiceScript.py` for the scorebot checker (includes full encrypt/decrypt functions).
