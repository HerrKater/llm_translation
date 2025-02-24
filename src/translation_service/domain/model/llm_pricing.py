from typing import Dict, Tuple

class LLMPricing:
    # Pricing per 1K tokens in USD
    MODEL_PRICES = {
        "gpt-4o-mini": {
            "input": 0.01,   # $0.01 per 1K input tokens
            "output": 0.03   # $0.03 per 1K output tokens
        },
        "gpt-3.5-turbo": {
            "input": 0.0005,  # $0.0005 per 1K input tokens
            "output": 0.0015  # $0.0015 per 1K output tokens
        }
    }

    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int) -> Tuple[float, Dict[str, float]]:
        """
        Calculate the cost of an LLM API call based on input and output tokens.
        
        Args:
            model: The model name (e.g., 'gpt-4-turbo', 'gpt-3.5-turbo')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Tuple containing:
            - total_cost: Total cost in USD
            - breakdown: Dictionary with input_cost and output_cost
        """
        if model not in cls.MODEL_PRICES:
            raise ValueError(f"Unknown model: {model}")
            
        prices = cls.MODEL_PRICES[model]
        
        input_cost = (input_tokens / 1000) * prices["input"]
        output_cost = (output_tokens / 1000) * prices["output"]
        total_cost = input_cost + output_cost
        
        return total_cost, {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }

    @classmethod
    def get_model_prices(cls, model: str) -> Dict[str, float]:
        """Get the pricing information for a specific model."""
        if model not in cls.MODEL_PRICES:
            raise ValueError(f"Unknown model: {model}")
        return cls.MODEL_PRICES[model]
