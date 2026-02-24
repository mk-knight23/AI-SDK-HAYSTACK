"""
Vector Stores Module

Provides vector storage and retrieval backends:
- Qdrant (default) - High-performance vector database
- Elasticsearch - Full-text + vector search
- In-memory - For development and testing
"""

from .qdrant_store import QdrantVectorStore
from .elasticsearch_store import ElasticsearchVectorStore

__all__ = [
    'QdrantVectorStore',
    'ElasticsearchVectorStore',
]
