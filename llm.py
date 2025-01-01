"""
LLM Client Module

This module provides a client for interacting with various Language Learning Models (LLMs).
Currently supports Groq's LLM API, with extensibility for additional LLM providers.
"""

from typing import Optional
from pydantic import BaseModel, Field, SecretStr
from groq import Groq
import os
from dotenv import load_dotenv


class LLMConfig(BaseModel):
    """
    Pydantic model for LLM configuration settings.
    
    Attributes:
        api_key (SecretStr): API key for the LLM service
        model_name (str): Name of the model to use
        temperature (float): Sampling temperature for text generation
        max_tokens (int): Maximum number of tokens to generate
    """
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


class LLMClient:
    """
    A client for interacting with Language Learning Models.
    
    This class provides a unified interface for different LLM providers,
    currently supporting Groq with potential for extension to other providers.
    """
    
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
            api_key=SecretStr(os.environ.get("GROQ_API_KEY", "")),
        )
        
        # Initialize Groq client
        self._init_groq_client()
    
    def _init_groq_client(self) -> None:
        """
        Initialize the Groq client with the configured API key.
        
        Raises:
            ValueError: If no API key is provided or found in environment variables.
        """
        if not self.config.api_key.get_secret_value():
            raise ValueError("No Groq API key provided")
        
        self.groq_client = Groq(
            api_key=self.config.api_key.get_secret_value(),
        )


# Initialize default client
default_config = LLMConfig(
    api_key=SecretStr(os.environ.get("GROQ_API_KEY", "")),
    model_name="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=2048
)

try:
    llm_client = LLMClient(default_config)
    groq_client = llm_client.groq_client
except ValueError as e:
    print(f"Warning: Failed to initialize LLM client: {e}")
    groq_client = None


# Export the client for use in other modules
__all__ = ['groq_client', 'LLMClient', 'LLMConfig']