# iCTF 2008 — Data

This directory contains historical competition data. Large files (PCAPs, VM
images) may be tracked via Git LFS or stored externally.

## Contents

| Path | Contents |
|------|----------|
| `teams/` | Team registration info (names, universities, countries, IP assignments) |
| `scores/` | Final rankings, exploit submission grading records |
| `traffic/` | Network PCAP dumps from competition day |
| `media/` | Event photos, team logos, press materials |

## Source Locations (original archive)

Large original files live in the raw archive and are symlinked or documented here:

| Original Path | Type | Size |
|---------------|------|------|
| `../site/iCTF2008_1_WebSite.tgz` | VM image | 356 MB |
| `../site/iCTF2008_2_Financial.tgz` | VM image | 368 MB |
| `../site/iCTF2008_3_Development.tgz` | VM image | 327 MB |
| `../site/iCTF2008_4_Bomb.tgz` | VM image | 431 MB |
| `../dumps/ctf08_traffic.tgz` | PCAP | 3.0 GB |
| `../dumps/ctf08_training_traffic.tgz` | PCAP | 434 MB |
| `../dumps/ctf08_snort_log.tgz` | IDS logs | 12 MB |

Raw per-interface PCAPs (20 files, ~9 GB total) are in `../dumps/`.

## Teams

40 teams competed. IP assignments: 10.X.1.0/24 for team X (X = 2..40),
plus admin network 128.111.48.0/24.

Full participant list: `../site/participants.html`
