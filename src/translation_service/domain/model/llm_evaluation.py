from pydantic import BaseModel
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Union

class CostInfo(BaseModel):
    """Model for LLM API call cost information"""
    total_cost: float
    input_cost: float
    output_cost: float
    input_tokens: int
    output_tokens: int
    model: str

class EvaluationMetric(BaseModel):
    """Model for individual evaluation metric"""
    score: float  # Normalized score (0-10)
    raw_score: int  # Original score (1-5)
    explanation: str

class LLMEvaluation(BaseModel):
    """Model for LLM-based evaluation results"""
    accuracy: EvaluationMetric
    fluency: EvaluationMetric
    adequacy: EvaluationMetric
    consistency: EvaluationMetric
    contextual_appropriateness: EvaluationMetric
    terminology_accuracy: EvaluationMetric
    readability: EvaluationMetric
    format_preservation: EvaluationMetric
    error_rate: EvaluationMetric
    matches_reference: bool
    comments: str
    cost_info: CostInfo

class BatchEvaluationRequest(BaseModel):
    """Model for batch evaluation request from CSV"""
    file_content: str
    source_language: str = "en"
    target_language: str = "hu"
    
class EvaluationResult(BaseModel):
    """Model for individual evaluation result containing both reference and new translation evaluations"""
    source_text: str
    reference_translation: str
    new_translation: str
    reference_evaluation: LLMEvaluation
    new_evaluation: LLMEvaluation
    matches_reference: bool
    cost_info: CostInfo

class BatchEvaluationResponse(BaseModel):
    """Model for batch evaluation response"""
    results: List[EvaluationResult]
    summary: Dict[str, float]  # Average scores for each metric
    total_cost: float  # Total cost of all translations and evaluations