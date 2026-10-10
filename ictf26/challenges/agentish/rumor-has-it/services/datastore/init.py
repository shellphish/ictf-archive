import json
import os
import time
from dataclasses import dataclass
from typing import Any

import redis  # type: ignore[import-not-found]
import litellm  # type: ignore[import-not-found]


GOSSIP_KEY = "rumor:gossip:1"  # Redis string (JSON)


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


def _short(s: str, max_len: int = 700) -> str:
    s = s.replace("\n", "\\n")
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


@dataclass(frozen=True)
class Gossip:
    gossip_id: int
    sources: list[str]  # ordered chain
    true_ioc: str
    messages: list[dict[str, Any]]  # ordered; each has source, iocs, next_source, message
    created_at: int

    def to_json(self) -> str:
        return json.dumps(
            {
                "gossip_id": self.gossip_id,
                "sources": self.sources,
                "true_ioc": self.true_ioc,
                "messages": self.messages,
                "created_at": self.created_at,
            },
            ensure_ascii=False,
        )


def _validate_emailish(s: str) -> str:
    s = str(s).strip()
    if "@" not in s or "." not in s.split("@", 1)[-1]:
        raise ValueError(f"Invalid email address: {s!r}")
    return s


def parse_gossip_json(text: str) -> Gossip:
    obj = json.loads(text)
    gossip_id = int(obj.get("gossip_id", 1))
    sources_raw = obj["sources"]
    if not isinstance(sources_raw, list) or len(sources_raw) < 3:
        raise ValueError("sources must be a list with >= 3 entries")
    sources = [_validate_emailish(x) for x in sources_raw]
    if len(set(sources)) != len(sources):
        raise ValueError("sources must be unique")

    true_ioc = str(obj["true_ioc"]).strip()
    if not true_ioc:
        raise ValueError("true_ioc cannot be empty")

    messages_raw = obj["messages"]
    if not isinstance(messages_raw, list) or len(messages_raw) != len(sources):
        raise ValueError("messages must be a list with the same length as sources")

    messages: list[dict[str, Any]] = []
    for i, m in enumerate(messages_raw):
        if not isinstance(m, dict):
            raise ValueError("each message must be an object")
        source = _validate_emailish(m.get("source", ""))
        if source != sources[i]:
            raise ValueError("messages must be ordered and aligned with sources")
        iocs = m.get("iocs")
        if not isinstance(iocs, list) or len(iocs) < 3:
            raise ValueError("each message must include iocs (list) with >= 3 entries")
        iocs_s = [str(x).strip() for x in iocs if str(x).strip()]
        if true_ioc not in iocs_s:
            raise ValueError("each message must include true_ioc in iocs")
        msg_text = str(m.get("message", "")).strip()
        if not msg_text:
            raise ValueError("each message must include non-empty message text")
        for ioc in iocs_s:
            if ioc not in msg_text:
                raise ValueError("each message text must mention each IoC verbatim")
        next_source = m.get("next_source")
        if i < len(sources) - 1:
            ns = _validate_emailish(next_source)
            if ns != sources[i + 1]:
                raise ValueError("next_source must point to the next source in chain")
            if ns not in msg_text:
                raise ValueError("each message text must mention next_source email verbatim")
        else:
            # final message may omit next_source or set it to null/empty
            next_source = None

        messages.append(
            {
                "source": source,
                "iocs": iocs_s,
                "message": msg_text,
                "next_source": next_source,
            }
        )

    # Enforce that ONLY true_ioc is common to all messages (red herrings must vary).
    ioc_sets = [set(m["iocs"]) for m in messages]
    common = set.intersection(*ioc_sets) if ioc_sets else set()
    if common != {true_ioc}:
        raise ValueError("expected exactly one common IoC across all messages (true_ioc)")

    return Gossip(
        gossip_id=gossip_id,
        sources=sources,
        true_ioc=true_ioc,
        messages=messages,
        created_at=int(time.time()),
    )


def generate_gossip_via_llm() -> Gossip:
    base_url = _env("LITELLM_BASE_URL", "http://litellm:4000")
    api_key = _env("CHALLENGE_LITELLM_API_KEY")
    model = os.environ.get("CHALLENGE_LITELLM_MODEL") or _env("LITELLM_MODEL", "gpt-4o-mini")
    debug = _bool_env("DATASTORE_DEBUG_LITELLM", False)

    system = (
        "You generate configuration JSON for a CTF challenge.\n"
        "Return STRICT JSON with keys: gossip_id (int), sources (array of unique emails), true_ioc (string), "
        "messages (array of objects).\n"
        "Each messages[i] object MUST have keys: source (email), iocs (array of exactly 3 strings), "
        "message (string), next_source (email or null).\n"
        "Constraints:\n"
        "- sources length must be between 4 and 6.\n"
        "- messages length must equal sources length.\n"
        "- messages must be ordered and aligned: messages[i].source == sources[i].\n"
        "- For i < last, messages[i].next_source MUST equal sources[i+1]. For the last message, next_source MUST be null.\n"
        "- The true_ioc MUST appear in the iocs list of EVERY message.\n"
        "- Each iocs list must be EXACTLY 3 entries: [true_ioc, red_herring_1, red_herring_2].\n"
        "- CRITICAL: ONLY true_ioc should be common across ALL messages.\n"
        "- CRITICAL: red_herring_1 and red_herring_2 MUST vary by message and MUST NOT repeat across messages.\n"
        "- IoCs can be IPs, domains, URLs, or SHA-256 hashes. Mix types if you want.\n"
        "- The message string must be a bit longer (at least 3 sentences) and must embed all 3 IoCs verbatim IN PROSE.\n"
        "- Do NOT include an explicit list of IoCs (no bullets, no 'IoCs:' section). The IoCs should be naturally embedded.\n"
        "- The message MUST mention the next_source email verbatim (except last, where it should clearly indicate there is no next source).\n"
        "- Tip: end each non-final message with a sentence like: 'If you have more context, contact <next_source_email>.'\n"
        "- CRITICAL: each message MUST contain the exact substrings in messages[i].iocs inside messages[i].message.\n"
        "- CRITICAL: do NOT omit the URL/host/hash variants; include them exactly as written in the iocs array.\n"
        "- To ensure compliance, include a normal prose sentence like:\n"
        '  "In telemetry we observed <ioc1>, <ioc2>, and <ioc3>." (replace with the exact strings from the iocs array)\n'
        "- Do not include any extra keys."
    )
    base_user = "Generate one gossip chain about a single security compromise."

    last_err: Exception | None = None
    for attempt in range(1, 5):
        user = base_user
        if last_err is not None:
            user += (
                "\n\nYour previous output failed validation with this error:\n"
                f"{last_err!r}\n\nRegenerate from scratch and follow ALL constraints exactly."
            )

        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]

        print(
            f"[datastore] LiteLLM request: api_base={base_url.rstrip('/')!r} model={model!r} temperature=0.0 attempt={attempt}"
        )
        if debug:
            print(f"[datastore] LiteLLM request messages: {messages!r}")

        resp = litellm.completion(
            model=model,
            messages=messages,
            temperature=0.0,
            api_base=base_url.rstrip("/"),
            api_key=api_key,
            timeout=60.0,
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message["content"]
        print(f"[datastore] LiteLLM response content: {_short(str(content), 1200)}")

        try:
            return parse_gossip_json(content)
        except Exception as e:
            last_err = e
            print(f"[datastore] Gossip JSON validation failed attempt={attempt}: {e!r}")
            continue

    assert last_err is not None
    raise last_err


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

    if not force_regen and r.exists(GOSSIP_KEY):
        print(f"[datastore] {GOSSIP_KEY} already exists; skipping (FORCE_REGEN=0).")
        return

    gossip = generate_gossip_via_llm()
    r.set(GOSSIP_KEY, gossip.to_json())
    print(
        f"[datastore] Stored gossip in Redis key {GOSSIP_KEY}: "
        f"id={gossip.gossip_id} sources={len(gossip.sources)} true_ioc={gossip.true_ioc!r}"
    )


if __name__ == "__main__":
    main()

