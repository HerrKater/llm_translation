from pydantic import BaseModel
from typing import Dict, List, Optional, Union

class LLMEvaluation(BaseModel):
    """Model for LLM-based evaluation results"""
    accuracy_score: float
    fluency_score: float
    matches_reference: bool
    comments: str

class TranslationEvaluationResult(BaseModel):
    """Model for individual translation evaluation results"""
    source_text: str
    reference_translation: str
    new_translation: str
    llm_evaluation: LLMEvaluation
    
class BatchEvaluationRequest(BaseModel):
    """Model for batch evaluation request from CSV"""
    file_content: str
    source_language: str = "en"
    target_language: str = "hu"
    
class BatchEvaluationResponse(BaseModel):
    """Model for batch evaluation response"""
    results: List[TranslationEvaluationResult]
    summary: Dict[str, float]  # Average scores for each metric
