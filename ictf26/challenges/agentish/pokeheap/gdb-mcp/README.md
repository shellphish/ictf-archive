# gdb-mcp

GDB MCP server — lets an LLM debug binaries interactively through GDB.

Built with [FastMCP](https://gofastmcp.com) and [pygdbmi](https://github.com/cs01/pygdbmi).

## Features

- Full GDB control: breakpoints, stepping, registers, memory examination
- **Inferior I/O via PTY**: cleanly separated from GDB's command stream
- **Send raw bytes** (hex-encoded) — like pwntools `send()`/`sendline()`
- Read inferior stdout/stderr independently
- `send_and_continue`: atomic send-then-resume for programs that read stdin after a breakpoint

## Install

```bash
uv sync
```

## Run

```bash
# stdio transport (default, for Claude Code / MCP clients)
uv run python server.py
```

## Claude Code config

Add to `.claude/settings.json` (project) or `~/.claude/settings.json` (global):

```json
{
  "mcpServers": {
    "gdb": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/gdb-mcp", "run", "python", "server.py"]
    }
  }
}
```

## Tools

| Category | Tool | Description |
|---|---|---|
| Session | `start_debug` | Start GDB with a binary |
| | `stop_debug` | Stop GDB session |
| Execution | `run` | Run program from start |
| | `continue_exec` | Continue after stop |
| | `step` / `next_line` | Source-level stepping |
| | `stepi` / `nexti` | Instruction-level stepping |
| | `finish` | Run until function returns |
| | `interrupt` | Pause running program |
| Breakpoints | `set_breakpoint` | Set breakpoint (function, address, file:line) |
| | `delete_breakpoint` | Delete breakpoint by number |
| | `list_breakpoints` | List all breakpoints |
| Inspection | `backtrace` | Call stack |
| | `registers` | Register values |
| | `examine` | Memory examination (x/ command) |
| | `disassemble` | Disassemble at location |
| | `print_expr` | Evaluate C expression |
| | `info_locals` | Local variables |
| | `vmmap` | Memory mappings |
| | `info_inferior` | Process info |
| **I/O** | `send_input` | Send text to inferior stdin (sendline) |
| | `send_raw` | Send hex bytes to inferior (pwntools-style) |
| | `get_output` | Read inferior stdout/stderr |
| | `send_and_continue` | Send input then resume execution |
| Raw | `execute` | Run any GDB CLI command |
| | `check_status` | Check if inferior is running/stopped |
