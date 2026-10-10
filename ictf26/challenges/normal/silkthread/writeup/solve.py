#!/usr/bin/env python3
"""
SilkThread — Reference Solver (Agentish challenge)
This challenge requires an AI agent with access to MCP blockchain forensics tools.
This script is a step-by-step reference for the correct solution path.

Usage:
    MCP_URL=http://localhost:<port>/sse \
    LITELLM_BASE_URL=http://litellm:4000 \
    TEAM_LITELLM_API_KEY=<key> \
    python3 writeup/solve.py

The agent must follow money from a seized darknet marketplace through a tumbler,
CoinJoin, and a 5-hop peel chain to find the operator's exchange address.
"""

import asyncio
import json
import os

import anthropic
from mcp import ClientSession
from mcp.client.sse import sse_client


MCP_URL = os.environ.get("MCP_URL", "http://localhost:8765/sse")
MODEL = os.environ.get("LITELLM_MODEL", "claude-haiku-4-5")

SYSTEM_PROMPT = """
You are a blockchain forensics investigator. You must trace cryptocurrency
from a seized darknet marketplace to the operator's exchange cash-out address.

Key rules for avoiding red herrings:
1. Trust the moderator (post 20) over anonymous corrections (post 18).
2. At the tumbler, find the TWO outputs summing closest to the BTC hint (not just the largest).
3. At a CoinJoin (3 inputs / 4 outputs), do NOT blindly follow the largest output.
4. At the final hop, use forum corroboration to resolve ambiguity.
5. Ignore fake exchange addresses that don't appear on-chain.

Steps:
1. get_briefing → learn operator alias, blog name, forum name
2. search_blog + read_article(2) → get marketplace wallet address
3. explore_address(marketplace) → find largest withdrawal
4. get_transaction(withdrawal) → find intermediary (largest output)
5. explore_address(intermediary) → find tumbler deposit (larger of two outputs)
6. search_forum for tumbler and BTC amount hint
7. Follow tumbler hot wallet → identify two mixed outputs summing ~hint
8. Follow peel chain 5 hops (handle CoinJoin at hop 3)
9. search_forum for exchange/KYC info (trust post 20 for credibility)
10. submit_answer with exchange address and operator real name
""".strip()

HUMAN_PROMPT = "Start the investigation. Follow the money."


async def main():
    base_url = os.environ.get("LITELLM_BASE_URL")
    api_key = os.environ.get("TEAM_LITELLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    llm = anthropic.Anthropic(**client_kwargs)

    async with sse_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tools = [
                {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
                for t in tools_result.tools
            ]

            messages = [{"role": "user", "content": HUMAN_PROMPT}]
            print(f"[solve] Connected to MCP at {MCP_URL}")
            print(f"[solve] Tools: {[t['name'] for t in tools]}")

            while True:
                response = llm.messages.create(
                    model=MODEL,
                    max_tokens=8192,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    messages=messages,
                )

                assistant_content = []
                tool_calls = []
                for block in response.content:
                    assistant_content.append(block)
                    if block.type == "text":
                        print(f"[agent] {block.text}")
                    elif block.type == "tool_use":
                        tool_calls.append(block)
                        print(f"[tool→] {block.name}({json.dumps(block.input)[:120]})")

                messages.append({"role": "assistant", "content": assistant_content})

                if response.stop_reason == "end_turn" or not tool_calls:
                    break

                tool_results = []
                for call in tool_calls:
                    result = await session.call_tool(call.name, call.input)
                    text = result.content[0].text if result.content else ""
                    print(f"[←tool] {call.name}: {text[:200]}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": text,
                    })
                messages.append({"role": "user", "content": tool_results})

            print("\n[solve] Done.")


if __name__ == "__main__":
    asyncio.run(main())
