# iCTF 2008 — The Softerror.com Network

**Date:** December 5, 2008, 9:00 AM – 4:00 PM PST
**Location:** Frank Hall, UC Santa Barbara
**Format:** Attack (40 isolated identical target networks)
**Teams:** 40 from 5 continents
**Winner:** ENOFLAG — Technische Universität Berlin, Germany

---

## The Story

> *It's 9am and somebody is frantically knocking on your door. You open it and
> Jack Bauer is right there looking at you with spirited eyes. He screams:
> "Somebody set up us the bomb!"*

Inspired by the TV series *24*, this edition cast participants as elite hackers
hired by Jack Bauer to stop a nuclear device set by a terrorist group called
**Softerror.com**. Teams had seven hours to break into the target network and
neutralize the bomb's timer.

Each of the 40 teams received a private, identical replica of the Softerror.com
infrastructure. There was no inter-team attacking — the competition was a pure
penetration challenge across a four-host network.

## Network Architecture

Teams had to compromise four hosts in sequence:

```
Internet ──► [1] Public Web Server
                      │
                      ▼
             [2] Development Network
                      │
                      ▼
             [3] Financial Network (4 application layers)
                      │
                      ▼
             [4] Bomb Control Server  ◄── final target
```

An active IDS (Snort + anomaly detection) monitored all traffic. Noisy attacks
risked point penalties — stealth was rewarded.

## Challenges

### Main Services (attack chain)

| Directory | Name | Type | Description |
|-----------|------|------|-------------|
| [`challenges/mainwebsite/`](challenges/mainwebsite/) | Public Web Server | web | Entry point; PHP/Apache |
| [`challenges/develsite/`](challenges/develsite/) | Development Network | web | Internal dev servers |
| [`challenges/financialsite/`](challenges/financialsite/) | Financial Network | web | 4-layer financial apps |
| [`challenges/bombsite/`](challenges/bombsite/) | The Bomb | binary | Final target; defuse the timer |

### Side Challenges (jeopardy, extra points)

| Directory | Name | Category | Points |
|-----------|------|----------|--------|
| [`challenges/t100/`](challenges/t100/) | Trivial 100 | misc | 100 |
| [`challenges/t200/`](challenges/t200/) | Trivial 200 | misc | 200 |
| [`challenges/r100/`](challenges/r100/) | Reverse Engineering 100 | binary | 100 |
| [`challenges/r500/`](challenges/r500/) | Reverse Engineering 500 | binary | 500 |
| [`challenges/f200/`](challenges/f200/) | Forensics — Stereogram | forensics | 200 |
| [`challenges/b200/`](challenges/b200/) | Binary / Bomb | binary | 200 |
| [`challenges/bonus/`](challenges/bonus/) | Lagged Fibonacci OTP | crypto | — |

## Scoring

- Teams submitted exploits (code or data) by email or via the web interface.
- Each submission was manually graded by administrators: **0, 100, 200, or 300 points**.
- Points could be spent to buy hints from **"The Mole"** — an insider who knew
  Softerror.com's vulnerabilities.
- 39 exploit submissions are preserved in [`data/scores/exploits/`](data/scores/exploits/).

## Data

| Path | Contents | Size |
|------|----------|------|
| `data/traffic/ctf08_traffic.tgz` | Full competition PCAP | 3.0 GB |
| `data/traffic/ctf08_training_traffic.tgz` | Pre-competition training traffic | 434 MB |
| `data/traffic/ctf08_snort_log.tgz` | Snort IDS alert logs | 12 MB |
| `data/scores/exploits/` | Graded team exploit submissions | — |
| `site/iCTF2008_1_WebSite.tgz` | VMware image — MainWebsite | 356 MB |
| `site/iCTF2008_2_Financial.tgz` | VMware image — Financial | 368 MB |
| `site/iCTF2008_3_Development.tgz` | VMware image — Development | 327 MB |
| `site/iCTF2008_4_Bomb.tgz` | VMware image — Bomb | 431 MB |

Raw PCAP files (per-interface dumps) are in `dumps/` — total ~9 GB.

## Teams

40 teams competed from 9 countries:

- **North America (21):** UCSB, Georgia Tech, RPI, Naval Postgraduate School,
  U Nebraska, Penn State, Northwestern, U Florida, U South Florida, UIUC,
  UNC Charlotte, UC Colorado Springs, UC Davis, U Idaho, Brooklyn Polytechnic, …
- **Europe (16):** TU Berlin (ENOFLAG) ★, RWTH Aachen, U Mannheim,
  Ruhr-U Bochum, U Regensburg, U Hamburg, TU Vienna, Supelec, Eurecom,
  Politecnico di Milano, U Milano, Ural State, Tomsk State, Yaroslavl State,
  Tula State, USTU, …
- **South America (1):** Universidad de La Plata, Argentina
- **Asia-Pacific (2):** Amrita School of Engineering (India),
  Queensland University of Technology (Australia)

## Solutions

Official walkthroughs for all challenges are in [`site/challenges/`](site/challenges/):

- `b200_walkthrough.txt`, `f200_walkthrough.txt`, `r100_walkthrough.txt`,
  `r500_walkthrough.txt`, `t100_walkthrough.txt`, `t200_walkthrough.txt`,
  `bonus_walkthrough.txt`
- Winner's full solution: [`site/ENOFLAG_Walkthrough.html`](site/ENOFLAG_Walkthrough.html)

## Participant Attack Workstation

The `ucsb-ictf-08-final.tar.gz.gpg` GPG archive (password: `ucsb`) contained
the **bootable FreeDOS 4.1 disk image** used by participants as their attack
workstation. Key artifacts are in [`infrastructure/wopr-client/`](infrastructure/wopr-client/):

- **`WOPR.C`** — Source code for the scenario intro program (Open Watcom C).
  Prints the Jack Bauer story one character at a time, then counts down 10 seconds
  and deletes `\KERNEL.SYS`, making the disk unbootable (`unlink("\kernel.sys")`).
- **`STORY.TXT`** — The Jack Bauer / nuclear bomb intro text (C string literal format).
- **`WATTCP.CFG`** — TCP/IP configuration: `my_ip = 128.111.48.248` (UCSB network),
  gateway `128.111.48.2`, domain `cs.ucsb.edu`. Uses WATTCP networking for DOS.
- **`AUTOEXEC.BAT`** — Boot script: loads Crynwr packet driver, runs WOPR, reboots.

The disk contained a full Open Watcom C development environment, which teams
could use to compile custom attack tools in C for DOS.

## Infrastructure Code

The scoring and hint system is in [`iCTF_2008/public_html/`](iCTF_2008/public_html/):

| File | Purpose |
|------|---------|
| `scoreboard.py` | Real-time scoreboard (Python CGI + MySQL) |
| `exploit.py` / `exploit_submit.py` | Exploit upload interface |
| `exploit_grade.py` | Admin grading interface |
| `themole.py` | Hint purchase system ("The Mole") |

## Running Locally

> **Status:** Docker containers are being prepared. See each `challenges/<name>/Dockerfile`.

```bash
# Run a single challenge
cd challenges/mainwebsite
docker build -t ictf08-mainwebsite .
docker run -p 8080:80 ictf08-mainwebsite

# Run the full environment (when infrastructure/docker-compose.yml is ready)
cd infrastructure
docker compose up
```

## References

- [Original website](https://ictf.cs.ucsb.edu/archive/2008/site)
- [Traffic dumps index](https://ictf.cs.ucsb.edu/archive/2008/dumps)
- Story and rules: [`site/story.txt`](site/story.txt)
- Press release: [`site/press_release.txt`](site/press_release.txt)
- Announcement (post-event): [`site/announcement.txt`](site/announcement.txt)
- Competition document: [`site/CTF.pdf`](site/CTF.pdf)
