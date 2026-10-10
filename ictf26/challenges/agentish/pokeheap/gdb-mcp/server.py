#!/usr/bin/env python3
"""GDB MCP Server — let an LLM debug binaries with GDB.

Uses PTY for inferior I/O so stdin/stdout are cleanly separated from GDB's
MI protocol stream.  Supports sending raw bytes (pwntools-style) to the
debugged process.

Transport: plain FastAPI + JSON-RPC 2.0 over HTTP POST /rpc
"""

from __future__ import annotations

import fcntl
import functools
import logging
import os
import pty
import select
import signal
import time
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pygdbmi.gdbcontroller import GdbController
from pygdbmi.constants import GdbTimeoutError

log = logging.getLogger("gdb-mcp")

app = FastAPI()


# ── command sanitisation ────────────────────────────────────────────────────

_BLOCKED_PREFIXES = [
    "shell", "!",
    "python", "py ", "pi ", "pi\t",
    "source",
    "pipe", "|",
    "define", "document",
    "set logging", "dump", "restore", "generate-core-file", "gcore",
    "append",
    "add-symbol-file", "add-inferior",
    "call system", "call popen", "call exec",
    "print system", "print popen", "print exec",
    "p system", "p popen", "p exec",
]

_BLOCKED_EXPR_CALLS = [
    "system(", "popen(", "execve(", "execv(", "execl(",
    "execlp(", "execvp(", "dlopen(", "fork(",
]


def _check_command(command: str) -> str | None:
    cmd = command.strip()
    low = cmd.lower()
    for prefix in _BLOCKED_PREFIXES:
        if low.startswith(prefix):
            return f"BLOCKED: '{prefix}*' commands are not allowed (security)."
    return None


def _check_expression(expr: str) -> str | None:
    low = expr.lower().replace(" ", "")
    for call in _BLOCKED_EXPR_CALLS:
        if call in low:
            return f"BLOCKED: calling {call[:-1]}() is not allowed (security)."
    return None


def _sanitize_for_mi(value: str) -> str:
    return value.replace("\n", " ").replace("\r", " ").replace('"', '\\"')


# ── error-safe tool decorator ──────────────────────────────────────────────

def safe(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            log.exception("Tool %s failed", func.__name__)
            return f"ERROR ({type(exc).__name__}): {exc}"
    return wrapper


# ── GDB session management ─────────────────────────────────────────────────

class GDBSession:
    def __init__(self) -> None:
        self.gdb: Optional[GdbController] = None
        self.master_fd: Optional[int] = None
        self.slave_fd: Optional[int] = None
        self.slave_name: Optional[str] = None
        self.binary: Optional[str] = None
        self.inferior_running: bool = False

    @property
    def active(self) -> bool:
        if self.gdb is None:
            return False
        try:
            proc = self.gdb.gdb_process
            if proc and proc.poll() is not None:
                log.warning("GDB process exited (rc=%s), cleaning up", proc.returncode)
                self.stop()
                return False
        except Exception:
            pass
        return True

    def start(self, binary_path: str, gdb_path: str = "gdb") -> None:
        if self.active:
            self.stop()

        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)

        try:
            import termios, tty
            tty.setraw(self.slave_fd)
        except Exception:
            pass

        flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
        fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        self.gdb = GdbController(command=[gdb_path, "--interpreter=mi3", "-q"])
        self.binary = binary_path

        self._mi(f"-file-exec-and-symbols {binary_path}")
        self._mi(f"-gdb-set inferior-tty {self.slave_name}")
        self._mi("-gdb-set pagination off")
        self._mi("-gdb-set confirm off")
        self.inferior_running = False

    def stop(self) -> None:
        if self.gdb:
            try:
                self.gdb.exit()
            except Exception:
                pass
            self.gdb = None
        for fd in (self.master_fd, self.slave_fd):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
        self.master_fd = self.slave_fd = None
        self.slave_name = None
        self.inferior_running = False

    def _mi(self, cmd: str, timeout_sec: int = 15) -> list[dict]:
        if not self.gdb:
            raise RuntimeError("GDB not started")
        try:
            return self.gdb.write(cmd, timeout_sec=timeout_sec)
        except GdbTimeoutError as exc:
            log.warning("GDB command timed out: %s", exc)
            raise RuntimeError(
                f"GDB timed out waiting for response to '{cmd}'. "
                "The inferior may be blocking on input. Try interrupt() first."
            )
        except (ValueError, OSError) as exc:
            log.warning("GDB communication failed: %s — cleaning up session", exc)
            self.stop()
            raise RuntimeError(f"GDB session lost ({exc}). Call start_debug() to restart.")

    def _drain(self, timeout_sec: float = 0.5) -> list[dict]:
        if not self.gdb:
            return []
        try:
            return self.gdb.get_gdb_response(
                timeout_sec=timeout_sec, raise_error_on_timeout=False
            )
        except (ValueError, OSError):
            self.stop()
            return []

    def exec_and_wait(self, cmd: str, wait: float = 3.0) -> tuple[list[dict], bool]:
        responses = self._mi(cmd, timeout_sec=15)

        for r in responses:
            if r.get("type") == "notify" and r.get("message") == "running":
                self.inferior_running = True

        if self.inferior_running and wait > 0:
            more = self._drain(timeout_sec=wait)
            responses.extend(more)
            for r in more:
                if r.get("type") == "notify" and r.get("message") == "stopped":
                    self.inferior_running = False

        return responses, not self.inferior_running

    def write_inferior(self, data: bytes) -> int:
        if self.master_fd is None:
            raise RuntimeError("No inferior I/O channel (PTY not set up)")
        return os.write(self.master_fd, data)

    def read_inferior(self, timeout: float = 1.0) -> bytes:
        if self.master_fd is None:
            return b""
        buf = b""
        deadline = time.time() + timeout
        while True:
            remaining = max(deadline - time.time(), 0)
            if remaining <= 0:
                break
            try:
                ready, _, _ = select.select(
                    [self.master_fd], [], [], min(remaining, 0.1)
                )
            except (ValueError, OSError):
                break
            if ready:
                try:
                    chunk = os.read(self.master_fd, 4096)
                    if chunk:
                        buf += chunk
                    else:
                        break
                except OSError:
                    break
            elif buf:
                break
        return buf


session = GDBSession()


# ── response formatting ────────────────────────────────────────────────────

def _fmt(responses: list[dict]) -> str:
    parts: list[str] = []
    for r in responses:
        rtype = r.get("type", "")
        message = r.get("message", "")
        payload = r.get("payload", "")

        if rtype == "console" and payload:
            parts.append(str(payload).rstrip("\n"))

        elif rtype == "result":
            if message == "error":
                msg = payload.get("msg", str(payload)) if isinstance(payload, dict) else str(payload)
                parts.append(f"ERROR: {msg}")
            elif message == "done" and payload:
                parts.append(_fmt_payload(payload))

        elif rtype == "notify":
            if message == "stopped":
                parts.append(_fmt_stop(payload))
            elif message in ("breakpoint-created", "breakpoint-modified"):
                bkpt = payload.get("bkpt", {}) if isinstance(payload, dict) else {}
                parts.append(
                    f"Breakpoint {bkpt.get('number', '?')}: "
                    f"{bkpt.get('func', '')} at {bkpt.get('addr', '?')}"
                )

    return "\n".join(parts).strip() or "OK"


def _fmt_payload(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if not isinstance(payload, dict):
        return str(payload)

    if "value" in payload:
        prefix = f"${payload['name']} = " if "name" in payload else ""
        return f"{prefix}{payload['value']}"

    if "bkpt" in payload:
        bp = payload["bkpt"]
        loc = bp.get("func", bp.get("addr", "?"))
        f = bp.get("file", "")
        l = bp.get("line", "")
        at = f" at {f}:{l}" if f else ""
        return f"Breakpoint {bp.get('number', '?')}: {loc}{at}"

    if "stack" in payload:
        lines: list[str] = []
        for frame in payload["stack"]:
            fr = frame.get("frame", frame) if isinstance(frame, dict) else frame
            if isinstance(fr, dict):
                lvl = fr.get("level", "?")
                addr = fr.get("addr", "?")
                func = fr.get("func", "?")
                fi = fr.get("file", "")
                li = fr.get("line", "")
                at = f" at {fi}:{li}" if fi else ""
                lines.append(f"  #{lvl}  {addr} in {func}{at}")
        if lines:
            return "\n".join(lines)

    return str(payload)


def _fmt_stop(payload: object) -> str:
    if not isinstance(payload, dict):
        return f"[stopped] {payload}"
    reason = payload.get("reason", "unknown")
    frame = payload.get("frame", {})
    func = frame.get("func", "?")
    addr = frame.get("addr", "?")
    loc = ""
    if frame.get("file"):
        loc = f" at {frame['file']}:{frame.get('line', '?')}"
    sig = ""
    if reason == "signal-received":
        sig = f" ({payload.get('signal-name', '')}:{payload.get('signal-meaning', '')})"
    return f"[stopped: {reason}] {func} ({addr}){loc}{sig}"


def _require() -> GDBSession:
    if not session.active:
        raise RuntimeError("No active GDB session. Call start_debug() first.")
    return session


# ═══════════════════════════════════════════════════════════════════════════
#  TOOLS
# ═══════════════════════════════════════════════════════════════════════════

@safe
def start_debug(binary_path: str = "", gdb_path: str = "gdb") -> str:
    if not binary_path:
        binary_path = os.environ.get("CTF_CHALLENGE_BIN_PATH", "")
    if not binary_path:
        return "ERROR: No binary_path provided and CTF_CHALLENGE_BIN_PATH is not set."
    binary_path = os.path.realpath(binary_path)
    if not os.path.isfile(binary_path):
        return f"ERROR: Binary not found: {binary_path}"
    session.start(binary_path, gdb_path)
    return (
        f"GDB session started.\n"
        f"  binary : {binary_path}\n"
        f"  inf tty: {session.slave_name}"
    )


@safe
def stop_debug() -> str:
    session.stop()
    return "GDB session stopped."


@safe
def run(args: str = "") -> str:
    s = _require()
    if args:
        s._mi(f"-exec-arguments {args}")
    responses, stopped = s.exec_and_wait("-exec-run", wait=2.0)
    result = _fmt(responses)
    if not stopped:
        result += "\n[inferior is running — may be waiting for input]"
    return result


@safe
def gdb_run(program_args: str = "") -> str:
    """Alias for run() using program_args to avoid LangChain naming conflicts."""
    return run(args=program_args)


@safe
def continue_exec() -> str:
    s = _require()
    responses, stopped = s.exec_and_wait("-exec-continue", wait=2.0)
    result = _fmt(responses)
    if not stopped:
        result += "\n[inferior is running — may be waiting for input]"
    return result


@safe
def step() -> str:
    s = _require()
    responses, _ = s.exec_and_wait("-exec-step", wait=5.0)
    return _fmt(responses)


@safe
def next_line() -> str:
    s = _require()
    responses, _ = s.exec_and_wait("-exec-next", wait=5.0)
    return _fmt(responses)


@safe
def stepi() -> str:
    s = _require()
    responses, _ = s.exec_and_wait("-exec-step-instruction", wait=5.0)
    return _fmt(responses)


@safe
def nexti() -> str:
    s = _require()
    responses, _ = s.exec_and_wait("-exec-next-instruction", wait=5.0)
    return _fmt(responses)


@safe
def finish() -> str:
    s = _require()
    responses, _ = s.exec_and_wait("-exec-finish", wait=5.0)
    return _fmt(responses)


@safe
def interrupt() -> str:
    s = _require()
    proc = s.gdb.gdb_process if s.gdb else None
    if proc and proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        time.sleep(0.3)
        responses = s._drain(timeout_sec=2.0)
        for r in responses:
            if r.get("type") == "notify" and r.get("message") == "stopped":
                s.inferior_running = False
        return _fmt(responses) or "SIGINT sent to GDB."
    return "GDB process is not running."


@safe
def set_breakpoint(
    location: str,
    condition: str = "",
    temporary: bool = False,
    hardware: bool = False,
) -> str:
    s = _require()
    location = _sanitize_for_mi(location)
    cmd = "-break-insert"
    if temporary:
        cmd += " -t"
    if hardware:
        cmd += " -h"
    if condition:
        condition = _sanitize_for_mi(condition)
        cmd += f' -c "{condition}"'
    cmd += f" {location}"
    return _fmt(s._mi(cmd))


@safe
def delete_breakpoint(number: int) -> str:
    s = _require()
    return _fmt(s._mi(f"-break-delete {number}"))


@safe
def list_breakpoints() -> str:
    s = _require()
    responses = s._mi("-break-list")
    for r in responses:
        if r.get("type") == "result" and r.get("message") == "done":
            payload = r.get("payload", {})
            body = payload.get("BreakpointTable", {}).get("body", [])
            if not body:
                return "No breakpoints."
            lines: list[str] = []
            for bp in body:
                num = bp.get("number", "?")
                enabled = "y" if bp.get("enabled") == "y" else "n"
                addr = bp.get("addr", "?")
                func = bp.get("func", "")
                f = bp.get("file", "")
                l = bp.get("line", "")
                hits = bp.get("times", "0")
                cond = bp.get("cond", "")
                loc = func or addr
                if f:
                    loc += f" at {f}:{l}"
                c = f"  if {cond}" if cond else ""
                lines.append(f"  #{num} [{enabled}] {loc} (hits:{hits}){c}")
            return "Breakpoints:\n" + "\n".join(lines)
    return _fmt(responses)


@safe
def backtrace(full: bool = False) -> str:
    s = _require()
    if full:
        return _fmt(s._mi('-interpreter-exec console "bt full"'))
    return _fmt(s._mi("-stack-list-frames"))


@safe
def registers(names: str = "") -> str:
    s = _require()
    names = _sanitize_for_mi(names)
    cmd = f"info registers {names}" if names else "info registers"
    return _fmt(s._mi(f'-interpreter-exec console "{cmd}"'))


@safe
def examine(address: str, count: int = 16, fmt: str = "gx") -> str:
    s = _require()
    address = _sanitize_for_mi(address)
    fmt = _sanitize_for_mi(fmt)
    return _fmt(s._mi(f'-interpreter-exec console "x/{count}{fmt} {address}"'))


@safe
def disassemble(location: str, count: int = 20) -> str:
    s = _require()
    location = _sanitize_for_mi(location)
    return _fmt(s._mi(f'-interpreter-exec console "x/{count}i {location}"'))


@safe
def print_expr(expression: str) -> str:
    blocked = _check_expression(expression)
    if blocked:
        return blocked
    s = _require()
    expression = _sanitize_for_mi(expression)
    return _fmt(s._mi(f'-data-evaluate-expression "{expression}"'))


@safe
def info_locals() -> str:
    s = _require()
    return _fmt(s._mi('-interpreter-exec console "info locals"'))


@safe
def vmmap() -> str:
    s = _require()
    return _fmt(s._mi('-interpreter-exec console "info proc mappings"'))


@safe
def info_inferior() -> str:
    s = _require()
    return _fmt(s._mi('-interpreter-exec console "info inferior"'))


@safe
def send_input(text: str, newline: bool = True) -> str:
    s = _require()
    data = text.encode("utf-8")
    if newline:
        data += b"\n"
    s.write_inferior(data)
    return f"Sent {len(data)} bytes to inferior."


@safe
def send_raw(hex_data: str, newline: bool = False) -> str:
    s = _require()
    try:
        data = bytes.fromhex(hex_data)
    except ValueError as exc:
        return f"Bad hex string: {exc}"
    if newline:
        data += b"\n"
    s.write_inferior(data)
    return f"Sent {len(data)} raw bytes: {data!r}"


@safe
def get_output(timeout: float = 1.0) -> str:
    s = _require()
    data = s.read_inferior(timeout=timeout)
    if not data:
        return "[no output available]"
    text = data.decode("utf-8", errors="replace")
    return f"Inferior output ({len(data)} bytes):\n{text}"


@safe
def send_and_continue(
    text: str = "",
    hex_data: str = "",
    newline: bool = True,
    read_timeout: float = 1.0,
) -> str:
    s = _require()

    if hex_data:
        try:
            data = bytes.fromhex(hex_data)
        except ValueError as exc:
            return f"Bad hex string: {exc}"
    elif text:
        data = text.encode("utf-8")
    else:
        data = b""

    if newline and data:
        data += b"\n"

    if data:
        s.write_inferior(data)

    responses, stopped = s.exec_and_wait("-exec-continue", wait=2.0)
    result = f"Sent {len(data)} bytes, then continued.\n" if data else "Continued.\n"
    result += _fmt(responses)

    if not stopped:
        result += "\n[inferior is running — may be waiting for more input]"

    output = s.read_inferior(timeout=read_timeout)
    if output:
        result += f"\n\nInferior output:\n{output.decode('utf-8', errors='replace')}"

    return result


@safe
def execute(command: str, timeout: int = 10) -> str:
    blocked = _check_command(command)
    if blocked:
        return blocked
    s = _require()
    escaped = _sanitize_for_mi(command)
    return _fmt(s._mi(f'-interpreter-exec console "{escaped}"', timeout_sec=timeout))


@safe
def check_status() -> str:
    s = _require()
    responses = s._drain(timeout_sec=0.5)
    for r in responses:
        if r.get("type") == "notify" and r.get("message") == "stopped":
            s.inferior_running = False

    status = "running" if s.inferior_running else "stopped"
    result = f"Status : {status}\nBinary : {s.binary}"
    if responses:
        result += f"\nNotifications:\n{_fmt(responses)}"
    return result


# ── Tool dispatch table ─────────────────────────────────────────────────────

TOOLS: dict[str, Any] = {
    "start_debug": start_debug,
    "stop_debug": stop_debug,
    "run": run,
    "gdb_run": gdb_run,
    "continue_exec": continue_exec,
    "step": step,
    "next_line": next_line,
    "stepi": stepi,
    "nexti": nexti,
    "finish": finish,
    "interrupt": interrupt,
    "set_breakpoint": set_breakpoint,
    "delete_breakpoint": delete_breakpoint,
    "list_breakpoints": list_breakpoints,
    "backtrace": backtrace,
    "registers": registers,
    "examine": examine,
    "disassemble": disassemble,
    "print_expr": print_expr,
    "info_locals": info_locals,
    "vmmap": vmmap,
    "info_inferior": info_inferior,
    "send_input": send_input,
    "send_raw": send_raw,
    "get_output": get_output,
    "send_and_continue": send_and_continue,
    "execute": execute,
    "check_status": check_status,
}


# ── JSON-RPC 2.0 HTTP server ────────────────────────────────────────────────

class RpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: Any = None


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/rpc")
def rpc(request: RpcRequest):
    req_id = request.id

    if request.method == "tools/list":
        tools_list = [{"name": name} for name in TOOLS]
        return JSONResponse({"jsonrpc": "2.0", "result": {"tools": tools_list}, "id": req_id})

    if request.method == "tools/call":
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})

        if tool_name not in TOOLS:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
                "id": req_id,
            })

        result = TOOLS[tool_name](**arguments)
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": str(result)}]},
            "id": req_id,
        })

    return JSONResponse({
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": f"Method not found: {request.method}"},
        "id": req_id,
    })


# ── Entrypoint ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    host = os.environ.get("HOST", "0.0.0.0")
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host=host, port=port)
