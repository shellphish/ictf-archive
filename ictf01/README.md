# iCTF 2001 — The First Security Exercise

**Year:** 2001
**Location:** UC Santa Barbara
**Format:** Red-Blue Team Exercise
**Participants:** Internal UCSB graduate students only

---

## The Story

The very first iCTF was not a public competition — it was an in-class exercise
for a graduate security course at UC Santa Barbara. Two teams competed
directly against each other on a small network of five bare-metal Linux machines
housed at UCSB. One team (red) attacked while the other (blue) defended, and
roles rotated.

Teams were named after sub-groups: the blue side had Alpha and Omega components,
while the red side included sub-groups named Buzzco, Eagles, Escalation,
E-Squared, Vulture, and Wolf. This exercise was the seed from which the
international competition grew.

## Infrastructure

Five Intel x86 machines (166 MHz, 64–128 MB RAM) running Red Hat Linux 6.1/6.2
on the 128.111.54.0/24 network at UCSB:

| Hostname | IP | Name |
|----------|----|------|
| BETA | 128.111.54.60 | altman |
| ALFA | 128.111.54.70 | coppola |
| GAMMA | 128.111.54.30 | truffault |
| KAPPA | 128.111.54.20 | leone |
| LAMBDA | 128.111.54.10 | mamet |

Primary service: SSH 1.2.27 (an intentionally vulnerable version).

## Data

| Path | Contents |
|------|----------|
| `2001_Winter/` | Files from Winter 2001 exercise |
| `RedBlueTeam/` | HTML reports, flag files, network info |
| `RedTeamBlueTeam 2001/` | Exercise data (variant) |
| `Testbed/` | Host configuration notes |

## Notes

This exercise predates the public iCTF. It established the red-blue format
and the UCSB Security Lab's tradition of running hacking competitions as
educational tools. The next exercise (2002, "Treasure Hunt in Cyberspace")
would be the first to have the structure more recognizable as a CTF.
