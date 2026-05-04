"""End-to-end pipeline integration tests using demo mode."""

import pytest

from core.models import PipelineStatus
from core.pipeline import SpokePipeline


@pytest.mark.asyncio
async def test_demo_pipeline_full_run():
    """Full end-to-end pipeline in demo mode — zero credentials required."""
    pipeline = SpokePipeline()

    progress_events = []

    async def capture_progress(msg, pct, status, detail=""):
        progress_events.append((msg, pct, status))

    result = await pipeline.run(
        demo_mode=True,
        progress=capture_progress,
    )

    assert result.status == PipelineStatus.SUCCESS, f"Pipeline failed: {result.error}"
    assert result.agent_name
    assert result.code
    assert result.execution_preview
    assert result.time_saved_hours_per_week > 0
    assert result.deployment is not None
    assert result.deployment.agent_code
    assert result.deployment.readme
    assert result.deployment.requirements
    assert len(progress_events) > 3


@pytest.mark.asyncio
async def test_demo_pipeline_with_transcript():
    """Pipeline from text transcript in demo mode."""
    pipeline = SpokePipeline()

    result = await pipeline.run(
        transcript_text="I spend 2 hours every day manually copying data from emails to a spreadsheet.",
        demo_mode=True,
    )

    assert result.status == PipelineStatus.SUCCESS
    assert result.session_id


@pytest.mark.asyncio
async def test_pipeline_result_has_deployment_package():
    pipeline = SpokePipeline()
    result = await pipeline.run(demo_mode=True)

    dep = result.deployment
    assert dep is not None
    assert len(dep.agent_code) > 100
    assert "requirements" in dep.requirements.lower() or "loguru" in dep.requirements
    assert dep.setup_script.startswith("#!/bin/bash")
    assert "# " in dep.readme
