import os
import re
import subprocess
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing_extensions import TypedDict


COMMAND_TIMEOUT = 30

# ---------------------------------------------------------------------------
# Command-safety filter
# ---------------------------------------------------------------------------
# Patterns that must NOT appear anywhere in the command string.  Uses word
# boundaries (\b) where appropriate so we don't accidentally block harmless
# substrings (e.g. "skilled" matching "kill").
_BLOCKED_PATTERNS: list[str] = [
    # -- Anti-cheat: prevent direct Redis access -------------------------
    r"\bredis-cli\b",
    r"\bredis-server\b",
    r"\b6379\b",                          # Redis port in any form
    r"/dev/tcp/",                          # Bash built-in TCP redirect
    r"/dev/udp/",

    # -- Process manipulation -------------------------------------------
    r"\bkill\b",
    r"\bpkill\b",
    r"\bkillall\b",

    # -- Package / software installation --------------------------------
    r"\bapt-get\b",
    r"\bapt\s+install",
    r"\bdpkg\b",
    r"\bpip3?\s+install",

    # -- Destructive system commands ------------------------------------
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bpoweroff\b",
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r"\brm\s+-[rRf]*\s+/\s*$",           # rm -rf /
    r"\brm\s+-[rRf]*\s+/[a-z]+\s*$",     # rm -rf /usr etc.

    # -- Protect challenge infrastructure -------------------------------
    r">\s*/opt/",                          # redirect into /opt
    r"\bchmod\b.*\s/opt/",
    r"\bchown\b.*\s/opt/",
    r"\bmv\b.*\s/opt/",

    # -- Prevent spawning unrestricted interpreters that could bypass
    #    the filter by, e.g., opening a socket to Redis ----------------
    r"\bpython[23]?\b",
    r"\bperl\b",
    r"\bruby\b",
    r"\bnode\b",
    r"\blua\b",
]

_BLOCKED_RE = re.compile("|".join(_BLOCKED_PATTERNS), re.IGNORECASE)


def _is_command_allowed(command: str) -> tuple[bool, str]:
    """Return (allowed, reason).  reason is non-empty when blocked."""
    m = _BLOCKED_RE.search(command)
    if m:
        return False, f"blocked pattern: {m.group()!r}"
    return True, ""


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


TOOL = {
    "name": "run_command",
    "description": (
        "Execute a shell command on the target server container and return "
        "the combined stdout/stderr output. Commands time out after "
        f"{COMMAND_TIMEOUT} seconds."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Shell command to execute",
            }
        },
        "required": ["command"],
        "additionalProperties": False,
    },
}


app = FastAPI(title="mcp_shell", version="0.1.0")


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
                "serverInfo": {"name": "mcp_shell", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": [TOOL]})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}

        if name != "run_command":
            return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

        command = str(arguments.get("command", "")).strip()
        if not command:
            return jsonrpc_err(_id, -32602, "Empty command")

        allowed, reason = _is_command_allowed(command)
        if not allowed:
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": f"Command rejected ({reason})."}]},
            )

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=COMMAND_TIMEOUT,
            )
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
        except subprocess.TimeoutExpired:
            output = f"Command timed out after {COMMAND_TIMEOUT} seconds."
        except Exception as e:
            output = f"Error executing command: {e}"

        return jsonrpc_ok(
            _id, {"content": [{"type": "text", "text": output}]}
        )

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


if __name__ == "__main__":
    port = int(os.environ.get("SHELL_PORT", "7001"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
