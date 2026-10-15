# WOPR Client — iCTF 2008 "24"

The iCTF 2008 competition VM was a **bootable FreeDOS 4.1 disk image** that
participants used as their attack workstation. The disk was recovered from the
GPG-encrypted `ucsb-ictf-08-final.tar.gz.gpg` archive.

## The WOPR Program

`WOPR.EXE` (War Operations Plan Response — referencing the 1983 film *WarGames*)
was the first thing each participant saw when they booted their machine.
It played the competition story one character at a time — Jack Bauer, "24",
nuclear bomb, Softerror.com — framing the attack scenario.

After the story finished, WOPR counted down 10 seconds and then **deleted
`\KERNEL.SYS`**, making the FreeDOS disk unbootable on next reboot. The
`AUTOEXEC.BAT` then called `@reboot`, so the machine rebooted immediately.
This gave participants a hard time limit before their attack workstation
self-destructed (or they had to re-image it from the competition organizers).

### Source

`WOPR.C` — 1529 bytes of C compiled with Open Watcom C (`wcl /l=dos`).
Key implementation details:
- Story text is `#include "story.txt"` as a C string literal
- `srand(42)` — fixed seed (not truly random)
- Closes stdin and stderr (`close(0); close(2)`) — output only
- Ignores SIGINT and SIGTERM — can't be interrupted
- `unlink("\kernel.sys")` — deletes FreeDOS kernel on exit

## Network Configuration

`WATTCP.CFG` loaded the WATTCP TCP/IP stack (DOS networking) with:
```
my_ip    = 128.111.48.248    (UCSB network)
netmask  = 255.255.255.0
domain   = cs.ucsb.edu
gateway  = 128.111.48.2
```

The Crynwr packet driver (`pcntpk`) was loaded for the VMware network adapter.
Teams used this FreeDOS box (with WATTCP-linked tools) to attack the
Softerror.com network containing the actual CTF services.

## Files

| File | Description |
|------|-------------|
| `WOPR.C` | Source code of the intro/scenario program |
| `WOPR.EXE` | Compiled Open Watcom C DOS executable |
| `MAKE.BAT` | Build script (`wcl /l=dos wopr.c`) |
| `STORY.TXT` | The Jack Bauer / nuclear bomb story (C string literal format) |
| `WATTCP.CFG` | TCP/IP network configuration for the attack workstation |
| `AUTOEXEC.BAT` | FreeDOS startup script (loads WATTCP, runs WOPR, reboots) |

## Competition Format

iCTF 2008 used an **ATTACK** format (not attack-defense). There were
40 isolated identical "islands", one per participating team. Each island
had the Softerror.com services (mainwebsite, develsite, financialsite, bombsite)
deployed identically. Teams used their FreeDOS WOPR workstation to attack
their island's services and capture flags.
