from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class WebPage:
    """Domain model representing a web page"""
    url: str
    raw_html: str
    markdown_content: Optional[str] = None
    crawled_at: datetime = datetime.now()

@dataclass
class TranslationRequest:
    """Domain model representing a translation request"""
    source_content: str
    target_languages: List[str]

@dataclass
class Translation:
    """Domain model representing a translation result"""
    original_content: str
    translations: Dict[str, str]
    translated_at: datetime = datetime.now()
