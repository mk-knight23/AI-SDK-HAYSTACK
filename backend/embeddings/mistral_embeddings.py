"""
Mistral Embeddings Provider

Provides embedding generation using Mistral AI API.
"""

from typing import List, Optional, Dict, Any
import os

from haystack.utils import Secret
from haystack.components.embedders import MistralDocumentEmbedder, MistralTextEmbedder
from haystack.dataclasses import Document


class MistralEmbeddingProvider:
    """
    Provides embedding generation using Mistral AI.

    Supports:
    - Document embedding for indexing
    - Text embedding for queries
    - Batch embedding for efficiency
    """

    MODELS = {
        'mistral-embed': 'mistral-embed',  # Default, 1024 dimensions
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'mistral-embed',
    ):
        """
        Initialize the Mistral embedding provider.

        Args:
            api_key: Mistral API key (defaults to MISTRAL_API_KEY env var)
            model: Model to use for embeddings
        """
        self.api_key = api_key or os.environ.get('MISTRAL_API_KEY')
        self.model = model

        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY must be provided or set as environment variable")

        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Available: {list(self.MODELS.keys())}")

        # Initialize Haystack embedders
        self._document_embedder = None
        self._text_embedder = None

    @property
    def document_embedder(self) -> MistralDocumentEmbedder:
        """Lazy initialization of document embedder."""
        if self._document_embedder is None:
            self._document_embedder = MistralDocumentEmbedder(
                model=self.model,
                api_key=Secret.from_token(self.api_key),
            )
        return self._document_embedder

    @property
    def text_embedder(self) -> MistralTextEmbedder:
        """Lazy initialization of text embedder."""
        if self._text_embedder is None:
            self._text_embedder = MistralTextEmbedder(
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
        return 1024  # Mistral embed model produces 1024-dimensional vectors


def create_mistral_embeddings(
    api_key: Optional[str] = None,
    model: str = 'mistral-embed',
) -> MistralEmbeddingProvider:
    """Factory function to create a Mistral embedding provider."""
    return MistralEmbeddingProvider(api_key=api_key, model=model)
