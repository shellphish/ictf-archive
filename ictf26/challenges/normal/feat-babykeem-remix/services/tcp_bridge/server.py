"""
TCP bridge for FileBot.

Accepts a TCP connection, reads lines from the player, forwards each as
a ``chat`` MCP tool call to mcp_filebot via HTTP, and prints the LLM
response back to the player.  One conversation per connection.
"""

import json
import os
import socketserver
import urllib.request

MCP_URL = os.environ.get("MCP_FILEBOT_URL", "http://localhost:7101").rstrip("/")

BANNER = """\
=== FileBot ===
Type a message and press Enter to chat.
Press Ctrl+C or Ctrl+D to disconnect.
"""


def rpc(method: str, params=None, _id=1):
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
    with urllib.request.urlopen(req, timeout=120) as resp:
        out = json.loads(resp.read().decode("utf-8"))
    if "error" in out:
        raise RuntimeError(f"RPC error: {out['error']}")
    return out["result"]


def chat(message: str, session_id: str | None = None, _id: int = 1) -> str:
    params = {"name": "chat", "arguments": {"message": message}}
    if session_id:
        params["sessionId"] = session_id
    res = rpc("tools/call", params, _id=_id)
    content = res.get("content") or []
    if not content or content[0].get("type") != "text":
        return "(no response)"
    return str(content[0].get("text", ""))


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(BANNER.encode("utf-8"))
        self.wfile.flush()

        # Initialize MCP session to get an isolated session ID.
        session_id = None
        try:
            result = rpc("initialize", {}, _id=0)
            session_id = result.get("sessionId")
        except Exception:
            pass

        msg_id = 0
        while True:
            prompt = f"#{msg_id + 1} You: "
            self.wfile.write(prompt.encode("utf-8"))
            self.wfile.flush()
            try:
                line = self.rfile.readline()
            except Exception:
                break
            if not line:
                break
            text = line.decode("utf-8", errors="replace").strip()
            if not text:
                continue
            msg_id += 1
            try:
                reply = chat(text, session_id=session_id, _id=msg_id)
            except Exception as e:
                reply = f"(error: {e})"
            self.wfile.write(f"FileBot: {reply}\n\n".encode("utf-8"))
            self.wfile.flush()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    port = int(os.environ.get("TCP_PORT", "31338"))
    server = ThreadedTCPServer(("0.0.0.0", port), Handler)
    print(f"TCP bridge listening on :{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
