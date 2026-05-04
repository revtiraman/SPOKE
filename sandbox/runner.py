"""Sandbox runner — thin wrapper that picks the right execution strategy."""

from __future__ import annotations

from core.config import settings
from core.models import ExecutionResult


class SandboxRunner:
    """Selects and runs the appropriate sandbox based on config."""

    def __init__(self):
        self.sandbox_type = settings.sandbox_type

    async def run(self, code: str, timeout: int | None = None) -> ExecutionResult:
        """Execute code in the configured sandbox."""
        from agents.executor import ExecutorAgent
        executor = ExecutorAgent()
        return await executor.execute(code, timeout=timeout)
