# iCTF 2010 — PerlCGI (S4)

**Category:** Web
**Port:** 80
**Language:** Perl (CGI)
**Tags:** web, perl, path-traversal

## Description

PerlCGI was a web service with a Perl CGI text file viewer (`txtviewer.pl`)
running via Apache 2.0.59 inside a chroot (SecuriTech_2005/challenge_08_10/).
Teams had to exploit the Perl script to read flag files.

## Source

Extracted from `vms/ictf2010.services.tar.gz` → `iCTF2010_service_perlcgi/Challenge-SecuriTech.vmdk`

| File | Description |
|------|-------------|
| `txtviewer.pl` | Perl CGI text viewer (~1.3 KB) |
| `htdocs/index.html` | Web interface |
| `htdocs/style.css` | Stylesheet |

## Vulnerability

The `txtviewer.pl` validates the `file` parameter with:
```perl
if($file !~ m/.*\.tx/)         # must end in .tx (note: matches .txt)
if($file =~ m/txtviewer\.pl.*\|/)  # block pipe injection via txtviewer.pl
```

The second check is incomplete and can be bypassed. The `$szDirPathLogs`
base path and parameter filtering likely allow path traversal to read arbitrary
`.txt` files, including flag files in the `ccn/` directory.
