"""Unified LLM client supporting HuggingFace Inference API and Anthropic."""

from __future__ import annotations
import json
import time
from typing import Any, AsyncIterator

import httpx
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError,
)
import logging

from core.config import settings


_RETRY_ERRORS = (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError)


class TokenUsage(dict):
    """Tracks cumulative API token usage across the session."""
    prompt_tokens: int = 0
    completion_tokens: int = 0

    def add(self, prompt: int, completion: int) -> None:
        self.prompt_tokens = getattr(self, "prompt_tokens", 0) + prompt
        self.completion_tokens = getattr(self, "completion_tokens", 0) + completion

    @property
    def total(self) -> int:
        return getattr(self, "prompt_tokens", 0) + getattr(self, "completion_tokens", 0)


_usage = TokenUsage()


def get_usage() -> TokenUsage:
    return _usage


class LLMClient:
    """Unified async LLM client with retry, timeout, and usage tracking."""

    def __init__(self):
        self._hf_client = httpx.AsyncClient(
            base_url=settings.hf_base_url,
            headers={
                "Authorization": f"Bearer {settings.hf_api_token}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(120.0, connect=10.0),
        )
        self._anthropic_client = None
        if settings.has_anthropic:
            import anthropic
            self._anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def complete(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> str:
        """Send a completion request. Returns the assistant message string."""
        if model.startswith("claude-") and self._anthropic_client:
            return await self._anthropic_complete(model, system, user, temperature, max_tokens)
        return await self._hf_complete(model, system, user, temperature, max_tokens, json_mode)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(_RETRY_ERRORS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def _hf_complete(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool,
    ) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        # Note: json_mode not sent — not all HF models support structured-outputs.
        # _parse_json handles extraction from plain text responses.

        t0 = time.perf_counter()
        try:
            resp = await self._hf_client.post("/v1/chat/completions", json=payload)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise httpx.ConnectError("Rate limited") from e
            logger.error(f"HF API error {e.response.status_code}: {e.response.text[:300]}")
            raise

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        _usage.add(usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
        elapsed = time.perf_counter() - t0
        logger.debug(f"HF [{model.split('/')[-1]}] → {len(content)} chars in {elapsed:.1f}s")
        return content

    async def _anthropic_complete(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        message = await self._anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        content = message.content[0].text
        _usage.add(message.usage.input_tokens, message.usage.output_tokens)
        return content

    async def complete_json(self, model: str, system: str, user: str, **kwargs) -> dict:
        """Complete and parse JSON response, with fallback extraction."""
        raw = await self.complete(model, system, user, json_mode=True, **kwargs)
        return self._parse_json(raw)

    def _parse_json(self, text: str) -> dict:
        text = text.strip()
        # strip markdown fences
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
        # find first { or [
        for start_char, end_char in [('{', '}'), ('[', ']')]:
            idx = text.find(start_char)
            if idx != -1:
                ridx = text.rfind(end_char)
                if ridx != -1:
                    try:
                        return json.loads(text[idx:ridx+1])
                    except json.JSONDecodeError:
                        pass
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}\nRaw: {text[:200]}")
            raise ValueError(f"LLM returned invalid JSON: {text[:200]}") from e

    async def aclose(self) -> None:
        await self._hf_client.aclose()


# Module-level singleton
_client: LLMClient | None = None


def get_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
