# iCTF Historical Dataset

This repository contains the archives of the **iCTF (International Capture the Flag)** competition,
organized by the [Security Lab at UC Santa Barbara](https://seclab.cs.ucsb.edu) since 2001.
iCTF is one of the longest-running academic CTF competitions in the world, spanning 23 editions
over more than two decades.

## Editions

| Directory | Date | Title | Format | Teams | Winner |
|-----------|------|-------|--------|-------|--------|
| [ictf01](ictf01/) | 2001 | Red Team / Blue Team | red-blue (class exercise) | — | — |
| [ictf02](ictf02/) | 2002 | Treasure Hunt in Cyberspace | jeopardy | — | — |
| [ictf03](ictf03/) | Nov 2003 | Windows Goes Open-Source | attack-defense | — | — |
| [ictf04](ictf04/) | Nov–Dec 2004 | The 2004 United Nations Vote | attack-defense | — | *(none declared)* |
| [ictf04-05](ictf04-05/) | Jun 2005 | The Bass Tard Corporation | attack-defense | — | — |
| [ictf05](ictf05/) | Dec 2005 | The Spam Museum | attack-defense | — | — |
| [ictf06](ictf06/) | 2006 | The Hillbilly Bank | attack-defense | — | — |
| [ictf07](ictf07/) | 2007 | The Copyright Mafia | attack-defense | — | — |
| [ictf08](ictf08/) | Dec 2008 | "24" (Softerror.com) | attack (isolated) | 40 | ENOFLAG (TU Berlin) |
| [ictf09](ictf09/) | 2009 | Know Your Enemy: Rise of the Botnet | browser exploitation | 47 | CInsects (Germany) |
| [ictf10](ictf10/) | 2010 | Hit 'em Where it Hurts | attack-defense | — | — |
| [ictf11](ictf11/) | 2011 | Money Laundering | attack-defense | — | — |
| [ictf12](ictf12/) | Mar 2013 | SCADA Breakdown | attack-defense (ZDI) | — | PPP (CMU) |
| [ictf13](ictf13/) | Dec 2013 | Nuke 'em (or duck and cover!) | attack-defense (ZDI) | 100+ | Bushwhackers (Russia) |
| [ictf14](ictf14/) | Apr 2015 | Large-scale Hacking | attack-defense (ZDI) | 88 | SpamAndHex (Hungary) |
| [ictf15](ictf15/) | Dec 2015 | Crowdsourcing Evil | attack-defense (crowdsourced) | 35 | Bushwhackers (Russia) |
| [ictf16](ictf16/) | Mar 2017 | Shell We Play a Game? | attack-defense (open, DEF CON qual.) | 314 | Bushwhackers (Russia) |
| [ictf17](ictf17/) | 2017–18 | Defend the Critical Infrastructure | attack-defense | — | — |
| [ictf19](ictf19/) | 2019 | The Grey Hat Nation | attack-defense (ZDI) | — | — |
| [ictf20](ictf20/) | 2020 | Abbey Road (1 After 909) | attack-defense | — | — |
| [ictf21](ictf21/) | 2021 | The Ethalia Market | attack-defense (market mechanic) | — | — |
| [ictf23](ictf23/) | 2023 | AI and Cybersecurity | jeopardy (2 tracks) | ~52 | *(per track)* |
| [ictf24](ictf24/) | 2024 | iCTF 2024 | jeopardy (3 tracks) | ~66 | *(per track)* |

*Note: ictf18 and ictf22 were not held. ictf16 ended early due to a DDoS; LC/BC disqualified.*

---

## Data Availability by Edition

| Edition | Challenges (count) | Source Code | VM Images | Scoreboard | DB / Scores | Notes |
|---------|-------------------|-------------|-----------|------------|-------------|-------|
| [ictf01](ictf01/) | — | — | — | — | — | HTML team reports only |
| [ictf02](ictf02/) | — | — | — | — | — | Minimal files |
| [ictf03](ictf03/) | 6 stubs | — | ✓ VMware | — | — | RedHat 9 VMDKs; scorebot scripts |
| [ictf04](ictf04/) | 9 + source | ✓ | — | — | — | No winner declared; rematch → ictf04-05 |
| [ictf04-05](ictf04-05/) | 10 + source | ✓ | — | — | — | June 2005 Bass Tard rematch |
| [ictf05](ictf05/) | 11 + source | ✓ | — | — | — | Scorebot checker scripts preserved |
| [ictf06](ictf06/) | — | — | — | — | — | Minimal archive |
| [ictf07](ictf07/) | 8 + source | ✓ | — | — | — | Scorebot checker scripts preserved |
| [ictf08](ictf08/) | 11 + Dockerfiles | ✓ | — | — | ✓ MySQL | Reference impl; exploit submissions; side challenges |
| [ictf09](ictf09/) | 8 entries | — | ✓ VMware | ✓ 47 teams | — | Browser-exploit format; stats.pdf; scores.pdf |
| [ictf10](ictf10/) | 15 (13 + source) | ✓ partial | ✓ Linux VMs | — | ✓ MySQL | LVM VMs; scorekeeper backup.sql |
| [ictf11](ictf11/) | 10 stubs | — | ✗ encrypted | — | — | Service VM AES-encrypted; source unavailable |
| [ictf12](ictf12/) | 9 confirmed | — | — | — | — | ZDI framework; writeup from codezen.fr |
| [ictf13](ictf13/) | 11 (debs preserved) | — | — | — | — | 32-bit i386 .deb packages; IRC log; audio |
| [ictf14](ictf14/) | 42 (recycled) | ✓ in src editions | — | ✓ 88 teams | ✓ MySQL | Service DB in ictf15/database/; reg. DB |
| [ictf15](ictf15/) | 43 | partial | — | — | ✓ MySQL | Crowdsourced; service DB preserved; best-service prize |
| [ictf16](ictf16/) | 2 confirmed / 12 total | — | — | ✓ top 10 | — | DEF CON qual; DDoS incident; LC/BC disqualified |
| [ictf17](ictf17/) | — | — | — | — | — | Minimal; anti-cheating system docs |
| [ictf19](ictf19/) | — | — | — | — | — | Service spec template only |
| [ictf20](ictf20/) | 7 + source | ✓ GitHub | — | — | — | Public repo: shellphish/ictf-2020-challs-public |
| [ictf21](ictf21/) | — | — | — | — | — | Source at shellphish/ictf21-challenges (private) |
| [ictf23](ictf23/) | 43 (complete) | ✓ | — | — | ✓ CTFd | Full CTFd export; 21 undergrad + 22 HS challenges |
| [ictf24](ictf24/) | 25+ (complete) | ✓ | — | — | ✓ CTFd | Full CTFd export; 3 tracks (UG + HS + training) |

**Key:** ✓ = available, ✗ = exists but inaccessible (encrypted), — = not in archive, *partial* = incomplete

---

## Repository Structure

Each edition directory follows a uniform layout (see [`_schema/`](_schema/)):

```
ictfXX/
├── metadata.yaml          # Machine-readable edition metadata
├── README.md              # Human-readable overview
├── challenges/            # One subdirectory per service or challenge
│   └── <name>/
│       ├── README.md      # Description, flag format, hints, writeup
│       ├── Dockerfile     # Standalone container for this challenge
│       ├── src/           # Source code (if available)
│       ├── writeup/       # Official solution / exploit / walkthrough
│       └── attachments/   # Files distributed to participants
├── infrastructure/        # Full CTF orchestration
│   ├── docker-compose.yml # Runs all services + scorebot together
│   ├── scoring/           # Scorebot and flag-submission scripts
│   └── network/           # Network topology and configuration
└── data/                  # Historical competition data
    ├── teams/             # Registration, country/university info
    ├── scores/            # Final rankings, flag submissions
    ├── traffic/           # PCAP network dumps
    └── media/             # Photos, logos, press releases
```

## Running a Challenge

Each challenge with a `Dockerfile` can be run standalone:

```bash
cd ictf08/challenges/mainwebsite
docker build -t ictf08-mainwebsite .
docker run -p 8080:80 ictf08-mainwebsite
```

## Running a Full Edition

Editions with sufficient data have a `docker-compose.yml`:

```bash
cd ictf08/infrastructure
docker compose up
```

This starts all services and the scoring infrastructure on an isolated virtual network.

## CTFd / pwn.college Compatibility

Each challenge directory contains a `challenge.yml` in
[ctfcli format](https://github.com/CTFd/ctfcli), making individual challenges
importable into CTFd or pwn.college DOJO courses.

## Notable Editions

- **ictf08** is the best-preserved edition, with full source code, Dockerfiles, scoring
  database, exploit submissions, and side challenges. It serves as the reference
  implementation for the archive structure.
- **ictf10** has the most complete VM extraction: all 15 services recovered from LVM-backed
  VMDK images using `qemu-img` + `debugfs`.
- **ictf14** reused 42 services from six earlier editions (ictf04–ictf13) and has a complete
  88-team final scoreboard. The service database is preserved in `ictf15/database/`.
- **ictf16** (March 2017) was the first iCTF hosted on AWS and the first DEF CON CTF
  qualifier. It ended early when second-place team LC/BC launched a botnet DDoS via a
  Flask SSTI exploit (`flasking_unicorns` service). The forensic analysis is in `ictf16/DDOS.md`.
- **ictf23** and **ictf24** are fully preserved as CTFd exports with complete challenge
  source code across undergraduate and high-school tracks.

## Citation

If you use this dataset in research, please cite:

```bibtex
@misc{ictf-dataset,
  author       = {Vigna, Giovanni},
  title        = {iCTF Historical Dataset},
  year         = {2025},
  organization = {Shellphish},
  url          = {https://github.com/shellphish/ictf-archive}
}
```

## License

Competition infrastructure code and challenge source code are released under the
MIT License unless otherwise noted. Competition data (network captures, scoring
records, team submissions) is released for research and educational use.
