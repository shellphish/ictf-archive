# iCTF 2004 — UN Voting System (pollit)

**Edition:** iCTF 2004
**Category:** web
**Language:** Perl CGI

## Description

The iCTF 2004 scenario placed teams inside the United Nations during a
fictional 2014 Security Council vote. The **pollit** service is the
web-based voting system used by member nations to cast and track ballots.

It is a Perl CGI application (`poll.pl`) that handles user sessions,
vote submission, and result tabulation. The service takes parameters
including `username`, `pollid`, `schmidt`, `blitzkrieg`, `stallone`,
`blix`, `schtrappe` — names corresponding to fictional UN delegates.

## Environment

```bash
docker build -t ictf04-pollit .
docker run -p 8080:80 ictf04-pollit
```

Application available at http://localhost:8080/cgi-bin/poll.pl

## Files

| Path | Description |
|------|-------------|
| `src/cgi-bin/poll.pl` | Main voting CGI script |
| `src/cgi-bin/global_func.pl` | Shared utility functions |
| `src/cgi-bin/local_func.pl` | Local helper functions |
| `src/html/pollit.html` | Frontend HTML |

## Writeup

See [`writeup/`](writeup/).
