"""Reference solver for Agent Monitor.

Uses run_command to collect cgroup metrics from the target container, then
asks an LLM to diagnose the issue. Supports both OpenAI directly
(OPENAI_API_KEY) and LiteLLM proxy as fallback. Three rounds must pass to
get the flag.
"""

import json
import os
import sys
import time
from typing import Any

import requests


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


SHELL_URL = _env("MCP_SHELL_URL", "http://target_app:7001")
FLAG_URL = _env("MCP_FLAG_URL", "http://mcp_flag:7002")

# LLM config: prefer OpenAI direct, fall back to LiteLLM proxy
OPENAI_API_KEY = _env("OPENAI_API_KEY", "")
OPENAI_MODEL = _env("OPENAI_MODEL", "")
LITELLM_BASE_URL = _env("LITELLM_BASE_URL", "http://litellm:4000")
LITELLM_API_KEY = _env("TEAM_LITELLM_API_KEY", "")
LITELLM_MODEL = _env("TEAM_LITELLM_MODEL", "gpt-4o-mini")

TOTAL_ROUNDS = 3
SAMPLE_INTERVAL = 5
SAMPLE_COUNT = 28

_rpc_counter = 0


def rpc_call(
    url: str,
    method: str,
    params: dict[str, Any] | None = None,
    retries: int = 12,
    backoff: float = 5.0,
) -> Any:
    global _rpc_counter
    _rpc_counter += 1
    payload = {
        "jsonrpc": "2.0",
        "id": _rpc_counter,
        "method": method,
        "params": params or {},
    }
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(f"{url}/rpc", json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise RuntimeError(f"RPC error: {data['error']}")
            return data.get("result", {})
        except requests.ConnectionError:
            if attempt == retries:
                raise
            print(f"  Connection to {url} failed (attempt {attempt}/{retries}), "
                  f"retrying in {backoff}s...")
            time.sleep(backoff)


def init_mcp(url: str) -> None:
    rpc_call(url, "initialize", {
        "protocolVersion": "2024-11-05",
        "clientInfo": {"name": "solver", "version": "1.0"},
        "capabilities": {},
    })


def run_command(cmd: str) -> str:
    result = rpc_call(SHELL_URL, "tools/call", {
        "name": "run_command",
        "arguments": {"command": cmd},
    })
    contents = result.get("content", [])
    return contents[0].get("text", "") if contents else ""


def submit_diagnosis(issue_type: str, **kwargs: Any) -> str:
    args: dict[str, Any] = {"issue_type": issue_type}
    args.update(kwargs)
    result = rpc_call(FLAG_URL, "tools/call", {
        "name": "submit_diagnosis",
        "arguments": args,
    })
    contents = result.get("content", [])
    return contents[0].get("text", "") if contents else ""


# ---- LLM integration (OpenAI direct or LiteLLM proxy) ----


def _chat_completion(prompt: str, system: str) -> str:
    """Call chat completions API. Uses OpenAI if OPENAI_API_KEY is set,
    otherwise falls back to LiteLLM proxy."""
    if OPENAI_API_KEY:
        url = "https://api.openai.com/v1/chat/completions"
        api_key = OPENAI_API_KEY
        model = OPENAI_MODEL or "gpt-4o-mini"
        print(f"  [LLM] Using OpenAI directly (model={model})")
    else:
        url = LITELLM_BASE_URL.rstrip("/") + "/v1/chat/completions"
        api_key = LITELLM_API_KEY
        model = LITELLM_MODEL
        print(f"  [LLM] Using LiteLLM proxy (model={model})")

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    resp = requests.post(
        url,
        headers=headers,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        },
        timeout=45,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


DIAGNOSIS_SYSTEM_PROMPT = """\
You are a DevOps monitoring expert. You are given CPU usage percentages and \
memory usage (MB) readings collected over time from a container running a \
server application.

Analyze the data and determine if there is an issue:
- "cpu-issue": CPU usage is abnormally high (sustained above ~15% average)
- "memory-leak": Memory usage is steadily growing over time (growth > 30 MB)
- "normal": CPU and memory are within expected ranges

Return STRICT JSON with these fields:
{
  "issue_type": "cpu-issue" | "memory-leak" | "normal",
  "max_cpu": <float, the peak CPU% observed>,
  "max_mem": <float, the peak memory MB observed>,
  "reasoning": "<brief explanation>"
}
"""


def ask_llm_for_diagnosis(
    cpu_readings: list[float],
    mem_readings: list[float],
) -> dict[str, Any]:
    prompt_lines = ["CPU% readings (chronological):"]
    prompt_lines.append(", ".join(f"{v:.1f}" for v in cpu_readings))
    prompt_lines.append("")
    prompt_lines.append("Memory MB readings (chronological):")
    prompt_lines.append(", ".join(f"{v:.1f}" for v in mem_readings))

    prompt = "\n".join(prompt_lines)

    try:
        content = _chat_completion(prompt, DIAGNOSIS_SYSTEM_PROMPT)
        return json.loads(content)
    except Exception as e:
        print(f"  LLM call failed ({e!r}), falling back to heuristic.")
        return heuristic_diagnosis(cpu_readings, mem_readings)


def heuristic_diagnosis(
    cpu_readings: list[float],
    mem_readings: list[float],
) -> dict[str, Any]:
    avg_cpu = sum(cpu_readings) / len(cpu_readings) if cpu_readings else 0
    max_cpu = max(cpu_readings) if cpu_readings else 0
    max_mem = max(mem_readings) if mem_readings else 0
    mem_growth = (mem_readings[-1] - mem_readings[0]) if len(mem_readings) > 1 else 0

    if avg_cpu > 15.0:
        issue = "cpu-issue"
    elif mem_growth > 30.0:
        issue = "memory-leak"
    else:
        issue = "normal"

    return {
        "issue_type": issue,
        "max_cpu": max_cpu,
        "max_mem": max_mem,
        "reasoning": f"avg_cpu={avg_cpu:.1f}%, mem_growth={mem_growth:.1f}MB",
    }


# ---- Monitoring logic ----

def detect_cgroup_version() -> str:
    out = run_command("test -f /sys/fs/cgroup/cpu.stat && echo v2 || echo v1")
    return "v2" if "v2" in out.strip() else "v1"


def read_sample_v2() -> tuple[int, int, int]:
    out = run_command(
        "grep usage_usec /sys/fs/cgroup/cpu.stat | awk '{print $2}'; "
        "cat /sys/fs/cgroup/memory.current; "
        "date +%s%N"
    )
    lines = [l.strip() for l in out.strip().split("\n")
             if l.strip() and not l.startswith("STDERR")]
    return int(lines[0]), int(lines[1]), int(lines[2])


def read_sample_v1() -> tuple[int, int, int]:
    out = run_command(
        "cat /sys/fs/cgroup/cpu/cpuacct.usage; "
        "cat /sys/fs/cgroup/memory/memory.usage_in_bytes; "
        "date +%s%N"
    )
    lines = [l.strip() for l in out.strip().split("\n")
             if l.strip() and not l.startswith("STDERR")]
    return int(lines[0]), int(lines[1]), int(lines[2])


def wait_for_app_ready(max_wait: int = 120) -> None:
    print("  Waiting for target application to be ready...")
    start = time.time()
    while time.time() - start < max_wait:
        try:
            out = run_command("ls /opt/runtime/ 2>/dev/null; pgrep -fl 'target-app|gogs|pocketbase|java|tidb-server' || true")
            if out.strip():
                time.sleep(10)
                print("  Target application is running.")
                return
        except Exception:
            pass
        time.sleep(3)
    print("  WARNING: Timed out waiting for target application.")


def monitor_round(cgroup_ver: str) -> tuple[list[float], list[float]]:
    read_sample = read_sample_v2 if cgroup_ver == "v2" else read_sample_v1

    cpu_percentages: list[float] = []
    mem_mb_values: list[float] = []

    prev_cpu, prev_mem, prev_ts = read_sample()
    mem_mb_values.append(prev_mem / (1024 * 1024))

    print(f"  Collecting {SAMPLE_COUNT} samples at {SAMPLE_INTERVAL}s intervals...")

    for i in range(SAMPLE_COUNT):
        time.sleep(SAMPLE_INTERVAL)
        try:
            cur_cpu, cur_mem, cur_ts = read_sample()
        except Exception as e:
            print(f"  Sample {i+1} failed: {e}")
            continue

        mem_mb = cur_mem / (1024 * 1024)
        mem_mb_values.append(mem_mb)

        cpu_delta = cur_cpu - prev_cpu
        time_delta_us = (cur_ts - prev_ts) / 1000
        if cgroup_ver == "v1":
            cpu_delta_us = cpu_delta / 1000
        else:
            cpu_delta_us = cpu_delta
        cpu_pct = (cpu_delta_us / time_delta_us) * 100 if time_delta_us > 0 else 0
        cpu_percentages.append(cpu_pct)

        prev_cpu, prev_mem, prev_ts = cur_cpu, cur_mem, cur_ts

        if (i + 1) % 5 == 0:
            print(f"  Sample {i+1}/{SAMPLE_COUNT}: CPU={cpu_pct:.1f}%, Mem={mem_mb:.1f}MB")

    return cpu_percentages, mem_mb_values


def main() -> None:
    print("=== Agent Monitor Solver ===\n")

    init_mcp(SHELL_URL)
    init_mcp(FLAG_URL)

    cgroup_ver = detect_cgroup_version()
    print(f"Detected cgroup version: {cgroup_ver}\n")

    for rnd in range(1, TOTAL_ROUNDS + 1):
        print(f"--- Round {rnd}/{TOTAL_ROUNDS} ---")
        wait_for_app_ready()

        cpu_readings, mem_readings = monitor_round(cgroup_ver)

        if not cpu_readings:
            print("  No samples collected, skipping round.")
            continue

        print("  Asking LLM for diagnosis...")
        diagnosis = ask_llm_for_diagnosis(cpu_readings, mem_readings)

        issue_type = diagnosis.get("issue_type", "normal")
        max_cpu = float(diagnosis.get("max_cpu", max(cpu_readings)))
        max_mem = float(diagnosis.get("max_mem", max(mem_readings)))
        reasoning = diagnosis.get("reasoning", "")

        print(f"  LLM diagnosis: {issue_type} (reason: {reasoning})")
        print(f"  max_cpu={max_cpu:.1f}%, max_mem={max_mem:.1f}MB")

        kwargs: dict[str, Any] = {}
        if issue_type == "cpu-issue":
            kwargs["cpu_usage_percent"] = round(max_cpu, 2)
        elif issue_type == "memory-leak":
            kwargs["memory_usage_mb"] = round(max_mem, 0)

        response = submit_diagnosis(issue_type, **kwargs)
        print(f"  Server response: {response}\n")

        if "Flag:" in response or "flag:" in response.lower():
            print("Flag obtained!")
            sys.exit(0)

        if "Incorrect" in response:
            print("Wrong diagnosis. Exiting.")
            sys.exit(1)

    print("All rounds completed.")


if __name__ == "__main__":
    main()
