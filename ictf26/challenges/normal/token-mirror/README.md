# Token Mirror

**Category:** ML | **Points:** 500

## Description

Tokenizers don't care about your reading direction. Find a string that looks completely different forwards and backwards, yet the tokenizer counts them the same.

## Setup

```bash
docker compose up --build
```

Connect with: `nc localhost 1337`

## Challenge Structure

Interactive TCP service (Python) using the tiktoken tokenizer (OpenAI). Accepts a string and validates it against five constraints: alphanumeric characters and spaces only, length greater than 20, character-to-token ratio above 5, equal token count when reversed, and different token IDs when reversed.
