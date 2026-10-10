import json
import os
import re
from datetime import datetime
from typing import Any, Optional

import requests


def _env(name: str, default: Optional[str] = None) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return value


def jsonrpc(url: str, method: str, params: dict[str, Any] | None = None, _id: int = 1) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()
    out = resp.json()
    if "error" in out:
        raise RuntimeError(f"JSON-RPC error: {out['error']}")
    return out


def parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


def tool_call(url: str, name: str, arguments: dict[str, Any], _id: int) -> str:
    out = jsonrpc(url, "tools/call", {"name": name, "arguments": arguments}, _id=_id)
    content = out["result"]["content"]
    if not content:
        raise RuntimeError("tool returned empty content")
    return str(content[0].get("text", ""))


def resolve_gate7_duty_officer(events: list[dict[str, Any]]) -> str:
    """
    Two-hop reasoning to find the shard holder's speaker_id.

    Hop 1 — find a line saying the Gate 7 comms duty officer holds the rotation shards.
    Hop 2 — find a line assigning a specific alias to Gate 7 comms duty.
    Then map that alias to a speaker_id via the event data.
    """
    ordered = sorted(events, key=lambda x: parse_ts(str(x["timestamp"])))

    # Collect all known speaker aliases so we can recognise them in clue text.
    aliases = {str(e.get("speaker_alias", "")).lower() for e in events}
    aliases.discard("")

    # Match lines that mention "Gate 7", "comms", and "duty" in any order.
    gate7_duty_re = re.compile(
        r"\bgate\s*7\b.*\bcomms\b.*\bduty\b"
        r"|\bduty\b.*\bgate\s*7\b.*\bcomms\b",
        re.IGNORECASE,
    )

    holder_alias: Optional[str] = None
    for event in ordered:
        text = str(event["text"])
        if not gate7_duty_re.search(text):
            continue
        # Check whether a known alias appears in this line.
        text_lower = text.lower()
        for alias in sorted(aliases):  # sorted for determinism
            if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                holder_alias = alias
                break
        if holder_alias:
            break

    if not holder_alias:
        raise RuntimeError("could not identify Gate 7 comms duty officer from logs")

    # Resolve the alias to a speaker_id.
    for event in ordered:
        if str(event.get("speaker_alias", "")).lower() == holder_alias:
            return str(event["speaker_id"])

    raise RuntimeError(f"could not find speaker_id for alias {holder_alias!r}")


def extract_shards_for_speaker(events: list[dict[str, Any]], speaker_id: str) -> str:
    """Collect key shard one/two/three from the given speaker and concatenate."""
    ordered = sorted(events, key=lambda x: parse_ts(str(x["timestamp"])))
    shard_pattern = re.compile(r"\bkey\s+shard\s+(one|two|three):\s*([a-f0-9]+)\b", re.IGNORECASE)
    ordinal = {"one": 1, "two": 2, "three": 3}
    shards: list[tuple[int, datetime, str]] = []
    for event in ordered:
        if str(event["speaker_id"]) != speaker_id:
            continue
        m = shard_pattern.search(str(event["text"]))
        if not m:
            continue
        shards.append((ordinal[m.group(1).lower()], parse_ts(str(event["timestamp"])), m.group(2).lower()))
    if len(shards) < 3:
        raise RuntimeError("failed to extract all three key shards")
    shards.sort(key=lambda x: (x[0], x[1]))
    return "".join(part for _, _, part in shards[:3])


def load_all_events(rpc_url: str) -> list[dict[str, Any]]:
    logs_text = tool_call(rpc_url, "list_logs", {}, _id=1)
    logs_payload = json.loads(logs_text)
    logs = logs_payload.get("logs", [])
    if not isinstance(logs, list):
        raise RuntimeError("list_logs returned invalid payload")

    events: list[dict[str, Any]] = []
    for index, log_name in enumerate(logs, start=2):
        raw = tool_call(
            rpc_url,
            "retrieve_lines_from_log",
            {"log_name": str(log_name), "start_line": 1, "end_line": 5000},
            _id=index,
        )
        payload = json.loads(raw)
        for line in payload.get("lines", []):
            events.append(json.loads(str(line)))
    return events


def main() -> None:
    rpc_url = _env("MCP_LOGS_URL", "http://mcp_logs:7301").rstrip("/") + "/rpc"
    jsonrpc(rpc_url, "initialize", {"clientInfo": {"name": "writeup-solver", "version": "1.0"}}, _id=100)

    for attempt in range(1, 4):
        events = load_all_events(rpc_url)
        if not events:
            raise RuntimeError("no events were loaded")
        speaker_id = resolve_gate7_duty_officer(events)
        key = extract_shards_for_speaker(events, speaker_id)
        result = tool_call(rpc_url, "submit_key", {"key": key}, _id=200 + attempt).strip()
        print(f"[attempt={attempt}] speaker_id={speaker_id} key={key} result={result}")
        if result.startswith("flag{"):
            print(result)
            return

    raise RuntimeError("failed to submit a fresh key after retries")


if __name__ == "__main__":
    main()
