from abc import ABC, abstractmethod
from domain.model.translation_request import TranslationRequest
from domain.model.translation import Translation

class TranslatorService(ABC):
    """Interface for translation service"""
    @abstractmethod
    async def translate(self, request: TranslationRequest) -> tuple[Translation, dict]:
        """Translate content into multiple languages
        
        Returns:
            tuple containing:
            - Translation object with original and translated content
            - Cost information dictionary with token counts and pricing
        """
        pass
