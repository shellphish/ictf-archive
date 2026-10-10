"""
MCP server for waikness flag submission.

Tool: submit_sentence
- Receives a 10-word sentence
- Returns "OK" + flag if correct
- Returns "VALID-WRONG" if words are correct but in wrong order (allows retry)
- Returns "INVALID" if any word is not in the original sentence; after 3 INVALID the challenge terminates
"""

import os
from typing import Any, Literal

import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing_extensions import TypedDict


CONFIG_KEY = "waikness:config"
INVALID_COUNT_KEY = "waikness:invalid_count"


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


class JsonRpcReq(TypedDict, total=False):
    jsonrpc: Literal["2.0"]
    id: Any
    method: str
    params: dict[str, Any]


def jsonrpc_ok(_id: Any, result: Any) -> JSONResponse:
    return JSONResponse({"jsonrpc": "2.0", "id": _id, "result": result})


def jsonrpc_err(_id: Any, code: int, message: str, data: Any = None) -> JSONResponse:
    err: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return JSONResponse({"jsonrpc": "2.0", "id": _id, "error": err})


def load_config(r: redis.Redis) -> dict[str, Any] | None:
    cfg = r.hgetall(CONFIG_KEY)
    if not cfg:
        return None
    return {
        "sentence": cfg.get("sentence", ""),
    }


def _normalize_word(w: str) -> str:
    """Strip punctuation for comparison; words must be alphabetic after stripping."""
    return w.strip(".,!?;:\"'")


def _get_words(sentence: str) -> list[str]:
    """Split into words and normalize (strip punctuation)."""
    return [_normalize_word(w) for w in sentence.strip().split() if _normalize_word(w)]


def is_valid_format(sentence: str) -> bool:
    """Check if the sentence has exactly 10 alphabetic words (punctuation stripped)."""
    words = _get_words(sentence)
    if len(words) != 10:
        return False
    for w in words:
        if not w or not w.isalpha():
            return False
    return True


def words_match_expected(submitted: str, expected: str) -> bool:
    """True if submitted has the same words as expected (multiset), possibly in different order."""
    return sorted(_get_words(submitted)) == sorted(_get_words(expected))


TOOL = {
    "name": "submit_sentence",
    "description": "Submit a 10-word sentence. Returns OK+flag if correct, VALID-WRONG if words correct but wrong order, INVALID if any word not in original. After 3 INVALID the challenge terminates.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "sentence": {
                "type": "string",
                "description": "A 10-word English sentence",
            },
        },
        "required": ["sentence"],
        "additionalProperties": False,
    },
}


app = FastAPI(title="mcp_flag", version="0.1.0")
redis_client = redis.Redis.from_url(_env("REDIS_URL", "redis://datastore:6379/0"), decode_responses=True)
FLAG = os.environ.get("FLAG_CHALLENGE") or _env("FLAG", "")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"ok": "true"}


@app.post("/rpc")
def rpc(req: JsonRpcReq) -> JSONResponse:
    _id = req.get("id")
    method = req.get("method", "")
    params = req.get("params") or {}

    if method == "initialize":
        return jsonrpc_ok(
            _id,
            {
                "serverInfo": {"name": "mcp_flag", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return jsonrpc_ok(_id, {"tools": [TOOL]})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name != TOOL["name"]:
            return jsonrpc_err(_id, -32602, "Unknown tool", {"name": name})

        sentence = str(arguments.get("sentence", "")).strip()

        cfg = load_config(redis_client)
        if not cfg:
            return jsonrpc_err(_id, -32001, "Challenge not initialized yet")

        expected = cfg.get("sentence", "").strip()
        expected_words = _get_words(expected)
        submitted_words = _get_words(sentence)

        # Check invalid count
        invalid_count = int(redis_client.get(INVALID_COUNT_KEY) or 0)
        if invalid_count >= 3:
            return jsonrpc_ok(
                _id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": "TERMINATED: Challenge ended after 3 invalid guesses.",
                        }
                    ]
                },
            )

        # Exact match (same words in same order; punctuation ignored)
        if submitted_words == expected_words:
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": f"OK. Flag: {FLAG}"}]},
            )

        # Check format: 10 alphabetic words
        if not is_valid_format(sentence):
            redis_client.incr(INVALID_COUNT_KEY)
            invalid_count += 1
            suffix = f" ({invalid_count}/3 invalid guesses)" if invalid_count < 3 else " (Challenge terminated.)"
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": f"INVALID{suffix}"}]},
            )

        # Any word not in the original sentence -> INVALID
        if not words_match_expected(sentence, expected):
            redis_client.incr(INVALID_COUNT_KEY)
            invalid_count += 1
            suffix = f" ({invalid_count}/3 invalid guesses)" if invalid_count < 3 else " (Challenge terminated.)"
            return jsonrpc_ok(
                _id,
                {"content": [{"type": "text", "text": f"INVALID{suffix}"}]},
            )

        # Words correct but wrong order -> VALID-WRONG
        return jsonrpc_ok(
            _id,
            {"content": [{"type": "text", "text": "VALID-WRONG. Words correct but wrong order. Try again."}]},
        )

    return jsonrpc_err(_id, -32601, "Method not found", {"method": method})


def main() -> None:
    port = int(_env("PORT", "7002"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
