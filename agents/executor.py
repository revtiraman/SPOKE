"""Agent 6 — Executor: runs generated Python code in a safe sandbox."""

from __future__ import annotations
import asyncio
import os
import subprocess
import tempfile
import time
from pathlib import Path

from loguru import logger

from core.config import settings
from core.models import ExecutionResult
from sandbox.validator import CodeValidator


class ExecutorAgent:
    """Executes generated Python code in a sandboxed environment."""

    def __init__(self):
        self.validator = CodeValidator()
        self.sandbox_type = settings.sandbox_type

    async def execute(
        self,
        code: str,
        timeout: int | None = None,
        attempt: int = 1,
    ) -> ExecutionResult:
        """Execute code in demo mode. Returns stdout, stderr, success flag."""
        timeout = timeout or settings.execution_timeout_seconds
        logger.info(f"Executing code (attempt {attempt}, sandbox: {self.sandbox_type})...")

        # Validate before running
        validation = self.validator.validate(code)
        if not validation.passed:
            logger.warning(f"Validation failures: {validation.failures}")

        t0 = time.perf_counter()

        if self.sandbox_type == "e2b" and settings.has_e2b:
            result = await self._execute_e2b(code, timeout)
        else:
            result = await self._execute_subprocess(code, timeout)

        result.duration_seconds = time.perf_counter() - t0
        result.attempt = attempt

        if result.success:
            logger.success(f"Execution succeeded in {result.duration_seconds:.1f}s")
        else:
            logger.warning(f"Execution failed in {result.duration_seconds:.1f}s")
            logger.debug(f"stderr: {result.stderr[:500]}")

        return result

    async def _execute_subprocess(self, code: str, timeout: int) -> ExecutionResult:
        """Execute code in a local subprocess with timeout."""
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).parent.parent)
            env["PYTHONUNBUFFERED"] = "1"

            proc = await asyncio.create_subprocess_exec(
                "python3", tmp_path, "--mode", "demo",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return ExecutionResult(
                    success=False,
                    stderr=f"Execution timed out after {timeout}s",
                    exit_code=-1,
                )

            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")

            return ExecutionResult(
                success=proc.returncode == 0,
                stdout=stdout_text,
                stderr=stderr_text,
                exit_code=proc.returncode or 0,
            )
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    async def _execute_e2b(self, code: str, timeout: int) -> ExecutionResult:
        """Execute code in E2B cloud sandbox."""
        try:
            import e2b
            async with e2b.Sandbox() as sandbox:
                await sandbox.filesystem.write("/agent.py", code)
                await sandbox.process.start_and_wait(
                    "pip install loguru rich tenacity pydantic python-dotenv -q",
                    timeout=60,
                )
                result = await sandbox.process.start_and_wait(
                    "python /agent.py --mode demo",
                    timeout=timeout,
                )
                return ExecutionResult(
                    success=result.exit_code == 0,
                    stdout=result.stdout or "",
                    stderr=result.stderr or "",
                    exit_code=result.exit_code,
                )
        except Exception as e:
            logger.error(f"E2B execution failed: {e} — falling back to subprocess")
            return await self._execute_subprocess(code, timeout)

    async def execute_demo(self, code: str) -> ExecutionResult:
        """Execute demo code directly."""
        return await self.execute(code, timeout=60, attempt=1)
