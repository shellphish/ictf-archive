# Feat. Baby Keem — REMIX

**Category:** LLM | **Points:** 500

## Description

FileBot is back with a new defense. The rules are now actively monitored and restored if they disappear. Can you still find a way to read the flag?

## Setup

```bash
docker compose up --build
```

Connect with: `nc localhost 31338`

## Challenge Structure

Same architecture as Feat. Baby Keem — a TCP-to-MCP bridge exposing an LLM-powered file browser. This version adds active monitoring that detects and restores the server's rule configuration if it is modified or removed.
