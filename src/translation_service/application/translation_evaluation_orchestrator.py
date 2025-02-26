from io import StringIO
import asyncio
import pandas as pd
from typing import List, Dict, Any
from functools import partial

from domain.model.language_models import ModelName
from domain.model.language_settings import language_settings
from domain.model.translation_request import TranslationRequest
from domain.services.llm_translator_service import LlmTranslatorService
from domain.services.llm_translation_evaluator_service import LlmTranslationEvaluatorService
from domain.model.llm_evaluation import (LLMEvaluation, CostInfo, EvaluationMetric, 
    BatchEvaluationResponse, EvaluationResult)

class TranslationEvaluationOrchestrator:
    def __init__(
        self,
        translator: LlmTranslatorService,
        evaluator: LlmTranslationEvaluatorService,
        batch_size: int = 10  # Control concurrency with batch size
    ):
        self.translator = translator
        self.evaluator = evaluator
        self.batch_size = batch_size
        self._semaphore = asyncio.Semaphore(batch_size)  # Limit concurrent API calls

    def validate_language(self, target_language: str) -> None:
        if not language_settings.is_language_supported(target_language):
            raise ValueError(f"Unsupported language code: {target_language}")

    def validate_models(self, translation_model: str, evaluation_model: str) -> tuple[ModelName, ModelName]:
        try:
            translation_model_enum = ModelName(translation_model)
            evaluation_model_enum = ModelName(evaluation_model)
            return translation_model_enum, evaluation_model_enum
        except ValueError:
            raise ValueError(f"Invalid model. Must be one of: {[model.value for model in ModelName]}")

    def validate_csv_content(self, content: bytes) -> pd.DataFrame:
        try:
            df = pd.read_csv(StringIO(content.decode()), na_filter=True)
            # Convert all columns to string and strip whitespace
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].astype(str).str.strip()
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")

        # Validate required columns
        required_columns = ['english', 'translated_value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}. "
                f"CSV must have columns: {', '.join(required_columns)}"
            )
        
        # Check for empty values in required columns
        empty_rows = df[df[required_columns].isna().any(axis=1)]
        if not empty_rows.empty:
            raise ValueError(f"Rows {empty_rows.index + 1} contain empty values in required columns")
            
        return df

    async def process_row(
        self,
        index: int,
        row,
        target_language: str,
        translation_model: str,
        evaluation_model: str
    ) -> EvaluationResult:
        # Use semaphore to limit concurrent API calls
        async with self._semaphore:
            try:
                # Get source and target language texts
                source_text = str(row['english'])
                reference_translation = str(row['translated_value'])
                
                # Get new translation with specified model
                request = TranslationRequest(source_content=source_text, target_languages=[target_language])
                translation, translation_cost_info = await self.translator.translate(
                    request, model=translation_model
                )
                new_translation = translation.translations[target_language]
                
                # Create cost info for translation
                translation_cost = CostInfo(
                    total_cost=translation_cost_info['input_cost'] + translation_cost_info['output_cost'],
                    input_cost=translation_cost_info['input_cost'],
                    output_cost=translation_cost_info['output_cost'],
                    input_tokens=translation_cost_info['input_tokens'],
                    output_tokens=translation_cost_info['output_tokens'],
                    model=translation_cost_info['model']
                )
                
                # Evaluate translation with specified model
                evaluation_result = await self.evaluator.evaluate_translation(
                    source_text,
                    reference_translation,
                    new_translation,
                    target_language,
                    model=evaluation_model
                )
                
                return evaluation_result
            except Exception as e:
                # Log error but continue processing other rows
                print(f"Error processing row {index}: {str(e)}")
                raise

    async def batch_process(
        self, 
        tasks: List[asyncio.Task]
    ) -> List[EvaluationResult]:
        """Process tasks in batches to control concurrency"""
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def evaluate_translations(
        self,
        file_content: bytes,
        target_language: str,
        translation_model: str,
        evaluation_model: str
    ) -> BatchEvaluationResponse:
        # Validate inputs
        self.validate_language(target_language)
        translation_model_enum, evaluation_model_enum = self.validate_models(translation_model, evaluation_model)
        df = self.validate_csv_content(file_content)

        # Create tasks for all rows but don't execute them yet
        tasks = [
            self.process_row(
                i, row, 
                target_language,
                translation_model_enum.value,
                evaluation_model_enum.value
            ) 
            for i, row in df.iterrows()
        ]
        
        # Use tqdm if available for progress reporting
        try:
            from tqdm.asyncio import tqdm_asyncio
            results = await tqdm_asyncio.gather(*tasks, desc="Processing translations")
        except ImportError:
            # Process using our batched approach if tqdm isn't available
            results = await asyncio.gather(*tasks)
            
        # Filter out any exceptions that were returned
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        # Log how many failures occurred
        if len(valid_results) < len(results):
            print(f"Warning: {len(results) - len(valid_results)} rows failed to process")
        
        # Calculate summary statistics
        num_results = len(valid_results)
        if num_results == 0:
            raise ValueError("No valid results were obtained from the evaluation")
            
        # Calculate metrics using a helper function to avoid repetition
        def calculate_avg_metric(attr_path: str) -> float:
            total = 0.0
            for result in valid_results:
                # Navigate the attribute path, e.g., "new_evaluation.accuracy.score"
                obj = result
                for attr in attr_path.split('.'):
                    obj = getattr(obj, attr)
                total += obj
            return total / num_results
            
        # Build summary with all metrics
        metrics = {
            'accuracy': ('new_evaluation.accuracy.score', 'reference_evaluation.accuracy.score'),
            'fluency': ('new_evaluation.fluency.score', 'reference_evaluation.fluency.score'),
            'adequacy': ('new_evaluation.adequacy.score', 'reference_evaluation.adequacy.score'),
            'consistency': ('new_evaluation.consistency.score', 'reference_evaluation.consistency.score'),
            'contextual_appropriateness': ('new_evaluation.contextual_appropriateness.score', 'reference_evaluation.contextual_appropriateness.score'),
            'terminology_accuracy': ('new_evaluation.terminology_accuracy.score', 'reference_evaluation.terminology_accuracy.score'),
            'readability': ('new_evaluation.readability.score', 'reference_evaluation.readability.score'),
            'format_preservation': ('new_evaluation.format_preservation.score', 'reference_evaluation.format_preservation.score'),
            'error_rate': ('new_evaluation.error_rate.score', 'reference_evaluation.error_rate.score'),
        }
        
        summary = {}
        for metric_name, (new_path, ref_path) in metrics.items():
            summary[f'avg_{metric_name}'] = calculate_avg_metric(new_path)
            summary[f'avg_reference_{metric_name}'] = calculate_avg_metric(ref_path)
        
        # Calculate total cost (translations + evaluations)
        total_cost = sum(r.cost_info.total_cost for r in valid_results)
        
        return BatchEvaluationResponse(
            results=valid_results,
            summary=summary,
            total_cost=total_cost
        )