from pydantic import BaseModel
from typing import Dict, List, Optional, Union

class CostInfo(BaseModel):
    """Model for LLM API call cost information"""
    total_cost: float
    input_cost: float
    output_cost: float
    input_tokens: int
    output_tokens: int
    model: str

class LLMEvaluation(BaseModel):
    """Model for LLM-based evaluation results"""
    accuracy_score: float
    fluency_score: float
    matches_reference: bool
    comments: str
    cost_info: CostInfo

class TranslationEvaluationResult(BaseModel):
    """Model for individual translation evaluation results"""
    source_text: str
    reference_translation: str
    new_translation: str
    llm_evaluation: LLMEvaluation
    translation_cost_info: CostInfo
    
class BatchEvaluationRequest(BaseModel):
    """Model for batch evaluation request from CSV"""
    file_content: str
    source_language: str = "en"
    target_language: str = "hu"
    
class BatchEvaluationResponse(BaseModel):
    """Model for batch evaluation response"""
    results: List[TranslationEvaluationResult]
    summary: Dict[str, float]  # Average scores for each metric
    total_cost: float  # Total cost of all translations and evaluations
