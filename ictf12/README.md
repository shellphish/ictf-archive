# iCTF 2012–2013 — SCADA Breakdown

**Date:** March 22, 2013, 8:00 AM – 5:00 PM PDT
**Format:** Attack-Defense (with ZDI exploit submission framework)
**Note:** This edition ran in March 2013 (delayed from the 2012 school year); the local directory is named `ictf12`.

---

## The Story

> *Welcome to the National Cyberdefense Corps! You, along with other qualified
> applicants, have just been hired to secure the critical infrastructure of
> your country.*

In the 2012 iCTF competition, teams had to **attack critical infrastructure
components — SCADA systems** (Supervisory Control and Data Acquisition).
SCADA systems control physical industrial processes: power grids, water
treatment plants, chemical manufacturing, transportation networks.

The fictional scenario: **Sicilian hackers** are on the offensive, threatening
to compromise your nation's critical services. You must defend your country's
SCADA infrastructure while simultaneously developing exploits to attack other
nations' systems — selling those exploits to the **Zebra Dwarf Institution
(ZDI)**, a sort of underground vulnerability clearinghouse, for points and
residuals.

## Scoring System (ZDI Framework)

This edition introduced the **ZDI exploit submission framework** used in
several subsequent iCTF editions:

1. **Detection scoring:** The organizers push attack flow descriptions (src/dst
   IP, port, timestamp, ID) to each team. Teams claim which connections are
   attacks. Correct detections → points; false positives → point penalties.
   Detections become worthless after a few hours (time-sensitive).

2. **Exploit submission:** Teams develop exploits in a Python-based framework
   and submit them to ZDI. ZDI runs the exploits against other teams. Successful
   flag capture → points to the attacking team + residuals per capture.

3. **Service availability multiplier:** Teams must keep their services up.
   Historical availability creates a multiplier on detection scores.

## Data

| Path | Contents |
|------|----------|
| `pictures/` | Event photographs |
| `description3.txt` | Full competition description and rules |

Note: Minimal data preserved locally (~7.6 MB). No traffic dumps or VM images
in the local archive.

## References

- Competition registration was at http://www.ictf2013.info
- [Pictures](https://ictf.cs.ucsb.edu/archive/2010/pictures) (linked in website)
