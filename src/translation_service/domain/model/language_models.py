from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Union

class ModelName(str, Enum):
    """Supported language models"""
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_O1_MINI = "o1-mini"

@dataclass
class ModelConfig:
    """Configuration for a language model"""
    name: ModelName
    display_name: str
    input_cost_per_1k: float
    output_cost_per_1k: float
    max_tokens: int
    description: str = ""

class LanguageModels:
    """Central configuration for language models"""
    
    MODELS: Dict[ModelName, ModelConfig] = {
        ModelName.GPT_4O_MINI: ModelConfig(
            name=ModelName.GPT_4O_MINI,
            display_name="GPT-4o-mini",
            input_cost_per_1k=0.00015,
            output_cost_per_1k=0.0006,
            max_tokens=128000,
            description="GPT-4o mini (“o” for “omni”) is a fast, affordable small model for focused tasks. It accepts both text and image inputs, and produces text outputs (including Structured Outputs). It is ideal for fine-tuning, and model outputs from a larger model like GPT-4o can be distilled to GPT-4o-mini to produce similar results at lower cost and latency."
        ),
        ModelName.GPT_4O: ModelConfig(
            name=ModelName.GPT_4O,
            display_name="GPT-4o",
            input_cost_per_1k=0.005,
            output_cost_per_1k=0.015,
            max_tokens=128000,
            description="GPT-4o (“o” for “omni”) is our versatile, high-intelligence flagship model. It accepts both text and image inputs, and produces text outputs (including Structured Outputs). Learn how to use GPT-4o in our text generation guide.The chatgpt-4o-latest model ID below continuously points to the version of GPT-4o used in ChatGPT. It is updated frequently, when there are significant changes to ChatGPT's GPT-4o model."
        ),
        ModelName.GPT_O1_MINI: ModelConfig(
            name=ModelName.GPT_O1_MINI,
            display_name="GPT-O1-mini",
            input_cost_per_1k=0.001,
            output_cost_per_1k=0.004,
            max_tokens=128000,
            description="The o1 series of models are trained with reinforcement learning to perform complex reasoning. o1 models think before they answer, producing a long internal chain of thought before responding to the user. Learn about the capabilities of o1 models in our reasoning guide.The o1 reasoning model is designed to solve hard problems across domains. o1-mini is a faster and more affordable reasoning model, but we recommend using the newer o3-mini model that features higher intelligence at the same latency and price as o1-mini."
        )
    }

    @classmethod
    def get_model_config(cls, model_name: Union[str, ModelName]) -> ModelConfig:
        """Get configuration for a model by name"""
        if isinstance(model_name, str):
            model_name = ModelName(model_name)
        return cls.MODELS[model_name]

    @classmethod
    def get_all_models(cls) -> List[ModelConfig]:
        """Get list of all available models"""
        return list(cls.MODELS.values())

    @classmethod
    def calculate_cost(cls, model_name: Union[str, ModelName], input_tokens: int, output_tokens: int) -> tuple[float, Dict]:
        """Calculate cost for a model usage"""
        config = cls.get_model_config(model_name)
        
        input_cost = (input_tokens / 1000) * config.input_cost_per_1k
        output_cost = (output_tokens / 1000) * config.output_cost_per_1k
        total_cost = input_cost + output_cost
        
        return total_cost, {
            "total_cost": total_cost,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": model_name if isinstance(model_name, str) else model_name.value
        }
