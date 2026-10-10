import json
import os
import time
from dataclasses import dataclass
from typing import Any

import redis  # type: ignore[import-not-found]
import litellm  # type: ignore[import-not-found]


CONFIG_KEY = "waldo:config"  # Redis hash


@dataclass(frozen=True)
class WaldoConfig:
    city: str
    state: str
    landmarks: list[str]

    def to_redis_hash(self) -> dict[str, str]:
        return {
            "city": self.city,
            "state": self.state,
            "landmarks_json": json.dumps(self.landmarks),
            "created_at": str(int(time.time())),
        }


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


def _bool_env(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


def _short(s: str, max_len: int = 500) -> str:
    s = s.replace("\n", "\\n")
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def parse_config_json(text: str) -> WaldoConfig:
    obj = json.loads(text)
    city = str(obj["city"]).strip()
    state = str(obj["state"]).strip()
    landmarks_raw = obj["landmarks"]
    if not isinstance(landmarks_raw, list):
        raise ValueError("landmarks must be a list")
    landmarks = [str(x).strip() for x in landmarks_raw if str(x).strip()]
    if len(landmarks) < 3:
        raise ValueError("need at least 3 landmarks")
    landmarks = landmarks[:3]
    if not city or not state:
        raise ValueError("city/state cannot be empty")
    return WaldoConfig(city=city, state=state, landmarks=landmarks)


def generate_config_via_llm() -> WaldoConfig:
    base_url = _env("LITELLM_BASE_URL", "http://litellm:4000")
    # Important: datastore/bootstrap uses the *challenge* LiteLLM key (not the team key).
    api_key = _env("CHALLENGE_LITELLM_API_KEY")
    # Prefer CHALLENGE_LITELLM_MODEL; keep LITELLM_MODEL as backward-compatible fallback.
    model = os.environ.get("CHALLENGE_LITELLM_MODEL") or _env("LITELLM_MODEL", "gpt-4o-mini")
    debug = _bool_env("DATASTORE_DEBUG_LITELLM", False)

    system = (
        "You generate the configuration for a CTF challenge.\n"
        "Return STRICT JSON with keys: city (string), landmarks (array of 3 strings), state (string).\n"
        "Constraints:\n"
        "- City must be a city in the United States.\n"
        "- Landmarks must be real and located in that city.\n"
        "- State must be the US state the city is in (full state name, not abbreviation).\n"
        "- Do not include any extra keys."
    )

    user = "Pick one city and 3 landmarks."
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]

    print(f"[datastore] LiteLLM request: api_base={base_url.rstrip('/')!r} model={model!r} temperature=0.0")
    if debug:
        print(f"[datastore] LiteLLM request messages: {messages!r}")

    try:
        resp = litellm.completion(
            model=model,
            messages=messages,
            temperature=0.0,
            api_base=base_url.rstrip("/"),
            api_key=api_key,
            timeout=45.0,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        print(f"[datastore] LiteLLM request failed: {e!r}")
        raise

    # Best-effort response logging without assuming a specific response type.
    if debug:
        if isinstance(resp, dict):
            print(f"[datastore] LiteLLM raw response (dict): {_short(json.dumps(resp, ensure_ascii=False))}")
        elif hasattr(resp, "model_dump"):
            try:
                print(
                    f"[datastore] LiteLLM raw response (model_dump): "
                    f"{_short(json.dumps(resp.model_dump(), ensure_ascii=False))}"  # type: ignore[attr-defined]
                )
            except Exception:
                print(f"[datastore] LiteLLM raw response (repr): {_short(repr(resp))}")
        else:
            print(f"[datastore] LiteLLM raw response (repr): {_short(repr(resp))}")

    content = resp.choices[0].message["content"]
    print(f"[datastore] LiteLLM response content: {_short(str(content), 800)}")
    return parse_config_json(content)


def main() -> None:
    redis_url = _env("REDIS_URL", "redis://127.0.0.1:6379/0")
    force_regen = _env("FORCE_REGEN", "0") == "1"

    r = redis.Redis.from_url(redis_url, decode_responses=True)

    # Give Redis a moment on cold start (avoid hard dependency on healthchecks).
    for _ in range(30):
        try:
            r.ping()
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError("Redis not reachable")

    if not force_regen and r.exists(CONFIG_KEY):
        print(f"[datastore] {CONFIG_KEY} already exists; skipping (FORCE_REGEN=0).")
        return

    cfg = generate_config_via_llm()
    print("[datastore] Generated config via LiteLLM.")

    r.hset(CONFIG_KEY, mapping=cfg.to_redis_hash())
    print(f"[datastore] Stored config in Redis key {CONFIG_KEY}: city={cfg.city!r}, state={cfg.state!r}")


if __name__ == "__main__":
    main()

