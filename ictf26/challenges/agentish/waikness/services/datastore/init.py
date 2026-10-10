"""
Waikness datastore bootstrap.

At startup:
- Discovers all sample_XXX directories in the dataset
- Randomly selects 10 samples
- Compiles C sources (vuln.c) freshly for the selected challenges
- Generates a 10-word sentence via LLM
- Associates each sample with a word
- Assigns each challenge a failure probability (10–70%)
- Stores config in Redis for MCP servers
"""

import json
import os
import random
import subprocess
import time
from pathlib import Path

import redis  # type: ignore[import-not-found]
import litellm  # type: ignore[import-not-found]


CONFIG_KEY = "waikness:config"
DATASET_PATH = Path("/dataset")
COMPILED_PATH = Path("/compiled")


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


def compile_c_sample(sample_id: str) -> None:
    """Compile vuln.c for a sample into COMPILED_PATH/sample_id/vuln."""
    vuln_c = DATASET_PATH / sample_id / "vuln.c"
    if not vuln_c.exists():
        return
    out_dir = COMPILED_PATH / sample_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_bin = out_dir / "vuln"
    result = subprocess.run(
        ["gcc", "-o", str(out_bin), str(vuln_c)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to compile {sample_id}: {result.stderr}")
    out_bin.chmod(0o755)
    print(f"[datastore] Compiled {sample_id}/vuln.c -> {out_bin}")


def compile_selected_c_samples(selected: list[str]) -> None:
    """Compile all C samples in the selected list."""
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    for sample_id in selected:
        if (DATASET_PATH / sample_id / "vuln.c").exists():
            compile_c_sample(sample_id)


def discover_samples() -> list[str]:
    """Return sorted list of sample IDs (e.g. sample_001, sample_002)."""
    if not DATASET_PATH.exists():
        raise RuntimeError(f"Dataset path {DATASET_PATH} does not exist")
    samples = []
    for d in DATASET_PATH.iterdir():
        if d.is_dir() and d.name.startswith("sample_"):
            vuln = d / "vuln"
            vuln_py = d / "vuln.py"
            vuln_c = d / "vuln.c"
            if vuln.exists() or vuln_py.exists() or vuln_c.exists():
                samples.append(d.name)
    return sorted(samples)


BANNED_WORDS = {"fox", "dof"}

FALLBACK_SENTENCES = [
    "Curious students explore cybersecurity concepts through fun capture the flag challenges",
    "Learning security skills helps protect systems from malicious attackers",
    "The quick brown cat jumps over the lazy dog today",
]


def contains_banned_word(sentence: str) -> bool:
    words = {w.lower().strip(".,!?") for w in sentence.split()}
    return bool(words & BANNED_WORDS)


def generate_sentence_via_llm() -> str:
    base_url = os.environ.get("LITELLM_BASE_URL", "http://litellm:4000")
    api_key = os.environ.get("CHALLENGE_LITELLM_API_KEY") or ""
    model = os.environ.get("CHALLENGE_LITELLM_MODEL") or os.environ.get("LITELLM_MODEL", "gpt-4o-mini")
    debug = _bool_env("DATASTORE_DEBUG_LITELLM", False)

    system = (
        "You generate a single English sentence for a CTF challenge.\n"
        "Return STRICT JSON with one key: sentence (string).\n"
        "The sentence must have EXACTLY 10 words. Use common English words.\n"
        "Do NOT use the words: fox, dog, or jump (or any variant).\n"
        "Make the sentence themed around cybersecurity concepts, AI, and capture the flag challenges.\n"
        "Example: {\"sentence\": \"Curious students explore cybersecurity concepts through fun capture the flag challenges\"}\n"
        "Do not include any extra keys or explanation."
    )
    user = "Generate one 10-word English sentence."
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]

    if debug:
        print(f"[datastore] LiteLLM request: api_base={base_url!r} model={model!r}")

    try:
        resp = litellm.completion(
            model=model,
            messages=messages,
            temperature=0.95,
            api_base=base_url.rstrip("/"),
            api_key=api_key or None,
            timeout=45.0,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        print(f"[datastore] LiteLLM request failed: {e!r}, using fallback sentence")
        return random.choice(FALLBACK_SENTENCES)

    content = resp.choices[0].message["content"]
    obj = json.loads(content)
    raw = str(obj.get("sentence", "")).strip()
    words = [w.strip(".,!?;:\"'") for w in raw.split() if w.strip(".,!?;:\"'")]
    sentence = " ".join(words)
    if len(words) != 10 or contains_banned_word(sentence):
        valid_fallbacks = [s for s in FALLBACK_SENTENCES if not contains_banned_word(s)]
        return random.choice(valid_fallbacks) if valid_fallbacks else "Curious students explore cybersecurity concepts through fun capture the flag challenges"
    return sentence


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
        print(f"[datastore] {CONFIG_KEY} already exists; skipping (FORCE_REGEN=0).")
        return

    samples = discover_samples()
    if len(samples) < 10:
        raise RuntimeError(f"Need at least 10 samples, found {len(samples)}")

    selected = random.sample(samples, 10)
    compile_selected_c_samples(selected)
    sentence = generate_sentence_via_llm()
    words = sentence.split()

    # Build challenge config: random IDs 1-1024 (not in sentence order)
    challenge_ids = random.sample(range(1, 1025), 10)
    challenges = []
    for i, sample_id in enumerate(selected):
        word = words[i] if i < len(words) else f"word{i}"
        failure_prob = random.uniform(0.1, 0.7)
        challenges.append({
            "id": str(challenge_ids[i]),
            "sample_id": sample_id,
            "word": word,
            "failure_prob": failure_prob,
        })

    config = {
        "sentence": sentence,
        "challenges_json": json.dumps(challenges),
        "created_at": str(int(time.time())),
    }
    r.hset(CONFIG_KEY, mapping=config)
    print(f"[datastore] Stored config: sentence={sentence!r}, challenges={[c['sample_id'] for c in challenges]}")


if __name__ == "__main__":
    main()
