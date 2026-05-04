"""Tests for TranscriberAgent."""

import pytest
import asyncio

from agents.transcriber import TranscriberAgent
from core.models import TranscriptResult


@pytest.mark.asyncio
async def test_demo_transcription():
    agent = TranscriberAgent()
    result = await agent.transcribe_demo()
    assert isinstance(result, TranscriptResult)
    assert len(result.cleaned_text) > 10
    assert result.confidence_score > 0.0
    assert result.word_count > 0


@pytest.mark.asyncio
async def test_demo_with_custom_text():
    agent = TranscriberAgent()
    custom = "I spend 3 hours every day updating spreadsheets manually."
    result = await agent.transcribe_demo(sample_text=custom)
    assert result.cleaned_text == custom
    assert result.word_count == len(custom.split())


def test_clean_text():
    agent = TranscriberAgent()
    text = "  hello world.  this is a test.   "
    cleaned = agent._clean_text(text)
    assert cleaned.startswith("Hello")
    assert "  " not in cleaned
