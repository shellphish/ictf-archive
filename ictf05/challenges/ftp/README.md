# FTP Service (iCTF 2005)

Part of the **Spam World** theme of iCTF 2005.

## Description

An FTP server with anonymous login. The scorebot stores flags as file contents
in `/home/ftp/incoming/`. Each file is named randomly; the filename is the cookie.

## Protocol

Standard FTP (port 21). Anonymous login, then `STOR <filename>` to store flag,
`RETR <filename>` to retrieve.

## Source

See `writeup/FtpServiceScript.py` for the scorebot checker.
