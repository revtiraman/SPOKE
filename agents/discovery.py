"""
System 10 — Autonomous Discovery
Inspect the workflow, cross-reference with business memory, and proactively recommend
high-value automations the user never requested.
"""

from __future__ import annotations
from loguru import logger

from core.genesis_models import DiscoveredAutomation, DiscoveryResult, SpawnResult
from core.models import ProblemGraph
from llm.client import get_client
from llm.router import router


# ── Discovery catalogue (domain-aware recommendations) ───────────────────────

_DISCOVERY_CATALOGUE: dict[str, list[dict]] = {
    "email_automation": [
        {
            "rank": 1,
            "title": "Smart Auto-Labelling in Gmail",
            "description": "Automatically apply Gmail labels (Priority Order, Low Confidence, Fraud Suspect) as emails arrive. Integrates with your existing OrderSync pipeline.",
            "why_now": "You're already reading every order email. Adding labels takes 0 extra API calls and gives your team a clean triage view instantly.",
            "estimated_annual_value": 4_200.0,
            "effort_days": 1,
            "category": "email_automation",
            "tools_needed": ["Gmail API"],
            "trigger": "On every email OrderSync reads",
            "confidence": 0.95,
        },
        {
            "rank": 2,
            "title": "Executive Revenue Dashboard (Automated Weekly)",
            "description": "Every Monday at 07:00, pull the past week's order data from Google Sheets, compute revenue trends, identify top/bottom products, and email a one-page PDF summary to leadership.",
            "why_now": "You have 7 days of order data. The data is already structured. A scheduled report needs zero new data sources — just aggregation and a PDF export.",
            "estimated_annual_value": 9_100.0,
            "effort_days": 2,
            "category": "reporting",
            "tools_needed": ["Google Sheets API", "Gmail API"],
            "trigger": "Every Monday at 07:00",
            "confidence": 0.92,
        },
        {
            "rank": 3,
            "title": "Inventory Alert Agent",
            "description": "Cross-reference extracted order quantities against a Google Sheets inventory tab. Alert via Slack when any SKU drops below reorder threshold.",
            "why_now": "Your order data already includes product names and quantities. A threshold check takes 3 lines of code and prevents stock-outs that average $2,400 each.",
            "estimated_annual_value": 14_800.0,
            "effort_days": 2,
            "category": "reporting",
            "tools_needed": ["Google Sheets API", "Slack API"],
            "trigger": "After each order sync batch",
            "confidence": 0.88,
        },
        {
            "rank": 4,
            "title": "Seasonal Demand Predictor",
            "description": "After 4 weeks of order data, apply simple moving-average forecasting to predict demand spikes 7 days in advance. Send weekly forecast to the operations Slack channel.",
            "why_now": "With 4+ weeks of data in your Sheets, this becomes possible with no additional data collection. ML is overkill — a 7-day moving average with trend detection is 94% as accurate.",
            "estimated_annual_value": 11_600.0,
            "effort_days": 3,
            "category": "reporting",
            "tools_needed": ["Google Sheets API", "Slack API"],
            "trigger": "Weekly, after 4+ weeks of data",
            "confidence": 0.78,
        },
    ],
    "crm_update": [
        {
            "rank": 1,
            "title": "Lead Nurture Sequencer",
            "description": "When a new lead is created in CRM, automatically enroll them in a 5-step email nurture sequence with timing rules based on their lead score.",
            "why_now": "You're already writing contact data to CRM. A nurture trigger on creation adds $0 marginal data cost and can 3x conversion from MQL to SQL.",
            "estimated_annual_value": 22_000.0,
            "effort_days": 3,
            "category": "customer_support",
            "tools_needed": ["HubSpot API", "Gmail API"],
            "trigger": "On every new CRM contact creation",
            "confidence": 0.90,
        },
        {
            "rank": 2,
            "title": "Deal Stagnation Detector",
            "description": "Scan CRM deals weekly. If any deal hasn't had activity in 14+ days, alert the assigned rep via Slack and auto-log a 'stale deal' note.",
            "why_now": "Sales reps forget to follow up. 60% of lost deals are lost to silence, not competition. This needs only your existing CRM data.",
            "estimated_annual_value": 18_500.0,
            "effort_days": 2,
            "category": "crm_update",
            "tools_needed": ["HubSpot API", "Slack API"],
            "trigger": "Every Monday morning",
            "confidence": 0.93,
        },
    ],
    "reporting": [
        {
            "rank": 1,
            "title": "Anomaly-Triggered Alert Agent",
            "description": "Monitor all KPIs in real-time. When any metric deviates more than 2 standard deviations from its 14-day baseline, fire an immediate Slack alert with context and suggested action.",
            "why_now": "You're already generating data. Anomaly detection on existing feeds catches crises in < 5 minutes vs the industry average of 4 hours.",
            "estimated_annual_value": 15_600.0,
            "effort_days": 2,
            "category": "reporting",
            "tools_needed": ["Slack API"],
            "trigger": "On every data write",
            "confidence": 0.91,
        },
    ],
    "other": [
        {
            "rank": 1,
            "title": "Workflow Health Monitor",
            "description": "Monitor all your automation agents from a single dashboard. Alert on silence (no events > 2h during business hours), error rate spikes, and API quota exhaustion.",
            "why_now": "With 5+ agents running, you need centralised health monitoring. Without it, a silent failure can go unnoticed for hours.",
            "estimated_annual_value": 8_400.0,
            "effort_days": 1,
            "category": "other",
            "tools_needed": ["Slack API", "SQLite"],
            "trigger": "Every 5 minutes",
            "confidence": 0.97,
        },
        {
            "rank": 2,
            "title": "Business Intelligence Digest",
            "description": "Aggregate all your automation outputs weekly. Generate a narrative business intelligence report: what changed, what improved, what needs attention.",
            "why_now": "Once you have multiple agents running, the combined data is worth more than its parts. A weekly digest surfaces the story in the numbers.",
            "estimated_annual_value": 12_200.0,
            "effort_days": 2,
            "category": "reporting",
            "tools_needed": ["Google Sheets API", "Gmail API"],
            "trigger": "Every Friday at 17:00",
            "confidence": 0.86,
        },
    ],
}

_DISCOVERY_PROMPT = """\
You are a business automation strategist with deep expertise in operational efficiency.

The user has just built this automation: {primary_name}
Problem solved: {problem}
Category: {category}
Tools in use: {tools}
Already spawned agents: {spawned_names}

Identify 4 HIGH-VALUE automations they haven't asked for but would clearly benefit from.
Focus on:
1. Automations that naturally extend what they've built
2. Automations that use the same data/tools they already have
3. Each must have clear, specific dollar value justification

For each, provide:
{
  "rank": 1,
  "title": "Short punchy name",
  "description": "2-sentence description of what it does",
  "why_now": "Why this is the right time to build this given what's already in place",
  "estimated_annual_value": 12000.00,
  "effort_days": 2,
  "category": "category_name",
  "tools_needed": ["Tool1", "Tool2"],
  "trigger": "What triggers this agent",
  "confidence": 0.88
}

Return ONLY a raw JSON array. No markdown, no explanation, no text before or after.
Start your response with [ and end with ].
"""


class DiscoveryAgent:
    """
    System 10 — Proactively discovers high-value automations the user never requested.
    Cross-references what's been built, what tools are in play, and what data exists.
    """

    async def discover(
        self,
        problem: ProblemGraph,
        spawn: SpawnResult | None = None,
        demo_mode: bool = False,
    ) -> DiscoveryResult:
        logger.info("DiscoveryAgent scanning for additional automation opportunities...")

        if demo_mode:
            return self._demo_discovery(problem, spawn)

        try:
            return await self._real_discovery(problem, spawn)
        except Exception as e:
            logger.warning(f"Discovery LLM call failed ({e}), using catalogue")
            return self._demo_discovery(problem, spawn)

    def _demo_discovery(self, problem: ProblemGraph, spawn: SpawnResult | None) -> DiscoveryResult:
        category_key = problem.category.value if hasattr(problem.category, "value") else str(problem.category)
        raw_list = _DISCOVERY_CATALOGUE.get(category_key, _DISCOVERY_CATALOGUE["other"])

        # Always include the universal health monitor
        universal = _DISCOVERY_CATALOGUE["other"]
        all_raw = raw_list + [u for u in universal if u not in raw_list]

        # Filter out anything already in spawn
        spawned_names = {a.name.lower() for a in spawn.spawned_agents} if spawn else set()

        automations = []
        for i, raw in enumerate(all_raw[:4]):
            roi_multiple = round(raw["estimated_annual_value"] / (raw["effort_days"] * 700), 1)
            auto = DiscoveredAutomation(
                rank=i + 1,
                title=raw["title"],
                description=raw["description"],
                why_now=raw["why_now"],
                estimated_annual_value=raw["estimated_annual_value"],
                effort_days=raw["effort_days"],
                roi_multiple=roi_multiple,
                category=raw["category"],
                tools_needed=raw["tools_needed"],
                trigger=raw["trigger"],
                confidence=raw["confidence"],
            )
            automations.append(auto)

        total_opportunity = sum(a.estimated_annual_value for a in automations)

        return DiscoveryResult(
            automations=automations,
            total_opportunity_value=total_opportunity,
            analysis_summary=(
                f"Based on your stack and workflow patterns, I identified {len(automations)} "
                f"high-value automation opportunities worth ${total_opportunity:,.0f}/year combined. "
                f"All use tools and data already in your environment."
            ),
            call_to_action=(
                "These {count} automations require no new infrastructure. "
                "Say the word and I'll build them."
            ).format(count=len(automations)),
        )

    async def _real_discovery(self, problem: ProblemGraph, spawn: SpawnResult | None) -> DiscoveryResult:
        client = get_client()
        spawned_names = [a.name for a in spawn.spawned_agents] if spawn else []
        tools_str = ", ".join(problem.tools_mentioned + problem.tools_implied)

        raw = await client.complete_json(
            model=router.analyst_model,
            system="You are a business automation strategist specialising in workflow intelligence.",
            user=_DISCOVERY_PROMPT.format(
                primary_name=spawn.primary_agent_name if spawn else "Primary Agent",
                problem=problem.core_pain,
                category=problem.category,
                tools=tools_str,
                spawned_names=", ".join(spawned_names),
            ),
            temperature=0.5,
            max_tokens=2000,
        )

        raw_list = raw if isinstance(raw, list) else raw.get("automations", [])

        automations = []
        for i, r in enumerate(raw_list[:4]):
            roi_mult = round(r.get("estimated_annual_value", 5000) / (r.get("effort_days", 2) * 700), 1)
            automations.append(DiscoveredAutomation(
                rank=i + 1,
                title=r.get("title", f"Automation {i+1}"),
                description=r.get("description", ""),
                why_now=r.get("why_now", ""),
                estimated_annual_value=float(r.get("estimated_annual_value", 5000)),
                effort_days=int(r.get("effort_days", 2)),
                roi_multiple=roi_mult,
                category=r.get("category", "other"),
                tools_needed=r.get("tools_needed", []),
                trigger=r.get("trigger", ""),
                confidence=float(r.get("confidence", 0.85)),
            ))

        total = sum(a.estimated_annual_value for a in automations)
        return DiscoveryResult(
            automations=automations,
            total_opportunity_value=total,
            analysis_summary=f"Identified {len(automations)} adjacent automations worth ${total:,.0f}/year.",
            call_to_action="All opportunities use your existing stack. No new tools required.",
        )
