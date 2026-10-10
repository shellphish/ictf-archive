# iCTF 2010 — ICMBD (S8)

**Category:** Binary
**Port:** 8080
**Tags:** binary, network, botnet

## Description

ICMBD ("International Cruise Missile Bureauscratique Depepartmentalish") was
the competition's special prize service. It was physically connected to a USB
missile launcher in the UCSB hallway — successfully hacking in gave the team
the ability to fire real (foam) missiles. Running at 10.14.42.42:8080.

Hackinberg (TU Graz) was announced as the first team to break in:
*"Hackinberg broke into the missile system... CONGRATULATIONS!!!"*
*"We 0wn you: thanks for moving the missile"*

Each team's bot agent (bot.py) sent base64-encoded heartbeats to ICMBD,
making the bot service integral to this challenge.

## Source

Source not preserved in this archive. The ICMBD VM is not included in
`vms/ictf2010.services.tar.gz` — it was a unique infrastructure service.
