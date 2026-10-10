import json
import os
from typing import Any, Literal

import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing_extensions import TypedDict


CONFIG_KEY = "waldo:config"


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


def load_state(r: redis.Redis) -> str | None:
    cfg = r.hgetall(CONFIG_KEY)
    if not cfg:
        return None
    state = (cfg.get("state") or "").strip()
    return state or None


TOOL = {
    "name": "guess_state",
    "description": "Guess the US state where Waldo resides. Returns the flag if correct.",
    "inputSchema": {
        "type": "object",
        "properties": {"state": {"type": "string", "description": "US state name (full)."}},
        "required": ["state"],
        "additionalProperties": False,
    },
}


app = FastAPI(title="mcp_flag", version="0.1.0")
redis_client = redis.Redis.from_url(_env("REDIS_URL", "redis://datastore:6379/0"), decode_responses=True)
FLAG = os.environ["FLAG_CHALLENGE"]


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
                "serverInfo": {"name": "mcp_flag", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": [TOOL]})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name != TOOL["name"]:
            return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

        state_guess = str(arguments.get("state", "")).strip()
        if not state_guess:
            return jsonrpc_err(_id, -32602, "Missing required argument: state")

        expected = load_state(redis_client)
        if not expected:
            return jsonrpc_err(_id, -32001, "Challenge not initialized yet (missing config in Redis)")

        if state_guess.casefold() == expected.casefold():
            return jsonrpc_ok(_id, {"content": [{"type": "text", "text": f"Correct. Flag: {FLAG}"}]})

        return jsonrpc_ok(_id, {"content": [{"type": "text", "text": "Incorrect state guess."}]})

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7002"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()

