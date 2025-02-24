from pydantic import BaseModel, ConfigDict
from typing import Dict, List
from domain.model.language_models import ModelName

class ModelConfigDTO(BaseModel):
    """Data Transfer Object for language model configuration"""
    id: str
    name: str
    description: str
    inputCost: float
    outputCost: float
    maxTokens: int

    model_config = ConfigDict(arbitrary_types_allowed=True)

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

class CostInfoDTO(BaseModel):
    """Data Transfer Object for cost information"""
    total_cost: float
    input_cost: float
    output_cost: float
    input_tokens: int
    output_tokens: int
    model: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

class TranslationResponseDTO(BaseModel):
    """Data Transfer Object for translation responses"""
    original_text: str
    translations: Dict[str, str]
    cost_info: CostInfoDTO

    model_config = ConfigDict(arbitrary_types_allowed=True)
