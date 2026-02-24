"""
Embeddings Module

Provides embedding generation using various providers:
- Mistral (default)
- OpenAI
- Anthropic
"""

from .mistral_embeddings import MistralEmbeddingProvider
from .openai_embeddings import OpenAIEmbeddingProvider

__all__ = [
    'MistralEmbeddingProvider',
    'OpenAIEmbeddingProvider',
]
