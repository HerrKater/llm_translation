from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class LLMClient(ABC):
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
    ) -> str:
        """Generate a chat completion for the given messages."""
        pass
