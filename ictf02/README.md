# iCTF 2002 — Treasure Hunt in Cyberspace

**Date:** December 6, 2002 (scavenge hunt; Spring 2002 exercise also in archive)
**Location:** UC Santa Barbara
**Format:** Sequential task-based exercise
**Participants:** Two internal UCSB teams (Alpha and Omega)

---

## The Story

The 2002 security exercise was not a proper CTF — it was an exercise in a
graduate security class taught at UC Santa Barbara in 2002.

The class was divided into two teams, **Alpha** and **Omega**, competing
against each other in a **treasure hunt**. The goal was to break into a
simulated (yet realistic) **payroll system** and perform a money transfer
transaction. Each team had to complete a series of tasks (e.g., scan a network
or break into a host) within a limited time window (e.g., 30 minutes).

**Scoring:** The first team to complete a task got the most points. If the
other team also completed it within the time limit, it received a fraction of
the points. If time ran out without completion, a cheat-sheet was provided so
work could continue — but no points were awarded. Tasks were revealed only
after both teams had completed the previous one.

The exercise was designed to generate a dataset of host-based and network
events for **research on multi-step attack correlation**.

## Format

This was a sequential jeopardy-style exercise, not a classic attack-defense
CTF. There was no service defense or inter-team exploitation. Teams raced
through a pre-defined sequence of hacking tasks on a simulated corporate
network containing a payroll system.

## Data

| Path | Contents | Size |
|------|----------|------|
| `dumps/treasurehunt_dataset.tgz` | Network traffic and host audit data | ~6 GB |
| `dumps/img/` | Exercise images | — |
| `Spring/` | Spring 2002 exercise data | — |
| `ScavengeHunt/` | December scavenge hunt variant | — |

## References

- [Traffic dumps and host audit data](https://ictf.cs.ucsb.edu/archive/2002/dumps)
- [Pictures](https://ictf.cs.ucsb.edu/archive/2002/pictures)
