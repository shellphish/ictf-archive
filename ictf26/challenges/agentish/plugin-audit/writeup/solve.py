#!/usr/bin/env python3
"""
Reference solver for Plugin Audit.

Single ReAct agent (claude-haiku-4-5) connected to the MCP server via SSE.
Diffs the plugin, exploits the SQL injection, and prints the captured flag.

Usage:
    MCP_URL=http://localhost:8765/sse \
    LITELLM_BASE_URL=http://184.32.253.37:4000 \
    TEAM_LITELLM_API_KEY=<key> \
    python3 writeup/solve.py
"""

import asyncio
import json
import os
import sys

import anthropic
from mcp import ClientSession
from mcp.client.sse import sse_client

MCP_URL = os.environ.get("MCP_URL", "http://localhost:8765/sse")
MODEL = os.environ.get("LITELLM_MODEL", "claude-haiku-4-5")

SYSTEM_PROMPT = open(os.path.join(os.path.dirname(__file__), "system_prompt.txt")).read()
HUMAN_PROMPT = open(os.path.join(os.path.dirname(__file__), "human_prompt.txt")).read()


async def main():
    base_url = os.environ.get("LITELLM_BASE_URL", None)
    api_key = os.environ.get("TEAM_LITELLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    llm = anthropic.Anthropic(**client_kwargs)

    async with sse_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover available tools
            tools_result = await session.list_tools()
            tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema,
                }
                for t in tools_result.tools
            ]

            messages = [{"role": "user", "content": HUMAN_PROMPT}]

            print(f"[solve] Connected to MCP at {MCP_URL}")
            print(f"[solve] Tools: {[t['name'] for t in tools]}")
            print("[solve] Starting agent...\n")

            # ReAct loop
            while True:
                response = llm.messages.create(
                    model=MODEL,
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    messages=messages,
                )

                # Collect assistant content
                assistant_content = []
                tool_calls = []

                for block in response.content:
                    assistant_content.append(block)
                    if block.type == "text":
                        print(f"[agent] {block.text}")
                    elif block.type == "tool_use":
                        tool_calls.append(block)
                        print(f"[tool→] {block.name}({json.dumps(block.input, ensure_ascii=False)[:120]})")

                messages.append({"role": "assistant", "content": assistant_content})

                if response.stop_reason == "end_turn" or not tool_calls:
                    break

                # Execute tool calls
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
