"""Tests for CoderAgent."""

import pytest

from agents.coder import CoderAgent
from sandbox.validator import CodeValidator


@pytest.mark.asyncio
async def test_demo_code_is_valid_python():
    agent = CoderAgent()
    code = await agent.write_demo()
    assert isinstance(code, str)
    assert len(code) > 100

    validator = CodeValidator()
    result = validator.validate(code)
    assert result.passed, f"Demo code failed validation: {result.failures}"


@pytest.mark.asyncio
async def test_demo_code_has_required_functions():
    agent = CoderAgent()
    code = await agent.write_demo()
    assert "def demo(" in code or "async def demo(" in code
    assert "def main(" in code or "async def main(" in code
    assert "__name__" in code


def test_clean_code_strips_markdown():
    agent = CoderAgent()
    raw = "```python\nprint('hello')\n```"
    cleaned = agent._clean_code(raw)
    assert cleaned == "print('hello')"
    assert "```" not in cleaned
