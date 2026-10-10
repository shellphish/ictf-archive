import json
import os
from typing import Any

import requests  # type: ignore[import-not-found]


def _clean_env_value(v: str) -> str:
    return v.split("#", 1)[0].strip()


def _env(name: str, default: str | None = None) -> str:
    raw = os.environ.get(name)
    v = _clean_env_value(raw) if raw is not None else ""
    if v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


def jsonrpc(url: str, method: str, params: dict[str, Any] | None = None, _id: int = 1) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data


def _content_text(resp: dict[str, Any]) -> str:
    return str(resp["result"]["content"][0]["text"])


def _parse_json_text(resp: dict[str, Any]) -> Any:
    return json.loads(_content_text(resp))


def openai_chat_completion(*, base_url: str, api_key: str | None, model: str, messages: list[dict[str, str]]) -> str:
    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "temperature": 0.0,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def main() -> None:
    uba_rpc = _env("MCP_UBA_URL") + "/rpc"
    edr_rpc = _env("MCP_EDR_URL") + "/rpc"
    ids_rpc = _env("MCP_IDS_URL") + "/rpc"
    soc_rpc = _env("MCP_SOC_URL") + "/rpc"

    # LiteLLM proxy (OpenAI-compatible)
    litellm_base_url = _env("LITELLM_BASE_URL", "")
    team_key = _env("TEAM_LITELLM_API_KEY", "")
    model = _env("TEAM_LITELLM_MODEL", _env("LITELLM_MODEL", "gpt-4o-mini"))
    api_key = team_key or None

    ci = {"clientInfo": {"name": "mario-soc-solver", "version": "1.0"}}
    jsonrpc(uba_rpc, "initialize", ci, _id=1)
    jsonrpc(edr_rpc, "initialize", ci, _id=2)
    jsonrpc(ids_rpc, "initialize", ci, _id=3)
    jsonrpc(soc_rpc, "initialize", ci, _id=4)

    # 1) Find anomalous login (attacker + first victim + compromised user)
    users = _parse_json_text(jsonrpc(uba_rpc, "tools/call", {"name": "uba_list_users", "arguments": {}}, _id=10))
    if not isinstance(users, list) or not users:
        raise RuntimeError("No users returned by UBA")

    anomaly_event: dict[str, Any] | None = None
    attacker: dict[str, str] | None = None
    victim: dict[str, str] | None = None

    for u in users:
        u_str = str(u).strip()
        if not u_str:
            continue
        events = _parse_json_text(
            jsonrpc(uba_rpc, "tools/call", {"name": "uba_events_for_user", "arguments": {"user": u_str}}, _id=11)
        )
        if not isinstance(events, list):
            continue
        for ev in events:
            if not isinstance(ev, dict):
                continue
            if ev.get("event_type") == "login" and bool(ev.get("is_anomalous")) is True:
                anomaly_event = ev
                attacker = {"ip": str(ev.get("source_ip", "")).strip(), "domain": str(ev.get("source_domain", "")).strip()}
                victim = {
                    "ip": str(ev.get("destination_ip", "")).strip(),
                    "domain": str(ev.get("destination_domain", "")).strip(),
                    "user": str(ev.get("user", "")).strip(),
                }
                break
        if attacker and victim:
            break

    if not attacker or not victim or not anomaly_event:
        raise RuntimeError("Unable to find anomalous login event in UBA logs")
    print("[solve] Anomalous login:", json.dumps(anomaly_event, indent=2))

    # 2) Confirm EDR metasploit alert on victim host
    edr_events = _parse_json_text(jsonrpc(edr_rpc, "tools/call", {"name": "edr_events_for_host", "arguments": {"ip": victim["ip"]}}, _id=20))
    if not isinstance(edr_events, list):
        raise RuntimeError("EDR events payload invalid")
    edr_malware = next(
        (
            ev
            for ev in edr_events
            if isinstance(ev, dict)
            and ev.get("event_type") == "malware_alert"
            and str(ev.get("file_name", "")).strip() == "metasploit"
        ),
        None,
    )
    if not edr_malware:
        raise RuntimeError("Expected metasploit malware alert not found in EDR logs")
    print("[solve] EDR malware alert:", json.dumps(edr_malware, indent=2))

    # 3) Use IDS to find at least one successfully compromised internal host (C2)
    ids_events = _parse_json_text(jsonrpc(ids_rpc, "tools/call", {"name": "ids_events_for_ip", "arguments": {"ip": attacker["ip"]}}, _id=30))
    if not isinstance(ids_events, list):
        raise RuntimeError("IDS events payload invalid")

    c2_events = [
        ev
        for ev in ids_events
        if isinstance(ev, dict)
        and str(ev.get("signature", "")).strip() == "Command-and-control connection"
        and str(ev.get("dst_ip", "")).strip() == attacker["ip"]
    ]
    if not c2_events:
        raise RuntimeError("No IDS C2 events found for attacker IP")

    candidates: list[dict[str, str]] = []
    for ev in c2_events:
        src_ip = str(ev.get("src_ip", "")).strip()
        src_domain = str(ev.get("src_domain", "")).strip()
        if not src_ip or not src_domain:
            continue
        if src_ip == victim["ip"]:
            continue
        candidates.append({"ip": src_ip, "domain": src_domain})
    if not candidates:
        raise RuntimeError("IDS C2 events did not yield any internal host candidates")
    print("[solve] IDS C2 candidates:", json.dumps(candidates, indent=2))

    # 4) Ask an LLM to assemble the correlated alert JSON to submit.
    correlated: dict[str, Any] | None = None
    if litellm_base_url:
        system = (
            "You are a SOC analyst assistant.\n"
            "Given evidence from UBA, EDR and IDS logs, produce a SINGLE correlated alert to submit.\n"
            "Return STRICT JSON with keys: attacker, victim, compromised_internal_host.\n"
            "attacker must have: ip, domain\n"
            "victim must have: ip, domain, user\n"
            "compromised_internal_host must have: ip, domain\n"
            "Do NOT include any extra keys.\n"
            "Choose exactly ONE compromised_internal_host from the provided candidates."
        )
        user_msg = json.dumps(
            {"uba_anomaly_event": anomaly_event, "edr_malware_alert": edr_malware, "ids_c2_candidates": candidates},
            indent=2,
        )
        try:
            content = openai_chat_completion(
                base_url=litellm_base_url,
                api_key=api_key,
                model=model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user_msg}],
            )
            correlated = json.loads(content)
        except Exception as e:
            print(f"[solve] Warning: LLM correlation failed; falling back to deterministic assembly. Error: {e!r}")

    if correlated is None:
        correlated = {"attacker": attacker, "victim": victim, "compromised_internal_host": candidates[0]}

    # Minimal validation
    corr_att = correlated.get("attacker") or {}
    corr_vic = correlated.get("victim") or {}
    corr_int = correlated.get("compromised_internal_host") or {}
    if not all(str(corr_att.get(k, "")).strip() for k in ("ip", "domain")):
        raise RuntimeError("Invalid correlated alert: attacker missing fields")
    if not all(str(corr_vic.get(k, "")).strip() for k in ("ip", "domain", "user")):
        raise RuntimeError("Invalid correlated alert: victim missing fields")
    if not all(str(corr_int.get(k, "")).strip() for k in ("ip", "domain")):
        raise RuntimeError("Invalid correlated alert: compromised_internal_host missing fields")

    print("[solve] Submitting correlated alert:", json.dumps(correlated, indent=2))
    out = jsonrpc(
        soc_rpc,
        "tools/call",
        {"name": "soc_submit_correlated_alert", "arguments": correlated},
        _id=40,
    )
    print(_content_text(out))


if __name__ == "__main__":
    main()

