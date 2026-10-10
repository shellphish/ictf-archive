# Agent Monitor

An agentic DevOps challenge where the agent must diagnose the health of a
running server application by monitoring its CPU and memory usage across
**3 rounds**.

## Overview

Each deployment runs 3 rounds. Per round the challenge randomly selects a
server program *and* one of three issue scenarios:

| Scenario        | Symptom                                    |
|-----------------|--------------------------------------------|
| `cpu-issue`     | CPU usage climbs well above normal levels  |
| `memory-leak`   | Memory usage steadily increases over time  |
| `normal`        | Server operates within expected parameters |

The specific program is drawn from a pool of candidates (MinIO, Gogs,
PocketBase, Spring PetClinic, TiDB). The agent does **not** need to
identify the program — only diagnose the resource condition.

The agent has **shell access** to the target container via the `run_command`
MCP tool. It must figure out how to read system resource metrics (e.g.
cgroup files, `/proc` stats), collect data over time, identify the pattern,
and submit a diagnosis with evidence. All 3 rounds must be correct to
receive the flag. Between rounds the server environment is cleaned and
restarted.

## Architecture

| Service          | Role                                                       |
|------------------|------------------------------------------------------------|
| `datastore`      | Redis + bootstrap (generates 3 random scenarios)           |
| `target_app`     | Runs the selected server binary, workload, metrics, + shell MCP server |
| `mcp_flag`       | MCP server for diagnosis submission / grading              |
| `sandbox` (debug)| Agent runtime (uses stubs for local testing)               |

## Quick start (local testing)

```bash
cp env.example .env
docker compose up --build                        # core services only
docker compose --profile debug up --build        # with solver sandbox
```

## MCP tools

### `mcp_shell` (port 7001, on `target_app`)

- **`run_command`** — execute an arbitrary shell command on the target
  server container and get stdout/stderr back (30 s timeout)

### `mcp_flag` (port 7002)

- **`submit_diagnosis`** — submit `issue_type` plus CPU/memory evidence
  for the current round; returns the flag after all 3 rounds are correct.

## Supported programs

| Program          | Binary type | Issue variants          |
|------------------|-------------|-------------------------|
| MinIO            | Go binary   | cpu-issue, memory-leak, normal |
| Gogs             | Go binary   | cpu-issue, memory-leak, normal |
| PocketBase       | Go binary   | cpu-issue, memory-leak, normal |
| Spring PetClinic | Java JAR    | cpu-issue, memory-leak, normal |
| TiDB             | Go binary   | memory-leak, normal            |
