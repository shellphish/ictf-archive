"""
Street Fighter MCP Trainer server.
Endpoints: train, action, reaction, assessment, opponent, status
"""
import json
import os
import secrets
from typing import Any, Literal

import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing_extensions import TypedDict


import random

CONFIG_KEY = "sf:config"
TRAINING_PREFIX = "sf:training:"
TRAINING_DONE_PREFIX = "sf:training:done:"
REQUIRED_STEPS_MIN = 3
REQUIRED_STEPS_MAX = 10

ATTACKS = ["punch", "kick", "sweep", "elbow", "headbutt"]
DEFENSE_FOR_ATTACK = {
    "punch": "parry",
    "kick": "block",
    "sweep": "jump",
    "elbow": "sidestep",
    "headbutt": "brace",
}


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
        combatant = json.loads(cfg.get("combatant_json", "{}"))
        opponent = json.loads(cfg.get("opponent_json", "{}"))
        return {"combatant": combatant, "opponent": opponent}
    except Exception:
        return None


def train(r: redis.Redis) -> str:
    """Create new training session, return training_id."""
    training_id = secrets.token_hex(8)
    required_steps = random.randint(REQUIRED_STEPS_MIN, REQUIRED_STEPS_MAX)
    attack = random.choice(ATTACKS)
    state = {
        "step": 1,
        "attack": attack,
        "correct_count": 0,
        "trained": False,
        "required_steps": required_steps,
    }
    r.setex(f"{TRAINING_PREFIX}{training_id}", 3600, json.dumps(state))
    return training_id


def action(r: redis.Redis, training_id: str) -> dict[str, Any] | None:
    """Return current step and attack. If trained, return action='trained'."""
    key = f"{TRAINING_PREFIX}{training_id}"
    raw = r.get(key)
    if not raw:
        return None
    state = json.loads(raw)
    if state.get("trained"):
        return {"step": state["step"], "action": "trained"}
    return {"step": str(state["step"]), "attack": state["attack"]}


def reaction(r: redis.Redis, training_id: str, step_id: str, reaction: str) -> dict[str, Any]:
    """Validate reaction. If correct, advance. After required_steps correct, set trained."""
    key = f"{TRAINING_PREFIX}{training_id}"
    raw = r.get(key)
    if not raw:
        return {"ok": False, "message": "Unknown or expired training_id"}

    state = json.loads(raw)
    if state.get("trained"):
        return {"ok": True, "message": "Already trained."}

    if str(state["step"]) != str(step_id):
        return {"ok": False, "message": "Step ID mismatch."}

    expected_defense = DEFENSE_FOR_ATTACK.get(state["attack"], "")
    if reaction.strip().casefold() != expected_defense.casefold():
        return {"ok": False, "message": "Incorrect defense."}

    required_steps = state.get("required_steps", 5)
    correct_count = state.get("correct_count", 0) + 1

    if correct_count >= required_steps:
        state["trained"] = True
        state["correct_count"] = correct_count
        r.setex(key, 3600, json.dumps(state))
        # Mark this training_id as successfully completed so the arena can verify it.
        # TTL matches the training session (1 hour) — after that the token is gone anyway.
        r.setex(f"{TRAINING_DONE_PREFIX}{training_id}", 3600, "1")
        return {"ok": True, "message": "Correct! You are now trained.", "action": "trained"}
    else:
        state["step"] += 1
        state["attack"] = random.choice(ATTACKS)
        state["correct_count"] = correct_count
        r.setex(key, 3600, json.dumps(state))
        return {
            "ok": True,
            "message": f"Correct! ({correct_count}/{required_steps})",
            "step": str(state["step"]),
            "attack": state["attack"],
        }


TOOLS = [
    {
        "name": "train",
        "description": "Start training with Master Jee-Oh Vhun-Ee. Returns a unique training_id.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "action",
        "description": "Get the current training step and attack to defend against. Pass training_id.",
        "inputSchema": {
            "type": "object",
            "properties": {"training_id": {"type": "string"}},
            "required": ["training_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "reaction",
        "description": "Submit your defense (parry/block/jump/sidestep/brace) for the given step.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "training_id": {"type": "string"},
                "step_id": {"type": "string"},
                "reaction": {"type": "string"},
            },
            "required": ["training_id", "step_id", "reaction"],
            "additionalProperties": False,
        },
    },
    {
        "name": "assessment",
        "description": "Get your combatant's damage and success rates. Requires training to be complete.",
        "inputSchema": {
            "type": "object",
            "properties": {"training_id": {"type": "string"}},
            "required": ["training_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "opponent",
        "description": "Get opponent name, description, and damage/success rates. Requires training to be complete.",
        "inputSchema": {
            "type": "object",
            "properties": {"training_id": {"type": "string"}},
            "required": ["training_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "status",
        "description": "Get training status: 'in_progress', 'success', or 'failure'. Pass training_id.",
        "inputSchema": {
            "type": "object",
            "properties": {"training_id": {"type": "string"}},
            "required": ["training_id"],
            "additionalProperties": False,
        },
    },
]


app = FastAPI(title="mcp_trainer", version="0.1.0")
redis_client = redis.Redis.from_url(
    _env("REDIS_URL", "redis://datastore:6379/0"), decode_responses=True
)


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
                "serverInfo": {"name": "mcp_trainer", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}

        if name == "train":
            config = load_config(redis_client)
            if not config:
                return jsonrpc_err(
                    _id, -32001, "Challenge not initialized yet (missing sf:config in Redis)"
                )
            training_id = train(redis_client)
            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": f"Training started. training_id={training_id}"}],
                    "training_id": training_id,
                },
            )

        if name == "action":
            training_id = str(arguments.get("training_id", "")).strip()
            if not training_id:
                return jsonrpc_err(_id, -32602, "Missing required argument: training_id")
            result = action(redis_client, training_id)
            if result is None:
                return jsonrpc_err(_id, -32002, "Unknown or expired training_id")
            text = f"Step {result.get('step')}, "
            if result.get("action") == "trained":
                text += "trained."
            else:
                text += f"incoming attack: {result.get('attack')}."
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": text}], **result},
            )

        if name == "reaction":
            training_id = str(arguments.get("training_id", "")).strip()
            step_id = str(arguments.get("step_id", "")).strip()
            reaction_val = str(arguments.get("reaction", "")).strip()
            if not training_id or not step_id or not reaction_val:
                return jsonrpc_err(
                    _id, -32602, "Missing required arguments: training_id, step_id, reaction"
                )
            result = reaction(redis_client, training_id, step_id, reaction_val)
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": result["message"]}], **result},
            )

        if name == "assessment":
            training_id = str(arguments.get("training_id", "")).strip()
            if not training_id:
                return jsonrpc_err(_id, -32602, "Missing required argument: training_id")
            key = f"{TRAINING_PREFIX}{training_id}"
            raw = redis_client.get(key)
            if not raw:
                return jsonrpc_err(_id, -32002, "Unknown or expired training_id")
            state = json.loads(raw)
            if not state.get("trained"):
                return jsonrpc_err(_id, -32003, "Complete training first")
            config = load_config(redis_client)
            if not config:
                return jsonrpc_err(_id, -32001, "Challenge not initialized")
            combatant = config["combatant"]
            lines = ["Combatant stats:"]
            for attack, data in combatant.get("attacks", {}).items():
                lines.append(f"  {attack}: damage={data['damage']}, success_rate={data['success_rate']}")
            for defense, data in combatant.get("defenses", {}).items():
                lines.append(f"  {defense}: success_rate={data['success_rate']}")
            text = "\n".join(lines)
            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": text}],
                    "combatant": combatant,
                },
            )

        if name == "status":
            training_id = str(arguments.get("training_id", "")).strip()
            if not training_id:
                return jsonrpc_ok(
                    _id,
                    {
                        "content": [{"type": "text", "text": "Training status: failure. Missing required argument: training_id."}],
                        "status": "failure",
                        "error_message": "Missing required argument: training_id",
                    },
                )
            key = f"{TRAINING_PREFIX}{training_id}"
            raw = redis_client.get(key)
            if not raw:
                return jsonrpc_ok(
                    _id,
                    {
                        "content": [{"type": "text", "text": "Training status: failure. Unknown or expired training_id."}],
                        "status": "failure",
                        "error_message": "Unknown or expired training_id",
                    },
                )
            state = json.loads(raw)
            status = "success" if state.get("trained") else "in_progress"
            text = f"Training status: {status}"
            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": text}],
                    "status": status,
                },
            )

        if name == "opponent":
            training_id = str(arguments.get("training_id", "")).strip()
            if not training_id:
                return jsonrpc_err(_id, -32602, "Missing required argument: training_id")
            key = f"{TRAINING_PREFIX}{training_id}"
            raw = redis_client.get(key)
            if not raw:
                return jsonrpc_err(_id, -32002, "Unknown or expired training_id")
            state = json.loads(raw)
            if not state.get("trained"):
                return jsonrpc_err(_id, -32003, "Complete training first")
            config = load_config(redis_client)
            if not config:
                return jsonrpc_err(_id, -32001, "Challenge not initialized")
            opponent = config["opponent"]
            lines = [
                f"Opponent: {opponent.get('name')}",
                f"Description: {opponent.get('description')}",
                "Attacks:",
            ]
            for attack, data in opponent.get("attacks", {}).items():
                lines.append(f"  {attack}: damage={data['damage']}, success_rate={data['success_rate']}")
            lines.append("Defenses:")
            for defense, data in opponent.get("defenses", {}).items():
                lines.append(f"  {defense}: success_rate={data['success_rate']}")
            text = "\n".join(lines)
            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": text}],
                    "opponent": opponent,
                },
            )

        return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7011"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
