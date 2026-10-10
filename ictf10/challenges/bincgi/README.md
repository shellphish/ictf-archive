# iCTF 2010 — BinCGI (S3)

**Category:** Binary
**Port:** 80
**Tags:** binary, web, cgi, reverse-engineering

## Description

BinCGI was a web service with a compiled CGI binary ("Storm Control Logs viewer
by Darknight@1337-team.com"). Running as a CGI executable via Apache 2.0.59
inside a chroot (SecuriTech_2006/challenge_15/). Teams had to find and exploit
binary vulnerabilities in the CGI handler.

## Source

Extracted from `vms/ictf2010.services.tar.gz` → `iCTF2010_service_bincgi/Challenge-SecuriTech.vmdk`

| File | Description |
|------|-------------|
| `displ.cgi` | 32-bit ELF CGI binary (~18 KB, debug symbols intact) |
| `htdocs/README.txt` | Service description |

## Analysis

Reverse `displ.cgi` with debug symbols. The binary parses HTTP query
parameters passed through Apache CGI. Look for stack buffer overflows or
format string vulnerabilities in parameter handling. The flag is in
`/home/gpior/data/` inside the chroot.
