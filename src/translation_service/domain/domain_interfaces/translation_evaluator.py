from abc import ABC, abstractmethod
from dataclasses import dataclass
from domain.model.llm_evaluation import LLMEvaluation, CostInfo, EvaluationMetric, BatchEvaluationResponse

class TranslationEvaluatorService(ABC):
    """Interface for evaluating translation quality"""
    
    @abstractmethod
    async def evaluate_translation(
        self, 
        english_text: str, 
        reference_translation: str, 
        new_translation: str,
        target_language: str
    ) -> LLMEvaluation:
        """Evaluate the quality of a translation compared to a reference translation.
        
        Args:
            english_text: The original English text
            reference_translation: The reference translation to compare against
            new_translation: The new translation to evaluate
            target_language: The target language code (e.g. 'hu' for Hungarian)
            
        Returns:
            TranslationEvaluationResult containing scores and comments
        """
        pass
