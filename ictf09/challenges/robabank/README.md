# iCTF 2009 — RobaBank

**Category:** Web
**Tags:** banking, credential-theft

## Description

RobaBank was the in-game banking service accessible at `robabank.com` within
the competition network. Automated browser bots held accounts with virtual
money. The intended attack path was:

1. Exploit a visiting browser (see `erlang-browser/`)
2. Steal the browser's RobaBank session cookie or credentials
3. Log into RobaBank as the victim
4. Transfer funds to your team's account

Direct attacks on RobaBank were explicitly forbidden by the rules.
The bank was a prop to make the browser exploitation economically meaningful.

## Source

Source not preserved in this archive.
