"""
Tests for the API views module.

This module tests the API endpoints including:
- Health check endpoint
- Campaign generation endpoint
"""

import pytest
import sys
from unittest.mock import MagicMock, patch
import json

# Create mock crewai module before importing
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


class TestHealthCheckEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200(self, api_client):
        """Test health check returns 200 status code."""
        response = api_client.get('/health')

        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, api_client):
        """Test health check returns healthy status."""
        response = api_client.get('/health')

        assert response.data['status'] == 'healthy'

    def test_health_check_includes_service_name(self, api_client):
        """Test health check includes service name."""
        response = api_client.get('/health')

        assert 'service' in response.data
        assert 'trendfactory' in response.data['service']

    def test_health_check_includes_version(self, api_client):
        """Test health check includes version."""
        response = api_client.get('/health')

        assert 'version' in response.data
        assert response.data['version'] == '1.0.0'


class TestGenerateCampaignEndpoint:
    """Tests for the generate campaign endpoint."""

    @patch('marketing.crew.create_marketing_crew')
    def test_generate_campaign_returns_200_on_success(self, mock_create_crew, api_client):
        """Test successful campaign generation returns 200."""
        mock_crew = MagicMock()
        mock_crew.generate_campaign.return_value = {
            'success': True,
            'campaign_topic': 'Test Topic',
            'results': {'test': 'data'},
            'agents_used': ['ContentStrategist', 'Copywriter', 'SEOExpert', 'CampaignManager']
        }
        mock_create_crew.return_value = mock_crew

        data = {
            'campaign_topic': 'AI-Powered Trend Analysis Platform Launch',
            'target_audience': 'Data analysts and marketing managers',
            'campaign_goals': 'Generate 500 qualified leads',
            'key_messages': 'Real-time insights, competitive advantage'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.status_code == 200

    @patch('marketing.crew.create_marketing_crew')
    def test_generate_campaign_returns_success_response(self, mock_create_crew, api_client):
        """Test successful campaign generation returns success response."""
        mock_crew = MagicMock()
        mock_crew.generate_campaign.return_value = {
            'success': True,
            'campaign_topic': 'Test Topic',
            'results': {'test': 'data'},
            'agents_used': ['ContentStrategist', 'Copywriter', 'SEOExpert', 'CampaignManager']
        }
        mock_create_crew.return_value = mock_crew

        data = {
            'campaign_topic': 'AI-Powered Trend Analysis Platform Launch',
            'target_audience': 'Data analysts and marketing managers',
            'campaign_goals': 'Generate 500 qualified leads',
            'key_messages': 'Real-time insights, competitive advantage'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.data['success'] is True
        assert response.data['error'] is None

    @patch('marketing.crew.create_marketing_crew')
    def test_generate_campaign_returns_campaign_data(self, mock_create_crew, api_client):
        """Test successful campaign generation returns campaign data."""
        mock_crew = MagicMock()
        mock_crew.generate_campaign.return_value = {
            'success': True,
            'campaign_topic': 'Test Topic',
            'results': {'test': 'data'},
            'agents_used': ['ContentStrategist', 'Copywriter', 'SEOExpert', 'CampaignManager']
        }
        mock_create_crew.return_value = mock_crew

        data = {
            'campaign_topic': 'AI-Powered Trend Analysis Platform Launch',
            'target_audience': 'Data analysts and marketing managers',
            'campaign_goals': 'Generate 500 qualified leads',
            'key_messages': 'Real-time insights, competitive advantage'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert 'data' in response.data
        assert response.data['data']['campaign_topic'] == 'Test Topic'

    @patch('marketing.crew.create_marketing_crew')
    def test_generate_campaign_creates_crew_with_api_key(self, mock_create_crew, api_client):
        """Test campaign endpoint creates crew with API key from environment."""
        mock_crew = MagicMock()
        mock_crew.generate_campaign.return_value = {
            'success': True,
            'campaign_topic': 'Test',
            'results': {},
            'agents_used': []
        }
        mock_create_crew.return_value = mock_crew

        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-env-key'}):
            data = {
                'campaign_topic': 'Test Topic',
                'target_audience': 'Test Audience',
                'campaign_goals': 'Test Goals',
                'key_messages': 'Test Messages'
            }
            api_client.post('/generate-campaign', data, format='json')

            mock_create_crew.assert_called_once_with(openai_api_key='test-env-key')

    @patch('marketing.crew.create_marketing_crew')
    def test_generate_campaign_calls_generate_campaign(self, mock_create_crew, api_client):
        """Test campaign endpoint calls crew.generate_campaign with correct input."""
        mock_crew = MagicMock()
        mock_crew.generate_campaign.return_value = {
            'success': True,
            'campaign_topic': 'Test',
            'results': {},
            'agents_used': []
        }
        mock_create_crew.return_value = mock_crew

        data = {
            'campaign_topic': 'AI-Powered Trend Analysis Platform Launch',
            'target_audience': 'Data analysts',
            'campaign_goals': 'Generate 500 leads',
            'key_messages': 'Real-time insights'
        }

        api_client.post('/generate-campaign', data, format='json')

        mock_crew.generate_campaign.assert_called_once()
        call_args = mock_crew.generate_campaign.call_args[0][0]
        assert call_args['campaign_topic'] == 'AI-Powered Trend Analysis Platform Launch'
        assert call_args['target_audience'] == 'Data analysts'


class TestGenerateCampaignValidation:
    """Tests for campaign endpoint input validation."""

    def test_generate_campaign_returns_400_for_missing_topic(self, api_client):
        """Test missing campaign_topic returns 400 error."""
        data = {
            'target_audience': 'Data analysts',
            'campaign_goals': 'Generate 500 leads',
            'key_messages': 'Real-time insights'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'campaign_topic' in response.data['error']

    def test_generate_campaign_returns_400_for_missing_audience(self, api_client):
        """Test missing target_audience returns 400 error."""
        data = {
            'campaign_topic': 'AI Platform',
            'campaign_goals': 'Generate 500 leads',
            'key_messages': 'Real-time insights'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'target_audience' in response.data['error']

    def test_generate_campaign_returns_400_for_missing_goals(self, api_client):
        """Test missing campaign_goals returns 400 error."""
        data = {
            'campaign_topic': 'AI Platform',
            'target_audience': 'Data analysts',
            'key_messages': 'Real-time insights'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'campaign_goals' in response.data['error']

    def test_generate_campaign_returns_400_for_missing_messages(self, api_client):
        """Test missing key_messages returns 400 error."""
        data = {
            'campaign_topic': 'AI Platform',
            'target_audience': 'Data analysts',
            'campaign_goals': 'Generate 500 leads'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'key_messages' in response.data['error']

    def test_generate_campaign_returns_400_for_empty_request(self, api_client):
        """Test empty request returns 400 error."""
        data = {}

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'Missing required fields' in response.data['error']

    def test_generate_campaign_lists_all_missing_fields(self, api_client):
        """Test error message lists all missing fields."""
        data = {}

        response = api_client.post('/generate-campaign', data, format='json')

        error_message = response.data['error']
        assert 'campaign_topic' in error_message
        assert 'target_audience' in error_message
        assert 'campaign_goals' in error_message
        assert 'key_messages' in error_message


class TestGenerateCampaignErrorHandling:
    """Tests for campaign endpoint error handling."""

    @patch('marketing.crew.create_marketing_crew')
    def test_generate_campaign_handles_import_error(self, mock_create_crew, api_client):
        """Test endpoint handles CrewAI import error."""
        mock_create_crew.side_effect = ImportError("No module named 'crewai'")

        data = {
            'campaign_topic': 'AI Platform',
            'target_audience': 'Data analysts',
            'campaign_goals': 'Generate 500 leads',
            'key_messages': 'Real-time insights'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.status_code == 500
        assert response.data['success'] is False
        assert 'CrewAI not installed' in response.data['error']

    @patch('marketing.crew.create_marketing_crew')
    def test_generate_campaign_handles_generic_exception(self, mock_create_crew, api_client):
        """Test endpoint handles generic exceptions."""
        mock_create_crew.side_effect = Exception("Something went wrong")

        data = {
            'campaign_topic': 'AI Platform',
            'target_audience': 'Data analysts',
            'campaign_goals': 'Generate 500 leads',
            'key_messages': 'Real-time insights'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.status_code == 500
        assert response.data['success'] is False
        assert 'Campaign generation failed' in response.data['error']

    @patch('marketing.crew.create_marketing_crew')
    def test_generate_campaign_handles_crew_generation_error(self, mock_create_crew, api_client):
        """Test endpoint handles error during campaign generation."""
        mock_crew = MagicMock()
        mock_crew.generate_campaign.side_effect = Exception("Generation failed")
        mock_create_crew.return_value = mock_crew

        data = {
            'campaign_topic': 'AI Platform',
            'target_audience': 'Data analysts',
            'campaign_goals': 'Generate 500 leads',
            'key_messages': 'Real-time insights'
        }

        response = api_client.post('/generate-campaign', data, format='json')

        assert response.status_code == 500
        assert response.data['success'] is False
