# Feat. Baby Keem

**Category:** LLM | **Points:** 500

## Description

FileBot is an LLM-powered file browser. It has access to your files and a set of security rules. Can you convince it to share what it shouldn't?

## Setup

```bash
docker compose up --build
```

Connect with: `nc localhost 31337`

## Challenge Structure

TCP server (Python) that bridges user input to an MCP server running an LLM-powered file browser called FileBot. Each connection gets an isolated session. Users interact with FileBot via a conversational text interface over the TCP connection; FileBot can invoke MCP tools to access files and apply its configured rules.
