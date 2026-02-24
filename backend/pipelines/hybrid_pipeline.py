"""
Hybrid Pipeline

Combines multiple retrieval strategies for optimal results:
- Vector search (semantic)
- BM25 (keyword)
- Hybrid fusion
"""

from typing import List, Optional, Dict, Any

from haystack import Document, Pipeline
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformerSimilarityRanker

from embeddings import MistralEmbeddingProvider
from llm import MistralLLMProvider
from vectorstores import QdrantVectorStore, ElasticsearchVectorStore
from .rag_pipeline import RAGPipeline, RAGConfig


class HybridPipeline(RAGPipeline):
    """
    Hybrid retrieval pipeline combining semantic and keyword search.

    Provides better results by fusing multiple retrieval strategies.
    """

    def __init__(
        self,
        vector_store: QdrantVectorStore,
        keyword_store: Optional[ElasticsearchVectorStore] = None,
        embedder: Optional[MistralEmbeddingProvider] = None,
        llm: Optional[MistralLLMProvider] = None,
        config: Optional[RAGConfig] = None,
        alpha: float = 0.5,
    ):
        """
        Initialize the hybrid pipeline.

        Args:
            vector_store: Vector store for semantic search
            keyword_store: Optional keyword/BM25 store
            embedder: Embedding provider
            llm: LLM provider
            config: RAG configuration
            alpha: Balance between semantic (1) and keyword (0) search
        """
        super().__init__(vector_store, embedder, llm, config)
        self.keyword_store = keyword_store
        self.alpha = alpha

    def run(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run the hybrid RAG pipeline.

        Args:
            query: User question
            top_k: Number of documents to retrieve
            filters: Metadata filters for retrieval

        Returns:
            Dictionary with answer, sources, and metadata
        """
        top_k = top_k or self.config.top_k

        # 1. Embed the query
        query_embedding = self.embedder.embed_text(query)

        # 2. Retrieve from both stores
        semantic_docs = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k * 2,
            filters=filters,
            score_threshold=self.config.score_threshold,
        )

        keyword_docs = []
        if self.keyword_store:
            keyword_docs = self.keyword_store.bm25_search(
                query=query,
                top_k=top_k * 2,
                filters=filters,
            )

        # 3. Combine and rank results
        combined_docs = self._fuse_results(
            semantic_docs=semantic_docs,
            keyword_docs=keyword_docs,
            alpha=self.alpha,
            top_k=top_k,
        )

        if not combined_docs:
            return {
                'answer': "I couldn't find any relevant information to answer your question.",
                'sources': [],
                'query': query,
                'retrieval_method': 'hybrid',
            }

        # 4. Build the prompt with retrieved context
        context = '\n\n'.join([doc.content for doc in combined_docs])

        prompt = (
            f"{self.config.system_prompt}\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer:"
        )

        # 5. Generate the answer
        response = self.llm.generate(
            prompt=prompt,
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens,
        )

        # 6. Format the response
        return {
            'answer': response['text'],
            'sources': [
                {
                    'id': doc.id,
                    'content': doc.content,
                    'metadata': doc.meta,
                    'score': getattr(doc, 'score', None),
                }
                for doc in combined_docs
            ],
            'query': query,
            'retrieval_method': 'hybrid',
            'meta': response.get('meta', {}),
        }

    def _fuse_results(
        self,
        semantic_docs: List[Document],
        keyword_docs: List[Document],
        alpha: float,
        top_k: int,
    ) -> List[Document]:
        """
        Fuse results from semantic and keyword search.

        Uses reciprocal rank fusion (RRF) for combining results.
        """
        if not keyword_docs:
            return semantic_docs[:top_k]

        if not semantic_docs:
            return keyword_docs[:top_k]

        # Simple RRF implementation
        doc_scores = {}

        # Score semantic docs (rank-based)
        for rank, doc in enumerate(semantic_docs):
            doc_id = doc.id
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {'doc': doc, 'semantic_score': 0, 'keyword_score': 0}
            doc_scores[doc_id]['semantic_score'] = 1 / (rank + 1)

        # Score keyword docs (rank-based)
        for rank, doc in enumerate(keyword_docs):
            doc_id = doc.id
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {'doc': doc, 'semantic_score': 0, 'keyword_score': 0}
            doc_scores[doc_id]['keyword_score'] = 1 / (rank + 1)

        # Combine scores
        for doc_id in doc_scores:
            scores = doc_scores[doc_id]
            combined = (
                alpha * scores['semantic_score'] +
                (1 - alpha) * scores['keyword_score']
            )
            scores['combined'] = combined

        # Sort by combined score and return top_k
        sorted_docs = sorted(
            doc_scores.values(),
            key=lambda x: x['combined'],
            reverse=True,
        )

        return [item['doc'] for item in sorted_docs[:top_k]]


def create_hybrid_pipeline(
    vector_store: QdrantVectorStore,
    keyword_store: Optional[ElasticsearchVectorStore] = None,
    embedder: Optional[MistralEmbeddingProvider] = None,
    llm: Optional[MistralLLMProvider] = None,
    config: Optional[RAGConfig] = None,
    alpha: float = 0.5,
) -> HybridPipeline:
    """
    Factory function to create a hybrid RAG pipeline.

    Args:
        vector_store: Vector store for semantic search
        keyword_store: Optional keyword store for BM25
        embedder: Embedding provider (created if None)
        llm: LLM provider (created if None)
        config: RAG configuration
        alpha: Balance between semantic and keyword search

    Returns:
        Configured HybridPipeline instance
    """
    return HybridPipeline(
        vector_store=vector_store,
        keyword_store=keyword_store,
        embedder=embedder,
        llm=llm,
        config=config,
        alpha=alpha,
    )
