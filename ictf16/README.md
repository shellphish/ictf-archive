# iCTF 2016–2017 — Shell We Play a Game?

**Date:** March 3, 2017 (organized in 2016, delayed execution)
**Format:** Attack-Defense (AWS-hosted, open to all teams)
**Teams:** 300+ (first edition open to non-academic teams)
**Winner:** Bushwhackers
**Notable:** LC/BC disqualified for launching a DDoS attack

---

## The Story

The 2016-2017 iCTF, **"Shell We Play a Game?"**, was a landmark edition:

- **First iCTF open to all teams** (not just academic institutions)
- **First iCTF hosted on Amazon Web Services** (AWS)
- **One of the largest online attack-defense CTFs ever run** (300+ teams)

The competition ran through the night. By 4:15am, the network began to
collapse. Second-place team **LC/BC** had installed a botnet on compromised
team VMs using a Python SSTI exploit against the `flasking_unicorns` service.
At exactly 4:15am, they sent a payload to 300+ bots instructing each to open
a persistent connection to first-place team **Bushwhackers** — a coordinated
DDoS that brought down the entire game network.

The organizers terminated the competition. Bushwhackers, who were barely ahead,
were declared winners. LC/BC was disqualified.

The UCSB Security Lab published a detailed forensic analysis of the incident,
including reverse-engineered binaries, decoded payloads, and network traffic
analysis — a rare public post-mortem of a CTF DDoS attack.

## Infrastructure

- **Hosting:** Amazon Web Services, /17 network (172.31.128.0/17)
- **Team VMs:** One VM per team at 172.31.129.TEAM_ID or 172.31.130.(TEAM_ID-254)
- **Router:** Central masquerading/anonymizing router
- **Service ports:** 20001–20012

## Data

| Path | Contents |
|------|----------|
| `iCTF 2016 Planning.docx` | Organizer planning documents |
| `Reply to LCBC.docx` | Organizer response to LC/BC's post-competition complaints |

Note: ~20 KB locally. Competition data (traffic, flags, scores) referenced at
the archive website below.

## The DDoS Incident

A detailed forensic analysis of the DDoS is in the competition website:
[`attic/ictf-website/content/pages/ictf_2016-2017_ddos.md`](../attic/ictf-website/content/pages/ictf_2016-2017_ddos.md)

Key findings:
- LC/BC exploited SSTI in `flasking_unicorns` to install a backdoor binary on 300+ team VMs
- Binary was UPX-packed, obfuscated, and contained an anti-analysis check (`if user == "hellman": exit`)
- At 4:15am, LC/BC sent a DDoS payload causing all bots to open persistent connections to Bushwhackers
- LC/BC's first-half VM was found wiped (overwritten with `/dev/zero`)

## References

- [Original website](https://ictf.cs.ucsb.edu/archive/2016-2017/website)
- [Final results](https://ictf.cs.ucsb.edu/archive/2016-2017/scoreboard)
- [Flag captures](https://ictf.cs.ucsb.edu/archive/2016-2017/captures.tar.xz)
- [Traffic round 1](https://ictf.cs.ucsb.edu/archive/2016-2017/traffic-round1.tpxz)
- [Traffic round 2](https://ictf.cs.ucsb.edu/archive/2016-2017/traffic.tpxz)
- DDoS analysis: [`attic/ictf-website/content/pages/ictf_2016-2017_ddos.md`](../attic/ictf-website/content/pages/ictf_2016-2017_ddos.md)
