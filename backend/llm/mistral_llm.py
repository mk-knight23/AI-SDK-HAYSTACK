"""
Mistral LLM Provider

Provides LLM generation using Mistral AI API.
"""

from typing import List, Optional, Dict, Any, Generator
import os

from haystack.utils import Secret
from haystack.components.generators import MistralGenerator
from haystack.dataclasses import ChatMessage, ChatRole


class MistralLLMProvider:
    """
    Provides text generation using Mistral AI.

    Supports:
    - Text generation
    - Chat completion
    - Streaming responses
    - Multiple models
    """

    MODELS = {
        'mistral-small': 'mistral-small-latest',
        'mistral-medium': 'mistral-medium-latest',
        'mistral-large': 'mistral-large-latest',
        'codestral': 'codestral-latest',
        'mistral-7b': 'open-mistral-7b',
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'mistral-small',
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 0.9,
    ):
        """
        Initialize the Mistral LLM provider.

        Args:
            api_key: Mistral API key (defaults to MISTRAL_API_KEY env var)
            model: Model to use for generation
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
        """
        self.api_key = api_key or os.environ.get('MISTRAL_API_KEY')
        self.model = self.MODELS.get(model, model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p

        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY must be provided or set as environment variable")

        self._generator = None

    @property
    def generator(self) -> MistralGenerator:
        """Lazy initialization of the generator."""
        if self._generator is None:
            self._generator = MistralGenerator(
                model=self.model,
                api_key=Secret.from_token(self.api_key),
                generation_kwargs={
                    'temperature': self.temperature,
                    'max_tokens': self.max_tokens,
                    'top_p': self.top_p,
                },
            )
        return self._generator

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate text from a prompt.

        Args:
            prompt: Input prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Dictionary with generated text and metadata
        """
        generation_kwargs = {}
        if temperature is not None:
            generation_kwargs['temperature'] = temperature
        if max_tokens is not None:
            generation_kwargs['max_tokens'] = max_tokens

        result = self.generator.run(prompt=prompt, generation_kwargs=generation_kwargs)

        return {
            'text': result.get('replies', [''])[0],
            'meta': result.get('meta', {}),
        }

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a chat response.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Dictionary with response and metadata
        """
        # Convert messages to Haystack ChatMessage format
        chat_messages = []
        for msg in messages:
            role = ChatRole[msg['role'].upper()] if msg['role'].upper() in ChatRole.__members__ else ChatRole.USER
            chat_messages.append(ChatMessage(content=msg['content'], role=role))

        generation_kwargs = {}
        if temperature is not None:
            generation_kwargs['temperature'] = temperature
        if max_tokens is not None:
            generation_kwargs['max_tokens'] = max_tokens

        result = self.generator.run(messages=chat_messages, generation_kwargs=generation_kwargs)

        return {
            'text': result.get('replies', [''])[0],
            'meta': result.get('meta', {}),
        }

    def stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Generator[str, None, None]:
        """
        Stream generated text.

        Args:
            prompt: Input prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Yields:
            Generated text chunks
        """
        # For streaming, we'd need to use a streaming generator
        # This is a simplified version
        result = self.generate(prompt, temperature, max_tokens)
        yield result['text']


def create_mistral_llm(
    api_key: Optional[str] = None,
    model: str = 'mistral-small',
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> MistralLLMProvider:
    """Factory function to create a Mistral LLM provider."""
    return MistralLLMProvider(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
