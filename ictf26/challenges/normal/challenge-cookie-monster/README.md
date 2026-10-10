# Cookie Monster

**Category:** Web | **Points:** 500

## Description

A login portal hands out signed session cookies. Log in as a guest — the admin panel is just one forged cookie away. Can you satisfy the Cookie Monster?

## Setup

```bash
docker compose up --build
```

Service available at `http://localhost:8000`.

## Challenge Structure

Flask web application with session-based authentication. Exposes endpoints for guest registration (`/register`), login (`/login`), a user dashboard (`/dashboard`), and an admin panel (`/admin`). Sessions are managed via signed cookies.
