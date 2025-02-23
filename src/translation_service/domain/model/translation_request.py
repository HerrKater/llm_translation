from pydantic import BaseModel, ConfigDict
from typing import List

class TranslationRequest(BaseModel):
    """Domain model representing a translation request"""
    source_content: str
    target_languages: List[str]

    model_config = ConfigDict(arbitrary_types_allowed=True)
