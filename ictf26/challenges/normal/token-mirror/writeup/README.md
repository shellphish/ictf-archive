# Token Mirror — Writeup

**Category:** ML  
**Flag:** `ictf{t0k3n_m1rr0r_r3fl3ct5_th3_s4m3}`

---

## Overview

The challenge asks you to find a string where the forward and reversed versions tokenize to the same count of tokens but with completely different token IDs. The key insight is using palindromic word pairs — pairs where `word_a` reversed equals `word_b`.

---

## Solution

### Key Insight

The `o200k_base` tokenizer merges common English words into single tokens. When you reverse the entire string character-by-character, the tokenizer re-splits it differently — usually into far more tokens because reversed English is gibberish.

The trick is to use **palindromic word pairs**: two words where `word1 + " " + word2` reads the same forwards and backwards (e.g., `"reward drawer"`, `"star rats"`, `"evil live"`). Each such pair is a character-level palindrome, so reversing the whole string just **reorders the pairs** without breaking them.

For example:
- `"reward drawer star rats evil live"` (6 tokens)
- Reversed: `"evil live star rats reward drawer"` (6 tokens)

Both have 6 tokens, but the token IDs are completely different because each word maps to a different token ID, and the ordering changes.

## Constructing a Solution

1. Find word pairs where `word_a` reversed equals `word_b`:
   - `reward` / `drawer`
   - `star` / `rats`
   - `evil` / `live`
   - `deliver` / `reviled`
   - `stressed` / `desserts`
   - `smart` / `trams`
   - `diaper` / `repaid`

2. Concatenate multiple pairs: `"reward drawer star rats evil live"`

3. The full reversal swaps pair order: `"evil live star rats reward drawer"`

4. Both tokenize to the same number of tokens but with different IDs.

## Example Solution

```
reward drawer star rats evil live
```

- 33 characters, 6 tokens, ratio = 5.50
- Forward tokens:  `[95118, 43738, 8253, 52238, 24604, 4561]`
- Reversed tokens: `[158278, 4561, 8253, 52238, 16563, 43738]`

## Flag

`ictf{t0k3n_m1rr0r_r3fl3ct5_th3_s4m3}`
