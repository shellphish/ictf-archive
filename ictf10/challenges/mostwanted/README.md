# iCTF 2010 — MostWanted (S2)

**Category:** Network
**Port:** 2048
**Language:** Python 2
**Tags:** network, python

## Description

MostWanted was a custom network service hosting a "most wanted criminals"
database. Teams exploited protocol or logic vulnerabilities to capture flags
from rival instances. During the competition organizers leaked the source on
LityaLeaks, and asked teams to work on it: *"HUGE LEAK ON LITYALEAKS! SOURCE
CODE OF MOSTWANTED ON SITE."*

## Source

Extracted from `vms/ictf2010.services.tar.gz` → `mostwanted/iCTF2010_Service_Base.vmdk`

| File | Description |
|------|-------------|
| `mostwanted.py` | Python 2 service (~8.5 KB) |
| `secret.txt` | Flag file |

## Notes

The `data/` directory contained many `mug*.` files (mugshot images, likely
per-team flag data). The service operates on port 2048.
