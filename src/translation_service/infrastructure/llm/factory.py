from enum import Enum
from domain.model.settings import Settings, LLMProvider, get_settings
from domain.infrastructure_interfaces.llm_repository import LlmRepository
from infrastructure.llm.openai_client import OpenAILLMClient


def create_llm_client(provider: LLMProvider, settings: Settings = None) -> LlmRepository:
    """Create an LLM client instance based on the provider."""
    if provider == LLMProvider.OPENAI:
        settings = settings or get_settings()
        return OpenAILLMClient(settings)
    
    raise ValueError(f"Unsupported LLM provider: {provider}")
