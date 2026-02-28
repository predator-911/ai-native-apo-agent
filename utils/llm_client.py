"""Centralized LLM client for OpenAI and Anthropic APIs."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict


class LLMClientError(Exception):
    """Raised when LLM API requests fail."""


@dataclass
class LLMConfig:
    """Runtime configuration for LLM calls."""

    provider: str
    model: str
    temperature: float = 0.2
    timeout_seconds: int = 60


class LLMClient:
    """Minimal multi-provider client with clear error handling."""

    def __init__(self, config: LLMConfig | None = None) -> None:
        provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
        model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
        self.config = config or LLMConfig(provider=provider, model=model)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if self.config.provider == "openai":
            return self._complete_openai(system_prompt, user_prompt)
        if self.config.provider == "anthropic":
            return self._complete_anthropic(system_prompt, user_prompt)
        raise LLMClientError(
            f"Unsupported LLM_PROVIDER '{self.config.provider}'. Use 'openai' or 'anthropic'."
        )

    def complete_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        raw = self.complete(system_prompt, user_prompt)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMClientError("Model returned invalid JSON. Tighten prompt or switch model.") from exc

    def _complete_openai(self, system_prompt: str, user_prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise LLMClientError("Missing OPENAI_API_KEY environment variable.")

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"},
        }
        return self._post_json(
            url="https://api.openai.com/v1/chat/completions",
            payload=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            parser=self._parse_openai_response,
            provider_name="OpenAI",
        )

    def _complete_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise LLMClientError("Missing ANTHROPIC_API_KEY environment variable.")

        payload = {
            "model": self.config.model,
            "max_tokens": 1800,
            "temperature": self.config.temperature,
            "system": f"{system_prompt}\nAlways return valid JSON.",
            "messages": [{"role": "user", "content": user_prompt}],
        }
        return self._post_json(
            url="https://api.anthropic.com/v1/messages",
            payload=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            parser=self._parse_anthropic_response,
            provider_name="Anthropic",
        )

    def _post_json(self, url: str, payload: Dict[str, Any], headers: Dict[str, str], parser: Any, provider_name: str) -> str:
        req = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body)
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise LLMClientError(f"{provider_name} request failed ({exc.code}): {error_body}") from exc
        except urllib.error.URLError as exc:
            raise LLMClientError(f"{provider_name} network error: {exc.reason}") from exc
        except TimeoutError as exc:
            raise LLMClientError(f"{provider_name} request timed out.") from exc
        except json.JSONDecodeError as exc:
            raise LLMClientError(f"{provider_name} returned non-JSON response.") from exc

        return parser(data)

    @staticmethod
    def _parse_openai_response(data: Dict[str, Any]) -> str:
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError("Unexpected OpenAI response format.") from exc

    @staticmethod
    def _parse_anthropic_response(data: Dict[str, Any]) -> str:
        try:
            content_blocks = data["content"]
            text_blocks = [b["text"] for b in content_blocks if b.get("type") == "text"]
            if not text_blocks:
                raise LLMClientError("Anthropic response had no text content.")
            return "\n".join(text_blocks)
        except (KeyError, TypeError, ValueError) as exc:
            raise LLMClientError("Unexpected Anthropic response format.") from exc
