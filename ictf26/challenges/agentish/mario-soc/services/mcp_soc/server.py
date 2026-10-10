import json
import os
from typing import Any, Literal

import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing_extensions import TypedDict
import uvicorn


CONFIG_KEY = "mariosoc:config"


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


def _load_config(r: redis.Redis) -> dict[str, Any] | None:
    cfg = r.hgetall(CONFIG_KEY)
    if not cfg:
        return None
    try:
        attacker = json.loads(cfg.get("attacker_json", "{}"))
        victim = json.loads(cfg.get("victim_json", "{}"))
        internal_hosts = json.loads(cfg.get("internal_hosts_json", "[]"))
    except Exception:
        return None
    return {"attacker": attacker, "victim": victim, "internal_hosts": internal_hosts}


def _find_internal(internal_hosts: list[dict[str, Any]], ip: str) -> dict[str, Any] | None:
    for h in internal_hosts:
        if str(h.get("ip", "")).strip() == ip:
            return h
    return None


TOOL_SUBMIT = {
    "name": "soc_submit_correlated_alert",
    "description": "Submit a correlated alert identifying the attacker, first victim (and compromised user), and one successfully exploited internal host. Returns the flag if correct.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "attacker": {
                "type": "object",
                "properties": {"ip": {"type": "string"}, "domain": {"type": "string"}},
                "required": ["ip", "domain"],
                "additionalProperties": False,
            },
            "victim": {
                "type": "object",
                "properties": {"ip": {"type": "string"}, "domain": {"type": "string"}, "user": {"type": "string"}},
                "required": ["ip", "domain", "user"],
                "additionalProperties": False,
            },
            "compromised_internal_host": {
                "type": "object",
                "properties": {"ip": {"type": "string"}, "domain": {"type": "string"}},
                "required": ["ip", "domain"],
                "additionalProperties": False,
            },
        },
        "required": ["attacker", "victim", "compromised_internal_host"],
        "additionalProperties": False,
    },
}


app = FastAPI(title="mcp_soc", version="0.1.0")
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
        return jsonrpc_ok(_id, {"serverInfo": {"name": "mcp_soc", "version": "0.1.0"}, "capabilities": {"tools": {}}})

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": [TOOL_SUBMIT]})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name != TOOL_SUBMIT["name"]:
            return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

        cfg = _load_config(redis_client)
        if not cfg:
            return jsonrpc_err(_id, -32001, "Challenge not initialized yet (missing config in Redis)")

        expected_attacker = cfg["attacker"]
        expected_victim = cfg["victim"]
        internal_hosts: list[dict[str, Any]] = cfg["internal_hosts"]

        attacker = arguments.get("attacker") or {}
        victim = arguments.get("victim") or {}
        internal = arguments.get("compromised_internal_host") or {}

        a_ip = str(attacker.get("ip", "")).strip()
        a_domain = str(attacker.get("domain", "")).strip()
        v_ip = str(victim.get("ip", "")).strip()
        v_domain = str(victim.get("domain", "")).strip()
        v_user = str(victim.get("user", "")).strip()
        i_ip = str(internal.get("ip", "")).strip()
        i_domain = str(internal.get("domain", "")).strip()

        missing = [k for k, val in [("attacker.ip", a_ip), ("attacker.domain", a_domain), ("victim.ip", v_ip), ("victim.domain", v_domain), ("victim.user", v_user), ("compromised_internal_host.ip", i_ip), ("compromised_internal_host.domain", i_domain)] if not val]
        if missing:
            return jsonrpc_err(_id, -32602, "Missing required fields", {"missing": missing})

        ok_attacker = a_ip == str(expected_attacker.get("ip", "")).strip() and a_domain == str(expected_attacker.get("domain", "")).strip()
        ok_victim = (
            v_ip == str(expected_victim.get("ip", "")).strip()
            and v_domain == str(expected_victim.get("domain", "")).strip()
            and v_user == str(expected_victim.get("user", "")).strip()
        )

        internal_expected = _find_internal(internal_hosts, i_ip)
        ok_internal = (
            internal_expected is not None
            and bool(internal_expected.get("exploitation_succeeded")) is True
            and i_domain == str(internal_expected.get("domain", "")).strip()
        )

        if ok_attacker and ok_victim and ok_internal:
            return jsonrpc_ok(_id, {"content": [{"type": "text", "text": f"Correlated alert accepted. Flag: {FLAG}"}]})

        return jsonrpc_ok(
            _id,
            {
                "content": [
                    {
                        "type": "text",
                        "text": "Correlated alert rejected. Ensure you included the attacker, the first victim (with the compromised user), and one successfully compromised internal host (and no non-compromised hosts).",
                    }
                ]
            },
        )

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7104"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()

