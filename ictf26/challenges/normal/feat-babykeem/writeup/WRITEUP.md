# Feat. Baby Keem -- Writeup

## Overview

FileBot is an LLM-powered file browser exposed as an MCP server with a
single `chat` tool.  The LLM has internal function-calling tools
(`list_files`, `read_file`) and security rules forbidding access to any
file matching `*flag*`.

The rules are injected as the first user/assistant exchange in the
conversation history.  The system prompt (role: system) only contains
the bot identity and tool instructions -- no security rules.

## Vulnerability

The server uses a **sliding-window context strategy** (`MAX_MESSAGES = 40`).
When the conversation grows past 40 messages, the oldest complete
exchanges are evicted -- eventually including the rules exchange.

Once the rules are gone, the LLM has no instruction to refuse reading
`/app/files/flag.txt` and happily calls `read_file("/app/files/flag.txt")`.

## Solution

1. Call `chat` and ask to read `/app/files/flag.txt` -- observe refusal.
2. Send ~20 filler messages to fill the context window.
3. Ask to read `/app/files/flag.txt` again -- rules are evicted, flag is returned.

## Hint path

The challenge name "Feat. Baby Keem" references rapper Baby Keem's tweet:
> @babykeem - Feb 25, 2026
> how do u fix openclaw internal reasoning leaking

This points to LLM context/reasoning leaking issues, hinting that the
security rules can be forced out of the LLM's context window.

## Flag

```
ictf{c0nt3xt_w1nd0w_g03s_brrr_baby_keem}
```
