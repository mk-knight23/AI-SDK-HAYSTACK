"""
API Services

Business logic layer for document and RAG operations.
"""

import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

from pipelines import create_rag_pipeline, create_indexing_pipeline, create_hybrid_pipeline
from vectorstores import create_qdrant_store
from embeddings import MistralEmbeddingProvider
from llm import MistralLLMProvider


# Singleton instances
_vector_store = None
_embedder = None
_llm = None
_rag_pipeline = None
_indexing_pipeline = None
_hybrid_pipeline = None


def get_vector_store():
    """Get or create the vector store singleton."""
    global _vector_store
    if _vector_store is None:
        # Configure based on environment
        url = os.environ.get('QDRANT_URL')
        api_key = os.environ.get('QDRANT_API_KEY')
        in_memory = os.environ.get('QDRANT_IN_MEMORY', 'true').lower() == 'true'

        _vector_store = create_qdrant_store(
            url=url,
            api_key=api_key,
            in_memory=in_memory,
        )
    return _vector_store


def get_embedder():
    """Get or create the embedder singleton."""
    global _embedder
    if _embedder is None:
        api_key = os.environ.get('MISTRAL_API_KEY')
        _embedder = MistralEmbeddingProvider(api_key=api_key)
    return _embedder


def get_llm():
    """Get or create the LLM singleton."""
    global _llm
    if _llm is None:
        api_key = os.environ.get('MISTRAL_API_KEY')
        model = os.environ.get('MISTRAL_LLM_MODEL', 'mistral-small')
        _llm = MistralLLMProvider(api_key=api_key, model=model)
    return _llm


def get_rag_pipeline():
    """Get or create the RAG pipeline singleton."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = create_rag_pipeline(
            vector_store=get_vector_store(),
            embedder=get_embedder(),
            llm=get_llm(),
        )
    return _rag_pipeline


def get_indexing_pipeline():
    """Get or create the indexing pipeline singleton."""
    global _indexing_pipeline
    if _indexing_pipeline is None:
        _indexing_pipeline = create_indexing_pipeline(
            vector_store=get_vector_store(),
            embedder=get_embedder(),
        )
    return _indexing_pipeline


def get_hybrid_pipeline():
    """Get or create the hybrid pipeline singleton."""
    global _hybrid_pipeline
    if _hybrid_pipeline is None:
        _hybrid_pipeline = create_hybrid_pipeline(
            vector_store=get_vector_store(),
            embedder=get_embedder(),
            llm=get_llm(),
        )
    return _hybrid_pipeline


class DocumentService:
    """Service for document operations."""

    @staticmethod
    def index_file(
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Index a document file."""
        pipeline = get_indexing_pipeline()
        return pipeline.index_file(file_path, metadata)

    @staticmethod
    def index_text(
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Index raw text."""
        pipeline = get_indexing_pipeline()
        return pipeline.index_text(text, document_id, metadata)

    @staticmethod
    def delete_document(document_id: str) -> Dict[str, Any]:
        """Delete a document from the index."""
        pipeline = get_indexing_pipeline()
        return pipeline.delete_document(document_id)

    @staticmethod
    def list_documents(
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """List documents in the index."""
        store = get_vector_store()
        documents = store.get_documents(filters=filters, limit=limit)

        return {
            'documents': [
                {
                    'id': doc.id,
                    'content': doc.content[:500] + '...' if len(doc.content) > 500 else doc.content,
                    'metadata': doc.meta,
                }
                for doc in documents
            ],
            'total': len(documents),
        }

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get vector store statistics."""
        store = get_vector_store()
        return {
            'total_documents': store.count_documents(),
        }


class RAGService:
    """Service for RAG operations."""

    @staticmethod
    def query(
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        retrieval_method: str = 'semantic',
    ) -> Dict[str, Any]:
        """
        Query the RAG system.

        Args:
            query: User question
            top_k: Number of documents to retrieve
            filters: Metadata filters
            retrieval_method: 'semantic' or 'hybrid'

        Returns:
            Response with answer and sources
        """
        if retrieval_method == 'hybrid':
            pipeline = get_hybrid_pipeline()
        else:
            pipeline = get_rag_pipeline()

        return pipeline.run(query=query, top_k=top_k, filters=filters)
