# iCTF 2008 — Forensics 200: Stereogram

**Edition:** iCTF 2008
**Category:** forensics / steganography
**Points:** 200
**Difficulty:** medium

## Description

A stereogram image is provided. Hidden within it is a message encoded using
**OutGuess**, a steganographic tool that embeds data in JPEG images while
preserving statistical properties.

Your task: extract the hidden data from the stereogram.

## Files

| Path | Description |
|------|-------------|
| `attachments/` | The stereogram image distributed to participants |
| `solution/f200_walkthrough.txt` | Official solution |

## Quick Solve

```bash
# Install outguess
apt-get install outguess

# Extract hidden data
outguess -r attachments/<image>.jpg solution.txt
cat solution.txt
```

## Solution

See [`solution/f200_walkthrough.txt`](solution/f200_walkthrough.txt).
