# Nexus

**Category:** Web | **Points:** 500

## Description

A new social network just launched. They claim their platform is hardened. Register an account and find a way to read something you shouldn't.

## Setup

```bash
docker compose up --build
```

Service available at `http://localhost:5000`.

## Challenge Structure

Flask social network backed by SQLite. Exposes user registration and login, profile pages (`/profile/<user>`), direct messaging (`/dm`), a search interface, account settings with TOTP 2FA, a reporting system, and a JSON API under `/api/`.
