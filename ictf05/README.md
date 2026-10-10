# iCTF 2005 — The Spam Museum

**Date:** December 9, 2005
**Format:** Attack-Defense

---

## The Story

The theme of the 2005 iCTF was the **SPAM Museum**, inspired by the actual
[SPAM (the food) Museum](https://www.spam.com/spam-101/the-spam-museum) in
Austin, Minnesota.

Teams competed in an attack-defense format centered on **email spam
infrastructure** — services for sending, routing, filtering, and measuring
spam. In the fictional world of the competition, teams were operating and
sabotaging rival spam operations.

## Services

| Name | Description |
|------|-------------|
| `spamback` | Spam backend / relay service |
| `spaminout` | Spam ingestion and delivery |
| `spamometer` | Spam measurement and tracking |

## Network Architecture

The competition used a VMware-based setup documented in `CTF_setup/`:
- **mainbox** — central server
- **teambox** — per-team competition server
- **imagebox** — VM image distribution server
- VMware Blender used for network management

## Data

| Path | Contents | Size |
|------|----------|------|
| `site/` | Original competition website | — |
| `dumps/` | Network traffic captures | ~33 GB total |
| `CTF2005_spam_with_netdumps/` | VM and network dump archives | — |
| `pictures/` | Event photographs | — |
| `CTF_setup/` | Network setup documentation | — |
| `spam2005Scripts/` | Scoring and spam generation scripts | — |

**Note:** `ctf05-final.tar.gz.gpg` contains the full encrypted VM images
(key not available in this archive).

## References

- [Original website](https://ictf.cs.ucsb.edu/archive/2005/site)
- [Traffic dump](https://ictf.cs.ucsb.edu/archive/2005/dumps)
- [VMs](https://ictf.cs.ucsb.edu/archive/2005/vms)
- [Pictures](https://ictf.cs.ucsb.edu/archive/2005/pictures)
