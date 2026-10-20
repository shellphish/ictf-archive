# iCTF 2014–2015 — Large-scale Hacking

**Date:** April 2015 (organized in 2014, delayed execution)
**Format:** Attack-Defense (proxy exploit submission model)

---

## The Story

The 2014-2015 iCTF, themed **"Large-scale Hacking,"** introduced a novel
infrastructure that reflected the realities of large-scale remote hacking
operations.

Teams received a **VirtualBox VM as their router** into the competition network.
The VMs were delivered encrypted; the decryption key was disclosed on competition
morning — adding a time-pressure element to the setup phase.

Unlike classic attack-defense where teams attack each other directly, this
edition used a **proxy exploitation model**: teams could not attack other teams
directly. Instead, they developed exploits using an organizer-provided framework
and **submitted them to the organizers**, who would run the exploits on each
team's behalf against the target teams. This design prevented DoS attacks and
ensured all exploits were assessed fairly.

## Scoring System

Four components contributed to a team's final score:

| Component | Description |
|-----------|-------------|
| **SLA** | Service Level Agreement — services must stay up and uncompromised |
| **Timeliness** | Bonus for teams that exploit a service earlier in the game |
| **Diversity** | Bonus for exploiting a larger number of distinct services |
| **Leetness** | Points based on how many teams also exploited a service (rarer = more points) |

## Data

| Path | Contents |
|------|----------|
| `2014-2015.mysql.gz` | MySQL dump with scoring/team data |
| `infrastructure/metactf/` | Recovered reused-service source, gamebot scripts, and Debian deployment tooling |
| `ictf scoreboard/` | Scoreboard screenshots |
| `ictf20145_announcement.txt` | Competition instructions to teams |
| `ictf2014-5-press_release.txt` | Press release |
| `ictf2014_scoreboard_screenshot.png` | Final scoreboard |

The `metactf` snapshot contains 54 package-ready services from earlier iCTF
editions. It is the candidate pool used while preparing this event; the exact
41-service final selection is not established by the repository alone.
Traffic dumps have not been recovered.

## References

- Announcement: [`ictf20145_announcement.txt`](ictf20145_announcement.txt)
- Pictures: [archive link](https://ictf.cs.ucsb.edu/archive/2014-2015/pictures)
