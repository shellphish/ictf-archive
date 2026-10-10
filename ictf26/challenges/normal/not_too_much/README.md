# bof_64

**Category:** PWN | **Points:** 500

## Description

A 64-bit binary with a classic memory corruption vulnerability. Can you gain unauthorized access?

## Setup

```bash
docker compose up --build
```

Connect with: `nc localhost 4444`

## Challenge Structure

64-bit compiled C binary served over TCP. The program accepts user input and performs a login check using an in-memory struct that contains a username buffer alongside admin flag fields.
