import json
import os
from typing import Any, Literal

import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing_extensions import TypedDict
import uvicorn


UBA_USERS_KEY = "mariosoc:uba:users_json"
UBA_EVENTS_KEY_PREFIX = "mariosoc:uba:events:"


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


def _load_json(r: redis.Redis, key: str) -> Any | None:
    raw = r.get(key)
    if not raw:
        return None
    return json.loads(raw)


TOOL_LIST_USERS = {
    "name": "uba_list_users",
    "description": "List all users mentioned in the user behavior anomaly logs.",
    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
}

TOOL_EVENTS_FOR_USER = {
    "name": "uba_events_for_user",
    "description": "Return user behavior log events for a given user (JSON array).",
    "inputSchema": {
        "type": "object",
        "properties": {"user": {"type": "string", "description": "Username to query."}},
        "required": ["user"],
        "additionalProperties": False,
    },
}


app = FastAPI(title="mcp_uba", version="0.1.0")
redis_client = redis.Redis.from_url(_env("REDIS_URL", "redis://datastore:6379/0"), decode_responses=True)


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
            {"serverInfo": {"name": "mcp_uba", "version": "0.1.0"}, "capabilities": {"tools": {}}},
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": [TOOL_LIST_USERS, TOOL_EVENTS_FOR_USER]})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}

        if name == TOOL_LIST_USERS["name"]:
            users = _load_json(redis_client, UBA_USERS_KEY)
            if users is None:
                return jsonrpc_err(_id, -32001, "Challenge not initialized yet (missing UBA users)")
            return jsonrpc_ok(_id, {"content": [{"type": "text", "text": json.dumps(users, indent=2)}]})

        if name == TOOL_EVENTS_FOR_USER["name"]:
            user = str(arguments.get("user", "")).strip()
            if not user:
                return jsonrpc_err(_id, -32602, "Missing required argument: user")
            events = _load_json(redis_client, UBA_EVENTS_KEY_PREFIX + user)
            if events is None:
                return jsonrpc_err(_id, -32004, "Unknown user (no events)", {"user": user})
            return jsonrpc_ok(_id, {"content": [{"type": "text", "text": json.dumps(events, indent=2)}]})

        return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7101"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()

