from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from enum import Enum

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    url: str
    api_key: str
    api_version: str
    language_model: str
    embedding_model: str
    embedding_dimension: int
    embedding_max_input_length: int
    language_model_max_input_length: int
    llm_provider: LLMProvider = LLMProvider.OPENAI

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OPENAI_"
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
