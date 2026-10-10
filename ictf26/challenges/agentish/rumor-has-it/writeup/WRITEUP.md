# Writeup: Rumor Has It

### Goal

Recover the **ordered list of sources** in the gossip chain and identify the **true IoC**.

### Interface (MCP)

The challenge exposes a single MCP server (`mcp_gossip`) with three tools:

- `gossip()` → returns the first message and the `gossip_id`
- `rumor(gossip_id, source)` → returns that source’s message
- `opinion(sources, ioc)` → returns the flag if both the chain and IoC are correct

### Intended solve

- Call `gossip()` to get the first source and a “next source” hint.
- Follow the chain by repeatedly calling `rumor(gossip_id, next_source)` until there is no next source.
- Each message includes exactly 3 IoCs. The **true IoC appears in every message**, while red herrings vary.
  - Intersect the sets of IoCs across all messages to find the unique common IoC.
- Submit `opinion(sources=<ordered chain>, ioc=<common IoC>)`.

