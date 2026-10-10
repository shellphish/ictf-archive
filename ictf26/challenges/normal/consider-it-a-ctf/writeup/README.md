# Consider it a CTF... — Writeup

**Category:** Forensics  
**Flag:** `ictf{n3xt_t1me_ple4s3_ema1l_u$}`

---

## Overview

We're given `announcement.zip`, which supposedly contains the original CTF announcement that Professor Light claims he sent weeks ago. The current file has been modified, but the challenge hints that **version control keeps careful records**.

---

## Step 1 — Extract and inspect

```bash
unzip announcement.zip -d announcement/
cd announcement/
ls -la
# .git/  ← there's a git repository!
```

---

## Step 2 — Check the git history

```bash
git log --oneline
```

You'll see multiple commits. The current state of the file has been modified — but the original content is preserved in an earlier commit.

```bash
git log --all --oneline
# e.g.:
# a3f1b2c  (HEAD) Update announcement
# 7d4e8f1  Initial announcement
```

---

## Step 3 — Recover the original content

```bash
git show 7d4e8f1
# or
git diff HEAD~1 HEAD
```

The diff reveals the deleted content, which contains the flag.

Alternatively, check out the earlier version:

```bash
git checkout 7d4e8f1 -- .
cat announcement.txt  # or whichever the main file is
```

---

## Key insight

`git log` + `git show` are enough to recover any content that was ever committed, even if it was later deleted or overwritten. Never commit sensitive data to a repository thinking that "deleting" it later makes it safe.

---

## Flag

`ictf{n3xt_t1me_ple4s3_ema1l_u$}`
