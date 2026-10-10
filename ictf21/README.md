# iCTF 2021 — The Ethalia Market

**Date:** December 2021 (exact date not documented)
**Format:** Attack-Defense (cyber-economy variant)

---

## The Story

> *Each team represents a for-profit hacking cell operating behind the
> screen of a legitimate business. You don't score points — you grow a
> bank account. Ethalia is watching, and they pay top dollar for
> working zero-days.*

The 2021 iCTF broke from tradition by replacing the standard point system
with an **in-game cyber-economy**. Teams were hacking collectives that
ran "legitimate businesses" (the services) as a front, while selling
vulnerabilities on an underground marketplace.

The game was structured around three economies running simultaneously:

### 1. The Businesses (SLA Income)

As long as your services stayed alive, you earned **100 currency per
service per game-tick**. This was the safe, passive income — essentially
running a protection racket on your own infrastructure.

### 2. The Open Market

Teams could list **exploit-shooters** (Docker containers that attack a
specific vulnerability) and **patches** (Docker containers that fix a
service) for sale at fixed prices. Any team could buy from any seller,
creating a peer-to-peer economy in working code.

- Exploit buyers gained offensive capability without the R&D cost.
- Patch sellers profited from fixing bugs they themselves created.
- Rating and review systems incentivized quality.

### 3. The Nation-State (Ethalia)

**Ethalia** — the nation-state actor lurking in the background — would
pay a large bounty for a genuine **zero-day exploit**: one that worked
against an unpatched service AND bypassed every patch currently listed on
the open market.

Once Ethalia bought a zero-day, it:
- De-listed the bounty (no longer interested in buying)
- Waited a random number of ticks (1–10)
- Deployed the exploit against **all** teams, indefinitely

This created a dilemma: selling a zero-day to Ethalia was lucrative, but
it meant every team (including yours) would soon be hit by it. The only
counter was to patch your service — but that unlocked the bounty again,
incentivizing rivals to find the next zero-day.

## Scoring

- Winning teams: highest final account balance
- Flag submission: splits 1,000 currency among all teams that captured
  flags in that tick, weighted by victim count
- Market transactions: taxed to control inflation
- Ethalia zero-day sale: large one-time payment

## Data

| Path | Contents |
|------|----------|
| `iCTF 2021.docx` | Game design planning document |
| `iCTF Redesign.docx` | Infrastructure redesign document |

## References

- [iCTF website](https://ictf.cs.ucsb.edu)
