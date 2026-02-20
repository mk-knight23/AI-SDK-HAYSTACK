"""
Tests for the CrewAI Marketing Crew module.

This module tests the MarketingCrew class and all its agents:
- ContentStrategist
- Copywriter
- SEOExpert
- CampaignManager
"""

import pytest
import sys
from unittest.mock import MagicMock, patch, call

# Create mock crewai module before importing marketing.crew
mock_crewai = MagicMock()
mock_agent_class = MagicMock()
mock_task_class = MagicMock()
mock_crew_class = MagicMock()
mock_process = MagicMock()
mock_process.sequential = 'sequential'

mock_crewai.Agent = mock_agent_class
mock_crewai.Task = mock_task_class
mock_crewai.Crew = mock_crew_class
mock_crewai.Process = mock_process

# Add mock to sys.modules
sys.modules['crewai'] = mock_crewai
sys.modules['crewai.tools'] = MagicMock()

# Now import the module under test
from marketing.crew import MarketingCrew, create_marketing_crew


class TestMarketingCrewInitialization:
    """Tests for MarketingCrew initialization and setup."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_agent_class.reset_mock()
        mock_task_class.reset_mock()
        mock_crew_class.reset_mock()

    def test_marketing_crew_init_without_api_key(self):
        """Test MarketingCrew initializes correctly without API key."""
        crew = MarketingCrew()

        assert crew.openai_api_key is None
        assert crew.crew is not None
        # Should create 4 agents
        assert mock_agent_class.call_count == 4

    def test_marketing_crew_init_with_api_key(self):
        """Test MarketingCrew initializes correctly with API key."""
        api_key = 'test-api-key-12345'
        crew = MarketingCrew(openai_api_key=api_key)

        assert crew.openai_api_key == api_key
        assert crew.crew is not None

    def test_agents_created_with_correct_roles(self):
        """Test that all agents are created with their correct roles."""
        MarketingCrew()

        # Check that Agent was called 4 times (one for each agent)
        assert mock_agent_class.call_count == 4

        # Get all the calls made to Agent
        calls = mock_agent_class.call_args_list

        # Extract role names from the calls
        roles = [call.kwargs.get('role') for call in calls]

        assert 'Content Strategist' in roles
        assert 'Copywriter' in roles
        assert 'SEO Expert' in roles
        assert 'Campaign Manager' in roles


class TestContentStrategistAgent:
    """Tests for the Content Strategist agent."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_agent_class.reset_mock()
        mock_task_class.reset_mock()
        mock_crew_class.reset_mock()

    def test_content_strategist_configuration(self):
        """Test Content Strategist agent has correct configuration."""
        MarketingCrew()

        # Find the Content Strategist call
        content_strategist_call = None
        for call in mock_agent_class.call_args_list:
            if call.kwargs.get('role') == 'Content Strategist':
                content_strategist_call = call
                break

        assert content_strategist_call is not None
        assert 'Develop compelling content strategies' in content_strategist_call.kwargs.get('goal', '')
        assert content_strategist_call.kwargs.get('verbose') is True
        assert content_strategist_call.kwargs.get('allow_delegation') is True

    def test_content_strategist_backstory(self):
        """Test Content Strategist has descriptive backstory."""
        MarketingCrew()

        content_strategist_call = None
        for call in mock_agent_class.call_args_list:
            if call.kwargs.get('role') == 'Content Strategist':
                content_strategist_call = call
                break

        backstory = content_strategist_call.kwargs.get('backstory', '')
        assert 'content strategist' in backstory.lower()
        assert 'B2B SaaS' in backstory or 'SaaS' in backstory


class TestCopywriterAgent:
    """Tests for the Copywriter agent."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_agent_class.reset_mock()
        mock_task_class.reset_mock()
        mock_crew_class.reset_mock()

    def test_copywriter_configuration(self):
        """Test Copywriter agent has correct configuration."""
        MarketingCrew()

        copywriter_call = None
        for call in mock_agent_class.call_args_list:
            if call.kwargs.get('role') == 'Copywriter':
                copywriter_call = call
                break

        assert copywriter_call is not None
        assert 'Create engaging, persuasive copy' in copywriter_call.kwargs.get('goal', '')
        assert copywriter_call.kwargs.get('verbose') is True
        assert copywriter_call.kwargs.get('allow_delegation') is False

    def test_copywriter_backstory(self):
        """Test Copywriter has descriptive backstory."""
        MarketingCrew()

        copywriter_call = None
        for call in mock_agent_class.call_args_list:
            if call.kwargs.get('role') == 'Copywriter':
                copywriter_call = call
                break

        backstory = copywriter_call.kwargs.get('backstory', '')
        assert 'copywriter' in backstory.lower() or 'Fortune 500' in backstory


class TestSEOExpertAgent:
    """Tests for the SEO Expert agent."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_agent_class.reset_mock()
        mock_task_class.reset_mock()
        mock_crew_class.reset_mock()

    def test_seo_expert_configuration(self):
        """Test SEO Expert agent has correct configuration."""
        MarketingCrew()

        seo_call = None
        for call in mock_agent_class.call_args_list:
            if call.kwargs.get('role') == 'SEO Expert':
                seo_call = call
                break

        assert seo_call is not None
        assert 'Optimize all content' in seo_call.kwargs.get('goal', '')
        assert seo_call.kwargs.get('verbose') is True
        assert seo_call.kwargs.get('allow_delegation') is False

    def test_seo_expert_temperature(self):
        """Test SEO Expert has lower temperature for consistency."""
        api_key = 'test-key'
        MarketingCrew(openai_api_key=api_key)

        seo_call = None
        for call in mock_agent_class.call_args_list:
            if call.kwargs.get('role') == 'SEO Expert':
                seo_call = call
                break

        llm_config = seo_call.kwargs.get('llm_config', {})
        assert llm_config.get('temperature') == 0.6


class TestCampaignManagerAgent:
    """Tests for the Campaign Manager agent."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_agent_class.reset_mock()
        mock_task_class.reset_mock()
        mock_crew_class.reset_mock()

    def test_campaign_manager_configuration(self):
        """Test Campaign Manager agent has correct configuration."""
        MarketingCrew()

        manager_call = None
        for call in mock_agent_class.call_args_list:
            if call.kwargs.get('role') == 'Campaign Manager':
                manager_call = call
                break

        assert manager_call is not None
        assert 'Orchestrate all marketing activities' in manager_call.kwargs.get('goal', '')
        assert manager_call.kwargs.get('verbose') is True
        assert manager_call.kwargs.get('allow_delegation') is True


class TestMarketingCrewTasks:
    """Tests for task creation and configuration."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_agent_class.reset_mock()
        mock_task_class.reset_mock()
        mock_crew_class.reset_mock()

    def test_strategy_task_created(self):
        """Test strategy task is created with correct configuration."""
        MarketingCrew()

        # Task should be called 4 times (one for each task)
        assert mock_task_class.call_count == 4

        # Find strategy task
        strategy_call = None
        for call in mock_task_class.call_args_list:
            description = call.kwargs.get('description', '')
            if 'content strategy' in description.lower():
                strategy_call = call
                break

        assert strategy_call is not None
        assert 'campaign_topic' in strategy_call.kwargs.get('description', '')

    def test_copywriting_task_created(self):
        """Test copywriting task is created with correct configuration."""
        MarketingCrew()

        copywriting_call = None
        for call in mock_task_class.call_args_list:
            description = call.kwargs.get('description', '')
            if 'Email sequence' in description or 'copy' in description.lower():
                copywriting_call = call
                break

        assert copywriting_call is not None
        assert 'expected_output' in copywriting_call.kwargs

    def test_seo_task_created(self):
        """Test SEO task is created with correct configuration."""
        MarketingCrew()

        seo_call = None
        for call in mock_task_class.call_args_list:
            description = call.kwargs.get('description', '')
            if 'SEO' in description or 'keyword' in description.lower():
                seo_call = call
                break

        assert seo_call is not None

    def test_campaign_plan_task_created(self):
        """Test campaign plan task is created with correct configuration."""
        MarketingCrew()

        plan_call = None
        for call in mock_task_class.call_args_list:
            description = call.kwargs.get('description', '')
            if 'campaign execution plan' in description.lower():
                plan_call = call
                break

        assert plan_call is not None


class TestGenerateCampaign:
    """Tests for the generate_campaign method."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_agent_class.reset_mock()
        mock_task_class.reset_mock()
        mock_crew_class.reset_mock()

    def test_generate_campaign_returns_success(self):
        """Test generate_campaign returns success response."""
        # Setup mock crew instance
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = {'result': 'test campaign data'}
        mock_crew_class.return_value = mock_crew_instance

        crew = MarketingCrew()
        campaign_input = {
            'campaign_topic': 'Test Topic',
            'target_audience': 'Test Audience',
            'campaign_goals': 'Test Goals',
            'key_messages': 'Test Messages'
        }

        result = crew.generate_campaign(campaign_input)

        assert result['success'] is True
        assert result['campaign_topic'] == 'Test Topic'
        assert 'results' in result
        assert 'agents_used' in result

    def test_generate_campaign_calls_kickoff(self):
        """Test generate_campaign calls crew.kickoff with correct inputs."""
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = {'result': 'test'}
        mock_crew_class.return_value = mock_crew_instance

        crew = MarketingCrew()
        campaign_input = {
            'campaign_topic': 'Test Topic',
            'target_audience': 'Test Audience',
            'campaign_goals': 'Test Goals',
            'key_messages': 'Test Messages'
        }

        crew.generate_campaign(campaign_input)

        mock_crew_instance.kickoff.assert_called_once_with(inputs=campaign_input)

    def test_generate_campaign_includes_all_agents(self):
        """Test generate_campaign response includes all agent names."""
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = {'result': 'test'}
        mock_crew_class.return_value = mock_crew_instance

        crew = MarketingCrew()
        campaign_input = {
            'campaign_topic': 'Test Topic',
            'target_audience': 'Test Audience',
            'campaign_goals': 'Test Goals',
            'key_messages': 'Test Messages'
        }

        result = crew.generate_campaign(campaign_input)

        agents = result['agents_used']
        assert 'ContentStrategist' in agents
        assert 'Copywriter' in agents
        assert 'SEOExpert' in agents
        assert 'CampaignManager' in agents


class TestCreateMarketingCrewFactory:
    """Tests for the create_marketing_crew factory function."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_agent_class.reset_mock()
        mock_task_class.reset_mock()
        mock_crew_class.reset_mock()

    def test_factory_function_returns_marketing_crew(self):
        """Test factory function returns MarketingCrew instance."""
        crew = create_marketing_crew()

        assert isinstance(crew, MarketingCrew)

    def test_factory_function_passes_api_key(self):
        """Test factory function passes API key to MarketingCrew."""
        api_key = 'test-factory-api-key'
        crew = create_marketing_crew(openai_api_key=api_key)

        assert crew.openai_api_key == api_key

    def test_factory_function_without_api_key(self):
        """Test factory function works without API key."""
        crew = create_marketing_crew()

        assert crew.openai_api_key is None
