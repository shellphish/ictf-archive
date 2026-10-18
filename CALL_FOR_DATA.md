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

## Missing Data

### ictf05 — Spam Museum (December 2005)

Source needed for 3 services (binaries are in the archive):
- `spamometer` — spam volume measurement service
- `spaminout` — spam tracking service
- `spamback` — spam response service

The source was GPG-encrypted and the password has not been found. If you wrote
these services or know the decryption password for `ctf05-final.tar.gz.gpg`,
please reach out.

---

### ictf12 — SCADA Breakdown (March 2013)

Source needed for 5 services (others already recovered):
- `nuclearboom` — nuclear plant control (binary only)
- `pewpew_smartgrid` — smart grid service (binary only)
- `stockjobber` — stock trading service (binary only)
- `powerplan` — power plant service (Python `.pyc` bytecode only)
- `traintrain` — train scheduling service (binary only)

---

### ictf13 — Nuke 'em (December 2013)

All 9 service names are known but **no source is available**. Services were
written by student teams as course projects. If you wrote one, please share.

---

### ictf14 — Large-scale Hacking (April 2015)

**No service source available** (88 teams, winner SpamAndHex). This edition
reused 41 services from prior years plus one new service (`echo`, port 9148,
by Fish Wang). VM images or service source from any year it reused would help.

---

### ictf15 — Crowdsourcing Evil (December 2015)

**No service source available** for any of the 43 services. Service names are
documented in the archive. VM images welcome.

---

### ictf16 — Shell We Play a Game? (March 2017)

**10 of 12 service names are unknown.** Known services:
- `flasking_unicorns` (Flask SSTI, port 20001)
- `turing_award` (port 20006)

This edition was disrupted by a DDoS from LC/BC. If you played or helped
organize it, we need service names and, ideally, source code.

---

### ictf17 — Unicorns vs. AI (March 2017, DEF CON qualifier)

**No challenges recovered at all** — no service names, no source, no port
assignments. Co-organized with ASU SEFCOM (Adam Doupé). Any information
about the services or infrastructure is welcome.

---

### ictf19 — Grey Hat Nation (March 2019)

**Attack/defense services completely unknown.** Only one jeopardy challenge
(`carprey`) has been recovered. No service names, source, or port assignments
for the main competition.

---

### ictf21 — Ethalia Market (December 2021)

**No challenges recovered.** Source lives in `shellphish/ictf21-challenges`
(currently private). If you have access, please help make it public or
contribute a copy here.

---

## How to Contribute

**Option 1 — Pull request.** Each challenge follows this structure:

```
ictfXX/challenges/<service-name>/
├── challenge.yml      # CTFd/ctfcli metadata
├── src/               # Service source code
├── flag/flag.txt      # The flag (placeholder is fine)
└── writeup/README.md  # Vulnerability description
```

See `ictf08/challenges/ftp/` for a complete example.

**Option 2 — Raw files.** Email VM images, tarballs, or source trees to
vigna@cs.ucsb.edu or open an issue with a download link. We will extract
and format the challenges.

**Option 3 — Information only.** Even without source, useful contributions are:
service names and ports, vulnerability class descriptions, team writeups or
blog posts, network captures from competition day.

---

*Every contribution — a line of source code, a writeup, a service name — helps
preserve 25 years of iCTF history.*
