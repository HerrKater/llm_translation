from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Dict, List

class TranslationRequestDTO(BaseModel):
    """Data Transfer Object for translation requests"""
    url: HttpUrl
    target_languages: List[str]

    model_config = ConfigDict(arbitrary_types_allowed=True)

class TranslationResponseDTO(BaseModel):
    """Data Transfer Object for translation responses"""
    original_text: str
    translations: Dict[str, str]

    model_config = ConfigDict(arbitrary_types_allowed=True)
