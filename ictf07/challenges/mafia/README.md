# iCTF 2007 — Copyright Mafia

**Edition:** iCTF 2007
**Category:** misc / game-theory
**Language:** Python

## Description

Teams were rival factions within the Copyright Mafia — part organized crime,
part aggressive IP enforcement corporation. Beyond standard attack-defense,
teams could take game-theory actions against each other:

| Script | Action | Effect |
|--------|--------|--------|
| `petition_bot.py` | Plead for mercy | Reduce penalties from rivals |
| `amends_bot.py` | Make reparations | Settle disputes with rivals |
| `shakedown_bot.py` | Extort rivals | Demand tribute payments |
| `copyright_bot.py` | File copyright actions | Attack rivals via legal mechanism |
| `therapy_bot.py` | Rehabilitate members | Reform "turned" team members |
| `snitch_script.py` | Report to authorities | Inform on rivals' activities |
| `wouldyou_bot.py` | Propose deals | Negotiate with other teams |

## Source Files

The `src/` directory contains all game bot scripts (`mafia2007Scripts/`).
The full service binary is only available in the VMware image:

`../../vms/mafia2007.tar.gz` (661 MB)

## Network Traffic

Competition PCAP dumps available in `../../dumps/` (~7.8 GB).

## Writeup

See [`writeup/`](writeup/).
