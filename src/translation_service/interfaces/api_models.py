from pydantic import BaseModel, HttpUrl
from typing import Dict, List

class TranslationRequestDTO(BaseModel):
    """Data Transfer Object for translation requests"""
    url: HttpUrl
    target_languages: List[str]

class TranslationResponseDTO(BaseModel):
    """Data Transfer Object for translation responses"""
    original_text: str
    translations: Dict[str, str]
