from domain.model.settings import Settings
from infrastructure.llm.factory import create_llm_client, LLMProvider
from domain.domain_interfaces.translation_evaluator import TranslationEvaluatorService, TranslationEvaluationResult

class LlmTranslationEvaluatorService(TranslationEvaluatorService):
    def __init__(self, settings: Settings):
        self.llm_client = create_llm_client(
            provider=settings.llm_provider,
            settings=settings
        )
        self.model = settings.language_model

    async def evaluate_translation(
        self, 
        english_text: str, 
        reference_translation: str, 
        new_translation: str
    ) -> TranslationEvaluationResult:
        """Use LLM to evaluate the translation quality."""
        prompt = f"""You are a Hungarian language expert. Please evaluate the following translation from English to Hungarian:

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

        response = self.llm_client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Hungarian language expert. Provide evaluation in the exact JSON format requested."},
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            # Parse the JSON string from the response content
            import json
            evaluation_dict = json.loads(response['content'])
            
            return TranslationEvaluationResult(
                accuracy_score=float(evaluation_dict["accuracy_score"]),
                fluency_score=float(evaluation_dict["fluency_score"]),
                matches_reference=bool(evaluation_dict["matches_reference"]),
                comments=str(evaluation_dict["comments"])
            )
        except (json.JSONDecodeError, KeyError, ValueError, AttributeError) as e:
            # Return a default result in case of any parsing errors
            return TranslationEvaluationResult(
                accuracy_score=0.0,
                fluency_score=0.0,
                matches_reference=False,
                comments=f"Error parsing LLM response: {str(e)}"
            )
