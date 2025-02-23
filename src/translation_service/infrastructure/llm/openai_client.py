from typing import Dict, List, Optional
import openai

from ..config import Settings
from .interfaces import LLMClient

class OpenAILLMClient(LLMClient):
    """OpenAI implementation of the LLM client."""
    
    def __init__(self, settings: Settings):
        """Initialize the OpenAI client with settings."""
        self.client = openai.OpenAI(
            api_key=settings.api_key,
            base_url=settings.url
        )
        self.model_name = settings.language_model
        
    def complete(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Generate a completion using OpenAI's completion API."""
        response = self.client.completions.create(
            model=model or self.model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
        return response.choices[0].text.strip()

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Generate a chat completion using OpenAI's chat API."""
        response = self.client.chat.completions.create(
            model=model or self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
        return response.choices[0].message.content.strip()
