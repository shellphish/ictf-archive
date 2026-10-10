# KITTENS PARADISE

**Category:** Web | **Points:** 500

## Description

A cozy web portal for cat lovers. It's probably secure — they ran an audit and everything checked out. Or did it?

## Setup

```bash
docker compose up --build
```

Service available at `http://localhost:3000`.

## Challenge Structure

Node.js HTTP server (no framework). Provides a cat-themed portal with a public guestbook, user preferences, JWT-based authentication, and dynamically generated SVG cat avatars. Exposes a REST API at `/api/preferences` (PATCH) alongside standard page routes.
