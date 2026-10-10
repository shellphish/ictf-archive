# iCTF 2008 — Bonus: Lagged Fibonacci OTP

**Edition:** iCTF 2008
**Category:** crypto
**Points:** bonus

## Description

A one-time pad (OTP) encrypted message is provided. The keystream was
generated using a **Lagged Fibonacci Generator (LFG)**, a pseudo-random
number generator with known weaknesses when the internal state can be
partially reconstructed.

Your task: recover the plaintext by cryptanalyzing the LFG keystream.

## Files

| Path | Description |
|------|-------------|
| `attachments/` | Encrypted message and any auxiliary files |
| `solution/bonus_walkthrough.txt` | Official solution |

## Background

Lagged Fibonacci Generators produce a sequence:
```
S(n) = S(n-j) ⊕ S(n-k)   (for XOR-based variant)
```
where j and k are the "lags". Given enough output bytes, the full state
can be reconstructed and the keystream predicted.

## Solution

See [`solution/bonus_walkthrough.txt`](solution/bonus_walkthrough.txt).
