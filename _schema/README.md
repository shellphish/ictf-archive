# Schema Reference

This directory defines the conventions used across all iCTF edition directories.

## `metadata.schema.yaml`

Documents every field that may appear in an edition's `metadata.yaml`.
REQUIRED fields must be present; OPTIONAL fields should be included when the
data is known.

## Directory Layout

Every edition (`ictfXX/`) should follow this structure:

```
ictfXX/
├── metadata.yaml          # Machine-readable metadata (see metadata.schema.yaml)
├── README.md              # Human-readable overview
│
├── challenges/            # One subdirectory per service or challenge
│   └── <slug>/
│       ├── challenge.yml  # ctfcli descriptor (CTFd-compatible)
│       ├── README.md      # Description, flag format, difficulty, writeup links
│       ├── Dockerfile     # Standalone container (remote/interactive challenges)
│       ├── src/           # Original service/challenge source code
│       ├── writeup/       # Official exploit, solution script, and notes
│       ├── attachments/   # Files distributed to participants during the CTF
│       ├── rw/            # Writeable runtime files (Docker volume)
│       └── ro/            # Read-only runtime files (compiled binary, etc.)
│
├── infrastructure/        # Full CTF environment
│   ├── docker-compose.yml # Starts all services + scoring infrastructure
│   ├── scoring/           # Scorebot, flag submission, and checker scripts
│   └── network/           # Network topology diagrams and configuration
│
└── data/                  # Historical competition data (read-only artifacts)
    ├── teams/             # Registration records, university/country info
    ├── scores/            # Final rankings, flag submission logs
    ├── traffic/           # PCAP dumps (may be Git LFS pointers)
    └── media/             # Photos, logos, press releases, presentations
```

## `challenge.yml` Template (ctfcli / CTFd)

The `challenge.yml` format is defined by [ctfcli](https://github.com/CTFd/ctfcli),
the official CTFd CLI tool. Every challenge should have one.

```yaml
name: "iCTF YEAR — Challenge Title"
author: "Author Name"
category: web          # web | binary | crypto | forensics | network | misc
description: |
  <The challenge description shown to participants.>
value: 100             # points (0 for attack-defense stages)
type: standard         # standard | dynamic

image: .               # "." = build from Dockerfile; null = no container
protocol: http         # http | tcp | null

flags:
    - ictfYEAR{flag_here}

topics:
    - web exploitation

tags:
    - web
    - ictfYEAR

files:
    - src/             # files distributed to participants
    - attachments/

state: visible
version: "0.1"
```

## Challenge README Template

Each `challenges/<slug>/README.md` should include:

```markdown
# iCTF YEAR — Challenge Title

**Edition:** iCTF YEAR
**Category:** <web | binary | crypto | forensics | network | misc>
**Points:** N
**Port:** N (if applicable)

## Description

<The challenge description shown to participants.>

## Environment

Build and run locally:

    docker build -t ictfYY-<slug> .
    docker run -p PORT:PORT ictfYY-<slug>

## Files

| File | Description |
|------|-------------|
| `src/...` | Service source code |
| `attachments/...` | Files distributed to participants |

## Writeup

See [`writeup/`](writeup/) for the official solution and exploit.
```

## Conventions

- **Slug:** lowercase, hyphens, no spaces. Matches the directory name.
- **Large files:** VM images and PCAPs are stored in Git LFS. Any file > 50 MB
  should be tracked with `git lfs track`.
- **Encryption:** Some original VM images are GPG-encrypted. Include a note in
  `data/` with the key distribution policy.
- **Symlinks:** Prefer symlinks over copying large files within the repo
  (e.g., `data/traffic/` → original dump location).
