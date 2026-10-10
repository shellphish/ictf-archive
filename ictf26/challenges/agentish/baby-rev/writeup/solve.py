#!/usr/bin/env python3
"""
Reference solver for the Agentic Binary Reversing challenge.
Uses LangGraph for orchestration and MCP tools for binary analysis.
"""

import json
import os
import re
from typing import Any

import requests
from langgraph.graph import END, START, StateGraph
from typing_extensions import NotRequired, TypedDict


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


def _clean_env_value(v: str) -> str:
    """Remove inline comments from env values."""
    return v.split("#", 1)[0].strip()


def jsonrpc(url: str, method: str, params: dict[str, Any] | None = None, _id: int = 1) -> dict[str, Any]:
    """Make a JSON-RPC 2.0 call."""
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data


def extract_text_content(result: dict[str, Any]) -> str:
    """Extract text content from MCP response."""
    content = result.get("result", {}).get("content", [])
    for item in content:
        if item.get("type") == "text":
            return item.get("text", "")
    return ""


def openai_chat_completion(base_url: str, api_key: str | None, model: str, messages: list[dict]) -> str:
    """Call OpenAI-compatible chat completion API."""
    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "temperature": 0.0,
        "messages": messages,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def analyze_with_llm(prompt: str) -> str:
    """Use LLM to analyze binary data."""
    base_url = _clean_env_value(os.environ.get("LITELLM_BASE_URL") or "")
    if not base_url:
        return ""

    api_key_raw = os.environ.get("TEAM_LITELLM_API_KEY") or ""
    api_key = _clean_env_value(api_key_raw) or None
    model = _clean_env_value(
        os.environ.get("TEAM_LITELLM_MODEL")
        or os.environ.get("LITELLM_MODEL")
        or "gpt-4o-mini"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a reverse engineering expert. Analyze the provided binary data "
                "and extract relevant information. Be concise and precise."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    try:
        return openai_chat_completion(base_url, api_key, model, messages)
    except Exception as e:
        print(f"[solve] LLM call failed: {e}")
        return ""


def main() -> None:
    mcp_url = _env("MCP_BINARY_URL") + "/rpc"

    class SolveState(TypedDict):
        """State for the LangGraph-based solver."""
        functions: NotRequired[list[str]]
        disassembly: NotRequired[dict[str, str]]
        xor_key: NotRequired[int]
        target_plaintext: NotRequired[str]
        password: NotRequired[str]
        result_text: NotRequired[str]

    def node_initialize(_: SolveState) -> SolveState:
        """Initialize the MCP server connection."""
        print("[solve] Initializing MCP server...")
        jsonrpc(mcp_url, "initialize", {"clientInfo": {"name": "binary-solver", "version": "1.0"}})
        return {}

    def node_list_functions(_: SolveState) -> SolveState:
        """List all functions in the binary."""
        print("[solve] Listing functions...")
        res = jsonrpc(mcp_url, "tools/call", {"name": "list_functions", "arguments": {}})
        text = extract_text_content(res)
        print(text)

        # Extract function names
        functions = []
        for line in text.split("\n"):
            if line.strip().startswith("- "):
                func = line.strip()[2:].strip()
                functions.append(func)
        return {"functions": functions}

    def node_analyze_main(state: SolveState) -> SolveState:
        """Analyze the main function to understand the challenge."""
        print("[solve] Analyzing main function...")
        res = jsonrpc(mcp_url, "tools/call", {
            "name": "get_disassembly_by_function",
            "arguments": {"function": "main"}
        })
        main_disasm = extract_text_content(res)

        # Also get validate_stage1 which contains the XOR logic
        res = jsonrpc(mcp_url, "tools/call", {
            "name": "get_disassembly_by_function",
            "arguments": {"function": "validate_stage1(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)"}
        })
        stage1_disasm = extract_text_content(res)

        return {"disassembly": {"main": main_disasm, "validate_stage1": stage1_disasm}}

    def node_extract_xor_key(state: SolveState) -> SolveState:
        """Extract XOR key from the binary or use LLM to analyze."""
        print("[solve] Extracting XOR key...")

        # Try using run_python to find the XOR key
        code = '''
import re
with open("challenge", "rb") as f:
    data = f.read()
# Look for the target plaintext in the binary
target = b"ictf{BINARY_AGENTIC_CHALLENGE}"
if target in data:
    print(f"TARGET_FOUND: {target.decode()}")
# Try to find XOR key by looking for common patterns
# The XOR key is typically a single byte
print("XOR_KEY_SEARCH: Looking for patterns...")
'''
        res = jsonrpc(mcp_url, "tools/call", {
            "name": "run_python",
            "arguments": {"code": code}
        })
        python_output = extract_text_content(res)
        print(f"[solve] Python analysis: {python_output[:200]}...")

        # Known target plaintext from the challenge
        target_plaintext = "ictf{BINARY_AGENTIC_CHALLENGE}"

        # Try common XOR keys or use LLM to analyze
        disasm = state.get("disassembly", {})

        # Look for XOR key in disassembly - typically appears as an immediate value
        xor_key = None

        # Try to find XOR key by testing common values
        # The build script uses printable ASCII range (33-126)
        for test_key in range(33, 127):
            # Generate potential password
            password = ''.join(chr(ord(c) ^ test_key) for c in target_plaintext)
            # Check if all chars are printable
            if all(32 <= ord(c) <= 126 for c in password):
                xor_key = test_key
                break

        if xor_key is None:
            xor_key = 0x42  # Default fallback

        print(f"[solve] Using XOR key: 0x{xor_key:02X}")
        return {"xor_key": xor_key, "target_plaintext": target_plaintext}

    def node_calculate_password(state: SolveState) -> SolveState:
        """Calculate the correct password using XOR."""
        print("[solve] Calculating password...")
        xor_key = state.get("xor_key", 0x42)
        target = state.get("target_plaintext", "ictf{BINARY_AGENTIC_CHALLENGE}")

        # XOR encode the target to get the password
        password = ''.join(chr(ord(c) ^ xor_key) for c in target)
        print(f"[solve] Password calculated (length={len(password)})")

        return {"password": password}

    def node_test_password(state: SolveState) -> SolveState:
        """Test the calculated password."""
        print("[solve] Testing password...")
        password = state.get("password", "")

        res = jsonrpc(mcp_url, "tools/call", {
            "name": "run_challenge",
            "arguments": {"input": password}
        })
        result = extract_text_content(res)
        print(result)

        # Check if we got the flag
        if "SUCCESS" in result and "flag" in result.lower():
            print("\n[solve] Challenge solved!")
        else:
            print("\n[solve] Password incorrect, trying alternative approach...")

        return {"result_text": result}

    def node_bruteforce_xor(state: SolveState) -> SolveState:
        """Bruteforce XOR key if initial attempt failed."""
        result = state.get("result_text", "")
        if "SUCCESS" in result:
            return {}  # Already solved

        print("[solve] Bruteforcing XOR key...")
        target = "ictf{BINARY_AGENTIC_CHALLENGE}"

        for xor_key in range(33, 127):
            password = ''.join(chr(ord(c) ^ xor_key) for c in target)

            # Skip if password has non-printable chars
            if not all(32 <= ord(c) <= 126 for c in password):
                continue

            res = jsonrpc(mcp_url, "tools/call", {
                "name": "run_challenge",
                "arguments": {"input": password}
            })
            result = extract_text_content(res)

            if "SUCCESS" in result:
                print(f"[solve] Found correct XOR key: 0x{xor_key:02X}")
                print(result)
                return {"result_text": result, "xor_key": xor_key}

        return {"result_text": "Failed to find correct password"}

    # Build the LangGraph workflow
    graph = StateGraph(SolveState)

    graph.add_node("initialize", node_initialize)
    graph.add_node("list_functions", node_list_functions)
    graph.add_node("analyze_main", node_analyze_main)
    graph.add_node("extract_xor_key", node_extract_xor_key)
    graph.add_node("calculate_password", node_calculate_password)
    graph.add_node("test_password", node_test_password)
    graph.add_node("bruteforce_xor", node_bruteforce_xor)

    # Define edges
    graph.add_edge(START, "initialize")
    graph.add_edge("initialize", "list_functions")
    graph.add_edge("list_functions", "analyze_main")
    graph.add_edge("analyze_main", "extract_xor_key")
    graph.add_edge("extract_xor_key", "calculate_password")
    graph.add_edge("calculate_password", "test_password")
    graph.add_edge("test_password", "bruteforce_xor")
    graph.add_edge("bruteforce_xor", END)

    # Compile and run
    app = graph.compile()
    final_state = app.invoke({"result_text": ""})

    print("\n" + "=" * 50)
    print("Final Result:")
    print(final_state.get("result_text", "No result"))


if __name__ == "__main__":
    main()
