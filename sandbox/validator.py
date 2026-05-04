"""Code validator — safety-checks generated Python before execution."""

from __future__ import annotations
import ast
import re

from core.models import ValidationResult


_BLOCKED_PATTERNS = [
    (r"\bos\.system\s*\(", "os.system() call blocked"),
    (r"\bsubprocess\.call\s*\([^)]*shell\s*=\s*True", "subprocess with shell=True blocked"),
    (r"\bsubprocess\.Popen\s*\([^)]*shell\s*=\s*True", "subprocess with shell=True blocked"),
    (r"\bshutil\.rmtree\s*\(", "shutil.rmtree() blocked"),
    (r"\bos\.remove\s*\(.*etc|.*home|.*root|.*usr", "os.remove on system path blocked"),
    (r"\beval\s*\(\s*input\s*\(", "eval(input()) blocked"),
    (r"__import__\s*\(\s*['\"]os['\"]", "dynamic os import blocked"),
    (r"\brm\s+-rf\b", "rm -rf blocked"),
]

_REQUIRED_ELEMENTS = [
    ("def demo(", "demo() function required"),
    ("def main(", "main() function required"),
    ("if __name__", "__main__ block required"),
]


class CodeValidator:
    """Validates generated Python code for safety and completeness."""

    def validate(self, code: str) -> ValidationResult:
        """Run all validation checks. Returns ValidationResult."""
        failures: list[str] = []

        # Syntax check
        try:
            ast.parse(code)
        except SyntaxError as e:
            failures.append(f"SyntaxError: {e}")
            return ValidationResult(passed=False, failures=failures)

        # Safety checks
        for pattern, message in _BLOCKED_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                failures.append(message)

        # Completeness checks
        for pattern, message in _REQUIRED_ELEMENTS:
            if pattern not in code:
                failures.append(message)

        # Demo mode check — warn but don't block
        if "SPOKE_DEMO" not in code:
            # Not a hard failure, just warn
            pass

        return ValidationResult(passed=len(failures) == 0, failures=failures)

    def check_syntax(self, code: str) -> bool:
        """Quick syntax check only."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
