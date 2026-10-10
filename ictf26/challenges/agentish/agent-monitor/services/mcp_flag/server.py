import json
import os
from typing import Any, Literal

import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing_extensions import TypedDict


CONFIG_KEY = "monitor:config"
MIN_SAMPLES_FOR_SUBMISSION = 20


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


def _text_ok(_id: Any, text: str) -> JSONResponse:
    return jsonrpc_ok(_id, {"content": [{"type": "text", "text": text}]})


TOOL = {
    "name": "submit_diagnosis",
    "description": (
        "Submit your diagnosis of the server's health status for the "
        "current round. There are 3 rounds total — each round the server "
        "may run a different scenario. You must correctly diagnose all 3 "
        "rounds to get the flag. Provide the issue type and CPU/memory "
        "evidence based on your monitoring data."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "issue_type": {
                "type": "string",
                "description": (
                    "The diagnosed issue: 'cpu-issue', 'memory-leak', or 'normal'"
                ),
                "enum": ["cpu-issue", "memory-leak", "normal"],
            },
            "cpu_usage_percent": {
                "type": "number",
                "description": (
                    "Observed peak (maximum) CPU usage percentage "
                    "(required for cpu-issue diagnosis)"
                ),
            },
            "memory_usage_mb": {
                "type": "number",
                "description": (
                    "Observed peak (maximum) memory usage in MB "
                    "(required for memory-leak diagnosis)"
                ),
            },
        },
        "required": ["issue_type"],
        "additionalProperties": False,
    },
}


app = FastAPI(title="mcp_flag", version="0.1.0")
redis_client = redis.Redis.from_url(
    _env("REDIS_URL", "redis://datastore:6379/0"), decode_responses=True
)
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

        return _handle_submit_diagnosis(_id, arguments)

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def _handle_submit_diagnosis(_id: Any, arguments: dict[str, Any]) -> JSONResponse:
    issue_type = str(arguments.get("issue_type", "")).strip()
    if issue_type not in ("cpu-issue", "memory-leak", "normal"):
        return jsonrpc_err(
            _id, -32602,
            "Invalid issue_type. Must be 'cpu-issue', 'memory-leak', or 'normal'",
        )

    config = redis_client.hgetall(CONFIG_KEY)
    if not config:
        return jsonrpc_err(_id, -32001, "Challenge not initialized yet")

    current_round = int(config.get("current_round", "1"))
    total_rounds = int(config.get("total_rounds", "3"))
    current_scenario = config.get("current_scenario", "")
    round_status = config.get("round_status", "")

    rnd_label = f"Round {current_round}/{total_rounds}"

    if round_status == "restarting":
        return _text_ok(
            _id,
            f"{rnd_label}: The system is restarting for this round. "
            "Please wait for it to come back up and collect new metrics.",
        )

    raw_samples = redis_client.lrange("monitor:samples", 0, -1)
    samples = [json.loads(s) for s in raw_samples] if raw_samples else []

    if len(samples) < MIN_SAMPLES_FOR_SUBMISSION:
        return _text_ok(
            _id,
            f"{rnd_label}: Not enough monitoring data collected yet "
            f"({len(samples)} samples). Please wait for at least "
            f"{MIN_SAMPLES_FOR_SUBMISSION} samples before submitting.",
        )

    if issue_type != current_scenario:
        return _text_ok(
            _id,
            f"{rnd_label}: Incorrect diagnosis. The issue is not "
            f"'{issue_type}'. Keep monitoring and try again.",
        )

    cpu_values = [
        float(s["cpu_percent"])
        for s in samples
        if s.get("cpu_percent") is not None and float(s["cpu_percent"]) > 0
    ]
    mem_values = [
        float(s["memory_mb"])
        for s in samples
        if s.get("memory_mb") is not None
    ]

    if current_scenario == "cpu-issue":
        reported_cpu = arguments.get("cpu_usage_percent")
        if reported_cpu is None:
            return _text_ok(
                _id,
                f"{rnd_label}: You correctly identified a CPU issue, but "
                "you must provide 'cpu_usage_percent' (peak value) as evidence.",
            )
        reported_cpu = float(reported_cpu)
        actual_max = max(cpu_values) if cpu_values else 0
        if not (actual_max * 0.8 <= reported_cpu <= actual_max * 1.2):
            return _text_ok(
                _id,
                f"{rnd_label}: You correctly identified a CPU issue, but "
                f"your reported peak CPU usage ({reported_cpu:.1f}%) is not "
                "within the acceptable range. Keep monitoring and try again.",
            )

    elif current_scenario == "memory-leak":
        reported_mem = arguments.get("memory_usage_mb")
        if reported_mem is None:
            return _text_ok(
                _id,
                f"{rnd_label}: You correctly identified a memory leak, but "
                "you must provide 'memory_usage_mb' (peak value) as evidence.",
            )
        reported_mem = float(reported_mem)
        actual_max = max(mem_values) if mem_values else 0
        if not (actual_max * 0.8 <= reported_mem <= actual_max * 1.2):
            return _text_ok(
                _id,
                f"{rnd_label}: You correctly identified a memory leak, but "
                f"your reported peak memory ({reported_mem:.0f}MB) is not "
                "within the acceptable range. Keep monitoring and try again.",
            )

    if current_round < total_rounds:
        next_round = current_round + 1
        raw_next = config.get(f"scenario_{next_round}", "")
        try:
            next_obj = json.loads(raw_next)
            next_program = next_obj.get("program", "minio")
            next_issue = next_obj.get("issue", "normal")
        except Exception:
            next_program = "minio"
            next_issue = raw_next or "normal"

        redis_client.hset(CONFIG_KEY, mapping={
            "current_round": str(next_round),
            "current_program": next_program,
            "current_scenario": next_issue,
            "round_status": "restarting",
        })
        redis_client.set("monitor:restart", "1")

        return _text_ok(
            _id,
            f"{rnd_label}: Correct! Advancing to round {next_round}/{total_rounds}. "
            "The system is restarting with a new scenario. Please wait for "
            "it to come back up and collect fresh metrics before diagnosing.",
        )

    return _text_ok(
        _id,
        f"{rnd_label}: Correct! All {total_rounds} rounds passed! "
        f"Flag: {FLAG}",
    )


def main() -> None:
    port = int(_env("PORT", "7002"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
