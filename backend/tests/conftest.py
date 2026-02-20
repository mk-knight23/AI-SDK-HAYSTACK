"""
Pytest configuration and fixtures for TrendFactory tests.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_crewai_agent():
    """Fixture to mock CrewAI Agent class."""
    with patch('marketing.crew.Agent') as MockAgent:
        agent_instance = MagicMock()
        MockAgent.return_value = agent_instance
        yield MockAgent, agent_instance


@pytest.fixture
def mock_crewai_task():
    """Fixture to mock CrewAI Task class."""
    with patch('marketing.crew.Task') as MockTask:
        task_instance = MagicMock()
        MockTask.return_value = task_instance
        yield MockTask, task_instance


@pytest.fixture
def mock_crewai_crew():
    """Fixture to mock CrewAI Crew class."""
    with patch('marketing.crew.Crew') as MockCrew:
        crew_instance = MagicMock()
        crew_instance.kickoff.return_value = {
            'strategy': 'Test strategy content',
            'copy': 'Test copy content',
            'seo': 'Test SEO content',
            'campaign_plan': 'Test campaign plan'
        }
        MockCrew.return_value = crew_instance
        yield MockCrew, crew_instance


@pytest.fixture
def mock_crewai_process():
    """Fixture to mock CrewAI Process enum."""
    with patch('marketing.crew.Process') as MockProcess:
        MockProcess.sequential = 'sequential'
        yield MockProcess


@pytest.fixture
def campaign_input():
    """Fixture providing valid campaign input data."""
    return {
        'campaign_topic': 'AI-Powered Trend Analysis Platform Launch',
        'target_audience': 'Data analysts and marketing managers at mid-market companies',
        'campaign_goals': 'Generate 500 qualified leads in Q1 2025',
        'key_messages': 'Real-time insights, competitive advantage, easy integration'
    }


@pytest.fixture
def api_client():
    """Fixture providing Django REST framework API client."""
    from rest_framework.test import APIClient
    return APIClient()
