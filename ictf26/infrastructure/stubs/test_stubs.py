#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


def _clean_env_value(v: str) -> str:
    return v.split("#", 1)[0].strip()


def load_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = _clean_env_value(v)
        if not k:
            continue
        # strip optional quotes
        if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
            v = v[1:-1]
        out[k] = v
    return out


def run(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout_s: int = 120,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout_s,
        check=False,
    )


def require_ok(cp: subprocess.CompletedProcess[str], what: str) -> None:
    if cp.returncode == 0:
        return
    raise RuntimeError(f"{what} failed (exit={cp.returncode}).\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}")


def http_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: Any | None = None,
) -> tuple[int, str]:
    # Use stdlib only (don't assume requests is installed on the host).
    import urllib.error
    import urllib.request

    data: bytes | None = None
    hdrs = dict(headers or {})
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, method=method, data=data, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # nosec - local test only
            body = resp.read().decode("utf-8", errors="replace")
            return int(resp.status), body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        return int(getattr(e, "code", 0) or 0), body


def wait_http_ok(url: str, *, headers: dict[str, str] | None = None, timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    last: tuple[int, str] | None = None
    while time.time() < deadline:
        try:
            status, text = http_request("GET", url, headers=headers)
            last = (status, text)
            if status == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError(f"Timed out waiting for HTTP 200: {url} (last={last})")


def find_repo_root(start_dir: Path) -> Path:
    for p in (start_dir, *start_dir.parents):
        if (p / "challenges").is_dir() and (p / "stubs").is_dir():
            return p
    raise RuntimeError(f"Could not locate repo root starting from: {start_dir}")


DEFAULT_QUERY = "Reply with exactly: hello from litellm"


def main(*, query: str, challenge: str, challenge_dir: str | None) -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = find_repo_root(script_dir)
    stubs_dir = repo_root / "stubs"

    if challenge_dir:
        resolved_challenge_dir = Path(challenge_dir).expanduser().resolve()
    else:
        resolved_challenge_dir = (repo_root / "challenges" / challenge).resolve()

    if not resolved_challenge_dir.exists():
        raise SystemExit(f"Challenge directory does not exist: {resolved_challenge_dir}")

    # Prefer real `.env` values over `env.example` placeholders.
    dotenv: dict[str, str] = {}
    dotenv.update(load_dotenv(stubs_dir / "example.env"))
    dotenv.update(load_dotenv(stubs_dir / ".env"))
    dotenv.update(load_dotenv(resolved_challenge_dir / "env.example"))
    dotenv.update(load_dotenv(resolved_challenge_dir / ".env"))

    # Required for litellm stub authentication + upstream call.
    litellm_api_key = os.environ.get("LITELLM_API_KEY") or dotenv.get("LITELLM_API_KEY") or ""
    team_key = os.environ.get("TEAM_LITELLM_API_KEY") or dotenv.get("TEAM_LITELLM_API_KEY") or ""
    challenge_key = os.environ.get("CHALLENGE_LITELLM_API_KEY") or dotenv.get("CHALLENGE_LITELLM_API_KEY") or ""

    if not litellm_api_key.strip():
        raise SystemExit(
            "Missing LITELLM_API_KEY (needed for LiteLLM upstream call). "
            "Set it in stubs/.env, challenges/<name>/.env, or the environment."
        )
    if not team_key.strip():
        raise SystemExit(
            "Missing TEAM_LITELLM_API_KEY (needed to auth to LiteLLM stub). "
            "Set it in stubs/.env, challenges/<name>/.env, or the environment."
        )

    env = os.environ.copy()
    # Ensure litellm has an upstream key and the request key allowlist is populated.
    env["LITELLM_API_KEY"] = litellm_api_key
    env["TEAM_LITELLM_API_KEY"] = team_key
    if challenge_key:
        env["CHALLENGE_LITELLM_API_KEY"] = challenge_key

    def cleanup() -> None:
        run(
            ["docker", "compose", "down", "-v", "--remove-orphans"],
            cwd=resolved_challenge_dir,
            env=env,
            timeout_s=120,
        )

    try:
        print("[test_stubs.py] Starting stubs (litellm + langfuse)...")
        cp = run(
            ["docker", "compose", "up", "-d", "--build", "litellm", "langfuse"],
            cwd=resolved_challenge_dir,
            env=env,
            timeout_s=300,
        )
        require_ok(cp, "docker compose up stubs")

        print("[test_stubs.py] Waiting for LiteLLM /v1/models (authenticated)...")
        wait_http_ok("http://localhost:4000/v1/models", headers={"Authorization": f"Bearer {team_key}"}, timeout_s=90)

        print("[test_stubs.py] Performing a LiteLLM chat completion...")
        status, text = http_request(
            "POST",
            "http://localhost:4000/v1/chat/completions",
            headers={"Authorization": f"Bearer {team_key}", "Content-Type": "application/json"},
            json_body={
                "model": "gpt-4o-mini",
                "temperature": 0.0,
                "messages": [{"role": "user", "content": query}],
            },
        )
        if status != 200:
            raise RuntimeError(f"LiteLLM chat completion failed: status={status} body={text[:1000]}")
        try:
            obj = json.loads(text)
            content = obj["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"LiteLLM response not parseable: {e!r} body={text[:1000]}")
        print("[test_stubs.py] LiteLLM completion content:", repr(str(content)[:200]))
        if query == DEFAULT_QUERY:
            if str(content).strip() != "hello from litellm":
                raise RuntimeError(
                    "LiteLLM completion did not match expected output for default query. "
                    f"got={str(content).strip()!r}"
                )

        print("[test_stubs.py] Checking langfuse stub healthz...")
        wait_http_ok("http://localhost:3000/healthz", timeout_s=60)

        print("[test_stubs.py] Building sandbox stub image...")
        # Build the sandbox stub image directly from the stubs directory.
        img = "mario-soc-sandbox-stub-test"
        cp = run(
            ["docker", "build", "-t", img, "-f", str(stubs_dir / "sandbox_stub" / "Dockerfile"), str(stubs_dir)],
            cwd=repo_root,
            env=env,
            timeout_s=300,
        )
        require_ok(cp, "docker build sandbox stub")

        print("[test_stubs.py] Running hello world program in sandbox stub...")
        with tempfile.TemporaryDirectory(prefix="mario-soc-sandbox-") as td:
            td_path = Path(td)
            hello = td_path / "hello.py"
            hello.write_text(
                "print('hello from sandbox')\n",
                encoding="utf-8",
            )
            cp = run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-e",
                    "AGENT_FILE=/workspace/hello.py",
                    "-v",
                    f"{td_path}:/workspace:ro",
                    img,
                ],
                cwd=repo_root,
                env=env,
                timeout_s=120,
            )
            require_ok(cp, "docker run sandbox stub")
            if "hello from sandbox" not in cp.stdout:
                raise RuntimeError(
                    f"Sandbox did not print expected output. STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
                )
            print("[test_stubs.py] Sandbox output OK.")

        print("[test_stubs.py] All stub checks passed.")
        return 0
    finally:
        print("[test_stubs.py] Cleaning up...")
        cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bring up local stubs and verify they are operational.")
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help="Text sent as the user message to the LLM via the LiteLLM stub.",
    )
    parser.add_argument(
        "--challenge",
        default="mario-soc",
        help="Challenge name under challenges/ (default: mario-soc). Ignored if --challenge-dir is set.",
    )
    parser.add_argument(
        "--challenge-dir",
        default=None,
        help="Explicit path to a challenge directory (where docker compose will be run).",
    )
    args = parser.parse_args()
    raise SystemExit(main(query=args.query, challenge=args.challenge, challenge_dir=args.challenge_dir))

