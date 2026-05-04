"""Tests for ExecutorAgent and CodeValidator."""

import pytest

from agents.executor import ExecutorAgent
from sandbox.validator import CodeValidator


SIMPLE_DEMO_CODE = '''
import argparse
import asyncio

async def demo():
    print("Spoke Demo: 3 orders processed")
    print("  Customer: John Smith | Product: Widget | $49.99")
    print("Done!")

async def main():
    print("Production mode")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="demo")
    args = parser.parse_args()
    asyncio.run(demo() if args.mode == "demo" else main())
'''


@pytest.mark.asyncio
async def test_executor_runs_simple_code():
    executor = ExecutorAgent()
    result = await executor.execute(SIMPLE_DEMO_CODE, timeout=30)
    assert result.success
    assert "Spoke Demo" in result.stdout
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_executor_captures_failure():
    executor = ExecutorAgent()
    bad_code = "import nonexistent_module_xyz\nprint('never reached')"
    result = await executor.execute(bad_code, timeout=30)
    assert not result.success
    assert result.exit_code != 0


def test_validator_passes_valid_code():
    validator = CodeValidator()
    result = validator.validate(SIMPLE_DEMO_CODE)
    assert result.passed


def test_validator_blocks_os_system():
    validator = CodeValidator()
    bad = "import os\nos.system('rm -rf /')\ndef demo(): pass\ndef main(): pass\nif __name__: pass"
    result = validator.validate(bad)
    assert not result.passed
    assert any("os.system" in f for f in result.failures)


def test_validator_catches_syntax_error():
    validator = CodeValidator()
    result = validator.validate("def broken(\n  print('oops'")
    assert not result.passed
    assert any("Syntax" in f for f in result.failures)
