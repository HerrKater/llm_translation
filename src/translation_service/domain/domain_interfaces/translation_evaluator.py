from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class TranslationEvaluationResult:
    """Result of a translation evaluation"""
    accuracy_score: float
    fluency_score: float
    matches_reference: bool
    comments: str

class TranslationEvaluatorService(ABC):
    """Interface for evaluating translation quality"""
    
    @abstractmethod
    async def evaluate_translation(
        self, 
        english_text: str, 
        reference_translation: str, 
        new_translation: str
    ) -> TranslationEvaluationResult:
        """Evaluate the quality of a translation compared to a reference translation.
        
        Args:
            english_text: The original English text
            reference_translation: The reference translation to compare against
            new_translation: The new translation to evaluate
            
        Returns:
            TranslationEvaluationResult containing scores and comments
        """
        pass
