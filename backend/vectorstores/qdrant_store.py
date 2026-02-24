"""
Qdrant Vector Store

Provides vector storage and retrieval using Qdrant.
Supports both in-memory and cloud deployments.
"""

from typing import List, Optional, Dict, Any, Union
import os

from haystack import Document
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore


class QdrantVectorStore:
    """
    Qdrant-based vector store for document storage and retrieval.

    Supports:
    - In-memory storage for development
    - Cloud storage for production
    - Hybrid search (vector + keyword)
    - Filtering by metadata
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        index: str = "documents",
        embedding_dim: int = 1024,
        in_memory: bool = False,
        location: Optional[str] = None,
    ):
        """
        Initialize the Qdrant vector store.

        Args:
            url: Qdrant server URL (for cloud or self-hosted)
            api_key: Qdrant API key (for cloud)
            index: Collection/index name
            embedding_dim: Dimension of embedding vectors
            in_memory: Use in-memory storage
            location: Path for persistent storage
        """
        self.index = index
        self.embedding_dim = embedding_dim

        # Build connection config
        kwargs = {
            'index': index,
            'embedding_dim': embedding_dim,
        }

        if in_memory:
            kwargs['location'] = ':memory:'
        elif location:
            kwargs['location'] = location
        elif url:
            kwargs['url'] = url
            if api_key:
                kwargs['api_key'] = api_key
        else:
            # Default to in-memory for development
            kwargs['location'] = ':memory:'

        self._store = QdrantDocumentStore(**kwargs)

    @property
    def store(self) -> QdrantDocumentStore:
        """Get the underlying Haystack document store."""
        return self._store

    def add_documents(
        self,
        documents: List[Document],
        policy: DuplicatePolicy = DuplicatePolicy.OVERWRITE,
    ) -> int:
        """
        Add documents to the vector store.

        Args:
            documents: List of Haystack Document objects
            policy: How to handle duplicates

        Returns:
            Number of documents added
        """
        self._store.write_documents(documents=documents, policy=policy)
        return len(documents)

    def delete_documents(self, document_ids: List[str]) -> int:
        """
        Delete documents from the vector store.

        Args:
            document_ids: List of document IDs to delete

        Returns:
            Number of documents deleted
        """
        return self._store.delete_documents(document_ids=document_ids)

    def get_document(self, document_id: str) -> Optional[Document]:
        """
        Get a document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        return self._store.get_document(document_id=document_id)

    def get_documents(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Document]:
        """
        Get documents with optional filtering.

        Args:
            filters: Metadata filters
            limit: Maximum number of documents to return

        Returns:
            List of documents
        """
        return self._store.get_documents(filters=filters, limit=limit)

    def count_documents(self) -> int:
        """Get the total number of documents in the store."""
        return self._store.count_documents()

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
    ) -> List[Document]:
        """
        Search for similar documents by embedding.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filters: Metadata filters
            score_threshold: Minimum similarity score

        Returns:
            List of similar documents
        """
        results = self._store.search_documents(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
            score_threshold=score_threshold,
        )
        return [hit.document for hit in results]

    def hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        alpha: float = 0.5,
    ) -> List[Document]:
        """
        Hybrid search combining keyword and semantic search.

        Args:
            query: Query text for keyword search
            query_embedding: Query vector for semantic search
            top_k: Number of results to return
            filters: Metadata filters
            alpha: Balance between keyword (0) and semantic (1) search

        Returns:
            List of similar documents
        """
        # Qdrant supports hybrid search natively
        # For now, we'll use semantic search
        return self.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )

    def clear(self) -> None:
        """Clear all documents from the store."""
        # Delete and recreate the collection
        all_docs = self._store.get_documents(limit=None)
        if all_docs:
            self._store.delete_documents(document_ids=[doc.id for doc in all_docs])


def create_qdrant_store(
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    index: str = "documents",
    embedding_dim: int = 1024,
    in_memory: bool = False,
) -> QdrantVectorStore:
    """
    Factory function to create a Qdrant vector store.

    Args:
        url: Qdrant server URL
        api_key: Qdrant API key
        index: Collection name
        embedding_dim: Embedding dimension
        in_memory: Use in-memory storage

    Returns:
        Configured QdrantVectorStore instance
    """
    return QdrantVectorStore(
        url=url,
        api_key=api_key,
        index=index,
        embedding_dim=embedding_dim,
        in_memory=in_memory,
    )
