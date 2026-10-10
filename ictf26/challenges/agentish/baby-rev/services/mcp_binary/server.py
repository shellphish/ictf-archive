#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Binary Analysis
Provides tools for agents to analyze the challenge binary.

Uses JSON-RPC 2.0 protocol as per the challenge format specification.
"""

import json
import os
import subprocess
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing_extensions import TypedDict

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHALLENGE_BINARY = os.path.join(BASE_DIR, "challenge")
METADATA_FILE = os.path.join(BASE_DIR, "challenge_metadata.json")
FLAG_FILE = os.getenv("FLAG_FILE", os.path.join(BASE_DIR, "flag"))

# Load metadata
METADATA: dict[str, Any] = {}
if os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "r") as f:
        METADATA = json.load(f)

# If FLAG env var is set (dynamic per-team flag), write it to the flag file
# so the challenge binary reads the correct flag.
_flag_override = os.environ.get("FLAG_CHALLENGE", "")
if _flag_override:
    with open(FLAG_FILE, "w") as f:
        f.write(_flag_override)


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


class JsonRpcReq(TypedDict, total=False):
    jsonrpc: Literal["2.0"]
    id: Any
    method: str
    params: dict[str, Any]


def jsonrpc_ok(_id: Any, result: Any) -> JSONResponse:
    return JSONResponse({"jsonrpc": "2.0", "id": _id, "result": result})


def jsonrpc_err(_id: Any, code: int, message: str, data: Any = None) -> JSONResponse:
    err: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return JSONResponse({"jsonrpc": "2.0", "id": _id, "error": err})


# Tool definitions following MCP schema
TOOLS = [
    {
        "name": "list_functions",
        "description": "List all discovered functions from the challenge binary",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "get_disassembly_by_function",
        "description": "Fetch the disassembly for a specific function name",
        "inputSchema": {
            "type": "object",
            "properties": {
                "function": {
                    "type": "string",
                    "description": "Function name/signature to get disassembly for",
                }
            },
            "required": ["function"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_caller_callee_mapping",
        "description": "Return which functions the given caller function invokes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "function_signature": {
                    "type": "string",
                    "description": "Caller function name",
                }
            },
            "required": ["function_signature"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_callee_caller_mapping",
        "description": "Return which functions call the provided callee function",
        "inputSchema": {
            "type": "object",
            "properties": {
                "function_signature": {
                    "type": "string",
                    "description": "Callee function name",
                }
            },
            "required": ["function_signature"],
            "additionalProperties": False,
        },
    },
    {
        "name": "run_challenge",
        "description": "Execute the challenge binary with a candidate password",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Password to test",
                }
            },
            "required": ["input"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_flag",
        "description": "Retrieve the flag after solving the challenge. Requires the correct password.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "The correct password",
                }
            },
            "required": ["input"],
            "additionalProperties": False,
        },
    },
    {
        "name": "run_python",
        "description": "Execute a Python snippet inside the challenge sandbox",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python source to execute",
                },
                "stdin": {
                    "type": "string",
                    "description": "Optional STDIN for the script",
                },
            },
            "required": ["code"],
            "additionalProperties": False,
        },
    },
]


def tool_list_functions() -> str:
    if "functions" not in METADATA:
        return "Error: Functions metadata not available"

    functions = METADATA["functions"]
    result = f"Found {len(functions)} functions in the binary:\n"
    for func in functions:
        result += f"- {func}\n"
    return result


def tool_get_disassembly_by_function(function: str) -> str:
    if not function:
        return "Error: Missing required parameter 'function'"

    disasm_data = METADATA.get("disassembly_by_function", {})
    if function not in disasm_data:
        available = list(disasm_data.keys())
        return f"Error: Function '{function}' not found. Available functions: {available}"

    disasm = disasm_data[function]
    return f"Disassembly for {function}:\n\n{disasm}"


def tool_get_caller_callee_mapping(function_signature: str) -> str:
    if not function_signature:
        return "Error: Missing required parameter 'function_signature'"

    mapping = METADATA.get("caller_callee_mapping", {})
    if function_signature not in mapping:
        available = list(mapping.keys())
        return f"Error: Function '{function_signature}' not found in caller-callee mapping. Available: {available}"

    callees = mapping[function_signature]
    if not callees:
        return f"Function '{function_signature}' does not call any other functions in the binary."

    result = f"Function '{function_signature}' calls:\n"
    for callee in callees:
        result += f"- {callee}\n"
    return result


def tool_get_callee_caller_mapping(function_signature: str) -> str:
    if not function_signature:
        return "Error: Missing required parameter 'function_signature'"

    mapping = METADATA.get("callee_caller_mapping", {})
    if function_signature not in mapping:
        available = list(mapping.keys())
        return f"Error: Function '{function_signature}' not found in callee-caller mapping. Available: {available}"

    callers = mapping[function_signature]
    if not callers:
        return f"Function '{function_signature}' is not called by any other functions in the binary."

    result = f"Function '{function_signature}' is called by:\n"
    for caller in callers:
        result += f"- {caller}\n"
    return result


def tool_run_challenge(input_password: str) -> str:
    if not input_password:
        return "Error: Missing required parameter 'input'"

    if not os.path.exists(CHALLENGE_BINARY):
        return f"Error: Challenge binary not found at {CHALLENGE_BINARY}"

    try:
        result = subprocess.run(
            [CHALLENGE_BINARY, input_password],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=BASE_DIR,
        )

        output = result.stdout
        if result.stderr:
            output += f"\nStderr: {result.stderr}"

        if result.returncode == 0:
            output += "\n\n[SUCCESS] Password accepted!"
        else:
            output += f"\n\n[FAILED] Return code: {result.returncode}"

        return output

    except subprocess.TimeoutExpired:
        return "Error: Execution timeout (5 seconds exceeded)"
    except Exception as e:
        return f"Error: {str(e)}"


def tool_get_flag(input_password: str) -> str:
    if not input_password:
        return "Error: Missing required parameter 'input'"

    if not os.path.exists(CHALLENGE_BINARY):
        return f"Error: Challenge binary not found at {CHALLENGE_BINARY}"

    try:
        result = subprocess.run(
            [CHALLENGE_BINARY, input_password],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=BASE_DIR,
        )

        if result.returncode != 0:
            return "Error: Incorrect password. Solve the challenge first."

        flag = os.environ.get("FLAG_CHALLENGE", "")
        if not flag:
            return "Error: Flag not available"

        return flag

    except subprocess.TimeoutExpired:
        return "Error: Execution timeout (5 seconds exceeded)"
    except Exception as e:
        return f"Error: {str(e)}"


def tool_run_python(code: str, stdin: str = "") -> str:
    if not code:
        return "Error: Missing required parameter 'code'"

    try:
        result = subprocess.run(
            ["python3", "-c", code],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=BASE_DIR,
        )

        output = ""
        if result.stdout:
            output += f"stdout:\n{result.stdout}\n"
        if result.stderr:
            output += f"stderr:\n{result.stderr}\n"
        output += f"return_code: {result.returncode}"

        return output

    except subprocess.TimeoutExpired:
        return "Error: Python execution timed out (10 seconds exceeded)"
    except Exception as e:
        return f"Error: {str(e)}"


def handle_tool_call(name: str, arguments: dict[str, Any]) -> str:
    """Dispatch tool calls to their implementations."""
    if name == "list_functions":
        return tool_list_functions()
    elif name == "get_disassembly_by_function":
        return tool_get_disassembly_by_function(arguments.get("function", ""))
    elif name == "get_caller_callee_mapping":
        return tool_get_caller_callee_mapping(arguments.get("function_signature", ""))
    elif name == "get_callee_caller_mapping":
        return tool_get_callee_caller_mapping(arguments.get("function_signature", ""))
    elif name == "run_challenge":
        return tool_run_challenge(arguments.get("input", ""))
    elif name == "get_flag":
        return tool_get_flag(arguments.get("input", ""))
    elif name == "run_python":
        return tool_run_python(arguments.get("code", ""), arguments.get("stdin", ""))
    else:
        return f"Error: Unknown tool '{name}'"


app = FastAPI(title="mcp_binary", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"ok": "true"}


@app.post("/rpc")
def rpc(req: JsonRpcReq) -> JSONResponse:
    _id = req.get("id")
    method = req.get("method", "")
    params = req.get("params") or {}

    if method == "initialize":
        return jsonrpc_ok(
            _id,
            {
                "serverInfo": {"name": "mcp_binary", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})

        # Validate tool name
        valid_names = [t["name"] for t in TOOLS]
        if name not in valid_names:
            return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name, "valid": valid_names})

        # Execute the tool
        try:
            result_text = handle_tool_call(name, arguments)
            return jsonrpc_ok(_id, {"content": [{"type": "text", "text": result_text}]})
        except Exception as e:
            return jsonrpc_err(_id, -32000, f"Tool execution failed: {str(e)}")

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
