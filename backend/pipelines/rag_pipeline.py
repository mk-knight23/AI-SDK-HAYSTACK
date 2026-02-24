"""
RAG Pipeline

Implements Retrieval-Augmented Generation for question answering.
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field

from haystack import Document, Pipeline
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret

from embeddings import MistralEmbeddingProvider
from llm import MistralLLMProvider
from vectorstores import QdrantVectorStore


@dataclass
class RAGConfig:
    """Configuration for RAG pipeline."""
    embedding_model: str = 'mistral-embed'
    llm_model: str = 'mistral-small'
    llm_temperature: float = 0.7
    llm_max_tokens: int = 512
    top_k: int = 5
    score_threshold: Optional[float] = None

    # Prompt template
    system_prompt: str = (
        "You are a helpful assistant that answers questions based on "
        "the provided context. Use only the information from the context "
        "to answer questions. If the answer cannot be found in the context, "
        "say so clearly and do not make up information."
    )

    def get_prompt_template(self) -> str:
        """Get the prompt template for RAG."""
        return (
            "{{ system_prompt }}\n\n"
            "Context:\n"
            "{% for doc in documents %}\n"
            "- {{ doc.content }}\n"
            "{% endfor %}\n\n"
            "Question: {{ question }}\n\n"
            "Answer:"
        )


class RAGPipeline:
    """
    Retrieval-Augmented Generation Pipeline.

    Combines vector search with LLM generation for question answering.
    """

    def __init__(
        self,
        vector_store: QdrantVectorStore,
        embedder: MistralEmbeddingProvider,
        llm: MistralLLMProvider,
        config: Optional[RAGConfig] = None,
    ):
        """
        Initialize the RAG pipeline.

        Args:
            vector_store: Vector store for document retrieval
            embedder: Embedding provider for query encoding
            llm: LLM provider for answer generation
            config: RAG configuration
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.llm = llm
        self.config = config or RAGConfig()

        # Build the pipeline
        self._pipeline = self._build_pipeline()

    def _build_pipeline(self) -> Pipeline:
        """Build the Haystack RAG pipeline."""
        pipeline = Pipeline()

        # Note: This is a simplified pipeline structure
        # In production, you'd use Haystack's built-in components
        return pipeline

    def run(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run the RAG pipeline.

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

        # 2. Retrieve relevant documents
        documents = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
            score_threshold=self.config.score_threshold,
        )

        if not documents:
            return {
                'answer': "I couldn't find any relevant information to answer your question.",
                'sources': [],
                'query': query,
            }

        # 3. Build the prompt with retrieved context
        context = '\n\n'.join([doc.content for doc in documents])

        prompt = (
            f"{self.config.system_prompt}\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer:"
        )

        # 4. Generate the answer
        response = self.llm.generate(
            prompt=prompt,
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens,
        )

        # 5. Format the response
        return {
            'answer': response['text'],
            'sources': [
                {
                    'id': doc.id,
                    'content': doc.content,
                    'metadata': doc.meta,
                    'score': getattr(doc, 'score', None),
                }
                for doc in documents
            ],
            'query': query,
            'meta': response.get('meta', {}),
        }

    async def arun(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async version of run method."""
        # For simplicity, just call the sync version
        # In production, implement proper async handling
        return self.run(query, top_k, filters)


def create_rag_pipeline(
    vector_store: QdrantVectorStore,
    embedder: Optional[MistralEmbeddingProvider] = None,
    llm: Optional[MistralLLMProvider] = None,
    config: Optional[RAGConfig] = None,
) -> RAGPipeline:
    """
    Factory function to create a RAG pipeline.

    Args:
        vector_store: Vector store for document retrieval
        embedder: Embedding provider (created if None)
        llm: LLM provider (created if None)
        config: RAG configuration

    Returns:
        Configured RAGPipeline instance
    """
    if embedder is None:
        embedder = MistralEmbeddingProvider()
    if llm is None:
        llm = MistralLLMProvider()

    return RAGPipeline(
        vector_store=vector_store,
        embedder=embedder,
        llm=llm,
        config=config,
    )
