import json
import os
import re
import sys
import urllib.request
from typing import Any


MCP_URL = os.environ.get("MCP_GOSSIP_URL", "http://mcp_gossip:7003").rstrip("/")


def _clean_env_value(v: str) -> str:
    return v.split("#", 1)[0].strip()


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v.strip() == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


def rpc(method: str, params: dict[str, Any] | None = None, _id: int = 1) -> dict[str, Any]:
    payload = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        MCP_URL + "/rpc",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        out = json.loads(resp.read().decode("utf-8"))
    if "error" in out:
        raise RuntimeError(f"RPC error: {out['error']}")
    return out["result"]


def tool_call(name: str, arguments: dict[str, Any], _id: int) -> str:
    res = rpc("tools/call", {"name": name, "arguments": arguments}, _id=_id)
    content = res.get("content") or []
    if not content or content[0].get("type") != "text":
        raise RuntimeError(f"Unexpected tool result shape: {res!r}")
    return str(content[0].get("text", ""))


RE_SOURCE = re.compile(r"^Source:\s*(.+?)\s*$", re.MULTILINE)

def parse_packet(text: str) -> tuple[str, str]:
    src_m = RE_SOURCE.search(text)
    if not src_m:
        raise RuntimeError(f"Could not parse Source from packet:\n{text}")
    src = src_m.group(1).strip()

    lines = text.splitlines()
    msg_lines: list[str] = []
    for i, ln in enumerate(lines):
        if ln.strip() == "Message:":
            msg_lines = lines[i + 1 :]
            break
        if ln.startswith("Message:"):
            msg_lines = [ln.split(":", 1)[1].lstrip()] + lines[i + 1 :]
            break
    msg = "\n".join(msg_lines).strip()
    if not msg:
        raise RuntimeError(f"Could not parse Message from packet:\n{text}")
    return src, msg


def openai_chat_completion(base_url: str, api_key: str, model: str, *, system: str, user: str) -> str:
    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "temperature": 0.0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=45) as resp:  # nosec - local challenge call
        out = json.loads(resp.read().decode("utf-8"))
    return str(out["choices"][0]["message"]["content"])


def extract_iocs_and_next(message_text: str) -> tuple[list[str], str | None]:
    base_url = _clean_env_value(_env("LITELLM_BASE_URL", "http://litellm:4000"))
    api_key = _clean_env_value(_env("TEAM_LITELLM_API_KEY"))
    model = _clean_env_value(os.environ.get("TEAM_LITELLM_MODEL") or os.environ.get("LITELLM_MODEL") or "gpt-4o-mini")

    system = (
        "You extract structured indicators from unstructured threat intel messages.\n"
        "Return STRICT JSON with keys:\n"
        '- "iocs": array of EXACTLY 3 strings\n'
        '- "next_source": string email or null\n'
        "Rules:\n"
        "- The 3 iocs MUST be verbatim substrings that appear in the message text.\n"
        "- next_source MUST be an email address mentioned as the next contact/hint. If none, use null.\n"
        "- Do not include any extra keys."
    )
    user = "Message:\n" + message_text
    content = openai_chat_completion(base_url, api_key, model, system=system, user=user)
    try:
        obj = json.loads(content)
    except Exception as e:
        raise RuntimeError(f"LLM returned non-JSON content: {e!r}\ncontent={content!r}")

    iocs_raw = obj.get("iocs")
    if not isinstance(iocs_raw, list) or len(iocs_raw) != 3:
        raise RuntimeError(f"LLM extraction failed: expected iocs list of len 3, got: {iocs_raw!r}")
    iocs = [str(x).strip() for x in iocs_raw if str(x).strip()]
    if len(iocs) != 3:
        raise RuntimeError(f"LLM extraction failed: iocs not all non-empty strings: {iocs_raw!r}")
    for ioc in iocs:
        if ioc not in message_text:
            raise RuntimeError(f"LLM extraction failed: ioc not present verbatim in message: {ioc!r}")

    nxt_raw = obj.get("next_source")
    nxt: str | None
    if nxt_raw is None:
        nxt = None
    else:
        nxt = str(nxt_raw).strip() or None
        if nxt is not None and nxt not in message_text:
            raise RuntimeError(f"LLM extraction failed: next_source not present verbatim in message: {nxt!r}")

    return iocs, nxt


def main() -> int:
    # Initialize (optional but mirrors typical clients)
    rpc("initialize", {}, _id=100)

    first = tool_call("gossip", {}, _id=1)
    src, msg = parse_packet(first)
    iocs, nxt = extract_iocs_and_next(msg)
    chain = [src]
    ioc_sets = [set(iocs)]

    _id = 2
    while nxt is not None:
        pkt = tool_call("rumor", {"source": nxt}, _id=_id)
        _id += 1
        src2, msg2 = parse_packet(pkt)
        iocs2, nxt2 = extract_iocs_and_next(msg2)
        chain.append(src2)
        ioc_sets.append(set(iocs2))
        nxt = nxt2

    common = set.intersection(*ioc_sets)
    if len(common) != 1:
        raise RuntimeError(f"Expected exactly 1 common IoC, got {sorted(common)!r}")
    ioc = next(iter(common))

    verdict = tool_call("opinion", {"sources": chain, "ioc": ioc}, _id=_id)
    sys.stdout.write(verdict)
    if "Flag:" not in verdict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

