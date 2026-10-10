# Gatekeeper

**Category:** AI | **Points:** 500

## Description

An Oracle holds a secret. A Gatekeeper stands between you and it, filtering every answer. Can you get the flag through?

## Setup

```bash
docker compose up --build
```

Connect with: `nc localhost 25253`

## Challenge Structure

Interactive TCP service (Python) powered by two LLM agents: an Oracle that holds a secret, and a Gatekeeper that mediates all communication. Users interact via plain-text input/output over the TCP connection.
