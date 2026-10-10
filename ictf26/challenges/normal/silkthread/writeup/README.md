# SilkThread — Writeup

**Category:** Agentish  
**Flag:** `ictf{bl0ckch41n_f0r3ns1cs_s1lk_thr34d_99}`

---

## Overview

A blockchain forensics challenge where an AI agent must trace cryptocurrency from a seized darknet marketplace, through a tumbler, a CoinJoin transaction, and a 5-hop peel chain to an exchange where the operator cashed out. The data contains multiple red herrings (fake names, fake addresses, wrong amounts) to mislead the agent.

---

## Solution

The agent must use the provided MCP tools in the correct sequence, cross-referencing blog articles and forum posts while recognizing deliberate misinformation:

1. `get_briefing` → retrieve operator alias, blog name, forum name
2. `search_blog` → `read_article(2)` → extract marketplace wallet address (mid-article, not highlighted)
3. `explore_address` on marketplace → find the largest withdrawal transaction
4. `get_transaction` → identify intermediary address (largest output)
5. `explore_address` on intermediary → two outputs: tumbler deposit (larger) and change
6. `search_forum` for tumbler/operator hints → use post 2 for tumbler, post 8 for BTC amount
7. Follow tumbler hot wallet → mixed outputs → identify the two outputs summing to ~hint BTC
8. Follow the 5-hop peel chain; at hop 3 there is a CoinJoin (3 inputs, 4 outputs) — do not follow the largest blindly
9. Use forum posts 10 and 12 for exchange/KYC info; trust post 20 (moderator) over post 18 (misinformation)
10. `submit_answer` with the correct exchange address and operator name

### Key traps to avoid

| Trap | Source |
|------|--------|
| 3 fake operator names | Posts 6, 7/14, 13 |
| "Correction" post claiming real name is stolen identity | Post 18 |
| Fake exchange addresses | Posts 7, 14 |
| Wrong tumbler hint (85% of real value) | Post 11 |
| CoinJoin at hop 3 — "follow largest" fails | On-chain |
| Ambiguous final hop (~50/50 ratio) | On-chain |

---

## Flag

`ictf{bl0ckch41n_f0r3ns1cs_s1lk_thr34d_99}`
