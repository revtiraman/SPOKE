"""
System 2 — Counterfactual Architect
Generate 3–5 candidate architectures, score them, reject weaker designs,
and explain exactly why the chosen design wins.
"""

from __future__ import annotations
import asyncio
import time
from loguru import logger

from core.genesis_models import (
    ArchitectureCandidate, ArchitectureScore, CounterfactualResult,
)
from core.models import ProblemGraph
from llm.client import get_client
from llm.router import router


# ── Demo architecture library ─────────────────────────────────────────────────

_DEMO_CANDIDATES: dict[str, list[dict]] = {
    "email_automation": [
        {
            "id": "arch_a",
            "name": "Polling Loop",
            "pattern": "Simple synchronous loop",
            "description": "A single Python script that runs in a while-True loop, polling Gmail every N seconds. Simple to understand and deploy.",
            "pros": ["Trivial to implement", "Easy to debug", "No external dependencies"],
            "cons": ["Blocks CPU between polls", "Crashes kill entire process", "No parallelism across mailboxes"],
            "rejection_reason": "Synchronous polling blocks the process — if one email extraction takes 10s, all others queue. At scale this creates 5-minute lags. Eliminated.",
            "scores": {"reliability": 5, "scalability": 3, "maintainability": 7, "cost_efficiency": 8, "time_to_value": 9},
            "selected": False,
            "color": "#ef4444",
        },
        {
            "id": "arch_b",
            "name": "Kafka Event Stream",
            "pattern": "Distributed message queue",
            "description": "Gmail events pushed to Kafka topic, N consumer workers process in parallel. Horizontally scalable to millions of emails.",
            "pros": ["Infinite horizontal scale", "Guaranteed delivery", "Replay capability"],
            "cons": ["Requires Kafka cluster ($200+/month)", "2-week setup time", "Massive operational overhead for 10-15 emails/day"],
            "rejection_reason": "Enterprise-grade overkill for 10-15 emails/day. Infrastructure cost ($200/month) exceeds the problem's value. ROI negative for first 3 years. Eliminated.",
            "scores": {"reliability": 10, "scalability": 10, "maintainability": 4, "cost_efficiency": 2, "time_to_value": 2},
            "selected": False,
            "color": "#ef4444",
        },
        {
            "id": "arch_c",
            "name": "Webhook Push",
            "pattern": "Gmail push notification + FastAPI handler",
            "description": "Register a Gmail push notification webhook. Process emails the instant they arrive — zero polling latency.",
            "pros": ["Zero latency", "No wasted CPU on empty polls", "Real-time"],
            "cons": ["Requires public HTTPS endpoint", "Gmail push expires every 7 days, needs renewal", "Complex auth flow"],
            "rejection_reason": "Real-time is appealing but Gmail push requires a publicly accessible HTTPS endpoint — which adds infrastructure complexity and a maintenance burden. Requires credential renewal every 7 days. Eliminated.",
            "scores": {"reliability": 7, "scalability": 8, "maintainability": 4, "cost_efficiency": 6, "time_to_value": 5},
            "selected": False,
            "color": "#f59e0b",
        },
        {
            "id": "arch_d",
            "name": "Async Event Loop",
            "pattern": "Async polling with SQLite dedup cache",
            "description": "asyncio-based agent with non-blocking Gmail API calls, exponential backoff, SQLite deduplication, and a self-monitoring health layer. Runs forever as a lightweight process.",
            "pros": ["Non-blocking — handles 50 emails in parallel", "SQLite dedup survives restarts", "No external infrastructure", "Health monitoring built-in", "60s latency is acceptable for batch order sync"],
            "cons": ["Single process — horizontal scale requires orchestration"],
            "rejection_reason": "",
            "scores": {"reliability": 9, "scalability": 7, "maintainability": 9, "cost_efficiency": 10, "time_to_value": 9},
            "selected": True,
            "color": "#22c55e",
        },
    ],
    "crm_update": [
        {
            "id": "arch_a",
            "name": "Direct API Calls",
            "pattern": "Synchronous REST calls on each update",
            "description": "For every trigger event, immediately make a synchronous API call to the CRM.",
            "pros": ["Simple", "Immediate consistency"],
            "cons": ["CRM API rate limits", "Blocks on slow responses", "No retry on failure"],
            "rejection_reason": "Synchronous calls with no retry logic will fail silently when CRM API is slow. Rate limit violations cause data loss. Eliminated.",
            "scores": {"reliability": 4, "scalability": 4, "maintainability": 7, "cost_efficiency": 8, "time_to_value": 9},
            "selected": False,
            "color": "#ef4444",
        },
        {
            "id": "arch_b",
            "name": "Batch Sync",
            "pattern": "Collect changes, sync hourly",
            "description": "Buffer all CRM updates in a local queue and batch-sync hourly.",
            "pros": ["Respects rate limits", "Reduces API calls"],
            "cons": ["1-hour lag on CRM updates", "Sales reps see stale data"],
            "rejection_reason": "1-hour CRM lag means sales reps are working with stale contact data. In a competitive sales environment, a hot lead can go cold in 20 minutes. Eliminated.",
            "scores": {"reliability": 7, "scalability": 8, "maintainability": 7, "cost_efficiency": 9, "time_to_value": 4},
            "selected": False,
            "color": "#f59e0b",
        },
        {
            "id": "arch_c",
            "name": "Event-driven with retry queue",
            "pattern": "Async upsert with SQLite retry queue",
            "description": "Async CRM upserts with exponential backoff, failed writes to a local retry queue, and deduplication by contact email.",
            "pros": ["Near-real-time", "Handles rate limits gracefully", "Zero data loss", "Deduplicates contacts"],
            "cons": ["Slightly more complex"],
            "rejection_reason": "",
            "scores": {"reliability": 9, "scalability": 8, "maintainability": 9, "cost_efficiency": 9, "time_to_value": 8},
            "selected": True,
            "color": "#22c55e",
        },
    ],
}


_COUNTERFACTUAL_PROMPT = """\
You are a principal software architect comparing design options for an autonomous agent.

Problem: {problem}
Category: {category}

Generate exactly 4 candidate architectures for solving this problem. Include:
1. The obvious/naive approach (reject it)
2. The enterprise/overengineered approach (reject it)  
3. A real alternative with trade-offs (conditionally reject)
4. The optimal approach (select this one)

For each candidate return:
{
  "id": "arch_a",
  "name": "Short name",
  "pattern": "Architecture pattern name",
  "description": "2 sentences",
  "pros": ["pro 1", "pro 2", "pro 3"],
  "cons": ["con 1", "con 2"],
  "rejection_reason": "Why this was eliminated (empty string if selected)",
  "scores": {
    "reliability": 1-10,
    "scalability": 1-10,
    "maintainability": 1-10,
    "cost_efficiency": 1-10,
    "time_to_value": 1-10
  },
  "selected": false
}

The winner (selected=true) must have the highest total score.
Return ONLY a raw JSON array. No markdown, no explanation, no text before or after.
Start your response with [ and end with ].
"""


class CounterfactualArchitect:
    """
    System 2 — Generates multiple competing architectures, rejects the weaker ones,
    and shows exactly why the final design was chosen.
    """

    async def analyze(
        self,
        problem: ProblemGraph,
        demo_mode: bool = False,
    ) -> CounterfactualResult:
        t_start = time.perf_counter()
        logger.info("CounterfactualArchitect analyzing design space...")

        if demo_mode:
            return self._demo_result(problem)

        try:
            return await self._real_analysis(problem)
        except Exception as e:
            logger.warning(f"Counterfactual LLM call failed ({e}), using templates")
            return self._demo_result(problem)

    def _demo_result(self, problem: ProblemGraph) -> CounterfactualResult:
        category_key = problem.category.value if hasattr(problem.category, "value") else str(problem.category)
        raw_list = _DEMO_CANDIDATES.get(category_key, _DEMO_CANDIDATES["email_automation"])

        candidates = []
        winner = None
        for raw in raw_list:
            scores = ArchitectureScore(**raw["scores"])
            c = ArchitectureCandidate(
                id=raw["id"],
                name=raw["name"],
                pattern=raw["pattern"],
                description=raw["description"],
                pros=raw["pros"],
                cons=raw["cons"],
                rejection_reason=raw.get("rejection_reason", ""),
                scores=scores,
                selected=raw.get("selected", False),
                color=raw.get("color", "#1e1e3f"),
            )
            candidates.append(c)
            if c.selected:
                winner = c

        rationale = (
            f"**{winner.name}** selected with score {winner.scores.total:.1f}/10. "
            f"Rejected {len([c for c in candidates if not c.selected])} alternatives: "
            + "; ".join(
                f'{c.name} ({c.scores.total:.1f}/10 — {c.rejection_reason[:60]}...)'
                for c in candidates if not c.selected and c.rejection_reason
            )
        ) if winner else ""

        return CounterfactualResult(
            candidates=candidates,
            winner=winner,
            selection_rationale=rationale,
        )

    async def _real_analysis(self, problem: ProblemGraph) -> CounterfactualResult:
        client = get_client()
        raw = await client.complete_json(
            model=router.planner_model,
            system="You are a principal software architect comparing design options.",
            user=_COUNTERFACTUAL_PROMPT.format(
                problem=problem.core_pain,
                category=problem.category,
            ),
            temperature=0.3,
            max_tokens=2000,
        )

        if isinstance(raw, list):
            raw_list = raw
        elif isinstance(raw, dict):
            raw_list = raw.get("candidates", raw.get("architectures", []))
        else:
            raw_list = []

        candidates = []
        winner = None
        for r in raw_list:
            try:
                sc_raw = r.get("scores", {})
                scores = ArchitectureScore(
                    reliability=int(sc_raw.get("reliability", 5)),
                    scalability=int(sc_raw.get("scalability", 5)),
                    maintainability=int(sc_raw.get("maintainability", 5)),
                    cost_efficiency=int(sc_raw.get("cost_efficiency", 5)),
                    time_to_value=int(sc_raw.get("time_to_value", 5)),
                )
                c = ArchitectureCandidate(
                    id=r.get("id", f"arch_{len(candidates)}"),
                    name=r.get("name", "Unknown"),
                    pattern=r.get("pattern", ""),
                    description=r.get("description", ""),
                    pros=r.get("pros", []),
                    cons=r.get("cons", []),
                    rejection_reason=r.get("rejection_reason", ""),
                    scores=scores,
                    selected=bool(r.get("selected", False)),
                    color="#22c55e" if r.get("selected") else "#ef4444",
                )
                candidates.append(c)
                if c.selected:
                    winner = c
            except Exception as parse_err:
                logger.warning(f"Skipping malformed candidate: {parse_err}")

        # Auto-select highest scorer if none marked
        if not winner and candidates:
            winner = max(candidates, key=lambda c: c.scores.total)
            winner.selected = True
            winner.color = "#22c55e"

        rationale = (
            f"**{winner.name}** wins with a composite score of {winner.scores.total:.1f}/10."
        ) if winner else ""

        return CounterfactualResult(
            candidates=candidates,
            winner=winner,
            selection_rationale=rationale,
        )
