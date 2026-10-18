# iCTF Archive — Call for Data

This repository is a public archive of the International Capture the Flag (iCTF)
competition, founded by Giovanni Vigna at UC Santa Barbara in 2001 and organized by
[Shellphish](https://shellphish.net) from 2005 to the present.

We have recovered challenge source code and metadata for most editions, but several
years have gaps. **If you organized, played in, or wrote services for any of the
editions below, we would love your contribution.**

Contact: Giovanni Vigna \<vigna@cs.ucsb.edu\> or open a pull request against
[shellphish/ictf-archive](https://github.com/shellphish/ictf-archive).

---

## What We Have

| Edition | Year | Theme | Challenges | Source |
|---------|------|-------|------------|--------|
| ictf01 | 2001 | Red Team / Blue Team | 3 (phf, lprng, wuftpd) | ✓ exploit code |
| ictf02 | 2002 | Treasure Hunt in Cyberspace | 4 (guestbook, save-message, query-extension, transaction) | ✓ full source |
| ictf03 | 2003 | Windows Goes Open-Source | 6 | ✓ full source + Dockerfiles |
| ictf04 | 2004 | The United Nations Vote | 9 | ✓ full source |
| ictf04-05 | 2005 | Bass Tard Corp (rematch) | 10 | ✓ full source |
| ictf05 | 2005 | Spam Museum | 13 | partial (spamometer/spaminout/spamback: binaries only) |
| ictf06 | 2006 | Hillbilly Bank | 9 | ✓ full source |
| ictf07 | 2007 | Copyright Mafia | 8 | ✓ full source |
| ictf08 | 2008 | "24" (Nuclear Bomb) | 18 | ✓ full source + Dockerfiles |
| ictf09 | 2009 | Rise of the Botnet | 4 | ✓ source + Windows artifacts |
| ictf10 | 2010 | Hit 'em Where it Hurts | 15 | ✓ source (13/15) |
| ictf11 | 2011 | Money Laundering | 10 | ✓ full source |
| ictf12 | 2013 | SCADA Breakdown | 10 | partial (see below) |
| ictf13 | 2013 | Nuke 'em | 9 | ✗ stubs only |
| ictf14 | 2015 | Large-scale Hacking | 42 (1 new) | ✗ stubs only |
| ictf15 | 2015 | Crowdsourcing Evil | 43 | ✗ stubs only |
| ictf16 | 2017 | Shell We Play a Game? | 12 (2 named) | ✗ stubs only |
| ictf17 | 2017 | Unicorns vs. AI | 12 (unknown names) | ✗ no challenges |
| ictf19 | 2019 | Grey Hat Nation | 1 (carprey) | partial |
| ictf20 | 2020 | Abbey Road | 7 | ✓ full source |
| ictf21 | 2021 | Ethalia Market | unknown | ✗ no challenges |
| ictf23 | 2023 | AI and Cybersecurity | 43 | ✓ full source |
| ictf24 | 2024 | iCTF 2024 | 25 | ✓ full source |

---

## What We Need

### ictf05 — Spam Museum (December 2005)

**Missing source for 3 services:**
- `spamometer` — spam volume measurement service
- `spaminout` — spam tracking service
- `spamback` — spam response service

The binaries are in the archive. The source was GPG-encrypted and the password
has not been found in any mailing list archive. If you wrote these services or
know the decryption password for `ctf05-final.tar.gz.gpg`, please reach out.

---

### ictf12 — SCADA Breakdown (March 2013)

**Services with binaries or bytecode only (source needed):**
- `nuclearboom` — nuclear plant control service (binary only)
- `pewpew_smartgrid` — smart grid service (binary only)
- `stockjobber` — stock trading service (binary only, run.sh wrapper)
- `powerplan` — power plant service (Python 2.7 `.pyc` bytecode only)
- `traintrain` — train scheduling service (binary only)

**Services with full source already recovered:**
airplane, curiosityblogging, pesticides, water, dexware ✓

If you wrote `nuclearboom`, `pewpew_smartgrid`, `stockjobber`, `powerplan`, or
`traintrain`, please share the source.

---

### ictf13 — Nuke 'em (December 2013)

**All 9 service names are known but no source is available:**
(Services were written by student teams as course projects.)

If you wrote a service for iCTF 2013, please share the source. We have stubs
for all 9 services in the archive.

---

### ictf14 — Large-scale Hacking (April 2015)

**42 services total — source needed for most.**

This edition reused 41 services from ictf04 through ictf13, plus one new service:
- `echo` (port 9148) — written by Fish Wang

If you have the VM images or service source from ictf14, please contribute.
The competition used encrypted VirtualBox VMs with a novel exploit-submission format
(88 teams; winner SpamAndHex).

---

### ictf15 — Crowdsourcing Evil (December 2015)

**43 services — source unknown for all.**

Service names are documented in the archive from the CTFd database. If you wrote
a service for iCTF 2015 or have VM images from the competition, please contribute.

---

### ictf16 — Shell We Play a Game? (March 2017)

**12 services on ports 20001–20012. Only 2 names are known:**
- `flasking_unicorns` (Flask SSTI vulnerability)
- `turing_award` (port 20006)

**The other 10 service names and source are completely unknown.**

This was the edition disrupted by the LC/BC DDoS attack. If you played in or
organized iCTF 2017 (the "Shell We Play a Game?" / "Unicorns, Ponies, and
Rainbows vs. AI" edition), we need the service names and, ideally, source code.

---

### ictf17 — Unicorns vs. AI (March 2017, DEF CON qualifier)

This was the same competition as ictf16 (March 3–4, 2017, organized jointly
with ASU SEFCOM). **We have no challenge information at all** — no service
names, no source, no port assignments.

If you organized this edition or have network captures from the competition
infrastructure, please reach out.

---

### ictf19 — Grey Hat Nation (March 2019)

**Only 1 jeopardy challenge recovered** (`carprey` — TI-84+ SE emulator, Z80 shellcode).

The main attack/defense services from ictf19 are completely unknown — no service
names, no source, no port assignments.

If you organized iCTF 2019 or played and captured traffic, please contribute.

---

### ictf21 — Ethalia Market (December 2021)

**No challenges recovered.** This edition featured a novel cyber-economy mechanic
with in-game currency, an exploit/patch marketplace, and a nation-state actor
(Ethalia) that purchased zero-days. 88 teams participated; winner: Bushwhackers.

The source repository `shellphish/ictf21-challenges` exists on GitHub but is
private. If you have access or wrote services for this edition, please help
make the source public or contribute a copy here.

---

## How to Contribute

### Option 1: Pull Request

Each challenge follows this directory structure:

```
ictfXX/challenges/<service-name>/
├── challenge.yml      # CTFd/ctfcli metadata
├── src/               # Service source code
├── flag/flag.txt      # The flag (can be a placeholder)
├── writeup/README.md  # Vulnerability description and exploit
├── ro/                # Read-only files mounted into container
└── rw/                # Read-write files mounted into container
```

See any existing challenge (e.g., `ictf08/challenges/ftp/`) for a complete example.

### Option 2: Raw Files

If you have VM images, tarballs, or source trees without time to format them,
just email them to vigna@cs.ucsb.edu or open an issue with a download link.
We will extract and format the challenges.

### Option 3: Information Only

Even if you don't have source code, the following is useful:
- Service names and the ports they ran on
- A description of the vulnerability class
- Team writeups or blog posts about exploits you used
- Network captures from competition day

---

## Format Reference

`challenge.yml` template for a service without source:

```yaml
name: <service-name>
author: iCTF Organizers
description: |
  **iCTF 20XX — <Theme>**

  <One-paragraph description of what the service does and its vulnerability.>

  Source not available in archive.
value: 200
type: standard
flags:
  - FLAG_ICTFYYYY{placeholder}
topics:
  - pwn
hints: []
files: []
image: null
protocol: tcp
host: null
port: <port>
```

---

*This archive is a labor of love for the security education community.
Every contribution — a line of source code, a writeup, a service name — helps
preserve 25 years of iCTF history.*
