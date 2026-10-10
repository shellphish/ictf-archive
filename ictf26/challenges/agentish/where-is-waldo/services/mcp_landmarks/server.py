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


def load_config(r: redis.Redis) -> dict[str, Any] | None:
    cfg = r.hgetall(CONFIG_KEY)
    if not cfg:
        return None
    try:
        landmarks = json.loads(cfg.get("landmarks_json", "[]"))
    except Exception:
        landmarks = []
    return {
        "city": cfg.get("city", ""),
        "state": cfg.get("state", ""),
        "landmarks": landmarks,
    }


TOOL = {
    "name": "waldo_landmarks",
    "description": "Return three landmarks near where Waldo is hiding (in the same US city).",
    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
}


app = FastAPI(title="mcp_landmarks", version="0.1.0")
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
            {
                "serverInfo": {"name": "mcp_landmarks", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": [TOOL]})

    if method == "tools/call":
        name = params.get("name")
        if name != TOOL["name"]:
            return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

        cfg = load_config(redis_client)
        if not cfg or not cfg.get("landmarks"):
            return jsonrpc_err(_id, -32001, "Challenge not initialized yet (missing config in Redis)")

        text = "Landmarks near Waldo:\n" + "\n".join(f"- {x}" for x in cfg["landmarks"])
        return jsonrpc_ok(_id, {"content": [{"type": "text", "text": text}]})

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7001"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()

