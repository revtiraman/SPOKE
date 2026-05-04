"""Agent 4 — Architect: designs a complete solution blueprint from the problem graph."""

from __future__ import annotations
from pathlib import Path

from loguru import logger

from core.models import (
    ProblemGraph, Blueprint, ToolRequirement, TriggerMechanism,
    ErrorHandling, LoggingConfig, MockMode, ArchitectureType, AgentCategory,
)
from llm.client import get_client
from llm.router import router


_PROMPT_PATH = Path(__file__).parent.parent / "llm" / "prompts" / "architect_prompt.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()

_DEMO_BLUEPRINT = Blueprint(
    agent_name="OrderSync",
    agent_description="Automatically extracts order data from Gmail and syncs it to Google Sheets every 60 seconds",
    architecture_type=ArchitectureType.EVENT_DRIVEN,
    tools_required=[
        ToolRequirement(
            name="Gmail API",
            purpose="Read unread order emails from inbox",
            auth="OAuth2 service account",
            endpoints=["gmail.users.messages.list", "gmail.users.messages.get", "gmail.users.messages.modify"],
        ),
        ToolRequirement(
            name="Google Sheets API",
            purpose="Append extracted order rows to spreadsheet",
            auth="OAuth2 service account",
            endpoints=["spreadsheets.values.append", "spreadsheets.values.get"],
        ),
    ],
    trigger_mechanism=TriggerMechanism(
        type="polling",
        interval_seconds=60,
        filter="subject:order is:unread label:inbox",
    ),
    processing_steps=[
        "1. Poll Gmail API for unread emails matching 'order' filter",
        "2. For each email: fetch full message body (text + HTML)",
        "3. Use LLM to extract: customer_name, product_name, quantity, total_price, order_date",
        "4. Validate extracted fields — flag rows with confidence < 0.8",
        "5. Append valid rows to Google Sheets via API",
        "6. Move low-confidence emails to 'Review' Gmail label",
        "7. Mark all processed emails as read + apply 'spoke-processed' label",
        "8. Log every action as JSON: email_id, extracted_data, sheet_row, timestamp",
        "9. Sleep for poll interval, then repeat",
    ],
    data_schema={
        "customer_name": "string",
        "product_name": "string",
        "quantity": "integer",
        "total_price": "float",
        "order_date": "ISO8601 date string",
        "email_id": "string (Gmail message ID)",
        "confidence_score": "float (0.0–1.0)",
        "processed_at": "ISO8601 datetime",
    },
    error_handling=ErrorHandling(
        network_timeout="retry 3× with exponential backoff: 2s, 4s, 8s",
        auth_failure="log full traceback, send alert email to owner, pause agent",
        malformed_data="move email to Review label, log for manual inspection, continue",
        rate_limit="respect Retry-After header, wait then resume automatically",
    ),
    logging=LoggingConfig(
        location="logs/ordersync.log",
        format="JSON",
        fields=["timestamp", "email_id", "action", "status", "data_extracted", "error"],
    ),
    mock_mode=MockMode(
        trigger="reads sample emails from tests/sample_emails/ folder",
        output="prints formatted Rich table to console instead of writing to Sheets",
    ),
    implementation_base="email_processor",
)


class ArchitectAgent:
    """Designs a complete, production-ready agent blueprint from a problem graph."""

    async def design(self, problem: ProblemGraph) -> Blueprint:
        """Design a complete solution blueprint."""
        logger.info(f"Designing architecture for: {problem.core_pain[:60]}...")

        client = get_client()
        raw = await client.complete_json(
            model=router.architect_model,
            system=_SYSTEM_PROMPT,
            user=(
                f"Design an autonomous agent for this problem:\n\n"
                f"{problem.model_dump_json(indent=2)}"
            ),
            temperature=0.2,
            max_tokens=3000,
        )

        blueprint = self._parse_blueprint(raw)
        logger.success(f"Blueprint designed: {blueprint.agent_name} ({blueprint.architecture_type})")
        return blueprint

    def _parse_blueprint(self, raw: dict) -> Blueprint:
        """Parse raw LLM output into a Blueprint with safe fallbacks."""
        tools = [
            ToolRequirement(
                name=t.get("name", "API"),
                purpose=t.get("purpose", ""),
                auth=t.get("auth", "API key"),
                endpoints=t.get("endpoints", []),
            )
            for t in raw.get("tools_required", [])
        ]

        trigger_raw = raw.get("trigger_mechanism", {})
        trigger = TriggerMechanism(
            type=trigger_raw.get("type", "polling"),
            interval_seconds=int(trigger_raw.get("interval_seconds", 60)),
            filter=trigger_raw.get("filter", ""),
            cron=trigger_raw.get("cron", ""),
        )

        err_raw = raw.get("error_handling", {})
        error_handling = ErrorHandling(
            network_timeout=err_raw.get("network_timeout", "retry 3×"),
            auth_failure=err_raw.get("auth_failure", "log and alert"),
            malformed_data=err_raw.get("malformed_data", "log and skip"),
            rate_limit=err_raw.get("rate_limit", "pause and retry"),
        )

        log_raw = raw.get("logging", {})
        logging_cfg = LoggingConfig(
            location=log_raw.get("location", "logs/agent.log"),
            format=log_raw.get("format", "JSON"),
            fields=log_raw.get("fields", ["timestamp", "action", "status"]),
        )

        mock_raw = raw.get("mock_mode", {})
        mock_mode = MockMode(
            trigger=mock_raw.get("trigger", "reads from tests/sample_data/"),
            output=mock_raw.get("output", "prints to console"),
        )

        arch_str = raw.get("architecture_type", "event_driven")
        try:
            arch_type = ArchitectureType(arch_str)
        except ValueError:
            arch_type = ArchitectureType.EVENT_DRIVEN

        return Blueprint(
            agent_name=raw.get("agent_name", "AutoAgent"),
            agent_description=raw.get("agent_description", "An autonomous automation agent"),
            architecture_type=arch_type,
            tools_required=tools,
            trigger_mechanism=trigger,
            processing_steps=raw.get("processing_steps", []),
            data_schema=raw.get("data_schema", {}),
            error_handling=error_handling,
            logging=logging_cfg,
            mock_mode=mock_mode,
            implementation_base=raw.get("implementation_base", "custom"),
        )

    async def design_demo(self) -> Blueprint:
        """Return demo blueprint instantly without API call."""
        logger.info("[DEMO] Returning pre-built blueprint")
        return _DEMO_BLUEPRINT
