# SilkThread

**Category:** Agentish | **Points:** 500

## Description

Operation SilkThread. A darknet marketplace has been seized but the operator vanished with the funds. Trace the money. Cross-reference your sources. Not everything you read is true.

## Setup

```bash
cp env.example .env  # configure LiteLLM credentials
docker compose up --build
```

MCP endpoint available at `http://localhost:8000`.

## Challenge Structure

HTTP MCP server providing blockchain forensics tools to an LLM agent. The server exposes tools to query cryptocurrency transactions, forum posts, and blog articles — some sources contain deliberate misinformation. The agent has a single submission attempt to identify the correct wallet address.
