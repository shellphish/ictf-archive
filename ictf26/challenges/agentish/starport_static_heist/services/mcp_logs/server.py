import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing_extensions import TypedDict


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
KEY_PATH = ROOT / "private" / "answer_key.json"


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


def now_unix() -> int:
    override = os.environ.get("CHALLENGE_NOW")
    if override:
        return int(override)
    return int(time.time())


def load_key_config() -> dict[str, Any]:
    return json.loads(KEY_PATH.read_text(encoding="utf-8"))


def compute_temporal_key(secret: str, bucket: int) -> str:
    raw = f"{secret}|{bucket}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:10]


def current_expected_key(cfg: dict[str, Any]) -> str:
    bucket = now_unix() // int(cfg["key_rotation_seconds"])
    return compute_temporal_key(str(cfg["key_secret"]), bucket)


def render_text(text: str) -> str:
    cfg = load_key_config()
    key = current_expected_key(cfg)
    rendered = text.replace("{{KEY_1}}", key[:3])
    rendered = rendered.replace("{{KEY_2}}", key[3:7])
    rendered = rendered.replace("{{KEY_3}}", key[7:10])
    return rendered


def list_logs() -> list[str]:
    return sorted(p.name for p in DATA_DIR.glob("vr_session_logs_part*.jsonl"))


def retrieve_lines_from_log(log_name: str, start_line: int, end_line: int) -> dict[str, Any]:
    if start_line < 1 or end_line < start_line:
        raise ValueError("Invalid line range.")
    path = DATA_DIR / log_name
    if not path.exists():
        raise FileNotFoundError(f"Unknown log: {log_name}")

    lines: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if lineno < start_line:
                continue
            if lineno > end_line:
                break
            event = json.loads(line.rstrip("\n"))
            event["text"] = render_text(str(event.get("text", "")))
            lines.append(json.dumps(event, ensure_ascii=True))

    return {
        "log_name": log_name,
        "start_line": start_line,
        "end_line": end_line,
        "lines": lines,
    }


TOOL_LIST_LOGS = {
    "name": "list_logs",
    "description": "List available VR session log files.",
    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
}

TOOL_RETRIEVE_LINES = {
    "name": "retrieve_lines_from_log",
    "description": "Get an inclusive line range from a single log file.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "log_name": {"type": "string"},
            "start_line": {"type": "integer"},
            "end_line": {"type": "integer"},
        },
        "required": ["log_name", "start_line", "end_line"],
        "additionalProperties": False,
    },
}

TOOL_SUBMIT_KEY = {
    "name": "submit_key",
    "description": "Submit a 10-hex rotating key and receive the flag if correct.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "key": {"type": "string"},
        },
        "required": ["key"],
        "additionalProperties": False,
    },
}

TOOLS = [TOOL_LIST_LOGS, TOOL_RETRIEVE_LINES, TOOL_SUBMIT_KEY]

app = FastAPI(title="mcp_logs", version="0.1.0")


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
                "serverInfo": {"name": "mcp_logs", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}

        if name == "list_logs":
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": json.dumps({"logs": list_logs()}, ensure_ascii=True)}]},
            )

        if name == "retrieve_lines_from_log":
            try:
                payload = retrieve_lines_from_log(
                    str(arguments.get("log_name", "")),
                    int(arguments.get("start_line")),
                    int(arguments.get("end_line")),
                )
            except (ValueError, TypeError) as e:
                return jsonrpc_err(_id, -32602, "Invalid arguments", {"error": str(e)})
            except FileNotFoundError as e:
                return jsonrpc_err(_id, -32602, "Unknown log", {"error": str(e)})
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=True)}]},
            )

        if name == "submit_key":
            submitted = str(arguments.get("key", "")).strip().lower()
            if not re.fullmatch(r"[a-f0-9]{10}", submitted):
                return jsonrpc_ok(_id, {"content": [{"type": "text", "text": "invalid format"}]})

            cfg = load_key_config()
            expected = current_expected_key(cfg)
            if submitted == expected:
                flag = os.environ["FLAG_CHALLENGE"]
                return jsonrpc_ok(_id, {"content": [{"type": "text", "text": flag}]})
            return jsonrpc_ok(_id, {"content": [{"type": "text", "text": "incorrect key"}]})

        return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(os.environ.get("PORT", "7301"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
