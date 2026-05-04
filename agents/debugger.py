"""Agent 7 — Debugger: reads errors, fixes code, and retries until it works."""

from __future__ import annotations
from pathlib import Path

from loguru import logger

from core.config import settings
from core.models import DebugResult, ExecutionResult
from llm.client import get_client
from llm.router import router
from sandbox.validator import CodeValidator


_PROMPT_PATH = Path(__file__).parent.parent / "llm" / "prompts" / "debugger_prompt.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


class DebuggerAgent:
    """Self-healing agent: reads errors and fixes code in a loop."""

    def __init__(self):
        self.validator = CodeValidator()
        self.max_retries = settings.max_debug_retries

    async def debug_and_retry(
        self,
        code: str,
        error: str,
        attempt: int = 1,
        error_history: list[str] | None = None,
        executor=None,
    ) -> DebugResult:
        """Fix failing code in a recursive retry loop."""
        if error_history is None:
            error_history = []

        if attempt > self.max_retries:
            logger.error(f"Max retries ({self.max_retries}) exceeded")
            return DebugResult(
                success=False,
                message=f"Could not fix all errors after {self.max_retries} attempts",
                final_code=code,
                attempts_used=attempt - 1,
                error_history=error_history,
            )

        logger.info(f"Debug attempt {attempt}/{self.max_retries} — fixing error...")
        logger.debug(f"Error: {error[:200]}")

        error_history.append(self._fingerprint_error(error))
        is_looping = len(error_history) > 2 and error_history[-1] in error_history[:-1]

        fixed_code = await self._fix_code(code, error, attempt, is_looping)
        fixed_code = self._clean_code(fixed_code)

        # Validate fixed code first
        validation = self.validator.validate(fixed_code)
        if not validation.passed and attempt <= 3:
            logger.warning(f"Fixed code failed validation: {validation.failures}")
            return await self.debug_and_retry(
                fixed_code,
                f"Code validation failed: {'; '.join(validation.failures)}",
                attempt + 1,
                error_history,
                executor,
            )

        # Execute fixed code
        if executor is None:
            from agents.executor import ExecutorAgent
            executor = ExecutorAgent()

        result: ExecutionResult = await executor.execute(fixed_code, attempt=attempt)

        if result.success:
            logger.success(f"Fixed on attempt {attempt}! Code is working.")
            return DebugResult(
                success=True,
                final_code=fixed_code,
                attempts_used=attempt,
                message=f"Fixed after {attempt} attempt{'s' if attempt > 1 else ''}",
                error_history=error_history,
            )

        return await self.debug_and_retry(
            fixed_code,
            result.stderr,
            attempt + 1,
            error_history,
            executor,
        )

    async def _fix_code(self, code: str, error: str, attempt: int, is_looping: bool) -> str:
        """Ask the LLM to fix the failing code."""
        escalation = ""
        if attempt >= 3:
            escalation = "\n\nThis is attempt 3+. Simplify the failing part or use an alternative approach."
        if is_looping:
            escalation += "\n\nSame error keeps occurring. Rewrite the failing section completely with a different approach."
        if attempt >= 5:
            escalation = "\n\nFINAL ATTEMPT. Maximum simplicity. Make it work at all costs, even if less elegant."

        client = get_client()
        fixed = await client.complete(
            model=router.debugger_model,
            system=_SYSTEM_PROMPT,
            user=(
                f"Attempt #{attempt}. Fix this Python code.\n\n"
                f"ERROR:\n{error[:3000]}\n\n"
                f"CODE:\n{code[:6000]}"
                f"{escalation}"
            ),
            temperature=0.1 + (attempt * 0.05),
            max_tokens=6000,
        )
        return fixed

    def _fingerprint_error(self, error: str) -> str:
        """Extract a short fingerprint of the error for loop detection."""
        lines = [l.strip() for l in error.split("\n") if l.strip()]
        for line in reversed(lines):
            if line.startswith(("Error", "Exception", "ValueError", "TypeError",
                               "AttributeError", "NameError", "ImportError")):
                return line[:100]
        return lines[-1][:100] if lines else error[:100]

    def _clean_code(self, code: str) -> str:
        """Strip markdown fences."""
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()
