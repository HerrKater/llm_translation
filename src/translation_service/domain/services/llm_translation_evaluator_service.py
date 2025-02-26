import json
import asyncio
import re
from typing import Dict, Tuple, Any, Optional
from functools import lru_cache

from domain.model.settings import Settings
from domain.model.llm_pricing import LLMPricing
from infrastructure.llm.factory import create_llm_client, LLMProvider
from domain.domain_interfaces.translation_evaluator import TranslationEvaluatorService
from domain.model.llm_evaluation import LLMEvaluation, CostInfo, EvaluationMetric, EvaluationResult

class LlmTranslationEvaluatorService(TranslationEvaluatorService):
    def __init__(self, settings: Settings, batch_size: int = 5):
        self.llm_client = create_llm_client(
            provider=LLMProvider.OPENAI,
            settings=settings
        )
        # Add semaphore for rate limiting
        self._semaphore = asyncio.Semaphore(batch_size)
        # Cache for language names
        self._language_names = {
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

    @lru_cache(maxsize=10)
    def get_language_name(self, target_language: str) -> str:
        """Get full language name from language code with caching."""
        return self._language_names.get(target_language, target_language.upper())

    async def evaluate_translation(
        self, 
        english_text: str,
        reference_translation: str,
        new_translation: str,
        target_language: str,
        model: str = None
    ) -> EvaluationResult:
        """Use LLM to evaluate the translation quality with rate limiting."""
        # Use semaphore to control API request rate
        async with self._semaphore:
            return await self._evaluate_translation_impl(
                english_text, 
                reference_translation, 
                new_translation, 
                target_language, 
                model
            )

    async def _evaluate_translation_impl(
        self,
        english_text: str,
        reference_translation: str,
        new_translation: str,
        target_language: str,
        model: str = None
    ) -> EvaluationResult:
        """Internal implementation of translation evaluation."""
        # Use provided model or fallback to default
        model_to_use = model or self.model
        
        # Get language name for prompt
        language_name = self.get_language_name(target_language)
        
        # Prepare evaluation prompts
        reference_prompt = self.create_prompt(english_text, reference_translation, language_name)
        new_prompt = self.create_prompt(english_text, new_translation, language_name)

        try:
            # Create API call tasks
            ref_task = self.llm_client.chat(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": f"You are a {language_name} language expert. Provide evaluation in the exact JSON format requested."},
                    {"role": "user", "content": reference_prompt}
                ]
            )
            
            new_task = self.llm_client.chat(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": f"You are a {language_name} language expert. Provide evaluation in the exact JSON format requested."},
                    {"role": "user", "content": new_prompt}
                ]
            )
            
            # Use asyncio.shield to prevent cancellation during critical operations
            reference_response, new_response = await asyncio.gather(
                asyncio.shield(ref_task),
                asyncio.shield(new_task),
                return_exceptions=True
            )
            
            # Check for exceptions in responses
            if isinstance(reference_response, Exception):
                raise reference_response
            if isinstance(new_response, Exception):
                raise new_response

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
            return self._handle_error(
                error_message, 
                english_text, 
                reference_translation, 
                new_translation
            )
        except Exception as e:
            error_message = f"Unexpected error during evaluation: {str(e)}"
            return self._handle_error(
                error_message, 
                english_text, 
                reference_translation, 
                new_translation
            )

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
        # Truncate texts if they exceed token limits
        max_text_length = 1000  # Approximate character limit to avoid excessive token usage
        
        if len(original_text) > max_text_length:
            original_text = original_text[:max_text_length] + "... [truncated]"
            
        if len(translation) > max_text_length:
            translation = translation[:max_text_length] + "... [truncated]"
            
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

    def extract_json_from_response(self, content: str) -> str:
        """Extract JSON from response content more robustly."""
        # Try to extract JSON using regex pattern matching
        json_pattern = r'({[\s\S]*})'
        match = re.search(json_pattern, content)
        
        if match:
            return match.group(1).strip()
        
        # If regex fails, try manual extraction
        content = content.strip()
        
        # Remove common markdown code markers
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
            
        return content.strip()

    def parse_evaluation_response(self, response: dict, model_to_use: str) -> LLMEvaluation:
        """Parse LLM evaluation response with improved error handling."""
        try:
            # Extract content more reliably
            content = response.get('content', '').strip()
            json_content = self.extract_json_from_response(content)
            
            # Parse JSON with error handling
            try:
                evaluation_dict = json.loads(json_content)
            except json.JSONDecodeError:
                # As fallback, try to extract JSON again with more aggressive cleaning
                clean_content = re.sub(r'[^\x00-\x7F]+', '', json_content)  # Remove non-ASCII chars
                evaluation_dict = json.loads(clean_content)
            
            # Calculate cost for evaluation
            usage = response.get('usage', {'prompt_tokens': 0, 'completion_tokens': 0})
            total_cost, cost_breakdown = LLMPricing.calculate_cost(
                model=model_to_use,
                input_tokens=usage.get('prompt_tokens', 0),
                output_tokens=usage.get('completion_tokens', 0)
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
            
            # Process each evaluation metric with validation
            metrics = {}
            for criterion in [
                'Accuracy', 'Fluency', 'Adequacy', 'Consistency', 
                'Contextual_Appropriateness', 'Terminology_Accuracy', 
                'Readability', 'Format_Preservation', 'Error_Rate'
            ]:
                # Handle potential case sensitivity issues
                criterion_key = criterion
                for key in evaluation_dict.keys():
                    if key.lower() == criterion.lower():
                        criterion_key = key
                        break
                
                # Extract data with validation
                data = evaluation_dict.get(criterion_key, {})
                if not isinstance(data, dict):
                    data = {'score': 3, 'explanation': f"Missing or invalid data for {criterion}"}
                
                # Get and validate score
                raw_score = data.get('score', 3)
                if not isinstance(raw_score, (int, float)) or raw_score < 1 or raw_score > 5:
                    raw_score = 3  # Default to middle score if invalid
                
                # Create metric
                metrics[criterion.lower()] = EvaluationMetric(
                    score=float(raw_score),
                    raw_score=int(raw_score),
                    explanation=str(data.get('explanation', f"No explanation provided for {criterion}"))
                )
            
            # Create LLM evaluation with cost info
            comments = "\n".join([
                f"{k.replace('_', ' ').title()}: {v.explanation}" 
                for k, v in metrics.items() 
                if v and v.explanation
            ])
            
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
                matches_reference=metrics['accuracy'].score >= 4,  # Consider it matching if accuracy is high
                comments=comments,
                cost_info=cost_info
            )
            
            return result
            
        except Exception as e:
            # If anything goes wrong, create a default evaluation with error
            error_message = f"Failed to parse LLM response: {str(e)}"
            return self._create_default_evaluation(error_message, model_to_use)
            
    def _create_default_evaluation(self, error_message: str, model: str) -> LLMEvaluation:
        """Create a default evaluation for error cases."""
        default_cost = CostInfo(
            total_cost=0.0,
            input_cost=0.0,
            output_cost=0.0,
            input_tokens=0,
            output_tokens=0,
            model=model
        )
        
        default_metric = EvaluationMetric(
            score=0.0, 
            raw_score=0, 
            explanation=error_message
        )
        
        return LLMEvaluation(
            accuracy=default_metric,
            fluency=default_metric,
            adequacy=default_metric,
            consistency=default_metric,
            contextual_appropriateness=default_metric,
            terminology_accuracy=default_metric,
            readability=default_metric,
            format_preservation=default_metric,
            error_rate=default_metric,
            matches_reference=False,
            comments=error_message,
            cost_info=default_cost
        )
            
    def _handle_error(
        self, 
        error_message: str, 
        english_text: str = '', 
        reference_translation: str = '', 
        new_translation: str = ''
    ) -> EvaluationResult:
        """Handle errors and return a default evaluation result."""
        default_evaluation = self._create_default_evaluation(error_message, getattr(self, 'model', 'unknown'))
        
        return EvaluationResult(
            source_text=english_text,
            reference_translation=reference_translation,
            new_translation=new_translation,
            reference_evaluation=default_evaluation,
            new_evaluation=default_evaluation,
            matches_reference=False,
            cost_info=default_evaluation.cost_info
        )