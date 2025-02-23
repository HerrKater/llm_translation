from pydantic import BaseModel, ConfigDict
from typing import Dict, List

class TranslationRequestDTO(BaseModel):
    """Data Transfer Object for translation requests"""
    url: str
    target_languages: List[str]

    model_config = ConfigDict(arbitrary_types_allowed=True)

class RawTextTranslationRequestDTO(BaseModel):
    """Data Transfer Object for raw text translation requests"""
    text: str
    target_languages: List[str]

    model_config = ConfigDict(arbitrary_types_allowed=True)

class TranslationResponseDTO(BaseModel):
    """Data Transfer Object for translation responses"""
    original_text: str
    translations: Dict[str, str]

    model_config = ConfigDict(arbitrary_types_allowed=True)
