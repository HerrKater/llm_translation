import json
from domain.model.settings import Settings
from domain.model.llm_pricing import LLMPricing
from infrastructure.llm.factory import create_llm_client, LLMProvider
from domain.domain_interfaces.translation_evaluator import TranslationEvaluatorService
from domain.model.llm_evaluation import LLMEvaluation, CostInfo, EvaluationMetric, EvaluationResult

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
        new_translation: str,
        target_language: str,
        model: str = None
    ) -> EvaluationResult:
        """Use LLM to evaluate the translation quality."""
        # Use provided model or fallback to default
        model_to_use = model or self.model
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
        # Evaluate reference translation
        try:
          reference_prompt = self.create_prompt(english_text, reference_translation)
          reference_response = self.llm_client.chat(
              model=model_to_use,
              messages=[
                  {"role": "system", "content": f"You are a {language_name} language expert. Provide evaluation in the exact JSON format requested."},
                  {"role": "user", "content": reference_prompt}
              ]
          )
          reference_evaluation = self.parse_evaluation_response(reference_response, model_to_use)

          # Evaluate new translation
          new_prompt = self.create_prompt(english_text, new_translation)

        
          new_response = self.llm_client.chat(
              model=model_to_use,
              messages=[
                  {"role": "system", "content": f"You are a {language_name} language expert. Provide evaluation in the exact JSON format requested."},
                  {"role": "user", "content": new_prompt}
              ]
          )

          new_evaluation = self.parse_evaluation_response(new_response, model_to_use)
          
          # Calculate total cost
          total_cost = CostInfo(
              total_cost=reference_evaluation.cost_info.total_cost + new_evaluation.cost_info.total_cost,
              input_cost=reference_evaluation.cost_info.input_cost + new_evaluation.cost_info.input_cost,
              output_cost=reference_evaluation.cost_info.output_cost + new_evaluation.cost_info.output_cost,
              input_tokens=reference_evaluation.cost_info.input_tokens + new_evaluation.cost_info.input_tokens,
              output_tokens=reference_evaluation.cost_info.output_tokens + new_evaluation.cost_info.output_tokens,
              model=model_to_use
          )
          
          # Create evaluation result
          return EvaluationResult(
              source_text=english_text,
              reference_translation=reference_translation,
              new_translation=new_translation,
              reference_evaluation=reference_evaluation,
              new_evaluation=new_evaluation,
              matches_reference=new_evaluation.matches_reference,
              cost_info=total_cost
          )
           
        except (json.JSONDecodeError, KeyError, ValueError, AttributeError) as e:
            error_message = f"Error parsing LLM response: {str(e)}"
            return self._handle_error(error_message)
        except Exception as e:
            error_message = f"Unexpected error during evaluation: {str(e)}"
            return self._handle_error(error_message)

    def create_prompt(original_text, translation):
      prompt = f"""You are an expert translator and evaluator. Your task is to assess the quality of a machine-generated translation based on several key criteria. Below are the source text and its translation. Evaluate the translation on each criterion listed, providing a score from 1 to 5 (where 1 is poor and 5 is excellent) and a brief explanation for each score.

Source Text:
{original_text}

Translated Text:
{translation}


Evaluation Criteria:

1. Accuracy: How well does the translation convey the original meaning?
2. Fluency: Is the translation grammatically correct and natural-sounding?
3. Adequacy: Are all important elements of the source text present?
4. Consistency: Is terminology used consistently throughout the translation?
5. Contextual Appropriateness: Does the translation appropriately reflect the context and cultural nuances?
6. Terminology Accuracy: Are specialized terms translated correctly?
7. Readability: Is the translation easy to read and understand?
8. Format Preservation: Does the translation maintain the original formatting and layout?
9. Error Rate: Are there any grammatical or typographical errors?

Provide the evaluation as a JSON object with each criterion as a key. Each key should have an object containing two fields:
"score": An integer between 1 and 5
"explanation": A brief string explaining the score

Example response format:
{{
  "Accuracy": {{
    "score": 5,
    "explanation": "The translation perfectly conveys the original meaning without any loss or alteration."
  }},
  "Fluency": {{
    "score": 4,
    "explanation": "The translation is grammatically correct and reads naturally, with minor stylistic improvements possible."
  }},
  "Adequacy": {{
    "score": 5,
    "explanation": "All important elements from the source text are present in the translation."
  }},
  "Consistency": {{
    "score": 5,
    "explanation": "Terminology is used consistently throughout the translation."
  }},
  "Contextual_Appropriateness": {{
    "score": 4,
    "explanation": "The translation reflects the context and cultural nuances well."
  }},
  "Terminology_Accuracy": {{
    "score": 5,
    "explanation": "All specialized terms are translated correctly."
  }},
  "Readability": {{
    "score": 4,
    "explanation": "The translation is clear and easy to understand."
  }},
  "Format_Preservation": {{
    "score": 5,
    "explanation": "The original formatting and layout are perfectly maintained."
  }},
  "Error_Rate": {{
    "score": 5,
    "explanation": "There are no grammatical or typographical errors."
  }}
}}"""
    
    def create_prompt(self, original_text: str, translation: str) -> str:
        prompt = f"""Please evaluate the following translation pair and provide a detailed assessment in JSON format.

Original Text:
{original_text}

Translation:
{translation}

Provide an evaluation using the following criteria, scoring each on a scale of 1-5 where 5 is best.
Return the evaluation in this exact JSON format:

{{
  "Accuracy": {{
    "score": 5,
    "explanation": "The translation accurately conveys all the meaning from the source text."
  }},
  "Fluency": {{
    "score": 5,
    "explanation": "The translation reads naturally and smoothly in the target language."
  }},
  "Adequacy": {{
    "score": 5,
    "explanation": "All information is preserved without additions or omissions."
  }},
  "Consistency": {{
    "score": 5,
    "explanation": "Terminology and style are consistent throughout."
  }},
  "Contextual_Appropriateness": {{
    "score": 5,
    "explanation": "The translation is appropriate for the context and target audience."
  }},
  "Terminology_Accuracy": {{
    "score": 5,
    "explanation": "Domain-specific terms are correctly translated."
  }},
  "Readability": {{
    "score": 5,
    "explanation": "The text is clear and easy to understand."
  }},
  "Format_Preservation": {{
    "score": 5,
    "explanation": "The original formatting and layout are perfectly maintained."
  }},
  "Error_Rate": {{
    "score": 5,
    "explanation": "There are no grammatical or typographical errors."
  }}
}}"""
        return prompt
    
    
    
    def parse_evaluation_response(self, response: dict, model_to_use: str):
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
      
      # Process each evaluation metric
      metrics = {}
      for criterion, data in evaluation_dict.items():
          raw_score = int(data['score'])
          metrics[criterion.lower()] = EvaluationMetric(
              score=raw_score,
              raw_score=raw_score,
              explanation=data['explanation']
          )
      
      # Create LLM evaluation with cost info for the UI
      return LLMEvaluation(
          accuracy=metrics['accuracy'],
          fluency=metrics['fluency'],
          adequacy=metrics['adequacy'],
          consistency=metrics['consistency'],
          contextual_appropriateness=metrics['contextual_appropriateness'],
          terminology_accuracy=metrics['terminology_accuracy'],
          readability=metrics['readability'],
          format_preservation=metrics['format_preservation'],
          error_rate=metrics['error_rate'],
          matches_reference=metrics['accuracy'].score > 7.5,  # Consider it matching if accuracy is high
          comments="\n".join([f"{k.replace('_', ' ').title()}: {v.explanation}" for k, v in metrics.items()]),
          cost_info=cost_info
      )

            
    def _handle_error(self, error_message: str, english_text: str = '', reference_translation: str = '', new_translation: str = '') -> EvaluationResult:
        default_cost = CostInfo(
            total_cost=0.0,
            input_cost=0.0,
            output_cost=0.0,
            input_tokens=0,
            output_tokens=0,
            model=self.model
        )
        
        default_evaluation = LLMEvaluation(
            accuracy=EvaluationMetric(score=0.0, raw_score=0, explanation=error_message),
            fluency=EvaluationMetric(score=0.0, raw_score=0, explanation=error_message),
            adequacy=EvaluationMetric(score=0.0, raw_score=0, explanation=error_message),
            consistency=EvaluationMetric(score=0.0, raw_score=0, explanation=error_message),
            contextual_appropriateness=EvaluationMetric(score=0.0, raw_score=0, explanation=error_message),
            terminology_accuracy=EvaluationMetric(score=0.0, raw_score=0, explanation=error_message),
            readability=EvaluationMetric(score=0.0, raw_score=0, explanation=error_message),
            format_preservation=EvaluationMetric(score=0.0, raw_score=0, explanation=error_message),
            error_rate=EvaluationMetric(score=0.0, raw_score=0, explanation=error_message),
            matches_reference=False,
            comments=error_message,
            cost_info=default_cost
        )
        
        return EvaluationResult(
            source_text=english_text,
            reference_translation=reference_translation,
            new_translation=new_translation,
            reference_evaluation=default_evaluation,
            new_evaluation=default_evaluation,
            matches_reference=False,
            cost_info=default_cost
        )
