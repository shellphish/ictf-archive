# PyVault

**Category:** Web | **Points:** 500

## Description

We built the most secure notes manager in Python. Our serialization is hardened, our authentication is rock solid, and our secrets are safe.

Can you prove us wrong?

## Setup

```bash
docker compose up --build
```

Service available at `http://localhost:5000`.

## Challenge Structure

Flask web application backed by SQLite with HMAC-authenticated pickle backups. Exposes user registration and login (guest/admin roles), note creation and management, backup download (`/backup/download`), backup import (`/backup/import`), and an admin panel (`/admin`).
