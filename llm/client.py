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
        # Fail fast: 3 attempts, up to ~5s total wait. If the provider is down/rate-limited
        # past this we fall back to templates rather than stalling the pipeline for minutes.
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
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
            # Normalize rate limits into a retryable error.
            if e.response.status_code == 429:
                retry_after = e.response.headers.get("retry-after")
                if retry_after:
                    try:
                        wait_s = float(retry_after)
                        logger.warning(f"Rate limited (429). Respecting Retry-After: {wait_s:.1f}s")
                        await asyncio.sleep(wait_s)
                    except Exception:
                        pass
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

    def _parse_json(self, text: str) -> dict | list:
        text = text.strip()

        # Strip markdown fences
        if "```" in text:
            import re
            text = re.sub(r"```(?:json)?\s*", "", text).strip()

        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Find outermost { } or [ ] — handles truncated/prefixed responses
        for start_char, end_char in [('[', ']'), ('{', '}')]:
            idx = text.find(start_char)
            if idx == -1:
                continue
            # Walk backwards from end to find matching close
            depth = 0
            end_idx = -1
            in_str = False
            escape_next = False
            for i, ch in enumerate(text[idx:], start=idx):
                if escape_next:
                    escape_next = False
                    continue
                if ch == '\\' and in_str:
                    escape_next = True
                    continue
                if ch == '"':
                    in_str = not in_str
                    continue
                if in_str:
                    continue
                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break
            if end_idx != -1:
                candidate = text[idx:end_idx+1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    # Try to repair common issues: trailing commas
                    import re
                    repaired = re.sub(r',\s*([\}\]])', r'\1', candidate)
                    try:
                        return json.loads(repaired)
                    except json.JSONDecodeError:
                        pass

        # Last resort: LLM returned the inside of an object/array without outer brackets.
        # e.g. `\n  "id": "arch_a", "name": "Foo"` → wrap as object, then as array item
        stripped = text.strip().lstrip('\n ')
        if stripped.startswith('"') and ':' in stripped:
            # Try as single object
            for wrapper in (('{\n', '\n}'), ('[{\n', '\n}]')):
                try:
                    return json.loads(wrapper[0] + stripped + wrapper[1])
                except json.JSONDecodeError:
                    pass
            # Try repairing then wrapping
            import re as _re
            repaired = _re.sub(r',\s*([\}\]])', r'\1', stripped)
            for wrapper in (('{\n', '\n}'), ('[{\n', '\n}]')):
                try:
                    return json.loads(wrapper[0] + repaired + wrapper[1])
                except json.JSONDecodeError:
                    pass

        logger.error(f"JSON parse failed. Raw[:300]: {text[:300]}")
        raise ValueError(f"LLM returned invalid JSON: {text[:200]}")

    async def aclose(self) -> None:
        await self._hf_client.aclose()


# Module-level singleton
_client: LLMClient | None = None


def get_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
