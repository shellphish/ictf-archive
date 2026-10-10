# SilkThread

An agentic CTF challenge where an AI agent must conduct a blockchain forensics investigation to trace cryptocurrency from a seized darknet marketplace and identify the operator's real identity.

Every session generates unique addresses, transaction hashes, amounts, and names while maintaining the same investigation structure.

## Objective

Identify the **final cash-out wallet address** and the **operator's real name**, then submit both via `submit_answer` to receive the flag.

## Investigation Sources

| Source | Description |
|--------|-------------|
| **Blog** | Investigative journalist articles — starting lead, marketplace wallet, and laundering analysis |
| **Forum** | Darknet community posts — tumbler details, operator OPSEC leaks, exchange KYC data |
| **Blockchain** | Transaction explorer — follow the money through addresses and transactions |

## Money Trail

```
Marketplace Wallet (from blog)
  └─► Intermediary Address (large withdrawal)
        └─► Tumbler Deposit (identified via forum)
              └─► Tumbler Hot Wallet (pools all users)
                    └─► Mixed Outputs (2 belong to operator — forum hint: sum ≈ X BTC)
                          └─► Consolidation Wallet (2 outputs merged)
                                └─► Peel Chain (3 hops — follow the larger output)
                                      └─► Exchange Deposit (cash-out — KYC links to real name)
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_briefing` | Initial case briefing with starting leads |
| `search_blog` | Search journalist articles by keyword |
| `read_article` | Read a specific article by ID |
| `search_forum` | Search darknet forum by keyword |
| `read_post` | Read a specific post by ID |
| `explore_address` | Get all transactions for a Bitcoin address |
| `get_transaction` | Get full details of a transaction by hash |
| `submit_answer` | Submit wallet + name (max 5 attempts) |

## Agent Strategy

1. **Get briefing** → learn the operator alias and which blog/forum to check.
2. **Search & read blog articles** → find the marketplace wallet address and withdrawal txid.
3. **Explore the marketplace wallet** → identify the large withdrawal transaction.
4. **Follow the withdrawal** → get_transaction to see the intermediary address.
5. **Explore intermediary** → find the outgoing tx to the tumbler.
6. **Search forum** for tumbler info → learn which tumbler was used and the deposit address.
7. **Explore tumbler deposit** → trace to the hot wallet.
8. **Explore tumbler hot wallet** → see all mixed outputs.
9. **Read forum posts** about the tumbler outputs → get the hint about the sum of the operator's 2 outputs.
10. **Identify the 2 outputs** that sum to ~hint BTC → explore them.
11. **Follow consolidation** → peel chain → always follow the larger output.
12. **Reach the exchange deposit** → note the address.
13. **Search forum** for exchange/KYC info → learn the real name.
14. **Submit** wallet_address + owner_name.

## Setup

```bash
cp env.example .env
docker compose up --build
```
