import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.config import Settings
from infrastructure.translator import OpenAITranslator
from infrastructure.translation_evaluator import OpenAITranslationEvaluator

@dataclass
class TranslationRequest:
    source_content: str
    target_languages: list[str]

load_dotenv()

class TranslationEvaluator:
    def __init__(self):
        settings = Settings()
        self.translator = OpenAITranslator(settings)
        self.evaluator = OpenAITranslationEvaluator(settings)

    async def evaluate_translation(self, english_text: str, reference_translation: str, new_translation: str) -> Dict:
        """Use LLM to evaluate the translation quality."""
        result = await self.evaluator.evaluate_translation(english_text, reference_translation, new_translation)
        return {
            "accuracy_score": result.accuracy_score,
            "fluency_score": result.fluency_score,
            "matches_reference": result.matches_reference,
            "comments": result.comments
        }

    async def run_evaluation(self, csv_path: str) -> List[Dict]:
        """Run evaluation on all translations in the CSV file."""
        results = []
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            english_text = row['english']
            reference_translation = row['translated_value']
            
            # Get new translation
            request = TranslationRequest(source_content=english_text, target_languages=['hu'])
            translation = await self.translator.translate(request)
            new_translation = translation.translations['hu']
            
            # Evaluate translation
            evaluation = await self.evaluate_translation(
                english_text, 
                reference_translation, 
                new_translation
            )
            
            results.append({
                'english_text': english_text,
                'reference_translation': reference_translation,
                'new_translation': new_translation,
                'evaluation': evaluation
            })
            
        return results

async def main():
    evaluator = TranslationEvaluator()
    csv_path = Path(__file__).parent / 'translated_output.csv'
    
    print("Starting translation evaluation...")
    results = await evaluator.run_evaluation(str(csv_path))
    
    # Calculate average scores
    accuracy_scores = [r['evaluation']['accuracy_score'] for r in results]
    fluency_scores = [r['evaluation']['fluency_score'] for r in results]
    match_count = sum(1 for r in results if r['evaluation']['matches_reference'])
    
    print("\nEvaluation Summary:")
    print(f"Average Accuracy Score: {sum(accuracy_scores)/len(accuracy_scores):.2f}")
    print(f"Average Fluency Score: {sum(fluency_scores)/len(fluency_scores):.2f}")
    print(f"Reference Match Rate: {match_count/len(results)*100:.2f}%")
    
    # Save detailed results
    output_path = Path(__file__).parent / 'translation_evaluation_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nDetailed results saved to: {output_path}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
