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

| Name | Category | Vulnerability | Source |
|------|----------|---------------|--------|
| [`museum`](challenges/museum/) | web | Command injection (`grep -i $keyword`), path traversal, hardcoded password | ✓ Perl |
| [`contribute`](challenges/contribute/) | web | SQL injection (unescaped MySQL INSERT) | ✓ Python |
| [`spamgen`](challenges/spamgen/) | web | Info disclosure (Markov model reads all flags) | ✓ Python |
| [`aqs`](challenges/aqs/) | pwn | Rotating-key cipher bypass in C CGI → exec to Perl | ✓ C + Python + Perl |
| [`spamdb`](challenges/spamdb/) | web | Weak password generation, XML-RPC PHP | ✓ PHP |
| [`acquire`](challenges/acquire/) | web | SQL injection (PHP, large scripts) | ✓ PHP |
| [`ftp`](challenges/ftp/) | network | Custom C FTP server; all flags world-readable | ✓ C |
| [`spammer`](challenges/spammer/) | network | Custom binary SPAM protocol (Python) | ✓ Python |
| [`spamagent`](challenges/spamagent/) | pwn | Code injection in XML+Tcl agent scripting engine | ✓ C |
| [`spaminout`](challenges/spaminout/) | pwn | C spam relay (spamin/spamout pair) | ✓ C |
| [`syscalld`](challenges/syscalld/) | pwn | Remote x86 assembly exec; arbitrary syscalls via `sysenter` | binary only |
| [`spamometer`](challenges/spamometer/) | pwn | Spam metrics service (binary only) | ✗ encrypted (`spamometer-1.0.tar.gz.gpg`) |
| [`spamback`](challenges/spamback/) | unknown | Spam response service — no binary or source recovered | ✗ encrypted (`spamback.tgz.gpg`) |

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
