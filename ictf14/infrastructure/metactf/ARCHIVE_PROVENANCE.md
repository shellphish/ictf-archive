# iCTF 2014–2015 metactf snapshot

This directory preserves the service pool and Debian deployment tooling used
while preparing the April 2015 iCTF.

- Original repository: `git@git.seclab.cs.ucsb.edu:ictf/metactf`
- Preserved commit: `560453954cfdc2557d19618d978fcf4d5f362ff1`
- Commit date: 2015-04-13 12:36:04 -0700
- Service directories: 54, spanning iCTF 2004, 2005, 2007, 2011, 2012,
  and 2013

The `Services/` entries contain the service source, `info.json`, installation
and post-installation scripts, and gamebot scripts where available. The root
scripts build and test Debian packages. `repository/repo/` is the recovered
APT repository and contains 14 built amd64 packages; the adjacent `.gpg` file
is its expired public signing key.

This is the complete package-ready candidate pool from the repository, not a
claim that all 54 services ran in the competition. The final selection was 41
reused services, but this snapshot alone does not identify that exact subset.

The following were intentionally not copied:

- the nested `.git` directory (the source commit is recorded above);
- `Old and broken services/`, which was outside the package-ready pool;
- `ictf-2014-echo`, already preserved under `ictf14/challenges/echo/`;
- `ictf-2014-registration`, which was registration infrastructure rather than
  a reused attack-defense service;
- an untracked package-signing private key;
- untracked test state containing generated email/password pairs and other
  untracked scratch files.
