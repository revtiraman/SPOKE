"""Agent 3 — Clarifier: generates targeted follow-up questions to fill knowledge gaps."""

from __future__ import annotations
from pathlib import Path

from loguru import logger

from core.models import ProblemGraph, ClarificationQuestions
from llm.client import get_client
from llm.router import router


_PROMPT_PATH = Path(__file__).parent.parent / "llm" / "prompts" / "clarifier_prompt.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()

_CONFIDENCE_THRESHOLD = 0.85


class ClarifierAgent:
    """Determines whether clarification is needed and generates targeted questions."""

    async def generate_questions(self, problem: ProblemGraph) -> ClarificationQuestions:
        """Generate 2 clarifying questions based on missing information."""
        if self._should_skip(problem):
            logger.info(f"Skipping clarification — confidence {problem.confidence:.0%} is sufficient")
            return ClarificationQuestions(
                questions=[],
                skip_reason=f"Confidence {problem.confidence:.0%} — sufficient to proceed",
            )

        logger.info(f"Generating clarifying questions (confidence: {problem.confidence:.0%})...")

        context = (
            f"Problem: {problem.core_pain}\n"
            f"Category: {problem.category}\n"
            f"Tools: {', '.join(problem.tools_mentioned + problem.tools_implied)}\n"
            f"Missing info: {', '.join(problem.missing_information)}\n"
            f"Confidence: {problem.confidence:.0%}"
        )

        client = get_client()
        raw = await client.complete_json(
            model=router.clarifier_model,
            system=_SYSTEM_PROMPT,
            user=f"Generate 2 clarifying questions for this automation request:\n\n{context}",
            temperature=0.4,
            max_tokens=256,
        )

        questions = self._parse_questions(raw)
        logger.success(f"Generated {len(questions)} clarifying questions")
        return ClarificationQuestions(questions=questions)

    def _should_skip(self, problem: ProblemGraph) -> bool:
        return problem.confidence >= _CONFIDENCE_THRESHOLD and not problem.missing_information

    def _parse_questions(self, raw) -> list[str]:
        if isinstance(raw, list):
            return [str(q) for q in raw[:2]]
        if isinstance(raw, dict):
            for key in ("questions", "data", "result"):
                if key in raw and isinstance(raw[key], list):
                    return [str(q) for q in raw[key][:2]]
        return ["Which account or service should I connect to?", "Any specific format or naming convention for the output?"]

    async def generate_demo(self) -> ClarificationQuestions:
        """Return demo questions instantly."""
        return ClarificationQuestions(
            questions=[
                "Which Gmail address receives the order emails?",
                "What are the column headers in your Google Sheet (from left to right)?",
            ]
        )
