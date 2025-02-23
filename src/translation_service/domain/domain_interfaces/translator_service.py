from abc import ABC, abstractmethod
from domain.model.translation_request import TranslationRequest
from domain.model.translation import Translation

class TranslatorService(ABC):
    """Interface for translation service"""
    @abstractmethod
    async def translate(self, request: TranslationRequest) -> Translation:
        """Translate content into multiple languages"""
        pass
