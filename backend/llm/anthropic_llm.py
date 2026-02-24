"""
Anthropic LLM Provider

Provides LLM generation using Anthropic Claude API.
"""

from typing import List, Optional, Dict, Any
import os

from haystack.utils import Secret
from haystack.components.generators import AnthropicGenerator
from haystack.dataclasses import ChatMessage, ChatRole


class AnthropicLLMProvider:
    """
    Provides text generation using Anthropic Claude.

    Supports:
    - Text generation
    - Chat completion
    - Claude 3.5 Sonnet, Claude 3 Opus, etc.
    """

    MODELS = {
        'claude-sonnet-4': 'claude-sonnet-4-20250514',
        'claude-sonnet-3.5': 'claude-3-5-sonnet-20241022',
        'claude-opus-3': 'claude-3-opus-20240229',
        'claude-haiku-3.5': 'claude-3-5-haiku-20241022',
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'claude-sonnet-3.5',
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 0.9,
    ):
        """
        Initialize the Anthropic LLM provider.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use for generation
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.model = self.MODELS.get(model, model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set as environment variable")

        self._generator = None

    @property
    def generator(self) -> AnthropicGenerator:
        """Lazy initialization of the generator."""
        if self._generator is None:
            self._generator = AnthropicGenerator(
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


def create_anthropic_llm(
    api_key: Optional[str] = None,
    model: str = 'claude-sonnet-3.5',
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> AnthropicLLMProvider:
    """Factory function to create an Anthropic LLM provider."""
    return AnthropicLLMProvider(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
