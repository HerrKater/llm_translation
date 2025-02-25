import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

from domain.model.settings import Settings, get_settings
from domain.services.llm_translation_evaluator_service import LlmTranslationEvaluatorService
from domain.services.llm_translator_service import LlmTranslatorService
from domain.model.translation_request import TranslationRequest


load_dotenv()

class TranslationEvaluator:
    def __init__(self):
        settings = Settings()
        self.translator = LlmTranslatorService(settings)
        self.evaluator = LlmTranslationEvaluatorService(settings)

    async def evaluate_translation(self, english_text: str, reference_translation: str, new_translation: str) -> Dict:
        """Use LLM to evaluate the translation quality."""
        result = await self.evaluator.evaluate_translation(
            english_text=english_text,
            reference_translation=reference_translation,
            new_translation=new_translation,
            target_language='hu'
        )
        # Get all metrics from the evaluation
        metrics = {
            "accuracy": {
                "score": result.new_evaluation.accuracy.score,
                "explanation": result.new_evaluation.accuracy.explanation
            },
            "fluency": {
                "score": result.new_evaluation.fluency.score,
                "explanation": result.new_evaluation.fluency.explanation
            },
            "adequacy": {
                "score": result.new_evaluation.adequacy.score,
                "explanation": result.new_evaluation.adequacy.explanation
            },
            "consistency": {
                "score": result.new_evaluation.consistency.score,
                "explanation": result.new_evaluation.consistency.explanation
            },
            "contextual_appropriateness": {
                "score": result.new_evaluation.contextual_appropriateness.score,
                "explanation": result.new_evaluation.contextual_appropriateness.explanation
            },
            "terminology_accuracy": {
                "score": result.new_evaluation.terminology_accuracy.score,
                "explanation": result.new_evaluation.terminology_accuracy.explanation
            },
            "readability": {
                "score": result.new_evaluation.readability.score,
                "explanation": result.new_evaluation.readability.explanation
            },
            "format_preservation": {
                "score": result.new_evaluation.format_preservation.score,
                "explanation": result.new_evaluation.format_preservation.explanation
            },
            "error_rate": {
                "score": result.new_evaluation.error_rate.score,
                "explanation": result.new_evaluation.error_rate.explanation
            }
        }
        
        return {
            "english_text": result.source_text,
            "reference_translation": result.reference_translation,
            "new_translation": result.new_translation,
            "metrics": metrics,
            "matches_reference": result.matches_reference,
            "comments": result.new_evaluation.comments,
            "cost_info": {
                "total_cost": result.cost_info.total_cost,
                "input_cost": result.cost_info.input_cost,
                "output_cost": result.cost_info.output_cost,
                "input_tokens": result.cost_info.input_tokens,
                "output_tokens": result.cost_info.output_tokens,
                "model": result.cost_info.model
            }
        }

    async def evaluate_single_row(self, english_text: str, reference_translation: str) -> Dict:
        """Evaluate a single translation."""
        # Get new translation
        request = TranslationRequest(source_content=english_text, target_languages=['hu'])
        translation, _ = await self.translator.translate(request)
        new_translation = translation.translations['hu']
        
        # Evaluate translation
        return await self.evaluate_translation(
            english_text, 
            reference_translation, 
            new_translation
        )

    async def run_evaluation(self, csv_path: str) -> List[Dict]:
        """Run evaluation on all translations in the CSV file concurrently."""
        df = pd.read_csv(csv_path)
        
        # Create tasks for all rows
        tasks = [
            self.evaluate_single_row(
                row['english'],
                row['translated_value']
            )
            for _, row in df.iterrows()
        ]
        
        # Run all evaluations concurrently
        print(f"\nStarting concurrent evaluation of {len(tasks)} translations...")
        results = await asyncio.gather(*tasks)
        print(f"Completed evaluation of {len(results)} translations.")
            
        return results

async def main():
    evaluator = TranslationEvaluator()
    csv_path = Path(__file__).parent / 'translated_output.csv'
    
    print("Starting translation evaluation...")
    results = await evaluator.run_evaluation(str(csv_path))
    
    # Calculate average scores
    accuracy_scores = [r['metrics']['accuracy']['score'] for r in results]
    fluency_scores = [r['metrics']['fluency']['score'] for r in results]
    adequacy_scores = [r['metrics']['adequacy']['score'] for r in results]
    consistency_scores = [r['metrics']['consistency']['score'] for r in results]
    contextual_scores = [r['metrics']['contextual_appropriateness']['score'] for r in results]
    terminology_scores = [r['metrics']['terminology_accuracy']['score'] for r in results]
    readability_scores = [r['metrics']['readability']['score'] for r in results]
    format_scores = [r['metrics']['format_preservation']['score'] for r in results]
    error_scores = [r['metrics']['error_rate']['score'] for r in results]
    match_count = sum(1 for r in results if r['matches_reference'])
    
    print("\nEvaluation Summary:")
    print(f"Average Accuracy Score: {sum(accuracy_scores)/len(accuracy_scores):.2f}")
    print(f"Average Fluency Score: {sum(fluency_scores)/len(fluency_scores):.2f}")
    print(f"Average Adequacy Score: {sum(adequacy_scores)/len(adequacy_scores):.2f}")
    print(f"Average Consistency Score: {sum(consistency_scores)/len(consistency_scores):.2f}")
    print(f"Average Contextual Appropriateness Score: {sum(contextual_scores)/len(contextual_scores):.2f}")
    print(f"Average Terminology Accuracy Score: {sum(terminology_scores)/len(terminology_scores):.2f}")
    print(f"Average Readability Score: {sum(readability_scores)/len(readability_scores):.2f}")
    print(f"Average Format Preservation Score: {sum(format_scores)/len(format_scores):.2f}")
    print(f"Average Error Rate Score: {sum(error_scores)/len(error_scores):.2f}")
    print(f"Reference Match Rate: {match_count/len(results)*100:.2f}%")
    
    # Save detailed results
    output_path = Path(__file__).parent / 'translation_evaluation_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nDetailed results saved to: {output_path}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
