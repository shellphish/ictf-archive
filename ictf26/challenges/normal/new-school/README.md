# New School

**Category:** Crypto | **Points:** 500

## Description

It's your first day at a new school. You need to register at the main office. I've heard they have a really advanced method of assigning IDs...

## Setup

```bash
docker compose up --build
```

Connect with: `nc localhost 28443`

## Challenge Structure

Interactive TCP service (Python). Simulates a school registration system — users provide personal details (name, grade, date of birth) and receive a generated student ID. After registration, users can navigate classrooms to look up students by their ID.
