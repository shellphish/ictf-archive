# iCTF Archive — What's Missing

This document tracks what data, source code, metadata, and infrastructure is missing from each edition, and what would be needed to fill each gap. Last updated: 2026-10-14.

**Recent updates (2026-10-14):** Winners for ictf15, ictf16, ictf19, ictf20, ictf21, ictf23, ictf24 added from CTFtime.org. ictf18 stub created (previously missing from archive). ictf22 confirmed: no competition was held (COVID-19). Dates corrected for ictf19, ictf20, ictf21. Team counts updated for ictf07, ictf15, ictf16, ictf19, ictf20, ictf21.

Severity scale: **🔴 Critical** (fundamental gap) | **🟡 Important** (notable gap) | **🟢 Minor** (nice-to-have)

---

## What misc_stuff Contains (New Material Review)

`attic/misc_stuff/` was reviewed 2026-10 and contains the following usable material not yet integrated:

| Item | Location | Relevant To |
|------|----------|------------|
| iCTF Services Historical.xlsx | `iCTF/` | All editions — service-name tracking spreadsheet (limited text content, mainly a gsheet) |
| IRC log #ictf (Dec 6, 2013) | `iCTF/irc.irc.ictf2013.net.#ictf.weechatlog` | ictf13 — confirms service names, winner (Bushwhackers) |
| iCTF Architecture photo (Apr 2015) | `iCTF/iCTF_Architecture.jpg` | General infrastructure documentation |
| iCTF 2021 planning doc | `iCTF3/iCTF 2021.docx` | ictf21 — already copied; confirms Ethalia market mechanic |
| iCTF Redesign.docx | `iCTF3/iCTF Redesign.docx` | ictf21 — infrastructure redesign notes |
| Public.iCTF_2007 challenges index | `iCTF3/Public.iCTF_2007/` | ictf07 — nearly empty directories (just HTML shell) |
| Public.iCTF_2006 | `iCTF3/Public.iCTF_2006/` | ictf06 — logos and stats only (empty dirs) |
| iCTF2004_lotsofstuff/CTF_1/ | `iCTF2/iCTF2004_lotsofstuff/CTF_1/` | Possibly ictf01/ictf02 — ftpd and webserver sources |
| iCTF2004_Nov12 VM stub | `iCTF2/iCTF2004_Nov12/` | ictf04 — VM config only, no disk data (vmdk is a stub) |
| iCTF2.tgz (540 MB) | `iCTF2/iCTF2_clean.tgz` | ictf04-05 Bass Tard rematch — full VMware VM |
| CTF2005_spam scorebot | `iCTF2/CTF2005_spam_with_netdumps/ctf_scorebot-1.0.tar.gz` | ictf05 — another copy of scorebot (already in attic) |
| iCTF23 challenge templates | `iCTF23/challenges/sample*/` | ictf23 — challenge author templates (local/remote/web) |
| CTFd platform source | `CTFd/` | ictf23/ictf24 — CTFd version used for jeopardy editions |
| ctfsite2015 (empty dirs) | `CTF/ctfsite2015-2015/` | ictf15 — directory structure only, no actual data |
| Mailing list archive (2008–2016) | `CTF/ictf-mailing-lists-historical.tgz` | All editions 2008–2016 — partially extracted in prior sessions |
| Security/ folder | `Security/` | Unrelated to iCTF (personal security research collection) |
| DEFCON Pictures | `CTF/DEFCON/` | Not iCTF-specific |

**Summary of what misc_stuff adds:** Mainly documents already integrated (iCTF 2021 planning doc, mailing list for winners), plus unextracted VM images and a large VM file (`iCTF2_clean.tgz`) for ictf04-05 that could potentially yield source code if mounted.

---

## Winners — Current Status

Winners confirmed from site files and mailing lists:

| Edition | Year | Winner | Source | Status |
|---------|------|--------|--------|--------|
| ictf01 | 2001 | Unknown | — | 🔴 Missing |
| ictf02 | 2002 | Alpha team (one of two UCSB teams) | Site description | 🟡 Partial |
| ictf03 | 2003 | Whitehat — 11,245 pts | scorebot.state | ✅ In metadata |
| ictf04 | 2004 | Unknown (competition had performance issues) | Site note | 🟡 Partial |
| ictf04-05 | 2005 | The Tower of Hanoi (Politecnico di Milano) | Site index.html | 🟡 Not in metadata |
| ictf05 | 2005 | 0ld Eur0pe — 13,191,520 pts | final_score.html | 🟡 Not in metadata |
| ictf06 | 2006 | We_0wn_Y0u (Austria) | final_results.html | 🟡 Not in metadata |
| ictf07 | 2007 | Chocolate Makers (Milano, Italy) | Site statistics.html | 🟡 Not in metadata |
| ictf08 | 2008 | ENOFLAG (TU Berlin) | Site + mailing list | 🟡 In metadata comment, not results section |
| ictf09 | 2009 | CInsect (University of Hamburg) | Site | ✅ In metadata |
| ictf10 | 2010 | PPP (Carnegie Mellon) | Metadata | ✅ In metadata |
| ictf11 | 2011 | We_0wn_Y0u (Austria) — 1790.99 pts | Scoreboard CSV | ✅ In metadata |
| ictf12 | 2013 | PPP (Carnegie Mellon) | Mailing list | ✅ In metadata |
| ictf13 | 2013 | Bushwhackers (Russia) | IRC log + website | ✅ In metadata |
| ictf14 | 2015 | SpamAndHex (Hungary) | MySQL dump | 🟡 Not in metadata results section |
| ictf15 | 2015 | Bushwhackers (Russia) | CTFtime event 336 | ✅ In metadata |
| ictf16 | 2017 | Bushwhackers | CTFtime event 439 + metadata | ✅ In metadata + scoreboard |
| ictf17 | 2018 | (same competition as ictf16) | — | ✅ Cross-referenced |
| ictf18 | 2018 | SiBears (Russia) | CTFtime event 567 | ✅ In metadata (new stub) |
| ictf19 | 2019 | Bushwhackers | CTFtime event 762 | ✅ In metadata |
| ictf20 | 2020 | Bushwhackers | CTFtime event 1053 | ✅ In metadata |
| ictf21 | 2021 | Bushwhackers | CTFtime event 1574 | ✅ In metadata |
| ictf22 | — | (no competition) | UCSB official statement | ✅ Confirmed absent (COVID-19) |
| ictf23 | 2023 | b01lers (undergrad) + "where's my pwnthic cakes" (HS) | ictf.cs.ucsb.edu | ✅ In metadata |
| ictf24 | 2024 | Hack_of_all_trades (undergrad) + "we lost" (HS) | ictf.cs.ucsb.edu | ✅ In metadata |
| ictf26 | 2026 | Unknown | — | 🔴 Missing |

---

## Edition-by-Edition Missing Items

---

### ictf01 (2001) — Red Team/Blue Team

🔴 **Service source code** — No service names or source preserved. This was a local UCSB course exercise.  
🔴 **Winner** — Two internal UCSB teams; outcome not documented.  
🔴 **Challenges directory** — Completely empty (`challenges/` has 0 subdirectories).  
🟡 **Scoreboard/results** — No scoreboard data preserved.  
🟢 **Metadata completeness** — `metadata.yaml` exists but `results:` section is absent.

**Possible recovery:** `attic/misc_stuff/iCTF2/iCTF2004_lotsofstuff/CTF_1/` contains `ftpd/` and `webserver/` subdirectories — these may be ictf01 or ictf02 service stubs, worth investigating. No VM image known.

---

### ictf02 (2002) — Treasure Hunt in Cyberspace

🔴 **Service source code** — No standard services; scavenger-hunt format with custom challenges.  
🔴 **Winner** — Format was two UCSB teams (Alpha vs. other); outcome not in metadata.  
🔴 **Challenges directory** — Empty (`challenges/` has 0 subdirectories).  
🟡 **Metadata completeness** — `results:` section absent.  
🟢 **Scoreboard** — Internal UCSB exercise; may never have had a public scoreboard.

**Possible recovery:** `attic/misc_stuff/iCTF2/treasurehunt_plus_some_unknown_images/` may contain assets for this edition.

---

### ictf03 (2003) — Windows Goes Open-Source

🟡 **Service source code** — 6 service stubs created (`servlet`, `icecast`, `guestbook`, `ftp`, `sfind`, `query`). Source is in a VMware split VMDK (RedHat 9, ~1.9 GB). No Dockerfiles yet.  
🟡 **Dockerfiles** — None created. Source accessible via VM but not yet extracted.  
🟢 **Winner** — Documented (Whitehat, 11,245 pts) ✅  
🟢 **Scoreboard** — Partial (top 9 teams from scorebot.state) ✅  

**Possible recovery:** Mount `vms/redhat9-i386-ctf*.vmdk` with `qemu-img + debugfs` to extract service source. RedHat 9 = ext2/ext3, should be straightforward.

---

### ictf04 (2004) — The 2004 United Nations Vote

🟡 **Service source code** — 9 services have stubs. Most source is accessible via the site VMs. Dockerfiles: only 1 of 9.  
🔴 **Winner** — Competition had "serious performance problems" and a rematch was held. No declared winner for ictf04 itself.  
🟡 **Scoreboard** — No final scoreboard preserved (competition ended without clear winner).  
🟢 **Metadata completeness** — `results:` section absent; should note "no winner declared — see ictf04-05".

**Possible recovery:** VMs in `vms/` contain service source. The `iCTF2004_Nov12/` in misc_stuff has a broken vmdk stub (no actual disk data — the vmdk file is just 351 bytes).

---

### ictf04-05 (2005) — The Bass Tard Corporation

🟡 **Service source code** — 10 services; 7 with Dockerfiles, 3 stub-only. Source partially extracted from VMs.  
🔴 **Winner not in metadata** — Winner is "The Tower of Hanoi" (Politecnico di Milano) — confirmed from `ictf04-05/site/index.html` but `results:` section missing from `metadata.yaml`.  
🟡 **Full scoreboard** — Not preserved (only winner confirmed).  
🟢 **VM source** — `attic/misc_stuff/iCTF2/iCTF2_clean.tgz` (540 MB, June 2005) is the full Bass Tard rematch VM — mounting this could yield remaining service source.

**Action needed:** Add `results:` section to `metadata.yaml` with winner. Consider mounting `iCTF2_clean.tgz` to extract remaining service source.

---

### ictf05 (2005) — The Spam Museum

🟡 **Service source code** — 11 services; 2 with Dockerfiles, rest are partial stubs. Source in `vms/` and partially in scorebot scripts.  
🔴 **Winner not in metadata** — Winner is "0ld Eur0pe" (13,191,520 pts) — confirmed from `ictf05/site/final_score.html` (dated Dec 9, 2005) but `results:` section absent.  
🟡 **Full scoreboard** — Preserved in `site/final_score.html` (top ~20 teams visible).  
🟢 **Encrypted VM** — `ctf05-final.tar.gz.gpg` is GPG-encrypted; key unknown.

**Action needed:** Add `results:` section to `metadata.yaml`. Dockerfiles needed for 9 remaining services.

---

### ictf06 (2006) — The Hillbilly Bank

🟡 **Service completeness** — 7 challenge directories created (atm, bpt-proto, bts-travel, etj-transactions, hillbilly-bank, mom-bank, sts-stock); 6 of 7 have Dockerfiles ✅. Service `bpt-proto` lacks a Dockerfile.  
🔴 **Winner not in metadata** — Winner is "We_0wn_Y0u" (Austria, 14,963,559 pts) from `ictf06/site/final_results.html`. `results:` section absent from `metadata.yaml`.  
🟡 **Scoreboard** — Preserved in `site/final_results.html` but not transcribed to metadata.  
🟡 **Service names confirmed?** — The 7 dirs seem right, but total service count vs. actual competition services not verified.  
🟢 **Num teams** — 25 teams mentioned in website text.

**Action needed:** Add `results:` section with winner and scoreboard data to `metadata.yaml`. Add Dockerfile for `bpt-proto`. Set `num_teams: 25`.

---

### ictf07 (2007) — The Copyright Mafia

🟡 **Service source code** — 8 services with source extracted; 5 of 8 have Dockerfiles. `amends`, `petition`, `therapy`, `wouldyou` still lack Dockerfiles.  
🔴 **Winner not in metadata** — Winner is "Chocolate Makers" (Milano, Italy) from `ictf07/site/statistics.html`. `results:` section absent.  
🟡 **Scoreboard** — Statistics page exists in site but not transcribed to metadata.  
🟢 **Network traffic** — `Public.iCTF_2007/iCTF2007_traces/` in misc_stuff is an empty directory; traces may be in `vms/` or `dumps/` (most likely gitignored).

**Action needed:** Add `results:` section to `metadata.yaml`. Create Dockerfiles for 4 remaining services.

---

### ictf08 (2008) — "24" / The Softerror.com Network

🟡 **Service completeness** — 11 services; 4 have Dockerfiles; 7 services still lack Dockerfiles (mainwebsite, develsite, financialsite, bombsite components).  
🟡 **Winner in metadata** — ENOFLAG confirmed in metadata comment, but `results:` section is absent (no formal `results:` block).  
🟢 **Scoreboard** — Not preserved in metadata. Competition was ATTACK format (40 isolated replicas), not attack-defense; winner was first to disarm the bomb.

**Action needed:** Add formal `results:` section to `metadata.yaml`. Create remaining Dockerfiles.

---

### ictf09 (2009) — Know Your Enemy: Rise of the Botnet

🔴 **Service source code** — 4 known services (erlang-browser, robabank, madoffunds, vulnerable-service) have stubs but NO source code and NO Dockerfiles. The services were browser-exploit-based (drive-by download attacks); source may never have been public.  
🔴 **Service count** — Only 4 services documented; actual competition may have had more.  
🟢 **Winner** — CInsect (University of Hamburg) ✅  
🟢 **Scoreboard** — PDF preserved in `data/scores/scores.pdf` ✅  

**Action needed:** Verify total service count. Source extraction would require mounting the VM (in `vms/`).

---

### ictf10 (2010) — Hit 'em Where it Hurts

🟡 **Service completeness** — 15 services; 13 with Dockerfiles. `icmbd` (missile launcher USB control, port 8080) and `flagsubmission` still lack Dockerfiles/full extraction.  
🟡 **Winner in metadata** — PPP confirmed but in a comment, not a formal `results:` section.  
🟡 **Scoreboard** — A `results.csv` snapshot was requested via mailing list but not confirmed received. No scoreboard file in the local archive.  
🟢 **All 15 service sources** — Available (extracted from VMs using qemu-img + debugfs).

**Action needed:** Add formal `results:` section. Create Dockerfiles for `icmbd` and `flagsubmission`. Locate final scoreboard.

---

### ictf11 (2011) — Do You Feel Lucky? (Money Laundering)

🔴 **Service source code** — 10 service stubs exist but the service VM (`iC7F-l337-vu1n.7z`, 772 MB) is AES-encrypted. Password unknown. Source completely inaccessible.  
🟢 **Winner** — We_0wn_Y0u (Austria), 1790.99 pts ✅  
🟢 **Scoreboard** — Full 85-team CSV in `data/scoreboard.csv` ✅  
🔴 **Dockerfiles** — Zero (source encrypted, cannot create containers).

**Recovery:** Only possible if the AES password is found. Check old emails/notes for the 7z password.

---

### ictf12 (2013) — SCADA Breakdown

🔴 **Service names** — No service names preserved in local archive.  
🔴 **Service source code** — Zero services in challenges directory.  
🟢 **Winner** — PPP (Carnegie Mellon) ✅  
🟡 **Scoreboard** — Score data preserved in `data/scores/` directory but not summarized in metadata.  
🟡 **Network traffic** — Traffic logs in `data/traffic/` are gitignored (too large).  
🟢 **Num teams** — Not documented.

**Action needed:** Transcribe top scoreboard from `data/scores/` to metadata. Document service names if findable in old emails or the website. Num teams from `data/scores/`.

---

### ictf13 (2013) — Nuke 'em (or Duck and Cover!)

🟡 **Service source** — 10 service stubs. Binaries (.deb packages) preserved in `data/ictf/` but no source code. Binaries are 32-bit i386 ELF (no ASLR).  
🟢 **Winner** — Bushwhackers (Russia), $1,024 Lastline prize ✅  
🟡 **Dockerfiles** — None. Would need to reverse-engineer from the .deb binaries or find source.  
🟡 **Scoreboard** — Not documented in metadata (IRC log confirms Bushwhackers won but no final ranking table).  
🟢 **Num teams** — "100+ teams, 1,200+ students" (from competition materials).

**Possible recovery:** Decompile the .deb binaries. The IRC log also confirms the L4 service was `uranus` (all four L4 services were active per topic messages).

---

### ictf14 (2015) — Large-scale Hacking

🔴 **Service names and source** — No services in challenges directory; specific service names not in archive.  
🟡 **Winner not in metadata results** — SpamAndHex (Hungary, score 92.744) confirmed from MySQL dump but `results:` section absent from `metadata.yaml`.  
🟡 **Scoreboard** — Scoreboard screenshots in `iCTF scoreboard/` but not transcribed. Full scoreboard from MySQL dump could be extracted.  
🟡 **Registration data** — 88-team registration SQL now in `data/ictf_registration_apr_2015-final-final.sql` ✅  
🟢 **Num teams** — 88 (confirmed).

**Action needed:** Add `results:` section. Extract and document full scoreboard from MySQL dump. Identify service names from mailing list or website.

---

### ictf15 (2015) — Crowdsourcing Evil

🔴 **Service source code** — 43 services documented (with port numbers) but zero have source code or Dockerfiles. The `database/last_db.sql.xz` contains April 2015 (ictf14) data, not ictf15 game data.  
🟢 **Winner** — Bushwhackers (Russia), confirmed from CTFtime event 336. Denis Gamayunov (co-founder) was the "Dennis" emailed by Giovanni Vigna. ✅  
🟡 **Final scoreboard** — Not preserved locally. External URL: `http://scoreboard.ictf2015.net/results/index.html` (may be dead). Try Wayback Machine.  
🟢 **Team count** — 35 teams (CTFtime event 336) ✅  
🟢 **Organizer materials** — Working notes, service vote, team location data preserved ✅.

**Action needed:** Recover the final scoreboard (Wayback Machine). Create at least stub challenge dirs for the named services. Source recovery would require mounting `base-vms/base-vms.tar.gz`.

---

### ictf16 (2017) — Shell We Play a Game? / Unicorns, Ponies, and Rainbows vs. AI

🔴 **Service names and source** — Only `flasking_unicorns` confirmed. 11 other services (ports 20001–20012) completely unknown.  
🟢 **Winner** — Bushwhackers (2,849,008 pts), full top-10 scoreboard from CTFtime event 439 ✅  
🔴 **Challenges directory** — Empty (0 challenge subdirectories).  
🟡 **Scoreboard** — Full CTFtime top-10 added to metadata. Local scoreboard not preserved.  
🟢 **Team count** — 314 teams (CTFtime event 439) ✅  
🟢 **Planning documents** — Announcement and planning docs preserved ✅.

**Action needed:** Create `challenges/` stubs for all 12 services once names are found. Check DDoS analysis doc and traffic dumps for remaining service names.

---

### ictf17 (2018) — (Unicorns, Ponies, and Rainbows vs. AI — same competition as ictf16)

🔴 **Service names and source** — Same gap as ictf16 (same competition). The ictf17 directory is auxiliary to ictf16.  
🔴 **Winner** — This is the same competition as ictf16; Bushwhackers won. Should be cross-referenced, not duplicated.  
🟡 **Directory purpose** — ictf17 holds supplemental documents (anti-cheating system, descriptions) that belong to the same 2016-2017 competition.

**Action needed:** Clarify in README whether ictf17 is truly a separate edition or should be merged into ictf16.

---

### ictf18 (2018) — Unknown Theme

🔴 **Game theme** — Not documented in official UCSB archive, website, or any preserved materials. The competition domain `ictf2018.net` is no longer active.  
🔴 **Service names and source** — No services in the local archive. No GitHub repos found under shellphish for ictf18.  
🔴 **Local archive** — The `ictf18/` directory was not in the original local archive at all; stub created 2026-10 from CTFtime data only.  
🟢 **Winner** — SiBears (Russia, 112,162 pts). Full top-10 scoreboard from CTFtime event 567 ✅  
🟢 **Team count** — 265 teams (CTFtime event 567) ✅  
🟡 **Infrastructure** — Co-organized by UCSB Shellphish + ASU pwndevils (Adam Doupé). Container-based, AWS-hosted.

**Possible recovery:** The mailing list archive (`ictf-mailing-lists-historical.tgz`) covers through 2016 and won't help here. Try reaching out to ASU SEFCOM / Adam Doupé, or searching Wayback Machine for ictf2018.net to recover theme/services.

---

### ictf19 (2019) — The Grey Hat Nation

🔴 **Service names and source** — No services documented or preserved. The "CTF Service Specification.docx" is a template, not a service list.  
🟢 **Winner** — Bushwhackers (98.670 CTFtime rating pts), March 15-16 2019. CTFtime event 762 ✅  
🟡 **Full scoreboard** — Only winner confirmed from CTFtime. Local score data in `data/scores/` not yet extracted.  
🔴 **Challenges directory** — Empty.  
🟡 **Score data** — `data/scores/` directory exists (not empty) but content not documented in metadata.  
🟡 **Team data** — `data/teams/` directory exists.  
🟢 **Team count** — 398 teams (CTFtime event 762) ✅

**Action needed:** Read `data/scores/` to extract full scoreboard. Identify service names (check GitHub: `shellphish/ictf19-*` repos may exist).

---

### ictf20 (2020) — Abbey Road (1 After 909)

🟡 **Service source** — 7 services cloned from `shellphish/ictf-2020-challs-public`. Source present in `src/` ✅. However, challenge directories (`challenges/`) have stub dirs without challenge.yml files from the actual game.  
🟢 **Winner** — Bushwhackers (505,740.85 pts), March 6-7 2020. Full top-10 from CTFtime event 1053 ✅  
🟡 **Scoreboard** — Top-10 in metadata from CTFtime (scores approximate). Full local scoreboard not preserved.  
🟢 **Team count** — 88 teams (CTFtime event 1053) ✅  
🟡 **Dockerfiles** — Source available but Dockerfiles in `challenges/` subdirs not created (source is in `src/<name>/service/`).

**Action needed:** Wire up `challenges/` dirs to point to source in `src/`. Dockerfiles can be created from `src/<name>/service/docker-compose.yml`.

---

### ictf21 (2021) — The Ethalia Market

🔴 **Service source** — Zero services in challenges directory. Source is at `shellphish/ictf21-challenges` (private GitHub repo — access needed).  
🟢 **Winner** — Bushwhackers (355,942.91 pts), Dec 3-4 2021. Full top-10 from CTFtime event 1574 ✅  
🟡 **Scoreboard** — Top-10 in metadata from CTFtime (scores approximate). Full local scoreboard not preserved.  
🟢 **Team count** — 88 teams (CTFtime event 1574) ✅  
🟡 **Score data** — `data/scores/scoreboard/` contains per-country flags (PNG files) suggesting a map-based scoreboard was used.  
🟢 **Planning doc** — `iCTF 2021.docx` preserved and game mechanics documented ✅.

**Action needed:** Request access to `shellphish/ictf21-challenges` to populate `challenges/`. Interpret `data/scores/scoreboard/` contents for full scoreboard.

---

### ictf23 (2023) — AI and Cybersecurity

🟡 **Challenge completeness** — 2 tracks (undergrad, high-school). Individual challenge dirs exist but are sparse — most lack source code or only have stub files. Only 2 challenge subdirs have Dockerfiles.  
🟢 **Winner** — Undergrad: b01lers (Purdue University). High School: "where's my pwnthic cakes" (Çorlu Arif Nihat Asya Anadolu Lisesi, Turkey). Confirmed from ictf.cs.ucsb.edu ✅  
🟡 **Scoreboard PDFs** — Preserved in `CTFd_Archive/` (PDF exports) but not transcribed to metadata.  
🟡 **CTFd export** — `CTFd_Archive/` preserved ✅ — full challenge/submission data available.  
🟡 **Num teams** — Not yet extracted from CTFd export.

**Action needed:** Count teams from CTFd export. Transcribe final scores from PDF to metadata. Populate challenge source from local CTFd export.

---

### ictf24 (2024) — iCTF 2024

🟡 **Challenge completeness** — 3 tracks (undergrad, high-school, training). Only 3 top-level track dirs, not individual challenge dirs per service.  
🟢 **Winner** — Undergrad: Hack_of_all_trades (UC Santa Barbara). High School: "we lost" (Dos Pueblos High School, Goleta, CA — $3,000 prize). Confirmed from ictf.cs.ucsb.edu ✅  
🟡 **Scoreboard** — Not transcribed to metadata. CTFd export available.  
🟡 **Num teams** — Not yet extracted from CTFd export.

**Action needed:** Count teams from CTFd export. Transcribe final scoreboard to metadata. Populate individual challenge dirs.

---

### ictf26 (2026) — AI Agents and Cybersecurity (Agentish)

🟡 **Challenge source** — References `shellphish/ictf-challenges-2026` but source not cloned locally.  
🔴 **Winner** — Not documented (competition may be recent/ongoing).  
🟡 **Challenge count** — 17 agentish + 25 normal = 42 total, but no individual challenge dirs.

**Action needed:** Clone `shellphish/ictf-challenges-2026`. Populate challenges. Document results once competition concludes.

---

## Priority Action List

### High Priority (fills critical data gaps)

1. **Add `results:` sections** to metadata for ictf04-05, ictf05, ictf06, ictf07, ictf08 — all have confirmed winners from site files or mailing lists. _(ictf10, ictf14, ictf15–ictf21, ictf23, ictf24 now done ✅)_
2. **Create Dockerfiles** for ictf05 (9 services), ictf07 (4 services), ictf08 (7 services), ictf03 (6 services).
3. **Wire up ictf20 challenges/** — source is in `src/`, needs challenge.yml linking. Dockerfiles can be derived from existing docker-compose.yml files.
4. **Extract ictf19 full scoreboard** from `data/scores/` directory (winner known; need complete ranking).
5. **Extract ictf12 scoreboard** from `data/scores/` directory.
6. **Identify ictf16/17 service names** — check `captures.tar.xz` or `traffic.tpxz` for service identifiers beyond `flasking_unicorns`.

### Medium Priority (improves coverage)

7. **Mount ictf04-05 VM** (`attic/misc_stuff/iCTF2/iCTF2_clean.tgz`, 540 MB) to extract remaining service source.
8. **Mount ictf03 VMDKs** to extract service source for 6 services.
9. **Clone ictf20 source into challenges/** — source is in `src/`, needs `challenges/<name>/` dirs with `challenge.yml`.
10. **Extract ictf21 scoreboard** from `data/scores/scoreboard/` PNG files or related data.
11. **Investigate ictf02 misc_stuff** — `treasurehunt_plus_some_unknown_images/` may contain useful content.
12. **Investigate CTF_1/** in `misc_stuff/iCTF2/iCTF2004_lotsofstuff/` — `ftpd/` and `webserver/` subdirs may be early service source.

### Low Priority (completeness/polish)

13. **ictf11 VM password** — The 7z password for `iC7F-l337-vu1n.7z` would unlock all 10 service sources.
14. **ictf15 final scoreboard** — Try Wayback Machine for `http://scoreboard.ictf2015.net/results/index.html`.
15. **ictf23/ictf24 num_teams** — extract from CTFd export archives.
16. **ictf13 scoreboard** — extract from IRC log or site (competition score data should be in `data/`).
17. **ictf26 challenge source** — clone `shellphish/ictf-challenges-2026`.

---

## Known Unrecoverable Data

| Edition | What's Missing | Why Unrecoverable |
|---------|---------------|-------------------|
| ictf01 | Service source, scoreboard | Local UCSB exercise, no VMs preserved |
| ictf11 | Service source | 7z AES-encrypted, password unknown |
| ictf05 | `ctf05-final.tar.gz.gpg` | GPG-encrypted, key unknown |
| ictf16/17 | 11 of 12 service names/sources | No VM images; only traffic captures (gitignored) could yield names |
| ictf19 | Service source | No VM images in local archive |
| ictf04 | Final scoreboard | Competition abandoned mid-game due to technical failures |
