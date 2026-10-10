"""
Street Fighter 2 MCP Trainer server.
Endpoints: train, attack, defense, assessment, opponents. assessment returns JSON for both combatants; opponents returns JSON for both opponents.
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
        combatant_1 = json.loads(cfg.get("combatant_1_json", "{}"))
        combatant_2 = json.loads(cfg.get("combatant_2_json", "{}"))
        opponent_1 = json.loads(cfg.get("opponent_1_json", "{}"))
        opponent_2 = json.loads(cfg.get("opponent_2_json", "{}"))
        opponent_combo_vulnerability = json.loads(cfg.get("opponent_combo_vulnerability_json", "[]"))
        combatant_combo_attack = json.loads(cfg.get("combatant_combo_attack_json", "[]"))
        combatant_combo_vulnerability = json.loads(cfg.get("combatant_combo_vulnerability_json", "[]"))
        opponent_combo_attack = json.loads(cfg.get("opponent_combo_attack_json", "[]"))
        return {
            "combatant_1": combatant_1,
            "combatant_2": combatant_2,
            "opponent_1": opponent_1,
            "opponent_2": opponent_2,
            "opponent_combo_vulnerability": opponent_combo_vulnerability,
            "combatant_combo_attack": combatant_combo_attack,
            "combatant_combo_vulnerability": combatant_combo_vulnerability,
            "opponent_combo_attack": opponent_combo_attack,
        }
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


def attack(r: redis.Redis, training_id: str) -> dict[str, Any] | None:
    """Return current step and attack. If trained, return status='trained'."""
    key = f"{TRAINING_PREFIX}{training_id}"
    raw = r.get(key)
    if not raw:
        return None
    state = json.loads(raw)
    if state.get("trained"):
        return {"step": state["step"], "status": "trained"}
    return {"step": str(state["step"]), "attack": state["attack"]}


def defense(r: redis.Redis, training_id: str, step_id: str, defense_val: str) -> dict[str, Any]:
    """Validate defense. If correct, advance. After required_steps correct, set trained."""
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
    if defense_val.strip().casefold() != expected_defense.casefold():
        return {"ok": False, "message": "Incorrect defense."}

    required_steps = state.get("required_steps", 5)
    correct_count = state.get("correct_count", 0) + 1

    if correct_count >= required_steps:
        state["trained"] = True
        state["correct_count"] = correct_count
        r.setex(key, 3600, json.dumps(state))
        return {"ok": True, "message": "Correct! You are now trained.", "status": "trained"}
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
        "name": "attack",
        "description": "Get the current training step and attack to defend against. Pass training_id.",
        "inputSchema": {
            "type": "object",
            "properties": {"training_id": {"type": "string"}},
            "required": ["training_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "defense",
        "description": "Submit your defense (parry/block/jump/sidestep/brace) for the given step.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "training_id": {"type": "string"},
                "step_id": {"type": "string"},
                "defense": {"type": "string"},
            },
            "required": ["training_id", "step_id", "defense"],
            "additionalProperties": False,
        },
    },
    {
        "name": "assessment",
        "description": "Returns JSON for both combatants (combatant_1, combatant_2) plus combatant combo info (combatant_combo_attack, combatant_combo_vulnerability). Requires training to be complete.",
        "inputSchema": {
            "type": "object",
            "properties": {"training_id": {"type": "string"}},
            "required": ["training_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "opponents",
        "description": "Returns JSON for both opponents (opponent_1, opponent_2) plus opponent combo info (opponent_combo_vulnerability, opponent_combo_attack). Requires training to be complete.",
        "inputSchema": {
            "type": "object",
            "properties": {"training_id": {"type": "string"}},
            "required": ["training_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "status",
        "description": "Get training status: 'in_progress', 'success', or 'failure'. Returns error_message if training_id is incorrect.",
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

        if name == "attack":
            training_id = str(arguments.get("training_id", "")).strip()
            if not training_id:
                return jsonrpc_err(_id, -32602, "Missing required argument: training_id")
            result = attack(redis_client, training_id)
            if result is None:
                return jsonrpc_err(_id, -32002, "Unknown or expired training_id")
            text = f"Step {result.get('step')}, "
            if result.get("status") == "trained":
                text += "trained."
            else:
                text += f"incoming attack: {result.get('attack')}."
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": text}], **result},
            )

        if name == "defense":
            training_id = str(arguments.get("training_id", "")).strip()
            step_id = str(arguments.get("step_id", "")).strip()
            defense_val = str(arguments.get("defense", "")).strip()
            if not training_id or not step_id or not defense_val:
                return jsonrpc_err(
                    _id, -32602, "Missing required arguments: training_id, step_id, defense"
                )
            result = defense(redis_client, training_id, step_id, defense_val)
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
            lines = []
            for i, combatant in enumerate([config["combatant_1"], config["combatant_2"]], 1):
                lines.append(f"Combatant {i}: {combatant.get('name', '?')}")
                lines.append(f"  Description: {combatant.get('description', '')}")
                lines.append("  Attacks:")
                for atk_name, data in combatant.get("attacks", {}).items():
                    lines.append(f"    {atk_name}: damage={data['damage']}, success_rate={data['success_rate']}")
                lines.append("  Defenses:")
                for def_name, data in combatant.get("defenses", {}).items():
                    lines.append(f"    {def_name}: success_rate={data['success_rate']}")
            lines.append("Combatant combo attack (use when opponents expose vulnerability): " + str(config["combatant_combo_attack"]))
            lines.append("Combatant combo vulnerability (avoid doing this): " + str(config["combatant_combo_vulnerability"]))
            text = "\n".join(lines)
            c1_name = config["combatant_1"].get("name", "?")
            c2_name = config["combatant_2"].get("name", "?")
            print(f"[assessment] training_id={training_id}, combatants: {c1_name}, {c2_name}")
            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": text}],
                    "combatant_1": config["combatant_1"],
                    "combatant_2": config["combatant_2"],
                    "combatant_combo_attack": config["combatant_combo_attack"],
                    "combatant_combo_vulnerability": config["combatant_combo_vulnerability"],
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

        if name == "opponents":
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
            lines = []
            for i, opp in enumerate([config["opponent_1"], config["opponent_2"]], 1):
                lines.append(f"Opponent {i}: {opp.get('name')}")
                lines.append(f"  Description: {opp.get('description')}")
                lines.append("  Attacks:")
                for atk_name, data in opp.get("attacks", {}).items():
                    lines.append(f"    {atk_name}: damage={data['damage']}, success_rate={data['success_rate']}")
                lines.append("  Defenses:")
                for def_name, data in opp.get("defenses", {}).items():
                    lines.append(f"    {def_name}: success_rate={data['success_rate']}")
            lines.append("Opponent combo vulnerability (opponents perform these): " + str(config["opponent_combo_vulnerability"]))
            lines.append("Opponent combo attack (they use when we expose ourselves): " + str(config["opponent_combo_attack"]))
            text = "\n".join(lines)
            o1_name = config["opponent_1"].get("name", "?")
            o2_name = config["opponent_2"].get("name", "?")
            print(f"[opponents] training_id={training_id}, opponents: {o1_name}, {o2_name}")
            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": text}],
                    "opponent_1": config["opponent_1"],
                    "opponent_2": config["opponent_2"],
                    "opponent_combo_vulnerability": config["opponent_combo_vulnerability"],
                    "opponent_combo_attack": config["opponent_combo_attack"],
                },
            )

        return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7011"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
