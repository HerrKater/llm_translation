from enum import Enum

from ..config import Settings, get_settings
from .interfaces import LLMClient
from .openai_client import OpenAILLMClient

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"

def create_llm_client(provider: LLMProvider, settings: Settings = None) -> LLMClient:
    """Create an LLM client instance based on the provider."""
    if provider == LLMProvider.OPENAI:
        settings = settings or get_settings()
        return OpenAILLMClient(settings)
    
    raise ValueError(f"Unsupported LLM provider: {provider}")
