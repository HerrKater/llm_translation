from io import StringIO
import asyncio
import pandas as pd
from typing import List

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
        evaluator: LlmTranslationEvaluatorService
    ):
        self.translator = translator
        self.evaluator = evaluator

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
            df = pd.read_csv(StringIO(content.decode()))
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
        return df

    async def process_row(
        self,
        index: int,
        row,
        target_language: str,
        translation_model: str,
        evaluation_model: str
    ) -> EvaluationResult:
        # Get source and target language texts
        source_text = str(row['english']).strip()
        reference_translation = str(row['translated_value']).strip()

        # Validate non-empty values
        if not source_text or not reference_translation:
            raise ValueError(f"Row {index + 1} contains empty values")
    
        # Get new translation with specified model
        request = TranslationRequest(source_content=source_text, target_languages=[target_language])
        translation, translation_cost_info = await self.translator.translate(request, model=translation_model)
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

        # Process all rows concurrently
        tasks = [
            self.process_row(
                i, row, 
                target_language,
                translation_model_enum.value,
                evaluation_model_enum.value
            ) 
            for i, row in df.iterrows()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Calculate summary statistics
        num_results = len(results)
        summary = {
            'avg_accuracy': sum(r.new_evaluation.accuracy.score for r in results) / num_results if num_results > 0 else 0,
            'avg_fluency': sum(r.new_evaluation.fluency.score for r in results) / num_results if num_results > 0 else 0,
            'avg_adequacy': sum(r.new_evaluation.adequacy.score for r in results) / num_results if num_results > 0 else 0,
            'avg_consistency': sum(r.new_evaluation.consistency.score for r in results) / num_results if num_results > 0 else 0,
            'avg_contextual_appropriateness': sum(r.new_evaluation.contextual_appropriateness.score for r in results) / num_results if num_results > 0 else 0,
            'avg_terminology_accuracy': sum(r.new_evaluation.terminology_accuracy.score for r in results) / num_results if num_results > 0 else 0,
            'avg_readability': sum(r.new_evaluation.readability.score for r in results) / num_results if num_results > 0 else 0,
            'avg_format_preservation': sum(r.new_evaluation.format_preservation.score for r in results) / num_results if num_results > 0 else 0,
            'avg_error_rate': sum(r.new_evaluation.error_rate.score for r in results) / num_results if num_results > 0 else 0
        }
        
        # Calculate total cost (translations + evaluations)
        total_cost = sum(
            r.cost_info.total_cost
            for r in results
        )
        
        return BatchEvaluationResponse(
            results=results,
            summary=summary,
            total_cost=total_cost
        )
