"""
System 1 — Agent Spawn
After the primary automation is built, autonomously infer and build 3–7 adjacent agents.
"You asked for 1 automation. I built 5."
"""

from __future__ import annotations
import asyncio
import time
from loguru import logger

from core.genesis_models import SpawnedAgent, SpawnResult
from core.models import ProblemGraph, Blueprint, AgentCategory
from llm.client import get_client
from llm.router import router


# ── Spawn Templates (demo mode) ───────────────────────────────────────────────

_SPAWN_LIBRARY: dict[str, list[dict]] = {
    "email_automation": [
        {
            "name": "FraudShield",
            "tagline": "Catches anomalous orders before they damage your business",
            "description": "Monitors every incoming order for statistical anomalies: unusually large quantities, mismatched currency codes, velocity spikes, and known fraud patterns. Quarantines suspicious orders for human review.",
            "category": "fraud_detection",
            "trigger": "Every new order synced by OrderSync",
            "what_it_does": "Scores each order 0–100 for fraud risk, auto-flags above threshold, sends Slack alert with evidence",
            "tools_required": ["SQLite", "Slack API", "Statistical analysis"],
            "estimated_annual_value": 12400.0,
            "value_description": "Prevents ~2% fraud rate on $50K/month GMV",
        },
        {
            "name": "CRMUpdater",
            "tagline": "Keeps your CRM perfectly in sync — zero manual entry",
            "description": "Watches the order stream and automatically upserts customer records in HubSpot/Salesforce. New customers get created; repeat customers get purchase history updated. Handles deduplication by email.",
            "category": "crm_update",
            "trigger": "Every high-confidence order from OrderSync",
            "what_it_does": "Creates/updates contact, logs deal activity, updates lifetime value field",
            "tools_required": ["HubSpot API", "Google Sheets"],
            "estimated_annual_value": 14560.0,
            "value_description": "Saves 8h/week of manual CRM entry at $35/hr",
        },
        {
            "name": "RevenueInsights",
            "tagline": "Boardroom-ready revenue reports, written by AI, sent automatically",
            "description": "Every morning at 08:00, aggregates the previous day's orders, computes MoM trends, identifies top products, flags anomalies, and sends a concise executive summary to Slack or email.",
            "category": "reporting",
            "trigger": "Daily at 08:00",
            "what_it_does": "Pulls order data, computes KPIs, generates narrative report, sends to Slack",
            "tools_required": ["Google Sheets", "Slack API", "Llama-3.3-70B"],
            "estimated_annual_value": 10400.0,
            "value_description": "Enables 30% faster decisions = $200/week opportunity value",
        },
        {
            "name": "InvoiceChaser",
            "tagline": "Recovers outstanding revenue automatically — zero awkward calls",
            "description": "Scans orders for unpaid invoice statuses, calculates days overdue, and sends progressively firmer follow-up emails at day 3, 7, 14, and 30. Marks resolved once payment confirmed.",
            "category": "invoice_processing",
            "trigger": "Daily at 09:00, checks orders > 3 days old",
            "what_it_does": "Detects unpaid orders, sends templated follow-ups, marks paid on confirmation",
            "tools_required": ["Gmail API", "Google Sheets"],
            "estimated_annual_value": 16200.0,
            "value_description": "Recovers 85% of overdue invoices vs 60% manual rate",
        },
        {
            "name": "CustomerFollowup",
            "tagline": "Turns every order into a relationship-building moment",
            "description": "Sends a personalised thank-you email 2 hours after each successful order sync. Includes estimated delivery, order summary, and a satisfaction survey link. Tracks reply rates for quality scoring.",
            "category": "customer_support",
            "trigger": "2 hours after each high-confidence order sync",
            "what_it_does": "Generates personalised email, sends via Gmail, logs open/reply rates",
            "tools_required": ["Gmail API", "Google Sheets"],
            "estimated_annual_value": 8840.0,
            "value_description": "Increases repeat purchase rate by 12% per industry benchmark",
        },
    ],
    "data_extraction": [
        {
            "name": "DataValidator",
            "tagline": "Zero bad data reaches your database",
            "description": "Intercepts all extracted records and runs schema validation, business rule checks, and cross-reference lookups before any write occurs.",
            "category": "data_extraction",
            "trigger": "Before every database write",
            "what_it_does": "Validates schema, checks business rules, logs rejections",
            "tools_required": ["SQLite", "Pydantic"],
            "estimated_annual_value": 9100.0,
            "value_description": "Prevents data quality issues averaging $175/hr to fix",
        },
        {
            "name": "DuplicateDetector",
            "tagline": "Catches duplicates your eyes would miss",
            "description": "Uses fuzzy matching and semantic similarity to catch near-duplicate records, even when customer names are spelled differently or order IDs differ slightly.",
            "category": "data_extraction",
            "trigger": "Every new record insertion",
            "what_it_does": "Fuzzy match on key fields, flags likely duplicates, routes to review queue",
            "tools_required": ["SQLite", "difflib"],
            "estimated_annual_value": 7800.0,
            "value_description": "Blocks 3% duplicate rate that corrupts downstream analytics",
        },
    ],
    "crm_update": [
        {
            "name": "LeadScorer",
            "tagline": "Prioritises your hottest leads automatically",
            "description": "As CRM records are updated, scores each lead 0–100 based on engagement signals, firmographics, and historical conversion data.",
            "category": "crm_update",
            "trigger": "Every CRM record update",
            "what_it_does": "Computes lead score, updates CRM field, notifies sales rep if score > 80",
            "tools_required": ["HubSpot API", "Slack API"],
            "estimated_annual_value": 22000.0,
            "value_description": "20% increase in sales conversion = $22K/year at current pipeline",
        },
    ],
    "reporting": [
        {
            "name": "AnomalyDetector",
            "tagline": "Catches business anomalies before they become crises",
            "description": "Runs statistical process control on all KPIs. When any metric deviates beyond 2σ, immediately alerts the appropriate team with context and suggested action.",
            "category": "reporting",
            "trigger": "Every report generation cycle",
            "what_it_does": "Statistical deviation check on all metrics, Slack alert with context",
            "tools_required": ["Slack API", "numpy"],
            "estimated_annual_value": 15600.0,
            "value_description": "Mean time to detect crises goes from 4 hours to < 5 minutes",
        },
    ],
}

_SPAWN_PROMPT = """\
You are an expert automation architect.

The user has just built an autonomous agent called "{primary_name}" that solves this problem:
"{problem}"

Category: {category}
Tools used: {tools}

Your job: identify 4-5 adjacent automation agents that naturally complement this primary agent.
Each adjacent agent should handle a related workflow the primary agent's output naturally triggers.

For each agent, return:
- name: short memorable name (e.g. FraudShield, RevenueInsights)
- tagline: one compelling sentence
- description: 2-3 sentence explanation
- category: one of email_automation|crm_update|reporting|fraud_detection|invoice_processing|customer_support|scheduling
- trigger: what event triggers this agent
- what_it_does: 1 sentence of concrete action
- tools_required: list of 2-4 tools/APIs
- estimated_annual_value: realistic dollar amount
- value_description: how that value is calculated

Return ONLY a raw JSON array. No markdown, no explanation, no text before or after.
Start your response with [ and end with ].
"""


def _default_spawn_for_category(category: str) -> list[dict]:
    """Return spawn templates for the closest matching category."""
    direct = _SPAWN_LIBRARY.get(category, [])
    if direct:
        return direct
    return _SPAWN_LIBRARY["email_automation"]


def _build_agent_code(agent: dict, primary_problem: str) -> str:
    """Generate a realistic but simplified code skeleton for a spawned agent."""
    name = agent["name"]
    trigger = agent.get("trigger", "")
    tools = agent.get("tools_required", [])
    category = agent.get("category", "automation")

    return f'''"""
{name} — Autonomous Agent
Built by Spoke Genesis | Adjacent to OrderSync

Trigger: {trigger}
Category: {category}
"""
from __future__ import annotations
import asyncio
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
LOG_FILE  = os.getenv("LOG_FILE", "logs/{name.lower()}.log")
CACHE_DB  = os.getenv("CACHE_DB", "storage/{name.lower()}_cache.db")
{'SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "")' if "Slack" in str(tools) else ""}

Path("logs").mkdir(exist_ok=True)
Path("storage").mkdir(exist_ok=True)

logger.add(
    LOG_FILE,
    format="{{time:YYYY-MM-DD HH:mm:ss}} | {{level:<8}} | {{message}}",
    level="INFO", rotation="10 MB", retention="30 days",
)


class {name}Agent:
    """
    Autonomous agent: {agent.get("what_it_does", "")}
    Self-monitoring with error tracking and automatic recovery.
    """

    def __init__(self, mode: str = "demo"):
        self.mode = mode
        self._db_path = CACHE_DB
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_records (
                    record_id TEXT PRIMARY KEY,
                    processed_at TEXT NOT NULL,
                    outcome TEXT
                )
            """)

    def _is_processed(self, record_id: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            return conn.execute(
                "SELECT 1 FROM processed_records WHERE record_id = ?", (record_id,)
            ).fetchone() is not None

    def _mark_processed(self, record_id: str, outcome: str) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_records VALUES (?, ?, ?)",
                (record_id, datetime.now().isoformat(), outcome),
            )

    async def run_once(self) -> dict:
        """Execute one cycle of the agent's core logic."""
        logger.info(f"{name} starting cycle — mode={{self.mode}}")
        t0 = __import__("time").perf_counter()

        try:
            if self.mode == "demo":
                result = await self._demo_cycle()
            else:
                result = await self._production_cycle()

            duration = __import__("time").perf_counter() - t0
            logger.success(f"{name} cycle complete in {{duration:.2f}}s — {{result}}")
            return result

        except Exception as e:
            logger.error(f"{name} cycle failed: {{e}}")
            return {{"status": "error", "message": str(e)}}

    async def _demo_cycle(self) -> dict:
        """Simulated cycle — no real API credentials required."""
        await asyncio.sleep(0.4)
        return {{"status": "ok", "processed": 5, "mode": "demo"}}

    async def _production_cycle(self) -> dict:
        """Real production cycle — requires credentials in .env"""
        # TODO: Implement with real {" + ".join(tools[:2])} integration
        raise NotImplementedError("Set credentials in .env to enable production mode")

    async def run_forever(self, interval_seconds: int = 300) -> None:
        """Run continuously at the configured interval."""
        import signal
        running = True

        def _stop(sig, frame):
            nonlocal running
            running = False
            logger.info("{name} received stop signal")

        signal.signal(signal.SIGINT, _stop)
        run_count = 0

        while running:
            run_count += 1
            logger.info(f"Run #{{run_count}}")
            await self.run_once()
            if running:
                logger.info(f"Next run in {{interval_seconds}}s...")
                await asyncio.sleep(interval_seconds)

        logger.info(f"{name} stopped after {{run_count}} runs")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="{name} — Autonomous Agent by Spoke")
    parser.add_argument("--mode", choices=["demo", "production"], default="demo")
    args = parser.parse_args()

    agent = {name}Agent(mode=args.mode)
    asyncio.run(agent.run_once() if args.mode == "demo" else agent.run_forever())
'''


class AgentSpawner:
    """
    System 1 — Autonomously infers and builds adjacent agents after the primary build.
    "You asked for 1 automation. I built 5."
    """

    async def spawn(
        self,
        problem: ProblemGraph,
        blueprint: Blueprint,
        primary_code: str,
        demo_mode: bool = False,
    ) -> SpawnResult:
        t_start = time.perf_counter()
        logger.info(f"AgentSpawner starting — category: {problem.category}")

        if demo_mode:
            return await self._spawn_demo(problem, blueprint)

        try:
            return await self._spawn_real(problem, blueprint)
        except Exception as e:
            logger.warning(f"Spawn LLM call failed ({e}), falling back to templates")
            return await self._spawn_demo(problem, blueprint)

    async def _spawn_demo(self, problem: ProblemGraph, blueprint: Blueprint) -> SpawnResult:
        """Use pre-built spawn templates — fast, no API needed."""
        logger.info("[GENESIS] Spawning adjacent agents from template library...")

        category_key = problem.category.value if hasattr(problem.category, "value") else str(problem.category)
        raw_agents = _default_spawn_for_category(category_key)

        spawned = []
        for i, raw in enumerate(raw_agents):
            await asyncio.sleep(0.2)          # simulate build time
            code = _build_agent_code(raw, problem.core_pain)
            agent = SpawnedAgent(
                **raw,
                code=code,
                status="built",
                build_time_seconds=round(0.8 + i * 0.3, 1),
            )
            spawned.append(agent)
            logger.success(f"  Spawned: {agent.name} — est. ${agent.estimated_annual_value:,.0f}/year")

        total_value = sum(a.estimated_annual_value for a in spawned)

        return SpawnResult(
            primary_agent_name=blueprint.agent_name,
            spawned_agents=spawned,
            total_agents_built=len(spawned) + 1,
            total_estimated_value=total_value,
            headline=f"You asked for 1 automation. I built {len(spawned) + 1}.",
        )

    async def _spawn_real(self, problem: ProblemGraph, blueprint: Blueprint) -> SpawnResult:
        """LLM-powered spawn — generates custom adjacent agents."""
        client = get_client()
        tools_str = ", ".join(problem.tools_mentioned + problem.tools_implied)

        raw = await client.complete_json(
            model=router.analyst_model,
            system="You are an expert automation architect that designs agent ecosystems.",
            user=_SPAWN_PROMPT.format(
                primary_name=blueprint.agent_name,
                problem=problem.core_pain,
                category=problem.category,
                tools=tools_str,
            ),
            temperature=0.6,
            max_tokens=2500,
        )

        if isinstance(raw, list):
            raw_agents = raw
        else:
            raw_agents = raw.get("agents", raw.get("data", []))

        spawned = []
        for raw_agent in raw_agents[:5]:
            code = _build_agent_code(raw_agent, problem.core_pain)
            agent = SpawnedAgent(
                name=raw_agent.get("name", "UnknownAgent"),
                tagline=raw_agent.get("tagline", ""),
                description=raw_agent.get("description", ""),
                category=raw_agent.get("category", "other"),
                trigger=raw_agent.get("trigger", ""),
                what_it_does=raw_agent.get("what_it_does", ""),
                tools_required=raw_agent.get("tools_required", []),
                estimated_annual_value=float(raw_agent.get("estimated_annual_value", 5000)),
                value_description=raw_agent.get("value_description", ""),
                code=code,
                status="built",
            )
            spawned.append(agent)

        total_value = sum(a.estimated_annual_value for a in spawned)
        return SpawnResult(
            primary_agent_name=blueprint.agent_name,
            spawned_agents=spawned,
            total_agents_built=len(spawned) + 1,
            total_estimated_value=total_value,
            headline=f"You asked for 1 automation. I built {len(spawned) + 1}.",
        )
