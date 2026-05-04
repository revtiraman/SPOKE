"""All Pydantic data models for the Spoke pipeline."""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class AgentCategory(str, Enum):
    EMAIL_AUTOMATION = "email_automation"
    DATA_EXTRACTION = "data_extraction"
    CRM_UPDATE = "crm_update"
    REPORTING = "reporting"
    INVOICE_PROCESSING = "invoice_processing"
    CUSTOMER_SUPPORT = "customer_support"
    SCHEDULING = "scheduling"
    SPREADSHEET = "spreadsheet"
    OTHER = "other"


class ArchitectureType(str, Enum):
    SINGLE_LOOP = "single_loop"
    EVENT_DRIVEN = "event_driven"
    SCHEDULED = "scheduled"
    MULTI_STEP = "multi_step"


class PipelineStatus(str, Enum):
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    ANALYSING = "analysing"
    CLARIFYING = "clarifying"
    AWAITING_CLARIFICATION = "awaiting_clarification"
    ARCHITECTING = "architecting"
    CODING = "coding"
    EXECUTING = "executing"
    DEBUGGING = "debugging"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"


# ── Transcription ─────────────────────────────────────────────────────────────

class TranscriptResult(BaseModel):
    raw_text: str
    cleaned_text: str
    duration_seconds: float = 0.0
    confidence_score: float = 1.0
    language_detected: str = "en"
    word_count: int = 0
    flagged_segments: list[str] = Field(default_factory=list)

    def model_post_init(self, __context) -> None:
        if not self.word_count:
            self.word_count = len(self.cleaned_text.split())


# ── Problem Analysis ──────────────────────────────────────────────────────────

class ProblemGraph(BaseModel):
    core_pain: str
    trigger: str
    process_steps: list[str]
    tools_mentioned: list[str] = Field(default_factory=list)
    tools_implied: list[str] = Field(default_factory=list)
    frequency: str = "daily"
    estimated_hours_per_week: float = 0.0
    data_fields: list[str] = Field(default_factory=list)
    output: str = ""
    success_condition: str = ""
    category: AgentCategory = AgentCategory.OTHER
    complexity_score: int = Field(default=2, ge=1, le=5)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    missing_information: list[str] = Field(default_factory=list)


# ── Clarification ─────────────────────────────────────────────────────────────

class ClarificationQuestions(BaseModel):
    questions: list[str]
    skip_reason: str = ""

    @property
    def should_skip(self) -> bool:
        return len(self.questions) == 0


class ClarificationAnswers(BaseModel):
    answers: dict[str, str] = Field(default_factory=dict)


# ── Architecture ──────────────────────────────────────────────────────────────

class ToolRequirement(BaseModel):
    name: str
    purpose: str
    auth: str
    endpoints: list[str] = Field(default_factory=list)


class TriggerMechanism(BaseModel):
    type: str
    interval_seconds: int = 60
    filter: str = ""
    cron: str = ""
    webhook_path: str = ""


class ErrorHandling(BaseModel):
    network_timeout: str = "retry 3 times with exponential backoff"
    auth_failure: str = "log error, send alert"
    malformed_data: str = "move to review queue"
    rate_limit: str = "pause 60 seconds, resume"


class LoggingConfig(BaseModel):
    location: str = "logs/agent.log"
    format: str = "JSON"
    fields: list[str] = Field(default_factory=lambda: ["timestamp", "action", "status", "error"])


class MockMode(BaseModel):
    trigger: str = "reads from tests/sample_data/"
    output: str = "prints to console"


class Blueprint(BaseModel):
    agent_name: str
    agent_description: str
    architecture_type: ArchitectureType = ArchitectureType.EVENT_DRIVEN
    tools_required: list[ToolRequirement] = Field(default_factory=list)
    trigger_mechanism: TriggerMechanism = Field(default_factory=TriggerMechanism)
    processing_steps: list[str] = Field(default_factory=list)
    data_schema: dict[str, str] = Field(default_factory=dict)
    error_handling: ErrorHandling = Field(default_factory=ErrorHandling)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    mock_mode: MockMode = Field(default_factory=MockMode)
    implementation_base: str = "custom"


# ── Code Execution ────────────────────────────────────────────────────────────

class ExecutionResult(BaseModel):
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration_seconds: float = 0.0
    attempt: int = 1


class ValidationResult(BaseModel):
    passed: bool
    failures: list[str] = Field(default_factory=list)


class DebugResult(BaseModel):
    success: bool
    final_code: str = ""
    attempts_used: int = 0
    message: str = ""
    error_history: list[str] = Field(default_factory=list)


# ── Deployment ────────────────────────────────────────────────────────────────

class DeploymentPackage(BaseModel):
    agent_name: str
    agent_code: str
    requirements: str
    readme: str
    setup_script: str
    env_example: str
    report: str
    output_dir: str = ""
    github_url: str = ""
    zip_path: str = ""


# ── Pipeline ──────────────────────────────────────────────────────────────────

class ProgressUpdate(BaseModel):
    message: str
    percent: int
    status: PipelineStatus
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    detail: str = ""


class PipelineResult(BaseModel):
    status: PipelineStatus
    session_id: str
    agent_name: str = ""
    deployment: DeploymentPackage | None = None
    execution_preview: str = ""
    time_saved_hours_per_week: float = 0.0
    code: str = ""
    error: str = ""
    questions: list[str] = Field(default_factory=list)
    problem: ProblemGraph | None = None
    blueprint: Blueprint | None = None
    total_duration_seconds: float = 0.0
    # New: rich metadata from advanced agents
    critic_report: dict | None = None
    evaluation: dict | None = None
    insights: list[dict] = Field(default_factory=list)
    files_generated: list[str] = Field(default_factory=list)

    @property
    def hours_per_year(self) -> float:
        return self.time_saved_hours_per_week * 52

    @property
    def cost_saved_per_year(self) -> str:
        hourly_rate = 35
        total = self.hours_per_year * hourly_rate
        return f"${total:,.0f}"
