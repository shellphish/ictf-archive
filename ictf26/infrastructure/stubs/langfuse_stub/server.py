import os

from fastapi import FastAPI  # type: ignore[import-not-found]
import uvicorn  # type: ignore[import-not-found]


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


app = FastAPI(title="langfuse_stub", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"ok": "true"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "langfuse_stub", "note": "Stub for local testing"}


def main() -> None:
    port = int(_env("PORT", "3000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()

