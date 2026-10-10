import os
from typing import Any

import litellm


class LLMClient:
    def __init__(self) -> None:
        self.model = os.getenv("CHALLENGE_LITELLM_MODEL") or os.getenv("LITELLM_MODEL", "gpt-4o-mini")
        self.api_base = (os.getenv("LITELLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE") or os.getenv("OPENAI_API_BASE_URL") or "").rstrip("/")
        self.api_key = os.getenv("LITELLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")

    def _msg_content(self, resp: Any) -> str:
        msg = resp.choices[0].message
        if isinstance(msg, dict):
            return str(msg.get("content", ""))
        return str(getattr(msg, "content", ""))

    async def chat(self, *, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        kwargs: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": float(temperature)}
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key
        resp = await litellm.acompletion(**kwargs)
        return self._msg_content(resp)

