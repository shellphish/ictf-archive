# iCTF Encrypted Image Passwords

All passwords were recovered from the mailing list archives at
`attic/ictf-mailing-lists-historical.tgz` (ctf-admin + ctf-participants,
2004–2017) and `attic/ctf_mailinglist.tgz` (ctf-admin pipermail, 2004–2011).

## GPG-encrypted VM images

| Edition | File | Password | Contents | Status |
|---------|------|----------|----------|--------|
| ictf04 | `ictf04/site/iCTF.tgz.gpg` | `w4f707c` | UN Vote competition VM (Fedora) | Confirmed; source already in challenges/ from tarballs |
| ictf04-05 | `ictf04-05/BassRetardCorp/images/iCTF2.tgz.gpg` | `dontbeabasstard` | Bass Tard Corp VM | Confirmed; secretd/biometric/sillyd extracted |
| ictf05 | `ictf05/site/ctf05-final.tar.gz.gpg` | `gotsp4m?` | Spam Museum VM | Confirmed; equivalent to `ctf05-final-decrypted.tar.gz` |
| ictf06 | `ictf06/site/bank2006.tar.gz.gpg` | `h1llb1lly` | Hillbilly Bank VM (Ubuntu Dapper) | Confirmed; source already extracted from VM |
| ictf07 | `ictf07/site/iCTF2007.tgz.gpg` | `dubmw4rt1` | Copyright Mafia VM (Ubuntu Server) | Confirmed |
| ictf08 | `ictf08/site/ucsb-ictf-08-final.tar.gz.gpg` | `ucsb` | FreeDOS 4.1 attack workstation (**not** OpenBSD — mailing list was a joke) | Confirmed; WOPR.C in `ictf08/infrastructure/wopr-client/` |
| ictf15 | `ictf15/site/iCTF-2015.tar.gz.gpg` | `it is not the flag that bends, it is only yourself` | Crowdsourcing Evil — likely team VMs | Confirmed working |

## GPG-encrypted service source files (ictf07)

These files were inside the competition VM at the paths shown. Passwords were
published by the organizers in the ctf-admin December 2007 mailing list under
the subject "releasing keys to source code."

| VM path | Password | Service | Status |
|---------|----------|---------|--------|
| `/home/wouldyou/wouldyou.tgz.gpg` | `Km0sVERC4U` | wouldyou | Extracted to `ictf07/challenges/wouldyou/src/` |
| `/home/petition/public_html/cgi-bin/petition.py.gpg` | `jOJiyur6ik` | petition | Extracted to `ictf07/challenges/petition/src/` |
| `/home/therapy/therapy-src.jar.gpg` | `HaURWM5844` | therapy | Extracted to `ictf07/challenges/therapy/src/` |
| `/home/snitch/source.tar.gpg` | `h19h19badabu` | snitch | Extracted to `ictf07/challenges/snitch/src/` |
| `/home/shakedown/shakedown-src.tar.gz.gpg` | `tclhe16550` | shakedown | Extracted to `ictf07/challenges/shakedown/src/` |

## 7z-encrypted archives

| Edition | File | Password | Contents | Status |
|---------|------|----------|----------|--------|
| ictf11 | `ictf11/site/iC7F-l337-vu1n.7z` | `w3_4r3_s00000000000_l337` | Money Laundering server VM (Ubuntu 10.10 LVM) | Confirmed; all 10 services extracted |

## Service-level GPG files — passwords NOT found

These files exist on the ictf05 Spam Museum VM but their decryption passwords
were never published in any recovered mailing list archive:

| VM path | Service |
|---------|---------|
| `/home/spamometer/spamometer-1.0.tar.gz.gpg` | spamometer |
| `/home/spaminout/spamback.tgz.gpg` | spamback |
| `/home/spaminout/shof-servlet-src.tar.gz.gpg` | shof-servlet |

The `spamometer` binary survives at `ictf05/challenges/spamometer/src/spamometer`
(source permanently inaccessible without the password).

## Password sources in the mailing list archives

- **ctf-participants/2004-December.txt** → ictf04 (`w4f707c`, subject: "The KEY to the image")
- **ctf-participants/2005-June.txt** → ictf04-05 (`dontbeabasstard`)
- **ctf-participants/2005-December.txt** → ictf05 (`gotsp4m?`, subject: "The password is...")
- **ctf-participants/2006-December.txt** → ictf06 (`h1llb1lly`)
- **ctf-participants/2007-December.txt** → ictf07 (`dubmw4rt1`, subject: "And the password is...")
- **ctf-admin/2007-December.txt** → ictf07 per-service keys (subject: "releasing keys to source code")
- **ctf-participants/20081205.txt** → ictf08 (`ucsb`, subject: "The key of the vmware image is")
- **ctf-admin/2011-December.txt** → ictf11 (`w3_4r3_s00000000000_l337`, sent by Giovanni Vigna at competition start)
- **ctf-admin/2015-December.txt** → ictf15 (`it is not the flag that bends, it is only yourself`)
