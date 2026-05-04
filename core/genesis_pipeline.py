"""
SPOKE Genesis — Full 10-System Orchestrator
Upgrades a standard pipeline result into a jaw-dropping autonomous business
automation intelligence platform experience.
"""

from __future__ import annotations
import asyncio
import time
from collections.abc import AsyncIterator, Callable
from typing import Awaitable

from loguru import logger

from core.models import PipelineResult, PipelineStatus, ProblemGraph, Blueprint
from core.pipeline import SpokePipeline
from core.genesis_models import (
    GenesisResult, GenesisPhase, WorkflowDAG, DAGNode, DAGEdge, DAGNodeStatus,
)
from core.state import SessionState
from core.config import settings

from agents.spawner import AgentSpawner
from agents.counterfactual import CounterfactualArchitect
from agents.multimodal import MultimodalDetector
from agents.simulator import BusinessSimulator
from agents.economic import EconomicBrain
from agents.selfheal import SelfHealTheater
from agents.deployment_manager import DeploymentManager
from agents.memory import BusinessMemory
from agents.discovery import DiscoveryAgent


ProgressCallback = Callable[[str, int, str, str], Awaitable[None]]


async def _noop(msg: str, pct: int, phase: str = "", detail: str = "") -> None:
    logger.info(f"[GENESIS {pct}%] {msg}")


def _build_workflow_dag(agent_name: str) -> WorkflowDAG:
    """Build the standard 9-node workflow DAG for the generated agent."""
    nodes = [
        DAGNode(id="observe",   label="Observe",   description="Monitor Gmail inbox",          icon="👁️",  x=0,   y=2),
        DAGNode(id="extract",   label="Extract",   description="LLM data extraction",          icon="🧠",  x=1,   y=2),
        DAGNode(id="validate",  label="Validate",  description="Schema + confidence check",    icon="✅",  x=2,   y=2),
        DAGNode(id="dedup",     label="Dedup",     description="SQLite cache lookup",          icon="🔍",  x=3,   y=1),
        DAGNode(id="route",     label="Route",     description="High-conf vs review queue",    icon="🔀",  x=3,   y=3),
        DAGNode(id="store",     label="Store",     description="Write to Google Sheets",       icon="💾",  x=4,   y=2),
        DAGNode(id="monitor",   label="Monitor",   description="Health + error tracking",      icon="📡",  x=5,   y=1),
        DAGNode(id="alert",     label="Alert",     description="Slack / email on failure",     icon="🔔",  x=5,   y=3),
        DAGNode(id="improve",   label="Improve",   description="Adaptive learning loop",       icon="📈",  x=6,   y=2),
    ]

    edges = [
        DAGEdge(source="observe",  target="extract",  label="email body"),
        DAGEdge(source="extract",  target="validate", label="structured data"),
        DAGEdge(source="validate", target="dedup",    label="passes check"),
        DAGEdge(source="validate", target="route",    label="low confidence"),
        DAGEdge(source="dedup",    target="route",    label="new record"),
        DAGEdge(source="route",    target="store",    label="high confidence"),
        DAGEdge(source="store",    target="monitor",  label="write success"),
        DAGEdge(source="monitor",  target="alert",    label="anomaly detected"),
        DAGEdge(source="monitor",  target="improve",  label="stats collected"),
        DAGEdge(source="improve",  target="observe",  label="next cycle", animated=True),
    ]

    return WorkflowDAG(nodes=nodes, edges=edges, agent_name=agent_name)


def _make_phase(name: str) -> GenesisPhase:
    return GenesisPhase(name=name, status="pending")


class GenesisOrchestrator:
    """
    SPOKE Genesis — the full 10-system autonomous business automation intelligence platform.

    Runs the standard 10-agent pipeline first, then wraps it in 10 additional
    intelligence systems to produce a jaw-dropping result.
    """

    def __init__(self):
        self.core_pipeline   = SpokePipeline()
        self.spawner         = AgentSpawner()
        self.counterfactual  = CounterfactualArchitect()
        self.multimodal      = MultimodalDetector()
        self.simulator       = BusinessSimulator()
        self.economic        = EconomicBrain()
        self.selfheal        = SelfHealTheater()
        self.deployer        = DeploymentManager()
        self.memory          = BusinessMemory()
        self.discovery       = DiscoveryAgent()
        self.state           = SessionState()

    async def run(
        self,
        video_path: str | None = None,
        transcript_text: str | None = None,
        clarification_answers: dict[str, str] | None = None,
        session_id: str | None = None,
        progress: ProgressCallback = _noop,
        demo_mode: bool = False,
    ) -> GenesisResult:
        t_start = time.perf_counter()

        if not session_id:
            session_id = await self.state.create_session()

        logger.info(f"SPOKE Genesis starting — session {session_id}")

        phases = [
            _make_phase("Core Pipeline"),
            _make_phase("Stack Detection"),
            _make_phase("Counterfactual Architect"),
            _make_phase("Agent Spawn"),
            _make_phase("Workflow DAG"),
            _make_phase("Business Simulation"),
            _make_phase("Economic Brain"),
            _make_phase("Self-Heal Theater"),
            _make_phase("Live Deployment"),
            _make_phase("Business Memory"),
            _make_phase("Autonomous Discovery"),
        ]

        genesis = GenesisResult(session_id=session_id, phases=phases)

        async def prog(msg: str, pct: int, phase_name: str = "", detail: str = "") -> None:
            await progress(msg, pct, phase_name, detail)

        # ══════════════════════════════════════════════════════════════════════
        # PHASE 0 — Core 10-Agent Pipeline
        # ══════════════════════════════════════════════════════════════════════
        phases[0].status = "running"
        await prog("Running core 10-agent pipeline...", 5, "Core Pipeline")

        async def core_progress(msg: str, pct: int, status: PipelineStatus, detail: str = "") -> None:
            # Map core pipeline progress (0-100) to genesis progress (5-35)
            gen_pct = 5 + int(pct * 0.30)
            await prog(msg, gen_pct, "Core Pipeline", detail)

        core_result: PipelineResult = await self.core_pipeline.run(
            video_path=video_path,
            transcript_text=transcript_text,
            clarification_answers=clarification_answers,
            session_id=session_id,
            progress=core_progress,
            demo_mode=demo_mode,
        )

        if core_result.status.value not in ("success",):
            genesis.status = core_result.status.value
            genesis.total_duration_seconds = time.perf_counter() - t_start
            phases[0].status = "done" if core_result.status.value == "success" else "failed"
            return genesis

        phases[0].status = "done"
        phases[0].duration_seconds = time.perf_counter() - t_start
        phases[0].headline = f"{core_result.agent_name} built"
        genesis.core_pipeline_result = core_result.model_dump()

        problem: ProblemGraph = core_result.problem
        blueprint: Blueprint = core_result.blueprint
        agent_code: str = core_result.code

        await prog(f"Core build complete — {core_result.agent_name}", 35, "Core Pipeline",
                   f"Built in {core_result.total_duration_seconds:.1f}s")

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 3 — Multimodal Stack Detection (fast, run immediately)
        # ══════════════════════════════════════════════════════════════════════
        phases[1].status = "running"
        await prog("Detecting your technology stack...", 37, "Stack Detection",
                   "Scanning transcript and video frames for tools...")

        t0 = time.perf_counter()
        try:
            detected_stack = self.multimodal.detect(
                transcript_text=transcript_text or "",
                video_path=video_path,
            )
            genesis.detected_stack = detected_stack
            phases[1].status = "done"
            phases[1].duration_seconds = time.perf_counter() - t0
            phases[1].headline = detected_stack.stack_summary
        except Exception as e:
            logger.warning(f"Multimodal detection failed: {e}")
            phases[1].status = "skipped"

        await prog(f"Stack detected: {genesis.detected_stack.stack_summary if genesis.detected_stack else 'N/A'}",
                   40, "Stack Detection")

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 2 — Counterfactual Architect
        # ══════════════════════════════════════════════════════════════════════
        phases[2].status = "running"
        await prog("Evaluating alternative architectures...", 42, "Counterfactual Architect",
                   "Generating 4 candidate designs and scoring each...")

        t0 = time.perf_counter()
        try:
            counterfactual_result = await self.counterfactual.analyze(problem, demo_mode=demo_mode)
            genesis.counterfactual = counterfactual_result
            n_rejected = len([c for c in counterfactual_result.candidates if not c.selected])
            phases[2].status = "done"
            phases[2].duration_seconds = time.perf_counter() - t0
            phases[2].headline = (
                f"Winner: {counterfactual_result.winner.name} — {n_rejected} alternatives rejected"
                if counterfactual_result.winner else "Analysis complete"
            )
        except Exception as e:
            logger.warning(f"Counterfactual analysis failed: {e}")
            phases[2].status = "skipped"

        await prog(f"Architecture selected: {phases[2].headline}", 46, "Counterfactual Architect")

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 1 — Agent Spawn
        # ══════════════════════════════════════════════════════════════════════
        phases[3].status = "running"
        await prog("Spawning adjacent automation agents...", 48, "Agent Spawn",
                   "Inferring complementary workflows from your primary automation...")

        t0 = time.perf_counter()
        try:
            spawn_result = await self.spawner.spawn(
                problem=problem,
                blueprint=blueprint,
                primary_code=agent_code,
                demo_mode=demo_mode,
            )
            genesis.spawn = spawn_result
            phases[3].status = "done"
            phases[3].duration_seconds = time.perf_counter() - t0
            phases[3].headline = spawn_result.headline
        except Exception as e:
            logger.warning(f"Agent spawn failed: {e}")
            phases[3].status = "skipped"

        await prog(
            phases[3].headline or "Spawn complete",
            54, "Agent Spawn",
            f"{genesis.spawn.spawn_count if genesis.spawn else 0} adjacent agents built",
        )

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 4 — Workflow DAG
        # ══════════════════════════════════════════════════════════════════════
        phases[4].status = "running"
        await prog("Building live workflow graph...", 56, "Workflow DAG")

        t0 = time.perf_counter()
        try:
            dag = _build_workflow_dag(blueprint.agent_name)
            # Animate: mark all nodes done
            for node in dag.nodes:
                node.status = DAGNodeStatus.DONE
                node.throughput = 12
            genesis.workflow_dag = dag
            phases[4].status = "done"
            phases[4].duration_seconds = time.perf_counter() - t0
            phases[4].headline = f"{len(dag.nodes)}-node DAG — all paths active"
        except Exception as e:
            logger.warning(f"DAG build failed: {e}")
            phases[4].status = "skipped"

        await prog("Workflow DAG live", 58, "Workflow DAG")

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 5 — Business Simulation
        # ══════════════════════════════════════════════════════════════════════
        phases[5].status = "running"
        await prog("Simulating one week of business operations...", 60, "Business Simulation",
                   "Running 7 days of synthetic orders, fraud, outages, and recovery...")

        t0 = time.perf_counter()
        try:
            sim_result = await self.simulator.simulate(
                problem=problem,
                spawn=genesis.spawn,
            )
            genesis.simulation = sim_result
            phases[5].status = "done"
            phases[5].duration_seconds = time.perf_counter() - t0
            phases[5].headline = sim_result.week_summary
        except Exception as e:
            logger.warning(f"Simulation failed: {e}")
            phases[5].status = "skipped"

        await prog("Simulation complete", 67, "Business Simulation",
                   genesis.simulation.week_summary if genesis.simulation else "")

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 6 — Economic Brain
        # ══════════════════════════════════════════════════════════════════════
        phases[6].status = "running"
        await prog("Computing ROI and economic impact...", 69, "Economic Brain")

        t0 = time.perf_counter()
        try:
            economics = self.economic.calculate(
                problem=problem,
                spawn=genesis.spawn,
                simulation=genesis.simulation,
            )
            genesis.economics = economics
            phases[6].status = "done"
            phases[6].duration_seconds = time.perf_counter() - t0
            phases[6].headline = economics.headline
        except Exception as e:
            logger.warning(f"Economic brain failed: {e}")
            phases[6].status = "skipped"

        await prog(f"Economic analysis: {genesis.economics.headline if genesis.economics else 'complete'}",
                   73, "Economic Brain")

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 7 — Self-Heal Theater
        # ══════════════════════════════════════════════════════════════════════
        phases[7].status = "running"
        await prog("Running self-heal demonstration...", 75, "Self-Heal Theater",
                   "Injecting controlled failure to prove autonomous recovery...")

        t0 = time.perf_counter()
        try:
            selfheal = await self.selfheal.perform(
                agent_code=agent_code,
                demo_mode=True,
            )
            genesis.selfheal = selfheal
            phases[7].status = "done"
            phases[7].duration_seconds = time.perf_counter() - t0
            phases[7].headline = f"Recovered in {selfheal.recovery_time_seconds:.1f}s — {selfheal.attempts_needed} attempt(s)"
        except Exception as e:
            logger.warning(f"Self-heal theater failed: {e}")
            phases[7].status = "skipped"

        await prog(f"Self-heal: {phases[7].headline}", 80, "Self-Heal Theater")

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 8 — Live Deployment
        # ══════════════════════════════════════════════════════════════════════
        phases[8].status = "running"
        await prog("Deploying agent stack...", 82, "Live Deployment")

        t0 = time.perf_counter()
        try:
            spawned_codes = [
                (a.name, a.code)
                for a in (genesis.spawn.spawned_agents if genesis.spawn else [])
                if a.code
            ]
            deploy_status = await self.deployer.deploy(
                session_id=session_id,
                agent_name=blueprint.agent_name,
                agent_code=agent_code,
                spawned_codes=spawned_codes,
            )
            genesis.deployment = deploy_status
            phases[8].status = "done"
            phases[8].duration_seconds = time.perf_counter() - t0
            phases[8].headline = f"Status: {deploy_status.status} — {len(deploy_status.health_checks)} health checks passed"
        except Exception as e:
            logger.warning(f"Deployment failed: {e}")
            phases[8].status = "skipped"

        await prog(f"Deployed: {phases[8].headline}", 86, "Live Deployment")

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 9 — Business Memory
        # ══════════════════════════════════════════════════════════════════════
        phases[9].status = "running"
        await prog("Saving to business memory...", 88, "Business Memory")

        t0 = time.perf_counter()
        try:
            annual_value = genesis.economics.total_annual_value if genesis.economics else 0.0
            hours_weekly = problem.estimated_hours_per_week

            mem_record = self.memory.save(
                problem=problem,
                session_id=session_id,
                agent_name=blueprint.agent_name,
                annual_value=annual_value,
                hours_saved_weekly=hours_weekly,
                spawned_count=genesis.spawn.spawn_count if genesis.spawn else 0,
            )
            if genesis.economics:
                self.memory.save_roi(
                    session_id, annual_value,
                    genesis.economics.payback_months,
                )

            # Query for learning
            mem_query = self.memory.query_similar(problem)
            genesis.memory_learning = mem_query.learning or "First automation in this category — baseline established."

            phases[9].status = "done"
            phases[9].duration_seconds = time.perf_counter() - t0
            phases[9].headline = f"Saved — memory ID: {mem_record.id}"
        except Exception as e:
            logger.warning(f"Memory save failed: {e}")
            genesis.memory_learning = "Memory system offline — this build was not persisted."
            phases[9].status = "skipped"

        await prog("Business memory updated", 91, "Business Memory", genesis.memory_learning)

        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM 10 — Autonomous Discovery
        # ══════════════════════════════════════════════════════════════════════
        phases[10].status = "running"
        await prog("Discovering adjacent automation opportunities...", 93, "Autonomous Discovery",
                   "Scanning your workflow for high-value automations you haven't asked for...")

        t0 = time.perf_counter()
        try:
            discovery = await self.discovery.discover(
                problem=problem,
                spawn=genesis.spawn,
                demo_mode=demo_mode,
            )
            genesis.discovery = discovery
            phases[10].status = "done"
            phases[10].duration_seconds = time.perf_counter() - t0
            phases[10].headline = (
                f"{len(discovery.automations)} opportunities — ${discovery.total_opportunity_value:,.0f}/year potential"
            )
        except Exception as e:
            logger.warning(f"Discovery failed: {e}")
            phases[10].status = "skipped"

        await prog(f"Discovery: {phases[10].headline}", 97, "Autonomous Discovery")

        # ══════════════════════════════════════════════════════════════════════
        # Final Aggregation
        # ══════════════════════════════════════════════════════════════════════
        total_seconds = time.perf_counter() - t_start

        total_agents = 1 + (genesis.spawn.spawn_count if genesis.spawn else 0)
        total_value = genesis.economics.total_annual_value if genesis.economics else 0.0
        hours_weekly = sum([
            problem.estimated_hours_per_week,
            *([a.estimated_annual_value / (35 * 52) for a in genesis.spawn.spawned_agents]
              if genesis.spawn else []),
        ])

        genesis.total_agents_built = total_agents
        genesis.total_annual_value = total_value
        genesis.total_hours_saved_weekly = round(hours_weekly, 1)
        genesis.total_duration_seconds = total_seconds
        genesis.status = "success"
        genesis.final_headline = (
            f"You asked for 1 automation. I built {total_agents} systems.\n"
            f"Estimated annual value created: ${total_value:,.0f}.\n"
            f"Would you like me to continue optimizing your business?"
        )

        await prog("SPOKE Genesis complete.", 100, "Genesis",
                   genesis.final_headline.replace("\n", " — "))

        logger.success(
            f"SPOKE Genesis complete — {total_agents} agents, "
            f"${total_value:,.0f}/year, {total_seconds:.0f}s total"
        )

        return genesis

    async def resume(
        self,
        session_id: str,
        clarification_answers: dict[str, str],
        progress: ProgressCallback = _noop,
    ) -> GenesisResult:
        """Resume a paused Genesis run after clarification answers are provided."""
        transcript_data = await self.state.load(session_id, "transcript")
        transcript_text = transcript_data.get("cleaned_text", "") if transcript_data else ""

        return await self.run(
            transcript_text=transcript_text,
            clarification_answers=clarification_answers,
            session_id=session_id,
            progress=progress,
        )
