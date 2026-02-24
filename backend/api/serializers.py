"""
API Serializers

Request/response serializers for document and RAG operations.
"""

from rest_framework import serializers
from typing import Dict, Any


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload requests."""
    file = serializers.FileField(required=False)
    text = serializers.CharField(required=False, allow_blank=True)
    document_id = serializers.CharField(required=False, max_length=255)
    metadata = serializers.JSONField(required=False, default=dict)


class QuerySerializer(serializers.Serializer):
    """Serializer for RAG query requests."""
    query = serializers.CharField(required=True, min_length=1, max_length=2000)
    top_k = serializers.IntegerField(required=False, default=5, min_value=1, max_value=50)
    filters = serializers.JSONField(required=False, default=None)
    retrieval_method = serializers.ChoiceField(
        choices=['semantic', 'hybrid'],
        required=False,
        default='semantic',
    )


class DocumentListSerializer(serializers.Serializer):
    """Serializer for document list requests."""
    filters = serializers.JSONField(required=False, default=None)
    limit = serializers.IntegerField(required=False, default=100, min_value=1, max_value=1000)


class DocumentDeleteSerializer(serializers.Serializer):
    """Serializer for document deletion."""
    document_id = serializers.CharField(required=True, max_length=255)


class CampaignRequestSerializer(serializers.Serializer):
    """Serializer for marketing campaign generation requests."""
    campaign_topic = serializers.CharField(
        required=True,
        max_length=500,
        help_text="Main topic of the marketing campaign"
    )
    target_audience = serializers.CharField(
        required=True,
        max_length=1000,
        help_text="Description of the target audience"
    )
    campaign_goals = serializers.CharField(
        required=True,
        max_length=500,
        help_text="What the campaign aims to achieve"
    )
    key_messages = serializers.CharField(
        required=True,
        max_length=1000,
        help_text="Core messages to communicate"
    )
