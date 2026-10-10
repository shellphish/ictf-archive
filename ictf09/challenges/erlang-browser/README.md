# iCTF 2009 — Erlang Browser

**Category:** Web / Browser Exploitation
**Tags:** erlang, browser-exploit, drive-by-download

## Description

The Erlang browser was the central attack target in iCTF 2009. It was a
custom Erlang-based web browser that automated "user" bots ran. Each browser
would:

1. Read news from the in-game news feed
2. Pick an interesting topic
3. Query the in-game search engine for that topic
4. Visit sites returned in the search results

Teams had to craft malicious pages that exploited vulnerabilities in the
browser when it visited. A known attack vector was Erlang's `erl_eval` module,
which could be abused for arbitrary code evaluation.

Successful exploitation let teams:
- Execute code in the browser process
- Steal the browser's RobaBank session / credentials
- Transfer the victim's in-game funds to their own account

To attract browser visits, teams needed to rank in the in-game search engine:
publish blog entries on trending topics, optimize for the SEO algorithm.

## Source

The browser source was distributed during the competition as
`http://www.cs.ucsb.edu/~vigna/browsers.tar.gz` and is not preserved here.
A Java browser implementation was also present but reportedly unstable.

## Techniques

- Erlang `erl_eval` code injection
- Drive-by download via SEO manipulation
- Credential theft from browser session
