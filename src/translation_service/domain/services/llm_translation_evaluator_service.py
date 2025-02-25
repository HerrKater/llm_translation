import json
import asyncio
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
        # Evaluate reference and new translations in parallel
        try:
          reference_prompt = self.create_prompt(english_text, reference_translation, language_name)
          new_prompt = self.create_prompt(english_text, new_translation, language_name)

          # Run evaluations in parallel
          reference_response, new_response = await asyncio.gather(
              self.llm_client.chat(
                  model=model_to_use,
                  messages=[
                      {"role": "system", "content": f"You are a {language_name} language expert. Provide evaluation in the exact JSON format requested."},
                      {"role": "user", "content": reference_prompt}
                  ]
              ),
              self.llm_client.chat(
                  model=model_to_use,
                  messages=[
                      {"role": "system", "content": f"You are a {language_name} language expert. Provide evaluation in the exact JSON format requested."},
                      {"role": "user", "content": new_prompt}
                  ]
              )
          )

          # Parse responses
          reference_evaluation = self.parse_evaluation_response(reference_response, model_to_use)
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

    def create_prompt(self, original_text: str, translation: str, target_language: str) -> str:
      """
      Creates a system prompt for evaluating translation quality.
      
      Args:
          original_text: The source text in English
          translation: The translated text to evaluate
          target_language: The language of the translation (e.g., "Hungarian", "Spanish")
          
      Returns:
          A formatted system prompt string for LLM translation evaluation
      """
      prompt = f"""# System Prompt for Translation Quality Evaluation

    You are a specialized evaluator for translations in a financial/investment context. Your task is to assess the translation of the provided English text to {target_language}, evaluating for accuracy, naturalness, and cultural appropriateness, and provide standardized scores in a structured JSON format.

    ## Original Text
    ```
    {original_text}
    ```

    ## Translation to Evaluate
    ```
    {translation}
    ```

    ## Target Language
    {target_language}

    ## Key Evaluation Criteria

    1. **Grammatical Accuracy**
      - Ensure proper use of grammatical features specific to {target_language} (cases, gender, tense, etc.)
      - Check that all syntactic structures are correctly applied according to {target_language} rules
      - Pay special attention to how parameters and variables (marked with brackets like [countryName]) are integrated grammatically

    2. **Number and Date Formatting**
      - Verify that numbers, currencies, dates, and other formatted elements follow {target_language} conventions
      - Check correct use of decimal and thousand separators according to local standards

    3. **Terminology**
      - Identify inappropriately borrowed English terms when {target_language} equivalents exist
      - Financial terms should use standard {target_language} terminology when established
      - Check for industry-specific terms that may have standardized translations

    4. **Word Order and Syntax**
      - Evaluate if the translation follows natural {target_language} syntax rather than mirroring English structure
      - Check if modifiers, adjectives, and other elements are placed correctly according to {target_language} norms

    5. **Stylistic Appropriateness**
      - Assess if the translation uses unnecessarily verbose or overly literal constructions
      - Check if idiomatic expressions are appropriately adapted to {target_language}
      - Evaluate whether the formality level is appropriate for a financial/investment context

    6. **Consistency**
      - Ensure product features, functions, and key terms are consistently translated
      - Check that recurring phrases maintain consistent translations throughout

    7. **Parameter Handling**
      - Verify that dynamic parameters (marked with brackets like [countryName], [brokerName], etc.) are properly integrated with appropriate grammatical adaptations required by {target_language}
      - Check if numeric parameters need grammatical agreement (e.g., pluralization rules)

    ## Scoring System

    For each metric below, you must assign a score from 1-5 based on EXACTLY these definitions:

    ### Accuracy (How accurately the translation conveys the meaning of the source text)
    - Score 1: Complete mistranslation that changes the meaning entirely
    - Score 2: Major inaccuracies that significantly alter the meaning
    - Score 3: Some inaccuracies that slightly alter the meaning
    - Score 4: Minor inaccuracies that don't significantly impact meaning
    - Score 5: Perfect accuracy with all meaning correctly preserved

    ### Fluency (How naturally and smoothly the translation reads in {target_language})
    - Score 1: Incomprehensible, not recognizable as {target_language}
    - Score 2: Difficult to understand, sounds like machine translation
    - Score 3: Understandable but with awkward phrasing
    - Score 4: Mostly natural with minor awkwardness
    - Score 5: Reads like it was originally written in {target_language}

    ### Adequacy (Whether all information is preserved without additions or omissions)
    - Score 1: Most information missing or added incorrectly
    - Score 2: Significant information missing or added unnecessarily
    - Score 3: Some information missing or added unnecessarily
    - Score 4: Minor details missing or added
    - Score 5: All information perfectly preserved

    ### Consistency (Whether terminology and style are consistent throughout)
    - Score 1: Completely inconsistent terminology and style
    - Score 2: Major inconsistencies in key terms
    - Score 3: Some noticeable inconsistencies
    - Score 4: Few minor inconsistencies
    - Score 5: Perfect consistency throughout

    ### Contextual_Appropriateness (Whether the translation is appropriate for the context and target audience)
    - Score 1: Completely inappropriate for financial/investment context
    - Score 2: Major issues with appropriateness
    - Score 3: Some elements inappropriate for context
    - Score 4: Minor issues with appropriateness
    - Score 5: Perfectly appropriate for financial/investment context

    ### Terminology_Accuracy (Whether domain-specific terms are correctly translated)
    - Score 1: Most financial terms incorrectly translated
    - Score 2: Several major financial terms mistranslated
    - Score 3: Some financial terms incorrectly translated
    - Score 4: Minor issues with specialized terminology
    - Score 5: All financial/investment terms correctly translated

    ### Readability (How clear and easy to understand the text is)
    - Score 1: Incomprehensible
    - Score 2: Very difficult to understand
    - Score 3: Requires effort to understand
    - Score 4: Easy to understand with minor clarity issues
    - Score 5: Perfectly clear and easy to understand

    ### Format_Preservation (Whether the original formatting and layout are maintained)
    - Score 1: Format completely altered
    - Score 2: Major formatting issues
    - Score 3: Some formatting inconsistencies
    - Score 4: Minor formatting differences
    - Score 5: Perfect preservation of format

    ### Error_Rate (Absence of grammatical or typographical errors)
    - Score 1: Numerous serious errors throughout
    - Score 2: Several major errors
    - Score 3: Some noticeable errors
    - Score 4: Few minor errors
    - Score 5: No errors detected

    ## Response Format

    You must return your evaluation ONLY as a valid JSON object. Do not include any text before or after the JSON. The response must be parseable by a JSON parser. 

    Your response must follow this exact structure:

    ```json
    {{
      "Accuracy": {{
        "score": [integer between 1-5],
        "explanation": "Detailed explanation of the score."
      }},
      "Fluency": {{
        "score": [integer between 1-5],
        "explanation": "Detailed explanation of the score."
      }},
      "Adequacy": {{
        "score": [integer between 1-5],
        "explanation": "Detailed explanation of the score."
      }},
      "Consistency": {{
        "score": [integer between 1-5],
        "explanation": "Detailed explanation of the score."
      }},
      "Contextual_Appropriateness": {{
        "score": [integer between 1-5],
        "explanation": "Detailed explanation of the score."
      }},
      "Terminology_Accuracy": {{
        "score": [integer between 1-5],
        "explanation": "Detailed explanation of the score."
      }},
      "Readability": {{
        "score": [integer between 1-5],
        "explanation": "Detailed explanation of the score."
      }},
      "Format_Preservation": {{
        "score": [integer between 1-5],
        "explanation": "Detailed explanation of the score."
      }},
      "Error_Rate": {{
        "score": [integer between 1-5],
        "explanation": "Detailed explanation of the score."
      }}
    }}
    ```

    IMPORTANT: 
    1. The response must be VALID JSON only. Do not include any explanatory text, markdown formatting, or any other content outside of the JSON object.
    2. The JSON must be properly formatted with all quotation marks, commas, and brackets in the correct places.
    3. Scores must be integers between 1-5, not strings or arrays.
    4. Always use the exact score definitions provided above to determine the appropriate score.
    5. For each metric, reference the specific definition for that score level in your explanation.

    ## Final Notes for Accurate Evaluation

    - Always consider {target_language} linguistic norms over literal translations
    - Pay special attention to cases where parameters ([countryName], [brokerName], etc.) would require grammatical adaptations specific to {target_language}
    - Consider the financial/investment context of the translations
    - Focus on both technical accuracy and natural-sounding {target_language}
    - Be aware of regional variations within {target_language} if applicable
    """
      return prompt

    def parse_evaluation_response(self, response: dict, model_to_use: str):
      print("DEBUG: Raw response:", response)
      content = response['content'].strip()
      if content.startswith('```json'):
          content = content[7:]
      elif content.startswith('```'):
          content = content[3:]
      if content.endswith('```'):
          content = content[:-3]
      content = content.strip()
      print("DEBUG: Content after cleanup:", content)
      evaluation_dict = json.loads(content)
      print("DEBUG: Parsed evaluation dict:", evaluation_dict)
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
              score=float(raw_score),  # Convert to float as required by the model
              raw_score=raw_score,
              explanation=data['explanation']
          )
      
      # Create LLM evaluation with cost info for the UI
      print("DEBUG: Final metrics:", metrics)
      result = LLMEvaluation(
          accuracy=metrics['accuracy'],
          fluency=metrics['fluency'],
          adequacy=metrics['adequacy'],
          consistency=metrics['consistency'],
          contextual_appropriateness=metrics['contextual_appropriateness'],
          terminology_accuracy=metrics['terminology_accuracy'],
          readability=metrics['readability'],
          format_preservation=metrics['format_preservation'],
          error_rate=metrics['error_rate'],
          matches_reference=metrics['accuracy'].score >= 4,  # Consider it matching if accuracy is high (4 or 5 out of 5)
          comments="\n".join([f"{k.replace('_', ' ').title()}: {v.explanation}" for k, v in metrics.items() if v and v.explanation]),
          cost_info=cost_info
      )
      print("DEBUG: Final result comments:", result.comments)
      return result

            
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
