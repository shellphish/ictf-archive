# iCTF 2009 — Know Your Enemy: Rise of the Botnet

**Date:** December 4, 2009
**Format:** Attack-Defense (with novel browser-as-service design)

---

## The Story

The theme of the 2009 iCTF was **"Know Your Enemy: Rise of the Botnet."**

This was a groundbreaking and unusual CTF design: instead of attacking and
defending traditional server-side services, participants had to **create
drive-by download attacks** against simulated web browsers — which served
as the "services" to compromise.

Each team ran a set of automated browser clients that browsed the web
as part of normal activity. Rival teams had to craft malicious web pages or
exploits that would infect these browser clients when they visited, turning
them into bots. Teams simultaneously had to **defend their own browser
services** (patch the browsers, block malicious content) while attacking
everyone else's.

The competition was inspired by the growing threat of browser-based malware
and drive-by download campaigns that were dominating the threat landscape in
2009. It attracted international media coverage, including articles in
*Heise Online* and *Technology Review*.

## Services

| Challenge | Type | Description |
|-----------|------|-------------|
| `erlang-browser` | Web | Erlang browser bot — exploit via erl_eval injection |
| `robabank` | Web | In-game bank — steal credentials from pwned browsers |
| `madoffunds` | Misc | Currency exchange — convert CTF points to in-game money |
| `vulnerable-service` | Binary | Traditional attack-defense service daemon on each team VM |

## Format

- **Primary attack:** Drive-by download against Erlang-based browser bots
- **Browser attraction:** SEO — publish blog entries to rank in the in-game search engine
- **Traditional AD:** `vulnerable_system_service` daemon on each team's Linux VM
- **Economy:** Standalone challenges → "leetness points" → MadoFunds → money → score
- **Browser sessions:** Stealing RobaBank credentials from exploited browsers

## Data

| Path | Contents | Size |
|------|----------|------|
| `dumps/ctf09_traffic.tgz` | Full competition network traffic | ~44 GB total |
| `dumps/ictf09dump.tgz` | Additional network dump | — |
| `Virtual Machine/` | VMware VM image | — |
| `site/` | Team logos, web interface | — |
| `pictures/` | Event photographs | — |

Press coverage preserved:
- `heise online - 27.05.09 - Sicherheitsexperte plädi.pdf`
- `Technology Review _ 20.05.09 _ _Die Russen sind wi.pdf`

## References

- [Original website](https://ictf.cs.ucsb.edu/archive/2009/site)
- [Traffic dumps](https://ictf.cs.ucsb.edu/archive/2009/dumps)
- [Pictures](https://ictf.cs.ucsb.edu/archive/2009/pictures)
