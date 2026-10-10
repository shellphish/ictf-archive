# iCTF 2010 — Hit 'em Where it Hurts

**Date:** December 3, 2010, 8:00 AM – 5:00 PM PST  
**Format:** Attack-Defense  
**Teams:** 72 (~900 students from 16 countries)  
**Winner:** Plaid Parliament of Pwning (PPP), Carnegie Mellon University

---

## The Story

In the 2010 iCTF, the participating teams were part of a **coalition of nations
engaged in cyber-war** with the rogue, corrupted nation of **Litya** — an anagram
of Italy.

Teams represented allied nations tasked with undermining Litya's digital
infrastructure through cyber-attacks, while simultaneously defending their own
national systems from Litya's retaliation. The scenario reflected the early
2010s discourse around nation-state cyber-warfare and critical infrastructure
attacks.

Litya's infrastructure painted a picture of a corrupt, leaky government: a social
network, a dating site, a WikiLeaks-inspired document leak service, and a botnet.
Teams could also **pay bribes** to temporarily unblock their own firewall — a game
economy feature unique to this edition.

## Services

### Per-Team Attack-Defense Services (in `vms/ictf2010.services.tar.gz`)

| Name | Category | Description |
|------|----------|-------------|
| `lityabook` | Web | Litya social network (Facebook parody) — Python |
| `lityahot` | Web | Litya dating/matchmaking service |
| `lityaleaks` | Web | WikiLeaks-inspired document repository (MediaWiki 1.15.5) |
| `idreamofjeannie` | Binary | Custom TCP service, port 2009 |
| `overtcovert` | Binary | Covert/overt channel challenge (C + Java) |
| `applet` | Binary | Java applet service |
| `bincgi` | Binary | Binary CGI |
| `perlcgi` | Web | Perl CGI |
| `weirdtcp` | Network | Non-standard TCP protocol |
| `icmbd` | Network | ICMP-based daemon |
| `mostwanted` | Web | Most-wanted criminals list |

### Infrastructure Services (separate VM images)

| Name | Category | Description |
|------|----------|-------------|
| `bot` | Network | Botnet agent — Python 2 heartbeat client |
| `bribe` | Web | Bribery payment service — Python 2 HTTP |
| `flagsubmission` | Network | Flag capture and submission |
| `scorekeeper` | Web | Central PHP scoring API |

## Game Economy

iCTF 2010 introduced a **game economy**: teams earned points for capturing flags
and could spend in-game money to bribe Litya's "firewall" into temporarily
unblocking their network. The scorekeeper coordinated all transactions with
component credentials:

| Component | Credential |
|-----------|-----------|
| `challenge` | `makeyourchallengecount` |
| `mothership` | `botnetseverywhere` |
| `firewall` | `iseeeverything` |
| `scorebot` | `getthatflagdude` |
| `scoreboard` | `gimmethescores` |

## Data

| Path | Contents | Size |
|------|----------|------|
| `site/` | Original competition website | — |
| `dumps/ictf2010pcap.tar.gz` | Full network traffic captures | ~23 GB |
| `dumps/ictf2010.bot.tar.gz` | Bot service VM | 270 MB |
| `dumps/ictf2010.bribe.tar.gz` | Bribe service VM | 343 MB |
| `dumps/ictf2010.flagsubmission.tar.gz` | Flag submission VM | 457 MB |
| `dumps/ictf2010.information.tar.gz` | Flag submission logs by team | 40 MB |
| `dumps/ictf2010.lityaleaks.tar.gz` | LityaLeaks VM | 535 MB |
| `dumps/ictf2010.scoreboard.tar.gz` | Scoreboard VM | 657 MB |
| `dumps/ictf2010.scorebot.tar.gz` | Scorebot VM | 677 MB |
| `dumps/ictf2010.scorekeeper.tar.gz` | Scorekeeper VM | 462 MB |
| `vms/ictf2010.services.tar.gz` | All per-team services VM | 4.6 GB |
| `pictures/` | Event photographs | — |
| `ucsb_ctfscorebot5.tar.gz` | CTF Scorebot 5 source | — |

## Notable

- First iCTF with an **in-game economy** (bribe payments, money transfers)
- The Scorebot 5 (`ucsb_ctfscorebot5.tar.gz`) is historically significant — used across multiple iCTF editions
- "Litya" is an anagram of "Italy" — a nod to the UCSB Security Lab's Italian roots
- PPP (CMU) took first place, winning a USD $1,000 prize (sponsored by IEEE S&P + Adobe)

## References

- [Original website](https://ictf.cs.ucsb.edu/archive/2010/site)
- [Traffic dumps](https://ictf.cs.ucsb.edu/archive/2010/dumps)
