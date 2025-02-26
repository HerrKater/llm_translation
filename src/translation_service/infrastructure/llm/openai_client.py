from typing import Dict, List, Optional
from openai import AsyncOpenAI

from domain.model.settings import Settings
from domain.infrastructure_interfaces.llm_repository import LlmRepository


class OpenAILLMClient(LlmRepository):
    """OpenAI implementation of the LLM client."""
    
    def __init__(self, settings: Settings):
        """Initialize the OpenAI client with settings."""
        self.client = AsyncOpenAI(
            api_key=settings.api_key,
            base_url=settings.url
        )
      
        
    async def complete(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """Generate a completion using OpenAI's completion API.
        
        Returns:
            Dictionary containing:
            - content: The generated text response
            - usage: Token usage information including prompt_tokens and completion_tokens
        """
        response = await self.client.completions.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
        return {
            'content': response.choices[0].text.strip(),
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """Generate a chat completion using OpenAI's chat API.
        
        Returns:
            Dictionary containing:
            - content: The generated text response
            - usage: Token usage information including prompt_tokens and completion_tokens
        """
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
        return {
            'content': response.choices[0].message.content.strip(),
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
        }
