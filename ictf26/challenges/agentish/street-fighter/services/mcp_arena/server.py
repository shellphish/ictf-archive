"""
Street Fighter MCP Arena server.
Endpoints: fight, arena_action, arena_reaction, arena_status
"""
import json
import os
import random
import secrets
from typing import Any, Literal

import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing_extensions import TypedDict


CONFIG_KEY = "sf:config"
FIGHT_PREFIX = "sf:fight:"
ARENA_FIGHT_DONE_KEY = "sf:arena:fight_done"
TRAINING_DONE_PREFIX = "sf:training:done:"
TRAINING_USED_PREFIX = "sf:training:used:"

ATTACKS = ["punch", "kick", "sweep", "elbow", "headbutt"]
DEFENSE_FOR_ATTACK = {
    "punch": "parry",
    "kick": "block",
    "sweep": "jump",
    "elbow": "sidestep",
    "headbutt": "brace",
}
DEFENSES = list(DEFENSE_FOR_ATTACK.values())

INITIAL_HEALTH = 100


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


app = FastAPI(title="mcp_arena", version="0.1.0")
redis_client = redis.Redis.from_url(
    _env("REDIS_URL", "redis://datastore:6379/0"), decode_responses=True
)
FLAG = os.environ.get("FLAG_CHALLENGE", "ictf{placeholder_flag}")
DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"ok": "true"}


def _mark_fight_done() -> None:
    """Mark that a fight has completed (used when DEBUG is False)."""
    redis_client.setex(ARENA_FIGHT_DONE_KEY, 86400, "1")  # 24h TTL


def _fight(training_id: str) -> tuple[str | None, str | None]:
    """Create fight. Requires a valid completed training_id. Returns (fight_id, error_message)."""
    if not training_id:
        return None, "Missing training_id. Complete training successfully first."

    # Verify training was actually completed successfully
    if not redis_client.exists(f"{TRAINING_DONE_PREFIX}{training_id}"):
        return None, "Invalid or incomplete training_id. Complete training successfully first."

    # Prevent the same training_id from opening more than one fight
    if not DEBUG and redis_client.exists(f"{TRAINING_USED_PREFIX}{training_id}"):
        return None, "This training_id has already been used to start a fight. Train again."

    config = load_config(redis_client)
    if not config:
        return None, None

    fight_id = secrets.token_hex(8)
    fight_state = {
        "combatant_health": INITIAL_HEALTH,
        "opponent_health": INITIAL_HEALTH,
        "step": 0,
        "combatant": config["combatant"],
        "opponent": config["opponent"],
        "opponent_name": config["opponent"].get("name", "Opponent"),
        "last_action": None,
        "last_success": None,
        "phase": "opponent_attack",  # or "agent_react"
    }
    redis_client.setex(f"{FIGHT_PREFIX}{fight_id}", 3600, json.dumps(fight_state))

    # LEO: Consume the training_id it cannot be used to open another fight with the same training_id
    if not DEBUG:
        redis_client.setex(f"{TRAINING_USED_PREFIX}{training_id}", 3600, "1")

    return fight_id, None


def _do_opponent_attack(fight_state: dict) -> dict:
    """Opponent attacks. Returns updated state and action info."""
    opponent = fight_state["opponent"]
    attacks = opponent.get("attacks", {})
    attack_name = random.choice(ATTACKS)
    attack_data = attacks.get(attack_name, {"damage": 5, "success_rate": 0.5})
    success_rate = attack_data["success_rate"]
    success = random.random() < success_rate
    damage = attack_data["damage"] if success else 0
    fight_state["combatant_health"] = max(0, fight_state["combatant_health"] - damage)
    fight_state["last_action"] = attack_name
    fight_state["last_success"] = success
    fight_state["last_success_rate"] = success_rate
    fight_state["last_damage"] = damage
    fight_state["phase"] = "agent_react"
    return fight_state


def _do_agent_defense(fight_state: dict, reaction: str) -> dict:
    """Agent defends. Reaction is parry/block/jump/sidestep/brace."""
    attack = fight_state.get("last_action")
    if not attack:
        return fight_state
    expected_defense = DEFENSE_FOR_ATTACK.get(attack)
    defense_success = False
    defense_success_rate = 0.0
    correct_defense = reaction.strip().casefold() == expected_defense.casefold()
    if correct_defense:
        combatant = fight_state["combatant"]
        defenses = combatant.get("defenses", {})
        def_data = defenses.get(reaction, {"success_rate": 0.5})
        defense_success_rate = def_data["success_rate"]
        defense_success = random.random() < defense_success_rate
        if defense_success:
            fight_state["combatant_health"] = min(
                INITIAL_HEALTH,
                fight_state["combatant_health"] + fight_state.get("last_damage", 0),
            )
    fight_state["last_defense_success"] = defense_success
    fight_state["last_defense_success_rate"] = defense_success_rate
    fight_state["last_defense_correct"] = correct_defense
    fight_state["phase"] = "opponent_attack"
    return fight_state


def _do_agent_attack(fight_state: dict, attack: str) -> dict:
    """Agent attacks."""
    combatant = fight_state["combatant"]
    attacks = combatant.get("attacks", {})
    attack_data = attacks.get(attack, {"damage": 5, "success_rate": 0.5})
    success_rate = attack_data["success_rate"]
    success = random.random() < success_rate
    damage = attack_data["damage"] if success else 0
    fight_state["opponent_health"] = max(0, fight_state["opponent_health"] - damage)
    fight_state["last_action"] = attack
    fight_state["last_success"] = success
    fight_state["last_success_rate"] = success_rate
    fight_state["last_damage"] = damage
    fight_state["phase"] = "opponent_react"
    return fight_state


def _do_opponent_defense(fight_state: dict, attack: str) -> dict:
    """Opponent defends against agent's attack."""
    expected_defense = DEFENSE_FOR_ATTACK.get(attack)
    opponent = fight_state["opponent"]
    defenses = opponent.get("defenses", {})
    def_data = defenses.get(expected_defense, {"success_rate": 0.5})
    defense_success_rate = def_data["success_rate"]
    defense_success = random.random() < defense_success_rate
    if defense_success:
        fight_state["opponent_health"] = min(
            INITIAL_HEALTH,
            fight_state["opponent_health"] + fight_state.get("last_damage", 0),
        )
    fight_state["last_defense_success"] = defense_success
    fight_state["last_defense_success_rate"] = defense_success_rate
    fight_state["phase"] = "opponent_attack"
    return fight_state


TOOLS = [
    {
        "name": "fight",
        "description": "Start a fight. Pass training_id from a successful training session. Returns fight_id.",
        "inputSchema": {
            "type": "object",
            "properties": {"training_id": {"type": "string"}},
            "required": ["training_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "arena_action",
        "description": "Get the current fight step: opponent's attack. Always alternate action then reaction.",
        "inputSchema": {
            "type": "object",
            "properties": {"fight_id": {"type": "string"}},
            "required": ["fight_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "arena_reaction",
        "description": "Perform defense or counter-attack. When opponent HITS: defend (parry/block/jump/sidestep/brace) or counter-attack (punch/kick/sweep/elbow/headbutt). When opponent MISSES: counter-attack only (defense useless); arena applies opponent's corresponding defense.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fight_id": {"type": "string"},
                "step_id": {"type": "string"},
                "action": {"type": "string"},
            },
            "required": ["fight_id", "step_id", "action"],
            "additionalProperties": False,
        },
    },
    {
        "name": "arena_status",
        "description": "Get combatant and opponent health. Returns flag if opponent health is 0.",
        "inputSchema": {
            "type": "object",
            "properties": {"fight_id": {"type": "string"}},
            "required": ["fight_id"],
            "additionalProperties": False,
        },
    },
]


@app.post("/rpc")
def rpc(req: JsonRpcReq) -> JSONResponse:
    _id = req.get("id")
    method = req.get("method", "")
    params = req.get("params") or {}

    if method == "initialize":
        return jsonrpc_ok(
            _id,
            {
                "serverInfo": {"name": "mcp_arena", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}

        if name == "fight":
            training_id = str(arguments.get("training_id", "")).strip()
            fight_id, err = _fight(training_id)
            if err:
                return jsonrpc_err(_id, -32002, err)
            if fight_id is None:
                return jsonrpc_err(
                    _id,
                    -32002,
                    "Could not start fight. Config may be missing.",
                )
            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": f"Fight started. fight_id={fight_id}"}],
                    "fight_id": fight_id,
                },
            )

        if name in ("action", "arena_action"):
            fight_id = str(arguments.get("fight_id", "")).strip()
            if not fight_id:
                return jsonrpc_err(_id, -32602, "Missing required argument: fight_id")
            key = f"{FIGHT_PREFIX}{fight_id}"
            raw = redis_client.get(key)
            if not raw:
                return jsonrpc_err(_id, -32002, "Unknown or expired fight_id")
            fight_state = json.loads(raw)

            if fight_state["combatant_health"] <= 0:
                if not DEBUG:
                    _mark_fight_done()
                return jsonrpc_ok(
                    _id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": "no flag, this time",
                            }
                        ],
                        "combatant_health": 0,
                        "opponent_health": fight_state["opponent_health"],
                        "game_over": True,
                    },
                )

            if fight_state["opponent_health"] <= 0:
                if not DEBUG:
                    _mark_fight_done()
                return jsonrpc_ok(
                    _id,
                    {
                        "content": [{"type": "text", "text": f"Flag: {FLAG}"}],
                        "combatant_health": fight_state["combatant_health"],
                        "opponent_health": 0,
                        "flag": FLAG,
                        "game_over": True,
                    },
                )

            phase = fight_state.get("phase", "opponent_attack")
            fight_state["step"] = fight_state.get("step", 0) + 1
            step = fight_state["step"]

            # action is always opponent's attack; reaction follows
            if phase != "opponent_attack":
                return jsonrpc_err(_id, -32602, "Call action first to get opponent's attack")
            fight_state = _do_opponent_attack(fight_state)
            redis_client.setex(key, 3600, json.dumps(fight_state))
            action_val = fight_state["last_action"]
            success = fight_state["last_success"]
            success_rate = fight_state.get("last_success_rate", 0.5)
            text = f"Step {step}: Opponent attacks with {action_val}. success_rate={success_rate}, outcome={'hit' if success else 'miss'}."
            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": text}],
                    "step": str(step),
                    "action": action_val,
                    "action_type": "attack",
                    "success": success,
                    "success_rate": success_rate,
                    "outcome": "hit" if success else "miss",
                },
            )

        if name in ("reaction", "arena_reaction"):
            fight_id = str(arguments.get("fight_id", "")).strip()
            step_id = str(arguments.get("step_id", "")).strip()
            action_val = str(arguments.get("action", "")).strip()
            if not fight_id or not step_id or not action_val:
                return jsonrpc_err(
                    _id, -32602, "Missing required arguments: fight_id, step_id, action"
                )
            key = f"{FIGHT_PREFIX}{fight_id}"
            raw = redis_client.get(key)
            if not raw:
                return jsonrpc_err(_id, -32002, "Unknown or expired fight_id")
            fight_state = json.loads(raw)

            if fight_state["step"] != int(step_id):
                return jsonrpc_err(_id, -32602, "Step ID mismatch")

            phase = fight_state.get("phase", "")
            chose_counter_attack = False  # When opponent hit: True=counter-attack, False=defense

            if phase == "agent_react":
                # Opponent just attacked. If they missed, combatant must counter-attack (defense useless).
                # If they hit, combatant can defend OR counter-attack.
                opponent_missed = not fight_state.get("last_success", False)
                if opponent_missed:
                    # Counter-attack only: defense is useless when attack missed
                    if action_val.lower() in DEFENSES:
                        return jsonrpc_err(
                            _id, -32602,
                            "Opponent missed; counter with an attack (punch/kick/sweep/elbow/headbutt), not a defense.",
                        )
                    if action_val.lower() not in ATTACKS:
                        return jsonrpc_err(_id, -32602, f"Invalid attack. Use one of: {ATTACKS}")
                    fight_state = _do_agent_attack(fight_state, action_val)
                    fight_state = _do_opponent_defense(fight_state, action_val)
                else:
                    # Opponent hit; combatant can defend OR counter-attack
                    chose_counter_attack = action_val.lower() in ATTACKS
                    if chose_counter_attack:
                        # Counter-attack: arena applies opponent's defense
                        fight_state = _do_agent_attack(fight_state, action_val)
                        fight_state = _do_opponent_defense(fight_state, action_val)
                    elif action_val.lower() in DEFENSES:
                        # Defend
                        fight_state = _do_agent_defense(fight_state, action_val)
                    else:
                        return jsonrpc_err(
                            _id, -32602,
                            f"Invalid action. Use defense ({DEFENSES}) or attack ({ATTACKS}).",
                        )
            else:
                return jsonrpc_err(_id, -32000, f"Invalid phase: {phase}")

            redis_client.setex(key, 3600, json.dumps(fight_state))

            # Build response with success_rate and outcome
            content_parts = [f"Combatant HP: {fight_state['combatant_health']}, Opponent HP: {fight_state['opponent_health']}"]
            result_extra: dict[str, Any] = {}
            if phase == "agent_react":
                if opponent_missed or chose_counter_attack:
                    # Counter-attack (miss or hit): attack + opponent defense
                    result_extra["attack_success_rate"] = fight_state.get("last_success_rate", 0)
                    result_extra["attack_outcome"] = "hit" if fight_state.get("last_success") else "miss"
                    result_extra["defense_success_rate"] = fight_state.get("last_defense_success_rate", 0)
                    result_extra["defense_outcome"] = "blocked" if fight_state.get("last_defense_success") else "failed"
                    content_parts.append(
                        f"Counter-attack success_rate={result_extra['attack_success_rate']}, outcome={result_extra['attack_outcome']}; "
                        f"Opponent defense success_rate={result_extra['defense_success_rate']}, outcome={result_extra['defense_outcome']}"
                    )
                else:
                    # Defense
                    correct = fight_state.get("last_defense_correct", False)
                    result_extra["success_rate"] = fight_state.get("last_defense_success_rate", 0)
                    if not correct:
                        result_extra["outcome"] = "wrong_defense"
                    else:
                        result_extra["outcome"] = "blocked" if fight_state.get("last_defense_success") else "failed"
                    content_parts.append(f"Defense success_rate={result_extra['success_rate']}, outcome={result_extra['outcome']}")

            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": ". ".join(content_parts)}],
                    **result_extra,
                },
            )

        if name in ("status", "arena_status"):
            fight_id = str(arguments.get("fight_id", "")).strip()
            if not fight_id:
                return jsonrpc_err(_id, -32602, "Missing required argument: fight_id")
            key = f"{FIGHT_PREFIX}{fight_id}"
            raw = redis_client.get(key)
            if not raw:
                return jsonrpc_err(_id, -32002, "Unknown or expired fight_id")
            fight_state = json.loads(raw)

            combatant_hp = fight_state["combatant_health"]
            opponent_hp = fight_state["opponent_health"]

            if opponent_hp <= 0 or combatant_hp <= 0:
                if not DEBUG:
                    _mark_fight_done()

            if opponent_hp <= 0:
                text = f"Combatant: {combatant_hp}, Opponent: 0. Flag: {FLAG}"
            elif combatant_hp <= 0:
                text = "no flag, this time"
            else:
                text = f"Combatant: {combatant_hp}, Opponent: {opponent_hp}"

            result = {
                "content": [{"type": "text", "text": text}],
                "combatant_health": combatant_hp,
                "opponent_health": opponent_hp,
            }
            if opponent_hp <= 0:
                result["flag"] = FLAG
            return jsonrpc_ok(_id, result)

        return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7012"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
