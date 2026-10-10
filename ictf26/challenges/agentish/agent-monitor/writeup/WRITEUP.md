# Agent Monitor — Writeup

## Challenge

A server application is running in a container. The specific program
varies between rounds (MinIO, Gogs, PocketBase, Spring PetClinic, or
TiDB). Each deployment has **3 rounds** — each round the system randomly
picks a program and an issue scenario:

1. **cpu-issue** — a bug drives CPU usage to 30-50%
2. **memory-leak** — a bug causes memory to grow steadily over time
3. **normal** — the server operates correctly

The agent has shell access via `run_command` and must correctly diagnose
all 3 rounds (with peak metric evidence) to receive the flag.

## Solution approach (per round)

1. **Discover monitoring approach** — Use `run_command` to explore the
   container's cgroup interface:
   - `/sys/fs/cgroup/cpu.stat` (v2) — `usage_usec` field
   - `/sys/fs/cgroup/memory.current` (v2) — memory in bytes
   - `date +%s%N` for nanosecond timestamps
2. **Implement monitoring loop** — Take ~28 readings at 5s intervals
   (~140s total). Compute CPU% from `usage_usec` deltas.
3. **Ask the LLM** — Feed the CPU% and memory readings to an LLM and
   ask it to classify the issue as `cpu-issue`, `memory-leak`, or
   `normal`. The LLM also returns the max observed values.
4. **Submit** via `submit_diagnosis` with `issue_type` and the peak
   metric evidence (`cpu_usage_percent` or `memory_usage_mb`).
5. After correct submission the system restarts — wait and repeat.

## Key thresholds

| Scenario      | Metric          | Typical values             |
|---------------|-----------------|----------------------------|
| cpu-issue     | avg CPU         | 25-35%                     |
| memory-leak   | memory growth   | 50-200+ MB over 3 min      |
| normal        | CPU / memory    | CPU < 10%, memory flat     |

## Flag

```
ictf{ag3nt_m0n1t0r_m4st3r}
```
