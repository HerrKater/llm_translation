from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from enum import Enum
import os

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    url: str
    api_key: str
    provider: LLMProvider = LLMProvider.OPENAI
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        env_file_encoding='utf-8',
        env_prefix="OPENAI_",
        case_sensitive=False
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    try:
        return Settings()
    except Exception as e:
        print(f"Error loading settings: {e}")
        print(f"Looking for .env at: {os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')}")
        raise
