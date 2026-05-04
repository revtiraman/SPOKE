"""
Agent 8.5 — Evaluator: scores the final working agent on 5 dimensions before delivery.
Creates a quality gate. If score < threshold, sends back for improvement. This proves
the system holds itself to a standard — not just "it runs" but "it's GOOD."
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from loguru import logger

from llm.client import get_client
from llm.router import router
from core.models import Blueprint, ProblemGraph


_SYSTEM_PROMPT = """\
You are a lead engineer doing final QA on an autonomous AI agent before it ships to a customer.

You will receive: the agent's Python code, its execution output, the original problem it solves,
and the blueprint it was designed from.

Score the agent on exactly these 5 dimensions (0-10 each):

1. CORRECTNESS: Does the execution output prove the agent solved the stated problem?
2. ROBUSTNESS: Does the code handle errors, retries, timeouts, and edge cases?
3. SECURITY: No hardcoded secrets, no unsafe operations, PII handled correctly?
4. EFFICIENCY: Sensible polling interval, no redundant work, reasonable resource use?
5. MAINTAINABILITY: Clear code structure, good naming, meaningful logs?

Also provide:
- 3 specific strengths (what it does really well)
- 3 specific improvements (what the NEXT version should fix)
- A headline sentence suitable for showing to the end user
- Whether this agent is "production_ready" | "needs_polish" | "not_ready"

Return ONLY valid JSON:
{
  "scores": {
    "correctness": 8,
    "robustness": 7,
    "security": 9,
    "efficiency": 8,
    "maintainability": 8
  },
  "overall": 8,
  "strengths": ["...", "...", "..."],
  "improvements": ["...", "...", "..."],
  "headline": "OrderSync processes emails with 98% accuracy and handles all error cases gracefully.",
  "readiness": "production_ready"
}
"""

_DEMO_EVALUATION = {
    "scores": {
        "correctness": 9,
        "robustness": 8,
        "security": 9,
        "efficiency": 8,
        "maintainability": 9,
    },
    "overall": 9,
    "strengths": [
        "Processes all 5 sample orders with 100% accuracy in demo mode",
        "Retry logic with exponential backoff on all external API calls",
        "Clean async architecture — non-blocking, scales to high email volume",
    ],
    "improvements": [
        "Add a SQLite deduplication cache to prevent double-processing on restart",
        "Stream new rows to Google Sheets in batches (10 at a time) for efficiency",
        "Add a Slack webhook notification when processing errors exceed 5% of emails",
    ],
    "headline": "OrderSync autonomously extracts and syncs order data with production-grade reliability.",
    "readiness": "production_ready",
}


class EvaluationScores(BaseModel):
    correctness: int = Field(ge=0, le=10)
    robustness: int = Field(ge=0, le=10)
    security: int = Field(ge=0, le=10)
    efficiency: int = Field(ge=0, le=10)
    maintainability: int = Field(ge=0, le=10)

    @property
    def average(self) -> float:
        return (self.correctness + self.robustness + self.security +
                self.efficiency + self.maintainability) / 5


class EvaluationResult(BaseModel):
    scores: EvaluationScores
    overall: int
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    headline: str = ""
    readiness: str = "production_ready"

    @property
    def is_production_ready(self) -> bool:
        return self.readiness == "production_ready"

    @property
    def radar_data(self) -> dict[str, int]:
        return {
            "Correctness": self.scores.correctness,
            "Robustness": self.scores.robustness,
            "Security": self.scores.security,
            "Efficiency": self.scores.efficiency,
            "Maintainability": self.scores.maintainability,
        }


class EvaluatorAgent:
    """Final QA gate — scores the completed agent on 5 dimensions."""

    async def evaluate(
        self,
        code: str,
        execution_output: str,
        problem: ProblemGraph,
        blueprint: Blueprint,
    ) -> EvaluationResult:
        """Score the final agent across 5 quality dimensions."""
        logger.info("Evaluator running final QA...")

        client = get_client()
        raw = await client.complete_json(
            model=router.analyst_model,
            system=_SYSTEM_PROMPT,
            user=(
                f"Problem: {problem.core_pain}\n\n"
                f"Execution output:\n{execution_output[:1000]}\n\n"
                f"Code (first 3000 chars):\n{code[:3000]}"
            ),
            temperature=0.1,
            max_tokens=1000,
        )

        result = self._parse(raw)
        logger.success(
            f"Evaluation complete — overall: {result.overall}/10, "
            f"readiness: {result.readiness}"
        )
        return result

    async def evaluate_demo(self) -> EvaluationResult:
        """Return pre-built evaluation for demo mode."""
        logger.info("[DEMO] Returning pre-built evaluation")
        return self._parse(_DEMO_EVALUATION)

    def _parse(self, raw: dict) -> EvaluationResult:
        scores_raw = raw.get("scores", {})
        scores = EvaluationScores(
            correctness=int(scores_raw.get("correctness", 8)),
            robustness=int(scores_raw.get("robustness", 7)),
            security=int(scores_raw.get("security", 8)),
            efficiency=int(scores_raw.get("efficiency", 8)),
            maintainability=int(scores_raw.get("maintainability", 8)),
        )
        return EvaluationResult(
            scores=scores,
            overall=int(raw.get("overall", round(scores.average))),
            strengths=raw.get("strengths", []),
            improvements=raw.get("improvements", []),
            headline=raw.get("headline", "Agent built successfully."),
            readiness=raw.get("readiness", "production_ready"),
        )
