import json
from domain.model.settings import Settings
from domain.model.llm_pricing import LLMPricing
from infrastructure.llm.factory import create_llm_client, LLMProvider
from domain.domain_interfaces.translation_evaluator import TranslationEvaluatorService, TranslationEvaluationResult
from interfaces.evaluation_models import LLMEvaluation, CostInfo

class LlmTranslationEvaluatorService(TranslationEvaluatorService):
    def __init__(self, settings: Settings):
        self.llm_client = create_llm_client(
            provider=settings.llm_provider,
            settings=settings
        )
        self.model = settings.language_model
        self.last_evaluation = None  # Will store the last LLMEvaluation with cost info

    async def evaluate_translation(
        self, 
        english_text: str, 
        reference_translation: str, 
        new_translation: str,
        target_language: str,
        model: str = None
    ) -> TranslationEvaluationResult:
        # Use provided model or fallback to default
        model_to_use = model or self.model
        """Use LLM to evaluate the translation quality."""
        # Get language name for prompt
        language_names = {
            'hu': 'Hungarian',
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean'
        }
        language_name = language_names.get(target_language, target_language.upper())
        
        prompt = f"""You are a {language_name} language expert. Please evaluate the following translation from English to {language_name}:

Original English text: {english_text}
Reference translation: {reference_translation}
New translation: {new_translation}

Please analyze the translations and provide a JSON response with the following structure:
{{
    "accuracy_score": <score from 0-10>,
    "fluency_score": <score from 0-10>,
    "matches_reference": <true/false>,
    "comments": "<brief explanation of the evaluation>"
}}

Focus on semantic accuracy, fluency, and whether the new translation conveys the same meaning as the reference."""
        try:
            response = self.llm_client.chat(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": f"You are a {language_name} language expert. Provide evaluation in the exact JSON format requested."},
                    {"role": "user", "content": prompt}
                ]
            )

            content = response['content'].strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()

            evaluation_dict = json.loads(content)

            # Calculate cost for evaluation
            total_cost, cost_breakdown = LLMPricing.calculate_cost(
                model=model_to_use,
                input_tokens=response['usage']['prompt_tokens'],
                output_tokens=response['usage']['completion_tokens']
            )
            
            # Create cost info
            cost_info = CostInfo(
                total_cost=total_cost,
                input_cost=cost_breakdown['input_cost'],
                output_cost=cost_breakdown['output_cost'],
                input_tokens=cost_breakdown['input_tokens'],
                output_tokens=cost_breakdown['output_tokens'],
                model=model_to_use
            )
            
            # Create LLM evaluation with cost info for the UI
            self.last_evaluation = LLMEvaluation(
                accuracy_score=float(evaluation_dict["accuracy_score"]),
                fluency_score=float(evaluation_dict["fluency_score"]),
                matches_reference=bool(evaluation_dict["matches_reference"]),
                comments=str(evaluation_dict["comments"]),
                cost_info=cost_info
            )
            
            # Return interface-compatible result
            return TranslationEvaluationResult(
                accuracy_score=float(evaluation_dict["accuracy_score"]),
                fluency_score=float(evaluation_dict["fluency_score"]),
                matches_reference=bool(evaluation_dict["matches_reference"]),
                comments=str(evaluation_dict["comments"])
            )
        except (json.JSONDecodeError, KeyError, ValueError, AttributeError) as e:
            error_message = f"Error parsing LLM response: {str(e)}"
            return self._handle_error(error_message)
        except Exception as e:
            error_message = f"Unexpected error during evaluation: {str(e)}"
            return self._handle_error(error_message)

    def _handle_error(self, error_message: str) -> TranslationEvaluationResult:
        default_cost = CostInfo(
            total_cost=0.0,
            input_cost=0.0,
            output_cost=0.0,
            input_tokens=0,
            output_tokens=0,
            model=model_to_use
        )
        self.last_evaluation = LLMEvaluation(
            accuracy_score=0.0,
            fluency_score=0.0,
            matches_reference=False,
            comments=error_message,
            cost_info=default_cost
        )
        return TranslationEvaluationResult(
            accuracy_score=0.0,
            fluency_score=0.0,
            matches_reference=False,
            comments=error_message
        )
