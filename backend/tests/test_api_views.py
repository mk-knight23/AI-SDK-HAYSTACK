"""
Tests for API views.
"""

import pytest
from rest_framework.test import APIRequestFactory
from unittest.mock import patch, Mock

from api.views import (
    health_check,
    query_rag,
    list_documents,
    delete_document,
    get_stats,
)
from api.serializers import (
    QuerySerializer,
    DocumentListSerializer,
    DocumentDeleteSerializer,
)


class TestHealthCheck:
    """Test health check endpoint."""

    @patch('api.views.DocumentService.get_stats')
    def test_health_check_returns_healthy(self, mock_get_stats):
        """Test health check returns healthy status."""
        mock_get_stats.return_value = {'total_documents': 5}

        factory = APIRequestFactory()
        request = factory.get('/api/v1/health')
        response = health_check(request)

        assert response.status_code == 200
        assert response.data['status'] == 'healthy'
        assert response.data['service'] == 'haystack-backend'

    @patch('api.views.DocumentService.get_stats')
    def test_health_check_returns_degraded_on_error(self, mock_get_stats):
        """Test health check returns degraded status on error."""
        mock_get_stats.side_effect = Exception('Database error')

        factory = APIRequestFactory()
        request = factory.get('/api/v1/health')
        response = health_check(request)

        assert response.status_code == 503
        assert response.data['status'] == 'degraded'


class TestQueryRAG:
    """Test RAG query endpoint."""

    @patch('api.views.RAGService.query')
    def test_query_rag_returns_answer(self, mock_query):
        """Test query endpoint returns answer and sources."""
        mock_query.return_value = {
            'answer': 'Test answer',
            'sources': [
                {
                    'id': 'doc1',
                    'content': 'Source content',
                    'metadata': {},
                }
            ],
            'query': 'Test query',
        }

        factory = APIRequestFactory()
        request = factory.post('/api/v1/query', {'query': 'Test query'}, format='json')
        response = query_rag(request)

        assert response.status_code == 200
        assert response.data['answer'] == 'Test answer'
        assert len(response.data['sources']) == 1

    def test_query_rag_validates_required_fields(self):
        """Test query endpoint validates query field."""
        factory = APIRequestFactory()
        request = factory.post('/api/v1/query', {}, format='json')
        response = query_rag(request)

        assert response.status_code == 400

    def test_query_rag_validates_query_length(self):
        """Test query endpoint validates query length."""
        factory = APIRequestFactory()
        request = factory.post('/api/v1/query', {'query': ''}, format='json')
        response = query_rag(request)

        assert response.status_code == 400

    @patch('api.views.RAGService.query')
    def test_query_rag_passes_options(self, mock_query):
        """Test query endpoint passes options to service."""
        mock_query.return_value = {
            'answer': 'Test',
            'sources': [],
            'query': 'Test',
        }

        factory = APIRequestFactory()
        request = factory.post(
            '/api/v1/query',
            {
                'query': 'Test',
                'top_k': 10,
                'retrieval_method': 'hybrid',
            },
            format='json',
        )
        response = query_rag(request)

        mock_query.assert_called_once()
        call_kwargs = mock_query.call_args[1]
        assert call_kwargs['top_k'] == 10
        assert call_kwargs['retrieval_method'] == 'hybrid'

    @patch('api.views.RAGService.query')
    def test_query_rag_handles_errors(self, mock_query):
        """Test query endpoint handles service errors."""
        mock_query.side_effect = Exception('LLM error')

        factory = APIRequestFactory()
        request = factory.post('/api/v1/query', {'query': 'Test'}, format='json')
        response = query_rag(request)

        assert response.status_code == 500
        assert response.data['success'] is False


class TestListDocuments:
    """Test document list endpoint."""

    @patch('api.views.DocumentService.list_documents')
    def test_list_documents_returns_list(self, mock_list):
        """Test list documents returns document list."""
        mock_list.return_value = {
            'documents': [
                {'id': 'doc1', 'content': 'Content 1', 'metadata': {}},
                {'id': 'doc2', 'content': 'Content 2', 'metadata': {}},
            ],
            'total': 2,
        }

        factory = APIRequestFactory()
        request = factory.get('/api/v1/documents')
        response = list_documents(request)

        assert response.status_code == 200
        assert len(response.data['documents']) == 2
        assert response.data['total'] == 2

    @patch('api.views.DocumentService.list_documents')
    def test_list_documents_passes_limit(self, mock_list):
        """Test list documents passes limit parameter."""
        mock_list.return_value = {'documents': [], 'total': 0}

        factory = APIRequestFactory()
        request = factory.get('/api/v1/documents?limit=50')
        response = list_documents(request)

        mock_list.assert_called_once()
        call_kwargs = mock_list.call_args[1]
        assert call_kwargs['limit'] == 50


class TestDeleteDocument:
    """Test document deletion endpoint."""

    @patch('api.views.DocumentService.delete_document')
    def test_delete_document_succeeds(self, mock_delete):
        """Test delete document succeeds."""
        mock_delete.return_value = {
            'success': True,
            'document_id': 'doc1',
            'chunks_deleted': 5,
        }

        factory = APIRequestFactory()
        request = factory.delete('/api/v1/documents', {'document_id': 'doc1'}, format='json')
        response = delete_document(request)

        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['chunks_deleted'] == 5

    def test_delete_document_validates_document_id(self):
        """Test delete document validates document_id."""
        factory = APIRequestFactory()
        request = factory.delete('/api/v1/documents', {}, format='json')
        response = delete_document(request)

        assert response.status_code == 400


class TestGetStats:
    """Test stats endpoint."""

    @patch('api.views.DocumentService.get_stats')
    def test_get_stats_returns_counts(self, mock_stats):
        """Test get stats returns document counts."""
        mock_stats.return_value = {
            'total_documents': 42,
        }

        factory = APIRequestFactory()
        request = factory.get('/api/v1/stats')
        response = get_stats(request)

        assert response.status_code == 200
        assert response.data['total_documents'] == 42
