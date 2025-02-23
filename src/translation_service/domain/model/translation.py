from pydantic import BaseModel, ConfigDict
from typing import Dict
from datetime import datetime

class Translation(BaseModel):
    """Domain model representing a translation result"""
    original_content: str
    translations: Dict[str, str]
    translated_at: datetime = datetime.now()

    model_config = ConfigDict(arbitrary_types_allowed=True)
