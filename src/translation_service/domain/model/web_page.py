from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class WebPage(BaseModel):
    """Domain model representing a web page"""
    url: str
    raw_html: str
    markdown_content: Optional[str] = None
    crawled_at: datetime = datetime.now()

    model_config = ConfigDict(arbitrary_types_allowed=True)
