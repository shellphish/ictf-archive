# Try More

**Category:** PWN | **Points:** 500

## Description

A binary reads your name and greets you. Simple enough. Can you make it do something more interesting?

## Setup

```bash
docker compose up --build
```

Connect with: `nc localhost 4445`

## Challenge Structure

32-bit compiled C binary (PIE enabled) served over TCP. The program reads user input into a fixed-size buffer and prints a greeting. The binary also contains a `win()` function that launches an interactive shell.
