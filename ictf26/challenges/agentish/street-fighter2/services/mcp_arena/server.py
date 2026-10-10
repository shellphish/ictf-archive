"""
Street Fighter 2 MCP Arena server.
2v2 combat: combatant_a, combatant_b vs opponent_a, opponent_b.
Endpoints: fight, action, status, history (no reaction - use action with combatant+move when combatant's turn)
Each round: 4 moves in random order. Opponent moves chosen randomly. Combatant moves via action(combatant, action, target).
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

ATTACKS = ["punch", "kick", "sweep", "elbow", "headbutt"]
DEFENSES = ["parry", "block", "jump", "sidestep", "brace"]
DEFENSE_FOR_ATTACK = {
    "punch": "parry",
    "kick": "block",
    "sweep": "jump",
    "elbow": "sidestep",
    "headbutt": "brace",
}
VULNERABILITY_COMBO_PROB = 0.5  # Base prob for vulnerability combo
VULNERABILITY_COMBO_PROB_OPPONENTS_FIRST = 0.9  # High prob when opponents occupy first two slots of round
OPPONENT_DEFEND_PROB = 0.5  # When opponent has pending attack, prob they try to defend vs take damage and counter

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


app = FastAPI(title="mcp_arena", version="0.2.0")
redis_client = redis.Redis.from_url(
    _env("REDIS_URL", "redis://datastore:6379/0"), decode_responses=True
)
FLAG = os.environ.get("FLAG_CHALLENGE", "ictf{placeholder_flag}")
DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"ok": "true"}


def _mark_fight_done() -> None:
    redis_client.setex(ARENA_FIGHT_DONE_KEY, 86400, "1")


FIGHTER_IDS = ["combatant_a", "combatant_b", "opponent_a", "opponent_b"]

# Orderings where opponents occupy the first two slots (vulnerability combo opportunity)
OPPONENTS_FIRST_ORDERINGS = [
    ["opponent_a", "opponent_b", "combatant_a", "combatant_b"],
    ["opponent_a", "opponent_b", "combatant_b", "combatant_a"],
    ["opponent_b", "opponent_a", "combatant_a", "combatant_b"],
    ["opponent_b", "opponent_a", "combatant_b", "combatant_a"],
]


def _get_round_order(_round_num: int, fight_state: dict | None = None) -> list[str]:
    """Each round: random permutation of the four fighters.
    Probability of opponents being first two is inversely proportional to combatant health:
    when combatants are close to losing, opponents are more likely first (vulnerability combo opportunity).
    Use min 0.5 so combo occurs in most rounds even at full health."""
    if fight_state:
        ca = max(0, fight_state.get("combatant_a_health", INITIAL_HEALTH))
        cb = max(0, fight_state.get("combatant_b_health", INITIAL_HEALTH))
        total_combatant_health = ca + cb
        max_health = 2 * INITIAL_HEALTH
        health_ratio = total_combatant_health / max_health
        # prob_opponents_first: 1 when health=0, min 0.5 when health=200 (so combo in ~50% of rounds)
        prob_opponents_first = max(0.5, 1.0 - (health_ratio * health_ratio))
        if random.random() < prob_opponents_first:
            return random.choice(OPPONENTS_FIRST_ORDERINGS).copy()
    return random.sample(FIGHTER_IDS, 4)


def _opponents_first_two(round_order: list[str], turn_index: int) -> bool:
    """True if opponents occupy the first two slots and we're at slot 0 or 1."""
    first_two = set(round_order[:2])
    return first_two == {"opponent_a", "opponent_b"} and turn_index < 2


def _combatants_first_two(round_order: list[str], turn_index: int) -> bool:
    """True if combatants occupy the first two slots and we're at slot 0 or 1."""
    first_two = set(round_order[:2])
    return first_two == {"combatant_a", "combatant_b"} and turn_index < 2


def _do_opponent_move(
    fight_state: dict,
    fighter: str,
    turn_index: int,
    round_order: list[str],
) -> dict:
    """Opponent acts. If has pending attack: with OPPONENT_DEFEND_PROB try to defend, else take damage and counter.
    Otherwise: vulnerability combo, opponent_combo_attack (when combatants exposed), or normal attack."""
    config = fight_state["config"]
    opponent = config["opponent_1"] if fighter == "opponent_a" else config["opponent_2"]
    # Combo order: index 0 = first to act, index 1 = second (use turn_index when opponents first two)
    combo_move_index = turn_index if _opponents_first_two(round_order, turn_index) else (0 if fighter == "opponent_a" else 1)

    # If opponent has pending attack, decide: defend or take damage and counter.
    # When combatants are low health, reduce defend prob so opponents reach vulnerability combo.
    pending = _get_first_pending(fight_state.get("pending_attacks") or {}, fighter)
    if pending:
        total_ca = (
            fight_state.get("combatant_a_health", INITIAL_HEALTH)
            + fight_state.get("combatant_b_health", INITIAL_HEALTH)
        )
        health_ratio = total_ca / (2 * INITIAL_HEALTH)
        defend_prob = OPPONENT_DEFEND_PROB * health_ratio  # 0 when health=0, 0.5 when health=200
        try_defend = random.random() < defend_prob
        if try_defend:
            attack_type = pending["attack_type"]
            defense = DEFENSE_FOR_ATTACK.get(attack_type, "block")
            fight_state, resolution = _resolve_pending_attack(fight_state, fighter, defense)
            fight_state["history"].append({
                "fighter": fighter,
                "action": defense,
                "type": "opponent_defense",
                "attack_type": attack_type,
                "success": resolution.get("defense_blocked"),
                "damage": resolution.get("damage", 0),
            })
        else:
            fight_state, _ = _resolve_pending_attack(fight_state, fighter, None)
            # Fall through to do their counter-attack
        if try_defend:
            return fight_state

    combatant_vulnerability_exposed = fight_state.get("combatant_vulnerability_exposed", False)
    opponent_combo_progress = fight_state.get("opponent_combo_progress", 0)

    # When combatants exposed, opponents may do opponent_combo_attack for instant win (ordered: first does [0], second does [1])
    if combatant_vulnerability_exposed and opponent_combo_progress < 2:
        combo_attack = config["opponent_combo_attack"]
        move = combo_attack[opponent_combo_progress]
        opponent_combo_progress += 1
        fight_state["opponent_combo_progress"] = opponent_combo_progress
        fight_state["history"].append({
            "fighter": fighter,
            "action": move,
            "type": "opponent_combo_attack",
            "progress": opponent_combo_progress,
        })
        if opponent_combo_progress == 2:
            fight_state["combatant_a_health"] = 0
            fight_state["combatant_b_health"] = 0
            fight_state["combatant_vulnerability_exposed"] = False
            fight_state["opponent_combo_progress"] = 0
        return fight_state

    # Opponent vulnerability combo (opens them to our combatant_combo_attack)
    # Probability inversely proportional to combatant health: when combatants are near death,
    # prob → 1 so every round has combo. Use min 0.7 at full health for meaningful combo rate.
    do_vulnerability = False
    if _opponents_first_two(round_order, turn_index):
        total_combatant_health = (
            fight_state.get("combatant_a_health", INITIAL_HEALTH)
            + fight_state.get("combatant_b_health", INITIAL_HEALTH)
        )
        health_ratio = total_combatant_health / (2 * INITIAL_HEALTH)
        # prob = 1 when health=0, min 0.7 when health=200 (P(both)=0.49 at full health)
        vuln_combo_prob = max(0.7, 1.0 - health_ratio * (1.0 - VULNERABILITY_COMBO_PROB_OPPONENTS_FIRST))
        do_vulnerability = random.random() < vuln_combo_prob
    if do_vulnerability:
        combo_vuln = config["opponent_combo_vulnerability"]
        move = combo_vuln[combo_move_index]
        targets = [
            t for t in ("combatant_a", "combatant_b")
            if fight_state.get(f"{t}_health", INITIAL_HEALTH) > 0
        ]
        target = random.choice(targets) if targets else "combatant_a"
        fight_state["vulnerability_exposed"] = True
        fight_state["combo_progress"] = 0
        fight_state["history"].append({
            "fighter": fighter,
            "action": move,
            "type": "vulnerability_combo",
            "target": target,
        })
    else:
        # Pick target: combatant with health > 0 (random if both alive)
        targets = [
            t for t in ("combatant_a", "combatant_b")
            if fight_state.get(f"{t}_health", INITIAL_HEALTH) > 0
        ]
        target = random.choice(targets) if targets else "combatant_a"
        target_combatant = config["combatant_1"] if target == "combatant_a" else config["combatant_2"]
        attacks = opponent.get("attacks", {})
        move = random.choice(ATTACKS)
        attack_data = attacks.get(move, {"damage": 5, "success_rate": 0.5})
        attack_sr = attack_data["success_rate"]
        attack_hit = random.random() < attack_sr
        damage = attack_data["damage"]

        if not attack_hit:
            fight_state["history"].append({
                "fighter": fighter,
                "action": move,
                "type": "attack",
                "target": target,
                "attack_failed": True,
                "pending": False,
            })
        else:
            # Attack landed - defer resolution until target's turn (defense is a move)
            # Queue attacks per target so combatant must defend against each
            pending = fight_state.setdefault("pending_attacks", {})
            attack_entry = {"attacker": fighter, "attack_type": move, "damage": damage}
            lst = pending.get(target)
            if lst is None:
                pending[target] = [attack_entry]
            else:
                if isinstance(lst, dict):
                    pending[target] = [lst, attack_entry]
                else:
                    lst.append(attack_entry)
            fight_state["history"].append({
                "fighter": fighter,
                "action": move,
                "type": "attack",
                "target": target,
                "attack_failed": False,
                "pending": True,
                "damage": damage,
            })
    return fight_state


def _get_first_pending(pending_attacks: dict, fighter: str) -> dict | None:
    """Get first pending attack for fighter. pending_attacks[target] is a list (queue)."""
    lst = (pending_attacks or {}).get(fighter)
    if not lst:
        return None
    # Support legacy single-dict format for backward compat
    if isinstance(lst, dict):
        return lst
    return lst[0] if lst else None


def _resolve_pending_attack(
    fight_state: dict, fighter: str, defense: str | None
) -> tuple[dict, dict]:
    """Resolve the first pending attack against fighter. defense=None means no defense (take full damage).
    Returns (fight_state, resolution_info). Works for both combatants and opponents.
    pending_attacks[target] is a list; we resolve and remove the first."""
    pending_all = fight_state.get("pending_attacks") or {}
    lst = pending_all.get(fighter)
    if not lst:
        return fight_state, {}
    # Support legacy single-dict format
    if isinstance(lst, dict):
        pending = lst
        pending_all = {k: v for k, v in pending_all.items() if k != fighter}
    else:
        if not lst:
            return fight_state, {}
        pending = lst[0]
        new_lst = lst[1:]
        pending_all = dict(pending_all)
        pending_all[fighter] = new_lst
    fight_state["pending_attacks"] = pending_all

    attacker = pending["attacker"]
    attack_type = pending["attack_type"]
    damage = pending["damage"]
    config = fight_state["config"]
    if fighter in ("combatant_a", "combatant_b"):
        defender = config["combatant_1"] if fighter == "combatant_a" else config["combatant_2"]
    else:
        defender = config["opponent_1"] if fighter == "opponent_a" else config["opponent_2"]

    if defense is None:
        # Chose to attack instead of defend - take full damage
        actual_damage = damage
        success = False
        attack_failed = False
        defense_blocked = False
    else:
        def_name = defense.strip().lower()
        expected_def = DEFENSE_FOR_ATTACK.get(attack_type, "block")
        if def_name != expected_def:
            # Wrong defense - cannot block (0% success)
            actual_damage = damage
            success = False
            attack_failed = False
            defense_blocked = False
        else:
            def_data = defender.get("defenses", {}).get(def_name, {"success_rate": 0.5})
            defense_sr = def_data.get("success_rate", 0.5)
            defense_blocked = random.random() < defense_sr
            actual_damage = 0 if defense_blocked else damage
            success = defense_blocked
            attack_failed = False

    fight_state[f"{fighter}_health"] = max(
        0, fight_state.get(f"{fighter}_health", INITIAL_HEALTH) - actual_damage
    )

    # Update the history entry for this pending attack (match attacker + target + pending)
    for i in range(len(fight_state["history"])):
        h = fight_state["history"][i]
        if (
            h.get("type") == "attack"
            and h.get("target") == fighter
            and h.get("pending")
            and h.get("fighter") == attacker
        ):
            fight_state["history"][i] = {
                **h,
                "pending": False,
                "resolved": True,
                "success": success,
                "damage": actual_damage,
                "attack_failed": attack_failed,
                "defense_blocked": defense_blocked,
                "defense_used": defense,
            }
            break

    return fight_state, {
        "attacker": attacker,
        "attack_type": attack_type,
        "damage": actual_damage,
        "success": success,
        "attack_failed": attack_failed,
        "defense_blocked": defense_blocked,
    }


def _do_combatant_move(fight_state: dict, fighter: str, move: str, target: str) -> dict:
    """Combatant acts. If opponent vulnerability exposed, do combatant_combo_attack for instant win.
    If we do combatant_combo_vulnerability, we expose ourselves to opponent_combo_attack.
    Normal attack: target (opponent_a or opponent_b) determines which defense is used for success rate."""
    config = fight_state["config"]
    combatant = config["combatant_1"] if fighter == "combatant_a" else config["combatant_2"]
    move_lower = move.strip().lower()

    if move_lower not in ATTACKS:
        return fight_state  # Invalid, caller will error

    combo_progress = fight_state.get("combo_progress", 0)
    combatant_vuln_progress = fight_state.get("combatant_vuln_progress", 0)
    vulnerability_exposed = fight_state.get("vulnerability_exposed", False)
    combatant_combo_attack = config["combatant_combo_attack"]
    combatant_combo_vuln = config["combatant_combo_vulnerability"]

    # Opponent vulnerability exposed - check combo_attack FIRST so we don't misclassify
    # our winning combo as vulnerability when combatant_combo_attack == combatant_combo_vulnerability
    if vulnerability_exposed:
        expected = combatant_combo_attack[combo_progress]
        if move_lower == expected:
            combo_progress += 1
            fight_state["combo_progress"] = combo_progress
            fight_state["history"].append({
                "fighter": fighter,
                "action": move_lower,
                "type": "combo_attack",
                "progress": combo_progress,
            })
            if combo_progress == 2:
                fight_state["opponent_a_health"] = 0
                fight_state["opponent_b_health"] = 0
                fight_state["vulnerability_exposed"] = False
                fight_state["combo_progress"] = 0
            return fight_state
        else:
            fight_state["vulnerability_exposed"] = False
            fight_state["combo_progress"] = 0

    # Check if we're doing our vulnerability combo (opens us to opponent_combo_attack)
    expected_vuln = combatant_combo_vuln[combatant_vuln_progress]
    if move_lower == expected_vuln:
        combatant_vuln_progress = fight_state.get("combatant_vuln_progress", 0) + 1
        fight_state["combatant_vuln_progress"] = combatant_vuln_progress
        fight_state["history"].append({
            "fighter": fighter,
            "action": move_lower,
            "type": "combatant_vulnerability_combo",
            "progress": combatant_vuln_progress,
        })
        if combatant_vuln_progress == 2:
            fight_state["combatant_vulnerability_exposed"] = True
            fight_state["opponent_combo_progress"] = 0
            fight_state["combatant_vuln_progress"] = 0
        return fight_state
    else:
        fight_state["combatant_vuln_progress"] = 0  # Wrong move, reset

    # Normal attack on opponent: defer resolution until opponent's turn (defense is a move)
    target_opponent = config["opponent_1"] if target == "opponent_a" else config["opponent_2"]
    attacks = combatant.get("attacks", {})
    attack_data = attacks.get(move_lower, {"damage": 5, "success_rate": 0.5})
    attack_sr = attack_data["success_rate"]
    attack_hit = random.random() < attack_sr
    damage = attack_data["damage"]

    if not attack_hit:
        fight_state["history"].append({
            "fighter": fighter,
            "action": move_lower,
            "type": "attack",
            "target": target,
            "attack_failed": True,
            "pending": False,
        })
    else:
        # Queue attacks per target so opponent must defend against each
        pending = fight_state.setdefault("pending_attacks", {})
        attack_entry = {"attacker": fighter, "attack_type": move_lower, "damage": damage}
        lst = pending.get(target)
        if lst is None:
            pending[target] = [attack_entry]
        else:
            if isinstance(lst, dict):
                pending[target] = [lst, attack_entry]
            else:
                lst.append(attack_entry)
        fight_state["history"].append({
            "fighter": fighter,
            "action": move_lower,
            "type": "attack",
            "target": target,
            "attack_failed": False,
            "pending": True,
            "damage": damage,
        })
    return fight_state


def _fight() -> tuple[str | None, str | None]:
    if not DEBUG and redis_client.exists(ARENA_FIGHT_DONE_KEY):
        return None, "Only one fight allowed. A fight has already been completed."
    config = load_config(redis_client)
    if not config:
        return None, None

    fight_id = secrets.token_hex(8)
    # Initial round: full health, so prob_opponents_first = 0 (random order)
    initial_state = {
        "combatant_a_health": INITIAL_HEALTH,
        "combatant_b_health": INITIAL_HEALTH,
    }
    round_order = _get_round_order(1, initial_state)
    fight_state = {
        "combatant_a_health": INITIAL_HEALTH,
        "combatant_b_health": INITIAL_HEALTH,
        "opponent_a_health": INITIAL_HEALTH,
        "opponent_b_health": INITIAL_HEALTH,
        "round_number": 1,
        "turn_index": 0,
        "round_order": round_order,
        "current_turn": round_order[0],
        "pending_attacks": {},
        "vulnerability_exposed": False,
        "combo_progress": 0,
        "combatant_vulnerability_exposed": False,
        "opponent_combo_progress": 0,
        "combatant_vuln_progress": 0,
        "config": config,
        "history": [],
    }
    redis_client.setex(f"{FIGHT_PREFIX}{fight_id}", 3600, json.dumps(fight_state))
    return fight_id, None


def _advance_turn(fight_state: dict) -> None:
    turn_index = fight_state["turn_index"] + 1
    round_order = fight_state["round_order"]
    round_number = fight_state["round_number"]

    if turn_index >= 4:
        turn_index = 0
        round_number += 1
        round_order = _get_round_order(round_number, fight_state)

    fight_state["turn_index"] = turn_index
    fight_state["round_number"] = round_number
    fight_state["round_order"] = round_order
    fight_state["current_turn"] = round_order[turn_index]


TOOLS = [
    {
        "name": "fight",
        "description": "Start a 2v2 fight. Training is not required.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "fight_status",
        "description": "Get combatant and opponent health, and whose turn it is. Returns flag if opponent health is 0.",
        "inputSchema": {
            "type": "object",
            "properties": {"fight_id": {"type": "string"}},
            "required": ["fight_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "history",
        "description": "Get the last n moves in the fight. Pass n=0 to get all moves.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fight_id": {"type": "string"},
                "n": {"type": "integer", "description": "Number of recent moves (0 = all)"},
            },
            "required": ["fight_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "action",
        "description": "Opponent turn: call with fight_id only. Combatant turn: if pending_attack (from status), use defense (parry/block/jump/sidestep/brace) or action+target to attack (take damage). If no pending, use action+target.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fight_id": {"type": "string"},
                "combatant": {"type": "string", "description": "combatant_a or combatant_b (required when current_turn is combatant)"},
                "action": {"type": "string", "description": "attack: punch/kick/sweep/elbow/headbutt (when attacking)"},
                "target": {"type": "string", "description": "opponent_a or opponent_b (when attacking)"},
                "defense": {"type": "string", "description": "parry/block/jump/sidestep/brace (when defending pending attack)"},
            },
            "required": ["fight_id"],
            "additionalProperties": False,
        },
    },
]


def _serialize_fight_state(fight_state: dict) -> dict:
    """Create a JSON-serializable copy (config has nested dicts)."""
    state = {k: v for k, v in fight_state.items() if k != "config"}
    return state


def _deserialize_fight_state(raw: dict, config: dict) -> dict:
    raw["config"] = config
    return raw


@app.post("/rpc")
def rpc(req: JsonRpcReq) -> JSONResponse:
    _id = req.get("id")
    method = req.get("method", "")
    params = req.get("params") or {}

    if method == "initialize":
        return jsonrpc_ok(
            _id,
            {
                "serverInfo": {"name": "mcp_arena", "version": "0.2.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}

        if name == "fight":
            fight_id, err = _fight()
            if err:
                return jsonrpc_err(_id, -32002, err)
            if fight_id is None:
                return jsonrpc_err(
                    _id, -32002, "Could not start fight. Config may be missing."
                )
            return jsonrpc_ok(
                _id,
                {
                    "content": [{"type": "text", "text": f"Fight started. fight_id={fight_id}"}],
                    "fight_id": fight_id,
                },
            )

        if name == "fight_status":
            fight_id = str(arguments.get("fight_id", "")).strip()
            if not fight_id:
                return jsonrpc_err(_id, -32602, "Missing required argument: fight_id")
            key = f"{FIGHT_PREFIX}{fight_id}"
            raw = redis_client.get(key)
            if not raw:
                return jsonrpc_err(_id, -32002, "Unknown or expired fight_id")
            fight_state = json.loads(raw)
            config = load_config(redis_client)
            if config:
                fight_state["config"] = config

            ca = fight_state.get("combatant_a_health", INITIAL_HEALTH)
            cb = fight_state.get("combatant_b_health", INITIAL_HEALTH)
            oa = fight_state.get("opponent_a_health", INITIAL_HEALTH)
            ob = fight_state.get("opponent_b_health", INITIAL_HEALTH)
            current_turn = fight_state.get("current_turn", "opponent_a")
            turn_index = fight_state.get("turn_index", 0)
            round_number = fight_state.get("round_number", 1)

            both_opponents_down = oa <= 0 and ob <= 0
            both_combatants_down = ca <= 0 and cb <= 0

            if both_opponents_down or both_combatants_down:
                if not DEBUG:
                    _mark_fight_done()

            if both_opponents_down:
                text = f"Combatant_a: {ca}, Combatant_b: {cb}. Opponents: 0. Flag: {FLAG}"
            elif both_combatants_down:
                text = "Both combatants down. No flag, this time."
            else:
                text = f"Combatant_a: {ca}, Combatant_b: {cb} | Opponent_a: {oa}, Opponent_b: {ob}. Round {round_number} move {turn_index + 1}/4: {current_turn}"

            result: dict[str, Any] = {
                "content": [{"type": "text", "text": text}],
                "combatant_a_health": ca,
                "combatant_b_health": cb,
                "opponent_a_health": oa,
                "opponent_b_health": ob,
                "current_turn": current_turn,
                "round_number": round_number,
                "turn_index": turn_index,
            }
            # Expose pending attack for combatant (first in queue)
            if current_turn in ("combatant_a", "combatant_b"):
                pa = _get_first_pending(fight_state.get("pending_attacks") or {}, current_turn)
                if pa:
                    result["pending_attack"] = {
                        "attacker": pa["attacker"],
                        "attack_type": pa["attack_type"],
                        "damage": pa["damage"],
                    }
            if both_opponents_down:
                result["flag"] = FLAG
                result["game_over"] = True
            elif both_combatants_down:
                result["game_over"] = True
            return jsonrpc_ok(_id, result)

        if name == "history":
            fight_id = str(arguments.get("fight_id", "")).strip()
            if not fight_id:
                return jsonrpc_err(_id, -32602, "Missing required argument: fight_id")
            n = int(arguments.get("n", 10))
            key = f"{FIGHT_PREFIX}{fight_id}"
            raw = redis_client.get(key)
            if not raw:
                return jsonrpc_err(_id, -32002, "Unknown or expired fight_id")
            fight_state = json.loads(raw)
            history = fight_state.get("history", [])
            if n == 0:
                moves = history
            else:
                moves = history[-n:]
            text = "\n".join(
                f"{m.get('fighter', '?')}: {m.get('action', '?')} ({m.get('type', '?')})"
                for m in moves
            ) or "No moves yet."
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": text}], "history": moves},
            )

        if name == "action":
            fight_id = str(arguments.get("fight_id", "")).strip()
            if not fight_id:
                return jsonrpc_err(_id, -32602, "Missing required argument: fight_id")
            key = f"{FIGHT_PREFIX}{fight_id}"
            raw = redis_client.get(key)
            if not raw:
                return jsonrpc_err(_id, -32002, "Unknown or expired fight_id")
            fight_state = json.loads(raw)
            config = load_config(redis_client)
            if not config:
                return jsonrpc_err(_id, -32001, "Challenge not initialized")
            fight_state["config"] = config

            ca = fight_state.get("combatant_a_health", INITIAL_HEALTH)
            cb = fight_state.get("combatant_b_health", INITIAL_HEALTH)
            oa = fight_state.get("opponent_a_health", INITIAL_HEALTH)
            ob = fight_state.get("opponent_b_health", INITIAL_HEALTH)
            both_combatants_down = ca <= 0 and cb <= 0
            both_opponents_down = oa <= 0 and ob <= 0

            if both_combatants_down:
                if not DEBUG:
                    _mark_fight_done()
                return jsonrpc_ok(
                    _id,
                    {
                        "content": [{"type": "text", "text": "Both combatants down. No flag, this time."}],
                        "combatant_a_health": ca,
                        "combatant_b_health": cb,
                        "opponent_a_health": oa,
                        "opponent_b_health": ob,
                        "game_over": True,
                    },
                )

            if both_opponents_down:
                if not DEBUG:
                    _mark_fight_done()
                return jsonrpc_ok(
                    _id,
                    {
                        "content": [{"type": "text", "text": f"Flag: {FLAG}"}],
                        "combatant_a_health": ca,
                        "combatant_b_health": cb,
                        "opponent_a_health": 0,
                        "opponent_b_health": 0,
                        "flag": FLAG,
                        "game_over": True,
                    },
                )

            current_turn = fight_state["current_turn"]
            turn_index = fight_state["turn_index"]
            round_order = fight_state["round_order"]

            combatant_arg = str(arguments.get("combatant", "")).strip().lower()
            action_arg = str(arguments.get("action", "")).strip().lower()
            target_arg = str(arguments.get("target", "")).strip().lower()

            if current_turn in ("combatant_a", "combatant_b"):
                if not combatant_arg or combatant_arg != current_turn:
                    return jsonrpc_err(
                        _id, -32602,
                        f"Wrong combatant. It is {current_turn}'s turn.",
                    )
                defense_arg = str(arguments.get("defense", "")).strip().lower()
                has_pending = _get_first_pending(fight_state.get("pending_attacks") or {}, current_turn)

                if has_pending:
                    # Can choose defense (resolve pending) or attack (take damage, then attack)
                    if defense_arg and defense_arg in DEFENSES:
                        # Defend: resolve pending with chosen defense
                        fight_state, resolution = _resolve_pending_attack(
                            fight_state, current_turn, defense_arg
                        )
                        _advance_turn(fight_state)
                        redis_client.setex(key, 3600, json.dumps(_serialize_fight_state(fight_state)))
                        oa = fight_state.get("opponent_a_health", INITIAL_HEALTH)
                        ob = fight_state.get("opponent_b_health", INITIAL_HEALTH)
                        res = resolution
                        if res.get("defense_blocked"):
                            text = f"{current_turn} defended {res.get('attack_type', '?')} with {defense_arg}. Defense BLOCKED."
                        else:
                            text = f"{current_turn} defended {res.get('attack_type', '?')} with {defense_arg}. Defense FAILED (took {res.get('damage', 0)} damage)."
                        combatant_result = {
                            "content": [{"type": "text", "text": text}],
                            "current_turn": fight_state["current_turn"],
                            "fighter": current_turn,
                            "action_type": "defense",
                            "defense": defense_arg,
                            "attack_type": res.get("attack_type"),
                            "success": res.get("defense_blocked"),
                            "damage": res.get("damage", 0),
                            "combatant_a_health": fight_state.get("combatant_a_health", INITIAL_HEALTH),
                            "combatant_b_health": fight_state.get("combatant_b_health", INITIAL_HEALTH),
                            "opponent_a_health": oa,
                            "opponent_b_health": ob,
                        }
                        if combatant_result["combatant_a_health"] <= 0 and combatant_result["combatant_b_health"] <= 0:
                            if not DEBUG:
                                _mark_fight_done()
                            combatant_result["game_over"] = True
                        return jsonrpc_ok(_id, combatant_result)
                    elif action_arg and target_arg:
                        # Attack: take full damage from ALL pending, then attack
                        total_dmg = 0
                        while _get_first_pending(fight_state.get("pending_attacks") or {}, current_turn):
                            fight_state, resolution = _resolve_pending_attack(
                                fight_state, current_turn, None
                            )
                            total_dmg += resolution.get("damage", 0)
                        if target_arg not in ("opponent_a", "opponent_b"):
                            return jsonrpc_err(_id, -32602, "Target must be opponent_a or opponent_b")
                        if action_arg not in ATTACKS:
                            return jsonrpc_err(_id, -32602, f"Invalid attack. Use one of: {ATTACKS}")
                        fight_state = _do_combatant_move(fight_state, current_turn, action_arg, target_arg)
                        _advance_turn(fight_state)
                        redis_client.setex(key, 3600, json.dumps(_serialize_fight_state(fight_state)))
                        last_move = fight_state["history"][-1] if fight_state["history"] else {}
                        oa = fight_state.get("opponent_a_health", INITIAL_HEALTH)
                        ob = fight_state.get("opponent_b_health", INITIAL_HEALTH)
                        text = f"{current_turn} took {total_dmg} damage (no defense), then attacked {target_arg} with {action_arg}. "
                        move_type = last_move.get("type", "attack")
                        if move_type == "combo_attack":
                            text += f"Combo progress: {last_move.get('progress', 0)}/2"
                        else:
                            if last_move.get("success"):
                                text += f"Attack HIT, damage={last_move.get('damage', 0)}"
                            elif last_move.get("attack_failed"):
                                text += f"Attack FAILED (success rate missed)"
                            else:
                                text += f"Defense BLOCKED (defender parried), damage=0"
                        combatant_result = {
                            "content": [{"type": "text", "text": text}],
                            "current_turn": fight_state["current_turn"],
                            "fighter": current_turn,
                            "action": action_arg,
                            "action_type": move_type,
                            "target": target_arg,
                            "combatant_a_health": fight_state.get("combatant_a_health", INITIAL_HEALTH),
                            "combatant_b_health": fight_state.get("combatant_b_health", INITIAL_HEALTH),
                            "opponent_a_health": oa,
                            "opponent_b_health": ob,
                            "success": last_move.get("success"),
                            "damage": last_move.get("damage", 0),
                            "attack_failed": last_move.get("attack_failed", False),
                            "defense_blocked": last_move.get("defense_blocked", False),
                        }
                        if oa <= 0 and ob <= 0:
                            if not DEBUG:
                                _mark_fight_done()
                            combatant_result["flag"] = FLAG
                            combatant_result["game_over"] = True
                        return jsonrpc_ok(_id, combatant_result)
                    else:
                        return jsonrpc_err(
                            _id, -32602,
                            f"{current_turn} has a pending attack. Provide defense (parry/block/jump/sidestep/brace) or action+target to attack (take damage).",
                        )
                else:
                    # No pending: can defend (waste) or attack
                    if defense_arg and defense_arg in DEFENSES:
                        # Defend with nothing to defend against - waste, but allowed
                        _advance_turn(fight_state)
                        redis_client.setex(key, 3600, json.dumps(_serialize_fight_state(fight_state)))
                        return jsonrpc_ok(_id, {
                            "content": [{"type": "text", "text": f"{current_turn} defended (no attack pending - waste)."}],
                            "current_turn": fight_state["current_turn"],
                            "fighter": current_turn,
                            "action_type": "defense",
                            "defense": defense_arg,
                            "combatant_a_health": fight_state.get("combatant_a_health", INITIAL_HEALTH),
                            "combatant_b_health": fight_state.get("combatant_b_health", INITIAL_HEALTH),
                            "opponent_a_health": fight_state.get("opponent_a_health", INITIAL_HEALTH),
                            "opponent_b_health": fight_state.get("opponent_b_health", INITIAL_HEALTH),
                        })
                    if not action_arg or not target_arg:
                        return jsonrpc_err(
                            _id, -32602,
                            f"It is {current_turn}'s turn. Call action with combatant, action, and target (or defense for waste).",
                        )
                    if target_arg not in ("opponent_a", "opponent_b"):
                        return jsonrpc_err(_id, -32602, "Target must be opponent_a or opponent_b")
                    if action_arg not in ATTACKS:
                        return jsonrpc_err(_id, -32602, f"Invalid attack. Use one of: {ATTACKS}")

                    fight_state = _do_combatant_move(fight_state, current_turn, action_arg, target_arg)
                    _advance_turn(fight_state)
                    redis_client.setex(key, 3600, json.dumps(_serialize_fight_state(fight_state)))

                    last_move = fight_state["history"][-1] if fight_state["history"] else {}
                    move_type = last_move.get("type", "attack")
                    text = f"{current_turn} did {action_arg} -> {target_arg}. "
                    oa = fight_state.get("opponent_a_health", INITIAL_HEALTH)
                    ob = fight_state.get("opponent_b_health", INITIAL_HEALTH)
                    if move_type == "combo_attack":
                        if oa <= 0 and ob <= 0:
                            text += "Combo complete! Instant win!"
                        else:
                            text += f"Combo progress: {last_move.get('progress', 0)}/2"
                    else:
                        if last_move.get("attack_failed"):
                            text += "Attack FAILED (success rate missed). "
                        elif last_move.get("pending"):
                            text += "Attack landed (pending target's defense). "
                        else:
                            if last_move.get("success") or last_move.get("defense_blocked"):
                                text += "Defense BLOCKED (defender parried). "
                            else:
                                text += "Attack HIT (defense failed). "
                        text += f"Damage: {last_move.get('damage', 0)}"

                    combatant_result = {
                        "content": [{"type": "text", "text": text}],
                        "current_turn": fight_state["current_turn"],
                        "fighter": current_turn,
                        "action": action_arg,
                        "action_type": move_type,
                        "combatant_a_health": fight_state.get("combatant_a_health", INITIAL_HEALTH),
                        "combatant_b_health": fight_state.get("combatant_b_health", INITIAL_HEALTH),
                        "opponent_a_health": oa,
                        "opponent_b_health": ob,
                    }
                    if move_type in ("attack", "combo_attack", "combatant_vulnerability_combo"):
                        combatant_result["target"] = target_arg
                    if move_type == "attack":
                        combatant_result["success"] = last_move.get("success")
                        combatant_result["damage"] = last_move.get("damage", 0)
                        combatant_result["attack_failed"] = last_move.get("attack_failed", False)
                        combatant_result["defense_blocked"] = last_move.get("defense_blocked", False)
                        combatant_result["pending"] = last_move.get("pending", False)
                    if oa <= 0 and ob <= 0:
                        if not DEBUG:
                            _mark_fight_done()
                        combatant_result["flag"] = FLAG
                        combatant_result["game_over"] = True
                    return jsonrpc_ok(_id, combatant_result)

            # Opponent's turn: must NOT provide combatant (arena chooses move)
            if combatant_arg:
                return jsonrpc_err(
                    _id, -32602,
                    f"It is {current_turn}'s turn (opponent). Call action with fight_id only - no combatant/action/target.",
                )

            # Opponent's turn
            fight_state = _do_opponent_move(
                fight_state, current_turn, turn_index, round_order
            )
            last_move = fight_state["history"][-1] if fight_state["history"] else {}
            _advance_turn(fight_state)
            redis_client.setex(key, 3600, json.dumps(_serialize_fight_state(fight_state)))

            move_type = last_move.get("type", "attack")
            text = f"{current_turn} did {last_move.get('action', '?')} ({move_type})"
            result_data: dict[str, Any] = {
                "content": [{"type": "text", "text": text}],
                "current_turn": fight_state["current_turn"],
                "fighter": current_turn,
                "action": last_move.get("action"),
                "action_type": move_type,
                "your_turn": False,
            }
            if move_type == "opponent_defense":
                atk = last_move.get("attack_type", "?")
                if last_move.get("success"):
                    text += f" vs {atk}. Defense BLOCKED."
                else:
                    text += f" vs {atk}. Defense FAILED, damage={last_move.get('damage', 0)}"
                result_data["attack_type"] = atk
                result_data["success"] = last_move.get("success")
                result_data["damage"] = last_move.get("damage", 0)
            elif move_type == "attack":
                tgt = last_move.get("target", "?")
                if last_move.get("attack_failed"):
                    text += f" -> {tgt}. Attack FAILED (success rate missed)."
                    result_data["target"] = tgt
                    result_data["attack_failed"] = True
                elif last_move.get("pending"):
                    text += f" -> {tgt}. Attack landed (pending target's defense on their turn)."
                    result_data["target"] = tgt
                    result_data["pending"] = True
                    result_data["damage"] = last_move.get("damage", 0)
                # else: resolved (shouldn't happen for opponent - we defer)
            elif move_type == "vulnerability_combo":
                tgt = last_move.get("target", "?")
                text += f" -> {tgt}"
                result_data["target"] = tgt
            result_data["content"] = [{"type": "text", "text": text}]
            return jsonrpc_ok(_id, result_data)

        return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7012"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
