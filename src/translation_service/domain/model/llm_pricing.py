from typing import Dict, Tuple
from domain.model.language_models import LanguageModels

class LLMPricing:
    """Calculate costs for LLM API usage"""
    
    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int) -> Tuple[float, Dict]:
        """Calculate cost for API usage"""
        return LanguageModels.calculate_cost(model, input_tokens, output_tokens)

    @classmethod
    def get_model_prices(cls, model: str) -> Dict[str, float]:
        """Get the pricing information for a specific model."""
        config = LanguageModels.get_model_config(model)
        return {
            "input": config.input_cost_per_1k,
            "output": config.output_cost_per_1k
        }
        return cls.MODEL_PRICES[model]
