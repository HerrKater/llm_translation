from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class LlmRepository(ABC):
    """Base interface for LLM interactions."""
    
    @abstractmethod
    def complete(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Generate a completion for the given prompt."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """Generate a chat completion for the given messages.
        
        Returns:
            Dictionary containing:
            - content: The generated text response
            - usage: Token usage information including prompt_tokens and completion_tokens
        """
        pass
