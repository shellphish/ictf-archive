import json
import os
import random
import time

import redis


CONFIG_KEY = "monitor:config"
TOTAL_ROUNDS = 3

SCENARIO_POOL = [
    {"program": "minio", "issue": "cpu-issue"},
    {"program": "minio", "issue": "memory-leak"},
    {"program": "minio", "issue": "normal"},
    {"program": "gogs", "issue": "cpu-issue"},
    {"program": "gogs", "issue": "memory-leak"},
    {"program": "gogs", "issue": "normal"},
    {"program": "pocketbase", "issue": "cpu-issue"},
    {"program": "pocketbase", "issue": "memory-leak"},
    {"program": "pocketbase", "issue": "normal"},
    {"program": "spring_petclinic", "issue": "cpu-issue"},
    {"program": "spring_petclinic", "issue": "memory-leak"},
    {"program": "spring_petclinic", "issue": "normal"},
    {"program": "tidb", "issue": "memory-leak"},
    {"program": "tidb", "issue": "normal"},
]


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


def main() -> None:
    redis_url = _env("REDIS_URL", "redis://127.0.0.1:6379/0")
    force_regen = _env("FORCE_REGEN", "0") == "1"

    r = redis.Redis.from_url(redis_url, decode_responses=True)

    for _ in range(30):
        try:
            r.ping()
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError("Redis not reachable")

    if not force_regen and r.exists(CONFIG_KEY):
        existing = r.hget(CONFIG_KEY, "scenario_1")
        print(f"[datastore] {CONFIG_KEY} already exists (scenario_1={existing}); skipping.")
        return

    abnormal = [s for s in SCENARIO_POOL if s["issue"] != "normal"]
    rounds = [random.choice(SCENARIO_POOL) for _ in range(TOTAL_ROUNDS)]
    if all(s["issue"] == "normal" for s in rounds):
        rounds[random.randrange(TOTAL_ROUNDS)] = random.choice(abnormal)

    mapping: dict[str, str] = {
        "total_rounds": str(TOTAL_ROUNDS),
        "current_round": "1",
        "current_program": rounds[0]["program"],
        "current_scenario": rounds[0]["issue"],
        "round_status": "starting",
        "created_at": str(int(time.time())),
    }
    for i, s in enumerate(rounds, 1):
        mapping[f"scenario_{i}"] = json.dumps(s)

    r.hset(CONFIG_KEY, mapping=mapping)
    r.set("monitor:restart", "0")

    summary = [f'{s["program"]}:{s["issue"]}' for s in rounds]
    print(f"[datastore] Generated {TOTAL_ROUNDS} rounds: {summary}")


if __name__ == "__main__":
    main()
