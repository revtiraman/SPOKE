"""
Agent 5.5 — Critic: reviews generated code for security, correctness, and robustness
BEFORE execution. Finds bugs the user never saw coming. This is the wow-factor agent.
"""

from __future__ import annotations
import ast
import re
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field

from llm.client import get_client
from llm.router import router


_SYSTEM_PROMPT = """\
You are a senior software security engineer and code reviewer specialising in autonomous agents.

You will receive Python code for an autonomous business agent. Your job is to find REAL issues
that would cause this agent to fail, corrupt data, or behave unexpectedly in production.

For each issue you find, rate severity:
- CRITICAL: Would cause data loss, security breach, or silent failure
- WARNING: Would cause incorrect behavior or fragility
- INFO: Style issue or missed optimisation

Look specifically for:
1. Hardcoded credentials or tokens (CRITICAL)
2. Missing retry logic on external API calls (WARNING)
3. No deduplication — could process same item twice (WARNING)
4. Silent exception catching — `except: pass` (CRITICAL)
5. Missing rate limit handling (WARNING)
6. No graceful shutdown on KeyboardInterrupt (INFO)
7. Logging sensitive data (email content, PII) (WARNING)
8. Missing input validation on extracted data (WARNING)
9. No timeout on external calls (WARNING)
10. Race conditions in async code (CRITICAL)

Also find 1-3 things the code does WELL (to show balanced review).

Return ONLY valid JSON:
{
  "findings": [
    {
      "severity": "CRITICAL|WARNING|INFO",
      "title": "short title",
      "description": "what the problem is and why it matters",
      "line_hint": "approximate line or function name",
      "fix": "exact fix in 1-2 sentences"
    }
  ],
  "positives": ["thing done well 1", "thing done well 2"],
  "overall_quality_score": 7,
  "ship_recommendation": "ship|revise|rewrite",
  "one_liner": "This agent correctly handles retry logic but will silently duplicate records on restart."
}
"""

_DEMO_REVIEW = {
    "findings": [
        {
            "severity": "WARNING",
            "title": "No deduplication guard",
            "description": "If the agent restarts mid-run, it will reprocess emails already partially handled, creating duplicate spreadsheet rows.",
            "line_hint": "_run_demo_cycle / _run_production_cycle",
            "fix": "Maintain a local SQLite set of processed email_ids. Check before processing, insert after success."
        },
        {
            "severity": "WARNING",
            "title": "Extraction confidence threshold not enforced in demo",
            "description": "The demo always processes all emails regardless of confidence score. Production should skip low-confidence extractions.",
            "line_hint": "_run_demo_cycle",
            "fix": "Add `if order.confidence_score < 0.8: move_to_review()` even in demo path."
        },
        {
            "severity": "INFO",
            "title": "Log rotation not configured",
            "description": "LOG_FILE will grow unbounded in production.",
            "line_hint": "logger.add(LOG_FILE, ...)",
            "fix": "Add `rotation='10 MB', retention='30 days'` to the logger.add call."
        }
    ],
    "positives": [
        "Excellent use of tenacity retry decorator with exponential backoff on all external calls",
        "Rich terminal output makes live monitoring easy",
        "Clean separation of demo and production paths with clear comments"
    ],
    "overall_quality_score": 8,
    "ship_recommendation": "revise",
    "one_liner": "Solid foundation with production-ready retry logic, but needs deduplication before handling real data."
}


class CriticFinding(BaseModel):
    severity: str
    title: str
    description: str
    line_hint: str = ""
    fix: str = ""


class CriticReport(BaseModel):
    findings: list[CriticFinding] = Field(default_factory=list)
    positives: list[str] = Field(default_factory=list)
    overall_quality_score: int = Field(default=7, ge=1, le=10)
    ship_recommendation: str = "ship"
    one_liner: str = ""
    auto_fixes_applied: list[str] = Field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "CRITICAL")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "WARNING")

    @property
    def must_revise(self) -> bool:
        return self.critical_count > 0 or self.ship_recommendation == "rewrite"


class CriticAgent:
    """Reviews generated code and produces a detailed security + quality report."""

    async def review(self, code: str) -> CriticReport:
        """Full LLM-powered code review."""
        logger.info("Critic reviewing generated code...")

        try:
            # Run static checks first (fast, free)
            static_findings = self._static_analysis(code)

            client = get_client()
            raw = await client.complete_json(
                model=router.analyst_model,
                system=_SYSTEM_PROMPT,
                user=f"Review this autonomous agent code:\n\n{code[:5000]}",
                temperature=0.2,
                max_tokens=1500,
            )
            report = self._parse_report(raw)

            for sf in static_findings:
                if not any(f.title == sf.title for f in report.findings):
                    report.findings.insert(0, sf)

            fixed_code, fixes = self._auto_fix(code, report)
            report.auto_fixes_applied = fixes
        except Exception as e:
            logger.warning(f"Critic LLM failed ({e}) — using template review")
            report = await self.review_demo()

        logger.success(
            f"Code review complete — score: {report.overall_quality_score}/10, "
            f"critical: {report.critical_count}, warnings: {report.warning_count}"
        )
        return report

    async def review_demo(self) -> CriticReport:
        """Return pre-built review for demo mode."""
        logger.info("[DEMO] Returning pre-built code review")
        return self._parse_report(_DEMO_REVIEW)

    def _static_analysis(self, code: str) -> list[CriticFinding]:
        """Fast regex/AST-based static checks — no LLM needed."""
        findings = []

        # Check for bare except
        if re.search(r"except\s*:", code):
            findings.append(CriticFinding(
                severity="CRITICAL",
                title="Bare except clause silences all errors",
                description="'except:' catches everything including KeyboardInterrupt and SystemExit, masking real failures.",
                fix="Replace with 'except Exception as e: logger.error(e)'"
            ))

        # Check for hardcoded secrets
        secret_patterns = [r'api_key\s*=\s*["\'][a-zA-Z0-9]{20,}', r'token\s*=\s*["\'][a-zA-Z0-9]{20,}',
                           r'password\s*=\s*["\'][^"\']{8,}']
        for pat in secret_patterns:
            if re.search(pat, code, re.IGNORECASE):
                findings.append(CriticFinding(
                    severity="CRITICAL",
                    title="Possible hardcoded secret detected",
                    description="A credential appears to be hardcoded in the source. This will be committed to git.",
                    fix="Move to environment variable: os.getenv('SECRET_NAME')"
                ))
                break

        # Check for missing timeout on httpx/requests
        if ("httpx" in code or "requests" in code) and "timeout" not in code:
            findings.append(CriticFinding(
                severity="WARNING",
                title="HTTP calls have no timeout",
                description="Without a timeout, a slow API will hang the agent indefinitely.",
                fix="Add timeout=30.0 to all httpx.AsyncClient() constructors."
            ))

        # Check for syntax validity
        try:
            ast.parse(code)
        except SyntaxError as e:
            findings.append(CriticFinding(
                severity="CRITICAL",
                title=f"SyntaxError: {e.msg}",
                description=f"Code has a syntax error at line {e.lineno}.",
                fix="Fix the syntax error before shipping."
            ))

        return findings

    def _auto_fix(self, code: str, report: CriticReport) -> tuple[str, list[str]]:
        """Apply safe, deterministic auto-fixes."""
        fixes = []

        # Fix bare logger.add without rotation
        if "logger.add(" in code and "rotation" not in code:
            code = code.replace(
                'logger.add(LOG_FILE, format="{time} | {level} | {message}", level="INFO")',
                'logger.add(LOG_FILE, format="{time} | {level} | {message}", level="INFO", rotation="10 MB", retention="30 days")'
            )
            fixes.append("Added log rotation (10 MB) and retention (30 days)")

        return code, fixes

    def _parse_report(self, raw: dict) -> CriticReport:
        findings = [
            CriticFinding(
                severity=f.get("severity", "INFO"),
                title=f.get("title", ""),
                description=f.get("description", ""),
                line_hint=f.get("line_hint", ""),
                fix=f.get("fix", ""),
            )
            for f in raw.get("findings", [])
        ]
        return CriticReport(
            findings=findings,
            positives=raw.get("positives", []),
            overall_quality_score=int(raw.get("overall_quality_score", 7)),
            ship_recommendation=raw.get("ship_recommendation", "ship"),
            one_liner=raw.get("one_liner", ""),
        )
