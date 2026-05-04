"""All Pydantic models for SPOKE Genesis — the 10-system upgrade."""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ── System 1: Agent Spawn ─────────────────────────────────────────────────────

class SpawnedAgent(BaseModel):
    name: str
    tagline: str
    description: str
    category: str
    trigger: str
    what_it_does: str
    tools_required: list[str] = Field(default_factory=list)
    estimated_annual_value: float = 0.0
    value_description: str = ""
    code: str = ""
    status: str = "built"         # built | pending | failed
    build_time_seconds: float = 0.0


class SpawnResult(BaseModel):
    primary_agent_name: str
    spawned_agents: list[SpawnedAgent] = Field(default_factory=list)
    total_agents_built: int = 0
    total_estimated_value: float = 0.0
    headline: str = ""

    @property
    def spawn_count(self) -> int:
        return len([a for a in self.spawned_agents if a.status == "built"])


# ── System 2: Counterfactual Architect ───────────────────────────────────────

class ArchitectureScore(BaseModel):
    reliability: int = Field(ge=0, le=10)
    scalability: int = Field(ge=0, le=10)
    maintainability: int = Field(ge=0, le=10)
    cost_efficiency: int = Field(ge=0, le=10)
    time_to_value: int = Field(ge=0, le=10)

    @property
    def total(self) -> float:
        return (self.reliability + self.scalability +
                self.maintainability + self.cost_efficiency + self.time_to_value) / 5


class ArchitectureCandidate(BaseModel):
    id: str
    name: str
    pattern: str                  # e.g. "Event-driven polling loop"
    description: str
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    rejection_reason: str = ""
    scores: ArchitectureScore
    selected: bool = False
    color: str = "#1e1e3f"        # UI accent colour


class CounterfactualResult(BaseModel):
    candidates: list[ArchitectureCandidate] = Field(default_factory=list)
    winner: ArchitectureCandidate | None = None
    selection_rationale: str = ""


# ── System 3: Multimodal Tool Detection ──────────────────────────────────────

class DetectedTool(BaseModel):
    name: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str = "transcript"    # transcript | ocr | logo | inferred
    logo_color: str = "#6c63ff"
    category: str = "productivity"


class DetectedStack(BaseModel):
    tools: list[DetectedTool] = Field(default_factory=list)
    primary_email: str = ""       # gmail | outlook
    primary_crm: str = ""         # hubspot | salesforce | pipedrive
    primary_storage: str = ""     # sheets | airtable | notion
    primary_comms: str = ""       # slack | teams | discord
    frames_analyzed: int = 0
    confidence: float = 0.0
    stack_summary: str = ""

    @property
    def tool_names(self) -> list[str]:
        return [t.name for t in self.tools]


# ── System 4: Live Workflow DAG ───────────────────────────────────────────────

class DAGNodeStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"
    ERROR = "error"


class DAGNode(BaseModel):
    id: str
    label: str
    description: str = ""
    status: DAGNodeStatus = DAGNodeStatus.PENDING
    icon: str = "⬡"
    x: float = 0.0               # layout hint
    y: float = 0.0
    throughput: int = 0          # items/min
    latency_ms: int = 0


class DAGEdge(BaseModel):
    source: str
    target: str
    label: str = ""
    animated: bool = False
    flow_count: int = 0


class WorkflowDAG(BaseModel):
    nodes: list[DAGNode] = Field(default_factory=list)
    edges: list[DAGEdge] = Field(default_factory=list)
    agent_name: str = ""

    def activate_node(self, node_id: str) -> None:
        for n in self.nodes:
            if n.id == node_id:
                n.status = DAGNodeStatus.ACTIVE
            elif n.status == DAGNodeStatus.ACTIVE:
                n.status = DAGNodeStatus.DONE

    def complete_node(self, node_id: str, throughput: int = 0) -> None:
        for n in self.nodes:
            if n.id == node_id:
                n.status = DAGNodeStatus.DONE
                n.throughput = throughput


# ── System 5: Business Simulation ────────────────────────────────────────────

class SimulationEvent(BaseModel):
    timestamp: str
    event_type: str               # order | duplicate | fraud | outage | retry | recovery
    description: str
    handled: bool = True
    agent: str = "OrderSync"
    value: float = 0.0
    action_taken: str = ""


class SimulationDayKPIs(BaseModel):
    day: int
    date: str
    events_processed: int = 0
    duplicates_blocked: int = 0
    fraud_detected: int = 0
    outages_recovered: int = 0
    revenue_captured: float = 0.0
    errors: int = 0
    accuracy_pct: float = 100.0
    uptime_pct: float = 100.0
    events: list[SimulationEvent] = Field(default_factory=list)


class SimulationResult(BaseModel):
    days: list[SimulationDayKPIs] = Field(default_factory=list)
    total_events: int = 0
    total_revenue: float = 0.0
    total_fraud_blocked: float = 0.0
    total_errors: int = 0
    final_accuracy: float = 0.0
    final_uptime: float = 0.0
    improvement_story: str = ""
    week_summary: str = ""


# ── System 6: Economic Brain ──────────────────────────────────────────────────

class EconomicLineItem(BaseModel):
    label: str
    annual_value: float
    calculation: str
    agent: str = "Primary"
    category: str = "time_savings"  # time_savings | error_prevention | opportunity | recovery


class EconomicReport(BaseModel):
    line_items: list[EconomicLineItem] = Field(default_factory=list)
    total_annual_value: float = 0.0
    implementation_cost: float = 5000.0
    roi_percentage: float = 0.0
    payback_months: float = 0.0
    five_year_value: float = 0.0
    automation_confidence: float = 0.0
    avoided_errors_per_year: int = 0
    hours_saved_per_year: float = 0.0
    headline: str = ""
    boardroom_summary: str = ""

    @property
    def monthly_value(self) -> float:
        return self.total_annual_value / 12


# ── System 7: Self-Heal Theater ───────────────────────────────────────────────

class SelfHealFrame(BaseModel):
    timestamp: float
    stage: str                    # injecting | running | failing | diagnosing | patching | redeploying | recovered
    content: str
    color: str = "#ef4444"


class SelfHealReport(BaseModel):
    injected_bug: str = ""
    injected_bug_description: str = ""
    error_output: str = ""
    diagnosis: str = ""
    root_cause: str = ""
    patch_description: str = ""
    patch_diff: str = ""
    recovery_time_seconds: float = 0.0
    attempts_needed: int = 1
    frames: list[SelfHealFrame] = Field(default_factory=list)
    success: bool = True


# ── System 8: Live Deployment ─────────────────────────────────────────────────

class HealthCheckResult(BaseModel):
    endpoint: str
    status: str                   # healthy | degraded | down
    latency_ms: int = 0
    message: str = ""


class DeploymentStatus(BaseModel):
    session_id: str
    agent_name: str
    preview_url: str = ""
    deployment_type: str = "local"   # local | docker | cloud
    status: str = "deploying"        # deploying | live | failed | rolled_back
    deployed_at: str = ""
    health_checks: list[HealthCheckResult] = Field(default_factory=list)
    logs: list[str] = Field(default_factory=list)
    rollback_available: bool = True
    version: str = "1.0.0"

    @property
    def is_live(self) -> bool:
        return self.status == "live"

    @property
    def all_healthy(self) -> bool:
        return all(h.status == "healthy" for h in self.health_checks)


# ── System 9: Business Memory ─────────────────────────────────────────────────

class MemoryRecord(BaseModel):
    id: str = ""
    session_id: str
    agent_name: str
    problem_summary: str
    tools_used: list[str] = Field(default_factory=list)
    category: str
    annual_value: float = 0.0
    hours_saved_weekly: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    tags: list[str] = Field(default_factory=list)
    spawned_count: int = 0


class MemoryQueryResult(BaseModel):
    records: list[MemoryRecord] = Field(default_factory=list)
    similar_found: bool = False
    similarity_score: float = 0.0
    learning: str = ""           # What we learned from history to improve this build


# ── System 10: Autonomous Discovery ──────────────────────────────────────────

class DiscoveredAutomation(BaseModel):
    rank: int
    title: str
    description: str
    why_now: str                 # Why this matters given what we know
    estimated_annual_value: float
    effort_days: int
    roi_multiple: float = 0.0
    category: str
    tools_needed: list[str] = Field(default_factory=list)
    trigger: str = ""
    confidence: float = 0.9


class DiscoveryResult(BaseModel):
    automations: list[DiscoveredAutomation] = Field(default_factory=list)
    total_opportunity_value: float = 0.0
    analysis_summary: str = ""
    call_to_action: str = ""


# ── Genesis Pipeline Result ───────────────────────────────────────────────────

class GenesisPhase(BaseModel):
    name: str
    status: str = "pending"      # pending | running | done | skipped
    duration_seconds: float = 0.0
    headline: str = ""


class GenesisResult(BaseModel):
    session_id: str
    status: str = "success"

    # Core pipeline
    core_pipeline_result: dict = Field(default_factory=dict)

    # System 1
    spawn: SpawnResult | None = None

    # System 2
    counterfactual: CounterfactualResult | None = None

    # System 3
    detected_stack: DetectedStack | None = None

    # System 4
    workflow_dag: WorkflowDAG | None = None

    # System 5
    simulation: SimulationResult | None = None

    # System 6
    economics: EconomicReport | None = None

    # System 7
    selfheal: SelfHealReport | None = None

    # System 8
    deployment: DeploymentStatus | None = None

    # System 9
    memory_learning: str = ""

    # System 10
    discovery: DiscoveryResult | None = None

    # Timeline
    phases: list[GenesisPhase] = Field(default_factory=list)
    total_duration_seconds: float = 0.0

    # The grand finale numbers
    total_agents_built: int = 0
    total_annual_value: float = 0.0
    total_hours_saved_weekly: float = 0.0
    final_headline: str = ""
    call_to_action: str = "Would you like me to continue optimizing your business?"
