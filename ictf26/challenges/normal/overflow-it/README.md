# overflow-it

**Category:** AI | **Points:** 500

## Description

A server translates English words to Italian using a secret mapping. Send words, learn translations. If your message makes sense in both languages and says the right thing, the AI agent might just reveal its secret.

## Setup

```bash
docker compose up --build
```

Connect with: `nc <host> <port>`

## Challenge Structure

Interactive TCP service (Python) with spaCy NLP and an LLM backend (LiteLLM/OpenAI). Users submit English words and receive Italian translations via a secret word-to-word mapping. The server validates grammar with spaCy and uses an LLM agent to verify the semantic content of submitted sentences.
