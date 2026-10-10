from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import yaml  # type: ignore[import-not-found]
from fastapi import Request  # type: ignore[import-not-found]

from litellm.proxy._types import UserAPIKeyAuth  # type: ignore[import-not-found]


@lru_cache(maxsize=1)
def _allowed_keys() -> set[str]:
    """
    Load allowed API keys from the mounted LiteLLM proxy config.

    This lets us define the *challenge* and *team* request keys in config.yaml,
    while keeping LiteLLM's built-in `master_key` as a single string.
    """
    cfg_path = "/app/config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg: Any = yaml.safe_load(f) or {}
    if not isinstance(cfg, dict):
        return set()
    gs = cfg.get("general_settings") or {}
    if not isinstance(gs, dict):
        return set()
    keys = gs.get("allowed_api_keys") or []
    if not isinstance(keys, list):
        return set()
    out: set[str] = set()
    for k in keys:
        s = str(k).strip()
        if not s:
            continue
        # Support env indirection in config.yaml (matches LiteLLM's master_key behavior).
        if s.startswith("os.environ/"):
            env_name = s.split("/", 1)[1]
            s = (os.environ.get(env_name) or "").strip()
        if s:
            out.add(s)
    return out


async def user_api_key_auth(request: Request, api_key: str) -> UserAPIKeyAuth:
    # request is unused for now, but is part of LiteLLM's custom_auth signature
    _ = request
    if api_key in _allowed_keys():
        return UserAPIKeyAuth(api_key=api_key)
    raise Exception("invalid api key")

