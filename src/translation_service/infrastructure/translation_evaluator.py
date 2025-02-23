import os
import openai
from dataclasses import dataclass
from typing import Dict
from infrastructure.config import Settings

@dataclass
class TranslationEvaluationResult:
    accuracy_score: float
    fluency_score: float
    matches_reference: bool
    comments: str

class OpenAITranslationEvaluator:
    def __init__(self, settings: Settings):
        self.openai_client = openai.OpenAI(
            base_url=os.getenv("OPENAI_URL"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("OPENAI_LANGUAGE_MODEL")

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

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Hungarian language expert. Provide evaluation in the exact JSON format requested."},
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            result = response.choices[0].message.content
            # Parse the JSON string into a dictionary
            import json
            evaluation_dict = json.loads(result)
            
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
