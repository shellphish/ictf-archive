"""
Street Fighter challenge datastore bootstrap.
Generates random combatant and opponent profiles, stores in Redis.
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

OPPONENT_NAMES = [
    "Shadow Viper",
    "Iron Fist",
    "Thunder Strike",
    "Crimson Blade",
    "Storm Rider",
    "Dark Phoenix",
    "Silver Wolf",
    "Frost Hammer",
]
OPPONENT_DESCRIPTIONS = [
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


def generate_combatant_profile(
    efficacy_attack: str,
    strategy_attack: str,
    total_damage: int = 25,
) -> dict[str, Any]:
    """Generate combatant. 80% of damage budget goes to efficacy and strategy attacks, 20% to others."""
    other_attacks = [a for a in ATTACKS if a not in (efficacy_attack, strategy_attack)]
    budget_primary = int(0.8 * total_damage)
    budget_other = total_damage - budget_primary
    half = budget_primary // 2
    damages = {a: 1 for a in ATTACKS}
    damages[efficacy_attack] = half
    damages[strategy_attack] = budget_primary - half
    other_damages = _random_damage_distribution(budget_other, other_attacks)
    for a in other_attacks:
        damages[a] = other_damages[a]
    attack_rates = _random_success_rates(ATTACKS)
    defense_rates = _random_success_rates(DEFENSES)
    return {
        "attacks": {
            a: {"damage": damages[a], "success_rate": attack_rates[a]} for a in ATTACKS
        },
        "defenses": {d: {"success_rate": defense_rates[d]} for d in DEFENSES},
    }


def generate_opponent_profile(total_damage: int = 65) -> dict[str, Any]:
    """Generate opponent with random damage and success rates for all attacks and defenses."""
    damages = _random_damage_distribution(total_damage, ATTACKS)
    attack_rates = _random_success_rates(ATTACKS)
    defense_rates = _random_success_rates(DEFENSES)
    return {
        "attacks": {
            a: {"damage": damages[a], "success_rate": attack_rates[a]} for a in ATTACKS
        },
        "defenses": {d: {"success_rate": defense_rates[d]} for d in DEFENSES},
        "name": random.choice(OPPONENT_NAMES),
        "description": random.choice(OPPONENT_DESCRIPTIONS),
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

    combatant_total = int(_env("COMBATANT_TOTAL_DAMAGE", "25"))
    opponent_total = int(_env("OPPONENT_TOTAL_DAMAGE", "50"))

    # 1) Pick efficacy and strategy attacks, then generate profiles (80% damage to these two)
    efficacy_attack, strategy_attack = random.sample(ATTACKS, 2)
    combatant = generate_combatant_profile(efficacy_attack, strategy_attack, combatant_total)
    opponent = generate_opponent_profile(opponent_total)

    # 2) Ensure efficacy has higher product; swap labels if not
    eff_product = combatant["attacks"][efficacy_attack]["damage"] * combatant["attacks"][efficacy_attack]["success_rate"]
    strat_product = combatant["attacks"][strategy_attack]["damage"] * combatant["attacks"][strategy_attack]["success_rate"]
    if strat_product > eff_product:
        efficacy_attack, strategy_attack = strategy_attack, efficacy_attack

    # 3) Make efficacy product only 5% better than strategy product.
    #    First try raising strategy success rate; if capped at 0.99, reduce efficacy instead.
    efficacy_damage = combatant["attacks"][efficacy_attack]["damage"]
    efficacy_product = efficacy_damage * combatant["attacks"][efficacy_attack]["success_rate"]
    strategy_damage = combatant["attacks"][strategy_attack]["damage"]
    target_strategy_product = efficacy_product * 0.95
    required_strategy_success = target_strategy_product / strategy_damage
    if required_strategy_success <= 0.99:
        combatant["attacks"][strategy_attack]["success_rate"] = round(
            required_strategy_success, 2
        )
    else:
        # Strategy capped at 0.99; reduce efficacy so it's only 5% better
        combatant["attacks"][strategy_attack]["success_rate"] = 0.99
        strategy_product = strategy_damage * 0.99
        target_efficacy_product = strategy_product * 1.05
        required_efficacy_success = target_efficacy_product / efficacy_damage
        combatant["attacks"][efficacy_attack]["success_rate"] = round(
            min(0.99, required_efficacy_success), 2
        )

    # 4) Opponent defense for efficacy attack -> 0.99
    # 5) Opponent defense for strategy attack -> 0.01
    # 6) Other defenses -> random between 0.8 and 0.9
    efficacy_defense_name = DEFENSE_FOR_ATTACK[efficacy_attack]
    strategy_defense_name = DEFENSE_FOR_ATTACK[strategy_attack]
    opponent["defenses"][efficacy_defense_name]["success_rate"] = 0.99
    opponent["defenses"][strategy_defense_name]["success_rate"] = 0.01
    for def_name in DEFENSES:
        if def_name not in (efficacy_defense_name, strategy_defense_name):
            opponent["defenses"][def_name]["success_rate"] = round(
                random.uniform(0.90, 0.99), 2
            )

    cfg = {
        "combatant_json": json.dumps(combatant),
        "opponent_json": json.dumps(opponent),
        "created_at": str(int(time.time())),
    }
    r.hset(CONFIG_KEY, mapping=cfg)

    # Print efficacy/strategy differences (recompute after modifications)
    efficacy_product = (
        combatant["attacks"][efficacy_attack]["damage"]
        * combatant["attacks"][efficacy_attack]["success_rate"]
    )
    strategy_product = (
        combatant["attacks"][strategy_attack]["damage"]
        * combatant["attacks"][strategy_attack]["success_rate"]
    )
    efficacy_diff = efficacy_product - strategy_product
    strategy_val_efficacy = efficacy_product * (1 - 0.99)
    strategy_val_strategy = strategy_product * (1 - 0.01)
    strategy_diff = strategy_val_strategy - strategy_val_efficacy
    ratio = strategy_diff / efficacy_diff if efficacy_diff != 0 else float("nan")
    print(
        f"[datastore] Stored config in Redis key {CONFIG_KEY}: "
        f"opponent={opponent['name']!r}, efficacy={efficacy_attack}, strategy={strategy_attack}"
    )
    efficacy_ratio = strategy_product / efficacy_product if efficacy_product != 0 else float("nan")
    print(f"[datastore] EFFICACY DIFFERENCE: {efficacy_diff}")
    print(f"[datastore] EFFICACY RATIO (strategy_product / efficacy_product): {efficacy_ratio}")
    print(f"[datastore] STRATEGY DIFFERENCE: {strategy_diff}")
    print(f"[datastore] STRATEGY_DIFFERENCE / EFFICACY_DIFFERENCE: {ratio}")


if __name__ == "__main__":
    main()
