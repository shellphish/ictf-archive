# iCTF 2010 — LityaHot (S0)

**Category:** Web
**Port:** 80
**Language:** Python 2
**Tags:** web, python, dating

## Description

LityaHot was the dating and photo-sharing web service in the fictional Lityan
cyberspace. Characters in the game's backstory (e.g., Femily Edeo) browsed it
for profile photos and then contacted people through LityaBook. Teams attacked
rival instances while defending their own.

## Source

Extracted from `vms/ictf2010.services.tar.gz` → `lityahot/iCTF2010_Service_Base.vmdk`

| File | Description |
|------|-------------|
| `lityahot.py` | Python 2 HTTP service (~13 KB) |
| `service_template.py` | Scorebot interaction template |

## Notes

The service stores profile banners and icons (`lityahot_banner.png`,
`lityahoticon.png`) and uses a SQLite database for user data.
