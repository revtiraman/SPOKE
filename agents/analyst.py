"""Agent 2 — Analyst: extracts a structured problem graph from transcript text."""

from __future__ import annotations
from pathlib import Path

from loguru import logger

from core.models import ProblemGraph, AgentCategory
from llm.client import get_client
from llm.router import router


_PROMPT_PATH = Path(__file__).parent.parent / "llm" / "prompts" / "analyst_prompt.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()

_DEMO_PROBLEM = ProblemGraph(
    core_pain="manually copying order data from Gmail emails into Google Sheets",
    trigger="new email arrives in Gmail with subject line containing 'order' or 'purchase'",
    process_steps=[
        "Open Gmail inbox",
        "Find unread emails with order-related subjects",
        "Open each email individually",
        "Read and mentally parse: customer name, product, quantity, price, date",
        "Switch to Google Sheets tab",
        "Scroll to next empty row",
        "Type each field into the correct column",
        "Switch back to Gmail and mark email as read",
        "Repeat for every order email",
    ],
    tools_mentioned=["Gmail", "Google Sheets"],
    tools_implied=["Google Workspace", "Chrome browser"],
    frequency="daily",
    estimated_hours_per_week=10.0,
    data_fields=["customer_name", "product_name", "quantity", "total_price", "order_date", "email_subject", "email_id"],
    output="spreadsheet row with complete order information for accounting and fulfillment",
    success_condition="new orders appear in Google Sheets automatically within 2 minutes of email arrival, with no manual work",
    category=AgentCategory.EMAIL_AUTOMATION,
    complexity_score=2,
    confidence=0.94,
    missing_information=["which Gmail address to monitor", "exact Google Sheets column layout"],
)


class AnalystAgent:
    """Extracts a structured ProblemGraph from a business transcript."""

    async def analyse(self, transcript: str) -> ProblemGraph:
        """Analyse the transcript and return a structured problem graph."""
        logger.info("Analysing transcript with main brain model...")

        client = get_client()
        raw = await client.complete_json(
            model=router.analyst_model,
            system=_SYSTEM_PROMPT,
            user=f"Analyse this business problem description:\n\n{transcript}",
            temperature=0.2,
            max_tokens=2048,
        )

        problem = self._parse_problem(raw)
        logger.success(
            f"Problem analysed — category: {problem.category}, "
            f"complexity: {problem.complexity_score}/5, "
            f"confidence: {problem.confidence:.0%}"
        )
        return problem

    async def refine(self, problem: ProblemGraph, answers: dict[str, str]) -> ProblemGraph:
        """Refine a problem graph with clarification answers."""
        logger.info("Refining problem graph with clarification answers...")

        answers_text = "\n".join(f"Q: {q}\nA: {a}" for q, a in answers.items())
        client = get_client()
        raw = await client.complete_json(
            model=router.analyst_model,
            system=_SYSTEM_PROMPT,
            user=(
                f"Original problem graph:\n{problem.model_dump_json(indent=2)}\n\n"
                f"Clarification answers:\n{answers_text}\n\n"
                "Update the problem graph with this new information. Return the complete updated JSON."
            ),
            temperature=0.1,
            max_tokens=2048,
        )
        refined = self._parse_problem(raw)
        refined.confidence = min(1.0, refined.confidence + 0.1)
        refined.missing_information = []
        logger.success(f"Problem refined — confidence now {refined.confidence:.0%}")
        return refined

    def _parse_problem(self, raw: dict) -> ProblemGraph:
        """Parse raw LLM JSON into a ProblemGraph, with safe fallbacks."""
        # Normalise category
        cat_raw = str(raw.get("category", "other")).lower().replace(" ", "_").replace("-", "_")
        try:
            category = AgentCategory(cat_raw)
        except ValueError:
            category = AgentCategory.OTHER

        return ProblemGraph(
            core_pain=raw.get("core_pain", "automate a repetitive business task"),
            trigger=raw.get("trigger", "manual trigger"),
            process_steps=raw.get("process_steps", []),
            tools_mentioned=raw.get("tools_mentioned", []),
            tools_implied=raw.get("tools_implied", []),
            frequency=raw.get("frequency", "daily"),
            estimated_hours_per_week=float(raw.get("estimated_hours_per_week", 2)),
            data_fields=raw.get("data_fields", []),
            output=raw.get("output", ""),
            success_condition=raw.get("success_condition", ""),
            category=category,
            complexity_score=int(raw.get("complexity_score", 2)),
            confidence=float(raw.get("confidence", 0.8)),
            missing_information=raw.get("missing_information", []),
        )

    async def analyse_demo(self) -> ProblemGraph:
        """Return demo problem graph instantly without API call."""
        logger.info("[DEMO] Returning pre-built problem graph")
        return _DEMO_PROBLEM
