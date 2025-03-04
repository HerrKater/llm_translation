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
from domain.services.translation_system import TranslationSystem

class LlmTranslationEvaluatorService(TranslationEvaluatorService):
    def __init__(self, settings: Settings, batch_size: int = 5):
        self.llm_client = create_llm_client(
            provider=LLMProvider.OPENAI,
            settings=settings
        )
        self.translation_system = TranslationSystem()
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
        reference_prompt = self.translation_system.create_evaluation_prompt(english_text, reference_translation, language_name)
        new_prompt = self.translation_system.create_evaluation_prompt(english_text, new_translation, language_name)

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