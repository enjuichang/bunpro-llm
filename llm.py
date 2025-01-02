"""
LLM Client Module

This module provides a client for interacting with various Language Learning Models (LLMs).
Currently supports Groq's LLM API, with extensibility for additional LLM providers.
"""

from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, SecretStr
from groq import Groq
import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod


class LLMConfig(BaseModel):
    """
    Pydantic model for LLM configuration settings.

    Attributes:
        provider (str): LLM provider name (e.g., "groq", "openai", "anthropic")
        api_key (SecretStr): API key for the LLM service
        model_name (str): Name of the model to use
        temperature (float): Sampling temperature for text generation
        max_tokens (int): Maximum number of tokens to generate
    """
    provider: Literal["groq", "openai", "anthropic"] = Field(
        default="groq",
        description="LLM provider to use"
    )
    api_key: SecretStr = Field(..., description="API key for the LLM service")
    model_name: str = Field(
        default="llama-3.3-70b-versatile",
        description="Model identifier to use for completions"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for text generation"
    )
    max_tokens: int = Field(
        default=2048,
        gt=0,
        description="Maximum number of tokens to generate"
    )


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def initialize_client(self, config: LLMConfig) -> Any:
        """Initialize the provider's client"""
        pass

    @abstractmethod
    def create_chat_completion(self, messages: list, stream: bool = True) -> Any:
        """Create a chat completion"""
        pass


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider implementation"""

    def initialize_client(self, config: LLMConfig) -> Groq:
        """Initialize Groq client"""
        if not config.api_key.get_secret_value():
            raise ValueError("No Groq API key provided")
        return Groq(api_key=config.api_key.get_secret_value())

    def create_chat_completion(self, messages: list, stream: bool = True) -> Any:
        """Create a chat completion using Groq"""
        return self.client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=stream
        )


# Add more providers here as needed
class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation (placeholder)"""
    def initialize_client(self, config: LLMConfig) -> Any:
        raise NotImplementedError("OpenAI provider not yet implemented")

    def create_chat_completion(self, messages: list, stream: bool = True) -> Any:
        raise NotImplementedError("OpenAI provider not yet implemented")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider implementation (placeholder)"""
    def initialize_client(self, config: LLMConfig) -> Any:
        raise NotImplementedError("Anthropic provider not yet implemented")

    def create_chat_completion(self, messages: list, stream: bool = True) -> Any:
        raise NotImplementedError("Anthropic provider not yet implemented")


class LLMClient:
    """
    A client for interacting with Language Learning Models.

    This class provides a unified interface for different LLM providers.
    """

    # Provider mapping
    PROVIDERS: Dict[str, type[BaseLLMProvider]] = {
        "groq": GroqProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider
    }

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the LLM client with configuration.

        Args:
            config (Optional[LLMConfig]): Configuration for the LLM client.
                If None, will attempt to load from environment variables.
        """
        # Load environment variables if not already loaded
        load_dotenv()

        # Initialize configuration
        self.config = config or LLMConfig(
            provider="groq",
            api_key=SecretStr(os.environ.get("GROQ_API_KEY", "")),
        )

        # Initialize provider
        self._init_provider()

    def _init_provider(self) -> None:
        """
        Initialize the selected LLM provider.

        Raises:
            ValueError: If provider is not supported or initialization fails.
        """
        provider_class = self.PROVIDERS.get(self.config.provider)
        if not provider_class:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        self.provider = provider_class()
        self.provider.config = self.config
        self.provider.client = self.provider.initialize_client(self.config)

    def create_chat_completion(self, messages: list, stream: bool = True) -> Any:
        """
        Create a chat completion using the configured provider.

        Args:
            messages (list): List of message dictionaries
            stream (bool): Whether to stream the response

        Returns:
            Response from the LLM provider
        """
        return self.provider.create_chat_completion(messages, stream)


# Initialize default client
default_config = LLMConfig(
    provider="groq",
    api_key=SecretStr(os.environ.get("GROQ_API_KEY", "")),
    model_name="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=2048
)

try:
    llm_client = LLMClient(default_config)
    groq_client = llm_client.provider.client
except ValueError as e:
    print(f"Warning: Failed to initialize LLM client: {e}")
    groq_client = None


# Export the client for use in other modules
__all__ = ['groq_client', 'LLMClient', 'LLMConfig', 'BaseLLMProvider']