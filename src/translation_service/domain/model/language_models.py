from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Union

class ModelName(str, Enum):
    """Supported language models"""
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_O1_MINI = "gpt-o1-mini"

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
            display_name="GPT-4O Mini",
            input_cost_per_1k=0.01,
            output_cost_per_1k=0.03,
            max_tokens=4000,
            description="Fast and cost-effective model for general translation tasks"
        ),
        ModelName.GPT_4O: ModelConfig(
            name=ModelName.GPT_4O,
            display_name="GPT-4O",
            input_cost_per_1k=0.03,
            output_cost_per_1k=0.06,
            max_tokens=8000,
            description="High accuracy model for complex translation tasks"
        ),
        ModelName.GPT_O1_MINI: ModelConfig(
            name=ModelName.GPT_O1_MINI,
            display_name="GPT-O1-mini",
            input_cost_per_1k=0.001,
            output_cost_per_1k=0.002,
            max_tokens=2000,
            description="Lightweight model for basic translation tasks"
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
