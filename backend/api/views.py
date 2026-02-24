"""
API Views

REST API endpoints for document processing and RAG operations.
"""

import os
import tempfile
from pathlib import Path

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
import os
import logging

logger = logging.getLogger(__name__)

from .serializers import (
    DocumentUploadSerializer,
    QuerySerializer,
    DocumentListSerializer,
    DocumentDeleteSerializer,
    CampaignRequestSerializer,
)
from .services import DocumentService, RAGService


@api_view(['GET'])
def health_check(request):
    """Health check endpoint for monitoring and load balancers."""
    try:
        # Check if services are initialized
        stats = DocumentService.get_stats()
        return Response({
            'status': 'healthy',
            'service': 'haystack-backend',
            'version': '2.0.0',
            'stats': stats,
        })
    except Exception as e:
        return Response({
            'status': 'degraded',
            'service': 'haystack-backend',
            'error': str(e),
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_document(request):
    """
    Upload and index a document file.

    Supports: PDF, DOCX, PPTX, TXT, MD

    Request:
        - file: Document file (multipart/form-data)
        - document_id: Optional document ID
        - metadata: Optional metadata JSON

    Returns:
        - success: Boolean indicating success
        - document_id: ID of the indexed document
        - chunks_added: Number of chunks indexed
        - metadata: Document metadata

    Example:
        POST /api/v1/documents/upload
        Content-Type: multipart/form-data
        file: <document.pdf>
    """
    try:
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid request data',
                'details': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # Handle file upload
        uploaded_file = serializer.validated_data.get('file')
        if uploaded_file:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(uploaded_file.name).suffix,
            ) as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name

            try:
                result = DocumentService.index_file(
                    file_path=temp_path,
                    metadata=serializer.validated_data.get('metadata'),
                )
            finally:
                # Clean up temp file
                os.unlink(temp_path)
        else:
            # Handle text input
            text = serializer.validated_data.get('text', '')
            document_id = serializer.validated_data.get(
                'document_id',
                f'doc_{hash(text)}',
            )
            result = DocumentService.index_text(
                text=text,
                document_id=document_id,
                metadata=serializer.validated_data.get('metadata'),
            )

        if result.get('success'):
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'success': False,
            'error': f'Document upload failed: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def query_rag(request):
    """
    Query the RAG system with a question.

    Request:
        - query: User question (required)
        - top_k: Number of documents to retrieve (default: 5)
        - filters: Metadata filters (optional)
        - retrieval_method: 'semantic' or 'hybrid' (default: 'semantic')

    Returns:
        - answer: Generated answer
        - sources: Retrieved source documents
        - query: Original query
        - meta: Response metadata

    Example:
        POST /api/v1/query
        {
            "query": "What is the return policy?",
            "top_k": 5,
            "retrieval_method": "hybrid"
        }
    """
    try:
        serializer = QuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid request data',
                'details': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        result = RAGService.query(
            query=serializer.validated_data['query'],
            top_k=serializer.validated_data.get('top_k', 5),
            filters=serializer.validated_data.get('filters'),
            retrieval_method=serializer.validated_data.get('retrieval_method', 'semantic'),
        )

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': f'Query failed: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_documents(request):
    """
    List indexed documents.

    Query params:
        - filters: JSON-encoded metadata filters
        - limit: Maximum number of documents to return (default: 100)

    Returns:
        - documents: List of documents
        - total: Total count

    Example:
        GET /api/v1/documents?limit=50
    """
    try:
        serializer = DocumentListSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid request data',
                'details': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        result = DocumentService.list_documents(
            filters=serializer.validated_data.get('filters'),
            limit=serializer.validated_data.get('limit', 100),
        )

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to list documents: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_document(request):
    """
    Delete a document from the index.

    Request body:
        - document_id: ID of the document to delete

    Returns:
        - success: Boolean indicating success
        - document_id: ID of the deleted document
        - chunks_deleted: Number of chunks deleted

    Example:
        DELETE /api/v1/documents
        {
            "document_id": "doc_abc123"
        }
    """
    try:
        serializer = DocumentDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid request data',
                'details': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        result = DocumentService.delete_document(
            document_id=serializer.validated_data['document_id'],
        )

        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'success': False,
            'error': f'Deletion failed: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_stats(request):
    """
    Get vector store statistics.

    Returns:
        - total_documents: Total number of documents

    Example:
        GET /api/v1/stats
    """
    try:
        result = DocumentService.get_stats()
        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to get stats: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def generate_campaign(request):
    """
    Generate a comprehensive marketing campaign using CrewAI agents.

    Request:
        - campaign_topic: Main topic of the campaign (required)
        - target_audience: Description of target audience (required)
        - campaign_goals: What the campaign aims to achieve (required)
        - key_messages: Core messages to communicate (required)

    Returns:
        - success: Boolean indicating success
        - data: Campaign generation results if successful
        - error: Error message if failed
        - agents_used: List of agents that participated

    Example:
        POST /api/v1/generate-campaign
        {
            "campaign_topic": "AI-Powered Trend Analysis Platform Launch",
            "target_audience": "Data analysts and marketing managers",
            "campaign_goals": "Generate 500 qualified leads",
            "key_messages": "Real-time insights, competitive advantage"
        }
    """
    try:
        serializer = CampaignRequestSerializer(data=request.data)
        if not serializer.is_valid():
            missing_fields = [field for field, errors in serializer.errors.items()]
            error_msg = f"Missing required fields: {', '.join(missing_fields)}" if missing_fields else "Invalid request data"
            return Response({
                'success': False,
                'error': error_msg,
                'details': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get API key from environment
        openai_api_key = os.environ.get('OPENAI_API_KEY')

        # Import marketing crew here to fail gracefully if CrewAI is not installed
        try:
            from marketing.crew import create_marketing_crew
        except ImportError as e:
            logger.error(f"CrewAI not installed: {e}")
            return Response({
                'success': False,
                'error': 'CrewAI not installed. Please add crewai to requirements.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create marketing crew
        crew = create_marketing_crew(openai_api_key=openai_api_key)

        # Generate campaign
        logger.info(f"Generating campaign for topic: {serializer.validated_data['campaign_topic']}")
        campaign_input = {
            'campaign_topic': serializer.validated_data['campaign_topic'],
            'target_audience': serializer.validated_data['target_audience'],
            'campaign_goals': serializer.validated_data['campaign_goals'],
            'key_messages': serializer.validated_data['key_messages'],
        }

        result = crew.generate_campaign(campaign_input)

        return Response({
            'success': True,
            'error': None,
            'data': result,
        }, status=status.HTTP_200_OK)

    except ImportError as e:
        logger.error(f"Import error during campaign generation: {e}")
        return Response({
            'success': False,
            'error': 'CrewAI not installed. Please add crewai to requirements.',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Campaign generation failed: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': f'Campaign generation failed: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
