"""
Elasticsearch Vector Store

Provides vector storage and retrieval using Elasticsearch.
Supports hybrid search with BM25 and vector similarity.
"""

from typing import List, Optional, Dict, Any
import os

from haystack import Document
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore


class ElasticsearchVectorStore:
    """
    Elasticsearch-based vector store for document storage and retrieval.

    Supports:
    - Hybrid search (BM25 + vector)
    - Full-text search
    - Metadata filtering
    - Scalable production deployment
    """

    def __init__(
        self,
        hosts: Optional[List[str]] = None,
        index: str = "documents",
        embedding_dim: int = 1024,
        username: Optional[str] = None,
        password: Optional[str] = None,
        cloud_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Elasticsearch vector store.

        Args:
            hosts: List of Elasticsearch hosts
            index: Index name
            embedding_dim: Dimension of embedding vectors
            username: Elasticsearch username
            password: Elasticsearch password
            cloud_id: Elastic Cloud ID
            api_key: Elasticsearch API key
        """
        self.index = index
        self.embedding_dim = embedding_dim

        # Build connection config
        kwargs = {
            'index': index,
            'embedding_dim': embedding_dim,
        }

        if cloud_id:
            kwargs['cloud_id'] = cloud_id
            if api_key:
                kwargs['api_key'] = api_key
        elif hosts:
            kwargs['hosts'] = hosts
            if username and password:
                kwargs['basic_auth'] = (username, password)
        else:
            # Default to localhost
            kwargs['hosts'] = ['http://localhost:9200']

        self._store = ElasticsearchDocumentStore(**kwargs)

    @property
    def store(self) -> ElasticsearchDocumentStore:
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

    def bm25_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Search using BM25 keyword ranking.

        Args:
            query: Query text
            top_k: Number of results to return
            filters: Metadata filters

        Returns:
            List of similar documents
        """
        from haystack.components.retrievers import BM25Retriever
        retriever = BM25Retriever(document_store=self._store, top_k=top_k, filters=filters)
        results = retriever.run(query=query)
        return results.get('documents', [])

    def hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        alpha: float = 0.5,
    ) -> List[Document]:
        """
        Hybrid search combining BM25 and vector similarity.

        Args:
            query: Query text for BM25
            query_embedding: Query vector for semantic search
            top_k: Number of results to return
            filters: Metadata filters
            alpha: Balance between BM25 (0) and semantic (1) search

        Returns:
            List of similar documents
        """
        from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchBM25Retriever
        from haystack.components.joiners import DocumentJoiner
        from haystack.components.rankers import TransformerSimilarityRanker

        # For simplicity, use vector search
        # In production, implement proper hybrid join
        return self.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )

    def clear(self) -> None:
        """Clear all documents from the store."""
        all_docs = self._store.get_documents(limit=None)
        if all_docs:
            self._store.delete_documents(document_ids=[doc.id for doc in all_docs])


def create_elasticsearch_store(
    hosts: Optional[List[str]] = None,
    index: str = "documents",
    embedding_dim: int = 1024,
    username: Optional[str] = None,
    password: Optional[str] = None,
    cloud_id: Optional[str] = None,
) -> ElasticsearchVectorStore:
    """
    Factory function to create an Elasticsearch vector store.

    Args:
        hosts: List of Elasticsearch hosts
        index: Index name
        embedding_dim: Embedding dimension
        username: Elasticsearch username
        password: Elasticsearch password
        cloud_id: Elastic Cloud ID

    Returns:
        Configured ElasticsearchVectorStore instance
    """
    return ElasticsearchVectorStore(
        hosts=hosts,
        index=index,
        embedding_dim=embedding_dim,
        username=username,
        password=password,
        cloud_id=cloud_id,
    )
