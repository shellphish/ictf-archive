import json
import os
from typing import Any, Literal

import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing_extensions import TypedDict


GOSSIP_KEY = "rumor:gossip:1"


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


def load_gossip(r: redis.Redis) -> dict[str, Any] | None:
    raw = r.get(GOSSIP_KEY)
    if not raw:
        return None
    try:
        obj = json.loads(raw)
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None
    return obj


def format_message(gossip: dict[str, Any], msg: dict[str, Any]) -> str:
    source = msg.get("source", "")
    message = msg.get("message", "")
    lines = [
        f"Source: {source}",
        "Message:",
        f"{message}",
    ]
    return "\n".join(lines).strip() + "\n"


TOOL_GOSSIP = {
    "name": "gossip",
    "description": "Return the first message in the gossip chain.",
    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
}

TOOL_RUMOR = {
    "name": "rumor",
    "description": "Return the message in the gossip associated with a given source.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "source": {"type": "string", "description": "Source email address."},
        },
        "required": ["source"],
        "additionalProperties": False,
    },
}

TOOL_OPINION = {
    "name": "opinion",
    "description": "Submit the ordered list of sources and your final IoC. Returns the flag if correct.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "sources": {"type": "array", "items": {"type": "string"}, "description": "Ordered list of sources."},
            "ioc": {"type": "string", "description": "Your final IoC guess (exact string)."},
        },
        "required": ["sources", "ioc"],
        "additionalProperties": False,
    },
}


app = FastAPI(title="mcp_gossip", version="0.1.0")
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
                "serverInfo": {"name": "mcp_gossip", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": [TOOL_GOSSIP, TOOL_RUMOR, TOOL_OPINION]})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}

        gossip = load_gossip(redis_client)
        if not gossip:
            return jsonrpc_err(_id, -32001, "Challenge not initialized yet (missing gossip in Redis)")

        if name == TOOL_GOSSIP["name"]:
            msgs = gossip.get("messages") or []
            if not isinstance(msgs, list) or not msgs:
                return jsonrpc_err(_id, -32002, "Invalid gossip data (missing messages)")
            text = format_message(gossip, msgs[0])
            return jsonrpc_ok(_id, {"content": [{"type": "text", "text": text}]})

        if name == TOOL_RUMOR["name"]:
            source = str(arguments.get("source", "")).strip()
            if not source:
                return jsonrpc_err(_id, -32602, "Missing required argument: source")

            msgs = gossip.get("messages") or []
            if not isinstance(msgs, list) or not msgs:
                return jsonrpc_err(_id, -32002, "Invalid gossip data (missing messages)")

            for m in msgs:
                if isinstance(m, dict) and str(m.get("source", "")).strip().casefold() == source.casefold():
                    text = format_message(gossip, m)
                    return jsonrpc_ok(_id, {"content": [{"type": "text", "text": text}]})

            return jsonrpc_err(_id, -32602, "Unknown source", {"source": source})

        if name == TOOL_OPINION["name"]:
            sources_arg = arguments.get("sources")
            if not isinstance(sources_arg, list):
                return jsonrpc_err(_id, -32602, "sources must be a list of strings")
            sources = [str(x).strip() for x in sources_arg if str(x).strip()]
            ioc = str(arguments.get("ioc", "")).strip()
            if not sources or not ioc:
                return jsonrpc_err(_id, -32602, "Missing required arguments: sources, ioc")

            expected_sources = [str(x).strip() for x in (gossip.get("sources") or [])]
            expected_ioc = str(gossip.get("true_ioc", "")).strip()
            if not expected_sources or not expected_ioc:
                return jsonrpc_err(_id, -32002, "Invalid gossip data (missing sources/true_ioc)")

            ok_chain = sources == expected_sources
            ok_ioc = ioc.casefold() == expected_ioc.casefold()

            if ok_chain and ok_ioc:
                return jsonrpc_ok(_id, {"content": [{"type": "text", "text": f"Correct. Flag: {FLAG}"}]})

            return jsonrpc_ok(
                _id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": "Failed to recover the IoC from the correct list of sources",
                        }
                    ]
                },
            )

        return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7003"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()

