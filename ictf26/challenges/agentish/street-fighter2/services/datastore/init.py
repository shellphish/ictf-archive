"""
Street Fighter 2 challenge datastore bootstrap.
Generates random combatant and opponent profiles for 2v2 combat.
- Two combatants, two opponents (each with own profile)
- Opponents: opponent_combo_vulnerability (opens them) + combatants use combatant_combo_attack
- Combatants: combatant_combo_vulnerability (opens us) + opponents use opponent_combo_attack
"""
import json
import os
import random
import time
from typing import Any

import redis  # type: ignore[import-not-found]


CONFIG_KEY = "sf:config"

ATTACKS = ["punch", "kick", "sweep", "elbow", "headbutt"]
DEFENSE_FOR_ATTACK = {
    "punch": "parry",
    "kick": "block",
    "sweep": "jump",
    "elbow": "sidestep",
    "headbutt": "brace",
}
DEFENSES = list(DEFENSE_FOR_ATTACK.values())

FIGHTER_NAMES = [
    "Shadow Viper",
    "Iron Fist",
    "Thunder Strike",
    "Crimson Blade",
    "Storm Rider",
    "Dark Phoenix",
    "Silver Wolf",
    "Frost Hammer",
]
FIGHTER_DESCRIPTIONS = [
    "A seasoned fighter with unpredictable moves.",
    "Known for lightning-fast kicks and powerful punches.",
    "Masters the art of close combat and evasion.",
    "Uses psychological warfare before striking.",
    "Relies on brute force and endurance.",
]


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


def _random_damage_distribution(total: int, attacks: list[str]) -> dict[str, int]:
    """Randomly distribute total damage across attacks, minimum 1 each."""
    damages = {a: 1 for a in attacks}
    remaining = total - len(attacks)
    for _ in range(max(0, remaining)):
        a = random.choice(attacks)
        damages[a] += 1
    return damages


def _random_success_rates(keys: list[str]) -> dict[str, float]:
    """Random success rates for each key."""
    return {k: round(random.uniform(0.2, 0.95), 2) for k in keys}


def generate_fighter_profile(
    total_damage: int,
    name: str,
    description: str,
) -> dict[str, Any]:
    """Generate a fighter profile with random damage and success rates."""
    damages = _random_damage_distribution(total_damage, ATTACKS)
    attack_rates = _random_success_rates(ATTACKS)
    defense_rates = _random_success_rates(DEFENSES)
    return {
        "attacks": {
            a: {"damage": damages[a], "success_rate": attack_rates[a]} for a in ATTACKS
        },
        "defenses": {d: {"success_rate": defense_rates[d]} for d in DEFENSES},
        "name": name,
        "description": description,
    }


def main() -> None:
    # Seed RNG: use INIT_SEED from host if set (guarantees different values per run),
    # otherwise fall back to os.urandom + time
    init_seed = os.environ.get("INIT_SEED")
    if init_seed:
        random.seed(int(init_seed, 16))
    else:
        random.seed(int.from_bytes(os.urandom(8), "big") ^ time.time_ns())

    redis_url = _env("REDIS_URL", "redis://127.0.0.1:6379/0")

    r = redis.Redis.from_url(redis_url, decode_responses=True)

    for _ in range(30):
        try:
            r.ping()
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError("Redis not reachable")

    combatant_total = int(_env("COMBATANT_TOTAL_DAMAGE", "10"))
    opponent_total = int(_env("OPPONENT_TOTAL_DAMAGE", "800"))

    # 1) Generate two combatant profiles and two opponent profiles
    names = random.sample(FIGHTER_NAMES, 4)
    descriptions = random.sample(FIGHTER_DESCRIPTIONS, 4)
    combatant_1 = generate_fighter_profile(combatant_total, names[0], descriptions[0])
    combatant_2 = generate_fighter_profile(combatant_total, names[1], descriptions[1])
    opponent_1 = generate_fighter_profile(opponent_total, names[2], descriptions[2])
    opponent_2 = generate_fighter_profile(opponent_total, names[3], descriptions[3])

    # 2) Opponent combos: opponent_combo_vulnerability (what they do) -> combatant_combo_attack (what we do for instant win)
    opponent_combo_vulnerability = [random.choice(ATTACKS), random.choice(ATTACKS)]
    combatant_combo_attack = [random.choice(ATTACKS), random.choice(ATTACKS)]

    # 3) Combatant combos: combatant_combo_vulnerability (what we do that opens us)
    #    -> opponent_combo_attack (what they do for instant win)
    combatant_combo_vulnerability = [random.choice(ATTACKS), random.choice(ATTACKS)]
    opponent_combo_attack = [random.choice(ATTACKS), random.choice(ATTACKS)]

    cfg = {
        "combatant_1_json": json.dumps(combatant_1),
        "combatant_2_json": json.dumps(combatant_2),
        "opponent_1_json": json.dumps(opponent_1),
        "opponent_2_json": json.dumps(opponent_2),
        "opponent_combo_vulnerability_json": json.dumps(opponent_combo_vulnerability),
        "combatant_combo_attack_json": json.dumps(combatant_combo_attack),
        "combatant_combo_vulnerability_json": json.dumps(combatant_combo_vulnerability),
        "opponent_combo_attack_json": json.dumps(opponent_combo_attack),
        "created_at": str(int(time.time())),
    }
    r.hset(CONFIG_KEY, mapping=cfg)

    print(
        f"[datastore] Stored config: combatants={combatant_1['name']!r}, {combatant_2['name']!r}; "
        f"opponents={opponent_1['name']!r}, {opponent_2['name']!r}"
    )
    print(
        f"[datastore] Opponent combo: vulnerability={opponent_combo_vulnerability}, combatant_attack={combatant_combo_attack}"
    )
    print(
        f"[datastore] Combatant combo: vulnerability={combatant_combo_vulnerability}, opponent_attack={opponent_combo_attack}"
    )


if __name__ == "__main__":
    main()
