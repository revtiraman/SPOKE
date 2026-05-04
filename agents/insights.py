"""
InsightsEngine — runs alongside the Analyst to surface proactive observations
the user never thought to mention. This is the "wow, it caught that" moment.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from loguru import logger

from core.models import ProblemGraph
from llm.client import get_client
from llm.router import router


_SYSTEM_PROMPT = """\
You are an expert automation consultant. A user has described a business problem and an AI
has already extracted a structured problem graph. Your job is to surface PROACTIVE INSIGHTS —
things the user didn't mention but you know from experience will matter.

Generate 3-5 insights, each one should be SURPRISING and SPECIFIC. Not generic advice.

Types of insights to look for:
- EDGE CASE: "What happens when X? You didn't mention it, but I've handled it."
- RATE_LIMIT: "The API you're using has a limit of X/day. Your use case needs Y. Here's how I handle it."
- PRIVACY: "You're processing customer email data. I've added PII masking for compliance."
- COST_SAVING: "Using approach A instead of B will save you $X/month."
- ENHANCEMENT: "I noticed you only mentioned extracting Y. I've also extracted Z which you'll probably need."
- RELIABILITY: "This workflow will fail silently if X happens. I've added a fallback."
- PERFORMANCE: "At your stated frequency, you'll hit 10,000 operations/month. I've optimised for that."

Return ONLY valid JSON array:
[
  {
    "type": "EDGE_CASE",
    "icon": "⚠️",
    "title": "What happens when an email has no price?",
    "body": "About 8% of order emails omit the price (discounts, free samples). I've added a fallback that flags these for manual review instead of writing $0.00 to your spreadsheet.",
    "impact": "Prevents 8% data corruption"
  }
]
"""

_DEMO_INSIGHTS = [
    {
        "type": "ENHANCEMENT",
        "icon": "💡",
        "title": "I extended your email filter beyond 'order'",
        "body": "I noticed emails might also contain 'purchase', 'invoice', or 'receipt'. I've added all four keywords to the filter — this typically catches 23% more orders than a single keyword.",
        "impact": "+23% coverage"
    },
    {
        "type": "EDGE_CASE",
        "icon": "⚠️",
        "title": "Duplicate protection added automatically",
        "body": "If your agent restarts mid-run, it would reprocess already-handled emails without protection. I've added a local SQLite cache of processed email IDs. Zero duplicates in your spreadsheet.",
        "impact": "Zero duplicate rows"
    },
    {
        "type": "RELIABILITY",
        "icon": "🛡️",
        "title": "Silent failure protection",
        "body": "Without monitoring, the agent could stop working and you'd never know. I've added a self-monitoring heartbeat — if the agent fails 3 consecutive runs, it emails you an alert automatically.",
        "impact": "Mean time to notice: < 3 minutes"
    },
    {
        "type": "PRIVACY",
        "icon": "🔒",
        "title": "Customer PII handled carefully",
        "body": "Email bodies contain customer names and contact details. I've ensured only the extracted structured fields (name, product, amount) are logged — full email content is never written to disk.",
        "impact": "GDPR-aligned logging"
    },
]


class Insight(BaseModel):
    type: str
    icon: str = "💡"
    title: str
    body: str
    impact: str = ""


class InsightsResult(BaseModel):
    insights: list[Insight] = Field(default_factory=list)


class InsightsEngine:
    """Surfaces proactive observations the user didn't think to mention."""

    async def generate(self, problem: ProblemGraph) -> InsightsResult:
        """Generate proactive insights from a problem graph."""
        logger.info("InsightsEngine generating proactive observations...")

        client = get_client()
        raw = await client.complete_json(
            model=router.clarifier_model,
            system=_SYSTEM_PROMPT,
            user=(
                f"Problem: {problem.core_pain}\n"
                f"Tools: {', '.join(problem.tools_mentioned + problem.tools_implied)}\n"
                f"Steps: {'; '.join(problem.process_steps[:5])}\n"
                f"Data fields: {', '.join(problem.data_fields)}\n"
                f"Frequency: {problem.frequency}"
            ),
            temperature=0.5,
            max_tokens=1000,
        )

        insights = self._parse(raw)
        logger.success(f"Generated {len(insights.insights)} proactive insights")
        return insights

    async def generate_demo(self) -> InsightsResult:
        """Return demo insights instantly."""
        return InsightsResult(insights=[Insight(**i) for i in _DEMO_INSIGHTS])

    def _parse(self, raw) -> InsightsResult:
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict):
            items = raw.get("insights", raw.get("data", [raw]))
        else:
            items = []

        insights = []
        for item in items[:5]:
            if isinstance(item, dict):
                insights.append(Insight(
                    type=item.get("type", "INFO"),
                    icon=item.get("icon", "💡"),
                    title=item.get("title", ""),
                    body=item.get("body", ""),
                    impact=item.get("impact", ""),
                ))
        return InsightsResult(insights=insights)
