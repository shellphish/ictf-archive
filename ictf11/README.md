# iCTF 2011 — Money Laundering

**Date:** December 2, 2011, 8:00 AM – 5:00 PM PST  
**Format:** Attack-Defense (with money-laundering scoring mechanic)

---

## The Story

You don't think of yourself as a criminal. Sure, your money might come from
unorthodox sources, but everyone does things a little differently in life.
The fact is: to keep your money, you gotta hide that money trail.

The theme for the 2011 iCTF was **money laundering**. Teams managed a fictional
digital money laundering operation and exploited ten services to capture flags and
convert "dirty" points into clean score. But the laundering process carried risk —
the Secret Service, the FBI, and pretty much everyone down to cousin Larry at the
county sheriff's office was working to trace the money.

*"Sink or swim, it's up to you."*

## Scoring Mechanic

Teams earned dirty points by capturing flags from rival services. Flags were
submitted to a scorekeeper that converted them to points, but the conversion was
risky — rivals could tip off the "feds" (the scoring system) to compromise your
laundering operation and reverse your gains. Teams had to find the optimal
risk-vs-reward strategy each round.

Game state (scores, service statuses, team rankings) was pushed to each team's
vulnbox on **port 55555 TCP** as JSON every scoring tick.

## Services (10 services per team)

| # | Name | Description | Times Captured |
|---|------|-------------|----------------|
| 0 | `convicts` | Convict records service | 18,552 |
| 1 | `egoats` | eGoats service | 13,234 |
| 2 | `mailgateway` | Email gateway | 6,437 |
| 3 | `msgdispatcher` | Message dispatcher | 507 |
| 4 | `muleadmin` | Mule administrator portal | 46,867 |
| 5 | `mulemanager` | Mule management service | 34,559 |
| 6 | `mulemassageappointment` | Mule massage booking | 1,995 |
| 7 | `muleuser` | Mule user portal | 2,953 |
| 8 | `sendalert` | Alert/notification service | 5,537 |
| 9 | `smsgateway` | SMS notification gateway | 1,951 |

## Challenges

52 standalone challenges were available. 45 of 52 were solved:
- First challenge solved at 8:03 AM (3 minutes into the competition)
- Last challenge solved at 4:50 PM
- Average money-to-points conversion rate: 2%

## Data

| Path | Contents |
|------|----------|
| `challenges/*/src/` | Package-ready source for all ten services |
| `challenges/*/original-2011/` | Missing helpers, tests, and differing event-time source revisions recovered from the original service tree |
| `site/` | Competition website, game documentation, scripts |
| `site/iC7F11-n37.ova` | Network infrastructure VM (334 MB) |
| `site/iC7F-l337-vu1n.7z` | Service VM — `iCTF 2011 Server.ova` (772 MB, AES-encrypted) |
| `site/120211.computerhacking.mp3` | Audio recording from the event |
| `site/iCTF2011_FluxFingers_writeup.txt` | FluxFingers team writeup |
| `pictures/` | Event photographs |

Note: Traffic dumps are not preserved in the local archive (~1.6 GB total).

## References

- [Original website](https://ictf.cs.ucsb.edu/archive/2011/site)
- [iCTF 2011 Description](site/iCTF_2011_Description.txt)
