# AgentZero

**Category:** Web | **Points:** 500

## Description

Meet **AgentZero** — a next-gen AI assistant with access to powerful administrative vault tools. Rumour has it there's a classified vault containing something very sensitive...

## Setup

```bash
docker compose up --build
```

Service available at `http://localhost:3001`.

## Challenge Structure

Full-stack web application with an Express.js backend and a Next.js frontend. An LLM-powered agent (Claude API) is equipped with MCP tools that interact with an administrative vault. Users can register, log in, and chat with the agent through a web interface. Exposed endpoints include `/api/chat`, `/api/auth`, `/api/preferences`, and `/api/tools`.
