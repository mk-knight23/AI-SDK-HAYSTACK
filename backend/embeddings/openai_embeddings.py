"""
OpenAI Embeddings Provider

Provides embedding generation using OpenAI API as fallback/alternative.
"""

from typing import List, Optional
import os

from haystack.utils import Secret
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.dataclasses import Document


class OpenAIEmbeddingProvider:
    """
    Provides embedding generation using OpenAI.

    Supports:
    - Document embedding for indexing
    - Text embedding for queries
    - Batch embedding for efficiency
    """

    MODELS = {
        'text-embedding-3-small': 'text-embedding-3-small',  # 1536 dimensions
        'text-embedding-3-large': 'text-embedding-3-large',  # 3072 dimensions
        'text-embedding-ada-002': 'text-embedding-ada-002',  # 1536 dimensions
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'text-embedding-3-small',
    ):
        """
        Initialize the OpenAI embedding provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use for embeddings
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be provided or set as environment variable")

        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Available: {list(self.MODELS.keys())}")

        # Initialize Haystack embedders
        self._document_embedder = None
        self._text_embedder = None

    @property
    def document_embedder(self) -> OpenAIDocumentEmbedder:
        """Lazy initialization of document embedder."""
        if self._document_embedder is None:
            self._document_embedder = OpenAIDocumentEmbedder(
                model=self.model,
                api_key=Secret.from_token(self.api_key),
            )
        return self._document_embedder

    @property
    def text_embedder(self) -> OpenAITextEmbedder:
        """Lazy initialization of text embedder."""
        if self._text_embedder is None:
            self._text_embedder = OpenAITextEmbedder(
                model=self.model,
                api_key=Secret.from_token(self.api_key),
            )
        return self._text_embedder

    def embed_documents(self, documents: List[Document]) -> List[Document]:
        """
        Generate embeddings for a list of documents.

        Args:
            documents: List of Haystack Document objects

        Returns:
            Documents with embedding field populated
        """
        result = self.document_embedder.run(documents=documents)
        return result.get('documents', documents)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text strings.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        result = self.text_embedder.run(texts=texts)
        return result.get('embedding', [])

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: Text string

        Returns:
            Embedding vector
        """
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        dimensions = {
            'text-embedding-3-small': 1536,
            'text-embedding-3-large': 3072,
            'text-embedding-ada-002': 1536,
        }
        return dimensions.get(self.model, 1536)


def create_openai_embeddings(
    api_key: Optional[str] = None,
    model: str = 'text-embedding-3-small',
) -> OpenAIEmbeddingProvider:
    """Factory function to create an OpenAI embedding provider."""
    return OpenAIEmbeddingProvider(api_key=api_key, model=model)
