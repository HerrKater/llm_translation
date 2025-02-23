from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional
from datetime import datetime

class WebPage(BaseModel):
    """Domain model representing a web page"""
    url: str
    raw_html: str
    markdown_content: Optional[str] = None
    crawled_at: datetime = datetime.now()

    model_config = ConfigDict(arbitrary_types_allowed=True)

class TranslationRequest(BaseModel):
    """Domain model representing a translation request"""
    source_content: str
    target_languages: List[str]

    model_config = ConfigDict(arbitrary_types_allowed=True)

class Translation(BaseModel):
    """Domain model representing a translation result"""
    original_content: str
    translations: Dict[str, str]
    translated_at: datetime = datetime.now()

    model_config = ConfigDict(arbitrary_types_allowed=True)
