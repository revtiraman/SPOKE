"""Tests for AnalystAgent."""

import pytest

from agents.analyst import AnalystAgent
from core.models import AgentCategory, ProblemGraph


@pytest.mark.asyncio
async def test_demo_analysis():
    agent = AnalystAgent()
    problem = await agent.analyse_demo()
    assert isinstance(problem, ProblemGraph)
    assert problem.category == AgentCategory.EMAIL_AUTOMATION
    assert problem.complexity_score >= 1
    assert 0.0 <= problem.confidence <= 1.0
    assert len(problem.process_steps) > 0


def test_parse_problem_safe_defaults():
    agent = AnalystAgent()
    result = agent._parse_problem({
        "core_pain": "doing boring things",
        "trigger": "every morning",
        "process_steps": ["step 1", "step 2"],
    })
    assert result.core_pain == "doing boring things"
    assert result.category == AgentCategory.OTHER
    assert result.complexity_score == 2


def test_parse_problem_category_normalisation():
    agent = AnalystAgent()
    result = agent._parse_problem({
        "core_pain": "x",
        "trigger": "y",
        "process_steps": [],
        "category": "email-automation",
    })
    assert result.category == AgentCategory.EMAIL_AUTOMATION
