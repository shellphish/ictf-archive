# Agentic Binary Reversing Challenge

A reverse engineering challenge where an AI agent must analyze a binary to discover the secret password.

## Challenge Description

The challenge binary has multi-stage password validation using XOR encryption. Agents must use the provided MCP tools to:

1. **list_functions** - Discover all functions in the binary
2. **get_disassembly_by_function** - Analyze function disassembly
3. **get_caller_callee_mapping** - Understand which functions a caller invokes
4. **get_callee_caller_mapping** - Find which functions call a given callee
5. **run_challenge** - Test candidate passwords against the binary
6. **run_python** - Execute custom Python analysis scripts

## Quick Start

### Prerequisites

- Docker and Docker Compose
- An OpenAI API key (or compatible LLM provider)

### Setup

1. Copy the environment template:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your API key:
   ```bash
   LITELLM_API_KEY=sk-your-openai-key-here
   ```

3. Build and run:
   ```bash
   docker compose up --build
   ```

4. The solver will automatically run and attempt to find the flag.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│    sandbox      │────▶│   mcp_binary    │
│  (agent/solver) │     │  (JSON-RPC 2.0) │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│    litellm      │     │    langfuse     │
│  (LLM proxy)    │     │  (observability)│
└─────────────────┘     └─────────────────┘
```

## MCP Server Interface

The `mcp_binary` service exposes a JSON-RPC 2.0 endpoint at `POST /rpc`.

Supported methods:
- `initialize` - Initialize the server
- `tools/list` - List available tools with schemas
- `tools/call` - Execute a tool

### Tool Schemas

#### list_functions
Returns all discovered functions from the challenge binary.

#### get_disassembly_by_function
```json
{
  "name": "get_disassembly_by_function",
  "arguments": {
    "function": "main"
  }
}
```

#### get_caller_callee_mapping
```json
{
  "name": "get_caller_callee_mapping",
  "arguments": {
    "function_signature": "main"
  }
}
```

#### get_callee_caller_mapping
```json
{
  "name": "get_callee_caller_mapping",
  "arguments": {
    "function_signature": "validate_stage1"
  }
}
```

#### run_challenge
```json
{
  "name": "run_challenge",
  "arguments": {
    "input": "test_password"
  }
}
```

#### run_python
```json
{
  "name": "run_python",
  "arguments": {
    "code": "print('Hello, World!')",
    "stdin": ""
  }
}
```

## Challenge Solution

The binary uses XOR encryption with key `0x42`. The password is the XOR-encoded form of `ictf{BINARY_AGENTIC_CHALLENGE}`.

See `writeup/WRITEUP.md` for the full solution explanation.

## Files

- `challenge.yml` - CTFd portable format metadata
- `challengish.yml` - MCP server contract for agents
- `docker-compose.yml` - Local development infrastructure
- `services/mcp_binary/` - MCP server implementation
- `writeup/` - Solution explanation and solver script
