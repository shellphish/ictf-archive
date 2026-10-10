# iCTF Historical Dataset

This repository contains the archives of the **iCTF (International Capture the Flag)** competition,
organized by the [Security Lab at UC Santa Barbara](https://seclab.cs.ucsb.edu) since 2002.
iCTF is one of the longest-running academic CTF competitions in the world.

## Editions

| Directory | Year | Title | Format | Teams |
|-----------|------|-------|--------|-------|
| [ictf01](ictf01/) | 2001 | The First Security Exercise | red-blue | — |
| [ictf02](ictf02/) | 2002 | Treasure Hunt in Cyberspace | jeopardy | — |
| [ictf03](ictf03/) | 2003 | Windows Goes Open-Source | attack-defense | — |
| [ictf04](ictf04/) | 2004 | The 2004 United Nations Vote | attack-defense | — |
| [ictf04-05](ictf04-05/) | 2005 (Jun) | The Bass Tard Corporation | attack-defense | — |
| [ictf05](ictf05/) | 2005 (Dec) | The Spam Museum | attack-defense | — |
| [ictf06](ictf06/) | 2006 | The Hillbilly Bank | attack-defense | — |
| [ictf07](ictf07/) | 2007 | The Copyright Mafia | attack-defense | — |
| [ictf08](ictf08/) | 2008 | The Softerror.com Network | attack | 40 |
| [ictf09](ictf09/) | 2009 | Know Your Enemy: Rise of the Botnet | attack-defense | — |
| [ictf10](ictf10/) | 2010 | Hit 'em Where it Hurts | attack-defense | — |
| [ictf11](ictf11/) | 2011 | Do You Feel Lucky? | attack-defense | — |
| [ictf12](ictf12/) | 2012–13 (Dec) | SCADA Breakdown | attack-defense | — |
| [ictf13](ictf13/) | 2013 (Dec) | Nuke 'em (or duck and cover!) | attack-defense | — |
| [ictf14](ictf14/) | 2014–15 (Apr) | Large-scale Hacking | attack-defense | — |
| [ictf15](ictf15/) | 2015 (Dec) | Crowdsourcing Evil | attack-defense | — |
| [ictf16](ictf16/) | 2016–17 | Shell We Play a Game? | attack-defense | 300+ |
| [ictf17](ictf17/) | 2017 | Defend the Critical Infrastructure | attack-defense | — |
| [ictf19](ictf19/) | 2019 | The Grey Hat Nation | attack-defense (ZDI) | — |
| [ictf20](ictf20/) | 2020 | Abbey Road (1 After 909) | attack-defense | — |
| [ictf21](ictf21/) | 2021 | The Ethalia Market | attack-defense | — |
| [ictf23](ictf23/) | 2023 | AI and Cybersecurity | jeopardy (2 tracks) | ~52 |
| [ictf24](ictf24/) | 2024 | iCTF 2024 | jeopardy (2 tracks) | ~66 |

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

Each challenge has a standalone `Dockerfile`. To run one:

```bash
cd ictf08/challenges/mainwebsite
docker build -t ictf08-mainwebsite .
docker run -p 8080:80 ictf08-mainwebsite
```

## Running a Full Edition

Each edition with sufficient data has a `docker-compose.yml`:

```bash
cd ictf08/infrastructure
docker compose up
```

This starts all services and the scoring infrastructure on an isolated virtual network.

## CTFd / pwn.college Compatibility

Each challenge directory contains a `challenge.yml` in
[ctfcli format](https://github.com/CTFd/ctfcli), making individual challenges
importable into CTFd or pwn.college DOJO courses.

## Data Availability

| Data Type | Editions | Notes |
|-----------|----------|-------|
| Service source code | 2004–2010 | Varying completeness |
| VMware VM images | 2004–2010 | Original deployment images |
| PCAP network dumps | 2003–2010 | Up to 44 GB per edition |
| CTFd exports | 2023–2024 | Full challenge + solve data |
| Scoring database | 2008, 2014–2015 | MySQL dumps |
| Team exploit submissions | 2008 | Graded submissions |
| Official writeups/walkthroughs | 2008 | Per-challenge solutions |

Large files (VM images, PCAPs) are stored via [Git LFS](https://git-lfs.com).

## Citation

If you use this dataset in research, please cite:

```bibtex
@misc{ictf-dataset,
  author       = {Vigna, Giovanni},
  title        = {iCTF Historical Dataset},
  year         = {2025},
  organization = {UC Santa Barbara Security Lab},
  url          = {https://github.com/ucsb-seclab/ictf-dataset}
}
```

## License

Competition infrastructure code and challenge source code are released under the
MIT License unless otherwise noted. Competition data (network captures, scoring
records, team submissions) is released for research and educational use.
