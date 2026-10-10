# iCTF 2017 — Defend the Critical Infrastructure

**Date:** December 2017 (exact date not documented)
**Format:** Attack-Defense (ZDI exploit submission + attack detection)

---

## The Story

> *You have just been hired to secure the critical infrastructure of your country.
> With the globally recognized threat of Sicilian hackers on the offensive, you
> need to defend your country's critical services.*

The 2017 iCTF continued the **National Cyberdefense Corps** narrative
introduced in ictf12. Teams were hired to protect their nation's critical
infrastructure against **Sicilian hackers** while covertly selling exploits
to the **Zebra Dwarf Institution (ZDI)** — a shady underground vulnerability
clearinghouse — for extra points.

## How it Worked

### Attack Detection (Primary Scoring)

The organizers pushed network flow descriptions (src IP, dst IP, src port,
dst port, timestamp, unique ID) to each team. Teams claimed which connections
contained attacks:

- **Correct detection** → points (time-sensitive; detections expire after a
  few hours)
- **False positives** → point penalty
- **Service availability** → creates a multiplier on all detection scores

### Exploit Submission (Secondary Scoring)

Teams developed exploits using a Python-based framework and submitted them
to ZDI. The organizers ran the exploits against other teams:

- **Valid exploit submitted** → points
- **Successful flag capture** → residual points per capture
- **Stealthy attacks** → harder for rivals to detect

### Anti-Cheating

An anti-cheating detection system was introduced (documented in
`Anti-cheating Detection System.docx`), likely in response to the 2016-2017
DDoS incident.

## Data

| Path | Contents |
|------|----------|
| `description.txt` | Competition rules and format |
| `description2.txt` | Narrative/theme description |
| `iCTF 2017 Announcement.docx` | Competition announcement |
| `Anti-cheating Detection System.docx` | Anti-cheat documentation |

Note: ~40 KB total. No traffic dumps, VM images, or service source code
preserved locally.
